# v3 experiments — no-GPU analysis (PR II)

Three CPU-only analyses that turn the existing predictions into PR-II-grade
results. They run **now** on the v2 exp1 data (3600 rows, en/zh/ar/hi, qwen7b)
and re-run unchanged on the weekend multi-model / 7-language data.

**Deps:** numpy, scipy, pandas, matplotlib (all already present). Optional:
`sacrebleu` (adds chrF to the translation audit). No statsmodels needed — the
stats are implemented in numpy/scipy (this box is py3.14 / PEP-668).

Shared loader `protobias_io.py` fixes a data trap: the `id` field is **not**
unique. The correct per-item key is the dataset row index (new runs store it as
`item`; for old exp1 data it is reconstructed from file order).

## exp3a — mixed-effects / clustered logistic regression  ← the headline upgrade
`exp3a_mixed_effects/fit_mixed_effects.py`

Logistic regression on demography rows with **item-cluster-robust SEs** (honours
the `(1|item)` intent without a GLMM) + likelihood-ratio tests.

Result on exp1 data (qwen7b, 300 items × 4 langs):
- **socio_attr is significant** (LRT χ²=51.6, df=4, **p=1.7e-10**):
  Wealth OR=3.6 [1.9, 7.0], Power OR=2.2 [1.3, 3.6]; intellect/civility
  indistinguishable from morality.
- **Language is NOT** (LRT χ²=0.5, df=3, p=0.93); **no interaction** (p=0.54).
- → the v2 point estimates are now statistical inference. Figure: `figC`.

## exp3b — cross-lingual metrics (CFR / SBR / SCR) + parse-failure
`exp3b_xlingual_metrics/compute_xlingual_metrics.py`

New behavioural metrics (proposal_new §7). Result on exp1 data:
- **SBR tracks the bias**: Wealth 0.52, Power 0.41 vs morality 0.25,
  intellect 0.21 — strongly-biased attributes are *stably* biased in every
  language. CFR is correspondingly lower for them.
- Aggregate stability hides item-level churn: overall **CFR≈0.56** (≈half of
  items flip across languages). Figure: `figD`.
- Parse-failure < 0.25% per language (QA backstop).

## exp3d — translation-quality audit (back-translation)
`exp3d_translation_qa/backtranslation_qa.py`  (**needs network**)

Back-translates each non-English prompt to English and measures drift
(token-F1; chrF if sacrebleu present). Pre-empts "are language effects just bad
translation?". Cached + resumable. Self-test: `--self-test` (offline).

## Running on the weekend data (3 models × 7 langs)

```bash
# from each exp dir; shell-glob expands to all per-model files
python fit_mixed_effects.py       --pred ../../../shared/code/results/predictions_*.jsonl
python compute_xlingual_metrics.py --pred ../../../shared/code/results/predictions_*.jsonl
python backtranslation_qa.py --limit 60     # after translate.py adds ru/bn/el
```

All three loop over every model found, so the cross-model comparison
(qwen7b / qwen32b / internvl8b) and the 7-language CFR/SBR drop out automatically.
