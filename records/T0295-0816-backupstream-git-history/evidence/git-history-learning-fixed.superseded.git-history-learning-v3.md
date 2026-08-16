# backupstream v65→v101 逐提交演进学习报告

> 本报告对应 PDCA 任务 T0295（0816-backupstream-git-history），基于 git diff 为事实来源、`docs/ROUND*_REVIEW.md` 为背景补充。
> 仓库 `main` 分支共 36 个提交，提交信息仅含版本号（`65`…`101`）。v91 无独立 git 提交（其设计说明并入 v92 提交）。
> 全程约束：RSP 协议恒为 v3；持久化 schema 逐版自增且"拒绝迁移、不部分迁移"。

---

## 概述

- 提交与版本对应：从旧到新 `729a681(65)`、`cf2d35d(66)`、`467c0c7(67)`、`bf2e902(68)`、`f779220(69)`、`68908a4(70)`、`35be9cc(71)`、`b5c77aa(72)`、`5af63a3(73)`、`dba4ec9(74)`、`7be954c(75)`、`4f9a333(76)`、`7933849(77)`、`ce1991c(78)`、`99aebc6(79)`、`5c47ab2(80)`、`431a0c8(81)`、`74e55f0(82)`、`942f02b(83)`、`f2a8912(84)`、`4ce0255(85)`、`c7a2c32(86)`、`21fc3c9(87)`、`c532611(88)`、`578519b(89)`、`76e2c77(90)`、`0aa4f65(92)`、`aa44419(93)`、`3775873(94)`、`f40f33e(95)`、`0f86ac4(96)`、`150dce1(97)`、`302ffc3(98)`、`0fb7d84(99)`、`c009dc5(100)`、`867da08(101)`。
- v65 是 root commit（压缩历史，231 文件）。
- 四条主线：**① 客户端目录队列/dirty journal 演进**（v65-v74）；**② Agent 传输 Reactor/FSM 化**（v75-v88）；**③ Observability 与离线诊断**（v89-v101）；**④ 贯穿全程的批量/正确性优化**。

---

## v65 (729a681) — 初始提交：项目整体形态

### 修改内容
- **改动文件**：全部 231 文件（root commit，压缩历史）。模块：`common`(帧类型/kProtocolVersion=3)、`error`、`channel`、`transfer`(RSP/3)、`regular_file_io`、`storage_backend`、`hardlink_tracker`、`data_lane`、`adaptive_window`、`reactor`/`reactor_connect`/`reactor_group`/`event_wait`/`tls_reactor`/`tls_sync_bridge`、`work_pool`/`cpu_resources`/`cpu_scheduler`、Agent 端（`backup_agent`、`agent_acceptor`、`agent_tree_runtime`、`agent_tls_runtime`、`agent_session_pool`、`agent_system_service`、`agent_exec_runtime`、`agent_restore_runtime`）、Client 端（`backupctl`、`client_backup_runtime/state`、`client_control_reactor`、`client_exec_reactor`、`client_data_lane_runtime`、`client_restore_runtime`、`client_blocking_exec`）、`backup_catalog`（SQLite+LMDB 双后端）。
- **核心代码**：`backup_catalog_t` 三索引模型（path→inode / inode→metadata+seen_run / parent+name→inode）；`client_backup_state` 持久目录队列（PENDING/PROCESSING/DONE）+ getdents cursor + 目录身份；`agent_tree_runtime` TREE PUT/GET 事务状态机；catalog-driven restore 帧（`FT_OPEN_RESTORE`=53…`FT_RESTORE_FILE`=58）与 Data Lane 帧（60-67）。

### 修改作用
压缩历史快照；最后一段演进是 catalog-driven、可重启的 restore（512 目录页游标 + 大文件 offset 两级续传）。

### 架构变更
初始骨架：单一权威 client catalog + 有界 backup-state DB + RSP/3 + Agent（root-confined objects / committed generation / stable partial）；递归 PUT 事务状态机（`OPEN_PUT_TREE→批扫描→TREE_BARRIER→身份复核→catalog 批提交→DIR_FINAL→TREE_END`）。

---

## v66 (cf2d35d) — 可信 dirty-directory feed（选择性增量）

### 修改内容
- **改动文件**：新增 `client_dirty_feed.cpp/hpp`；修改 `backup_catalog`、`client_backup_runtime`、`client_backup_state`、`client_config`、`agent_tree_apply`、`backupctl`、`common.hpp`；新增测试 `dirty_incremental_integration.sh`。
- **核心代码**：`client_dirty_feed_enqueue()`（校验 `backupstream-dirty-v1` 头 + `base-generation` 精确匹配 + 路径规范化 + 512 批量入队）；`backup_catalog_list_stale_children()`/`scan_subtree()`（新索引 `inode_parent_seen`）；dirty 模式下子目录不递归入队、不做全局 stale 扫描；Agent `delete_destination_entry` 改为 `remove_tree_entry_at` 递归整树删除；`--dirty-dir-list`（要求 incremental + catalog + `--no-hard-links`）。

### 修改作用
把增量扫描成本从"全命名空间"降到"真实脏工作集"（实测 100k 文件 full 2.02s vs dirty 0.01s）。父目录 mtime 不可靠（in-place 写不改变父目录时间戳），故用显式、generation 绑定的可信 feed。

### 架构变更
- 协议不变（RSP/3）；backup-state `64→66`、restore-state `65→66`。
- Agent 删除升级为递归整树；catalog 新增 `(parent_id,seen_run,name)` 索引。

---

## v67 (467c0c7) — 生产安全：job 资源锁 + active_run 栅栏 + catalog verify

### 修改内容
- **改动文件**：新增 `client_resource_lock.cpp/hpp`；修改 `backup_catalog`、`backupctl`、`client_backup_runtime`、`client_backup_state`、`client_config`、`client_restore_runtime`；新增测试 `catalog_safety_integration.sh`。
- **核心代码**：侧车 `flock(2)` 锁文件（catalog 写独占/读共享、state 独占，非阻塞 LOCK_NB 排序获取）；catalog 持久 `active_run` 栅栏（`begin_run` 拒绝已存在、`set_generation` 同事务清零）；job 启动 crash-safe 顺序（先提交 resume-state 带 run id，再原子打开 active_run）；`sqlite_catalog_verify`/`lmdb_catalog_verify` 逻辑校验；`backupctl catalog status/verify`。

