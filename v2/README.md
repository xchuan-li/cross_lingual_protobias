# v2 — 4-Language Full Eval + Attribute-Specific Discovery

## 核心思路

两个关键进展：

1. **扩大规模**：N=300/domain × 4 语言（EN/ZH/AR/**HI**）= 3600 条预测，CI 压到 ±0.056
2. **发现隐藏维度**：拆分 `socio_attr` 后，demography 的「平均偏见=0.56」被分解为：
   - wealth=**.774**、power=**.672**（强偏见，视觉刻板印象明确）
   - civility=.539（轻微）
   - morality=.487、intellect=.479（≈随机，无可视化偏见）

这个 **0.30** 的跨属性跨度被原始分析完全平均掉了。

## 核心结论（重构）

> Prototypicality bias 是**属性特异的**（集中于社会地位属性），且**跨语言一致**（EN/ZH/AR/HI 四语言中模式相同）。它是视觉表征的结构性属性，而非语言驱动的。

这是一个 null/robustness 结论：「语言无关」比「语言有效」对 ProtoBias 原论文更有支撑力（原论文本来就在讲结构性偏见，不是语言特定偏见）。

**关键细节 — object × Hindi = .553**：其余三语的 object 都只有 .46–.47，唯有低资源语言 hi 在「物体」类别异常偏高。局部支持「低资源语言偏见更强」假说，但单格 n≈300 还不够确定。

## 实验

### `experiments/exp1_900x4lang/`

4 语言全量评估结果（900 rows × 4 languages = 3600 predictions）：
- SLURM job 3687960，NHR@FAU Alex A40
- `results/` — predictions.jsonl, summary.csv, translations.json
- `figures/` — fig1 错误率按语言 / fig2 按 domain×语言
- `config_snapshot.py` — 实验参数快照
- `BRIEF.md` — 结果简报

### `experiments/exp2_attribute_bias/`

在 exp1 数据上重分析（**无需新 GPU 运行**）：
- `reanalyze_exp1.py` — 按 socio_attr 拆分 demography，可复现
- `exp1_attribute_breakdown.csv` — 每个 socio_attr × lang 的错误率 + CI
- `figures/figA_bias_by_attribute.png` — 核心发现（属性特异性）
- `figures/figB_attribute_by_language.png` — 跨语言一致性
- `PROPOSAL.md` — exp2 完整提案（含 RQ/方法/统计设计/后续计划）

## 报告

### `paper/`

- `proposal_new.md` — 完整的 workshop 论文方向提案（三阶段：课程版/workshop版/完整论文版）
  - 核心论点：「Cross-lingual stability is not sufficient evidence of semantic grounding」
  - 引入 Cross-lingual Flip Rate、Stable Bias Rate、Stable-but-Ungrounded Rate 新指标
  - 阶段3（强 paper）计划：shortcut-severing interventions
- `SUPPLEMENT_additions.pptx` — 报告补充材料幻灯片

## 局限（→ v3 的改进方向）

- exp2 的核心统计（混合效应逻辑回归）尚未运行，wealth/power 效应还是点估计
- demography 采样不均衡：wealth n=124，morality n=372，各语言每格仅 ≈30–60 条
- 低资源语言对比只有 Hindi，资源梯度不够（缺 Swahili/Bengali/Yoruba）
- 翻译质量未经回译校验（ar/hi 翻译可靠性未评估）
- 位置偏好（position bias）未检验：adv_position 随机化是否实际有效
