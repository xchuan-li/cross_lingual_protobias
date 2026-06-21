"""Exp3a — statistical confirmation of the attribute-specific bias.

Turns the v2 *point estimates* (wealth=.77, power=.67, ... morality/intellect~.5)
into statistical inference: is the socio_attr effect real, and is the language
effect really null?

Model (demography rows only):
    picked_adversarial ~ socio_attr + lang + gender        (main effects)
    picked_adversarial ~ socio_attr * lang + gender        (interaction)

Each demography item is shown in every language, so observations are not
independent. We honour the "(1 | item)" intent with **item-cluster-robust
(sandwich) standard errors** — valid inference on the fixed effects under
within-item correlation, with no GLMM dependency (this box is Python 3.14 /
PEP 668; statsmodels won't install). If statsmodels *is* available we also fit a
true random-intercept GLMM as a cross-check.

Pure numpy/scipy logistic regression (IRLS) + likelihood-ratio tests.

Outputs (next to this script):
    results/coefficients_<model>.csv   coef, OR, robust SE, z, p, 95% CI
    results/lrt_<model>.csv            LRT for socio_attr / lang / interaction
    figures/figC_attribute_OR_<model>.png   forest plot: the whole story

Usage:
    python fit_mixed_effects.py
    python fit_mixed_effects.py --pred ../../../shared/code/results/predictions_qwen32b.jsonl
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # project root
sys.path.insert(0, str(HERE.parent))  # v3/experiments for protobias_io
from protobias_io import load_rows  # noqa: E402

DEFAULT_PRED = ROOT / "v2/experiments/exp1_900x4lang/results/predictions.jsonl"
SOCIO_ORDER = ["morality", "intellect", "civility", "power", "wealth"]  # baseline=morality
LANG_ORDER = ["en", "zh", "ru", "ar", "hi", "bn", "el"]


# --------------------------------------------------------------------------- #
# data
# --------------------------------------------------------------------------- #
def demography_frame(rows, model):
    df = pd.DataFrame([r for r in rows if r["model"] == model])
    df = df[(df["domain"] == "demography") & df["picked_adversarial"].notna()].copy()
    df = df[df["socio_attr"].notna()]
    df["y"] = df["picked_adversarial"].astype(int)
    # order categories so the dropped (baseline) level is the first listed
    df["socio_attr"] = pd.Categorical(
        df["socio_attr"], [c for c in SOCIO_ORDER if c in set(df["socio_attr"])])
    df["lang"] = pd.Categorical(
        df["lang"], [c for c in LANG_ORDER if c in set(df["lang"])])
    df["gender"] = df["gender"].fillna("NA").astype(str)
    return df


def design(df, terms):
    """Build an intercept + dummy design matrix for the requested terms.

    terms: any of 'socio_attr', 'lang', 'gender', 'socio_attr:lang'.
    Returns (X ndarray, column names).
    """
    cols = {"Intercept": np.ones(len(df))}
    cats = {}
    for t in ("socio_attr", "lang", "gender"):
        if t in terms:
            d = pd.get_dummies(df[t], prefix=t, drop_first=True)
            cats[t] = d
            for c in d.columns:
                cols[c] = d[c].to_numpy(dtype=float)
    if "socio_attr:lang" in terms:
        ds, dl = cats["socio_attr"], cats["lang"]
        for cs in ds.columns:
            for cl in dl.columns:
                cols[f"{cs}:{cl}"] = (ds[cs].to_numpy(float) * dl[cl].to_numpy(float))
    names = list(cols)
    X = np.column_stack([cols[n] for n in names])
    return X, names


# --------------------------------------------------------------------------- #
# logistic regression (IRLS) + cluster-robust covariance + log-likelihood
# --------------------------------------------------------------------------- #
def fit_logit(X, y, groups=None, ridge=1e-6, max_iter=100, tol=1e-10):
    n, p = X.shape
    beta = np.zeros(p)
    R = ridge * np.eye(p)
    R[0, 0] = 0.0  # don't penalise intercept
    for _ in range(max_iter):
        eta = X @ beta
        mu = 1.0 / (1.0 + np.exp(-eta))
        W = np.clip(mu * (1 - mu), 1e-9, None)
        XtWX = X.T @ (W[:, None] * X) + R
        grad = X.T @ (y - mu) - R @ beta
        step = np.linalg.solve(XtWX, grad)
        beta += step
        if np.max(np.abs(step)) < tol:
            break
    eta = X @ beta
    mu = 1.0 / (1.0 + np.exp(-eta))
    W = np.clip(mu * (1 - mu), 1e-9, None)
    bread = np.linalg.inv(X.T @ (W[:, None] * X) + R)          # model-based cov
    # cluster-robust (sandwich) on `groups`
    if groups is not None:
        score = X * (y - mu)[:, None]
        meat = np.zeros((p, p))
        gids = pd.Series(groups)
        for _, idx in gids.groupby(gids).groups.items():
            u = score[np.asarray(idx)].sum(axis=0)
            meat += np.outer(u, u)
        G = gids.nunique()
        cov = bread @ meat @ bread * (G / (G - 1))
    else:
        cov = bread
    ll = float(np.sum(y * np.log(np.clip(mu, 1e-12, 1)) +
                      (1 - y) * np.log(np.clip(1 - mu, 1e-12, 1))))
    return {"beta": beta, "cov": cov, "ll": ll, "p": p}


def lrt(full, reduced):
    stat = 2 * (full["ll"] - reduced["ll"])
    dfree = full["p"] - reduced["p"]
    return stat, dfree, float(stats.chi2.sf(stat, dfree))


# --------------------------------------------------------------------------- #
# reporting
# --------------------------------------------------------------------------- #
def coef_table(fit, names):
    beta, se = fit["beta"], np.sqrt(np.diag(fit["cov"]))
    z = beta / se
    p = 2 * stats.norm.sf(np.abs(z))
    lo, hi = beta - 1.96 * se, beta + 1.96 * se
    return pd.DataFrame({
        "term": names, "coef": beta, "odds_ratio": np.exp(beta),
        "robust_se": se, "z": z, "p_value": p,
        "or_ci_lo": np.exp(lo), "or_ci_hi": np.exp(hi),
    })


def forest_plot(tab, model, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    socio = tab[tab["term"].str.startswith("socio_attr_")].copy()
    lang = tab[tab["term"].str.startswith("lang_")].copy()
    socio["label"] = socio["term"].str.replace("socio_attr_", "", regex=False)
    lang["label"] = lang["term"].str.replace("lang_", "", regex=False)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2),
                             gridspec_kw={"width_ratios": [1, 1]})
    for ax, sub, title, base in (
        (axes[0], socio, "socio_attr odds ratio (vs morality)", "morality"),
        (axes[1], lang, "language odds ratio (vs English)", "English"),
    ):
        sub = sub.iloc[::-1]
        yv = range(len(sub))
        ax.errorbar(sub["odds_ratio"], yv,
                    xerr=[sub["odds_ratio"] - sub["or_ci_lo"],
                          sub["or_ci_hi"] - sub["odds_ratio"]],
                    fmt="o", color="#C44E52", capsize=4)
        ax.axvline(1.0, ls="--", c="gray", lw=1)
        ax.set_yticks(list(yv))
        ax.set_yticklabels(sub["label"])
        ax.set_xlabel("odds ratio (95% CI)")
        ax.set_title(title, fontsize=10)
    fig.suptitle(f"Attribute moves the bias, language does not — {model}", fontsize=12)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def maybe_glmm(df):
    """Optional true random-intercept GLMM cross-check, if statsmodels exists."""
    try:
        from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
    except Exception:
        return None
    try:
        md = BinomialBayesMixedGLM.from_formula(
            "y ~ C(socio_attr) + C(lang) + C(gender)", {"item": "0 + C(id)"}, df)
        res = md.fit_vb()
        return str(res.summary())
    except Exception as e:
        return f"(GLMM cross-check failed: {e})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", nargs="+", default=[str(DEFAULT_PRED)],
                    help="prediction jsonl file(s)")
    args = ap.parse_args()

    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "figures").mkdir(exist_ok=True)
    rows = load_rows(args.pred)
    models = sorted({r["model"] for r in rows})

    for model in models:
        df = demography_frame(rows, model)
        if len(df) < 50:
            print(f"[{model}] too few demography rows ({len(df)}), skipping")
            continue
        print(f"\n===== {model}: {len(df)} demography predictions "
              f"({df['item'].nunique()} items x {df['lang'].nunique()} langs) =====")

        y = df["y"].to_numpy(float)
        item = df["item"].to_numpy()

        # fits
        X_g, _ = design(df, ["gender"])
        X_s, _ = design(df, ["socio_attr", "gender"])
        X_l, _ = design(df, ["lang", "gender"])
        X_m, n_m = design(df, ["socio_attr", "lang", "gender"])
        X_i, _ = design(df, ["socio_attr", "lang", "gender", "socio_attr:lang"])
        f_g = fit_logit(X_g, y, item)
        f_s = fit_logit(X_s, y, item)
        f_l = fit_logit(X_l, y, item)
        f_m = fit_logit(X_m, y, item)
        f_i = fit_logit(X_i, y, item)

        # main-effects coefficient table (cluster-robust)
        tab = coef_table(f_m, n_m)
        tab.insert(0, "model", model)
        tab.to_csv(HERE / f"results/coefficients_{model}.csv", index=False)
        show = tab[tab["term"].str.startswith(("socio_attr_", "lang_"))]
        print("\n-- main-effects odds ratios (item-cluster-robust 95% CI) --")
        for _, r in show.iterrows():
            sig = "*" if r["p_value"] < 0.05 else " "
            print(f"  {sig} {r['term']:<22} OR={r['odds_ratio']:.2f} "
                  f"[{r['or_ci_lo']:.2f}, {r['or_ci_hi']:.2f}]  p={r['p_value']:.3g}")

        # likelihood-ratio tests
        lrt_rows = []
        for name, full, red in (
            ("socio_attr (vs lang+gender)", f_m, f_l),
            ("lang (vs socio_attr+gender)", f_m, f_s),
            ("socio_attr x lang interaction", f_i, f_m),
        ):
            stat, dfree, pv = lrt(full, red)
            lrt_rows.append({"test": name, "chi2": stat, "df": dfree, "p_value": pv})
        lrt_df = pd.DataFrame(lrt_rows)
        lrt_df.insert(0, "model", model)
        lrt_df.to_csv(HERE / f"results/lrt_{model}.csv", index=False)
        print("\n-- likelihood-ratio tests --")
        for _, r in lrt_df.iterrows():
            verdict = "SIGNIFICANT" if r["p_value"] < 0.05 else "n.s."
            print(f"  {r['test']:<34} chi2={r['chi2']:7.2f} df={int(r['df'])} "
                  f"p={r['p_value']:.3g}  -> {verdict}")

        forest_plot(tab, model, HERE / f"figures/figC_attribute_OR_{model}.png")
        print(f"  saved figC_attribute_OR_{model}.png")

        glmm = maybe_glmm(df)
        if glmm:
            print("\n-- optional GLMM (1|item) cross-check --\n", glmm)


if __name__ == "__main__":
    main()