### 修改作用
修生产正确性/运维问题：两个进程不能交替出合法事务共享同一权威 DB；kill 后"部分新行持久、generation 仍旧"的混合视图；`active_run!=0` 时查询一律 EBUSY。

### 架构变更
- 协议不变；catalog schema `64→67`。
- 新增"完整 job 资源锁"层 + 持久 active_run 栅栏语义。

---

## v68 (bf2e902) — 高文件数备份批量处理

### 修改内容
- **改动文件**：修改 `backup_catalog`、`client_backup_runtime`、`client_backup_state`、`client_restore_state`；新增测试 `backup_batching_integration.sh`。
- **核心代码**：No-op 远端同步消除（无变更不发 TREE_BARRIER/DIR_FINAL）；64 目录组批量 claim/complete 单事务；catalog 预编译 `lookup_stmt`/`mark_seen_batch_stmt` + `backup_catalog_mark_seen_ids`（SQLite 批量 UPDATE、LMDB 同事务按 id 改）；宽目录 256-entry 游标不变。

### 修改作用
消除固定成本放大（实测 1000 目录×10 文件 full 1.84s→0.71s，unchanged incremental 0.73s→0.17s）。记录并否决了并行 metadata 探针实验（不稳定）。关键不变量："catalog commit 先于队列 completion，queue 永不领先 catalog"。

### 架构变更
- 协议不变；schema 全→68；重放界由"每目录"放宽到"至多 64 目录"。

---

## v69 (f779220) — hardlink-safe selective incremental

### 修改内容
- **改动文件**：修改 `backup_catalog`、`client_backup_runtime`、`client_backup_state`、`client_config`；`dirty_incremental_integration.sh`。
- **核心代码**：catalog 新增 fileid 反向索引（仅 `nlink>1` 行，SQLite 部分索引 `inode_fileid`、LMDB fileid DB）；`backup_catalog_list_file_id()`（256 行分页）；`enqueue_dirty_hardlink_peer_dirs()` 持久入队 peer 父目录；`sqlite_open_catalog` 先读 schema 再 DDL（干净拒绝旧库）。

### 修改作用
选择性增量无法保留 hardlink 拓扑的问题；仅对已提交 nlink>1 组做紧凑反向索引 + 持久 peer 扩展 + 首链路 feed 契约（需报新 link 父 + 至少一个旧 peer 父）。

### 架构变更
- catalog schema `68→69`，新增 fileid 反向索引；协议不变。

---

## v70 (68908a4) — first-party generation-fenced dirty journal

### 修改内容
- **改动文件**：新增 `backup_dirtyd.cpp`(461)、`client_dirty_journal.cpp/hpp`(706)；修改 `client_backup_runtime`、`client_backup_state`、`client_config`；新增测试 `dirty_journal_integration.sh`。
- **核心代码**：backup-dirtyd 守护进程（inotify 递归 watch、`event_waiter_t`、SIGTERM/SIGINT/SIGHUP、磁盘 file_index）；SQLite journal schema=1（`info`/`dirty(path,first_seq,last_seq)`/`file_index`）；生成/健康围栏（`health_epoch`/`valid`/`ready`/`base_generation`）；`prepare_backup` 捕获 cutoff_seq；`finish_backup` 单事务 cutover；首硬链接转换靠磁盘 file_index 自动找旧 peer（自动满足 v69 两父目录契约）。

### 修改作用
关闭外部 feed 正确性完全委托外部生产者的缺口，引入**失败关闭（fail-closed）**健康模型：任何重启/溢出/歧义都强制全量重扫后再武装。

### 架构变更
- **重大架构扩展**：新增运行时守护进程 backup-dirtyd；新持久格式 journal schema=1；backup-state/catalog `69→70`；协议不变。

---

## v71 (35be9cc) — adaptive high-latency metadata enumeration

### 修改内容
- **改动文件**：新增 `client_metadata_scan.cpp/hpp`、`metadata_scan_test.cpp`；修改 `client_backup_runtime`、`client_dirty_journal`。
- **核心代码**：`client_metadata_scanner_t` 串行启动 + 采样自适应（≥128 条目且平均 ≥50us 启动 4 worker）；`client_metadata_scan_batch` 把 fstatat 抽离遍历；失败降级串行；`--progress` 输出模式/workers/采样均值；dirty journal 修复 v70 ready=0 竞态（selective=false → 全量重扫）。

### 修改作用
工作负载门控的高延迟元数据枚举（500us 延迟 2.87x、1ms 3.10x）；不并行 readdir/catalog/TREE（保序）。

### 架构变更
- 每备份任务自适应线程池（仅 fstatat 并行）；schema/catalog 71、journal 仍 1。

---

## v72 (b5c77aa) — exact in-batch metadata activation

### 修改内容
- **改动文件**：修改 `client_metadata_scan`、`metadata_scan_test`。
- **核心代码**：采样只采恰好到 128 的前缀，达阈值立即激活 worker，未采样后缀并行处理；`parallel_recommended` 字段决策/激活分离（128 样本恰为 batch 末尾则延迟激活）；测试确定性 127+1 边界。

### 修改作用
消除 v71"整批串行后才决策"的错配（高延迟首 batch 白付最多 128 次串行 RTT）。

### 架构变更
无；纯内部激活时序优化；schema 72。

---

## v73 (5af63a3) — checkpoint-aware directory identity probes

### 修改内容
- **改动文件**：修改 `client_backup_runtime`、`backup_catalog`、`client_backup_state`；`directory_cursor_integration.sh`。
- **核心代码**：`client_catalog_pending_t` 增 `track_observed_paths`/`observed_paths`；最终 batch ≤256 条 catalog 决策保留内存 pending，完成时 identity 检查通过才 `client_catalog_commit_pending`（success-commit）；删除 v72 三次检查中前两次；dirty 模式 final observed paths 作 `protected_paths` 防 stale 误删。

