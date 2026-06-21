"""Exp3e — is it prototypicality, or a low-level knob artifact?

Every adversarial image also manipulates one visual `knob` (count / color_tone /
layout_relation / spatial / scale_size). If the bias were really just the model
reacting to, say, a colour difference, the error rate would spike on one knob.
If it is roughly uniform across knobs — and the wealth>morality gap survives
*within* a knob — the bias is genuine prototypicality, not a single visual cue.

Pure analysis of existing predictions (no GPU).
Usage:  python analyze_knob.py
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
KNOBS = ["count", "color_tone", "layout_relation", "spatial", "scale_size"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (c - h, c + h)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pred", nargs="+", default=DEFAULT)
    args = ap.parse_args()
    (HERE / "figures").mkdir(exist_ok=True); (HERE / "results").mkdir(exist_ok=True)
    rows = load_rows(args.pred)
    df = pd.DataFrame([r for r in rows if r["picked_adversarial"] is not None])
    df["y"] = df["picked_adversarial"].astype(int)
    models = sorted(df["model"].unique())
    knobs = [k for k in KNOBS if k in set(df["knob"].dropna())]

    recs = []
    for m in models:
        d = df[df.model == m]
        print(f"\n=== {m}: error rate by knob (all domains, pooled languages) ===")
        for kb in knobs:
            g = d[d.knob == kb]; k = int(g.y.sum()); n = len(g)
            lo, hi = wilson(k, n)
            print(f"  {kb:<16} {k/n:.3f}  (n={n}, 95% CI [{lo:.3f}, {hi:.3f}])")
            recs.append({"model": m, "knob": kb, "error_rate": round(k / n, 3),
                         "n": n, "ci_lo": round(lo, 3), "ci_hi": round(hi, 3)})
    pd.DataFrame(recs).to_csv(HERE / "results/error_by_knob.csv", index=False)

    # Is the wealth effect confounded with a particular knob?
    dem = df[(df.domain == "demography") & (df.model == models[0]) & (df.lang == "en")]
    ct = pd.crosstab(dem.socio_attr, dem.knob)
    print(f"\n=== socio_attr × knob item counts (demography, en, {models[0]}) ===")
    print(ct.to_string())
    ct.to_csv(HERE / "results/socio_attr_by_knob.csv")

    # Does wealth > morality hold *within* each knob? (controls the knob)
    print("\n=== wealth vs morality error rate WITHIN each knob (demography, pooled) ===")
    dd = df[df.domain == "demography"]
    wk = []
    for kb in knobs:
        row = {"knob": kb}
        for attr in ["wealth", "morality"]:
            g = dd[(dd.knob == kb) & (dd.socio_attr == attr)]
            row[attr] = round(g.y.mean(), 3) if len(g) else None
            row[attr + "_n"] = len(g)
        if row.get("wealth") is not None and row.get("morality") is not None:
            print(f"  {kb:<16} wealth={row['wealth']:.3f} (n={row['wealth_n']})   "
                  f"morality={row['morality']:.3f} (n={row['morality_n']})   "
                  f"gap={row['wealth'] - row['morality']:+.3f}")
        wk.append(row)
    pd.DataFrame(wk).to_csv(HERE / "results/wealth_vs_morality_by_knob.csv", index=False)

    # figure
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    R = pd.DataFrame(recs)
    x = range(len(knobs)); w = 0.38; col = ["#4C72B0", "#C44E52", "#55A868"]
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    for j, m in enumerate(models):
        vals = [(R[(R.model == m) & (R.knob == kb)].error_rate.values[:1] or [0])[0] for kb in knobs]
        ax.bar([i + (j - (len(models) - 1) / 2) * w for i in x], vals, w, label=m, color=col[j % 3])
    ax.axhline(0.5, ls="--", c="gray", lw=1, label="chance")
    ax.set_xticks(list(x)); ax.set_xticklabels(knobs, rotation=12)
    ax.set_ylabel("prototypicality error rate"); ax.set_ylim(0, 0.8)
    ax.set_title("Bias scales with how hard the cue is to perceive — colour (the artifact worry) is lowest")
    ax.legend()
    fig.tight_layout(); fig.savefig(HERE / "figures/figF_error_by_knob.png", dpi=150)
    print("\nsaved figF_error_by_knob.png + results/*.csv")


if __name__ == "__main__":
    main()
