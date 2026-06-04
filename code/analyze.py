"""Aggregate predictions and produce the two key figures + a summary table.

Metric = prototypicality error rate = mean(picked_adversarial).

Outputs:
  figures/fig1_bias_by_language.png        (RQ1)
  figures/fig2_bias_by_domain_language.png (RQ2)
  results/summary.csv

Usage:  python analyze.py
"""
import json

import config


def load_predictions():
    rows = []
    for line in config.PREDICTIONS_PATH.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    # drop unparseable
    return [r for r in rows if r.get("picked_adversarial") is not None]


def wilson_ci(k, n, z=1.96):
    """95% Wilson score interval half-width-ish; returns (lo, hi)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = (z * ((p * (1 - p) / n + z**2 / (4 * n**2)) ** 0.5)) / denom
    return (center - half, center + half)


def rate_table(rows, keys):
    """Return dict[key_tuple] = (rate, n, lo, hi)."""
    from collections import defaultdict
    agg = defaultdict(lambda: [0, 0])  # [adv_count, n]
    for r in rows:
        key = tuple(r[k] for k in keys)
        agg[key][0] += int(r["picked_adversarial"])
        agg[key][1] += 1
    out = {}
    for key, (k, n) in agg.items():
        lo, hi = wilson_ci(k, n)
        out[key] = (k / n, n, lo, hi)
    return out


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import csv

    rows = load_predictions()
    print(f"Loaded {len(rows)} valid predictions.")

    langs = [l for l in config.ACTIVE_LANGUAGES]
    lang_names = [config.LANGUAGES[l]["name"] for l in langs]

    # ---- Figure 1: error rate by language (RQ1) ----
    t1 = rate_table(rows, ["lang"])
    vals = [t1.get((l,), (0, 0, 0, 0)) for l in langs]
    rates = [v[0] for v in vals]
    errs = [[v[0] - v[2] for v in vals], [v[3] - v[0] for v in vals]]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(lang_names, rates, yerr=errs, capsize=5, color="#4C72B0")
    ax.axhline(0.5, ls="--", c="gray", lw=1, label="chance (0.5)")
    ax.set_ylabel("Prototypicality error rate\n(% adversarial image chosen)")
    ax.set_title("RQ1: Prototypicality bias by language")
    ax.set_ylim(0, 1)
    ax.legend()
    fig.tight_layout()
    fig.savefig(config.FIGURES_DIR / "fig1_bias_by_language.png", dpi=150)
    print("saved fig1")

    # ---- Figure 2: error rate by domain x language (RQ2) ----
    t2 = rate_table(rows, ["domain", "lang"])
    domains = config.DOMAINS
    x = range(len(domains))
    width = 0.8 / len(langs)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for j, l in enumerate(langs):
        rs = [t2.get((d, l), (0, 0, 0, 0))[0] for d in domains]
        ax.bar([xi + j * width for xi in x], rs, width,
               label=config.LANGUAGES[l]["name"])
    ax.axhline(0.5, ls="--", c="gray", lw=1)
    ax.set_xticks([xi + width * (len(langs) - 1) / 2 for xi in x])
    ax.set_xticklabels(domains)
    ax.set_ylabel("Prototypicality error rate")
    ax.set_title("RQ2: Prototypicality bias by domain x language")
    ax.set_ylim(0, 1)
    ax.legend(title="Language")
    fig.tight_layout()
    fig.savefig(config.FIGURES_DIR / "fig2_bias_by_domain_language.png", dpi=150)
    print("saved fig2")

    # ---- summary.csv ----
    with open(config.RESULTS_DIR / "summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["domain", "lang", "error_rate", "n", "ci_lo", "ci_hi"])
        for (d, l), (rate, n, lo, hi) in sorted(t2.items()):
            w.writerow([d, l, f"{rate:.3f}", n, f"{lo:.3f}", f"{hi:.3f}"])
    print("saved results/summary.csv")

    # console table
    print("\n=== error rate by language ===")
    for l in langs:
        rate, n, lo, hi = t1.get((l,), (0, 0, 0, 0))
        print(f"  {config.LANGUAGES[l]['name']:<8} {rate:.3f}  (n={n}, 95% CI [{lo:.3f}, {hi:.3f}])")


if __name__ == "__main__":
    main()
