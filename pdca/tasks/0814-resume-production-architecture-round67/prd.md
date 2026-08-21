# T0253 PRD：生产级断点续传架构调研与性能重构

## 问题

T0252 将 TREE checkpoint 从全量内存 map 改成 SQLite sidecar，解决了 RSS 线性增长，但把 SQLite point lookup、journal `fsync` 和事务提交放进了海量文件备份的关键路径。用户反馈当前方案性能下降严重；现有证据没有证明在真实存储、不同文件规模和并发条件下满足生产吞吐。

## 目标

基于 rsync、restic、Borg 等生产实现的可验证做法，重新划分单文件字节续传和海量目录恢复边界，消除每文件强持久化热路径；本项目源端没有 snapshot/immutable source view，因此目标是 live-tree 下可恢复、幂等的 best-effort fuzzy backup，而不是 point-in-time 或恢复时当前树的一致性快照。

文件数量契约为 `uint64_t`：总文件数、已扫描数、已跳过数、已发送数、重做数、segment 序号和 checkpoint 总量不得因 `uint32_t` 截断；单个网络 frame、单个 batch 和内存队列仍采用独立的有界类型。`UINT64_MAX` 是计数与协议序号的上限，不承诺物理介质能够实际存储 `UINT64_MAX` 个目录项。

## 范围

- 复核并量化当前 TREE checkpoint 的每文件 lookup、batch barrier、journal `fsync`、SQLite commit、锁和 page-cache 成本。
- 设计并实现生产路径：单文件 `.partial` offset resume；目录级 sealed ledger；目标端 immutable objects/packs、分段 manifest、durable receipt 和原子 current-ref。
- 保持源文件变化检测、ACK 后确认、损坏尾部不静默跳过和安全路径约束；新默认路径采用 versioned immutable backup，可保留上一成功 generation。进程运行期间观察到的变化执行重传/局部重扫；停机期间变化明确不保证被本次 generation 观察。
- 增加可复现的吞吐、CPU、I/O 等待、fsync 次数、RSS、重复发送窗口和崩溃恢复测试。
- 提供 immutable generation 的元数据 catalog：按目录路径查询直属文件/目录，支持稳定分页和原始名字节序；提供指定 generation/路径范围的可恢复 restore。

## 用户故事

1. 作为海量文件备份操作者，我希望任务中断后从已封存的目录 segment 继续，而不是重新枚举整个 namespace。
2. 作为生产运维人员，我希望远端只有在数据和 receipt 达到声明的 durability 后才 ACK，从而避免断电后错误跳过。
3. 作为 live-tree 使用者，我希望持续变化的文件被明确报告为 unstable，而不是无限重试或静默成功。
4. 作为性能工程师，我希望 checkpoint 成本按 segment 摊销，并能观测 lookup、sync、重做和重复发送成本。
5. 作为备份管理员，我希望输入 generation 和目录路径后按稳定字节序分页浏览直属文件与目录，并能选择整代、目录或单文件恢复。

## 实现决策

- 使用磁盘上的 append-only sealed segment 和每 shard durable cursor；不持久化裸 `getdents64.d_off`。
- 枚举器维护磁盘 work queue，目录状态为 discovered/scanning/sealed/unstable/done；未封存目录崩溃后只重扫该目录。
- 远端以 `(transfer_id, shard_id, segment_id, batch_id)` 作为幂等键，durable receipt 是客户端推进 cursor 的唯一依据。
- 目录元数据、硬链接 group、删除 mark 和普通文件记录使用同一 segment/receipt 模型；不再依赖匿名 `/tmp` spool 恢复。
- live-tree 设置最大重扫轮数和持续变化超时；超过限制返回 `INCOMPLETE/UNSTABLE`。
- 新默认目标布局为 content-addressed immutable objects/packs + 分段 manifest + 原子 `refs/current`；现有直接目录覆盖仅作为 capability 协商后的 legacy mirror。
- `metadata_index` 与 `resume` 是独立配置：metadata index 默认关闭，resume 默认开启。前者只控制源端/本地派生加速索引文件，不改变 repository manifest、catalog 或 restore 内容；后者控制 checkpoint/partial/receipt/lease。
- T0252 SQLite point-lookup 路径降级为兼容模式，新路径通过 capability negotiation 启用。

