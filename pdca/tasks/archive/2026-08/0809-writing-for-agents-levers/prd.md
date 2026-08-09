# PRD — 审查+增强 writing-great-skills（writing-for-agents 4 杠杆）

## 背景

对照 mattpocock writing-for-agents 全文，本地 skills/writing-great-skills/
SKILL.md（60 行）已覆盖核心方法论但缺失 4 个杠杆：锚定词（L1）、指针措辞
（L2）、双负载成本模型（L3）、no-op 模型相对测试（L4）。本任务审查并增补
这 4 个杠杆，提升所有未来技能/文档的 AI 可消费性。

## 需求

### R1 锚定词章节（L1）
`skills/writing-great-skills/SKILL.md` 新增"锚定词（leading words）"章节：
- 定义：预训练已有词，重复以 token 而非句子，锚定一类行为
- 例：_tight_（快速/确定性/低开销紧凑循环）、_red_（红灯=可证伪反馈环）
- 判定：自造词不招募先验，需定义 token 偿还；优先用已有词
- 反例：三词短语描述一概念 → 收拢为单 token

### R2 指针措辞章节（L2）
新增"指针措辞"：
- 上下文指针的**措辞**（非目标）决定触发可靠性；弱措辞=方差 bug
- 一分支一触发词；同义改写=一分支写两遍，收拢
- 指针首词前置（pointer 靠首词做触发工作）；常载指针每轮花费更贵需更狠修剪
- 与上下文指针引用信息层级的关联

### R3 双负载成本模型（L3）
新增"双负载"：
- context load：常载材料每轮 token 成本；pointer 本身也计 load
- cognitive load：人工索引成本，非最小化对象——花在人工判断处
- 渐进披露是保护信息层级的手段，非纯 token 优化
- 判定：inline 每分支都需的，推 pointer 只有某些分支达的

### R4 no-op 模型相对测试（L4）
增强"无操作不写"为模型相对判定：
- 测试："是否改变默认行为"模型相对的；两人分歧靠运行文档解决，非辩论
- 太弱的词是 no-op（_be thorough_），换更强词（_relentless_）
- 失败时删整句而非删词

### R5 测试
契约测试守护 L1-L4 落地点（机器可读断言）：
- 断言 SKILL.md 含：`锚定词`/`leading words`、`指针措辞`、`双负载`/
  `context load`、`模型相对`
- 现有测试全量回归通过

## 验收标准

- [ ] AC-1: SKILL.md 含锚定词章节（L1）
- [ ] AC-2: SKILL.md 含指针措辞章节（L2）
- [ ] AC-3: SKILL.md 含双负载章节（L3）
- [ ] AC-4: SKILL.md 含 no-op 模型相对判定（L4）
- [ ] AC-5: 契约测试守护 L1-L4（R5）
- [ ] AC-6: 全量测试通过，内容预算豁免记录在案

## 收敛条件

- [ ] CC-1: 上述 AC 全部满足
- [ ] CC-2: 内容预算豁免按 ADR-0007 记录（necessity + 契约守护）
- [ ] CC-3: 增补不破坏现有章节（信息层级/极简/拆分/失败模式仍在）

### 声明的测试接缝

- seam: tests/test_writing_for_agents_levers.py -> skills/writing-great-skills/SKILL.md
