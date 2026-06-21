# v1 — Course MVP: Cross-lingual Prototypicality Bias Evaluation

## 核心思路

课程项目 Topic 6 的第一版实现。核心问题：多模态 AI（VLM）在判断「哪张图更符合描述」时，是否受刻板印象/典型形象影响（prototypicality bias），且该偏见是否随提示语言改变？

ProtoBias 数据集提供了天然的 2AFC（二选一强制选择）控制：
- `correct_image`：语义正确但**不典型**的图（e.g., 竹节虫 perches on branch）
- `adversarial_image`：**典型但错误**的图（e.g., 猴子 perches on branch）
- `text`：中性遮蔽描述（e.g., "An animal perches on a branch"）

选到 adversarial = 中了典型性偏见。

## 实验

### `experiments/` — （无独立实验目录；pipeline 在 `shared/code/`）

第一版 pipeline：
- `shared/code/run_eval.py` — 主评估循环（2AFC 推理）
- `shared/code/backends.py` — 模型后端（MockChooser + Qwen2.5-VL）
- `shared/code/translate.py` — Google Translate 批量翻译
- `shared/code/config.py` — 实验配置
- `shared/code/data_utils.py` — 数据加载和解码

**试跑（N=50/domain）：**
- 450 条预测（EN/ZH/AR × 3 domains × 50）
- cluster A40，Qwen2.5-VL-7B-Instruct
- 结果：错误率 .40–.64，CI 宽（n=50，±.13），跨语言差异不显著
- 结论：有偏见信号（>0.5）但样本太小，跨语言差异无法下定论

第一轮结果已被第二轮（v2）覆盖，archive 见 `shared/code/results/`（v2 的结果）。

## 报告

### `paper/`

- `ProgressReport_1.pptx / .pdf` — 第一次进度报告（幻灯片）
- `SPEAKER_NOTES.md / .pdf` — 演讲稿
- `PRESENTATION_OUTLINE.md` — 幻灯片结构大纲
- `build_deck.js / build_supplement.py` — 幻灯片/补充材料构建脚本
- `assets/` — 演示用样本图（protobias_examples.png）

## 核心发现

- 整体偏见信号弱（≈0.5），animal/demography 略高（~.55–.58），object 接近随机
- 跨语言主效应不显著（同 domain 内各语言 CI 大面积重叠）
- N=50 样本量严重不足，跨语言对比无效

## 局限（→ v2 的改进方向）

- 样本太小（N=50/domain），所有跨语言结论都缺乏统计功效
- 分析粒度太粗：demography 被平均成单个数字，隐藏了属性内部结构
- 只有 3 种语言（EN/ZH/AR），缺低资源语言对比
- `analyze.py` 未使用 `socio_attr`/`gender`/`knob` 字段
