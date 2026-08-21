# T0248 Round 62：LMDB 增量索引生产化与海量 TREE 检查点续传

## 问题陈述

- **现状**：代码已有 `MetadataStore` 的 SQLite/LMDB 双实现和单文件 Data Lane resume；但 LMDB 只在编译开关打开时存在，现有 metadata integration 默认把缓存当 SQLite，LMDB 默认构建无法通过完整测试。递归 TREE 的本地增量索引在 `TREE_END` 后才发布 generation，没有可验证的传输中断 checkpoint。
- **目标**：让 LMDB 成为可部署、可回归、可量化的海量目录增量 backend，并让支持新 capability 的递归 TREE 在中断后从已确认批次安全恢复，减少重复 payload、重复落盘和恢复时间。
- **差距**：当前测试无法证明 LMDB 的真实功能与故障语义；当前恢复只覆盖单个 regular file，不能证明数十万文件 TREE 在进程/网络中断后的批次恢复和错误回退。

## 解决方案

1. 补齐 backend-neutral metadata integration：同一套测试参数化 SQLite/LMDB，校验 cache path、scope/generation、事务回滚、损坏缓存重建、锁竞争和 entry count；增加 100,000-entry 配对 benchmark，记录 full build、unchanged scan、changed scan、RSS、cache bytes 和 metadata lookup rate。
2. 在 TREE capability 协议上增加可选 checkpoint extension。客户端以 bounded batch 发送 entries/payload，服务端完成该 batch 的文件落盘、metadata/dir ordering 和 checkpoint ledger 更新后返回 batch confirmation；checkpoint 绑定 remote generation、options fingerprint、source path 和 `FsEntry` fingerprint。
3. checkpoint ledger 使用 MetadataStore 的事务语义：LMDB 使用独立 checkpoint DBI/记录，SQLite 使用等价表或 sidecar，批次确认与本地状态更新原子化；损坏、generation 不一致、source fingerprint 变化或 peer 不支持时清除/忽略 checkpoint 并安全 replay。
4. 保持旧 peer 和无 checkpoint 模式兼容；不把路径游标当作充分条件，不跳过未验证的源变更；普通 single-file resume、small-pack、hardlink、xattrs、sparse、durability 和 TREE_END 顺序保持不变。

## Seam 分析

### 测试接缝

- backend integration 接缝验证 `backupctl` 的 metadata backend 选择、cache 生命周期和跨运行 generation 行为。
- TREE checkpoint integration 接缝使用真实 TLS agent/client，注入进程中断或连接断开，验证批次确认、恢复、源文件变更和旧 capability fallback。
- 单元接缝验证 checkpoint record 编解码、fingerprint/generation 校验、损坏记录拒绝和 batch confirmation 状态机。
- benchmark 接缝比较 SQLite/LMDB 100,000-entry full/unchanged/changed scan，以及 clean replay 与 interrupted-resume 的 payload/time/RSS。

### 声明的测试接缝

- seam: tests/metadata_backend_integration.sh -> backupctl
- seam: tests/benchmark_metadata_index.sh -> backupctl
- seam: tests/tls_tree_checkpoint_resume_integration.sh -> backupctl
- seam: tests/unit.cpp -> src/metadata_store.cpp

### 验收可测性

- backend 行为由同一脚本在 `sqlite` 和 `lmdb` 两种显式 backend 下独立判定，禁止通过文件扩展名推断结果。
- checkpoint 恢复由确定性中断点、确认批次计数、恢复 payload、最终内容/metadata/hash 和退出码判定。
- 100,000-entry benchmark 至少五对交替样本；性能结论使用均值和最大 RSS，不使用单次样本。

## 用户故事

1. 作为海量文件备份用户，我希望增量扫描优先使用 LMDB 的有界查询和事务更新，以降低 unchanged scan 的耗时和内存压力。
2. 作为运维人员，我希望网络断开或进程重启后，递归 TREE 能从已确认批次继续，而不是重复发送已经落盘的海量文件。
3. 作为可靠性维护者，我希望 checkpoint 不会因源文件变化、generation 变化、缓存损坏或旧 peer 而错误跳过数据。
4. 作为部署人员，我希望 SQLite fallback、LMDB build、TLS/非 TLS 和旧协议兼容都有自动化证据。

