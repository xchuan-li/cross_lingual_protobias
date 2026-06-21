"""Run the 2AFC prototypicality-bias evaluation.

For every sampled row x active language:
  - decode the (correct, adversarial) image pair
  - randomize left/right order (record where adversarial landed)
  - ask the chooser which image matches the translated neutral description
  - record whether the model picked the adversarial (= prototypical) image

Results are appended to results/predictions.jsonl (resumable: rows already
present are skipped).

Usage:
  python run_eval.py --mock                 # smoke-test on a laptop, no GPU
  python run_eval.py                        # default model (config.ACTIVE_MODEL)
  python run_eval.py --model qwen32b        # pick a model from config.MODELS
  python run_eval.py --model internvl8b     # different-family judge

One model per invocation -> results/predictions_<model>.jsonl (resumable).
Submit one SLURM job per model for the full multi-model run.
"""
import argparse
import json
import random

from tqdm import tqdm

import config
from data_utils import sample_rows, get_image_pair


def load_translations():
    if not config.TRANSLATIONS_PATH.exists():
        raise SystemExit("Run translate.py first to create translations.json")
    return json.loads(config.TRANSLATIONS_PATH.read_text())


def already_done(pred_path):
    done = set()
    if pred_path.exists():
        for line in pred_path.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["id"], r["lang"]))
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true",
                    help="use MockChooser (no model/GPU) to test plumbing")
    ap.add_argument("--model", default=config.ACTIVE_MODEL,
                    choices=list(config.MODELS),
                    help="which model in config.MODELS to evaluate")
    ap.add_argument("--limit", type=int, default=None,
                    help="only process the first N items (smoke-test model "
                         "loading before the full batch; resumable, so kept rows "
                         "are real and the full job continues from there)")
    args = ap.parse_args()

    model_key = args.model
    # Mock output goes to a name analyze.py does NOT glob (predictions_*.jsonl),
    # so a laptop plumbing test can never pollute a real GPU run's resume set.
    pred_path = (config.RESULTS_DIR / f"mock_{model_key}.jsonl" if args.mock
                 else config.predictions_path(model_key))

    rows = sample_rows()
    if args.limit:
        rows = rows[:args.limit]
    translations = load_translations()
    done = already_done(pred_path)

    from backends import make_chooser
    chooser = make_chooser(model_key, mock=args.mock, seed=config.SAMPLE_SEED)
    print(f"Model: {model_key} ({config.MODELS[model_key]['hf']})"
          f"{' [MOCK]' if args.mock else ''} -> {pred_path.name}")

    order_rng = random.Random(config.SAMPLE_SEED)
    n_written = 0
    with open(pred_path, "a") as fout:
        for r in tqdm(rows, desc="rows"):
            rid = r["id"]
            pending = [l for l in config.ACTIVE_LANGUAGES if (rid, l) not in done]
            if not pending:
                continue
            correct_img, adv_img = get_image_pair(r["row_index"])
            for lang in pending:
                desc = translations.get(rid, {}).get(lang)
                if desc is None:
                    continue
                # randomize which slot the adversarial image occupies
                adv_pos = order_rng.choice([1, 2])
                if adv_pos == 1:
                    img1, img2 = adv_img, correct_img
                else:
                    img1, img2 = correct_img, adv_img
                instruction = config.LANGUAGES[lang]["instruction"].format(desc=desc)
                choice = chooser.choose(
                    img1, img2, instruction,
                    adv_position=adv_pos, lang=lang, domain=r["domain"],
                )
                picked_adv = (choice == adv_pos) if choice in (1, 2) else None
                rec = {
                    "id": rid,
                    "item": r["row_index"],  # stable unique item key (the HF
                    # row index): same across an item's languages, unique across
                    # items. `id` is NOT unique, so use this for cross-lingual
                    # pairing (CFR/SBR) and item-level clustering.
                    "model": model_key,
                    "lang": lang,
                    "domain": r["domain"],
                    "subcategory": r["subcategory"],
                    "socio_attr": r["socio_attr"],
                    "gender": r["gender"],
                    "knob": r["knob"],
                    "adv_position": adv_pos,
                    "raw_choice": choice,
                    "picked_adversarial": picked_adv,
                }
                fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fout.flush()
                n_written += 1
    print(f"Wrote {n_written} predictions -> {pred_path}")


if __name__ == "__main__":
    main()
