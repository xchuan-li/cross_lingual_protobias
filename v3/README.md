# v3 — Workshop Paper: Statistical Confirmation + Extended Languages

## 核心思路

将 v2 的探索性发现转化为可发表的 workshop 论文：

1. **坐实 attribute ≫ language 效应**：混合效应逻辑回归，从点估计升级为统计推断
2. **扩大低资源语言谱系**：加 Swahili/Bengali/Yoruba，真正建立高→低资源对照轴
3. **翻译质量控制**：回译 + 嵌入余弦校验，将翻译噪声与语言效应分离

**当前状态：未开始。** v2 的发现是 v3 的前提条件。

## 计划实验

### Exp3a — 混合效应模型（无需 GPU，在 exp1 数据上运行）

```
picked_adversarial ~ socio_attr * lang + gender + (1 | item)
```

- 固定效应：`socio_attr`（5 类）× `lang`（4 类）+ `gender`
- 随机效应：`item`（同一图对在 4 语言下被重复看到）
- 检验：likelihood-ratio test of `lang` term 和 `socio_attr × lang` interaction
- 目标：wealth/power CIs 与 morality/intellect 不重叠 → 结论锁定

### Exp3b — 扩大 demography 采样（需 GPU）

- 每个 socio_attr × lang 格子 ≥150 条（当前 wealth/lang ≈ 31 条）
- 在 `config.py` 设 stratified sampling on `socio_attr`
- 目标：给混合效应模型足够的 power

### Exp3c — 扩展语言谱系（可选，需 GPU）

| 语言 | 资源等级 | 选择理由 |
|---|---|---|
| English | 高 | 基线 |
| Chinese | 高 | Qwen 强项 |
| Spanish/French | 高 | 欧洲高资源对照 |
| Arabic | 中 | 字系差异 + 宗教文化 |
| Hindi | 中 | 第一轮低资源 |
| Swahili | 低 | Sub-Saharan，Qwen 训练数据稀少 |
| Bengali | 低 | 高说话者数 + 低资源 |
| Yoruba | 低 | 真正低资源极端 |

资源等级作为有序预测变量，测试 RQ3（低资源语言偏见是否更强）。

### Exp3d — 翻译质量控制（CPU，login node）

- 回译：非英语 → 英语，计算原文与回译的嵌入余弦相似度
- 标记翻译漂移 > 阈值（e.g., cosine < 0.85）的条目
- 报告各语言 parse-failure rate（`raw_choice` 不在 {1,2}）
- 排除/标记高漂移条目后重跑统计

## 目标成果

1. 混合效应模型结果表（fixed effects + LRT p-values）
2. 图：bias by attribute（tightened CIs），bias by resource level（新图）
3. 翻译质量报告表
4. Workshop 论文草稿（参见 `v2/paper/proposal_new.md` 的 Stage 2）

## 推荐工作顺序

1. **现在（无 GPU）**：Exp3a — 混合效应模型在 exp1 数据上跑 → 核心结论是否显著
2. **小 GPU 跑**：Exp3b — 扩大 demography 采样（tigthen CI）
3. **可选 GPU 跑**：Exp3c — 扩展语言谱系
4. **并行（CPU）**：Exp3d — 翻译质量
