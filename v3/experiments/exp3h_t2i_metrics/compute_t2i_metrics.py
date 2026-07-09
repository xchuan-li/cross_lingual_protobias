"""Exp3h — T2I alignment metrics on the ProtoBias pairs (advisor PR-II ask).

Advisor feedback on PR II: *"add some T2I evaluation metrics in the results,
such as VQAScore, CLIPScore, PickScore."*

Our main measure is *behavioural*: a VLM is asked to pick one of two images.
These T2I metrics give an orthogonal, *representational* measure. For every
sampled item we score the neutral English description `text` against BOTH images
and take the margin:

    margin = score(correct_image, text) - score(adversarial_image, text)

margin > 0  => the metric prefers the semantically-correct (atypical) image.
margin < 0  => the metric prefers the typical-but-wrong image = the metric ITSELF
               shows prototypicality bias, independent of any VLM's decoding.

Two modes (--text):
  english     score the English `text` — isolates the representation question
              ("is the bias baked into the embedding space?"). One row per
              (item, metric) in results/t2i_scores.csv.
  translated  score each language's TRANSLATED prompt with a multilingual
              backbone — the mentor's ask, the representational analogue of the
              VLM's per-language result. One row per (item, lang, metric) in
              results/t2i_scores_xlingual.csv.

The item set is exactly the evaluated one: same `data_utils.sample_rows()`
(seed 42, N_PER_DOMAIN), so scores join 1:1 to predictions on `item`.

Metrics:
  clip   — CLIPScore: cosine(image, text) via openai/clip-vit-large-patch14.
  pick   — PickScore: human-preference-tuned CLIP (yuvalkirstain/PickScore_v1).
  mclip  — multilingual CLIPScore via SigLIP-multilingual (for --text translated;
           clip/pick have English-only text towers).
  vqa    — VQAScore via `t2v_metrics` (default clip-flant5-xxl); needs a
           dedicated env (see README); skipped if the package is absent.

Usage:
  python compute_t2i_metrics.py --mock                    # english plumbing test
  python compute_t2i_metrics.py --mock --text translated  # xlingual plumbing test
  python compute_t2i_metrics.py --metrics clip pick       # english run (GPU)
  python compute_t2i_metrics.py --text translated         # xlingual run (GPU)
Resumable: english on (item, metric); translated on (item, lang, metric).
"""
import argparse
import csv
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "shared/code"))  # reuse the eval's data loading

RESULTS = HERE / "results"
OUT = RESULTS / "t2i_scores.csv"
FIELDS = ["item", "id", "domain", "subcategory", "socio_attr", "gender", "knob",
          "metric", "score_correct", "score_adv", "margin", "prefers_correct"]

# openai/clip-vit-large-patch14 is the CLIPScore reference backbone; PickScore
# ships its own weights but reuses the laion CLIP-ViT-H-14 *processor*.
CLIP_MODEL = "openai/clip-vit-large-patch14"
PICK_MODEL = "yuvalkirstain/PickScore_v1"
PICK_PROC = "laion/CLIP-ViT-H-14-laion2B-s32B-b79K"
# Multilingual image-text backbone (SigLIP multilingual) — its text encoder
# handles the translated prompts directly, which CLIP/PickScore (English-only
# text towers) cannot. Used for the cross-lingual T2I run (--text translated).
MCLIP_MODEL = "google/siglip-base-patch16-256-multilingual"

# Languages for the cross-lingual run (matches the VLM eval's ACTIVE_LANGUAGES).
XLING_LANGS = ["en", "zh", "ru", "ar", "hi", "bn", "el"]


# --------------------------------------------------------------------------- #
# Scorers.  Each exposes .score(pil_image, text) -> float (higher = better match)
# --------------------------------------------------------------------------- #
class MockScorer:
    """Random scores for plumbing tests (no model download)."""
    def __init__(self, seed=0):
        self.rng = random.Random(seed)

    def score(self, image, text):
        return self.rng.uniform(0, 1)


class CLIPScorer:
    def __init__(self, model_name=CLIP_MODEL):
        import torch
        from transformers import CLIPModel, CLIPProcessor
        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained(model_name).to(self.device).eval()
        self.proc = CLIPProcessor.from_pretrained(model_name)

    @property
    def _t(self):
        return self.torch

    def score(self, image, text):
        inp = self.proc(text=[text], images=[image], return_tensors="pt",
                        padding=True, truncation=True).to(self.device)
        with self._t.no_grad():
            out = self.model(**inp)
            img = out.image_embeds / out.image_embeds.norm(dim=-1, keepdim=True)
            txt = out.text_embeds / out.text_embeds.norm(dim=-1, keepdim=True)
            cos = (img * txt).sum(-1)  # cosine similarity in [-1, 1]
        return float(cos.item())


