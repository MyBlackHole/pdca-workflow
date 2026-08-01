---
schema: pdca.asset/v1
id: T0181-0802-physical-pointer-derived-state-contract
phase: check
source_ids: [evt-001, evt-002]
---

## 上下文

T0180 确认 range/physical pointer 引入前必须补齐 alloc/backpointer 派生链。本任务在
不改产品代码的前提下，先固定单一格式的主从数据与恢复边界，避免 T0182 直接引入没有
恢复契约的 transaction runner。

## 假设与结果

| 假设 | 结果 | 证据 |
| --- | --- | --- |
| extent 与内部 btree pointer 可作为同一类主 physical pointer 来源 | 成立；上游三类 key 都绑定 extent trigger | evt-001 |
| alloc/backpointer 可被视为主 pointer 的派生状态 | 成立；上游 pointer trigger 在同事务更新它们，并具备反向校验路径 | evt-001 |
| `norun` replay 可自动维护派生状态 | 不成立；必须在主键 replay 后显式扫描/重建，完成前不得发布派生查询 | evt-001 |
| 现有恢复/split 接缝可承接后续验证 | 成立；定向与全量测试均通过 | evt-002 |

## 分析

合约将有效 physical pointer 定义为唯一权威：extent、`btree_ptr` 或 `btree_ptr_v2` 中的
有效 device/bucket pointer，拥有 btree、level、position 和 pointer identity。alloc 是每
device/bucket 的派生使用状态，backpointer 是 bucket 到 owner 的反向记录，accounting 是
从主 pointer 重算的派生汇总。`mem_ptr` 不属于物理所有权证据。

恢复顺序固定为：恢复主 pointer → 派生状态不可发布 → 扫描主 pointer 重建 alloc、
backpointer/accounting → 校验集合等价 → 发布。这样覆盖主键 durable 而派生状态未可见的
崩溃窗口，且不依赖 `BTREE_TRIGGER_norun` 的隐式副作用。

## 失败原因

不适用：设计验收已满足，未发生产品实现失败。GC、stripe、LRU/free-index 与完整
alloc-v4 运营字段被明确排除，而非简化进本合约。

## 适用边界

本结论仅适用于将来引入真实 physical pointer 的 subvol 单一格式；不改变现有 cookie
引擎语义，不采用 bcachefs fs 层 btree-id 编号，也不授权直接实现完整 GC。

## 下一轮建议

确认后推进 T0182：按本合约接入 transaction runner、sort-order/multi-round 与
extent/btree-pointer dispatch，并追踪 split pointer 的实际持久化入口。T0183 仍等待
T0182 完成后再实现派生 writer/rebuild/validator。
