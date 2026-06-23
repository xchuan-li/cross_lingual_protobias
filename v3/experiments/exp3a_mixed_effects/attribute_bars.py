"""Refresh the attribute-breakdown bar chart on the NEW 7-language data, in the
same style as v2's figA (red = social-status attributes, blue = moral/cognitive,
grey = civility), so the deck shows the current run rather than the 4-lang one.

Usage:  python attribute_bars.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRED = ROOT / "shared/code/results/predictions_qwen7b.jsonl"
ORDER = ["wealth", "power", "civility", "morality", "intellect"]
COLORS = {"wealth": "#C44E52", "power": "#C44E52", "civility": "#9AA0B0",
          "morality": "#4C72B0", "intellect": "#4C72B0"}


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return c - h, c + h


def main():
    agg = {a: [0, 0] for a in ORDER}
    for line in open(PRED):
        r = json.loads(line)
        if r["domain"] == "demography" and r["socio_attr"] in agg and r["picked_adversarial"] is not None:
            agg[r["socio_attr"]][0] += int(r["picked_adversarial"]); agg[r["socio_attr"]][1] += 1
    rates = {a: agg[a][0] / agg[a][1] for a in ORDER}
    err_lo = [rates[a] - wilson(agg[a][0], agg[a][1])[0] for a in ORDER]
    err_hi = [wilson(agg[a][0], agg[a][1])[1] - rates[a] for a in ORDER]

    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    ax.bar(ORDER, [rates[a] for a in ORDER], yerr=[err_lo, err_hi], capsize=5,
           color=[COLORS[a] for a in ORDER])
    ax.axhline(0.5, ls="--", c="gray", lw=1, label="chance (no bias)")
    ax.set_ylabel("Prototypicality error rate")
    ax.set_ylim(0, 1)
    ax.set_title("Demography bias is attribute-specific\n(wealth/power >> morality/intellect)")
    ax.legend()
    fig.tight_layout()
    out = HERE / "figures/figA7_attribute_qwen7lang.png"
    fig.savefig(out, dpi=150)
    print("saved", out)
    for a in ORDER:
        print(f"  {a:<10} {rates[a]:.3f} (n={agg[a][1]})")


if __name__ == "__main__":
    main()
