"""Exp3b — cross-lingual behavioural metrics (proposal_new.md §7).

Beyond the per-language error rate, these summarise an item's behaviour *across*
languages (so they need the correct per-item key — see protobias_io):

  CFR  Cross-lingual Flip Rate   P(choice changes across languages)
  SBR  Stable Bias Rate          P(adversarial chosen in ALL languages)
  SCR  Stable Correct Rate       P(correct chosen in ALL languages)   [= 1-CFR-SBR]

A high SBR with a low CFR is the strong reading of "language-invariant bias":
the model is not flip-flopping with language, it is *stably* biased. Reported by
domain and (for demography) by socio_attr, per model.

Also audits data quality: per-language parse-failure rate (raw_choice not 1/2) —
this is the "is it just bad prompts/translation?" QA backstop.

Outputs (next to this script):
  results/xlingual_metrics.csv     model, group_type, group, n_items, CFR, SBR, SCR
  results/parse_failure.csv        model, lang, n_total, n_fail, fail_rate
  figures/figD_flip_stable_<model>.png

Usage:
  python compute_xlingual_metrics.py
  python compute_xlingual_metrics.py --pred ../../../shared/code/results/predictions_*.jsonl
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
from protobias_io import load_rows  # noqa: E402

DEFAULT_PRED = ROOT / "v2/experiments/exp1_900x4lang/results/predictions.jsonl"
DOMAINS = ["animal", "object", "demography"]


def item_level(df):
    """One row per item: the set of choices across its languages."""
    recs = []
    for item, g in df.groupby("item"):
        picks = g["picked_adversarial"].tolist()
        if len(picks) < 2:
            continue  # need >=2 languages to talk about flips
        recs.append({
            "item": item,
            "domain": g["domain"].iloc[0],
            "socio_attr": g["socio_attr"].iloc[0],
            "n_langs": len(picks),
            "flip": len(set(picks)) > 1,
            "stable_adv": all(picks),
            "stable_correct": not any(picks),
        })
    return pd.DataFrame(recs)


def summarise(items, group_type, group_col=None):
    out = []
    if group_type == "overall":
        groups = [("all", items)]
    else:
        groups = list(items.groupby(group_col))
    for name, g in groups:
        if group_type == "socio_attr" and (name is None or pd.isna(name)):
            continue
        out.append({
            "group_type": group_type, "group": name, "n_items": len(g),
            "CFR": round(g["flip"].mean(), 3),
            "SBR": round(g["stable_adv"].mean(), 3),
            "SCR": round(g["stable_correct"].mean(), 3),
        })
    return out


def parse_failure(raw):
    out = []
    for lang, g in raw.groupby("lang"):
        ok = g["raw_choice"].isin([1, 2]).sum()
        n = len(g)
        out.append({"lang": lang, "n_total": int(n), "n_fail": int(n - ok),
                    "fail_rate": round((n - ok) / n, 4) if n else 0.0})
    return out


def figure(items, model, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    doms = [d for d in DOMAINS if d in set(items["domain"])]
    cfr = [items[items.domain == d]["flip"].mean() for d in doms]
    sbr = [items[items.domain == d]["stable_adv"].mean() for d in doms]
    x = range(len(doms))
    w = 0.38
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.bar([i - w / 2 for i in x], cfr, w, label="CFR (flips across langs)", color="#4C72B0")
    ax.bar([i + w / 2 for i in x], sbr, w, label="SBR (adversarial in ALL langs)", color="#C44E52")
    ax.set_xticks(list(x))
    ax.set_xticklabels(doms)
    ax.set_ylabel("rate")
    ax.set_ylim(0, 1)
    ax.set_title(f"Cross-lingual flip vs stable bias by domain — {model}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", nargs="+", default=[str(DEFAULT_PRED)])
    args = ap.parse_args()

    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "figures").mkdir(exist_ok=True)
    rows = load_rows(args.pred)
    raw = pd.DataFrame(rows)
    models = sorted(raw["model"].unique())

    metric_rows, pf_rows = [], []
    for model in models:
        mraw = raw[raw["model"] == model]
        parseable = mraw[mraw["picked_adversarial"].notna()].copy()
        items = item_level(parseable)
        if items.empty:
            print(f"[{model}] no multi-language items, skipping")
            continue

        print(f"\n===== {model}: {len(items)} items with >=2 languages =====")
        summ = (summarise(items, "overall")
                + summarise(items, "domain", "domain")
                + summarise(items, "socio_attr", "socio_attr"))
        for s in summ:
            s["model"] = model
            metric_rows.append(s)
            print(f"  {s['group_type']:<11} {str(s['group']):<12} "
                  f"n={s['n_items']:<4} CFR={s['CFR']:.3f}  SBR={s['SBR']:.3f}  SCR={s['SCR']:.3f}")

        for pf in parse_failure(mraw):
            pf["model"] = model
            pf_rows.append(pf)

        figure(items, model, HERE / f"figures/figD_flip_stable_{model}.png")
        print(f"  saved figD_flip_stable_{model}.png")

    cols = ["model", "group_type", "group", "n_items", "CFR", "SBR", "SCR"]
    pd.DataFrame(metric_rows)[cols].to_csv(HERE / "results/xlingual_metrics.csv", index=False)
    pd.DataFrame(pf_rows)[["model", "lang", "n_total", "n_fail", "fail_rate"]].to_csv(
        HERE / "results/parse_failure.csv", index=False)
    print("\nsaved results/xlingual_metrics.csv + results/parse_failure.csv")

    print("\n=== parse-failure by language ===")
    for pf in pf_rows:
        print(f"  {pf['model']:<10} {pf['lang']:<4} {pf['n_fail']}/{pf['n_total']} "
              f"({pf['fail_rate']*100:.2f}%)")


if __name__ == "__main__":
    main()
