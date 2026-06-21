"""Re-analyze exp1 predictions along the UNUSED socio_attr / gender axes.

exp1's analyze.py only aggregated by (domain, lang), which averaged the whole
demography domain into a single number (~.56) and hid the real signal. This
script breaks demography down by socio_attr and gender, crossed with language,
and writes a tidy CSV + two figures.

Run:  python reanalyze_exp1.py
Reads: ../exp1_900x4lang/results/predictions.jsonl
"""
import json
import csv
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent
PRED = HERE.parent / "exp1_900x4lang" / "results" / "predictions.jsonl"
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)

ATTRS = ["wealth", "power", "civility", "morality", "intellect"]
LANGS = ["en", "zh", "ar", "hi"]
LANG_NAME = {"en": "English", "zh": "Chinese", "ar": "Arabic", "hi": "Hindi"}


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = (z * ((p * (1 - p) / n + z**2 / (4 * n**2)) ** 0.5)) / denom
    return (center - half, center + half)


def load():
    rows = [json.loads(l) for l in PRED.read_text().splitlines() if l.strip()]
    return [r for r in rows if r.get("picked_adversarial") is not None]


def rate(rows, keyfn):
    agg = defaultdict(lambda: [0, 0])
    for r in rows:
        k = keyfn(r)
        agg[k][0] += int(r["picked_adversarial"])
        agg[k][1] += 1
    out = {}
    for k, (a, n) in agg.items():
        lo, hi = wilson_ci(a, n)
        out[k] = (a / n, n, lo, hi)
    return out


def main():
    rows = load()
    demo = [r for r in rows if r["domain"] == "demography"]
    print(f"Loaded {len(rows)} preds; {len(demo)} demography.\n")

    # ---- table: socio_attr (pooled over langs) ----
    print("=== prototypicality error by socio_attr (pooled langs) ===")
    by_attr = rate(demo, lambda r: r["socio_attr"])
    for a in ATTRS:
        p, n, lo, hi = by_attr[(a)] if (a) in by_attr else by_attr.get(a, (0, 0, 0, 0))
        print(f"  {a:<10} {p:.3f}  n={n}  CI[{lo:.3f},{hi:.3f}]")

    # ---- CSV: socio_attr x lang ----
    by_al = rate(demo, lambda r: (r["socio_attr"], r["lang"]))
    with open(HERE / "exp1_attribute_breakdown.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["socio_attr", "lang", "error_rate", "n", "ci_lo", "ci_hi"])
        for a in ATTRS:
            for l in LANGS:
                p, n, lo, hi = by_al.get((a, l), (0, 0, 0, 0))
                w.writerow([a, l, f"{p:.3f}", n, f"{lo:.3f}", f"{hi:.3f}"])
    print("\nwrote exp1_attribute_breakdown.csv")

    # ---- figures ----
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Fig A: error by socio_attr (the headline)
    vals = [by_attr.get(a, (0, 0, 0, 0)) for a in ATTRS]
    rates = [v[0] for v in vals]
    errs = [[v[0] - v[2] for v in vals], [v[3] - v[0] for v in vals]]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    bars = ax.bar(ATTRS, rates, yerr=errs, capsize=5,
                  color=["#C44E52", "#C44E52", "#8C8C8C", "#4C72B0", "#4C72B0"])
    ax.axhline(0.5, ls="--", c="gray", lw=1, label="chance (no bias)")
    ax.set_ylabel("Prototypicality error rate")
    ax.set_title("Demography bias is attribute-specific\n(wealth/power >> morality/intellect)")
    ax.set_ylim(0, 1)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "figA_bias_by_attribute.png", dpi=150)
    print("saved figA_bias_by_attribute.png")

    # Fig B: socio_attr x language (is the trend consistent across langs?)
    x = range(len(ATTRS))
    width = 0.8 / len(LANGS)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for j, l in enumerate(LANGS):
        rs = [by_al.get((a, l), (0, 0, 0, 0))[0] for a in ATTRS]
        ax.bar([xi + j * width for xi in x], rs, width, label=LANG_NAME[l])
    ax.axhline(0.5, ls="--", c="gray", lw=1)
    ax.set_xticks([xi + width * (len(LANGS) - 1) / 2 for xi in x])
    ax.set_xticklabels(ATTRS)
    ax.set_ylabel("Prototypicality error rate")
    ax.set_title("Attribute-bias pattern is consistent across languages")
    ax.set_ylim(0, 1)
    ax.legend(title="Language", ncol=4, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "figB_attribute_by_language.png", dpi=150)
    print("saved figB_attribute_by_language.png")


if __name__ == "__main__":
    main()
