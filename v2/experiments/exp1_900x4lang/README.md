# Exp1 — 4-language × 900-row prototypicality-bias eval

**Date:** 2026-06-01 · **Cluster:** NHR@FAU Alex (A40) · **SLURM job:** 3687960

## Setup
- **Model:** Qwen/Qwen2.5-VL-7B-Instruct, MAX_NEW_TOKENS=8, image long side 512px
- **Dataset:** subha-roy/dl4dh_data (test split), domains = animal / object / demography
- **Sampling:** N_PER_DOMAIN=300, seed=42 → 900 rows total
- **Languages:** en, zh, ar, **hi** (Hindi added this round)
- **Task:** 2AFC — show (correct, adversarial) image pair in randomized L/R order, ask in
  the target language which image matches the neutral description. Metric =
  `error_rate` = mean(picked_adversarial) = how often the model prefers the
  prototypical/adversarial image. 0.5 = chance, >0.5 = prototypicality bias.
- **Predictions:** 3600 (900×4); n≈300/cell (animal·zh=299, object·ar=298, a couple
  translation-parse drops).
- **Translation:** deep-translator (Google), run on login node (compute node offline).

## Results (error_rate, n≈300, Wilson 95% CI half-width ≈ ±0.056)

| domain | en | zh | ar | hi |
|---|---|---|---|---|
| animal | .523 | .575 | .570 | .573 |
| demography | .560 | .577 | .573 | .553 |
| object | .467 | .470 | .463 | **.553** |

## Read
1. **Weak overall bias.** Rates hug 0.5. animal/demography slightly above (~.55–.58,
   mild bias); object essentially chance (en/zh/ar CIs cover 0.5 → no bias).
2. **No significant cross-lingual main effect.** Within each domain the per-language
   CIs overlap heavily.
3. **Key nugget — object × hindi = .553** is the lone outlier: en/zh/ar all sit at
   .46–.47 in `object`, only the low-resource language (hi) is elevated. Local support
   for the "low-resource languages show stronger prototypicality bias" hypothesis.
   hi is unremarkable in the other two domains.

## Caveats / known limitations (→ drive exp2 design)
- Effect sizes tiny vs. CI width; underpowered for cross-lingual contrasts.
- Single model (7B), single seed, single translation backend (no back-translation QA).
- Translation quality for ar/hi not formally validated.
- `picked_adversarial` collapses the L/R-randomization; no check on position bias or
  on raw_choice parse-failure rate per language.
