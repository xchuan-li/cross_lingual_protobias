

# Cross-lingual ProtoBias as a Grounding Stress Test

## 1. Project Motivation

This project starts from the ProtoBias setup: multimodal models are asked to choose which image better matches a text prompt when one image is semantically correct but non-prototypical, and the other image is visually or socially prototypical but semantically incorrect.

The original ProtoBias question is mainly about whether multimodal evaluation metrics and vision-language models prefer prototypical images over semantically correct ones. Our extension reframes this as a cross-lingual grounding problem:

> When a multimodal model makes a stable image-text matching decision across languages, is that decision actually grounded in language-independent semantic structure, or is it supported by language-specific prototype shortcuts?

This framing connects the bias project to a broader research direction on model grounding, shortcut behavior, and behavioral stability. The central idea is that cross-lingual consistency alone is not enough to prove semantic understanding. A model may appear stable across English, Chinese, Arabic, or Hindi while relying on different latent shortcuts in each language.

## 2. Core Research Framing

The project should not be framed only as:

> Does Qwen2.5-VL have bias in different languages?

A stronger framing is:

> Does language switching expose whether multimodal decisions are semantically grounded or shortcut-driven?

In this view, ProtoBias becomes an applied stress test for the distinction between surface-level behavioral stability and genuine semantic grounding.

The key thesis is:

> Cross-lingual stability is not sufficient evidence of semantic grounding.

A model can make the same correct decision in multiple languages, but that decision may still collapse when prototype cues, semantic details, or visual shortcuts are intervened on.

## 3. Research Questions

### RQ1: Cross-lingual decision stability

Does switching the prompt language change the model's preference between a semantically correct non-prototypical image and a prototypical adversarial image?

This asks whether the same image pair receives different model choices under English, Chinese, Arabic, Hindi, or other languages.

### RQ2: Domain sensitivity

Are language-induced decision changes more frequent in socially sensitive domains than in neutral domains?

The hypothesis is that demography samples may show larger cross-lingual instability than animal or object samples, because demographic prototypes are more culturally and linguistically loaded.

### RQ3: Stable but ungrounded behavior

When the model gives the same correct answer across languages, does that decision survive shortcut-severing interventions?

This asks whether cross-lingually stable correctness is truly supported by semantic details, or whether it disappears once prototype cues or auxiliary visual shortcuts are removed.

## 4. Dataset Setup

We use the ProtoBias dataset structure. Each sample contains:

| Component | Meaning |
|---|---|
| `text` | Neutral masked prompt using a hypernym such as animal, object, vehicle, or person |
| `correct_image` | Semantically correct image, often non-prototypical |
| `adversarial_image` | Prototypical image with a subtle semantic violation |
| `domain` | Animal, object, or demography |

The model receives two images and one text prompt, then chooses which image better matches the prompt.

The correct answer is always the semantically correct image. Choosing the adversarial image is counted as a typicality error.

## 5. Language Extension

The original English prompt is translated into several languages:

| Language | Role in experiment |
|---|---|
| English | Original prompt and baseline |
| Chinese | High-resource language for Qwen; strong comparison point |
| Arabic | Culturally and script-wise distinct language; important for religion-related cases |
| Hindi or Swahili | Lower-resource extension, useful for stronger cross-lingual contrast |

The first report can focus on English, Chinese, and Arabic. Hindi or Swahili can be framed as future work or a later extension.

Translation quality should be audited. At minimum, Chinese translations can be manually checked. For other languages, back-translation or external translation tools can be used as a sanity check.

## 6. Experimental Design

### 6.1 Basic 2AFC evaluation

For each sample and each language:

1. Randomize image order as A/B.
2. Show the model both images and the translated text prompt.
3. Ask the model which image better matches the prompt.
4. Map the answer back to correct or adversarial.
5. Compute error rates by language and domain.

### 6.2 Language-switch intervention

For each image pair, compare the model's choices across languages.

Example:

| Sample | English | Chinese | Arabic | Interpretation |
|---|---|---|---|---|
| 001 | Correct | Correct | Correct | Stable decision |
| 002 | Correct | Correct | Adversarial | Language-induced flip |
| 003 | Adversarial | Adversarial | Adversarial | Stable but biased decision |

This allows us to measure whether language alone changes the decision boundary.

### 6.3 Shortcut-severing audit

To connect the project to grounding, we should go beyond error rates and test whether correct decisions depend on semantic details.

