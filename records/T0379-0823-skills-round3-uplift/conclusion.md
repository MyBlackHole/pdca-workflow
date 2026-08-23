---
schema: pdca.asset/v1
id: T0379-0823-skills-round3-uplift
phase: check
source_ids: [grilling-after, agents-after, audit-findings, baseline-after, convergence-map]
---

## 上下文

skills 三轮借鉴：grilling 非阻塞并行细化、git 防护纪律、以写作杠杆反哺存量资产体检。

## 假设与结果

| 假设 | 结果 |
|------|------|
| H1 grilling 存在真实差距 | 成立：规则 4 缺非阻塞细节，已补 |
| H2 机器启发式可检出真实冗余 | **被推翻**：5 条粗筛全误报；人工深挖另获 2 条真实（R1/R2 已示范清理） |

## 分析

- **AC-1** ✅ grilling 规则 4 补 Non-blocking：探索进行中仅下游问题等待，其余 frontier 照常问（grilling-after）。
- **AC-2** ✅ AGENTS.md git 防护条目：五类破坏性命令禁用+被拒即停先读 receipt（agents-after）。
- **AC-3** ✅ 45 资产全覆盖体检清单：5 条粗筛逐条人工定性全误报，2 条人工补充发现含处置（audit-findings）。
- **AC-4** ✅ 抽样清理 2 处（flow-do A2 去重、grilling SSOT 收拢）；baseline 更新，audit 零 issue。

## 适用边界

- 体检启发式仅覆盖弱词/禁令/重复句三类模式，语义级 no-op（如过时流程描述）仍需人工审读。
- 真实冗余率约 4% 的结论基于本轮快照。

## 失败原因

不适用。

## 下一轮建议

1. 卡点 B 类四批推进仍为最大待办（T0377 清单）。
2. G2 的 git 防护若平台支持 hook 可后续评估自动化。