### 修改作用
"提交即成功"语义，关闭 v72 窄竞态（pre-final 通过、final 变更后留下假 seen 证据）；目录 fstat 减半。

### 架构变更
无协议/存储变化；提交时序与身份校验边界重构；schema 73。

---

## v74 (dba4ec9) — leaf-sparse first-party dirty journal

### 修改内容
- **改动文件**：修改 `client_dirty_journal`(+244)、`client_backup_state`(+187)、`client_backup_runtime`(+106)、`backup_dirtyd`、`client_metadata_scan`；新增测试 `dirty_journal_sparse_integration.sh`。
- **核心代码**：journal schema 1→2（`dirty_full`/`dirty_leaf` 表）；backup-dirtyd 普通命名事件归类 `(parent,child)` hint 写 leaf，目录级事件走 full；`prepare_backup` 稀疏化（≤1024 hints）；state 新增 `dirty_hint` 表 + `requeue` 位；稀疏扫描不 readdir 直接从 hint 喂；缺失目录 tombstone 修复（ENOENT 不再中止增量）。

### 修改作用
把 journal 从父目录级升级为叶稀疏（20000 文件目录改一个文件：fstatat 从 20000 降到 1，21.8x）。卡点：每 parent 每 cutoff 至多 1024 hints，超限回落全量。

### 架构变更
- journal schema 1→2、backup-state schema 74；扫描模式 full/sparse/tombstone 三路径；协议不变。

---

## v75 (7be954c) — TREE 往返优化

### 修改内容
- **改动文件**：修改 `common.hpp/cpp`、`agent_tree_runtime`、`client_backup_runtime`、`client_backup_state`；新增测试 `tree_fence_pipeline_integration.sh`。
- **核心代码**：新增 `CAP_TREE_DELETE_PIPELINE` 能力位；`TREE_DELETE` 带 `FF_PIPELINED` 抑制 per-delete ACK；catalog 擦除推迟到累积 fence + 身份校验双成功；final batch 不再发 TREE_BARRIER（以 DIR_FINAL ACK 为 fence）；全局 stale 清理至多 pipeline 64 行。

### 修改作用
消除控制面 RTT 放大（64 changed 目录 2.746s→1.437s，64 稀疏叶删除 10.1x）。

### 架构变更
- 纯 wire 增量（新能力位）；catalog 擦除延迟到累积 fence（可重放正确性约束）；schema 75。

---

## v76 (4f9a333) — plain EXEC 事件泵（per-EXEC）

### 修改内容
- **改动文件**：新增 `agent_exec_io_pump.cpp/hpp`；修改 `agent_exec_runtime`、`client_blocking_exec`、`common`（删 AsyncControlSender）；新增测试 `plain_exec_event_pump_integration.sh`。
- **核心代码**：`agent_exec_io_t` 不透明对象 + per-EXEC pump pthread（256KiB 栈），拥有三个 child pipe + EXEC TX + event_waiter(POLL) + wake pipe；session worker 变 network-RX-only；动态注册兴趣（stdin 有排队才注册 OUT、credit>0 才注册 IN）；`client_exec_tx_pump_t` 单一 TX pump。

### 修改作用
修 v75 暴露的 plain-EXEC child-pipe 死锁；去掉每会话 3 个 Agent 线程 + 2 个客户端 sender，改为每会话 1 个 pump（32 会话 +96→+32 线程）。

### 架构变更
**事件模型首次进入事件泵**，但事件域仍按会话私有（每 active plain EXEC 一个 pump pthread）。

---

## v77 (7933849) — 进程级共享事件域（EXEC shard）

### 修改内容
- **改动文件**：大改 `agent_exec_io_pump.cpp`(789)；修改 `agent_config`（`--plain-exec-reactors`）、`agent_exec_runtime`、`backup_agent`、`common`（`connection_try_writev_exclusive`）；新增测试 `plain_exec_shared_reactor_integration.sh`。
- **核心代码**：`exec_io_domain_t` + `exec_io_shard_t[]`（每 shard 512KiB 线程 + event_waiter + wake pipe + 命令队列 + sessions 哈希）；`--plain-exec-reactors`（0=auto=ceil(max-exec/64)，≤8，≤CPU）；per-session 有界 TX FIFO + shard-local scratch 非阻塞 sendmsg；`connection_try_writev_exclusive()` 非阻塞独占 TX。

### 修改作用
per-EXEC pump 线程变 O(shards)（100 sleeping EXEC 线程 229→131、active RSS 111944→8192 KiB）；32 路聊天上下文切换降 26%。

### 架构变更
**事件域由 per-EXEC 私有升级为进程级共享分片**；socket RX 仍在固定 blocking worker（拒绝共享 poll + 阻塞 send 方案）；引入非阻塞独占 TX 原语。

---

## v78 (ce1991c) — 弹性会话池 + pidfd 子进程事件

### 修改内容
- **改动文件**：大改 `agent_session_pool`；修改 `agent_exec_runtime`（pidfd）、`agent_config`（`--session-worker-idle-ms`）；新增测试 `plain_session_elastic_pidfd_integration.sh`。
- **核心代码**：`--session-workers` 语义改上限；`agent_session_pool_init` 不再预创建 worker，按队列压力 spawn；worker 用 `pthread_cond_timedwait` 空闲退休；`exec_pidfd_open`（SYS_pidfd_open），EXEC 等待用 event_waiter 同时等 socket + pidfd + deadline；pidfd 不可用回落 100ms 轮询。

### 修改作用
消除 idle 预创建 + 周期性 waitpid 轮询（idle 线程 129→1；100 sleeping EXEC 线程 131→103、上下文切换 1002/s→0/s）。

### 架构变更
**worker 生命周期弹性化 + 子进程完成事件化**（pidfd 取代 100ms waitpid 轮询）；剩余边界：每 active plain session 一个 blocking network-RX worker。