## 非目标

- 不以关闭断点续传、全量重传或无限制增加内存作为优化。
- 不把当前 SQLite sidecar 的一次合成 RSS 结果当作生产性能结论。
- 不在本轮假设或引入未经验证的 `MDB_VL32` no-mmap 外部依赖。
- 不破坏既有协议兼容；如需要协议扩展，必须提供 capability negotiation 和旧端回退。

## 验收标准

- [ ] AC-1: 研究报告列出至少 rsync、restic、Borg 三种生产实现的断点/崩溃恢复机制、持久化粒度、重复工作窗口和适用边界，并以官方文档或官方源码为依据。
- [ ] AC-2: 基准能分别报告当前方案与候选方案的 wall time、CPU time、peak RSS、SQLite lookup 数、事务数、`fsync` 次数、journal/index I/O bytes 和 skipped/resent/duplicate bytes；至少覆盖 100k 与 1M 合成条目以及真实可运行规模。
- [ ] AC-3: 单文件中断恢复只依赖受指纹保护的 partial/offset 和最终校验；源文件变化、截断、错误 offset、重放和重复提交均 fail-closed 或安全重传。
- [ ] AC-4: 目录恢复不在每个文件确认时执行强同步；checkpoint 周期由明确的时间/字节/条目阈值控制，断电后重复发送窗口有上限且远端提交幂等。
- [ ] AC-5: 不允许 lookup/索引错误被转换为 miss；并发锁、旧 checkpoint 迁移、坏尾部、ACK 后进程终止、索引提交中断均有故障注入测试。
- [ ] AC-6: Make、CMake TLS ON/OFF、unit、断点集成、性能基准和 style 回归通过；性能报告明确当前方案是否回滚、替换或保留为兼容模式。
- [ ] AC-7: 输出 migration/rollback、运维开关、数据清理策略和可观测指标文档；实现提交前必须有用户终审确认。
- [ ] AC-8: 对总量计数、segment/checkpoint 序号和累计统计做 `uint64_t` 边界测试；所有达到 `UINT64_MAX` 后的递增操作必须 fail-closed，不得回绕为 0；batch/frame 数量仍必须验证在各自有界类型内。
- [ ] AC-9: 在无 source snapshot/change journal 前提下，恢复直接消费已验证 sealed segment，不全量复核已有 durable receipt。结果必须标记 `consistency=fuzzy`，记录 scan/resume 时间窗、未复核 durable entry 数和限制说明；不得宣称恢复结果等于停机后当前源树。
- [ ] AC-10: 枚举器使用持久化目录 work queue 和迭代式 FD 预算；进程在 sealed segment、未 sealed 当前目录、发现子目录后以及目录 rename/delete 时崩溃，恢复最多重扫受影响的未完成目录且不重扫 durable-completed shard。目录深度不导致递归栈或 256 KiB/层常驻内存无界增长。
- [ ] AC-11: 远端 ACK 仅在该 batch 的数据、目录依赖和幂等 receipt 达到所选 durability 后返回；receipt 必须绑定 protocol/durability、target generation、segment digest、record range/count 和 payload byte length。ACK 前、数据 sync 后 receipt 前、receipt sync 后客户端 cursor 前和最终 generation 发布前崩溃均有确定性恢复断言。
- [ ] AC-12: 目录元数据只增量应用一次，不在每个 checkpoint 重放全部历史 spool；硬链接 first-path/group、空目录、符号链接、FIFO、xattr/ACL 和删除 mark 均可跨进程恢复。
- [ ] AC-13: partial 元数据绑定 protocol version、transfer/tree run、目标 generation、路径、源 identity、期望大小和已验证 offset；旧任务、错误目标、损坏元数据和指纹冲突不得复用 partial。
- [ ] AC-14: live-tree 默认最多重扫 3 轮且有可配置 timeout；达到限制返回 `INCOMPLETE/UNSTABLE` 并列出计数，不允许无限循环或成功码。中断运行不执行删除；仅成功完成的 final mark-and-sweep 可删除目标 stale entries。
- [ ] AC-15: 新路径在 100k/1M 配对基准中，峰值 RSS 有界，1M 恢复 wall time 至少比 T0252 point-lookup 基线降低 50%，checkpoint/receipt sync 次数按 segment 数而不是文件数增长；若未达到则不得成为默认路径。
- [ ] AC-16: segment temp write、file sync、rename、checkpoint-directory sync 和 work-queue state commit 有唯一规定顺序；任一边界掉电后不得出现 `done` 指向丢失/未 sealed segment，也不得为每个子目录执行一次同步。
- [ ] AC-17: 每 shard 明确采用串行 batch，或使用 contiguous high-watermark 加 gap set 表达乱序 ACK；同一幂等键携带不同 digest 必须返回冲突，不能复用旧 receipt。
- [ ] AC-18: 删除 mark-and-sweep 只接受 `coverage=complete` 的目录；权限错误、I/O 错误、exclude 规则变化、unstable、跨文件系统策略变化或计数不一致均禁止该目录删除。
- [ ] AC-19: 新路径使用 versioned immutable generation：objects/packs 和所有分段 manifest durable 后才原子切换 `refs/current`，任一发布崩溃点都保持旧 ref 或完整新 ref；legacy in-place mirror 不得声明该保证。
- [ ] AC-20: 跨 shard hardlink 使用先提交 canonical anchor、后提交 link records 的显式依赖，anchor 失败/变化/被 exclude 时安全降级为独立文件或使 generation 失败，不得产生悬空 link。
- [ ] AC-21: 大文件多次恢复不得每次从 0 重算全部已确认 prefix；使用版本化 chunk-hash checkpoint，或在基准中证明重算成本受明确上限约束并把限制暴露给运维。
- [ ] AC-22: durability 成本单独测量数据文件、父目录、receipt 和 final publication 的 sync 次数；严格模式不能通过对每个小文件逐一 `fsync` 实现 segment group commit，必须使用 pack/staging 或明确判定性能门禁失败。
- [ ] AC-23: manifest 采用有界内存的分段/Merkle root，不一次载入全部路径；regular file、chunk、small-file pack、sparse extent、hardlink 和 metadata 均有稳定对象引用，读取时校验 cryptographic content id。
- [ ] AC-24: GC 只删除未被任何 retained manifest 或 active-transfer lease 引用的对象；对象 durable receipt 后、manifest 发布前、ref 切换前后和 GC 并发崩溃均不得丢失可恢复或已发布数据。
- [ ] AC-25: restore 能从指定 generation 流式重建普通文件、目录、hardlink、symlink、FIFO、sparse、xattr/ACL，并验证 object/pack/manifest digest；损坏对象使恢复 fail-closed。
- [ ] AC-26: catalog 支持 `generation + directory_path + page_size + cursor` 查询直属子项；排序 key 是单个 child name 的原始字节按 unsigned lexicographic 比较，公共前缀相同时较短者在前，不按类型分组且不依赖 locale/UTF-8。
- [ ] AC-27: 首次查询把 `current` 解析为 immutable generation；后续 opaque authenticated cursor 绑定 repository、generation/root digest、directory node digest、order version、last-key、page limits 和 lease。跨目录/代复用、篡改、过期或 GC 后 token 必须明确失败，不得静默从头分页。
- [ ] AC-28: page size 和 response bytes 双重有界；响应包含 raw `name_bytes`、可选 escaped display name、type、size、allocated bytes、mode、uid/gid、mtime/ctime、link/metadata 摘要、`has_more` 和 `next_cursor`，非法 UTF-8 文件名可无损往返。
- [ ] AC-29: restore 支持 whole generation、directory subtree 和 single path，明确 overwrite/skip/fail/rename policy、目标路径 confinement、空间预检、断点 checkpoint、逐对象 digest 验证和 per-file atomic rename；中断后不得破坏已存在目标外的路径。
- [ ] AC-30: catalog point stat、generation list 和 directory pagination 不扫描 object payload 或全量 manifest；1M 同目录随机页/顺序全遍历具有有界 RSS，且无重复、遗漏或顺序漂移。
- [ ] AC-31: catalog 与 restore 在解析 cursor/object 前执行 repository、generation 和 path-scope 授权，并具备主体级 page/byte/lease/并发限额与审计；错误响应不泄露未授权路径是否存在。
- [ ] AC-32: selective restore 遇到 hardlink anchor 不在 selector 内时，以同一 file object 物化独立 regular file；不得创建越出 selector/destination 的 link，完整 group restore 才重建 hardlink 关系。
- [ ] AC-33: `metadata_index=on|off` 与 `resume=on|off` 可独立配置并覆盖四种组合；metadata index 默认 off、resume 默认 on。metadata index 是可重建本地优化，不进入 wire receipt 或 generation identity；resume policy 必须绑定 transfer/receipt。
- [ ] AC-34: `metadata_index=off` 时不得创建、打开、读取或更新 SQLite DB、`-journal/-wal/-shm`、LMDB data/lock、metadata builder temp 或其他文件元数据派生索引；配置 cache path 原先不存在时运行后仍不存在，已有旧索引保持未访问且不被修改。`resume=on` 的 work queue/segment/cursor 不属于该禁令。
- [ ] AC-35: `resume=off` 时不创建/读取 work-queue cursor、partial metadata、batch receipt 或 resume lease；中断 run 标记 abandoned，重启以新 transfer 全量枚举。已存在 immutable content object 可按 digest 去重，但不得计入 resumed entries/bytes。
- [ ] AC-36: `metadata_index_enabled/backend/path/lookup_count/index_bytes` 与 `resume_enabled/resumed_entries/resumed_bytes/dedup_bytes` 分开记录；metadata index off 时 lookup/index bytes 为 0，object dedup 不能计为 resume。旧 peer 不支持显式 resume on 时必须回退或拒绝，不能静默改变配置。
- [ ] AC-37: metadata index on/off 不改变 manifest 字段、catalog 分页结果、generation digest 语义或 restore 结果；关闭索引后 catalog 直接流式读取 segmented manifest，仍满足 1M 目录分页的有界 RSS 与顺序要求。