class PickScorer:
    def __init__(self, model_name=PICK_MODEL, proc_name=PICK_PROC):
        import torch
        from transformers import AutoModel, AutoProcessor
        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.proc = AutoProcessor.from_pretrained(proc_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device).eval()

    def score(self, image, text):
        # One combined forward and read the projected embeds off the output
        # (mirrors the CLIP path). Some transformers versions make
        # get_image_features return an output object rather than a tensor, so
        # we avoid it and use model(**inp).image_embeds / .text_embeds.
        t = self.torch
        inp = self.proc(text=[text], images=[image], return_tensors="pt",
                        padding=True, truncation=True, max_length=77).to(self.device)
        with t.no_grad():
            out = self.model(**inp)
            ie = out.image_embeds / out.image_embeds.norm(dim=-1, keepdim=True)
            te = out.text_embeds / out.text_embeds.norm(dim=-1, keepdim=True)
            s = self.model.logit_scale.exp() * (te * ie).sum(-1)
        return float(s.item())


class MCLIPScorer:
    """Multilingual image-text scorer (SigLIP multilingual).

    Lets us score the ACTUAL translated prompts — CLIP/PickScore have
    English-only text towers, so the cross-lingual T2I question (mentor: "run
    the evaluation on the translated prompts") needs a multilingual backbone.
    Same combined-forward pattern as CLIPScorer; SigLIP needs max_length padding.
    """
    def __init__(self, model_name=MCLIP_MODEL):
        import torch
        from transformers import AutoModel, AutoProcessor
        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModel.from_pretrained(model_name).to(self.device).eval()
        self.proc = AutoProcessor.from_pretrained(model_name)

    def score(self, image, text):
        t = self.torch
        inp = self.proc(text=[text], images=[image], padding="max_length",
                        max_length=64, truncation=True, return_tensors="pt").to(self.device)
        with t.no_grad():
            out = self.model(**inp)
            ie = out.image_embeds / out.image_embeds.norm(dim=-1, keepdim=True)
            te = out.text_embeds / out.text_embeds.norm(dim=-1, keepdim=True)
            cos = (ie * te).sum(-1)
        return float(cos.item())


class VQABlip2Scorer:
    """VQAScore via a transformers-native BLIP-2 FlanT5 VQA model.

    Same method as t2v_metrics' VQAScore — P("yes" | image, "does this image
    show <text>?") from a FlanT5-based VQA model — but self-contained in
    transformers, so it avoids the t2v_metrics / llava / torch-reinstall
    dependency stack that fights the base GPU environment (Kaggle, Colab).
    Default Salesforce/blip2-flan-t5-xl (~4GB, fits a 16GB T4).
    """
    def __init__(self, model_name="Salesforce/blip2-flan-t5-xl"):
        import torch
        from transformers import Blip2Processor, Blip2ForConditionalGeneration
        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.proc = Blip2Processor.from_pretrained(model_name)
        self.model = Blip2ForConditionalGeneration.from_pretrained(
            model_name, torch_dtype=self.dtype).to(self.device).eval()
        # token ids that spell "yes" (handle SentencePiece ▁ prefix + casing)
        ids = set()
        for w in ["yes", "Yes", " yes", " Yes"]:
            toks = self.proc.tokenizer(w, add_special_tokens=False).input_ids
            if toks:
                ids.add(toks[0])
        self.yes_ids = sorted(ids)

    def score(self, image, text):
        # P("yes") from the FIRST generated token — the same generate() path that
        # yields the model's yes/no answer, so the probability is consistent with
        # what the model actually decodes (a manual decoder forward read the wrong
        # position and returned ~uniform prob).
        t = self.torch
        prompt = f'Question: Does this image show "{text}"? Answer:'
        inp = self.proc(images=image, text=prompt, return_tensors="pt").to(self.device, self.dtype)
        with t.no_grad():
            out = self.model.generate(**inp, max_new_tokens=1,
                                      output_scores=True, return_dict_in_generate=True)
            probs = out.scores[0][0].float().softmax(-1)
            p_yes = probs[self.yes_ids].sum().item()
        return p_yes


