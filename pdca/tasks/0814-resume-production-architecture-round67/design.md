# T0253 Design：Resume Paths and Commit Granularity

## 1. Final boundary

断点续传分为两个不同问题，不能共享同一个热路径状态机：

1. 单个大文件中断：接收端保留受源指纹保护的 partial 文件和连续 offset；重连后只校验 prefix/size，发送端从 offset 继续，结束时做全文件 digest 和原子发布。
2. 海量目录任务中断：使用持久化目录 work queue、sealed segment 和每 shard cursor；仅未封存或检测到变化的目录重扫，不要求每个文件完成时执行本地强持久化。

## 2. Selected architecture: segmented ledger

- 枚举器使用磁盘 work queue，目录状态为 discovered/scanning/sealed/unstable/done。
- 每个 shard 仅保留有界数量的 open directories、ready segments 和 in-flight batches。
- segment 达到字节/条目/时间阈值后 seal，写入 footer digest 并 `fdatasync`；未 seal 文件永不进入 cursor。
- 远端对 `(transfer_id, shard_id, segment_id, batch_id)` 幂等 apply，并持久化 receipt。
- SQLite/LMDB 只允许批量构建派生索引，不参与每文件热路径；索引损坏可由 sealed segments 重建。
- 默认每 shard 串行提交，重启从 contiguous durable cursor 继续并最多重做一个 batch；未来若允许 shard 内乱序，必须增加 gap set。

## 3. Selected target store: content-addressed generations

- 文件切分为稳定 content-defined 或固定大小 chunks。
- 远端只接受 content id 未存在的 immutable blob/pack，重复上传由服务端或客户端索引消除。
- 任务完成时提交目标端 manifest generation；未被 manifest 引用的 pack 可回收。这里的 generation 不是源端 snapshot。
- 恢复时重新扫描目录并复用已上传 chunks，不依赖本地文件级 confirmed map。

这是用户确认的新默认 backup 模型，不再是后续备选。目标仓库布局为 `objects/`、`packs/`、`manifests/`、`refs/`、`receipts/` 和 `leases/`；legacy in-place tree 保持独立 capability，不能读取或修改 repository generation。

## 4. Compatibility path: per-file SQLite

保留 T0252 作为兼容/低速模式，不作为默认生产路径。必须加 feature gate，并明确其每文件 point lookup、每 checkpoint journal fsync 和 SQLite commit 的成本。

## 5. Rollout decision

实现 segmented ledger + content-addressed generation store 并通过新 capability 协商；T0252/in-place mirror 保持兼容但不默认启用。只有故障矩阵、restore 和 GC 测试全部通过，且 1M 配对基准恢复时间至少改善 50% 后，新仓库路径才成为默认 backup 模式。

## 6. Measurements

每个候选都测量：

- 100k/1M entries 的 wall time、user/system CPU、peak RSS。
- SQLite lookup/step、transaction、commit、journal fsync 和 directory fsync 次数。
- journal/index/segment bytes、网络 bytes、skipped、resent 和 duplicate bytes。
- tmpfs、SSD 和网络文件系统至少各一组；每组至少三次取中位数。
- 在 ACK 前、ACK 后 journal fsync 前、索引提交中、进程重启四个故障点注入终止。

## 7. Safety invariants

- 任何 source fingerprint 变化都只能导致 resend，不能导致 skip。
- lookup、segment 校验、索引恢复失败都必须 fail-closed。
- 远端 ACK 只确认幂等 batch，不等价于本地 durable checkpoint；本地 durable offset 之前允许重复发送，禁止宣称已完成。
- 正式文件只通过同目录原子 rename 发布；partial 元数据必须和路径、大小、指纹绑定。
- checkpoint 的时间/字节/条目上限必须可配置并在日志中暴露。

## 8. Cardinality contract

`uint64_t` 用于全局计数和序号：`files_scanned`、`files_sent`、`files_skipped`、`files_resent`、`duplicate_bytes`、segment id、checkpoint batch id 以及持久化总量。`uint32_t` 仅用于单帧长度、单批条目数、窗口和并发度，并在编码前检查上限。

当前 TREE checkpoint marker 的 batch count 为 `uint32_t`，并由接收端限制为 4096；这不是总文件数限制。当前 batch sequence 已为 `uint64_t`。SQLite sidecar 的物理行数仍受 SQLite/文件系统容量约束，不能声称可实际物化 `UINT64_MAX` 行；若要求跨物理 shard 的逻辑总量达到该范围，必须采用 segment/shard manifest 和 `uint64_t` aggregate counters，而不是单个 SQLite 表。

