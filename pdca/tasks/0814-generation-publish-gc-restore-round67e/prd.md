# T0258 PRD：generation 发布、retention 与 GC

## 输入与边界

依赖 T0255 durable receipt 和 T0257 immutable store。负责 generation root/current-ref、writer lease和 retention/GC；不负责 catalog API 或 restore 物化。

## 实现范围

- objects/manifests/final receipt/current-ref 的严格发布顺序和 expected-previous CAS。
- retained refs、pins、active-transfer leases 与 mark-epoch GC journal。
- legacy in-place mirror 与 repository namespace/capability 完全隔离。

## 验收标准

- [ ] AC-1: object 后、manifest 后、final receipt 后、current-ref temp/rename/dir-sync 各崩溃点只暴露完整旧 generation 或完整新 generation。
- [ ] AC-2: single-writer lease、过期 lease takeover 和 expected-previous CAS 防止并发任务丢失 ref 更新。
- [ ] AC-3: GC 只删除不被 retained refs、pins 或 active leases 引用且早于 mark epoch 的对象；GC 并发和崩溃不损坏可恢复/已发布 generation。
- [ ] AC-4: fuzzy consistency 标签、scan/resume 时间窗和未复核计数写入 immutable root manifest，并可由下游 catalog 读取。

## 声明的测试接缝

- seam: tests/tls_tree_checkpoint_resume_integration.sh -> src/backupctl.cpp
- seam: tests/tls_tree_checkpoint_resume_integration.sh -> src/tree_checkpoint.cpp
