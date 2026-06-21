# Speaker Notes — ProgressReport_1_merged.pptx (24 slides)

> Bilingual speaker notes for the merged deck. EN is the English delivery; 中文 is the same in Chinese.
> Slides 1–7 are the front half (partner); Xiaochuan presents from slide 8 — first results through the extension plan.

---

### Slide 1 — Title

**EN:** Good afternoon, and thank you for making the time. Our project is a multilingual extension of your ProtoBias work. The question we set out to answer is narrow but, I think, an important one: when a vision-language model acts as a judge — deciding whether an image fits a description — does it reward the image that merely looks typical over the one that is actually correct, and crucially, does that tendency change with the language we ask it in? We tested four languages spanning the high- and low-resource range: English, Chinese, Arabic, and Hindi. I'll be presenting the second half of the talk, from the first experimental results through the analysis and our plan for the next experiment.

**中文：** 下午好，谢谢您抽时间。我们这个项目是对您 ProtoBias 工作的一个多语言扩展。我们想回答的问题不大，但我认为相当重要：当一个视觉-语言模型充当"裁判"、判断一张图配不配一句描述时，它会不会更偏向那张"看起来典型"的图，而不是真正正确的那张；更关键的是，这种倾向会不会随着我们提问所用的语言而改变？我们选取了横跨高、低资源的四种语言：英语、汉语、阿拉伯语和印地语。我负责报告的后半部分，从第一批实验结果，一直讲到分析以及我们下一步实验的计划。

---

### Slide 2 — The problem

**EN:** This is the concept your paper introduced, so I'll keep it brief and mainly for the record, since not everyone here works on it daily. Automatic scorers — CLIPScore, VQAScore, and GPT-based judges — are increasingly used in place of human raters when we evaluate text-to-image models. The failure mode they exhibit is that they reward images which look stereotypical, even when those images are semantically wrong for the prompt. ProtoBias operationalizes this by pairing a semantically-correct but non-prototypical image against a prototypical-but-wrong adversarial one. The animal example on the slide makes it concrete: the prompt specifies two bamboo stalks, the correct image shows them with an unusual animal, the adversarial image is simply a typical dog by a pond, and many metrics still prefer the dog.

**中文：** 这个概念是您论文里提出的，所以我讲得简短一些，主要是为了对齐，因为在座的并非每个人都天天接触它。如今在评估文生图模型时，自动打分器——CLIPScore、VQAScore，以及基于 GPT 的裁判——越来越多地取代了人工评分。它们的典型失效是：哪怕一张图在语义上其实是错的，只要它看起来更符合刻板印象，就会被给高分。ProtoBias 把这一点具体化为一对图：一张语义正确但不典型，另一张典型但错误（即对抗图）。幻灯片上的动物例子很直观：提示句要求有两根竹子，正确图里配的是一种不常见的动物，对抗图则是一只典型的"池塘边的狗"，而很多指标仍然偏向那只狗。

---

### Slide 3 — Research questions

**EN:** The original study was English-only and focused on evaluation metrics. The extension you assigned us adds the language dimension, and we framed it as two questions. The first is cross-lingual consistency: does the prototypicality bias persist, or worsen, when we prompt the judge in other languages, including lower-resource ones? The second concerns sensitive contexts: is the bias stronger for socially loaded attributes — wealth, power, and so on — than for neutral domains such as animals and objects? The diagram on the right is the whole apparatus in a single line: a pair of images plus a prompt in language L goes to the Qwen judge, which returns a forced choice, and selecting the adversarial image is what we score as bias.

**中文：** 原始研究只使用英语，关注的是评测指标。您交给我们的扩展加入了语言这一维度，我们把它拆成两个问题。第一是跨语言一致性：当我们用其他语言（包括资源较少的语言）向裁判提问时，这种典型性偏见会保持不变，还是会加重？第二关乎敏感语境：在涉及社会属性（财富、权力等）时，偏见是否比动物、物体这类中性领域更强？右边那张图就是整套装置的一行概括：一对图像加上一句语言 L 的提示，送进 Qwen 裁判，它给出一个二选一的强制选择，而选中对抗图就被我们记为偏见。

---

### Slide 4 — Related work (1/2)

