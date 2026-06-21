# Exp1 Brief — Multilingual Prototypicality Bias (for the team)

**TL;DR:** We ran the first multilingual pass of ProtoBias (Qwen2.5-VL-7B as an MLLM-judge, 4 languages, 900 items). The headline isn't language — it's that the bias is **attribute-specific**: the model judges by appearance strongly for **wealth and power**, barely at all for morality/intellect, and this pattern is **the same across all four languages**.

---

## 1. What we did
- **Task (2AFC):** show two images — one semantically correct but non-prototypical, one prototypical but subtly wrong — and ask the model (in the target language) which matches the description. Picking the prototypical/wrong one = prototypicality bias. Metric = **error rate** = fraction of times it picks the wrong-but-prototypical image. 0.5 = chance / no bias.
- **Model:** Qwen2.5-VL-7B-Instruct (used as the judge).
- **Data:** ProtoBias test set — domains *animal / object / demography*; 300 rows/domain = **900 items**, seed 42.
- **Languages:** English, Chinese, Arabic, **Hindi** → 900 × 4 = **3,600 judgments**.
- **Infra:** NHR@FAU Alex (1× A40), SLURM job 3687960. Translations via Google (deep-translator). Eval ≈ a few minutes.

## 2. First-pass result (by domain × language)
| domain | en | zh | ar | hi |
|---|---|---|---|---|
| animal | .523 | .575 | .570 | .573 |
| demography | .560 | .577 | .573 | .553 |
| object | .467 | .470 | .463 | **.553** |

Read at this level: bias is **weak** (rates hug 0.5), and **no clear language effect** — per-cell differences are ~0.05 with overlapping CIs. The only eye-catcher was object×Hindi (.553 vs .46–.47 for the others), but n is too small to trust.

## 3. The real finding (re-analysis)
The dataset tags each demography item with a `socio_attr` (the stereotype axis being probed) — a field the original analysis **averaged away**. Splitting demography by `socio_attr` (all languages pooled):

| socio_attr | error rate | n | 95% CI |
|---|---|---|---|
| **wealth** | **.774** | 124 | [.69, .84] |
| **power** | **.672** | 256 | [.61, .73] |
| civility | .539 | 256 | [.48, .60] |
| morality | .487 | 372 | [.44, .54] |
| intellect | .479 | 192 | [.41, .55] |

The flat .56 demography average **hid a 0.30 spread**. The model has a strong "judge-by-looks" bias for **social-status** attributes (wealth, power) and essentially none for **moral/cognitive** ones (morality, intellect) — intuitive, since web data encodes what "rich/powerful" people look like but has no stable visual prototype for "moral" or "intelligent".

**This pattern holds in all four languages** (wealth & power high, morality & intellect ≈ chance in en/zh/ar/hi alike). Per-language differences are small and within noise at current cell sizes.

## 4. Takeaway
> Prototypicality bias in the MLLM-judge is **attribute-specific** (concentrated on social-status attributes) and **largely language-invariant**. It looks like a structural property of the visual representation, not an artifact of any single language — which strengthens, rather than contradicts, the original (English-only) paper. A "language doesn't move it much" result is itself a valid multilingual finding.

## 5. Caveats
- Effect sizes are small relative to CIs; underpowered for cross-language contrasts (wealth has only ~31 items/language).
- Single model (7B), single seed, single translation backend — translation quality for ar/hi not yet validated (possible confound for any language claim).
- Position bias and per-language parse-failure rates not yet audited.

## 6. Next (see exp2 proposal)
1. **No GPU needed:** mixed-effects logistic regression on this data to confirm "attribute effect ≫ language effect" is statistically real.
2. Enlarge/balance the demography sample (≥150/cell) to tighten the wealth/power estimates.
3. Optional: extend the language set across the resource spectrum (add low-resource langs) to test the "low-resource = worse" hypothesis directly.
4. Translation-QA (back-translation drift + parse-failure rates).

*Artifacts:* `results/summary.csv`, `results/predictions.jsonl` (3,600 rows), `figures/`. Re-analysis + attribute figures: `../exp2_attribute_bias/`.
