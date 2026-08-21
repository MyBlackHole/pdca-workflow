# T0254 PRD：可恢复目录枚举与 sealed segment

## 输入与边界

继承 T0253 的 live-tree 语义，不假设 source snapshot。仅负责源端枚举、checkpoint 文件格式和本地恢复；不定义远端 ACK durability。

## 实现范围

- 持久化目录 work queue：`discovered/scanning/sealed/unstable/done`。
- 使用有界 FD、内存和 in-flight segment 的迭代枚举；超大目录使用 checkpoint 目录内的外部排序 run。
- segment header/footer 记录版本、run/shard/segment、目录 epoch、record range、长度和 digest；未 seal 数据不可推进 cursor。
- SQLite/LMDB 只做可重建批量索引，禁止每文件 point lookup 热路径。
- 默认最多三轮局部重扫，并受 timeout、unstable cap 和磁盘 reserve 限制。

## 验收标准

- [ ] AC-1: sealed、未 sealed、发现子目录后、rename/delete 四类崩溃点恢复时，最多重扫受影响的未完成目录；durable-completed shard 不重扫并可立即续传。
- [ ] AC-2: 深目录和超大单目录测试证明 FD、RSS、open segment 和临时磁盘受配置上限约束。
- [ ] AC-3: segment 坏 header/footer、截断、digest 错误、版本不兼容和派生索引损坏均 fail-closed 或从权威 segment 重建。
- [ ] AC-4: 总计数、segment id 和 record offset 使用 checked `uint64_t`，达到 `UINT64_MAX` 时返回错误且不回绕。
- [ ] AC-5: 持续变化达到三轮或 timeout 后返回 `INCOMPLETE/UNSTABLE`，不得无限扫描或静默成功。
- [ ] AC-6: seal 按 temp sync、rename、checkpoint-dir sync、queue-reference commit 的顺序完成，任一掉电点不会留下引用丢失 segment 的 `done` 状态。
- [ ] AC-7: 无 change journal 的崩溃恢复不复核 pre-crash durable-completed entries；manifest/result 标记 `consistency=fuzzy`、resume 时间窗、未复核计数和 `downtime_changes_unobserved=true`。
- [ ] AC-8: 每目录输出带 exclude/policy digest 和 error state 的 coverage record，只有 complete coverage 可参与删除判定。
- [ ] AC-9: `resume=off` 不创建或读取 work queue/cursor/segment receipt，崩溃后新 transfer 全量枚举；`resume=on` 才执行本任务恢复状态机。

## 声明的测试接缝

- seam: tests/tls_tree_checkpoint_resume_integration.sh -> src/backupctl.cpp
- seam: tests/tree_checkpoint_paged_benchmark.sh -> src/tree_checkpoint.cpp
- seam: tests/unit.cpp -> src/tree_checkpoint.cpp
