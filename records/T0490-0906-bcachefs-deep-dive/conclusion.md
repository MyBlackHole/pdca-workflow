---
schema: pdca.asset/v1
id: T0490-0906-bcachefs-deep-dive
phase: check
source_ids: [node-core-move-unified-relocation-engine, node-core-reflink-trigger-refcount-self-delete, node-core-observability-status-text-matrix, node-core-time-stats-cheap-instrumentation, node-core-userspace-unlock-keyring-policy, o3-diff, validate-output, convergence-map]
---

## 上下文
用户要求继续分析代码并产出优化本体。Plan 定三方向（EC数据路径/可观测/用户态工具）+ 新增至少 3 节点 + 优化分析后定。Do 三方向并行深挖得 38 条机制，清单经用户确认：照建 5 节点 + O1。O1 执行后被 validate 报双向环，已回滚；替代 O3 经确认后执行通过。

## 假设与结果
- 假设 1：三方向深挖结论真实。结果：成立，子代理 Read/Grep 核实；用户态按现树旧形态核实（本地 main 落后，mount 重构未合入）。
- 假设 2：O1 双向关联可行。结果：不成立，关系图整体无环，双向 relates_to 即环；已回滚并改 O3 单向关联。
- 假设 3：O3 单向关联无环。结果：成立，validate 全量通过。

## 分析
- **AC-1** ✅ 三方向 38 条机制，每条带文件+函数名（5 node 证据正文引用）
- **AC-2** ✅ 新增 5 个不重复 domain 节点且 frontmatter 合法（5 node 证据）
- **AC-3** ✅ O3 三处单向关联落实，diff 各 +1 行有据可查；O1 失败回滚如实记录（o3-diff）
- **AC-4** ✅ validate 全量 0 issues，信号非泛化，引用无空悬（validate-output）

关键结论：新增 core-move-unified-relocation-engine、core-reflink-trigger-refcount-self-delete、core-observability-status-text-matrix、core-time-stats-cheap-instrumentation、core-userspace-unlock-keyring-policy；O3 优化 T0489 三节点单向关联。
复核途径：validate 输出 OK；`git diff` 查 O3 三处；逐节点 Read 核对。

## 适用边界
- 用户态分析基于本地落后 main 的旧形态，v1.39.3 mount 重构合入后部分结论需复核（节点正文已注明）。
- EC 修复状态机等主题本次未建节点（规模控制），机制留存在深挖记录中。
- O1 教训：relates_to 双向即环，跨节点关联必须单向。

## 下一轮建议
- 本地 main 合入上游 mount 重构后，复核 userspace-unlock 节点并增补 degraded/提问体系节点。
- 老 core-* 节点 testable_signal 泛化是系统性问题，宜单独立项批量治理，不在本任务零散改动。

verdict: {"outcome": "confirmed", "reason": "4 AC 全绿，5新节点+O3优化，validate 0 issues", "verdict_id": "vt0490-confirmed", "at": "2026-09-06T00:00:00+08:00"}