所有累计计数递增都要采用 checked add；达到 `UINT64_MAX` 时返回资源/协议错误并保留可恢复状态，禁止无符号回绕。

## 9. True enumeration resume

T0252 的“重启后从根目录重扫，再通过 path+fingerprint skip”只能称为 file-level recovery，不能满足海量文件的 enumeration resume。T0253 的生产方案必须显式持久化枚举坐标。

### 9.1 Live source observation

本项目不假设存在文件系统快照或只读 source view，因此不承诺 point-in-time 一致性。每次任务生成 `tree_run_id`；每个目录 segment 记录目录 inode、ctime/mtime、entry count hint、扫描前后目录 epoch 和 unstable 标志。发现目录在扫描期间变化时，将该目录标记为 unstable，回退到该目录 segment 起点重扫，而不是继续使用失效 offset。

目录 epoch 只能发现部分变化，不能证明全局静止；文件自身必须在读取前后做 identity 校验，发现 size/mtime/ctime/inode 变化就丢弃本次结果并重传。最终验证必须报告任务期间持续变化的条目，不能把它们标记为稳定完成。

### 9.2 Immutable manifest segments

枚举器不直接把 `getdents64` 的 `d_off` 当作跨重启游标。它把路径、类型、源 fingerprint 写入同目录的 append-only manifest segments；segment 尺寸按字节上限控制，记录使用 `uint64_t` offset。需要稳定顺序时，对目录项做磁盘外排序，按 path key 生成 immutable segment。

每个 segment 带有 `tree_run_id`、`directory_epoch`、`segment_id`、`first_key`、`last_key`、record count、byte length 和 digest。segment 生成后不再修改，传输阶段只消费 immutable 内容；source 后续变化生成新 segment，不修改旧 segment。

### 9.3 Durable cursor

本地状态保存：`transfer_id`、`tree_run_id`、`directory_epoch`、`segment_id`、`record_offset`、`segment_digest` 和远端 ACK token。提交顺序为：远端幂等应用 segment/batch -> 返回 ACK -> 本地 append cursor journal -> `fsync` -> 更新 cursor index。崩溃后从最后 durable cursor 继续；ACK 后本地 cursor 尚未落盘只会重做该 batch，不会跳过未确认记录。

### 9.4 Mutable-tree semantics

没有快照时，不承诺 `getdents64` offset 的精确续传，也不承诺全树 point-in-time 或恢复时当前视图。恢复后信任 durable receipt 并继续消费 sealed segment；已经 durable-completed 的目录/文件不因停机而复核。进程运行期间实际观察到 identity/epoch 变化时，只重扫受影响的未完成目录；停机期间变化留给下一次备份收敛。

### 9.5 Remote publish

远端应将 segment 应用到 transfer staging namespace，使用绑定 segment digest 的 identity 去重；单文件仍使用 partial + offset。全部 segment 完成后再发布 manifest/tree generation。若目标仍采用 in-place tree，则 completed marker 只能表示逻辑完成，不能提供上一 generation 回滚或整树原子可见性；只有独立 immutable generation namespace 加原子 current-ref 才能提供该保证。

### 9.6 Live-tree termination and metadata delta

live-tree 不能仅依靠“最终再扫一次”结束。必须配置最大重扫轮数、持续变化超时和 unstable 条目上限；达到上限时返回明确的 `INCOMPLETE/UNSTABLE` 结果，禁止无限重试或静默成功。

目录元数据必须随 segment 增量提交。接收端不能在每个 checkpoint 重新遍历整个目录 metadata spool；应保存 `dir_meta_offset`，每次只应用当前 batch 新增记录，或直接将目录元数据作为幂等 segment record 处理。目录 metadata spool 本身不承担断电恢复职责。

partial 元数据必须绑定 `transfer_id`、`tree_run_id`、目标 generation、源路径和源 identity；旧任务的 partial 即使 stat 指纹碰撞也不能被新任务继续使用。

## 10. Enumerator state machine

目录 work queue 持久化 `directory_id`、path、parent id、dev/ino、epoch-before、epoch-after、state、shard 和 latest segment。枚举采用迭代式调度，不以递归调用栈持有每层 256 KiB buffer；open FD 数受全局预算限制。目录开始扫描先写 `scanning`，发现子目录先 durable append `discovered`，segment seal 后再把父目录推进为 `sealed/done`。