---

## v79 (99aebc6) — EXEC socket RX 移交共享 shard

### 修改内容
- **改动文件**：修改 `agent_exec_io_pump`(+369)、`agent_exec_runtime`（`agent_exec_start_handoff`）、`agent_session_pool`、`backup_agent`、`common`（`connection_release_fd`）；新增测试 `plain_exec_shared_rx_integration.sh`。
- **核心代码**：blocking worker 完成 HELLO/auth/OPEN_EXEC 解码/fork/OPEN_OK 后 `connection_release_fd` + `connection_adopt_fd` + `agent_exec_io_start_async` 移交 shard；增量非阻塞 RSP 解析器（16 字节 header buffer）；pidfd 注册进 shard；RESULT 半关闭 drain 协议（修 TCP RST）；shutdown 顺序先 event domain 后 pool。

### 修改作用
移除剩余 per-active-EXEC Agent RX pthread（100 sleep EXEC 线程 103→3）；32×4MiB stdout 0.194s→0.097s。

### 架构变更
**EXEC 的 socket RX 从 blocking worker 正式迁入共享 shard**（单一所有权）；引入增量非阻塞帧解析器与 RESULT drain 协议；会话记账/生命周期改为"异步 shard 比 setup worker 活得更久"模型。

---

## v80 (5c47ab2) — 非阻塞 plain ingress

### 修改内容
- **改动文件**：新增 `agent_plain_ingress.cpp/hpp`(267)；修改 `agent_session_pool`（`agent_session_preface_t`、`submit_prefaced`）、`backup_agent`；新增测试 `plain_ingress_integration.sh`。
- **核心代码**：`agent_plain_ingress_t` 挂主 reactor，非阻塞持有 fd 至解析 HELLO→认证→HELLO_ACK→首个操作帧；状态机 `INGRESS_WAIT_HELLO→SEND_HELLO_ACK→WAIT_OPEN`；每事件至多 64KiB 预算；`ingress_handoff()` 构造 preface 提交业务池；admission 两层分离（max_sessions 会话槽 ≠ session_queue/workers 业务线程槽）。

### 修改作用
消除"未完成/未认证输入占满业务池"（256 个 1 字节 HELLO 客户端 v79 33 线程+1002ms 超时 → v80 1 线程+3.3ms）。

### 架构变更
**主 reactor 上的非阻塞 ingress 前端**，三层流水线：main reactor ingress → 弹性 blocking worker 池 → EXEC 二次 handoff 共享 shard；TLS 完全独立。

---

## v81 (431a0c8) — plain 控制 worker 让出（control worker yield）

### 修改内容
- **改动文件**：新增 `agent_plain_control.cpp/hpp`；修改 `agent_plain_ingress`、`agent_session_pool`、`backup_agent`；新增测试 `plain_control_yield_integration.sh`。
- **核心代码**：`agent_plain_control_can_continue()`（FIONREAD+MSG_PEEK 探测下个完整帧）；`agent_plain_control_return()` 归还连接；三态枚举 `agent_session_result_t`（DONE/ASYNC_HANDOFF/REACTOR_YIELD）；ingress eventfd return 通道；PING 等控制操作后 worker 让出或就地缓冲突发。

### 修改作用
解决"仅为可能稍后发请求的已验证对端保留 blocking worker"（`--session-workers 1` 时 A 空闲致 B PING 600ms 超时 → v81 0.1ms）。

### 架构变更
ingress 成为控制间隙 socket 所有者；引入 eventfd 跨线程归还闭环；worker 生命周期三态化；schema 81。

---

## v82 (74e55f0) — plain System-RPC 执行/传输拆分

### 修改内容
- **改动文件**：修改 `agent_plain_ingress`(+351)、`agent_config`（`--control-workers`）、`backup_agent`；新增测试 `plain_control_backpressure_integration.sh`。
- **核心代码**：ingress 相位新增 `INGRESS_CONTROL_WORK`/`SEND_CONTROL`；`ingress_control_pool_ensure()` 懒加载 control Work Pool；复用 `agent_response_vector_send` + Reactor 非阻塞 TX（64KiB 预算）；`ingress_control_readdir_run()`（1024 项/轮，EOF 才发 FT_DIR_END）；PING 32 请求纯 Reactor 突发；`SYS_STAT` ≤32 归并一轮。

### 修改作用
实现 v81 预留边界：慢读对端占死唯一 worker 的问题（30k 目录 + A 停读，B SYS_STAT 1001ms→0.2ms）。

### 架构变更
**"执行/传输分离"成为模板**（vector response sink + Reactor 非阻塞 TX），后续 TREE/FILE/RESTORE/Lane 全部复用；schema 82。

---

## v83 (942f02b) — plain 原生 TREE Reactor 传输（transport-neutral TREE FSM）

### 修改内容
- **改动文件**：新增 `agent_tree_legacy.cpp/hpp`(402)；大改 `agent_tree_runtime`(795)；修改 `agent_plain_ingress`、`agent_tls_runtime`；新增测试 `plain_tree_reactor_integration.sh`。
- **核心代码**：`agent_tree_transport_t` transport adapter（emit_frame/resume_rx/tx_bytes/request_close）；TLS 专属 `agent_tls_tree_t` 更名 `agent_tree_reactor_t` 中立化；旧同步 TREE 抽入 `agent_tree_legacy`；ingress `INGRESS_TREE` 相位 + `--tree-workers` 懒加载；非阻塞 TX 高水位 64MiB；**SEEK_DATA/SEEK_HOLE 稀疏正确性修正**。

### 修改作用
默认 plain TREE 移出阻塞 transport，TLS 与 plain 共享一个中立 FSM（空闲 PUT 1003ms→18ms；256MiB 慢读 GET 1003ms→11ms）。

### 架构变更
**FSM 中立化范式确立**（一个实现 + 两个薄 transport adapter）；剩余阻塞域：standalone FILE、RESTORE、非零 small-file-workers 的 TREE；schema 83。

