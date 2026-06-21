# AUDIT — ProtoBias · Cross-lingual Prototypicality Bias

- **论文/报告**：`README.md`、`PROJECT_NOTES.md`、`v2/paper/proposal_new.md`
- **结果**：`v2/experiments/exp1_900x4lang/`、`v2/experiments/exp2_attribute_bias/`、`shared/figures/`
- **代码**：`shared/code/`、`v2/experiments/exp2_attribute_bias/reanalyze_exp1.py`
- **状态**：⬜ 未开始 · 最近一次：—

> **4 步**：① 看论文框架 → ② 列实验 → ③ 读代码（🔴核心精读 / ⚪环境略读）→ ④ 验结果（对账 + 查 backing）
> 特注：纯推理评测、无训练；主结论（attribute-specific）来自一次**重分析** → ④ 的统计（每格 n、CI、混合效应）和 knob confound 是重点。

---

## ① 论文整体框架（在 claim 什么、怎么论证）
_[待填：一段话——VLM 选"典型但错"图 vs "语义对但不典型"图；2AFC；主结论 = 偏见属性特异（wealth/power 强，morality/intellect≈.5）且跨语言通用]_

## ② 有哪些实验
| 实验 | 支撑哪个结论 | 报告位置 | 结果文件 |
|---|---|---|---|
| _[待填]_ exp1 900×4lang | 跨语言/领域错误率 | PROJECT_NOTES | exp1_900x4lang/ |
| exp2 attribute_bias | 属性特异（主结论） | proposal_new | exp2_attribute_bias/*breakdown* |

## ③ 读代码 — 本次阅读顺序（按数据流；🔴核心精读 / ⚪环境略读）
> 🔴 = 有 bug 会让结果数变 → 逐行读、可能要改；⚪ = 只让程序跑 → 扫输入输出即可。

1. ⚪ `shared/code/config.py` + `data_utils.py` — 采样/语言/解码图对 → 略读，**但瞄一眼采样 seed 与"嵌套采样"坑**
2. ⚪ `shared/code/translate.py` — 翻 `text` → 略读（翻译质量是 caveat，不是 bug）
3. ⚪ `shared/code/backends.py` — Qwen2.5-VL 调用 → 略读
4. 🔴 `shared/code/run_eval.py` — 2AFC：图对 + 中性 text，随机左右，记选择 → **看：配对正确？左右随机化防位置偏好？正确答案永远是 correct_image？**
5. 🔴 `shared/code/analyze.py` — error_rate（选 adversarial 比例）+ 按 domain/语言聚合 + 出图 → **指标定义**
6. 🔴 `v2/experiments/exp2_attribute_bias/reanalyze_exp1.py` — 拆 socio_attr → wealth/power/… breakdown → **命门：主结论来源；每格 n、有没有 CI / 显著性检验**
> **最该盯**：`run_eval.py`（2AFC 配对+随机化）、`analyze.py`（指标）、`reanalyze_exp1.py`（主结论+统计）。

## ④ 验结果和结论
> - **对账** `cat v2/experiments/exp2_attribute_bias/*breakdown*.csv`（.77/.67/.49/.48 对回 README）
> - **查 backing / 统计** 每个 socio_attr 格 n 够吗、error_rate 的 CI 排不排除 **0.5**、"属性≫语言"是否真跑混合效应；overclaim："invariant/structural" 是"没测出差异"还是"证明无差异"

### 发现表
| 论文位置 | 印的数 | 结果文件 | 文件值 | 对账 | backing | 备注 |
|---|---|---|---|:--:|:--:|---|
| _[待填]_ wealth error_rate | .774 | exp2…/breakdown.csv | | | | |
| | | | | | | |

### 待修红旗（OPEN）
1. _[待填]_

### 可放心展示
- _[待填]_
