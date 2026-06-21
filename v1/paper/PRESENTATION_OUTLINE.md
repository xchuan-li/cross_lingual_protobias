# Progress Report — Slide-by-Slide Script
Multilingual Prototypicality Bias in MLLM Judges (Extending ProtoBias)
Target: 20–25 min talk · 16 content slides + backup · maps to the 10-pt rubric

Figure paths (relative to project root):
- F1  code/experiments/exp1_900x4lang/figures/fig1_bias_by_language.png
- F2  code/experiments/exp1_900x4lang/figures/fig2_bias_by_domain_language.png
- FA  code/experiments/exp2_attribute_bias/figures/figA_bias_by_attribute.png   (HEADLINE)
- FB  code/experiments/exp2_attribute_bias/figures/figB_attribute_by_language.png
- PaperFig1  papers/2601.04946v2.pdf  page 2, Figure 1 (SC vs PA examples)
Data: exp1_900x4lang/results/summary.csv · exp2_attribute_bias/exp1_attribute_breakdown.csv

=====================================================================
SLIDE 1 — Title  (~15 s)
On slide:
  Title: Multilingual Prototypicality Bias in MLLM Judges
  Subtitle: Extending ProtoBias (Roy, Bhatia & Eger, 2026) across English / Chinese / Arabic / Hindi
  Your names · Mentors · Date · "Progress Report"
Visual: optional small teaser = FA (the attribute bar chart) bottom-right.
Say: one sentence — "We tested whether a vision-language judge's prototypicality
  bias depends on the language you ask it in."

=====================================================================
SLIDE 2 — The problem: prototypicality bias  (~1.5 min)  [rubric: content]
On slide (title): What is prototypicality bias?
Bullets:
  - Automatic metrics (CLIPScore, VQAScore, GPT-judges) increasingly replace humans
    for evaluating text-to-image models.
  - Failure mode: they reward images that LOOK typical / stereotypical — even when
    the image is semantically WRONG for the prompt.
  - ProtoBias pairs a Semantically-Correct-but-non-prototypical image (SC) with a
    Prototypical-but-wrong Adversarial image (PA).
Visual: PaperFig1 (the 3-row SC vs PA examples — animal / demography / object).
  Caption: "Metrics often prefer the prototypical-but-wrong image (PA)."
Say: walk through ONE row (the dog/bamboo animal example) — "correct image has two
  bamboo stalks but no animal-typical scene; the model still prefers the prototypical
  dog image that violates the prompt."

=====================================================================
SLIDE 3 — Our task: the multilingual axis  (~1.5 min)  [rubric: content]
On slide (title): Our assignment — does language change the bias?
Bullets:
  - The original ProtoBias paper is ENGLISH-ONLY and studies evaluation metrics.
  - Our project (assigned by the authors): add the MULTILINGUAL axis.
  - Research question: "Does prototypicality bias persist — or worsen — when the
    judge is prompted in other languages, including low-resource ones?"
  - Setup: use Qwen2.5-VL-7B as an MLLM-judge in a 2-Alternative-Forced-Choice task,
    across English, Chinese, Arabic, Hindi.
Visual: a simple 1-line pipeline graphic: [image pair] + [prompt in lang L] -> judge -> picks 1/2
Say: frame it as "a focused extension, not a re-run of the paper."

=====================================================================
SLIDE 4 — Related work (1/2): judges & measurement are fragile  (~1.5 min) [rubric: related work 0.5]
On slide (title): Related work — bias in judges & in measurement
Bullets:
  - Chen et al., 2024 (EMNLP) "Humans or LLMs as the Judge?": LLM-as-judge carries
    its own biases (gender, authority, beauty). -> We use an MLLM as judge, so its
    biases are exactly what we must watch.
  - Akyurek et al., 2022 (GeBNLP) "Challenges in Measuring Bias via Open-Ended
    Generation": bias estimates flip with the choice of prompts / metrics / sampling.
    -> Motivates our finding that HOW you aggregate decides the conclusion.
Visual: two paper-title cards / thumbnails side by side.
Say: "These two tell us: (a) judges are biased, (b) measuring bias is fragile — both
  central to how we read our own numbers."

