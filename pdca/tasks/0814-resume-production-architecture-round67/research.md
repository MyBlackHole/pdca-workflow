# T0253 Research Review：商业生产语义与设计缺口

## 结论

公开资料无法证明商业软件内部使用某一种具体数据库或目录游标实现，但可以确认三类生产语义：

1. Veeam 对大文件维护 sync file 和 offset；默认按约 5 分钟 flush，文档明确警告过于频繁 flush 会降低性能。APFS 场景从 snapshot 继续，snapshot 不可用时退化为重新比较文件修改时间。[官方文档](https://helpcenter.veeam.com/docs/agentformac/userguide/backup_job_resume.html)
2. Commvault 公开支持 CIFS/NFS restartable backup、从 point of interruption 恢复、多节点/多线程扫描、增量 forever 和 NAS snapshot。[官方白皮书](https://documentation.commvault.com/2024e/expert/files/pdf/NAS_Solutions_A_Commvault_Engineering_White_Paper.pdf)
3. AWS DataSync Enhanced mode 在发现对象时持续准备并行传输，官方称每次执行可处理 virtually unlimited objects；对于 billions of files，建议按目录、manifest 或 filter 分片。中断后重新启动同一 task 可以完成一致的目标内容，而不是向用户承诺裸目录 offset 永久有效。[官方文档](https://docs.aws.amazon.com/datasync/latest/userguide/how-datasync-transfer-works.html)、[大数据集分片](https://docs.aws.amazon.com/datasync/latest/userguide/create-task-how-to.html)、[中断恢复](https://docs.aws.amazon.com/datasync/latest/apireference/API_CancelTaskExecution.html)

## 设计审查发现

### P0-1：source generation 仍然是抽象名词（已按无 snapshot 约束改写）

本项目没有源端 snapshot/immutable view，因此不能证明目录和文件来自同一时刻，也不能形成 point-in-time backup。`tree_run_id` 只能标识一次 live-tree 扫描；每目录 epoch 和文件前后 identity 校验只能发现部分并发变化。

本轮采用以下语义：

- live-tree fuzzy 模式：进程存活期间允许局部重扫；崩溃恢复信任 durable receipt，不复核停机期间变化。文档不宣称 point-in-time 或恢复时当前树一致性，持续变化条目返回 failure。

### P0-2：remote ACK 与 durable commit 尚未闭合

当前 `FT_TREE_CHECKPOINT_ACK` 在接收端应用目录项后返回；默认路径没有在 ACK 前完成远端文件、目录和 receipt 的 durable sync。并且当前接收端直接写目标 tree，generation 文件只在 TREE_END 时轮换，不能把中间目标目录当成原子 staging snapshot。

生产协议需要显式拆成：

`APPLY_SEGMENT(idempotency_key) -> DURABLE_RECEIPT -> CURSOR_COMMIT -> FINAL_MANIFEST_CAS`

若目标是 POSIX 文件系统且要求 versioned backup，需要独立 immutable generation directory、durable manifest 和原子 current-ref；不能假设普通 rename 可以替换非空目录。若目标是对象存储，需要 immutable objects、manifest object 和 conditional pointer update。

### P0-3：manifest 生成会成为第二个全量瓶颈

先完整生成 manifest，再开始传输会增加一次完整扫描、磁盘写入和空间占用；manifest 生成自身中断也需要恢复。

应采用有限 segment pipeline：枚举器顺序生成并 durable seal 一个 segment，传输器消费已 seal 的 segment，cursor 只指向已 seal segment 内的 batch；最多保留固定数量的 ready/in-flight segment。不能一次生成全量 manifest，也不能让未 seal segment 被恢复逻辑引用。

## P1 缺口

- 当前接收端在每个 `FT_TREE_CHECKPOINT` ACK 前调用 `apply_dir_metadata_agent`，该函数从临时 spool 的末尾重放全部已见目录，而不是只消费本 checkpoint 新增的目录；目录很多时会形成近似 O(directory_count * checkpoint_count) 的重复工作。新协议必须让目录元数据成为 segment record，或维护 durable `dir_meta_offset`，每次只应用增量。
- 无 snapshot 的 live-tree 必须有终止策略：`max_rescan_passes`、`unstable_timeout` 或显式 `INCOMPLETE/UNSTABLE` 结果。仅写“最终验证”会在持续变化目录上无限重扫，或被迫静默成功。
- partial 元数据目前只由路径和非加密 stat/FNV 指纹保护；必须绑定 `transfer_id/tree_run_id` 和远端目标 generation，避免旧任务 partial 在 inode/时间戳复用时被错误接管。
- segment identity 必须包含 `tree_run_id`、目录 epoch、canonical ordering version、segment digest、first/last key 和 record count；cursor 不能只保存路径和 offset。
- 并行传输必须使用确定性 shard 和每 shard cursor，不能用一个全局有序 cursor 覆盖 out-of-order ACK。
- manifest 必须表达删除项、空目录、符号链接、硬链接、xattr/ACL 以及目录元数据，否则只确认“出现过的文件”，不能保证目标快照收敛。
- hardlink first-path 映射、目录元数据 spool 和 segment receipt 必须进入同一恢复模型；当前临时 `/tmp` spool 不能承担断电恢复职责。
- segment 重做窗口必须同时以字节、条目、时间和磁盘空间约束；只写 `uint64_t` counter 不等于可物化 `UINT64_MAX` 行。
- segment compaction、过期 checkpoint 清理、孤儿 staging 和重复 pack 必须有 GC/保留策略。

## 推荐架构（无 source snapshot 约束）

本项目明确没有 source snapshot，因此只采用其中的 restartable work unit 语义，不宣称 point-in-time snapshot：

1. live source 产生 `tree_run_id`，每个目录 segment 记录扫描前后 epoch。
2. 以目录分片或 manifest segment 作为 work unit，而不是裸目录 offset。
3. segment seal 后计算 digest，远端用 idempotency key durable apply。
4. 每 shard 独立保存 durable cursor，故障后只重做最近未提交 work unit。
5. 大文件内部使用 sync file/partial offset；小文件装入 segment/pack。
6. 所有 segment 完成后以 manifest CAS 发布新 generation。
7. 存活期间目录变化只触发受影响 segment 重扫；崩溃后不复核 durable-completed set，停机期间变化由下一次备份收敛。

## 第二轮审查结论

当前方案仍不可进入 Do，存在两个根本语义缺口和六个协议/持久化缺口：

1. 无 snapshot/change journal 时，停机期间变化不可观测。用户明确接受该限制，因此采用 fuzzy generation：不做发布前全量 reconciliation，但必须永久记录一致性标签和未复核范围，不能宣称恢复时当前树一致性。
2. segmented ledger 不等于 versioned backup store。in-place tree 会在中断时暴露混合状态并覆盖上一版本；若要求上一成功 generation 可恢复，必须引入 immutable generation namespace/current-ref 或内容寻址存储。
3. segment file、checkpoint directory 与 work-queue journal 的跨文件 commit 顺序未定义，`fdatasync(segment)` 单独不足以保证 rename 后目录项掉电存活。
4. receipt 幂等键未绑定 digest/range/durability；同 key 不同 payload 以及乱序 ACK 可能错误推进单值 cursor。
5. deletion sweep 缺少 per-directory complete coverage proof，扫描错误或 exclude 变化可能被误判为删除。
6. hardlink anchor 跨 shard 依赖、父目录 metadata 应用顺序及 anchor 失败降级未闭合。
7. 严格 durability 若仍逐小文件 `fsync`，segment 化不会解决主要性能瓶颈；`syncfs` 也可能造成不可控系统级抖动。
8. 大文件 partial 恢复会从 0 重算 SHA-256 prefix，多次尾部中断产生近似二次读取成本，需要 chunk hash checkpoint 或明确上限。
