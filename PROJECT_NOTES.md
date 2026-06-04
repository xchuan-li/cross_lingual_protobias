# 跨语言典型性偏见研究 — 项目笔记 (Multi-linguistic histoBias)

> 最后更新:2026-05-31
> 这份文档是项目的长期记忆,记录动机、数据结构、实验设计与决策理由。新人/未来的自己读完这一份就能上手。

---

## 1. 项目是什么

**课程项目 Topic 6:跨语言「典型性偏见」在多模态 AI 评估中的表现**(导师 Subhadeep)。

### 核心直觉
多模态 AI(看图 + 读文字)在判断「这张图配不配这句话」时,可能不只看**语义是否正确**,还会被**刻板印象 / 典型形象**带偏。

经典例子:提示「a doctor treating a patient」
- 语义正确的图:女医生
- 「更典型但其实是偏见」的图:男医生

模型若倾向选刻板印象那张,就说明它没有「真正理解语义」,而是依赖某种文化里的「典型形象」。

### 两个研究问题
- **RQ1:跨语言一致性。** 把同一个提示翻成多种语言,模型的判断会不会随语言改变?若会变 → 模型依赖语言/文化特定的「典型表征」,而非语义。
- **RQ2:敏感 vs 中性领域。** 跨语言差异在**社会敏感领域**(财富、智力、职业、宗教等)是否比**中性领域**(动物、物体)更严重?借此判断 AI 偏见是「全人类通用」还是「被语言文化塑造」。

### 参考文献(`papers/` 目录)
- [1] https://aclanthology.org/2025.findings-acl.585/ → `2025.findings-acl.585.pdf`
- [2] https://aclanthology.org/2024.emnlp-main.474/ → `2024.emnlp-main.474.pdf`
- [3] https://aclanthology.org/2022.gebnlp-1.9/ → `2022.gebnlp-1.9.pdf`
- [4] https://aclanthology.org/2025.findings-emnlp.783/ → `2025.findings-emnlp.783.pdf`
- [5] https://arxiv.org/abs/2601.04946 (**ProtoBias 原论文**) → `2601.04946v2.pdf`

---

## 2. 数据集(已确认,权威)

**HuggingFace:`subha-roy/dl4dh_data`** — 这就是 ProtoBias 数据集本体。

```python
from datasets import load_dataset
ds = load_dataset("subha-roy/dl4dh_data")   # 单一 split: "test"
d  = ds["test"]                              # n = 1500
```

### 每条样本 = 一对图 + 三句文字
| 字段 | 含义 | 角色 |
|---|---|---|
| `correct_image` / `correct` | 语义正确但**不典型**的图 + 描述 | ✅ 正确答案 |
| `adversarial_image` / `adversarial` | **典型但错误**的图 + 描述 | ❌ 偏见陷阱 |
| `text` | **中性遮蔽提示**(把具体对象抽象掉) | 用来问模型 |

图片:1024×1024 JPEG,存为 `{'bytes':..., 'path':...}`,用 `PIL.Image.open(BytesIO(bytes))` 解码。

**典型样本(row 0):**
- `text`: "An animal perches on a branch with a leaf pile in the background of a grassy field."
- `correct`: "A **walking stick insect** perches on a branch..." (竹节虫,正确但不典型)
- `adversarial`: "A **monkey** perches on a branch..." (猴子,典型但错误)
- 模型若选猴子那张 = 中了典型性偏见。

### 三大领域,完美平衡 500/500/500 → 直接服务 RQ2
| `domain` | n | 内容举例 | 角色 |
|---|---|---|---|
| `animal` | 500 | 竹节虫 vs 猴子 | 中性 |
| `object` | 500 | 清酒杯(ochoko) vs 红酒杯 | 中性 |
| `demography` | 500 | 涉及宗教/性取向/国籍 + 道德/财富/智力等 | **社会敏感** |

### 其它可用于细分分析的字段
- `subcategory`(9 类):bird / vehicle / mammal / religion / sexual_orientation / tableware / nationality / furniture / animal
- `socio_attr`(仅 demography,各 ~60–140):morality / civility / power / intellect / wealth
- `gender`(仅 demography):male 270 / female 230
- `group_category`(仅 demography):religion / sexual_orientation / nationality
- `knob` = `adversarial_knob`(操纵维度,5 类):count / color_tone / layout_relation / spatial / scale_size
- `model`:生成文本用的 LLM(Qwen2.5-14B / gemma-3-12b / Llama-3.1-8B)
- `image_model_short`:生成图片用的模型(flux1_schnell / sana / sd35)

### ⚠️ 伦理注意
`demography` 那 500 条是带种族/宗教/性取向刻板印象的人物图(例:row 1499 "rude white Christian man" vs "rude brown Muslim man")。
→ **报告里主示例用 animal/object 的图;socio 样例要谨慎、学术化呈现。** 评委会关注伦理处理。