Possible interventions:

1. Remove key semantic attributes from the prompt, such as count, color, or spatial relation.
2. Replace the adversarial image with a non-prototypical but still incorrect image.
3. Replace the correct image with a typical and correct image if such controls can be generated.
4. Compare decisions before and after removing prototype cues.

The goal is to test whether the model's decision survives after shortcut cues are weakened or removed.

## 7. Proposed Metrics

### 7.1 Typicality Error Rate

The basic ProtoBias metric:

```text
TER(l, d) = P(model chooses adversarial image | language = l, domain = d)
```

A higher value means the model more often prefers the prototypical but semantically incorrect image.

### 7.2 Cross-lingual Flip Rate

A new metric for language-induced instability:

```text
CFR(d) = P(model choice changes across languages | domain = d)
```

This captures whether the same image pair produces different decisions under different prompt languages.

### 7.3 Stable Bias Rate

A metric for cases where the model consistently chooses the adversarial image across languages:

```text
SBR(d) = P(model chooses adversarial image in all languages | domain = d)
```

This identifies language-stable but biased behavior.

### 7.4 Stable-but-Ungrounded Rate

A grounding-oriented metric:

```text
SUR = P(model is correct across languages but fails after shortcut-severing intervention)
```

This metric directly tests the idea that stable correctness is not necessarily grounded correctness.

## 8. Expected Contributions

This project can be extended into a paper by making three contributions:

1. Cross-lingual extension of ProtoBias: We test whether prototype-driven multimodal failures remain stable under language intervention.
2. Behavioral diagnostics for language-conditioned shortcuts: We introduce decision flip rate and stable bias rate to distinguish ordinary errors from language-sensitive prototype effects.
3. Grounding-oriented audit: We show that cross-lingual consistency is not sufficient evidence of semantic grounding, because stable decisions may fail under shortcut-severing interventions.

## 9. Why This Fits My Research Direction

This project fits a broader research direction on model grounding, shortcut reliance, and stability analysis.

The bias setup is not only a fairness evaluation. It is a controlled environment where semantic correctness and prototype familiarity are deliberately put into conflict. This makes it useful for studying whether a model's behavior is caused by the intended semantic structure or by an unintended shortcut.

The cross-lingual extension makes the project especially relevant. If the same visual evidence and the same semantic content lead to different decisions under different languages, this suggests that the model's internal decision process is language-conditioned. If the model gives stable answers across languages, we still need to test whether that stability is grounded or merely shortcut-supported.

Therefore, the project can be positioned as:

> A cross-lingual multimodal stress test for distinguishing grounded semantic behavior from prototype-driven shortcut behavior.

## 10. Minimal Viable Plan

### Stage 1: Course project version

- Run Qwen2.5-VL on English, Chinese, and Arabic prompts.
- Use the full 1500 samples if possible, or a balanced subset across animal, object, and demography.
- Report typicality error rate by language.
- Report typicality error rate by language and domain.
- Report cross-lingual flip rate.

### Stage 2: Workshop-paper version

- Add Hindi or Swahili as a lower-resource language.
- Add confidence intervals and statistical tests.
- Add translation quality audit.
- Analyze error types by domain, subcategory, and semantic knob.
- Compare at least two multimodal models if time allows.

### Stage 3: Strong paper version

- Add shortcut-severing interventions.
- Build a small 2x2 factorial control set separating semantic correctness from prototypicality.
- Analyze stable-but-ungrounded behavior.
- Frame the paper around cross-lingual stability versus semantic grounding.

## 11. Possible Paper Titles

- Cross-lingual ProtoBias: When Multimodal Stability Is Not Semantic Grounding
- Prototype Drift: Cross-lingual Instability of Social Prototypes in Vision-Language Models
- Stable but Ungrounded: Diagnosing Cross-lingual Prototype Shortcuts in Multimodal Models
- Language-conditioned Prototype Bias in Multimodal Image-Text Evaluation

## 12. Main Risk and How to Handle It

The main risk is that the definition of “prototype” is itself culturally loaded, especially in the demography domain. This should not be hidden. Instead, it should become part of the research argument.

Rather than assuming that ProtoBias prototypes are universal, we can treat them as hypotheses to be tested under language intervention. If different languages produce different model behavior, this supports the idea that prototypes are not fixed objective properties, but language- and culture-conditioned structures.

This turns a weakness of the original setup into a research opportunity.