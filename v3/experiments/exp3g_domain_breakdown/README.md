# exp3g — animal & object breakdown (PR-II advisor ask)

Advisor feedback on PR II: *"check on other categories (animal & object)."*
The deck only ever showed animal/object as a single pooled error rate; this does
for them what exp2 did for demography — break each down by its own
`subcategory` and by the visual `knob`, both model families, Wilson CIs.

Run: `python analyze_domain_breakdown.py` (CPU, reads the existing
`shared/code/results/predictions_{qwen7b,internvl8b}.jsonl`).

## Findings

**1. Animal & object bias is subcategory-specific too — not flat.**
The pooled ~.5 hid real structure, and the ordering replicates across both
models (fig `figH_subcategory_breakdown.png`):

| domain | biased subcats | near / below chance |
|---|---|---|
| animal | `animal` (generic) .63–.75, `bird` .60–.64 | `mammal` .39–.48 |
| object | `vehicle` .62–.64 | `tableware` .51–.54, `furniture` .34–.48 |

So the v2/exp2 story generalises: bias is concentrated in specific categories in
every domain, not just demography's wealth/power — the same "structural, not
uniform" message.

**2. Knob pattern matches exp3e, within animal/object.**
`count` and `scale_size` drive the most bias; `color_tone` the least — the
"artifact worry" (colour) is again the *weakest* cue, reinforcing exp3e's
conclusion that this is prototypicality, not a low-level colour cue.

**3. The v2 object×Hindi anomaly localises — it is not a broad object effect.**
v2 flagged object×hi = .553 vs .46–.47 elsewhere. Broken down, the Hindi lift
sits almost entirely in **tableware** (both models, gap +.08 to +.11) and in the
**color_tone / layout_relation** cues (internvl gap +.15 to +.18); `vehicle`
shows ~zero Hindi gap. A narrow cell, not evidence that Hindi broadly raises
object bias.

## Outputs
- `figures/figH_subcategory_breakdown.png` — subcategory bars, both domains/models
- `results/error_by_subcategory.csv`
- `results/error_by_knob_within_domain.csv`
- `results/object_hindi_anomaly.csv`
