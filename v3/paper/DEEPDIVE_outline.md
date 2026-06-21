# Final-report deep-dive — one-page outline

Project stays an independent applied result (no forced link to the causal-
interpretability mainline). The "depth" is squeezing the existing 2-model ×
7-language data — **no new experiments** — into one mechanistic picture.

## The thesis (one sentence)
Prototypicality bias is a **fallback** whose *existence* is set by the attribute
and whose *strength* is set by how weak the discriminating signal is.

## The two-factor model
1. **Is there a prototype to take?  → the attribute.**
   A visual prototype exists for wealth / social status, not for morality /
   intellect (wealth OR ≈ 3, p ≈ 2×10⁻¹⁴; morality/intellect ≈ chance). This map
   *replicates across both model families*.
2. **How weak is the discriminating signal?  → perception & language.**
   The model falls back on the prototype when the cue is hard to perceive
   **(count, scale)** OR the prompt language is unfamiliar **(Bengali, Greek)**.
   Two routes, one mechanism.

## The four pieces of evidence (all from existing data)
| # | analysis | finding | what it buys |
|---|---|---|---|
| 1 | mixed-effects (exp3a) | attribute effect p≈2e-14; language effect p<0.025 (bn/el/ar) | the two axes, with statistics |
| 2 | translation QA (exp3d) | elevated langs have the *highest* fidelity | language effect is **not** MT noise |
| 3 | **knob (exp3e)** | colour LOWEST, count/scale HIGHEST; wealth>morality within every knob | rules out the colour artifact; gives the **perception route** |
| 4 | **agreement (exp3f)** | per-item error r = 0.68 across families | the trap is **item-intrinsic / objective** |

The knob result (3) and the language result (1–2) are the *same mechanism* via
two routes — that is the unifying move.

## Honest boundaries (say them)
- Single seed; demography cells small (wealth ≈ 31/lang).
- The language effect is not a clean resource gradient (Russian non-Latin yet
  flat) — "why ar/bn/el" is unresolved; "perceptual difficulty" and "model
  familiarity" are interpretations, not proven mechanisms.
- r = 0.68 ≠ 1.0: ~half the item variance is still model-specific.

## Suggested slide order (already in ProgressReport_2.pptx)
attribute (8) → replicates across models (9) → language not flat (10) →
not translation noise (11) → CFR/SBR (12) → **knob confound (13)** →
**item agreement (14)** → **two-factor synthesis (15)**.

## Possible final-report framing line
"We did not add experiments; we asked the existing 12,500 judgments four sharper
questions, and they converge on a single two-factor account of when a vision-
language judge takes the prototype shortcut."