---

## 3. 实验设计

### 任务:2AFC(二选一强制选择)
给模型看 **一对图(correct + adversarial,随机左右顺序)+ 中性 `text`**,问:「哪张图更符合这句描述?」
- 正确答案永远是 `correct_image`。
- 模型选 `adversarial_image` = **中了典型性偏见**。
- **核心指标:典型性错误率 = 选到 adversarial 图的比例**(越高 = 偏见越重)。
- 要随机化左右顺序,避免位置偏好混入。

### 自变量
- **语言**(RQ1):翻译 `text`。
- **domain × 语言**(RQ2):看 demography 的错误率是否随语言比 animal/object 波动更大。

### 输出图表(撑起评分表的 Results 4 分 + Illustrations 0.5 分)
1. 柱状图:错误率 **按语言** 分组(RQ1)
2. 柱状图:错误率 **按 domain × 语言**(RQ2)

---

## 4. 关键决策与理由

### 模型:Qwen2.5-VL(本地 GPU 推理)
- **没有「训练」环节** —— 这是纯推理/评测,GPU 只用于本地批量加速,不更新权重。1500 条全跑很轻松。
- 选 Qwen 的额外好处:它是阿里做的,**中英是强项语言**,这正好让「模型语言资源量 ↔ 语义鲁棒性」成为可分析的变量。

### 语言:高资源 vs 低资源 对照轴
| 语言 | 选它的理由 | 测什么 |
|---|---|---|
| **英语** | Qwen 高资源 + 数据原文 | 基线 |
| **中文** | Qwen 母语级、高资源、汉字 | 高资源对照 + 中华文化典型性 |
| **阿拉伯语** | 中/低资源、不同字系、强文化绑定(宗教) | 低资源是否更易被带偏;对 demography 敏感 |
| **印地语 / 斯瓦希里语** | 真正低资源 | RQ1 最可能出效应处 |

- **核心对照 = 高资源(英/中)vs 低资源(阿/印)。** 这个对比最容易跑出「有差异」,而「有差异」是 Results 拿分关键。
- Framing(report/QA 用):「我们故意选 Qwen 的强项(中/英)和弱项(阿/印)语言对照,因为 RQ1 本质是在问:**模型语义鲁棒性是否随语言资源量下降。**」
- 第一次报告可先跑 **英 + 中 + 阿** 三种,Outlook 里说「下一步扩到低资源印地/斯瓦希里」。

### 翻译
- 只需翻 `text`(可选也翻 `correct`/`adversarial` 做更细对照)。
- 用 Qwen 自身或 Google Translate 翻 → **人工抽查**(自己懂中文,至少能验证中文版)。
- 报告写清「翻译用 X,人工校验 N 条」→ 正面回答必被问的「翻译质量怎么保证」。

### 已知混杂因素(诚实加分点 / QA)
- adversarial 图同时改了 `knob`(如颜色),模型选错不一定纯是「典型性」,也可能是其它视觉差异。
- 报告主动点出 → QA 项加分。

---

## 5. 下周第一次报告:得分地图(满分 10)

| 评分项 | 分 | 怎么拿 | 状态 |
|---|---|---|---|
| **Progress Results** | **4** | 有新结果 + 图表(pipeline 跑通 + 初步发现) | ⚠️ 本周核心产出 |
| Presentation content | 1 | 讲清选题 + RQ1/RQ2 + 方法 | 易 |
| Presentation delivery | 1 | 口齿清楚、声音够 | 排练 |
| Presentation design | 1 | 幻灯片规整 | 做 |
| Outlook | 1 | 明确下一步(全量1500、加模型、按knob/gender细分、加低资源语言) | 易 |
| QA | 1 | 预演问题(为什么这几种语言/翻译质量/小样本可信吗) | 预演 |
| Nice illustrations | 0.5 | 数据/方法/结果的示例图 | 配合结果 |
| Awareness of related work | 0.5 | 讨论 ≥2 篇相关论文 + ProtoBias 原文 | 读 papers/ |

**策略:别把报告做成「我们读了5篇论文」(只值0.5分)。重心放在跑出初步结果。**

---