## 实现决策

- MetadataStore 对外 contract 保持 procedural C-style；checkpoint 记录不暴露 LMDB mapped pointer，也不依赖 mmap 语义。
- checkpoint 批次有界，服务端确认边界与既有 durability policy 对齐；未确认批次允许 replay，确认记录必须可验证。
- 新 checkpoint capability 是 opt-in wire extension；无 capability 时继续使用既有 TREE 流程。
- checkpoint key 不仅使用 path；至少包含 remote generation、options fingerprint 和 source FsEntry fingerprint，hash 命中必须回验完整 path。
- 失败优先保守回退到 replay，不得为了跳过扫描而信任无法验证的 cursor。

## 测试决策

- 先构造红测：LMDB 构建运行现有 backend integration、checkpoint malformed/invalid-state 单测和中断恢复测试必须在实现前失败或明确暴露缺口。
- 绿测覆盖 SQLite/LMDB、TLS ON/OFF、旧 capability fallback、generation mismatch、source mutation、checkpoint corruption、kill/reconnect 和最终 namespace 内容。
- 性能门槛：LMDB unchanged scan 的五对均值至少比 SQLite 低 10%，或在未达到时继续优化而不把无收益结果标记为生产达标；full build 不劣化超过 5%，RSS 不上升超过 5%。
- 恢复门槛：在至少 100,000 entries 的中断场景中，已确认批次不重复发送 payload，恢复最终 payload 不超过 clean replay 的 60%，内容/metadata/hash 全部一致；任何校验失败必须回退并最终成功。

## 验收标准

- [ ] AC-1: 同一 backend integration 在显式 `sqlite` 和 `lmdb` 下均通过 full baseline、unchanged incremental、one-content-change、metadata-only change、generation mismatch、failed-run rollback、cache lock 和 corrupt-cache rebuild；不再把 LMDB 文件当 SQLite 解析。
- [ ] AC-2: Make/CMake 的 LMDB ON 与 OFF、TLS ON 与 OFF 构建均无新增 warning；LMDB ON 的 `auto` 真实打开 LMDB，显式 sqlite 仍生成/读取 SQLite，显式 lmdb 在 OFF 构建中 fail-fast。
- [ ] AC-3: 100,000-entry 五对交替 benchmark 输出 full build、unchanged scan、changed scan、entries/s、metadata lookups、cache bytes、RSS；LMDB unchanged 均值至少快 10%，full build 不劣化超过 5%，RSS 增幅不超过 5%。
- [ ] AC-4: 新 capability 的 TREE checkpoint integration 在确定性网络/进程中断后恢复已确认批次，最终 regular/small/dir/hardlink/symlink/xattr/sparse 内容、metadata、hash 和 generation 正确；恢复 payload 不超过 clean replay 的 60%。
- [ ] AC-5: source fingerprint 变化、remote generation 变化、options 变化、checkpoint 截断/非法版本/错误 hash 和旧 peer 均不能错误跳过数据；测试证明会清除或忽略 checkpoint 并安全 replay。
- [ ] AC-6: checkpoint confirmation 与 bounded queue、durability、TREE_END/目录排序/硬链接顺序兼容；失败时未确认批次可重放，不能发布错误 generation，进程退出后无死锁、锁泄漏或未回收 worker。
- [ ] AC-7: 既有 regular FSM、single-file resume/sparse、small-pack、metadata-only、TLS/非 TLS tree regression 和 style check 全部通过，且默认行为只在显式支持 checkpoint/backend 时改变。

## 范围外

- 不在本轮实现无校验的全局路径 cursor 跳过，不牺牲源文件变化检测换取表面扫描速度。
- 不删除 SQLite fallback，不要求旧 agent/旧 client 同时升级。
- 不改变普通 Data Lane 的单文件协议和其已有 partial-file resume 语义。
- 不把 LMDB 的单机 benchmark 外推为所有存储介质、网络和内核的统一收益。

## 备注

- 当前唯一可确认的性能事实是 20,000-entry 单次 probe：LMDB unchanged `0.0667s`、SQLite `0.0741s`；Do 阶段必须重新做配对样本。
- checkpoint extension 若确认后会记录新的 ADR，并在 Do 阶段先完成 malformed/state-machine 红测。