=====================================================================
SLIDE 5 — Related work (2/2): multilingual & prompt sensitivity  (~1.5 min) [rubric: related work 0.5]
On slide (title): Related work — multilingual bias & prompt variation
Bullets:
  - Jin et al., 2025 (ACL Findings) "Social Bias Benchmark for Generation (BBG)":
    social-bias eval in English + Korean; generation vs QA give inconsistent results.
    -> Precedent for cross-lingual social-bias evaluation.
  - Hida, Kaneko & Okazaki, 2025 (EMNLP Findings) "...Requires Prompt Variations":
    LLM bias rankings fluctuate across prompt variants. -> Our cross-lingual prompts
    are a form of prompt variation; flags translation quality as a confound.
Bottom line (one line): "We sit at the intersection of judge-bias and multilingual
  bias evaluation — first cross-lingual test of visual prototypicality bias."
Visual: two paper-title cards.

=====================================================================
SLIDE 6 — Method: the 2AFC probe  (~2 min)  [rubric: content + illustrations]
On slide (title): Method — 2-alternative forced choice
Bullets:
  - Show two images: SC (correct, non-prototypical) vs PA (prototypical, wrong).
  - Ask, in the target language: "Which image matches this description?"
  - Left/right position randomized (controls position bias).
  - Metric = ERROR RATE = fraction of times the judge picks PA.
      0.50 = chance / no bias    >0.50 = prototypicality bias
Visual: PaperFig1 again OR a clean self-drawn schematic (pair -> question -> pick).
Say: define error rate slowly; everyone must leave this slide knowing 0.5 = no bias.

=====================================================================
SLIDE 7 — Data & experimental setup  (~1.5 min)  [rubric: content]
On slide (title): Data & setup
Bullets:
  - Dataset: ProtoBias test set; domains = Animals / Objects / Demography.
  - Demography rows carry a socio_attr label: Wealth, Power, Civility, Morality,
    Intellect (the social-hierarchy axis the paper designed in).
  - Sample: 300 rows/domain x 3 = 900 items; x 4 languages = 3,600 judgments.
  - Model: Qwen2.5-VL-7B-Instruct. Translation: Google (deep-translator).
  - Compute: NHR@FAU Alex, 1x A40 GPU (SLURM job 3687960).
Visual: small table: domains x #rows; flag "socio_attr only on Demography".
Say: emphasize the socio_attr label exists — you'll use it on slide 9-10.

=====================================================================
SLIDE 8 — First look: bias by domain x language  (~2 min)  [rubric: progress results + illustrations]
On slide (title): First pass — aggregate by domain x language
Table (error rate):
        en     zh     ar     hi
  animal     .523   .575   .570   .573
  demography .560   .577   .573   .553
  object     .467   .470   .463   .553
Bullets:
  - Rates hug 0.5; cross-language gaps ~0.05 with overlapping CIs.
  - Honest read at this granularity: bias is WEAK, no clear language effect.
Visual: F2 (bias by domain x language). Optionally F1 inset.
Say: deliberately set up suspense — "if we stopped here, the story is "nothing".
  We didn't stop here." (Do NOT linger; this is the setup, not the result.)

=====================================================================
SLIDE 9 — The catch: aggregation hid the signal  (~1.5 min)  [rubric: progress results — methods insight]
On slide (title): Why the aggregate was misleading
Bullets:
  - Each Demography row is tagged with WHICH stereotype it probes (socio_attr).
  - The default analysis averaged over socio_attr -> Demography collapsed to one
    number (~.56).
  - Hypothesis: averaging masks structure. -> Re-analyze, split by socio_attr.
Visual: a simple "before/after" arrow: [Demography = .56] --split socio_attr--> [5 bars].
Say: "This is the key move of the whole report — we suspected the average was lying."

=====================================================================
SLIDE 10 — HEADLINE: bias is attribute-specific  (~2.5 min)  [rubric: progress results — the 4-pt core]
On slide (title): The bias is attribute-specific
Table (pooled over languages):
  socio_attr   error   n     95% CI
  Wealth       .774   124   [.69, .84]
  Power        .672   256   [.61, .73]
  Civility     .539   256   [.48, .60]
  Morality     .487   372   [.44, .54]
  Intellect    .479   192   [.41, .55]
Bullets:
  - The flat .56 average hid a 0.30 spread.
  - Strong "judge-by-looks" bias for SOCIAL-STATUS attributes (wealth, power);
    almost none for moral/cognitive ones (morality, intellect).
  - Intuition: web data encodes what "rich/powerful" people look like; there is no
    stable visual prototype for "moral" or "intelligent".