恢复规则：`done` 和 durable receipt 不重扫；`sealed` 从 segment 消费；`scanning` 只重扫该目录；恢复后实际访问时发现路径消失或 dev/ino 改变，则标记 unstable 并重新排队受影响目录。`d_off` 仅用于单进程内减少重复 syscall，永不写入 durable cursor。

## 11. Segment format and ordering

segment header 包含 format/version、transfer/tree run、shard、segment、canonical-order version 和目录 epoch。record 使用长度、类型、record id、payload 和 checksum；footer 包含 record count、byte length、first/last key 和整个 segment digest。只有 footer 完整且 digest 正确的 segment 才是 sealed。

一个超大目录采用固定内存的 run files 做外部排序；普通目录可直接生成单个有序 run。排序临时文件与 segment 位于 checkpoint 专用目录，不使用匿名 `/tmp`。崩溃时未 seal run 可删除并仅重扫该目录。

## 12. Remote durability and publication

严格断电恢复模式采用 group commit：写入 partial/临时条目，完成本 batch 后同步受影响文件与父目录或执行受控 `syncfs`，再 append+sync receipt，最后 ACK。吞吐模式可以降低 durability，但其 receipt 不得被严格模式恢复接受。

远端直接维护版本化 run 状态和 completed-generation marker，不承诺用普通 rename 原子替换非空目录。中断运行只增加或更新安全条目，不删除旧条目；全部 shards 完成、unstable 策略通过后写 final generation receipt。删除使用 mark-and-sweep，仅针对上一成功 generation 中存在但本次成功 generation 未见的路径，并且在 final receipt 之后执行可恢复 sweep。

## 13. Recoverable metadata dependencies

目录 metadata、硬链接 group、空目录、symlink、FIFO、xattr/ACL 和 deletion mark 都是 segment record。硬链接使用稳定 group id `(dev, ino, tree_run_id)`；first-path 是派生状态，可从 segment 重建，不能只存在内存或临时 SQLite。目录 metadata 按 child-before-parent 的 dependency 顺序应用，并通过 receipt 记录已应用 record range，禁止每个 checkpoint 重放全部历史。

## 14. Partial isolation

partial metadata 使用版本化、带 checksum 的记录，绑定 transfer id、tree run id、目标 generation、canonical remote path、源 dev/ino/size/mtime/ctime、期望总长和 verified offset。恢复时逐字段校验；任何不匹配都丢弃 partial 并安全重传。最终 digest 成功且正式文件/父目录达到声明 durability 后才生成 batch receipt。

## 15. Bounded liveness and GC

默认 `max_rescan_passes=3`，同时受 timeout 和 unstable entry cap 限制。达到任一上限返回 `INCOMPLETE/UNSTABLE`。checkpoint 空间由 max ready segments、max in-flight bytes 和 free-space reserve 背压；过期 transfer、未 seal run、孤儿 staging、receipt 和旧兼容 sidecar 按 generation/TTL 清理，清理动作本身记录日志且不得删除最近一次成功 generation。

## 16. Second-review blockers

### 16.1 Crash-consistent local commit

segment seal 是跨文件事务：写 temp、`fdatasync(temp)`、rename 为 sealed 名、`fsync(checkpoint_dir)`，最后在 work-queue journal 中提交引用并同步。恢复只能接受 footer/digest 完整且目录项 durable 的 segment。child discovery 与 queue state 采用批量 WAL/group commit，不能每发现一个子目录就同步一次；允许崩溃后重复发现，依靠稳定 directory identity 去重。

### 16.2 Receipt conflict and cursor gaps

receipt 除 `(transfer_id, shard_id, segment_id, batch_id)` 外还必须绑定 target generation、segment digest、record first/last/count、payload bytes、protocol version 和 durability class。同一 key 不同 digest 是冲突，不是幂等成功。每 shard 默认串行发送；若允许并行，则 cursor 必须是 contiguous high-watermark 加 bounded gap set，不能用单个“最后 ACK”越过空洞。

### 16.3 Accepted fuzzy consistency

没有 snapshot、文件系统 change journal 或覆盖停机期的 watcher 时，局部变化集合不可观测。用户接受这一限制，因此本方案不执行发布前全量 reconciliation。durable-completed 记录代表“此前某时刻已观察并提交”，不代表恢复时仍存在或未变化；停机期间新增、修改、rename 和删除都可能不进入本 generation。

最终 manifest/result 必须写入 `consistency=fuzzy`、首次扫描时间、每次 resume 时间窗、durable-completed 未复核计数和 `downtime_changes_unobserved=true`。该状态可视为成功备份，但 UI/API/日志不得省略一致性标签；下一次独立备份负责重新枚举并收敛。