---

## v84 (f2a8912) — standalone FILE Reactor 所有权

### 修改内容
- **改动文件**：新增 `agent_file_runtime.cpp/hpp`(396)、`agent_tls_runtime_internal.hpp`、`agent_tls_runtime_metrics.cpp`；修改 `agent_plain_ingress`、`agent_tls_runtime`(-284)、`agent_config`；新增测试 `plain_file_reactor_integration.sh`、`tls_file_reactor_integration.sh`。
- **核心代码**：`agent_file_reactor_t` + `agent_file_transport_t`；PUT 分 OPEN/WRITE/FINISH 有界轮（credit 仅写轮完成后返还）；GET 仅在 credit+容量允许时调度 READ；`ingress_is_native_file()` 拦截 `FT_OPEN_PUT/GET`；TLS standalone FILE 也走同一 FSM；TLS runtime 因 850 行风格上限拆源。

### 修改作用
standalone FILE 移出阻塞路径（空闲 PUT 500ms→0.2ms；256MiB 慢读 GET 500ms→0.27ms），TLS 首次脱离同步 bridge。

### 架构变更
- 复用 `--tree-workers` 池（TREE/FILE）；socket RX/TX 归 Reactor；schema 84。剩余阻塞域：RESTORE + 非零 small-file-workers 的 TREE。

---

## v85 (4ce0255) — catalog RESTORE Reactor 所有权

### 修改内容
- **改动文件**：新增 `agent_restore_reactor.cpp/hpp`(577)；修改 `agent_plain_ingress`、`agent_tls_runtime`、`agent_tree_runtime`、`client_restore_runtime`；新增测试 `plain_restore_reactor_integration.sh`。
- **核心代码**：`agent_restore_reactor_t`（RESTORE_WORK_OPEN/BATCH_OPEN/ITEM_PREPARE/HASH_PREFIX/READ/FINISH）；`deferred_rx` 保留一个已消费未转换帧；紧凑 small-file batching（64×1KiB → 1 个 SMALL_PACK）；同轮 BATCH_END→RESTORE_END 竞态修复（handle_frame 反映 post-transition 状态）；**TLS FILE_END 超越 DATA 修复**（终帧仅 `tx_bytes()==0` 时发）。

### 修改作用
RESTORE 移出阻塞路径并删除旧阻塞运行时（空闲 RESTORE 500ms→0.17ms；128MiB 慢读 500ms→0.16ms）；跨版本 raw-RSP 驱动 SHA-256 一致。

### 架构变更
- 剩余阻塞桥收窄到"非零 small-file-workers 的 TREE"；RESTORE 共享 `--tree-workers` 池；确立"终帧需 tx_bytes()==0"中立规则；schema 85。

---

## v86 (c7a2c32) — 移除最后 TREE 阻塞桥（原生 small-file fan-out）

### 修改内容
- **改动文件**：大改 `agent_tree_runtime`(+238)；删除 `agent_tree_legacy.*`；修改 `agent_config`（`--small-file-workers` 重定义）、`agent_tls_runtime`、`agent_plain_ingress`、`backup_agent`；新增 `plain_tree_small_workers_reactor_integration.sh`；重写 `tls_tree_pool_isolation_integration.sh`。
- **核心代码**：`--small-file-workers N` 重定义为 **per-PUT-TREE 有界 fan-out 上限**（不创建 N 线程、不再作传输选择器）；`agent_tree_small_task_t/job_t` 在 Reactor 解码 FT_SMALL_FILE 拆独立 job；per-TREE 高水位 `max(8,8*N)`；fence 顺序机制（首个非 small 帧保留为单帧 deferred fence）；`small_cancel` 原子标志。

### 修改作用
移除最后一个 Agent 端 TREE 兼容桥（v85 500ms 超时 → v86 0.136ms）；`--small-file-workers` 与传输选择解耦。

### 架构变更
- 线程模型分层：per-TREE admission 上限与进程级 `tree-workers` 天花板解耦；TREE 无条件原生；schema 86。

---

## v87 (21fc3c9) — Data Lanes 迁移到 Reactor（transport-neutral lane FSM）

### 修改内容
- **改动文件**：新增 `agent_data_lane.cpp`(681)、`agent_lane_group.cpp`(779)、`agent_lane_transport.hpp`(118)；替换 TLS 专属 lane 实现；修改 `agent_plain_ingress`、`agent_session_pool`、`agent_tls_runtime`；大幅删减 `backup_agent.cpp`(-865)；新增测试 `plain_data_lane_reactor_integration.sh`。
- **核心代码**：`agent_lane_transport_t` 窄回调 adapter；`agent_data_lane_t` 状态机（PUT_IO/GET_IO/WAIT_FINAL_DRAIN 等）；`agent_lane_group_t` 生命周期；ingress 拦截 `OPEN_PUT_LANES/OPEN_GET_LANES/LANE_ATTACH`；`--lane-workers`/`--lane-cpu-workers` 懒创建；**阻塞 service 表整体删除**（backup_agent.cpp 从 ~1313 行降到 ~528 行）；plain ingress 只移交完整 `FT_OPEN_EXEC`。

### 修改作用
移除最后一个长生命周期 plain Data-Lane socket 所有权（空闲 lane-group 500ms→0.138ms；GET lane 慢读 500ms→0.273ms）；可达性清理阻塞 service 表。

### 架构变更
- 无 general blocking service table；lane 工作归共享池；`--session-workers` 收窄为 EXEC launch 上限；schema 87。

---

## v88 (c532611) — EXEC 最后会话池移交（bounded process-launch pool）

