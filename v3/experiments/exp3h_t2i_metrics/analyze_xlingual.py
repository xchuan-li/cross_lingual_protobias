"""Exp3h cross-lingual — does the representation carry the LANGUAGE effect too?

The mentor asked to run the T2I evaluation on the translated prompts. CLIP /
PickScore have English-only text towers, so we score the actual translated
prompt with a multilingual backbone (SigLIP-multilingual, metric `mclip`) — see
compute_t2i_metrics.py --text translated → results/t2i_scores_xlingual.csv.

This asks the representational analogue of the VLM's per-language result: is the
metric MORE prototypicality-biased for the low-resource / distinct-script
languages (Bengali, Greek) than for English?

Pure analysis (CPU). Usage: python analyze_xlingual.py
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
SCORES = HERE / "results/t2i_scores_xlingual.csv"
LANG_ORDER = ["en", "zh", "ru", "ar", "hi", "bn", "el"]
LANG_NAME = {"en": "English", "zh": "Chinese", "ru": "Russian", "ar": "Arabic",
             "hi": "Hindi", "bn": "Bengali", "el": "Greek"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (c - h, c + h)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--scores", default=str(SCORES))
    args = ap.parse_args()
    s = pd.read_csv(args.scores)
    (HERE / "figures").mkdir(exist_ok=True); out = HERE / "results"
    metrics = sorted(s.metric.unique())

    recs = []
    for m in metrics:
        sm = s[s.metric == m]
        langs = [l for l in LANG_ORDER if l in set(sm.lang)]
        print(f"\n=== metric '{m}': bias rate by language "
              f"(share preferring the typical-but-wrong image) ===")
        en_rate = None
        for l in langs:
            g = sm[sm.lang == l]
            n = len(g); k = int((g.prefers_correct == 0).sum())
            lo, hi = wilson(k, n); rate = k / n
            if l == "en":
                en_rate = rate
            delta = "" if en_rate is None else f"  ({rate - en_rate:+.3f} vs en)"
            print(f"  {LANG_NAME[l]:<9} {rate:.3f}  (n={n}, 95% CI [{lo:.3f}, {hi:.3f}])"
                  f"  mean margin {g.margin.mean():+.4f}{delta}")
            recs.append({"metric": m, "lang": l, "lang_name": LANG_NAME[l],
                         "bias_rate": round(rate, 3), "n": n,
                         "ci_lo": round(lo, 3), "ci_hi": round(hi, 3),
                         "mean_margin": round(g.margin.mean(), 4),
                         "delta_vs_en": None if en_rate is None else round(rate - en_rate, 3)})
    R = pd.DataFrame(recs)
    R.to_csv(out / "xlingual_bias_by_lang.csv", index=False)

    # figure: bias rate by language, per metric, English marked as the reference
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    col = {"mclip": "#4C72B0", "clip": "#4C72B0", "pick": "#C44E52"}
    for m in metrics:
        d = R[R.metric == m].set_index("lang").reindex([l for l in LANG_ORDER if l in set(R.lang)])
        fig, ax = plt.subplots(figsize=(7.6, 4.3))
        x = range(len(d))
        bars = [col.get(m, "#55A868") if l != "en" else "#9AA0B0" for l in d.index]
        lo = (d.bias_rate - d.ci_lo).values; hi = (d.ci_hi - d.bias_rate).values
        ax.bar(x, d.bias_rate.values, yerr=[lo, hi], capsize=4, color=bars)
        ax.axhline(0.5, ls="--", c="gray", lw=1)
        if "en" in d.index:
            ax.axhline(d.loc["en", "bias_rate"], ls=":", c="#5A6072", lw=1.2,
                       label="English reference")
            ax.legend(fontsize=9)
        ax.set_xticks(list(x)); ax.set_xticklabels([LANG_NAME[l] for l in d.index], rotation=15)
        ax.set_ylabel("metric bias rate\n(prefers typical-but-wrong image)"); ax.set_ylim(0, 1)
        ax.set_title(f"Cross-lingual T2I bias — {m} on the translated prompts\n"
                     "(does the representation carry the language effect?)", fontsize=11)
        fig.tight_layout()
        p = HERE / f"figures/figK_xlingual_bias_{m}.png"
        fig.savefig(p, dpi=150); print("saved", p.name)


if __name__ == "__main__":
    main()