## 6. 进度日志
- 2026-05-31:确认数据集 = `subha-roy/dl4dh_data`(1500条, 3 domain 各500)。确认环境 `datasets 4.8.5`。定了实验设计(2AFC)、模型(Qwen2.5-VL)、语言(英/中/阿 + 可选印地)。
- 2026-05-31:搭完 pipeline,放在 `code/`(config / data_utils / translate / backends / run_eval / analyze + README)。用 `MockChooser` 在 Mac 上空跑全流程验证通过(抽样→解码图对→2AFC→出两张图)。冒烟假数据已清。下一步:在 GPU 机器上跑真 Qwen2.5-VL。
- 2026-06-01:**首轮真实 GPU 跑通**。Alex 集群 A40,Qwen2.5-VL-7B-Instruct,`N_PER_DOMAIN=50` × 3 域 × 3 语言(英/中/阿)= 450 次 2AFC,eval 约 2.5 分钟,显存峰值 ~16 GB。产出 `results/{predictions.jsonl,summary.csv,translations.json}` + 两张图。初步典型性错误率(每格 n=50):animal en .64 / zh .62 / ar .56;object en .52 / zh .40 / ar .42;demography en .56 / zh .58 / ar .58。读数:错误率普遍 0.4–0.64(有偏见信号),但 n=50 CI 太宽(±0.13),跨语言差异**暂不显著**;object 比 animal 略低。
- 2026-06-01:启动**第二轮**——加 Hindi(低资源语言),`N_PER_DOMAIN=300`(3 域共 900 行)× 4 语言(英/中/阿/印)= 3600 次 2AFC。`config.py` 已设 `ACTIVE_LANGUAGES=["en","zh","ar","hi"]`。
  - ⚠️ **坑1 翻译要联网**:`translate.py` 用 Google(deep-translator),compute node 离线。必须先在 **login node** 跑 `python translate.py` 生成 hi/zh/ar 翻译缓存,再 sbatch。`submit_eval.sh` 只含 run_eval+analyze,不含翻译。
  - ⚠️ **坑2 采样不嵌套**:`rng.sample(idxs, k)` 改 k(50→300)后抽到的 900 行**不是**旧 150 行的超集。旧 `predictions.jsonl`(450 条,旧 id)会被 `analyze.py` 一起读入污染结果 → 跑前先归档旧 `predictions.jsonl`,从空文件重跑,保证 900×4 干净。
- 2026-06-01:**第二轮跑完**(job 3687960,A40,Qwen2.5-VL-7B)。3600 条预测(900×4),每格 n≈300(animal,zh=299、object,ar=298,各掉 1–2 条翻译解析)。退出时有个 `resource_tracker / _thread.RLock` AttributeError,是解释器关闭的无害告警,不影响结果。典型性错误率(error_rate,即选到对抗/典型图的比例):
  | domain | en | zh | ar | hi |
  |---|---|---|---|---|
  | animal | .523 | .575 | .570 | .573 |
  | demography | .560 | .577 | .573 | .553 |
  | object | .467 | .470 | .463 | **.553** |
  **读数**:(1) 整体偏见信号弱,错误率都贴着 0.5;animal/demography 略高(~.55-.58,轻微偏见),object 基本随机(en/zh/ar 的 CI 压在 0.5 上,无偏见)。(2) 跨语言主效应不显著,同 domain 内各语言 CI 大面积重叠。(3) **关键发现:object×hindi=.553 是唯一异常**——其他三语在 object 都只有 .46-.47,只有低资源语言 hi 在"物体"类别明显偏高,局部支持"低资源语言偏见更强"假说。其余 domain 里 hi 与他语无异。下一步建议:object×hi 这格做 bootstrap/对比检验确认显著性;若要更强结论,考虑 32B 模型或加更多低资源语言。
- 2026-06-01:**重分析 exp1 + 立 exp2**。把 exp1 结果归档到 `code/experiments/exp1_900x4lang/`(含 README、config 快照、results、figures)。重分析时发现 `analyze.py` 把 demography 的 `socio_attr/gender/knob` 字段全平均掉了——拆开 `socio_attr` 后真信号浮现:**典型性偏见是属性特异的**,wealth=.774 / power=.672(强偏见)>> civility=.539 > morality=.487 / intellect=.479(≈随机),平均成 .56 把 0.3 的跨度抹平了。且该模式**四语一致**(en/zh/ar/hi)。重新定调:**偏见是"属性特异 + 跨语言通用"的结构性问题,而非语言驱动**——这反而加固原 paper 主张(注:原 paper 是英文单语、研究评测指标的 prototypicality bias,我们做的是其多语言扩展,"语言无关"是合法的多语言结论)。已建 `code/experiments/exp2_attribute_bias/`:`PROPOSAL.md`(发现过程+RQ+方法)、`reanalyze_exp1.py`(可复现重分析)、`exp1_attribute_breakdown.csv`、figA/figB。exp2 计划:混合效应 logistic 回归检验"属性≫语言"、加大/平衡 demography 采样、(可选)扩低资源语言谱系、翻译质量回译校验。下一步无需 GPU:先在 exp1 数据上跑混合效应模型坐实核心结论。
