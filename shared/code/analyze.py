"""Aggregate predictions and produce the key figures + a summary table.

Metric = prototypicality error rate = mean(picked_adversarial).

Reads every results/predictions_<model>.jsonl, so a multi-model run (one SLURM
job per model) is analysed together.

Outputs (in figures/):
  <model>_fig1_bias_by_language.png        per-model, RQ1
  <model>_fig2_bias_by_domain_language.png per-model, RQ2
  fig_by_model_overall.png                 cross-model: overall error rate
  fig_by_model_domain.png                  cross-model: error rate by domain
And results/summary.csv with a `model` column.

Usage:  python analyze.py
"""
import json

import config


def load_predictions():
    """Load all per-model prediction files; tag each row with its model."""
    rows = []
    for path in sorted(config.RESULTS_DIR.glob("predictions_*.jsonl")):
        model_key = path.stem[len("predictions_"):]
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            r.setdefault("model", model_key)  # self-describing, but fall back
            rows.append(r)
    # drop unparseable
    return [r for r in rows if r.get("picked_adversarial") is not None]


def wilson_ci(k, n, z=1.96):
    """95% Wilson score interval; returns (lo, hi)."""
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


def present(rows, field, ordered):
    """Values of `field` that actually occur, in a stable preferred order."""
    seen = {r[field] for r in rows}
    out = [v for v in ordered if v in seen]
    out += [v for v in sorted(seen) if v not in out]
    return out


def per_model_figures(plt, rows, model, langs):
    """The original two figures, for one model."""
    lang_names = [config.LANGUAGES[l]["name"] for l in langs]

    # ---- Figure 1: error rate by language (RQ1) ----
    t1 = rate_table(rows, ["lang"])
    vals = [t1.get((l,), (0, 0, 0, 0)) for l in langs]
    rates = [v[0] for v in vals]
    errs = [[v[0] - v[2] for v in vals], [v[3] - v[0] for v in vals]]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(lang_names, rates, yerr=errs, capsize=4, color="#4C72B0")
    ax.axhline(0.5, ls="--", c="gray", lw=1, label="chance (0.5)")
    ax.set_ylabel("Prototypicality error rate\n(% adversarial image chosen)")
    ax.set_title(f"RQ1: Prototypicality bias by language — {model}")
    ax.set_ylim(0, 1)
    ax.legend()
    fig.tight_layout()
    fig.savefig(config.FIGURES_DIR / f"{model}_fig1_bias_by_language.png", dpi=150)
    plt.close(fig)

    # ---- Figure 2: error rate by domain x language (RQ2) ----
    t2 = rate_table(rows, ["domain", "lang"])
    domains = config.DOMAINS
    x = range(len(domains))
    width = 0.8 / max(len(langs), 1)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for j, l in enumerate(langs):
        rs = [t2.get((d, l), (0, 0, 0, 0))[0] for d in domains]
        ax.bar([xi + j * width for xi in x], rs, width,
               label=config.LANGUAGES[l]["name"])
    ax.axhline(0.5, ls="--", c="gray", lw=1)
    ax.set_xticks([xi + width * (len(langs) - 1) / 2 for xi in x])
    ax.set_xticklabels(domains)
    ax.set_ylabel("Prototypicality error rate")
    ax.set_title(f"RQ2: Prototypicality bias by domain x language — {model}")
    ax.set_ylim(0, 1)
    ax.legend(title="Language", ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(config.FIGURES_DIR / f"{model}_fig2_bias_by_domain_language.png", dpi=150)
    plt.close(fig)


def cross_model_figures(plt, rows, models):
    """New for PR II: does the bias replicate across models?"""
    # ---- overall error rate per model ----
    t = rate_table(rows, ["model"])
    vals = [t.get((m,), (0, 0, 0, 0)) for m in models]
    rates = [v[0] for v in vals]
    errs = [[v[0] - v[2] for v in vals], [v[3] - v[0] for v in vals]]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(models, rates, yerr=errs, capsize=5, color="#55A868")
    ax.axhline(0.5, ls="--", c="gray", lw=1, label="chance (0.5)")
    ax.set_ylabel("Prototypicality error rate")
    ax.set_title("Cross-model: overall prototypicality bias")
    ax.set_ylim(0, 1)
    ax.legend()
    fig.tight_layout()
    fig.savefig(config.FIGURES_DIR / "fig_by_model_overall.png", dpi=150)
    plt.close(fig)

    # ---- error rate by domain x model ----
    t2 = rate_table(rows, ["domain", "model"])
    domains = config.DOMAINS
    x = range(len(domains))
    width = 0.8 / max(len(models), 1)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for j, m in enumerate(models):
        rs = [t2.get((d, m), (0, 0, 0, 0))[0] for d in domains]
        ax.bar([xi + j * width for xi in x], rs, width, label=m)
    ax.axhline(0.5, ls="--", c="gray", lw=1)
    ax.set_xticks([xi + width * (len(models) - 1) / 2 for xi in x])
    ax.set_xticklabels(domains)
    ax.set_ylabel("Prototypicality error rate")
    ax.set_title("Cross-model: prototypicality bias by domain")
    ax.set_ylim(0, 1)
    ax.legend(title="Model")
    fig.tight_layout()
    fig.savefig(config.FIGURES_DIR / "fig_by_model_domain.png", dpi=150)
    plt.close(fig)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import csv

    rows = load_predictions()
    print(f"Loaded {len(rows)} valid predictions.")
    if not rows:
        raise SystemExit("No predictions found. Run run_eval.py first.")

    models = present(rows, "model", list(config.MODELS))
    langs = present(rows, "lang", config.ACTIVE_LANGUAGES)
    print(f"Models: {models}")
    print(f"Languages: {langs}")

    # ---- per-model figures ----
    for m in models:
        mrows = [r for r in rows if r["model"] == m]
        mlangs = present(mrows, "lang", config.ACTIVE_LANGUAGES)
        per_model_figures(plt, mrows, m, mlangs)
        print(f"saved {m}_fig1 / {m}_fig2")

    # ---- cross-model figures ----
    if len(models) > 1:
        cross_model_figures(plt, rows, models)
        print("saved fig_by_model_overall / fig_by_model_domain")

    # ---- summary.csv (model x domain x lang) ----
    t = rate_table(rows, ["model", "domain", "lang"])
    with open(config.RESULTS_DIR / "summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "domain", "lang", "error_rate", "n", "ci_lo", "ci_hi"])
        for (m, d, l), (rate, n, lo, hi) in sorted(t.items()):
            w.writerow([m, d, l, f"{rate:.3f}", n, f"{lo:.3f}", f"{hi:.3f}"])
    print("saved results/summary.csv")

    # ---- console table: overall error rate by model ----
    tm = rate_table(rows, ["model"])
    print("\n=== overall error rate by model ===")
    for m in models:
        rate, n, lo, hi = tm.get((m,), (0, 0, 0, 0))
        print(f"  {m:<12} {rate:.3f}  (n={n}, 95% CI [{lo:.3f}, {hi:.3f}])")


if __name__ == "__main__":
    main()