### 16.4 Target visibility contract

用户已选择 `versioned backup`。数据进入 content-addressed immutable objects/packs，路径树进入 immutable segmented manifest；全部依赖 durable 后原子更新 current-ref，并保留上一成功 generation。`in-place mirror` 只保留为旧协议兼容模式，不参与新 generation 的 receipt、ref 或 GC。

### 16.5 Safe deletion coverage

每目录 seal 必须产生 coverage record，包含扫描策略/exclude digest、epoch、完整 entry count/digest 和 error state。只有本 generation `coverage=complete` 且 final receipt durable 的目录可 sweep。ENOENT、EACCES、I/O error、mount boundary、exclude 变化和 unstable 都不得解释为源端删除。

### 16.6 Cross-shard dependency graph

hardlink canonical anchor 必须先 durable，link records 后提交；不能让各 shard 按 first-seen 独立选择 anchor。目录最终 metadata、ACL/xattr 和删除也需要依赖阶段，避免父目录提前变为只读导致后续 child apply 失败。依赖图必须有 bounded fan-out 和失败降级规则。

### 16.7 Data durability cost

segment receipt 批量化了 metadata，不会自动批量化数百万独立小文件的数据 durability。严格模式逐文件 `fsync` 仍可能主导性能，`syncfs` 又会冲刷同文件系统无关写入。小文件需要 pack/staging group，或把 durability 明确降为 filesystem/power-loss 级别不同的模式；两种 receipt 不得互认。

### 16.8 Repeated large-file resume

当前 SHA-256 路径恢复时从 0 重算 prefix。连续在接近文件尾部中断会重复读取大部分文件。partial metadata 应保存固定 chunk 的已验证 hash chain/Merkle checkpoints，并用最后一个完整 chunk 作为恢复边界；损坏或 identity 变化时退回安全重传。

## 17. Immutable repository publication

### 17.1 Object and manifest layout

regular file 使用 whole-object 或大文件 chunk list；小文件进入 immutable pack，pack index 自校验；sparse 文件在 manifest 中记录 data/hole extents。目录、metadata、hardlink group 和特殊文件作为 manifest records。所有 id 使用带 domain separator 的 cryptographic digest，接收端对已存在 object 重新验证 length/type，冲突时 fail-closed。

manifest 不物化为单个全量文件。每 shard 生成 immutable manifest segments，再构建有界 fan-out 的 root manifest tree；root 只引用 child digest、range 和 count。读取、恢复和 GC 均流式遍历，计数使用 checked `uint64_t`。

### 17.2 Publication order

提交顺序固定为：object/pack temp write -> file sync -> content-id rename -> object directory sync -> manifest segment sync -> root manifest sync -> final generation receipt sync -> `refs/current.tmp` sync -> rename current-ref -> refs directory sync -> ACK final publish。任一步失败都不得修改旧 current-ref。

batch receipt 只能引用已 durable 的 object/pack 和 manifest segment。相同 content id 的并发写通过 no-replace/compare-existing 收敛；仓库根使用单 writer lease，ref 更新同时校验 expected previous generation，防止两个 transfer 丢失更新。

### 17.3 Retention and GC

GC roots 是全部 retained generation refs、显式 pinned manifests 和未过期 active-transfer leases。GC 先生成 mark epoch，再 sweep 早于该 epoch 且未标记的 immutable objects；新 object 与 lease 建立顺序必须保证并发 GC 看见至少一个 root。删除 object/pack 后同步对应目录，GC journal 可恢复且不会回滚 current-ref。

## 18. Backup catalog and restore

### 18.1 Directory query model

catalog 的主键空间是 `(generation_id, canonical_path_bytes)`。`list-directory` 输入 generation（可为 `current`）、目录路径、page size 和可选 cursor，返回该目录直属 children；递归遍历由客户端反复分页组成，服务端不为一个请求构造全子树结果。另提供 `stat-path` 和 `list-generations`。

名字按单个 child name 的原始字节做 unsigned lexicographic compare：逐字节比较 `0..255`，首个不同字节较小者在前；一方是另一方前缀时短者在前。类型不参与排序，不做 Unicode normalization、case folding 或 locale collation。wire 以 byte string 返回 `name_bytes`，display name 只是转义后的派生字段。

### 18.2 Stable pagination

