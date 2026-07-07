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

Scoring the *English* text isolates the representation question ("is the bias
baked into the image-text embedding space?"); the cross-lingual axis stays with
the VLM behaviour and the multilingual-CLIP extension is a follow-up (see README).

The item set is exactly the evaluated one: same `data_utils.sample_rows()`
(seed 42, N_PER_DOMAIN), so scores join 1:1 to predictions on `item`.

Metrics:
  clip  — CLIPScore: cosine(image, text) via openai/clip-vit-large-patch14.
  pick  — PickScore: human-preference-tuned CLIP (yuvalkirstain/PickScore_v1).
  vqa   — VQAScore: needs the `t2v_metrics` package (optional; skipped if absent).

Usage:
  python compute_t2i_metrics.py --mock                 # plumbing test, no download
  python compute_t2i_metrics.py --metrics clip pick    # real, needs GPU
  python compute_t2i_metrics.py --limit 20             # smoke-test model loading
Resumable: (item, metric) rows already in results/t2i_scores.csv are skipped.
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
        t = self.torch
        img_in = self.proc(images=[image], return_tensors="pt").to(self.device)
        txt_in = self.proc(text=[text], return_tensors="pt", padding=True,
                           truncation=True, max_length=77).to(self.device)
        with t.no_grad():
            ie = self.model.get_image_features(**img_in)
            te = self.model.get_text_features(**txt_in)
            ie = ie / ie.norm(dim=-1, keepdim=True)
            te = te / te.norm(dim=-1, keepdim=True)
            s = (self.model.logit_scale.exp() * (te * ie).sum(-1))
        return float(s.item())


class VQAScorer:
    """VQAScore (Lin et al. 2024) via the optional `t2v_metrics` package.

    P(image entails text) from a VQA model. Heavy (clip-flant5); off by default.
    """
    def __init__(self, model="clip-flant5-xl"):
        import t2v_metrics  # optional dependency
        self.metric = t2v_metrics.VQAScore(model=model)

    def score(self, image, text):
        import tempfile
        # t2v_metrics takes image *paths*; write the PIL image to a temp file.
        with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as f:
            image.save(f.name)
            s = self.metric(images=[f.name], texts=[text])
        return float(s.reshape(-1)[0])


SCORERS = {"clip": CLIPScorer, "pick": PickScorer, "vqa": VQAScorer}


def build_scorer(name, mock, seed):
    if mock:
        return MockScorer(seed=seed + hash(name) % 1000)
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


def already_done(path):
    done = set()
    if path.exists():
        with open(path) as f:
            for r in csv.DictReader(f):
                done.add((int(r["item"]), r["metric"]))
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true",
                    help="random scores, no model download (plumbing test)")
    ap.add_argument("--metrics", nargs="+", default=["clip", "pick"],
                    choices=list(SCORERS), help="which metrics to compute")
    ap.add_argument("--limit", type=int, default=None,
                    help="only the first N items (smoke-test model loading)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    RESULTS.mkdir(exist_ok=True)

    if args.mock:
        data_utils = None
        rows = mock_rows()
    else:
        import data_utils  # from shared/code, added to sys.path above
        rows = data_utils.sample_rows()
    if args.limit:
        rows = rows[:args.limit]
    done = already_done(OUT)

    # Build only the scorers with outstanding work (loading is expensive).
    todo_metrics = [m for m in args.metrics
                    if any((r["row_index"], m) not in done for r in rows)]
    if not todo_metrics:
        print("Nothing to do — all (item, metric) pairs already scored.")
        return
    print(f"Metrics: {todo_metrics}  |  items: {len(rows)}"
          f"{' [MOCK]' if args.mock else ''}  ->  {OUT.name}")
    scorers = {}
    for m in todo_metrics:
        try:
            scorers[m] = build_scorer(m, args.mock, args.seed)
        except Exception as e:  # e.g. t2v_metrics not installed
            print(f"  ! skipping metric '{m}': {type(e).__name__}: {e}")
    if not scorers:
        raise SystemExit("No usable scorers.")

    new_file = not OUT.exists()
    from tqdm import tqdm
    n_written = 0
    with open(OUT, "a", newline="") as fout:
        w = csv.DictWriter(fout, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        for r in tqdm(rows, desc="items"):
            item = r["row_index"]
            pending = [m for m in scorers if (item, m) not in done]
            if not pending:
                continue
            if args.mock:
                correct_img = adv_img = None  # MockScorer ignores the image
            else:
                correct_img, adv_img = data_utils.get_image_pair(item)
            text = r["text"]  # English neutral description
            for m in pending:
                sc = scorers[m]
                s_c = sc.score(correct_img, text)
                s_a = sc.score(adv_img, text)
                margin = s_c - s_a
                w.writerow({
                    "item": item, "id": r["id"], "domain": r["domain"],
                    "subcategory": r["subcategory"], "socio_attr": r["socio_attr"],
                    "gender": r["gender"], "knob": r["knob"], "metric": m,
                    "score_correct": round(s_c, 6), "score_adv": round(s_a, 6),
                    "margin": round(margin, 6),
                    "prefers_correct": int(margin > 0),
                })
                fout.flush()
                n_written += 1
    print(f"Wrote {n_written} rows -> {OUT}")


if __name__ == "__main__":
    main()