**EN:** Two papers frame how we read our own numbers. Chen and colleagues, at EMNLP 2024, showed that when a large model is used as a judge, it carries its own biases — around gender, authority, and appearance. Since our setup uses a multimodal model as the judge, those judge-side biases are precisely the object of study rather than a nuisance to be removed. Akyurek and colleagues, in the 2022 gender-bias workshop, demonstrated that bias estimates are fragile: change the prompts, the metric, or the sampling, and the conclusion can flip. That finding directly motivates a point we will return to — that how you aggregate the data can decide which story you end up telling.

**中文：** 有两篇论文决定了我们如何看待自己的数据。Chen 等人在 EMNLP 2024 指出，当一个大模型被用作裁判时，它会带入自身的偏见——在性别、权威和外貌等方面。由于我们的设置正是用一个多模态模型当裁判，这些裁判侧的偏见恰恰是我们的研究对象，而不是需要排除的干扰。Akyurek 等人在 2022 年的性别偏见研讨会上则表明，偏见的估计很脆弱：改变提示词、指标或采样方式，结论都可能翻转。这一发现直接呼应了我们后面会回到的一个要点——你如何聚合数据，可能就决定了你最终讲出什么样的故事。

---

### Slide 5 — Related work (2/2)

**EN:** The other two locate us within multilingual bias evaluation. Jin and colleagues, at ACL Findings 2025, built a social-bias benchmark in English and Korean and found that generation and question-answering formats can give inconsistent results — a precedent for evaluating social bias across languages. Hida, Kaneko and Okazaki, at EMNLP Findings 2025, showed that bias rankings fluctuate across prompt variations; since our different languages are themselves a form of prompt variation, this both supports our design and flags translation quality as a confound we have to take seriously. Taken together, we sit at the intersection of judge-bias and multilingual bias evaluation, and to our knowledge this is the first cross-lingual test of visual prototypicality bias.

**中文：** 另外两篇把我们定位在多语言偏见评测之中。Jin 等人在 ACL Findings 2025 用英语和韩语构建了一个社会偏见基准，发现生成式与问答式的格式会给出不一致的结果——这为跨语言评测社会偏见提供了先例。Hida、Kaneko 和 Okazaki 在 EMNLP Findings 2025 表明，偏见排名会随提示词的变体而波动；由于我们使用的不同语言本身就是一种提示词变体，这既支持了我们的设计，也提醒我们必须认真对待翻译质量这个混杂因素。综合来看，我们正处在"裁判偏见"与"多语言偏见评测"的交叉点，而且据我们所知，这是第一次在跨语言下检验视觉上的典型性偏见。

---

### Slide 6 — How we measure

**EN:** The method is a two-alternative forced choice. We show the model two images — the semantically correct one and the prototypical-but-wrong one — and we ask, in the target language, which image better matches the description. We randomize which side each image appears on, so that any tendency to always pick the left or the right cannot masquerade as bias. The metric is the error rate: the fraction of trials on which the judge selects the prototypical-but-wrong image. The reference point matters, so I'll state it plainly — 0.5 means the model is effectively guessing and there is no bias, while anything reliably above 0.5 indicates prototypicality bias.

**中文：** 方法是一个二选一强制选择。我们给模型看两张图——语义正确的那张和典型但错误的那张——然后用目标语言问它：哪张更符合这句描述。我们会随机安排两张图出现在左边还是右边，这样"总是选左或选右"的倾向就不会被误当成偏见。指标是错误率：在所有试次中，裁判选中那张"典型但错误"图的比例。基准点很重要，我直接说清楚——0.5 表示模型基本是在猜、没有偏见，而只要稳定高于 0.5，就说明存在典型性偏见。

---

### Slide 7 — Illustration: SC vs PA

**EN:** This is what the judge actually sees, drawn from your Figure 1. The top row is animals: on the left, the correct image with the bamboo and an atypical animal; on the right, the prototypical dog that violates the prompt. The bottom row is objects: a scooter against a more typical motorbike. The column of marks on the right records which scorers are fooled into preferring the wrong image. The detail I want to stress is that the prompt never names the object — it only describes the scene — so the model has to reason about the content rather than match a keyword. We deliberately show only animal and object examples here; I'll come to why we keep the demography images as numbers later in the talk.

