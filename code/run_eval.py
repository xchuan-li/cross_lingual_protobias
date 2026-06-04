"""Run the 2AFC prototypicality-bias evaluation.

For every sampled row x active language:
  - decode the (correct, adversarial) image pair
  - randomize left/right order (record where adversarial landed)
  - ask the chooser which image matches the translated neutral description
  - record whether the model picked the adversarial (= prototypical) image

Results are appended to results/predictions.jsonl (resumable: rows already
present are skipped).

Usage:
  python run_eval.py --mock          # smoke-test on a laptop, no GPU
  python run_eval.py                 # real Qwen2.5-VL (needs GPU)
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


def already_done():
    done = set()
    if config.PREDICTIONS_PATH.exists():
        for line in config.PREDICTIONS_PATH.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["id"], r["lang"]))
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true",
                    help="use MockChooser (no model/GPU) to test plumbing")
    args = ap.parse_args()

    rows = sample_rows()
    translations = load_translations()
    done = already_done()

    if args.mock:
        from backends import MockChooser
        chooser = MockChooser(seed=config.SAMPLE_SEED)
    else:
        from backends import QwenChooser
        chooser = QwenChooser(config.QWEN_MODEL, config.MAX_NEW_TOKENS)

    order_rng = random.Random(config.SAMPLE_SEED)
    n_written = 0
    with open(config.PREDICTIONS_PATH, "a") as fout:
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
    print(f"Wrote {n_written} predictions -> {config.PREDICTIONS_PATH}")


if __name__ == "__main__":
    main()