class VQAScorer:
    """VQAScore (Lin et al. 2024) via the optional `t2v_metrics` package.

    P(image entails text) from a VQA model. Heavy; the mentor's default is
    clip-flant5-xxl (~11B, ~22GB). Its dependency stack (llava + a pinned torch)
    often fights the base GPU env — VQABlip2Scorer is the self-contained
    fallback (same method, transformers-native). Route via --vqa-model.
    """
    def __init__(self, model="clip-flant5-xxl"):
        import t2v_metrics  # optional dependency
        self.metric = t2v_metrics.VQAScore(model=model)

    def score(self, image, text):
        import tempfile
        # t2v_metrics takes image *paths*; write the PIL image to a temp file.
        with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as f:
            image.save(f.name)
            s = self.metric(images=[f.name], texts=[text])
        return float(s.reshape(-1)[0])


SCORERS = {"clip": CLIPScorer, "pick": PickScorer, "mclip": MCLIPScorer, "vqa": VQAScorer}


def build_scorer(name, mock, seed, vqa_model=None):
    if mock:
        return MockScorer(seed=seed + hash(name) % 1000)
    if name == "vqa":
        vm = vqa_model or "clip-flant5-xxl"
        if "blip2" in vm:  # self-contained transformers backend (no t2v_metrics)
            hf = vm if "/" in vm else f"Salesforce/{vm}"
            return VQABlip2Scorer(model_name=hf)
        return VQAScorer(model=vm)  # t2v_metrics (clip-flant5-*)
    return SCORERS[name]()


def mock_rows():
    """Offline stand-in for data_utils.sample_rows(): pull the real item set
    (and its metadata) from an existing predictions file, so a laptop plumbing
    test needs neither the HF dataset nor any image decode. Returns the same
    shape sample_rows() does (row_index / id / domain / subcategory / ...).
    """
    import json
    pred = ROOT / "shared/code/results/predictions_qwen7b.jsonl"
    seen, out = set(), []
    for line in pred.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r["item"] in seen:
            continue
        seen.add(r["item"])
        out.append({"row_index": r["item"], "id": r["id"], "domain": r["domain"],
                    "subcategory": r["subcategory"], "socio_attr": r["socio_attr"],
                    "gender": r["gender"], "knob": r["knob"], "text": "(mock)"})
    return out


OUT_X = RESULTS / "t2i_scores_xlingual.csv"           # cross-lingual output
FIELDS_X = FIELDS[:7] + ["lang"] + FIELDS[7:]          # insert `lang` before metric


def already_done(path, key):
    """Set of already-scored keys. key(r) -> tuple built from a CSV row dict."""
    done = set()
    if path.exists():
        with open(path) as f:
            for r in csv.DictReader(f):
                done.add(key(r))
    return done


def load_translations(override=None):
    """Locate translations.json across both repo and flat-cluster layouts."""
    import json
    cands = ([Path(override)] if override else []) + [
        ROOT / "shared/code/results/translations.json",   # repo layout
        Path.cwd() / "results/translations.json",         # cluster flat dir
        HERE / "results/translations.json",
    ]
    for p in cands:
        if p.exists():
            print(f"translations: {p}")
            return json.loads(p.read_text())
    raise SystemExit("translations.json not found; pass --translations PATH. "
                     f"Tried: {[str(c) for c in cands]}")


def build_scorers(todo_metrics, args):
    scorers = {}
    for m in todo_metrics:
        try:
            scorers[m] = build_scorer(m, args.mock, args.seed,
                                      vqa_model=getattr(args, "vqa_model", None))
        except Exception as e:  # e.g. t2v_metrics not installed
            print(f"  ! skipping metric '{m}': {type(e).__name__}: {e}")
    if not scorers:
        raise SystemExit("No usable scorers.")
    return scorers


