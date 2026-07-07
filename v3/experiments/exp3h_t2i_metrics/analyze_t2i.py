"""Exp3h analysis — turn T2I alignment scores into the PR-II result slides.

Reads results/t2i_scores.csv (from compute_t2i_metrics.py) and answers:

1. Does the *representation* itself show prototypicality bias?
   "metric bias rate" = fraction of items where the metric scores the
   typical-but-wrong image ABOVE the correct one (margin < 0). 0.5 = no bias.
   Broken out by domain, by socio_attr (demography), by subcategory — so it
   lines up with the VLM's attribute/subcategory pattern (exp2 / exp3g).

2. Does the VLM's *behaviour* track the metric?  (the unifying result)
   Join scores to the English VLM predictions on `item`. If the VLM picks the
   correct image more often exactly when the metric also prefers it, the choice
   bias and the embedding bias are the same phenomenon at two levels.

Pure analysis (CPU). Usage: python analyze_t2i.py
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))          # protobias_io
from protobias_io import load_rows            # noqa: E402

SCORES = HERE / "results/t2i_scores.csv"
PREDS = [ROOT / "shared/code/results/predictions_qwen7b.jsonl",
         ROOT / "shared/code/results/predictions_internvl8b.jsonl"]
ATTR_ORDER = ["wealth", "power", "civility", "morality", "intellect"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (c - h, c + h)


def bias_block(df, label_col=None):
    """metric-bias-rate (share preferring the typical/adversarial image) + mean
    margin, either overall (label_col=None) or grouped by label_col."""
    def one(g):
        n = len(g); k = int((g.prefers_correct == 0).sum())  # prefers adversarial
        lo, hi = wilson(k, n)
        return pd.Series({"metric_bias_rate": round(k / n, 3), "n": n,
                          "ci_lo": round(lo, 3), "ci_hi": round(hi, 3),
                          "mean_margin": round(g.margin.mean(), 4)})
    if label_col is None:
        return one(df)
    return df.groupby(label_col, group_keys=True).apply(one, include_groups=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", default=str(SCORES))
    args = ap.parse_args()
    s = pd.read_csv(args.scores)
    metrics = sorted(s.metric.unique())
    out = HERE / "results"; (HERE / "figures").mkdir(exist_ok=True)

    # ---- 1. representation bias, overall + by domain / attr / subcategory ----
    for m in metrics:
        sm = s[s.metric == m]
        ov = bias_block(sm)
        print(f"\n=== metric '{m}': overall bias rate "
              f"{ov.metric_bias_rate:.3f} (n={int(ov.n)}, "
              f"mean margin {ov.mean_margin:+.4f}) ===")
        print("  by domain:")
        print(bias_block(sm, "domain").to_string())
    # demography attribute breakdown — the key comparison to exp2
    dem = s[s.domain == "demography"]
    attr_tab = []
    for m in metrics:
        b = bias_block(dem[dem.metric == m], "socio_attr")
        b = b.reindex([a for a in ATTR_ORDER if a in b.index])
        b["metric"] = m
        attr_tab.append(b.reset_index())
        print(f"\n=== metric '{m}': demography bias rate by socio_attr ===")
        print(b.to_string())
    attr_df = pd.concat(attr_tab, ignore_index=True)
    attr_df.to_csv(out / "metric_bias_by_attr.csv", index=False)
    # subcategory breakdown (animal/object) — ties to exp3g
    sub = s[s.domain.isin(["animal", "object"])]
    sub_recs = []
    for m in metrics:
        for dom in ["animal", "object"]:
            b = bias_block(sub[(sub.metric == m) & (sub.domain == dom)], "subcategory")
            b = b.reset_index(); b["metric"] = m; b["domain"] = dom
            sub_recs.append(b)
    pd.concat(sub_recs, ignore_index=True).to_csv(out / "metric_bias_by_subcategory.csv", index=False)

    # ---- 2. does the VLM's choice track the metric? --------------------------
    rows = load_rows([str(p) for p in PREDS if p.exists()])
    pr = pd.DataFrame([r for r in rows
                       if r["lang"] == "en" and r["picked_adversarial"] is not None])
    track = []
    for m in metrics:
        sm = s[s.metric == m][["item", "prefers_correct", "margin"]]
        for model in sorted(pr.model.unique()):
            j = pr[pr.model == model].merge(sm, on="item", how="inner")
            if j.empty:
                continue
            j["vlm_correct"] = (~j.picked_adversarial.astype(bool)).astype(int)
            agree = (j.vlm_correct == j.prefers_correct).mean()
            # VLM's correct-pick rate split by whether the metric prefers correct
            when_pc = j[j.prefers_correct == 1].vlm_correct.mean()
            when_pa = j[j.prefers_correct == 0].vlm_correct.mean()
            print(f"\n[{m} / {model}] n={len(j)}  VLM–metric agreement={agree:.3f}")
            print(f"    VLM picks correct: {when_pc:.3f} when metric prefers correct "
                  f"vs {when_pa:.3f} when metric prefers typical  "
                  f"(tracking gap {when_pc - when_pa:+.3f})")
            track.append({"metric": m, "model": model, "n": len(j),
                          "agreement": round(agree, 3),
                          "vlm_correct_when_metric_correct": round(when_pc, 3),
                          "vlm_correct_when_metric_typical": round(when_pa, 3),
                          "tracking_gap": round(when_pc - when_pa, 3)})
    pd.DataFrame(track).to_csv(out / "vlm_metric_tracking.csv", index=False)

    # ---- figures -------------------------------------------------------------
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    # figI: representation bias by attribute (does the embedding show wealth>morality?)
    attrs = [a for a in ATTR_ORDER if a in set(attr_df.socio_attr)]
    x = range(len(attrs)); w = 0.8 / max(1, len(metrics))
    col = {"clip": "#4C72B0", "pick": "#C44E52", "vqa": "#55A868"}
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    for j, m in enumerate(metrics):
        d = attr_df[attr_df.metric == m].set_index("socio_attr")
        vals = [d.loc[a, "metric_bias_rate"] if a in d.index else 0 for a in attrs]
        lo = [d.loc[a, "metric_bias_rate"] - d.loc[a, "ci_lo"] if a in d.index else 0 for a in attrs]
        hi = [d.loc[a, "ci_hi"] - d.loc[a, "metric_bias_rate"] if a in d.index else 0 for a in attrs]
        ax.bar([i + (j - (len(metrics) - 1) / 2) * w for i in x], vals, w,
               yerr=[lo, hi], capsize=4, label=m, color=col.get(m, "#8172B3"))
    ax.axhline(0.5, ls="--", c="gray", lw=1, label="no bias")
    ax.set_xticks(list(x)); ax.set_xticklabels(attrs)
    ax.set_ylabel("metric bias rate\n(prefers typical-but-wrong image)")
    ax.set_ylim(0, 1)
    ax.set_title("T2I embedding space carries the VLM's attribute bias\n"
                 "(bias strongest on wealth/power, fades to morality/intellect; both metrics)")
    ax.legend(fontsize=9)
    fig.tight_layout(); fig.savefig(HERE / "figures/figI_metric_bias_by_attr.png", dpi=150)

    # figJ: VLM tracks the metric (correct-pick rate split by metric preference)
    if track:
        T = pd.DataFrame(track)
        labels = [f"{r.metric}\n{r.model}" for r in T.itertuples()]
        x = range(len(T)); w = 0.4
        fig, ax = plt.subplots(figsize=(max(6, 1.6 * len(T)), 4.3))
        ax.bar([i - w / 2 for i in x], T.vlm_correct_when_metric_correct, w,
               label="metric prefers correct", color="#55A868")
        ax.bar([i + w / 2 for i in x], T.vlm_correct_when_metric_typical, w,
               label="metric prefers typical", color="#C44E52")
        ax.axhline(0.5, ls="--", c="gray", lw=1)
        ax.set_xticks(list(x)); ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylabel("VLM picks the correct image (rate)"); ax.set_ylim(0, 1)
        ax.set_title("The VLM's choice tracks the T2I metric\n"
                     "correct-pick rate ~0.65+ when the metric agrees vs ~0.40 when it prefers the typical image")
        ax.legend(fontsize=9)
        fig.tight_layout(); fig.savefig(HERE / "figures/figJ_vlm_tracks_metric.png", dpi=150)
    print("\nsaved figI/figJ + results/*.csv")


if __name__ == "__main__":
    main()
