---
schema: pdca.asset/v1
id: T0186-0802-recovery-fault-matrix-public-validator
phase: check
source_ids: [source-audit, verification, convergence-map]
---

## 上下文

T0186 将 T0185 的派生状态校验从内部 recovery helper 提升为公开只读 API，并增加 recovery
阶段 fault matrix。

## 结果

- AC-1：本地 recovery/backpointer explicit pass 已审计并记录。
- AC-2：公开 validator 与结构化 mismatch 已实现。
- AC-3：journal replay 后、derived rebuild 阶段、publication 前三个 fault point 均会返回错误。
- AC-4：fault matrix 与无 fault baseline 测试通过。
- AC-5：185 个单测、10 个属性测试及 fmt/convergence gate 通过。

## 适用边界

fault point 复用现有 recovery 控制流，不代表完整 allocator、GC、LRU、stripe/EC 或 VFS 行为。
