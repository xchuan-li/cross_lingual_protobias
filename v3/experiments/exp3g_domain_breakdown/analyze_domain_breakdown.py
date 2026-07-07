"""Exp3g — do animal & object have structure too? (advisor PR-II ask)

v2/exp2 found demography bias is attribute-specific (wealth/power >> morality).
But animal & object were only ever reported as a single pooled error rate
(~.46-.57), so the deck says nothing about *what* drives them. The advisor asked
to "check on other categories (animal & object)". This does for animal/object
what exp2 did for demography: break each down by its own `subcategory`
(animal: bird/mammal/animal; object: vehicle/tableware/furniture) and by the
visual `knob`, with Wilson CIs, across both model families.

It also chases the one v2 anomaly: object x Hindi = .553 (every other language
sat at .46-.47 on objects). Here we localise it — is that spike concentrated in
one subcategory or one knob, or spread evenly?

Pure analysis of existing predictions (no GPU).
Usage:  python analyze_domain_breakdown.py
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
from protobias_io import load_rows  # noqa: E402

DEFAULT = [str(ROOT / "shared/code/results/predictions_qwen7b.jsonl"),
           str(ROOT / "shared/code/results/predictions_internvl8b.jsonl")]
SUBCATS = {"animal": ["bird", "mammal", "animal"],
           "object": ["vehicle", "tableware", "furniture"]}
KNOBS = ["count", "color_tone", "layout_relation", "spatial", "scale_size"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (c - h, c + h)


def rate_block(d, col, keys):
    """error_rate + Wilson CI + n for each key in `keys`, over frame d."""
    out = []
    for key in keys:
        g = d[d[col] == key]
        n = len(g); k = int(g.y.sum())
        if n == 0:
            continue
        lo, hi = wilson(k, n)
        out.append({col: key, "error_rate": round(k / n, 3), "n": n,
                    "ci_lo": round(lo, 3), "ci_hi": round(hi, 3)})
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pred", nargs="+", default=DEFAULT)
    args = ap.parse_args()
    (HERE / "figures").mkdir(exist_ok=True); (HERE / "results").mkdir(exist_ok=True)
    rows = load_rows(args.pred)
    df = pd.DataFrame([r for r in rows if r["picked_adversarial"] is not None])
    df["y"] = df["picked_adversarial"].astype(int)
    models = sorted(df["model"].unique())

    # ---- 1. error rate by subcategory, per domain, per model -----------------
    sub_recs = []
    for m in models:
        dm = df[df.model == m]
        for dom, cats in SUBCATS.items():
            print(f"\n=== {m} / {dom}: error rate by subcategory (pooled langs) ===")
            for rec in rate_block(dm[dm.domain == dom], "subcategory", cats):
                print(f"  {rec['subcategory']:<12} {rec['error_rate']:.3f}  "
                      f"(n={rec['n']}, 95% CI [{rec['ci_lo']:.3f}, {rec['ci_hi']:.3f}])")
                sub_recs.append({"model": m, "domain": dom, **rec})
    pd.DataFrame(sub_recs).to_csv(HERE / "results/error_by_subcategory.csv", index=False)

    # ---- 2. error rate by knob, WITHIN animal and object ---------------------
    knob_recs = []
    for m in models:
        dm = df[df.model == m]
        for dom in SUBCATS:
            print(f"\n=== {m} / {dom}: error rate by knob (pooled langs) ===")
            for rec in rate_block(dm[dm.domain == dom], "knob", KNOBS):
                print(f"  {rec['knob']:<16} {rec['error_rate']:.3f}  (n={rec['n']})")
                knob_recs.append({"model": m, "domain": dom, **rec})
    pd.DataFrame(knob_recs).to_csv(HERE / "results/error_by_knob_within_domain.csv", index=False)

    # ---- 3. localise the object x Hindi anomaly ------------------------------
    # v2 (qwen, 4-lang) had object.hi = .553 vs .46-.47 elsewhere. Is it one cell?
    obj = df[df.domain == "object"]
    print("\n=== object: hi vs other-language error rate, by subcategory (per model) ===")
    hi_recs = []
    for m in models:
        om = obj[obj.model == m]
        langs = sorted(om.lang.unique())
        others = [l for l in langs if l != "hi"]
        for cat in SUBCATS["object"]:
            gh = om[(om.subcategory == cat) & (om.lang == "hi")]
            go = om[(om.subcategory == cat) & (om.lang.isin(others))]
            if len(gh) == 0 or len(go) == 0:
                continue
            rh, ro = gh.y.mean(), go.y.mean()
            print(f"  {m} / {cat:<10} hi={rh:.3f} (n={len(gh)})  "
                  f"other={ro:.3f} (n={len(go)})  gap={rh - ro:+.3f}")
            hi_recs.append({"model": m, "subcategory": cat,
                            "hi": round(rh, 3), "hi_n": len(gh),
                            "other": round(ro, 3), "other_n": len(go),
                            "gap": round(rh - ro, 3)})
    print("\n=== object: hi vs other-language error rate, by knob (per model) ===")
    for m in models:
        om = obj[obj.model == m]
        others = [l for l in sorted(om.lang.unique()) if l != "hi"]
        for kb in KNOBS:
            gh = om[(om.knob == kb) & (om.lang == "hi")]
            go = om[(om.knob == kb) & (om.lang.isin(others))]
            if len(gh) == 0 or len(go) == 0:
                continue
            print(f"  {m} / {kb:<16} hi={gh.y.mean():.3f} (n={len(gh)})  "
                  f"other={go.y.mean():.3f} (n={len(go)})  gap={gh.y.mean() - go.y.mean():+.3f}")
    pd.DataFrame(hi_recs).to_csv(HERE / "results/object_hindi_anomaly.csv", index=False)

    # ---- figure: subcategory breakdown, both domains, both models ------------
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    R = pd.DataFrame(sub_recs)
    col = {"qwen7b": "#4C72B0", "internvl8b": "#C44E52"}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, dom in zip(axes, SUBCATS):
        cats = SUBCATS[dom]
        x = range(len(cats)); w = 0.38
        for j, m in enumerate(models):
            sub = R[(R.model == m) & (R.domain == dom)].set_index("subcategory")
            vals = [sub.loc[c, "error_rate"] if c in sub.index else 0 for c in cats]
            lo = [sub.loc[c, "error_rate"] - sub.loc[c, "ci_lo"] if c in sub.index else 0 for c in cats]
            hi = [sub.loc[c, "ci_hi"] - sub.loc[c, "error_rate"] if c in sub.index else 0 for c in cats]
            ax.bar([i + (j - (len(models) - 1) / 2) * w for i in x], vals, w,
                   yerr=[lo, hi], capsize=4, label=m, color=col.get(m, "#55A868"))
        ax.axhline(0.5, ls="--", c="gray", lw=1)
        ax.set_xticks(list(x)); ax.set_xticklabels(cats)
        ax.set_title(dom); ax.set_ylim(0, 0.8)
    axes[0].set_ylabel("prototypicality error rate")
    axes[0].legend(loc="upper left", fontsize=9)
    fig.suptitle("Animal & object bias is subcategory-specific too\n"
                 "(bird/animal & vehicle biased; mammal/furniture near chance; "
                 "ordering replicates across both models)",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(HERE / "figures/figH_subcategory_breakdown.png", dpi=150)
    print("\nsaved figH_subcategory_breakdown.png + results/*.csv")


if __name__ == "__main__":
    main()