## 测试接缝

### 声明的测试接缝

- seam: tests/tls_tree_checkpoint_resume_integration.sh -> src/backupctl.cpp
- seam: tests/tls_tree_checkpoint_resume_integration.sh -> src/tree_checkpoint.cpp
- seam: tests/tree_checkpoint_paged_benchmark.sh -> src/tree_checkpoint.cpp
- seam: tests/unit.cpp -> src/tree_checkpoint.cpp

## 方案方向

采用用户确认的 versioned immutable backup：保留 regular-file partial resume；TREE 使用批量确认日志/不可变 segment，目标以 content-addressed objects/packs 去重，路径和元数据进入分段 manifest，最后原子切换 current-ref。live-tree 使用 fuzzy 语义：进程存活期间按目录 epoch 局部重扫；崩溃恢复信任 durable receipt，不复核停机期间变化，由下一次独立备份收敛。现有 in-place tree 与 T0252 仅作为旧 peer 兼容路径。

## 关键取舍

- 性能优先但不牺牲正确性：允许有限重复发送，不允许静默漏发或错误跳过。
- 以批量 I/O 和不可变提交换取吞吐，接受断电后重做一个有界 checkpoint 窗口。
- 保留兼容读取和显式 feature gate，不能用回滚路径冒充验收通过。
