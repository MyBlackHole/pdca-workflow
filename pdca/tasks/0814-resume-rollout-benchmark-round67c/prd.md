# T0256 PRD：断点恢复集成、迁移与性能门禁

## 输入与边界

直接依赖 T0254 与 T0255。负责端到端集成、兼容迁移、故障矩阵和默认路径发布判定，不重新定义二者的数据格式与 durability 语义。

## 实现范围

- capability negotiation 下启用新路径，T0252 SQLite point-lookup 保留为旧 peer 兼容模式。
- 交替运行当前/候选的 100k、1M 配对基准，收集 wall、CPU、RSS、lookup、transaction、sync、I/O bytes 和重复发送。
- 覆盖 Make、CMake TLS ON/OFF、unit、TREE/data-lane 中断恢复和 style。
- 输出 migration/rollback、指标、checkpoint GC 和运行开关说明。

## 验收标准

- [ ] AC-1: 旧 peer 自动回退且不误读新 segment；新 peer 可安全重放 interrupted transfer。
- [ ] AC-2: 100k/1M 基准采用交替配对独立进程并报告中位数、离散度及环境，sync 次数按 segment 而非文件数增长。
- [ ] AC-3: 1M 恢复 wall time 相对 T0252 至少改善 50%，RSS 与 FD 有界；未达标时新路径不得默认启用。
- [ ] AC-4: 完整崩溃矩阵、构建矩阵、unit、integration、style 全部通过，错误 lookup 不得转成 miss。
- [ ] AC-5: migration/rollback、观测指标、磁盘预算和 generation/TTL 清理文档可执行，清理不会删除最近成功 generation。
- [ ] AC-6: 报告首次扫描与恢复传输耗时，并验证恢复不对 durable-completed shard执行全量 reconciliation；性能报告同时披露 fuzzy consistency 语义，不能把速度提升描述为一致性等价优化。
- [ ] AC-7: 严格 durability 报告 data/parent/receipt/final sync 分类；逐小文件 fsync 或不受控 syncfs 导致门槛失败时不得默认启用。
- [ ] AC-8: 对大文件多次尾部中断测量累计 prefix reread bytes，验证 chunk-hash checkpoint 或明确的运维上限。
- [ ] AC-9: metadata-index on/off × resume on/off 四组合完成 backup/catalog/restore/interrupt/GC 回归，并分别报告 index lookup/build、resume state 和 object dedup 成本；off 组证明无索引文件及相关 I/O。

## 声明的测试接缝

- seam: tests/tls_tree_checkpoint_resume_integration.sh -> src/backupctl.cpp
- seam: tests/tls_tree_checkpoint_resume_integration.sh -> src/tree_checkpoint.cpp
- seam: tests/tree_checkpoint_paged_benchmark.sh -> src/tree_checkpoint.cpp
