# Exp2 Proposal — Attribute-Specific Prototypicality Bias Across Languages

**Project:** Multilingual extension of *ProtoBias* (Roy, Bhatia, Eger 2026, arXiv:2601.04946) — small project assigned by the authors.
**Status:** PROPOSAL (re-analysis of exp1 done; new data collection not yet run)
**Author:** Xiaochuan Li · **Date:** 2026-06-01

---

## 1. Where this sits relative to the paper

The ProtoBias paper studies **prototypicality bias** — automatic T2I evaluators (CLIPScore, PickScore, VQAScore, GPT-4o/GPT-5 judges) preferring an image that *looks* prototypical/socially typical over the semantically correct one. The paper is **English-only**. Its **Demography** domain is purpose-built around social hierarchy: privileged groups (white, American, Christian, heterosexual, **wealthy, intelligent**) are the prototypical "default", crossed with five socio-attributes — **Wealth, Power, Civility, Morality, Intellect**.

Our assignment is the **multilingual axis**: *does prototypicality bias change with the language of the prompt?* We use Qwen2.5-VL-7B as an MLLM-judge in a 2AFC setup (which of two images matches the description) across **en / zh / ar / hi**.

## 2. What exp1 did, and what it missed

exp1 (`../exp1_900x4lang/`): 900 rows × 4 languages = 3600 2AFC judgments. The original `analyze.py` aggregated **only by (domain, language)**. Result: demography collapsed to a single number ≈ **.56**, and the cross-language differences were all tiny (≈0.05) and within noise. Headline-level conclusion from exp1 alone: *"weak bias, no clear language effect."* — true but uninteresting.

## 3. The discovery: re-analyzing along the unused axis

The dataset rows carry `socio_attr`, `gender`, and `knob` fields that `analyze.py` **never used**. `socio_attr` (wealth/power/civility/morality/intellect) is exactly the social-hierarchy label the paper designed into Demography. Breaking demography down by `socio_attr` (script: `reanalyze_exp1.py`, all 4 languages pooled, n≈300 demography rows/lang):

| socio_attr | error rate | n | 95% CI | reading |
|---|---|---|---|---|
| **wealth** | **.774** | 124 | [.69, .84] | strong bias |
| **power** | **.672** | 256 | [.61, .73] | strong bias |
| civility | .539 | 256 | [.48, .60] | mild |
| morality | .487 | 372 | [.44, .54] | ~chance |
| intellect | .479 | 192 | [.41, .55] | ~chance |

**The aggregate (.56) hid a 0.30 spread.** The model has a strong "judge by appearance" bias for *social-status* attributes (wealth, power) and essentially none for *moral/cognitive* attributes (morality, intellect). This is intuitive — web-scale image data encodes what "rich/powerful people look like", but there is no stable visual prototype for "moral" or "intelligent" — and it is precisely the stereotype-driven failure the paper's Demography design targets.

**Crucially, the pattern is consistent across all four languages** (see `exp1_attribute_breakdown.csv`, `figures/figB_attribute_by_language.png`): wealth & power are elevated and morality & intellect near chance in en, zh, ar, and hi alike. The per-cell language differences are small and, at n≈30–90/cell, not distinguishable from noise.

### Reframed conclusion (the real story)
> Prototypicality bias in an MLLM-judge is **attribute-specific** (concentrated on social-status attributes) and **largely language-invariant**. It is a structural property of the visual representation, not an artifact of one language's data. This *strengthens* the paper's thesis that the failure is structural.

A null/robustness result on language is still a valid multilingual finding — but to claim it credibly we must (a) power it properly and (b) ideally widen the language resource spectrum.

## 4. Exp2 — research questions

- **RQ1 (primary, confirmatory):** Is the attribute effect (wealth/power ≫ morality/intellect) statistically robust, and is it significantly larger than the language effect?
- **RQ2 (secondary):** Is the attribute-bias pattern stable across languages, or does any attribute's bias change with language (attribute × language interaction)?
- **RQ3 (exploratory, the original hypothesis):** Does the bias intensify for **low-resource** languages once we span a proper resource spectrum?
- **RQ4 (gender):** Does prototypicality bias differ by the `gender` of the depicted person (male .573 vs female .558 in exp1 — needs test)?

## 5. Methods

**Statistics.** Replace per-cell point estimates with a **mixed-effects logistic regression**:
`picked_adversarial ~ socio_attr * lang + gender + (1 | item)`
with item (row id) as a random effect. Report fixed-effect contrasts and a likelihood-ratio test of the `lang` and `socio_attr * lang` terms. This gives real power and respects the repeated-item structure (same image pair seen in 4 languages).

**Sampling / power.** exp1's wealth cell has only n≈124 pooled (≈31/lang). For exp2:
- **Balance and enlarge the demography sample** so each `socio_attr × lang` cell has ≥150 (target ≥600/attribute pooled). Either set `N_PER_DOMAIN` higher with stratified sampling on `socio_attr`, or sample demography separately from animal/object.
- Keep animal/object at current size as control domains.

**Language spectrum (for RQ3).** Add genuinely low-resource languages spanning the resource axis, e.g. high: en, zh, es/fr; mid: ar, hi; low: sw (Swahili), bn (Bengali), yo (Yoruba). Treat resource-level as an ordinal predictor. *Either outcome is publishable:* flat → "language-invariant" is nailed down; low-resource spike → recovers the authors' "low-resource is worse" hypothesis.

**Translation-confound control (validity).** Cross-lingual claims are confounded by translation quality (esp. low-resource). For each non-English prompt: back-translate to English, score semantic drift (e.g., embedding cosine / chrF), and **report per-language parse-failure rate** (`raw_choice` not in {1,2}). Flag/exclude high-drift items. This separates "language effect" from "bad-translation noise".

**Position-bias check.** `adv_position` is randomized; verify the model has no fixed left/right preference per language (a side bias would inflate/deflate error rate spuriously).

## 6. Deliverables

1. `reanalyze_exp1.py` — DONE (attribute breakdown + figA/figB on exp1 data).
2. Mixed-effects model script + results table (RQ1/RQ2) — on exp1 data first, then exp2 data.
3. Enlarged/balanced demography run + (optional) extended-language run.
4. Translation-QA report (back-translation drift + parse-failure rates).
5. Updated figures: bias-by-attribute, attribute×language, (if run) bias-by-resource-level.

## 7. Suggested order of work

1. **Now (no GPU):** run mixed-effects model on exp1 data → confirm "attribute ≫ language" is significant. If yes, the core story is locked regardless of further runs.
2. **Cheap GPU run:** enlarged/balanced demography (n≥150/cell) to tighten the wealth/power CIs.
3. **Bigger GPU run (optional):** extended language spectrum for RQ3.
4. Translation-QA in parallel (CPU/network, login node).

## 8. Files in this folder

- `PROPOSAL.md` — this document
- `reanalyze_exp1.py` — re-analysis of exp1 along socio_attr/gender (reproducible)
- `exp1_attribute_breakdown.csv` — socio_attr × lang error rates + CIs
- `figures/figA_bias_by_attribute.png` — the headline (attribute-specific bias)
- `figures/figB_attribute_by_language.png` — pattern consistency across languages