def run_english(rows, args):
    """Original path: score the English `text`, one row per (item, metric)."""
    done = already_done(OUT, lambda r: (int(r["item"]), r["metric"]))
    todo = [m for m in args.metrics if any((r["row_index"], m) not in done for r in rows)]
    if not todo:
        print("Nothing to do — all (item, metric) pairs already scored."); return
    print(f"[english] metrics: {todo}  |  items: {len(rows)}"
          f"{' [MOCK]' if args.mock else ''}  ->  {OUT.name}")
    scorers = build_scorers(todo, args)
    if not args.mock:
        import data_utils
    from tqdm import tqdm
    new_file = not OUT.exists(); n = 0
    with open(OUT, "a", newline="") as fout:
        w = csv.DictWriter(fout, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        for r in tqdm(rows, desc="items"):
            item = r["row_index"]
            pend = [m for m in scorers if (item, m) not in done]
            if not pend:
                continue
            ci, ai = (None, None) if args.mock else data_utils.get_image_pair(item)
            for m in pend:
                sc, ac = scorers[m].score(ci, r["text"]), scorers[m].score(ai, r["text"])
                w.writerow({"item": item, "id": r["id"], "domain": r["domain"],
                            "subcategory": r["subcategory"], "socio_attr": r["socio_attr"],
                            "gender": r["gender"], "knob": r["knob"], "metric": m,
                            "score_correct": round(sc, 6), "score_adv": round(ac, 6),
                            "margin": round(sc - ac, 6), "prefers_correct": int(sc - ac > 0)})
                fout.flush(); n += 1
    print(f"Wrote {n} rows -> {OUT}")


def run_translated(rows, args):
    """Cross-lingual path: score the TRANSLATED prompt for each language, one row
    per (item, lang, metric). The mentor's ask — run the eval on translated
    prompts — needs a multilingual scorer (default: mclip / SigLIP-multilingual).
    """
    tr = load_translations(args.translations)
    done = already_done(OUT_X, lambda r: (int(r["item"]), r["lang"], r["metric"]))
    todo = [m for m in args.metrics
            if any((r["row_index"], l, m) not in done for r in rows for l in args.langs)]
    if not todo:
        print("Nothing to do — all (item, lang, metric) already scored."); return
    print(f"[translated] metrics: {todo}  |  langs: {args.langs}  |  items: {len(rows)}"
          f"{' [MOCK]' if args.mock else ''}  ->  {OUT_X.name}")
    scorers = build_scorers(todo, args)
    if not args.mock:
        import data_utils
    from tqdm import tqdm
    new_file = not OUT_X.exists(); n = 0
    with open(OUT_X, "a", newline="") as fout:
        w = csv.DictWriter(fout, fieldnames=FIELDS_X)
        if new_file:
            w.writeheader()
        for r in tqdm(rows, desc="items"):
            item, rid = r["row_index"], r["id"]
            langs_pending = [l for l in args.langs
                             if any((item, l, m) not in done for m in scorers)
                             and tr.get(rid, {}).get(l)]
            if not langs_pending:
                continue
            ci, ai = (None, None) if args.mock else data_utils.get_image_pair(item)
            for l in langs_pending:
                text = tr[rid][l]
                for m in scorers:
                    if (item, l, m) in done:
                        continue
                    sc, ac = scorers[m].score(ci, text), scorers[m].score(ai, text)
                    w.writerow({"item": item, "id": rid, "domain": r["domain"],
                                "subcategory": r["subcategory"], "socio_attr": r["socio_attr"],
                                "gender": r["gender"], "knob": r["knob"], "lang": l, "metric": m,
                                "score_correct": round(sc, 6), "score_adv": round(ac, 6),
                                "margin": round(sc - ac, 6), "prefers_correct": int(sc - ac > 0)})
                    fout.flush(); n += 1
    print(f"Wrote {n} rows -> {OUT_X}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true",
                    help="random scores, no model download (plumbing test)")
    ap.add_argument("--text", choices=["english", "translated"], default="english",
                    help="english: score the English prompt (clip/pick). "
                         "translated: score each language's prompt (needs mclip).")
    ap.add_argument("--metrics", nargs="+", default=None, choices=list(SCORERS),
                    help="metrics to compute (default: clip pick for english, mclip for translated)")
    ap.add_argument("--langs", nargs="+", default=XLING_LANGS,
                    help="languages for --text translated")
    ap.add_argument("--translations", default=None,
                    help="path to translations.json (auto-located if omitted)")
    ap.add_argument("--vqa-model", default="clip-flant5-xxl",
                    help="model for --metrics vqa. clip-flant5-xxl/-xl -> t2v_metrics "
                         "(heavy deps). blip2-flan-t5-xl -> self-contained transformers "
                         "VQAScore, no t2v_metrics (recommended when the deps fight the GPU env).")
    ap.add_argument("--limit", type=int, default=None,
                    help="only the first N items (smoke-test model loading)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    RESULTS.mkdir(exist_ok=True)
    if args.metrics is None:
        args.metrics = ["mclip"] if args.text == "translated" else ["clip", "pick"]

    if args.mock:
        rows = mock_rows()
    else:
        import data_utils  # from shared/code, added to sys.path above
        rows = data_utils.sample_rows()
    if args.limit:
        rows = rows[:args.limit]

    if args.text == "translated":
        run_translated(rows, args)
    else:
        run_english(rows, args)


if __name__ == "__main__":
    main()