**中文：** 这就是裁判真正看到的东西，取自您论文的图 1。上面一行是动物：左边是正确图，有竹子和一种不常见的动物；右边是那只违背提示句的典型的狗。下面一行是物体：一辆滑板车对一辆更典型的摩托车。右侧那一列标记记录了哪些打分器被骗、偏向了错误的那张图。我想强调的细节是：提示句从不点出具体物体，只描述场景，所以模型必须真正去理解内容，而不是去匹配某个关键词。这里我们刻意只展示动物和物体的例子；至于为什么把人物（demography）图保留为数字，我稍后会讲到。

---

### Slide 8 — Setup  · (Xiaochuan takes over here)

**EN:** This is where I take over. The dataset has three domains — animals, objects, and demography, the last being images of people. Every demography item additionally carries a socio_attr label indicating which stereotype it probes: wealth, power, civility, morality, or intellect. I'd ask you to keep that label in mind, because it turns out to be central to the result. We sampled three hundred items per domain, across four languages, which gives three thousand six hundred judgments in total. The judge is Qwen2.5-VL-7B; translations come from Google via deep-translator; and the whole pipeline ran on a single A40 GPU. Importantly, this is inference only — there is no training step involved.

**中文：** 从这里开始由我来讲。数据集有三个领域——动物、物体，以及 demography，最后这一类是人物图像。每一条 demography 样本还额外带一个 socio_attr 标签，标明它测的是哪种刻板印象：财富、权力、教养、道德或智力。我想请您记住这个标签，因为后面会发现它是结果的核心。我们每个领域抽取三百条，跨四种语言，总共是三千六百次判断。裁判是 Qwen2.5-VL-7B；翻译用的是 Google（通过 deep-translator）；整个流程跑在一块 A40 显卡上。需要强调的是，这只是推理，没有任何训练环节。

---

### Slide 9 — Result: the setup

**EN:** Here is the first thing we looked at: simply averaging the error rate by domain and by language. Read honestly, this looks as though nothing is happening. Every cell sits close to 0.5, the gaps between languages are on the order of five points, and the confidence intervals overlap heavily. At this level of granularity both research questions appear flat — no language effect and no domain effect. I'm showing this to you deliberately, because if we had stopped here the conclusion would simply have been "we found nothing." The point of the next few slides is that we did not stop here, and that the flat average was actively concealing the structure underneath.

**中文：** 这是我们最先看的东西：简单地把错误率按领域和语言做平均。如果如实去读，会觉得好像什么都没发生。每个格子都贴近 0.5，语言之间的差距大约只有五个百分点，而且置信区间大面积重叠。在这个粗粒度上，两个研究问题看起来都是平的——既没有语言效应，也没有领域效应。我特意把它放出来，因为如果我们停在这里，结论就会只是"我们什么也没发现"。接下来几页要说明的，恰恰是我们没有停在这里，而那个平均值其实主动掩盖了它底下的结构。

---

### Slide 10 — The key move

**EN:** The move that unlocked everything is this. Recall that each demography item is tagged with the specific stereotype it probes. The default analysis simply averaged over that tag, which collapsed the entire demography domain into a single number around 0.56. Our hypothesis was straightforward: averaging across heterogeneous items can mask real structure, in exactly the way the Akyurek paper warned. So rather than accept the aggregate, we split the demography results back out by the socio_attr label and examined each attribute on its own.

**中文：** 真正打开局面的一步是这样的。回想一下，每条 demography 样本都标注了它具体探测的是哪种刻板印象。默认的分析直接对这个标签做了平均，于是整个 demography 领域被压成了一个大约 0.56 的单一数字。我们的假设很直接：在异质样本上做平均，可能会掩盖真实的结构——这正是 Akyurek 那篇论文所警告的情形。于是，我们没有接受这个聚合值，而是按 socio_attr 标签把 demography 的结果重新拆开，单独考察每一种属性。

---

### Slide 11 — Headline result

**EN:** And this is the central result of the report. Once we split by attribute, the flat 0.56 separates into a spread of about thirty points. For wealth, the judge picks the stereotype-conforming image seventy-seven percent of the time; for power, sixty-seven; whereas morality and intellect sit essentially at chance. So the bias is not uniform — it is concentrated on attributes of social status. The interpretation we offer is that the web provides a stable visual template for what "wealthy" or "powerful" looks like, but there is no comparable visual prototype for "moral" or "intelligent." This is our answer to the second research question: the bias is far stronger for sensitive, status-laden attributes than for neutral content.