首次请求把 `current` 解析为 immutable generation/root digest。opaque authenticated cursor 包含 repository id、generation/root digest、directory node digest、canonical order version、last child key、有效 page/byte limit、签发/过期时间和 query lease id。后续页只读同一 immutable root，即使 current-ref 已切换也保持稳定。

page size 使用有界 `uint32_t`，同时受 max response bytes 限制，因此实际返回数可小于请求值。`has_more=true` 时必须给出 next cursor；空页仅允许目录确实结束。cursor 被篡改、跨目录/仓库/代复用、lease 过期或 generation 已不再 retained 时返回明确 stale/invalid 错误，不从头继续。cursor lease 有 TTL 和每主体配额，防止分页请求无限阻止 GC。

### 18.3 Metadata response

默认 summary 返回 type、logical/allocated size、mode、uid/gid、atime/mtime/ctime、hardlink group、xattr/ACL presence、content/metadata digest 摘要；大 xattr/ACL、chunk list 和 object refs 通过 `stat-path(detail)` 按需获取。目录 node 在 manifest 中直接保存有序 child B-tree/ranges，查询不得扫描对象 payload或从 root 全表过滤。

### 18.4 Restore contract

restore 接受 immutable generation id 和可选 path selector，支持 whole generation、directory subtree 和 single path。恢复端先做目标 confinement、空间/配额预检和 overwrite policy（fail/skip/replace/rename），再按 catalog byte order与 dependency 顺序流式物化；regular file 写同目录 partial，逐 chunk/object 校验后 rename，目录 metadata 最后 child-before-parent 应用。

restore checkpoint 绑定 generation/root digest、selector、destination identity、policy 和最后 durable manifest position；重启只复用校验通过的 partial/chunks。hardlink anchor、sparse extents、symlink、FIFO、xattr/ACL 都必须可恢复；选择性恢复缺少 hardlink anchor 时，以同一 file object 生成独立 regular file，不链接到 selector 外路径。源 generation immutable，因此 restore 可精确重试，不继承 backup 侧 fuzzy source 语义；目标整树默认不承诺原子切换，但每个正式文件原子发布。

### 18.5 Authorization and resource control

每次 list/stat/restore 在解析目录 node、cursor 或 object 前验证主体对 repository、generation 和 canonical path prefix 的权限；not-found 与 unauthorized 对未授权主体使用不可区分响应。服务端限制每主体 page entries、response bytes、活跃 cursor leases、restore 并发和读取带宽，并审计 generation、selector、结果计数和拒绝原因。cursor MAC key 支持轮换，旧 key 仅在 token TTL 窗口内验证。

## 19. Independent metadata-index and resume policy

### 19.1 Derived metadata-index switch

新 repository job 提供 `metadata_index=on|off`，默认 off。它只控制源端/本地 SQLite/LMDB 派生加速索引，用于批量 unchanged lookup；repository segmented manifest 是备份、catalog 和 restore 的权威数据，不属于该可选索引，开关不改变其字段或 digest。

off 路径完全不调用 metadata store open/create/prefetch/put/publish，不探测 backend，也不创建 SQLite DB、journal/WAL/SHM、LMDB data/lock、builder temp 或 checkpoint index sidecar；已有旧索引不读取、不更新、不自动删除。on 路径的索引可由 sealed segments/manifest 重建，索引错误不得转换为 miss。该开关是本地性能策略，不写入 receipt/generation，运行间切换不改变备份语义。

### 19.2 Resume switch

`resume=on|off` 默认 on。on 使用 durable work queue、sealed segment cursor、partial/chunk checkpoint、batch receipt 和 active lease。off 不创建也不读取这些恢复状态；进程中断后 transfer 标记 abandoned，下次运行生成新 transfer id 并重新枚举。repository 中已 durable 的 immutable object 仍可通过 content id 去重，这属于跨 generation dedup，不得报告为 checkpoint resume。

### 19.3 Negotiation and configuration matrix

metadata index 由本地 job 配置决定，不需要 wire capability；显式 on 但 backend 不可用时拒绝，不能静默变 off。resume 由 client request、server policy 和 capability negotiation 计算 effective config；显式 on 无法满足时应拒绝，只有用户允许 fallback 才降级。effective resume、schema version、policy digest 和 transfer id 在开始后 immutable。

测试矩阵覆盖 metadata-index on/off × resume on/off。每组验证 backup、interrupt/restart、catalog、restore、legacy peer、metrics 和 GC；性能报告分别列出 index lookup/build、resume journal 和 pure object-dedup 成本。off 组使用 syscall/filesystem artifact 审计证明没有索引文件 I/O。