### 修改内容
- **改动文件**：删除 `agent_session_pool.*`；新增 `agent_exec_process.cpp/hpp`(129)；大改 `agent_exec_runtime`、`agent_exec_io_pump`(-156)；修改 `agent_config`（`--exec-launch-workers`/`--exec-launch-queue`）、`agent_plain_ingress`、`backup_agent`；新增 `exec_launch_pool_integration.sh`、`plain_exec_launch_pidfd_integration.sh`。
- **核心代码**：`--exec-launch-workers`（默认 1，有界 launch pool）；legacy `--session-workers` 兼容映射（≤4）；`agent_exec_process` 进程原语抽出（fork 前 materialize argv、管道 CLOEXEC）；**launch-error 管道**（chdir/execvp 失败回写真实 errno 作 OPEN_ERR，EOF=exec 成功）；`agent_exec_plain_launch_t` 创建/submit/cancel；共享 EXEC 域统一异步 add/handoff + fail-closed 清理。

### 修改作用
移除最终 `agent_session_pool` 边界；修复 v87"fork 成功≠启动成功"缺口（不存在的可执行返回 ENOENT）；多命令并发 fork/setup 的线程放大（24 并发 EXEC peak 25→6）。

### 架构变更
- `agent_session_pool.*` 整体移除；最终三种有界执行上下文：Reactor/event domain（socket+child-pipe 就绪）/ fs-hash-control Work Pools（不持 socket）/ 小型 EXEC launch Work Pool（仅进程 setup）；网络所有权恒驻 Reactor；schema 88。

---

## v89 (578519b) — server-local observability

### 修改内容
- **改动文件**：新增 `agent_observability.cpp/hpp`；修改 `agent_config`、`agent_exec_io_pump`、`agent_exec_runtime`、`agent_plain_ingress`、`agent_system_service`、`agent_tls_runtime`、`backup_agent`、`backupctl`；schema 88→89。
- **核心代码**：`agent_observability_t` 观测器（boot_id + session/operation id + 原子计数器）；trace 三元组 `<boot-id>-<session-id>-<operation-id>`；13 固定操作类；跨执行域 span 传播（`exec-handoff`）；异步终态帧分类（OPEN_ERR/RESET/LANE_ABORT 为 failed）；errno 保真（`bs_error_set_errno`）；SIGUSR1 在线快照；`--trace-events`/`--trace-slow-ms`。

### 修改作用
让传输所有权转移可观测、可归因（op-begin→worker-submit→worker-done→exec-handoff→op-end 完整 trace）；严格 server-local，不进 RSP。

### 架构变更
引入进程内 trace 数据模型 + 观测证据链雏形 + 错误保真契约；协议/认证/客户端零变化。

---

## v90 (76e2c77) — 机器可读 observability 导出

### 修改内容
- **改动文件**：修改 `agent_observability`(+286)、`agent_config`、`backup_agent`；新增测试 `observability_export_integration.sh`；schema 89→90。
- **核心代码**：异步 exporter 线程（有界队列 + `emit_record`，满则丢弃计数，绝不阻塞协议路径）；JSONL `--observability-jsonl`（schema 前缀 `backupstream.observability.v1`）+ Prometheus textfile `--metrics-textfile`（原子写，标签限 version/operation/status）；`--trace-op`/`--trace-sample-every`；`json_quote()`/`text_quote()` 分离；exporter 健康度量。

### 修改作用
把人类日志变为可操作监控契约（1200 PING 在队列容量 8 + 写盘拖慢时 29.7ms 完成、显式丢弃 2385 条——丢失显式有界）。

### 架构变更
观测升级为双平面导出（高基数 JSONL + 固定基数 metrics）；新增导出子系统（独立线程 + 有界队列 + 原子写 + 轮转）；协议零变化。

---

## v92 (0aa4f65) — observability resilience + backup-observe（含 v91）

> v91 无独立提交，其设计（观测韧性/运行时快照）与 v92 同落于此提交。

### 修改内容
- **改动文件**：新增 `backup_observe.cpp`(224)、`docs/backupstream-prometheus-alerts.yml`；修改 `agent_observability`(+132)、`backup_agent`；新增测试 `backup_observe_integration.sh`、`observability_resilience_integration.sh`；schema 91→92。
- **核心代码**：固定延迟直方图（14 桶，+Inf==count）；exporter 健康状态机（failure/success、recoveries）；`agent_observability_runtime_t` 运行时/config 快照（排除 token/root/cert 路径）；**backup-observe**（summary/trace/failures/check，手写 JSON 解析）；告警化 enable 状态 gauge；`docs/backupstream-prometheus-alerts.yml` 示例规则。

### 修改作用
v91 修 telemetry 契约的操作质量；v92 把本地证据变成可查询、可告警的消费面；明确"不新增网络监听面"。

### 架构变更
观测链路闭环（生产→韧性→离线消费/告警）；首次出现消费 telemetry 的独立可执行二进制；诊断证据权威性分层（聚合计数器对采样免疫 vs 可采样事件流）。

---

## v93 (aa44419) — client-requested session debug

### 修改内容
- **改动文件**：修改 `common.hpp`（`FF_SESSION_DEBUG`、`CAP_SESSION_DEBUG_LOG`）、`agent_config`、`agent_observability`、`agent_plain_ingress`、`agent_tls_runtime`、`backup_observe`、`backupctl`、`client_config`、各客户端 Reactor；schema 保持 92。
- **核心代码**：`FF_SESSION_DEBUG=1<<15` 在 FT_HELLO flags；Agent 仅策略允许且认证成立时在 HELLO_ACK 回显；`--allow-client-debug-log`（未认证即拒）；`agent_observability_session_debug()`；span 级 `client_debug` 标记绕过采样；`backupctl --debug-log`；固定计数。

### 修改作用
session 级、策略门控、认证要求的按需详细观测；v92 Agent 忽略 flags，v93 debug 请求对旧 Agent 自然降级为普通会话（非协议错误）。

### 架构变更
观测请求首次进入线上协议面（借用 HELLO/HELLO_ACK flags，无新帧）；隐私边界成文（不接受不可观测；接受也不记录 DATA/token/密钥/命令文本）。

---

## v94 (3775873) — client-debug guardrails

