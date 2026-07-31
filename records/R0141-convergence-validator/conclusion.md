---
schema: pdca.asset/v1
id: R0141-convergence-validator
phase: check
source_ids: [test-result, pairing-result, review-report, convergence-map]
---

## 上下文

检查 T0141 是否把原本依赖 AI 手工判断的 `convergence → PRD AC → evidence`
支撑关系变成可执行 Do→Check 门禁，并且确实发现现有 evidence gate 漏掉的错误。

## 假设与结果

- PRD AC 全覆盖可以由确定性代码验证：通过。map 自身被排除，不能作为验收证据。
- 每条 Plan convergence 可以完整回链到 AC 和 evidence ID：通过。缺项、重复、越界、文本漂移、未知 AC、未知 evidence 和不支持关系均有稳定错误码。
- 验证器会改变现有错误判断：通过。同一“第二条 convergence 缺少 map item”的夹具中，旧 evidence gate 返回有效，新门禁返回 `CONVERGENCE_ITEM_MISSING`。
- 可以接入真实阶段流程而非成为孤立脚本：通过。CLI 与 Do→Check 的 `gate_issues` 复用同一核心函数，T0141 已通过新门禁进入 Check。
- 不破坏现有行为：通过。33/33 单元测试、12/12 确定性场景夹具、skill index、doctor 和 Python compile 均通过，第三方依赖增量为 0。

## 分析

13 项 AC 均由非 map 实质证据覆盖，四项登记证据的 size 和 SHA-256 均匹配。配对实验满足项目的最低价值门槛：新增规则不只是检查字段存在，而是拒绝了旧 gate 接受的无支撑收敛结论。

双轴代码审查 Blocking 为 0。规范轴初审发现错误 kind、schema 非法和普通悬空 evidence ID 三个测试缺口，已在进入 Check 前补齐。

## 适用边界

- 验证器证明引用链结构成立，不判断证据内容在语义上是否充分；后者仍由 Check 审查。
- PRD 必须使用精确 `## 验收标准` 标题和规范 Markdown checkbox，不兼容其他旧格式。
- 新门禁作用于未来 Do→Check 转换，不追溯重放已完成的历史阶段。
- Do 收尾多一个小型 map 产物；其成本由稳定错误定位和防止无依据结论的收益抵偿。

## 下一轮建议

确认后将“结构证据门禁必须排除控制产物自证”沉淀到现有 AI 友好度方法论。不要立即增加更多映射类型；先让后续真实任务消费该门禁，再决定是否需要自动生成辅助。
