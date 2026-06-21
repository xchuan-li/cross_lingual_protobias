"""Overlay the per-model odds ratios into one cross-model forest plot.

Reads the coefficients_<model>.csv that fit_mixed_effects.py writes and draws
attribute (left) and language (right) ORs for every model side by side, so the
replication across model families is one glance. The PR II money slide.

Usage:  python cross_model_forest.py    (after fit_mixed_effects.py on >=2 models)
"""
import glob
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
COLORS = ["#C44E52", "#4C72B0", "#55A868", "#8172B3"]
SOCIO = ["intellect", "civility", "power", "wealth"]   # baseline morality
LANGS = ["zh", "ru", "ar", "hi", "bn", "el"]           # baseline English


def load():
    out = {}
    for f in sorted(glob.glob(str(HERE / "results/coefficients_*.csv"))):
        m = Path(f).stem[len("coefficients_"):]
        out[m] = pd.read_csv(f)
    return out


def panel(ax, tabs, prefix, order, title):
    models = list(tabs)
    n = len(models)
    for mi, m in enumerate(models):
        t = tabs[m].set_index("term")
        for yi, lvl in enumerate(order):
            term = f"{prefix}{lvl}"
            if term not in t.index:
                continue
            r = t.loc[term]
            # stack models vertically within each level's slot
            y = yi + (mi - (n - 1) / 2) * 0.18
            ax.errorbar(r["odds_ratio"], y,
                        xerr=[[r["odds_ratio"] - r["or_ci_lo"]],
                              [r["or_ci_hi"] - r["odds_ratio"]]],
                        fmt="o", color=COLORS[mi % len(COLORS)], capsize=3,
                        ms=5, label=m if yi == 0 else None)
    ax.axvline(1.0, ls="--", c="gray", lw=1)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order)
    ax.set_xlabel("odds ratio (95% CI)")
    ax.set_title(title, fontsize=10)


def main():
    tabs = load()
    if len(tabs) < 2:
        print(f"need >=2 coefficient files, found {list(tabs)}")
        return
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    panel(axes[0], tabs, "socio_attr_", SOCIO, "attribute OR (vs morality)")
    panel(axes[1], tabs, "lang_", LANGS, "language OR (vs English)")
    axes[0].legend(title="model", fontsize=9)
    fig.suptitle("Cross-model replication: attribute & language effects hold across families",
                 fontsize=13)
    fig.tight_layout()
    out = HERE / "figures/figE_cross_model_OR.png"
    fig.savefig(out, dpi=150)
    print(f"saved {out}")


if __name__ == "__main__":
    main()