### 修改内容
- **改动文件**：修改 `agent_observability`(+74)、`agent_config`（`--client-debug-max-sessions/events/seconds`）、`backup_observe`；新增测试 `session_debug_limits_integration.sh`、`tls_session_debug_limits_integration.sh`。
- **核心代码**：三档预算（默认 4 sessions/1024 events/300s，0=不限）；`client_debug_sessions` map + `client_debug_consume()`；容量满在 HELLO 拒绝（denied_capacity vs denied_policy）；触顶发单条 `session-debug-limit` 并释放槽位但**不关 socket/不取消操作**；span 区分 sampled/client_debug。

### 修改作用
受控配额使合法对端不能造成无界详细日志量或不限 debug 会话；截断只停额外 detail、不断业务。

### 架构变更
观测资源由无界会话 debug 变为显式配额管理的受控资源；`session-debug-limit` 成为"证据可能截断"信号（为 v95 diagnose 铺路）。

---

## v95 (f40f33e) — backup-observe diagnose（离线故障诊断）

### 修改内容
- **改动文件**：修改 `backup_observe.cpp`(+197)、`common.hpp`；Agent 零改动；新增测试 `backup_observe_diagnose_integration.sh`。
- **核心代码**：`diagnose` 命令（`--trace`/`--stage-ms`）；`diag_finding_t{severity,code,confidence,evidence}`；**confirmed** 诊断（基于终态 errno/message：transport-reset/storage-capacity/authorization/protocol/worker-capacity/slow-operation 等）+ 聚合级（exporter 失联/丢弃/队列压力）；**suspected** 诊断（`worker-stage-delay`、`exec-handoff-delay`，明确标注推断）；`--stage-ms 0` 关闭 suspected。

### 修改作用
把本地观测证据变成 operator-facing 诊断命令；confirmed 与 suspected 严格分离，确立"测量区间描述而非根因断言"的克制归因原则。

### 架构变更
诊断证据链首次具备置信度维度；Agent/协议/客户端零变化。

---

## v96 (0f86ac4) — worker queue/execution boundaries

### 修改内容
- **改动文件**：修改 `agent_observability`、`agent_exec_runtime`、`agent_plain_ingress`、`agent_tls_control_runtime`、`backup_observe`；schema 保持 92。
- **核心代码**：worker 四段契约 `worker-submit→start→finish→done`（拆 `_body` 再包首尾埋点）；**不可变快照 `agent_trace_event_snapshot_t`**（Reactor 提交前拷贝，worker 只读消费，绝不 dereference 活跃可变 span）；诊断细分 `worker-queue-delay`/`worker-execution-slow`/`worker-completion-delay`（confirmed）。

### 修改作用
把 v95 混合 submit→done 间隔拆为队列等待/执行/投递三段；快照机制保证跨线程证据安全。

### 架构变更
观测线程安全模型升级为"Reactor 侧不可变快照 + worker 只读消费"（后续 completion/callback 取证地基）。

---

## v97 (150dce1) — completion-post / Reactor scheduling boundaries

### 修改内容
- **改动文件**：修改 `work_pool`(+33)、`reactor`(+18)、`agent_exec_runtime`、`agent_plain_ingress`、`agent_tls_control_runtime`、`backup_observe`。
- **核心代码**：`work_item_set_lifecycle_callback()`（COMPLETION_POST/RUN 两类事件）；`reactor_post_wait_priority_timestamped()` 精确入队时间戳；新事件 `completion-post`/`completion-run`（带 `post_wait_ns`/`reactor_wait_ns`）；诊断 `worker-completion-overhead`/`reactor-post-backpressure`/`reactor-scheduling-delay`（confirmed）。

### 修改作用
补齐 finish→done 复合间隔，精确测量 worker 完成回投 Reactor 的延迟；明确 `reactor-scheduling-delay` 是测量区间描述、不证明 epoll 缺陷。

### 架构变更
Reactor 调度边界进入观测域；Work Pool 生命周期成为可观测阶段机。

---

## v98 (302ffc3) — bounded Reactor callback attribution

### 修改内容
- **改动文件**：大改 `reactor.cpp`(+212)、`reactor.hpp`(+59)；修改 `work_pool`、`agent_observability`、`backup_observe`、`reactor_group`。
- **核心代码**：256 项 callback 环形历史 `kReactorCallbackHistory`（fd/post-high/post-normal/timer 四类，排除内部 wake/timerfd 包装）；`reactor_callback_window()` 重叠裁剪累加摘要（coverage_complete/truncated）；`reactor_post_wait_priority_observed()` 返回 observation；诊断 `reactor-long-callback`/`reactor-callback-busy`/`reactor-post-backlog`/`reactor-callback-history-truncated`。

### 修改作用
让 `reactor-scheduling-delay` 成因可归因（长回调/累积/积压/历史不足），用有界固定基数摘要表达。

### 架构变更
Reactor 首次具备有界取证能力（固定环形历史 + 入队 sequence 快照 + 重叠窗口摘要）。

---

## v99 (0fb7d84) — bounded Reactor callback source identity

### 修改内容
- **改动文件**：修改 `reactor.cpp`(+96)、`reactor.hpp`(+41)、`agent_plain_ingress`、`agent_tls_runtime`、`agent_tls_control_runtime`、`agent_exec_runtime`、`tls_reactor`、`agent_observability`、`backup_observe`、`work_pool`。
- **核心代码**：`source_kind` 字节（17 固定枚举：listener/signal/plain-control/plain-data/plain-data-lane/plain-exec/tls-control/tls-data/tls-exec/exec-pipe/work-completion/cleanup/handoff/client-io/timer 等）；`reactor_source_set_kind()`/`reactor_timer_set_kind()`/`reactor_post_priority_kind()`；会话 kind 随操作所有权切换；窗口输出 top source；诊断 `reactor-source-busy`。

### 修改作用
从"哪个 class 占用了 Reactor"细化到"哪个固定子系统占用"，全程无 FD 号/路径/函数地址/命令/载荷等敏感标识。

### 架构变更
观测新增子系统归属维度（固定枚举，随操作生命周期联动）。

---

## v100 (c009dc5) — conservative CPU attribution

