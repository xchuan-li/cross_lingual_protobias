"""Exp3f — do the two model families err on the SAME items?

Aggregate patterns already replicate across Qwen2.5-VL-7B and InternVL3-8B. The
sharper question: is it the *same image pairs* that fool both models?
  high agreement / correlation  -> the prototype trap is item-intrinsic (an
        objective property of the image pair), not a model quirk.
  low                            -> the bias is model-specific.

Pure analysis of existing predictions (no GPU).
Usage:  python agreement.py
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
from protobias_io import load_rows  # noqa: E402

DEFAULT = [str(ROOT / "shared/code/results/predictions_qwen7b.jsonl"),
           str(ROOT / "shared/code/results/predictions_internvl8b.jsonl")]


def kappa(a, b):
    """Cohen's kappa for two 0/1 raters + observed/chance agreement."""
    po = float((a == b).mean())
    pa, pb = a.mean(), b.mean()
    pe = pa * pb + (1 - pa) * (1 - pb)
    k = (po - pe) / (1 - pe) if pe < 1 else float("nan")
    return k, po, pe


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pred", nargs="+", default=DEFAULT)
    args = ap.parse_args()
    (HERE / "figures").mkdir(exist_ok=True); (HERE / "results").mkdir(exist_ok=True)
    rows = load_rows(args.pred)
    df = pd.DataFrame([r for r in rows if r["picked_adversarial"] is not None])
    df["y"] = df["picked_adversarial"].astype(int)
    models = sorted(df["model"].unique())
    if len(models) < 2:
        raise SystemExit("need 2 models")
    m0, m1 = models[:2]

    # ---- (item, language)-level agreement ----
    p = df.pivot_table(index=["item", "lang"], columns="model", values="y", aggfunc="mean")
    p = p.dropna(subset=[m0, m1])
    a = p[m0].astype(int).values; b = p[m1].astype(int).values
    k, po, pe = kappa(a, b)
    print(f"\n=== (item,language)-level agreement  [{m0} vs {m1}] ===")
    print(f"  matched decisions: {len(a)}")
    print(f"  observed agreement = {po:.3f}   chance = {pe:.3f}   Cohen's kappa = {k:.3f}")

    # ---- item-level error-rate correlation (mean over languages) ----
    item = df.groupby(["item", "model"]).y.mean().unstack().dropna(subset=[m0, m1])
    r, pr = stats.pearsonr(item[m0], item[m1])
    rs, ps = stats.spearmanr(item[m0], item[m1])
    print(f"\n=== item-level error-rate correlation ({len(item)} items) ===")
    print(f"  Pearson r  = {r:.3f}  (p={pr:.1e})")
    print(f"  Spearman ρ = {rs:.3f}  (p={ps:.1e})")

    # ---- agreement by domain ----
    dom = df[["item", "lang", "domain"]].drop_duplicates().set_index(["item", "lang"])
    pj = p.join(dom)
    print("\n=== agreement by domain ===")
    drecs = []
    for d, g in pj.groupby("domain"):
        kk, poo, pee = kappa(g[m0].astype(int).values, g[m1].astype(int).values)
        print(f"  {d:<12} n={len(g):<5} agreement={poo:.3f}  kappa={kk:.3f}")
        drecs.append({"domain": d, "n": len(g), "agreement": round(poo, 3), "kappa": round(kk, 3)})

    pd.DataFrame([{"level": "item×lang", "n": len(a), "agreement": round(po, 3),
                   "chance": round(pe, 3), "kappa": round(k, 3),
                   "item_pearson_r": round(r, 3), "item_spearman_r": round(rs, 3)}]
                 ).to_csv(HERE / "results/agreement_summary.csv", index=False)
    pd.DataFrame(drecs).to_csv(HERE / "results/agreement_by_domain.csv", index=False)

    # ---- scatter: per-item error rates, model vs model ----
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    jit = (np.random.default_rng(0).random(len(item)) - 0.5) * 0  # no jitter (determinism)
    fig, ax = plt.subplots(figsize=(5.4, 5.2))
    ax.scatter(item[m0] + jit, item[m1] + jit, s=12, alpha=0.25, color="#4C72B0",
               edgecolors="none")
    ax.plot([0, 1], [0, 1], ls="--", c="gray", lw=1)
    ax.set_xlabel(f"{m0} — per-item error rate")
    ax.set_ylabel(f"{m1} — per-item error rate")
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
    ax.set_title(f"Same items, both models  (Pearson r = {r:.2f})")
    fig.tight_layout(); fig.savefig(HERE / "figures/figG_item_agreement.png", dpi=150)
    print("\nsaved figG_item_agreement.png + results/*.csv")


if __name__ == "__main__":
    main()