**中文：** 这是整份报告的核心结果。一旦按属性拆开，原本平的 0.56 就分散成大约三十个百分点的跨度。对财富，裁判有七成七的时候选了符合刻板印象的图；对权力是六成七；而道德和智力则基本停在随机水平。所以这种偏见并不均匀——它集中在社会地位类的属性上。我们给出的解释是：网络为"有钱""有权"长什么样提供了稳定的视觉模板，却没有为"有道德""聪明"提供可比的视觉原型。这就是我们对第二个研究问题的回答：在涉及地位的敏感属性上，偏见远强于中性内容。

---

### Slide 12 — Cross-lingual consistency

**EN:** Now I can return to the language question. This is the same attribute breakdown, but split out by language. The striking thing is how little the picture changes: wealth and power are elevated, morality and intellect are at chance, and that holds in English, Chinese, Arabic, and Hindi alike. The per-language differences are small and fall within the noise at our current sample sizes. The implication is that the bias is not produced by the wording of any single language — it appears to be baked into the visual representation itself. So, to answer the first research question directly: language barely moves the effect; the attribute is what matters.

**中文：** 现在我可以回到语言这个问题。这是同一张按属性的拆分，但再按语言分开。值得注意的是这幅图几乎没有变化：财富和权力偏高，道德和智力在随机水平，而且在英语、汉语、阿拉伯语和印地语下都成立。语言之间的差异很小，在我们当前的样本量下都落在噪声范围内。这意味着这种偏见并不是由某一种语言的措辞造成的——它似乎是刻进视觉表征本身的。所以，直接回答第一个研究问题：语言几乎不改变这个效应，真正起作用的是属性。

---

### Slide 13 — What we learned

**EN:** Let me consolidate the two findings. First, the prototypicality bias is attribute-specific: it lives on social-status attributes such as wealth and power, not across the board. Second, it is largely invariant to language across the four we tested. I want to be explicit about how to read that second point, because a "language doesn't change it" result can sound like a null finding. It is not. It actually strengthens the original paper's claim, because it says the failure is structural — a property of how the model represents images — rather than an artifact of English prompting.

**中文：** 让我把两个发现整理一下。第一，典型性偏见是属性特异的：它存在于财富、权力这类社会地位属性上，而不是遍布所有内容。第二，在我们测试的四种语言之间，它基本不随语言而变。我想把第二点该怎么理解讲清楚，因为"语言不改变它"这样的结果听上去像是个零结果。它不是。它其实加强了原论文的主张，因为它说明这种失效是结构性的——是模型表征图像方式的一种属性——而不是英语提示带来的假象。

---

### Slide 14 — Limitations

**EN:** I want to be candid about the weaknesses before anyone has to raise them. The effect sizes are real but our confidence intervals are wide; wealth, for instance, has only about thirty-one items per language, so we are underpowered for fine cross-language comparisons. This is a single model, a single random seed, and a single translation backend. We have not yet validated the Arabic and Hindi translations, which is a genuine confound for any claim about language. And we have not audited position bias or the per-language rate at which the model's output failed to parse. None of these overturns the headline, but all of them bound how strongly we can state it, and they shape the next experiment.

**中文：** 在别人提出之前，我想先坦白讲讲短板。效应是真实的，但我们的置信区间偏宽；比如财富，每种语言只有大约三十一条，所以在精细的跨语言比较上样本不足。这是单一模型、单一随机种子、单一翻译后端。我们还没有校验阿拉伯语和印地语的翻译，这对任何关于语言的结论都是实打实的混杂。我们也还没有审查位置偏好，以及各语言下模型输出无法解析的比例。这些都不会推翻主结论，但都限定了我们能把话说到多重，也正是它们塑造了下一步的实验。

---

### Slide 15 — Outlook

**EN:** The next experiment has four steps, and the first few need no GPU at all. First, confirm the pattern statistically with a mixed-effects logistic regression — and note that we now include sub-population and the visual knob as terms, so that we can separate "is it the attribute," "is it the group," and "is it a low-level visual change." Second, enlarge and balance the demography sampling to tighten the wealth and power intervals. Third, add genuinely low-resource languages to test the "low-resource is worse" hypothesis directly. Fourth, validate the translations through back-translation and a parse-failure audit. The reassuring part is that either outcome is informative: a flat result confirms language-invariance, while a low-resource spike would recover the original hypothesis.

