"""Exp3d — translation-quality audit by back-translation.

Adding low-resource / distinct-script languages (ru/bn/el) invites the obvious
QA question: "are language effects real, or just bad translations?" We answer it
directly: back-translate each non-English prompt to English and measure how much
it drifts from the original English. Low-similarity items are flagged so any
language claim can be re-checked with them excluded.

Similarity = token-F1 between original and back-translation (stdlib only, works
in this PEP-668 / py3.14 box). If `sacrebleu` is importable we also report chrF.
Back-translation uses deep-translator (Google) and is cached + resumable, so
re-runs are cheap and you can grow --limit over time.

Outputs (next to this script):
  results/backtranslations.json        cache: "<lang>:<item>" -> back-translation
  results/translation_qa.csv           per-language similarity summary
  results/translation_qa_flagged.jsonl drifted items, for eyeballing

Usage (needs network — run on the login node or your laptop):
  python backtranslation_qa.py --limit 60
  python backtranslation_qa.py --self-test         # offline: check the metric
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT_TRANS = ROOT / "v2/experiments/exp1_900x4lang/results/translations.json"
# deep-translator source codes (Google). en is the reference, never back-translated.
SRC_CODE = {"zh": "zh-CN", "ar": "ar", "hi": "hi", "ru": "ru", "bn": "bn", "el": "el"}

_word = re.compile(r"\w+", re.UNICODE)


def tokens(text):
    return set(_word.findall((text or "").lower()))


def token_f1(a, b):
    ta, tb = tokens(a), tokens(b)
    if not ta and not tb:
        return 1.0
    inter = len(ta & tb)
    return 2 * inter / (len(ta) + len(tb)) if (ta or tb) else 0.0


def chrf_fn():
    try:
        from sacrebleu.metrics import CHRF
        m = CHRF()
        return lambda a, b: m.sentence_score(b, [a]).score / 100.0
    except Exception:
        return None


def get_backtranslator():
    from deep_translator import GoogleTranslator
    return GoogleTranslator


def self_test():
    pairs = [
        ("a bird sits on a branch", "a bird sits on a branch", "identical"),
        ("a bird sits on a branch", "a bird is sitting on the branch", "paraphrase"),
        ("a bird sits on a branch", "a car drives on a highway", "unrelated"),
    ]
    print("token-F1 self-test:")
    for a, b, tag in pairs:
        print(f"  {tag:<11} {token_f1(a, b):.3f}   ({a!r} vs {b!r})")
    chrf = chrf_fn()
    print("chrF available:", bool(chrf))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trans", default=str(DEFAULT_TRANS))
    ap.add_argument("--limit", type=int, default=60, help="items per language to audit")
    ap.add_argument("--thr", type=float, default=0.5, help="flag if token-F1 < thr")
    ap.add_argument("--sleep", type=float, default=0.2, help="seconds between API calls")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    (HERE / "results").mkdir(exist_ok=True)
    cache_path = HERE / "results/backtranslations.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    trans = json.loads(Path(args.trans).read_text())
    items = sorted(trans)
    langs = sorted({l for e in trans.values() for l in e
                    if l not in ("source", "en")})
    print(f"Auditing {len(langs)} languages: {langs}  (limit {args.limit}/lang)")

    GoogleTranslator = get_backtranslator()
    chrf = chrf_fn()
    rows, flagged, n_new = [], [], 0

    for lang in langs:
        code = SRC_CODE.get(lang, lang)
        sims, chrfs, used = [], [], 0
        for item in items:
            if used >= args.limit:
                break
            entry = trans[item]
            src, tgt = entry.get("en") or entry.get("source"), entry.get(lang)
            if not src or not tgt:
                continue
            key = f"{lang}:{item}"
            if key not in cache:
                try:
                    cache[key] = GoogleTranslator(source=code, target="en").translate(tgt)
                    n_new += 1
                    time.sleep(args.sleep)
                except Exception as e:
                    print(f"  ! backtranslate failed {key}: {e}")
                    continue
            back = cache[key]
            s = token_f1(src, back)
            sims.append(s)
            if chrf:
                chrfs.append(chrf(src, back))
            used += 1
            if s < args.thr:
                flagged.append({"lang": lang, "item": item, "source": src,
                                "translation": tgt, "backtranslation": back,
                                "token_f1": round(s, 3)})
        if sims:
            row = {"lang": lang, "n": len(sims),
                   "mean_token_f1": round(sum(sims) / len(sims), 3),
                   "median_token_f1": round(median(sims), 3),
                   "min_token_f1": round(min(sims), 3),
                   "n_flagged": sum(s < args.thr for s in sims),
                   "flag_rate": round(sum(s < args.thr for s in sims) / len(sims), 3)}
            if chrfs:
                row["mean_chrf"] = round(sum(chrfs) / len(chrfs), 3)
            rows.append(row)

    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2))

    # CSV (stdlib, since column set can vary with chrF availability)
    import csv
    cols = ["lang", "n", "mean_token_f1", "median_token_f1", "min_token_f1",
            "n_flagged", "flag_rate"] + (["mean_chrf"] if chrf else [])
    with open(HERE / "results/translation_qa.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    with open(HERE / "results/translation_qa_flagged.jsonl", "w") as f:
        for r in flagged:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\n(+{n_new} new back-translations; cache now {len(cache)})")
    print("\n=== translation quality (higher token-F1 = less drift) ===")
    for r in rows:
        extra = f"  chrF={r['mean_chrf']:.3f}" if "mean_chrf" in r else ""
        print(f"  {r['lang']:<4} n={r['n']:<3} mean={r['mean_token_f1']:.3f} "
              f"median={r['median_token_f1']:.3f} flagged={r['n_flagged']}"
              f" ({r['flag_rate']*100:.0f}%){extra}")
    print(f"\nsaved results/translation_qa.csv + {len(flagged)} flagged items")


if __name__ == "__main__":
    main()
