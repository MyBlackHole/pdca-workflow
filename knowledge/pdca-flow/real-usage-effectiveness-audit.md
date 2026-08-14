---
schema: pdca.asset/v1
id: knowledge.pdca-flow.real-usage-effectiveness-audit
summary: 用独立真实参照集验证记录机制的发现价值，并将夹具正确性、运行数据可用性和治理转化分层判定
tags: [pdca, ai-efficiency, evidence, effectiveness, flow-issues]
scenarios: [research, review]
phases: [plan, do, check]
source_ids: [T0260-0814-self-improvement-effectiveness-audit]
---

# 用真实使用记录审计自我提升机制

## 核心方法

审计记录机制时，先从被测记录源之外建立真实问题参照集，再检查记录是否捕获。可使用真实任务的 clarifications、回退/重试、partial/rejected 结论、journal、doctor 和可复查失败证据。不能用 occurrence 自己证明 occurrence 有发现价值。

发现能力至少分四轴评价：

1. **覆盖**：独立问题是否被捕获；同时报告漏报。
2. **信噪**：区分同一 attempt 的原子失败、重复 burst 和跨任务系统问题。
3. **可行动性**：记录能否定位任务、原因、影响和可验证指标。
4. **转化及时性**：事实是否及时进入投影、治理 decision、candidate、实施和效果验证。

目的性参照集可以证明“存在明确缺口”，但其命中比例不能外推为全体统计召回率。

## 三层证据必须分开

- **实现正确性**：schema、单测和 fixture 证明隔离合约可执行。
- **运行数据可用性**：真实 occurrence 必须满足路径/身份不变量，完整投影可重建且足够新鲜。
- **效果闭环**：必须有真实 decision、candidate、Improvement Task、后周期 observation 和 effectiveness verdict。

任何一层通过都不能替代下一层。尤其是 fixture 全绿与真实 backlog 可重建可以同时一真一假。

## AI 效率证据边界

优先记录任务一次成功/返工、用户交互轮次、门禁失败及恢复。token、耗时和工具调用只有在真实 runner 产出绑定 task identity 的结构化遥测时才可使用；缺失时写 `unknown`，不能用 UTF-8 bytes、文件 mtime 或 fixture 模型冒充。

候选至少满足：同类损失出现在两个独立真实任务，或单次严重阻断具有明确因果链；同时记录任务自身缺陷、旧数据、人工违规和重复上报等替代解释。

## T0260 已验证实例

T0260 审计发现 199 个 occurrence，但正式 backlog 只覆盖 34 个；全量隔离重建因 event path 与 payload record_id 不一致而失败。记录机制曾通过 T0164→T0166 产生一次真实行动价值，因此不是完全无效；但其发现能力与完整闭环只能判定 partial。

这一实例还表明：原始不可变事实应保留；降低 burst 噪声应发生在 attempt/resolution 派生层，而不是删除事件。