### 修改内容
- **改动文件**：修改 `backup_observe.cpp`(+17)、`common.hpp`；Agent/Reactor 零改动。
- **核心代码**：CPU 证据展示 `callback_max_cpu_ns`（full-callback scope 不裁剪）；强分类前置条件（仅当 `callback_max_overlap_ns==callback_max_ns` 才允许 CPU/非 CPU 分类）；`reactor-callback-cpu-heavy`/`reactor-callback-noncpu-delay`（confirmed）；`reactor-unattributed-delay`（历史完整时 wall-callback 差）。

### 修改作用
补安全离线解读规则（缺的是保守归因，非新 Agent 字段）；反误报：部分重叠不给出 CPU-heavy/non-CPU 分类。

### 架构变更
诊断层确立"强分类需完全包含边界"的安全准则；无新 Agent 观测字段。

---

## v101 (867da08) — Reactor internal phase accounting

### 修改内容
- **改动文件**：大改 `reactor.cpp`(+226)、`reactor.hpp`(+47)；修改 `work_pool`、`agent_observability`、`backup_observe`。
- **核心代码**：第二套独立固定历史 `kReactorPhaseHistory=512`（`REACTOR_PHASE_EPOLL_WAIT/EVENT_DISPATCH/POST_DRAIN/TIMER_DISPATCH`，与 callback 历史互不挤占）；相位区间在 leaf callback 体外记录（会计域两两不相交）；双序列快照（`phase_sequence`）；**守恒不变量** `callback_wall + phase_wall + residual == reactor_wait`；诊断 `reactor-internal-phase-busy`/`reactor-residual-delay`/`reactor-phase-history-truncated`。

### 修改作用
把 v100 的"未归因补集"拆解为固定内部相位占用与真正残差；仍克制（epoll_wait wall 时间可含线程调度降级、post-drain 不证明内核缺陷）。

### 架构变更
Reactor 内部会计域完整化：leaf callback(256) + 内部相位(512) 双历史、双序列 + 残差，形成"归属+相位+残差"三层可分解观测模型——观测演进期顶点。

---

# 演进主线汇总与学习结论

## 主线 1：客户端目录队列 / dirty journal（v65-v74）

v65 确立 client catalog + 有界目录队列 + 递归 PUT 状态机骨架 → v66 引入 trusted dirty feed（选择性增量，成本降到真实脏工作集）→ v67 job 资源锁 + active_run 栅栏（并发/中断安全）→ v68 批量处理消除固定成本 → v69 fileid 反向索引（hardlink-safe）→ **v70 第一方 inotify dirty journal**（backup-dirtyd，fail-closed 健康模型）→ v71/v72 自适应元数据并行（工作负载门控）→ v73 提交即成功的 identity 校验 → **v74 leaf-sparse journal**（扫描成本从 O(目录条目数) 降到 O(变更叶子)）。

**主线本质**：让"massive namespace"下备份既正确又可承受；以实测/故障驱动代替投机优化。

## 主线 2：Agent 传输 Reactor/FSM 化（v75-v88）

v75 TREE 往返优化（能力位协商）→ **v76 事件泵（per-EXEC）** 修 child-pipe 死锁 → **v77 共享事件域（shard）** → v78 弹性会话池 + pidfd → v79 EXEC socket RX 移交 shard → **v80 非阻塞 plain ingress** → v81 control worker 让出 → v82 System-RPC 执行/传输拆分 → v83 TREE FSM 中立化 → v84 FILE FSM → v85 RESTORE FSM → v86 删最后 TREE 阻塞桥 → v87 Data Lane 迁移 + 删 service 表 → **v88 删 session pool**。

**主线本质**：plain transport 从"阻塞多线程"全面演进到"Reactor/event domain 持 socket + 有界 Work Pool 只做工作 + 小型 launch pool 只做进程 setup"；每类操作一套 transport-neutral FSM + 两个薄 adapter；阻塞桥逐一拆除（先证明替代路径达标再删死代码）。

## 主线 3：Observability 与离线诊断（v89-v101）

v89 进程内 trace 身份 + 跨执行域 span → v90 JSONL+metrics 双平面导出 → v92（含 v91）韧性 + backup-observe + 告警 → v93 session debug → v94 debug 配额 → v95 diagnose（confirmed/suspected）→ v96/v97 worker 与 completion 边界 → v98/v99 callback 历史与 source 归属 → v100 CPU 保守分类 → v101 内部相位会计（守恒分解）。

**主线本质**：从"服务器内部可观测"到"完整可归因的离线诊断证据链"；缺口驱动演进（每个版本命名前序证据缺口并由下一版本补上）；全程固定基数、有界历史、宁保守勿臆断、敏感载荷永不入日志。

## 贯穿设计原则（学习结论）

1. **协议冻结**：RSP/3 全程不变，无线协议变更靠能力位协商（CAP_TREE_DELETE_PIPELINE、FF_SESSION_DEBUG）而非新协议。
2. **schema 递增不迁移**：持久化 schema 每版自增并"拒绝旧版本"，不做就地迁移。
3. **内存/并发有界**：256/512/1024/64 等固定批量，worker 池有界懒加载，回调历史固定环形。
4. **可重放正确性不变量**："catalog commit 先于 queue completion、queue 永不领先 catalog"；"终帧需 tx_bytes()==0"。
5. **实测/故障驱动**：每个优化先量化瓶颈，每个阻塞桥拆除前先证明替代路径达标，每修复配 dedicated 回归测试。
6. **权限/隐私边界**：root-confined Agent、debug 会话策略门控 + 认证要求、敏感数据永不入观测日志。

## 与既有知识资产的关系

- T0287（已归档）覆盖 80.0.0 单版本架构；本报告覆盖完整 v65-v101 演进史，二者互补。
- 可复用知识（跨项目架构模式）已在 `knowledge/linux-epoll-eventloop/backupstream-plain-tls-ingress.md` 沉淀部分；本报告的共享事件域 shard、transport-neutral FSM、缺口驱动观测演进等可继续提炼。
