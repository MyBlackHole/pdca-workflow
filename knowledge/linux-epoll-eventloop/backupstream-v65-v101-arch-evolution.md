# backupstream v65→v101 架构演进模式（36 提交学习沉淀）

来源: records/T0295-0816-backupstream-git-history/conclusion.md

## 背景

backupstream 从 v65 到 v101（36 个 git 提交）完成四轮架构演进。本文件提炼其中
可跨项目复用的四类模式，具体版本事实见记录报告。

## 模式 1：Reactor/FSM 迁移（blocking 多线程 → 事件驱动）

演进路径：阻塞 worker 池 → per-EXEC 事件泵 → 进程级共享事件域（shard）→
transport-neutral FSM + 薄 adapter → 有界 Work Pool。

1. **按操作类型逐一迁移，而非整体重写**：TREE/FILE/RESTORE/EXEC/Data-Lane 每个
   操作单独做 FSM，先证明替代路径达标再拆除阻塞桥（每个拆桥版本配独立回归测试）。
2. **transport-neutral FSM + 双 adapter**：核心状态机与具体传输（plain/TLS）解耦，
   用窄回调 adapter 接口适配两端；换传输不重写业务逻辑。
3. **网络所有权恒驻 Reactor**：socket/管道就绪判断归事件域，Work Pool 只做有界计算，
   小型 launch pool 只做进程 setup（fork/exec 确认）。三类执行上下文严格分工：
   - Reactor/event domain：持 socket、管道就绪；
   - fs-hash/control Work Pools：不持 socket、只做有界工作；
   - 小型 EXEC launch pool：仅进程 setup，不做网络 I/O。
4. **worker 生命周期弹性化**：`--xxx-workers` 是上限而非固定值；按队列压力懒创建、
   空闲 `pthread_cond_timedwait` 超时自我退出、handoff 后立即退休。
5. **子进程事件化**：pidfd（SYS_pidfd_open）取代 waitpid 轮询；EXEC 等待同时等
   socket + pidfd + deadline；pidfd 不可用回落有限轮询。

## 模式 2：inotify dirty journal（fail-closed 增量备份）

1. **独立守护进程 + 磁盘 journal**：backup-dirtyd 用 inotify 递归 watch 维护
   SQLite dirty 表，备份进程 `prepare_backup` 捕获 cutoff_seq 后独立消费，
   进程间通过磁盘 journal 而非共享内存解耦。
2. **fail-closed 健康模型**：journal 无效（health_epoch 不匹配 / valid=false）时
   拒绝备份或回退全量，绝不冒险做部分增量——正确性优先于性能。
3. **生成/健康围栏**：`health_epoch`/`valid`/`ready`/`base_generation` 多重围栏，
   `prepare_backup` 捕获 cutoff_seq 保证一致性快照，`finish_backup` 单事务 cutover。
4. **leaf-sparse 扫描降本**：从 O(目录条目数) 全扫降到 O(变更叶子)；
   用磁盘 file_index 自动满足硬链接双父目录契约（首硬链接转换自动找旧 peer）。

## 模式 3：观测驱动架构演进（Observability 先行）

演进路径：server-local trace（三级身份）→ JSONL + Prometheus textfile 双平面
异步导出 → 离线消费诊断（backup-observe）→ Reactor 相位/回调守恒测量。

1. **本地 trace 先行**：boot/session/operation 三级身份贯穿，先有可诊断性再谈导出。
2. **双平面导出互不阻塞**：JSONL（离线深挖）+ Prometheus textfile（监控）两个
   平面异步导出，导出不阻塞业务路径。
3. **离线 diagnose 置信度分级**：confirmed/suspected 两级结论，避免把猜测当事实。
4. **守恒不变量驱动测量**：`callback_wall + phase_wall + residual == reactor_wait`
   的守恒分解，让"看不出来的忙"可归因到 callback/phase/residual 三域；
   callback 与 phase 各一套独立环形历史互不挤占。

## 模式 4：架构纪律原则（演进中的一致性约束）

1. **协议冻结、能力位协商**：无线协议变更用能力位（CAP_*）协商而非新协议，
   RSP 版本号全程不变。
2. **schema 递增不迁移**：持久化 schema 每版自增并拒绝旧版本，不做就地迁移。
3. **内存/并发有界**：固定批量上限（256/512/1024）、worker 池有界懒加载、
   回调历史固定环形；宁可截断历史也绝不放飞内存。
4. **可重放正确性不变量**："catalog commit 先于 queue completion、queue 永不
   领先 catalog"；"终帧需 tx_bytes()==0"——不变量编码进协议与状态机。
5. **实测/故障驱动**：每个优化先量化瓶颈，每修复配 dedicated 回归测试。
6. **dead-code 化而非物理删除**（文档-代码漂移陷阱）：架构收尾期的"删除"在 git 中
   表现为停止编译接线、文件保留为死代码（agent_tree_legacy/agent_plain_control/
   agent_session_pool 均如此）。阅读历史须以编译产物为准，而非源文件存在性。

## 验收信号

- 阻塞桥拆除后，对应操作无阻塞线程且延迟显著下降（v75→v88 各拆桥版本量化数据见报告）。
- 高并发 EXEC 下线程数不随并发放大（24 并发 EXEC peak 25→6）。
- 观测可归因：任何 reactor 忙均能分解为 callback/phase/residual。