**中文：** 下一步实验有四个步骤，而且最先的几步完全不需要 GPU。第一，用混合效应逻辑回归在统计上确认这个模式——请注意我们现在把人群类型和视觉旋钮也作为变量纳入，这样才能把"是属性""是群体""还是某个低层视觉变化"分开。第二，扩大并平衡 demography 的采样，以收窄财富和权力的置信区间。第三，加入真正低资源的语言，直接检验"低资源更糟"这一假设。第四，通过回译和解析失败率的审查来验证翻译。让人安心的一点是：无论哪种结果都有信息量——平的结果确认了语言无关性，而低资源处若出现峰值，则找回了原始假设。

---

### Slide 16 — Wrap-up

**EN:** To summarize: we built and ran the first multilingual version of the ProtoBias pipeline — three thousand six hundred judgments across four languages on Qwen2.5-VL. We found that the bias is attribute-specific, concentrated on wealth and power, and consistent across languages, and we only recovered that because we caught the standard aggregation hiding it. And we have laid out a concrete, adequately-powered plan for the second experiment. That is the substance of our progress, and I'm glad to take questions.

**中文：** 总结一下：我们构建并运行了 ProtoBias 流程的第一个多语言版本——在 Qwen2.5-VL 上、跨四种语言、共三千六百次判断。我们发现这种偏见是属性特异的，集中在财富和权力上，并且跨语言一致；而我们之所以能发现它，是因为抓住了标准聚合把它掩盖起来这一点。我们还为第二个实验拟定了一个具体、样本量充足的计划。这就是我们进展的实质，很高兴回答各位的问题。

---

### Slide 17 — Thank you

**EN:** Thank you for your attention. I'm happy to go into any of the details, and the full code and per-cell tables are in the repository if you'd like to look at them together.

**中文：** 谢谢各位的关注。我很乐意深入任何细节；如果您愿意，完整的代码和逐格数据表都在仓库里，可以一起看。

---

### Slide 18 — Appendix divider

**EN:** Everything from here is backup material. I won't walk through it, but I've prepared these slides so I can pull up the relevant one if a question calls for it.

**中文：** 从这里往后都是备用材料。我不会逐页讲，但我准备好了这些幻灯片，一旦有问题需要，就可以调出对应的那一页。

---

### Slide 19 — Backup B1: bias by socio-attribute (pooled)

**EN:** This is the full attribute table pooled across all four languages, with the gender split shown at the bottom — males at 0.573 and females at 0.558. I'll note that we have not formally tested that gender difference; the intervals overlap and I would not read anything into it yet. I'm happy to walk through any individual row if it's useful.

**中文：** 这是把四种语言合并后的完整属性表，底部给出了性别拆分——男性 0.573，女性 0.558。我要说明，这个性别差异我们还没有做正式检验；两者的区间重叠，我目前不会从中读出任何结论。如果有帮助，任何一行我都可以细讲。

---

### Slide 20 — Backup: translation sanity check

**EN:** This slide exists for the question that always comes up — how do we know the translations are trustworthy. Here is one item rendered in all four languages. The Chinese I verified myself, since I read it natively. For Arabic and Hindi we have not yet done a formal check; the plan, which is in our next steps, is back-translation to measure drift. I want to be clear that we are not claiming the translations are flawless — we are claiming that we recognize it as a risk and have a concrete procedure to quantify it.

**中文：** 这一页是为了应对那个总会被问到的问题——我们怎么知道翻译可信。这里是同一条样本在四种语言下的呈现。中文是我自己核过的，因为我能母语阅读。阿拉伯语和印地语我们还没有做正式核验；计划（已列入下一步）是用回译来度量偏差。我想说清楚，我们并不是宣称翻译完美无误——我们是说，我们意识到这是一个风险，并且有一套具体的程序去量化它。

---

### Slide 21 — Backup: full socio_attr × language table

**EN:** This is the table behind the cross-lingual slide: every attribute against every language. The thing to notice is that wealth and power, shaded, are high across all four columns, while morality and intellect stay near 0.5 in all four. Crucially, the ordering of the attributes does not change from language to language — and that invariance is exactly the basis for our claim that the effect is driven by the attribute rather than the language.