Visual: FA (figA_bias_by_attribute.png) — the headline chart.
Say: this is your money slide. Land the wealth/power vs morality/intellect contrast.

=====================================================================
SLIDE 11 — Cross-lingual consistency  (~2 min)  [rubric: progress results]
On slide (title): The pattern is the same in every language
Bullets:
  - Wealth & Power elevated, Morality & Intellect ~chance — in English, Chinese,
    Arabic AND Hindi alike.
  - Per-language differences are small and within noise at current cell sizes.
  - Interpretation: the bias is baked into the VISUAL representation, not produced
    by any single language's prompt.
Visual: FB (figB_attribute_by_language.png).
Say: tie back to RQ — "language barely moves it; the attribute is what matters."

=====================================================================
SLIDE 12 — Takeaway  (~1.5 min)  [rubric: content]
On slide (title): What we learned
Bullets:
  - (1) Prototypicality bias is ATTRIBUTE-SPECIFIC (social-status attributes).
  - (2) It is LARGELY LANGUAGE-INVARIANT across en/zh/ar/hi.
  - A "language doesn't move it" result is a valid multilingual finding — and it
    STRENGTHENS the original paper's claim that the failure is structural.
Visual: one big sentence, minimal text. Optional tiny FA + FB thumbnails.
Say: explicitly address the worry — "no language effect is not a null project; it's
  evidence the bias is universal."

=====================================================================
SLIDE 13 — Limitations  (~1 min)  [rubric: content / honesty, helps QA]
On slide (title): Caveats
Bullets:
  - Effect sizes small vs CIs; underpowered for cross-language contrasts
    (Wealth has only ~31 items per language).
  - Single model, single seed, single translation backend.
  - Translation quality for ar/hi not yet validated -> confound for any language claim.
  - Position bias & per-language parse-failure rates not yet audited.
Visual: none / icon list.
Say: pre-empt the obvious QA attacks by naming them first.

=====================================================================
SLIDE 14 — Outlook: Exp2 plan  (~2 min)  [rubric: outlook 1 pt]
On slide (title): Next steps (Exp2)
Bullets:
  - (1) NO GPU: mixed-effects logistic regression
        picked_adv ~ socio_attr * lang + gender + (1|item)
        -> confirm "attribute effect >> language effect" is statistically real.
  - (2) Enlarge / balance Demography sampling (>=150 per cell) to tighten Wealth/Power.
  - (3) Optional: extend language set across the resource spectrum (add low-resource
        langs) to directly test the "low-resource = worse" hypothesis.
  - (4) Translation-QA: back-translation drift + parse-failure rates.
Punchline: "Either outcome wins — flat confirms language-invariance; a low-resource
  spike recovers the authors' original hypothesis."
Visual: 4-step roadmap strip.

=====================================================================
SLIDE 15 — Summary  (~1 min)  [rubric: content]
On slide (title): Summary
Bullets:
  - Built & ran the first MULTILINGUAL ProtoBias pipeline (3,600 judgments, 4 langs).
  - Found the bias is attribute-specific (Wealth/Power) and consistent across
    languages — by catching that the standard aggregation hid the signal.
  - Delivered a concrete, powered Exp2 plan.
Visual: 3 icons. End-of-talk slide.

=====================================================================
SLIDE 16 — Thank you / Questions
On slide: "Thank you — Questions?" + contact + repo path.

=====================================================================
BACKUP SLIDES (after 16; do NOT present, pull up during QA)  [rubric: QA 1 pt]
  B1  Full summary.csv table (12 cells, error + CI).
  B2  Full socio_attr x language table (exp1_attribute_breakdown.csv).
  B3  Gender split: male .573 (n=648) vs female .558 (n=552) — not yet tested.
  B4  Example translated prompts (en/zh/ar/hi) for one item — translation sanity.
  B5  Infra details: Qwen2.5-VL-7B, A40, ~minutes runtime, resumable pipeline,
      offline compute node + login-node translation gotcha.
  B6  Why F1 object x Hindi (.553) is NOT over-claimed (small n).

=====================================================================
DELIVERY NOTES
- The 4-pt "Progress Results" item lives on slides 9->11. Spend your energy there.
- Do NOT dwell on slide 8 ("no effect") — it is the setup, not the result.
- Cover >=2 related papers explicitly (slides 4-5) — required for the 0.5 pt.
- Keep slides visual; one idea per slide; numbers in tables, not prose.