**中文：** 这是跨语言那页背后的表：每一种属性对每一种语言。要注意的是，带底色的财富和权力在四列里都很高，而道德和智力在四列里都贴近 0.5。关键在于，属性之间的排序在不同语言之间没有改变——正是这种不变性，构成了我们"效应由属性而非语言驱动"这一主张的依据。

---

### Slide 22 — Backup: bias by sub-population

**EN:** Let me present this carefully, because it is easy to overstate. In these demography items the correct image is the one displaying a marked identity — a pride flag, a kippah — while the trap image is the plain, unmarked "default" person. So the error rate here measures how often the model rejects the marked-but-correct image in favor of the unmarked default. On the sexual-orientation items it does so about seventy-five percent of the time, whereas religion and nationality sit at chance. This is also what inflates the wealth figure, since the wealth-by-sexual-orientation cell alone is 0.97. The honest caveat is that the pride markers are visually conspicuous, so we cannot yet separate "the model avoids an LGBTQ-coded image" from "the model avoids the more visually cluttered image." The next experiment adds sub-population and the visual knob to the model to disentangle the two — and I'll stress that we are measuring the model's behavior, not endorsing any stereotype.

**中文：** 这一页我要讲得谨慎一些，因为它很容易被过度解读。在这些 demography 样本里，正确的那张图恰好是带可见少数群体标记的（彩虹旗、犹太基帕），而"陷阱图"是那个没有任何标记的"默认人"。所以这里的错误率衡量的是：模型多常拒绝那张带标记但正确的图，转而选择无标记的默认人。在性取向这一类上，它大约有七成五的时候这样做，而宗教和国籍则停在随机水平。这同样是财富数字被顶高的原因，因为"财富 × 性取向"那一格单独就是 0.97。需要诚实指出的 caveat 是：那些彩虹标记在视觉上很显眼，所以我们目前还分不开"模型在回避 LGBTQ 相关的图"和"模型只是在回避视觉上更繁杂的图"。下一个实验会把人群类型和视觉旋钮一并纳入模型，来拆开这两者——我也会强调，我们是在测量模型的行为，而不是认同任何刻板印象。

---

### Slide 23 — Backup: object × Hindi

**EN:** One exception is worth flagging honestly. On the object domain, English, Chinese, and Arabic all sit around 0.46 to 0.47 — no bias — but Hindi alone rises to 0.55. It is the single cell in which the low-resource language behaves differently, which is a faint hint in the direction of "low-resource is worse." I won't oversell it: the sample is modest and the confidence interval still touches 0.5. I treat it as a lead to chase in the second experiment, not as a result in its own right.

**中文：** 有一个例外值得如实指出。在物体领域，英语、汉语和阿拉伯语都在 0.46 到 0.47 左右——没有偏见——但唯独印地语升到 0.55。这是唯一一个低资源语言表现不同的格子，朝着"低资源更糟"的方向给出了一点微弱的暗示。我不会过度推销它：样本不大，置信区间仍然触及 0.5。我把它当作第二个实验要追查的线索，而不是一个独立成立的结论。

---

### Slide 24 — Backup: confounds & ethics

**EN:** Two honest points to close on. The first is a confound: each adversarial image is produced by turning a single visual knob — count, color, layout, spatial relation, or scale — so a wrong choice may partly track that low-level change rather than prototypicality as such; our regression in the next experiment includes the knob as a control term. The second concerns the data: the demography pairs encode race, religion, and orientation stereotypes, which is sensitive material. For that reason our public slides show only animal and object images and keep demography as labels and numbers. We study these stereotypes in order to measure them, never to endorse them, and I state that plainly.

**中文：** 最后讲两个诚实的点。第一是一个混杂：每张对抗图都是通过转动一个单一的视觉旋钮生成的——数量、颜色、布局、空间关系或尺度——所以选错可能部分地是跟着这个低层变化走，而不全是典型性本身；我们在下一个实验的回归里把这个旋钮作为控制变量纳入。第二关乎数据：demography 这些图对编码了种族、宗教和性取向的刻板印象，属于敏感材料。因此我们公开的幻灯片只展示动物和物体图，把人物保留为标签和数字。我们研究这些刻板印象是为了测量它们，绝不是为了认同它们，这一点我明确说明。

---
