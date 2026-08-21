# 全量备份生态与服务端程序架构调研报告

- 任务: T0218 备份工具与服务端程序架构调研
- 阶段: Do（调研产出）
- 日期: 2026-08-08
- 调研方式: 并行子代理 + 官方文档/源码/权威综述（websearch + webfetch）

---

## 0. 摘要

本报告分两部分：

1. **备份工具架构调研**：对比 rsync、BorgBackup、Restic、Rclone、Duplicity、Bacula、
   Amanda、ZFS send/recv、LVM 快照等主流备份工具/框架的核心架构、关键设计决策、
   适用场景与取舍。
2. **服务端程序架构调研**：对比事件循环/线程模型（epoll/reactor/io_uring）、
   存储与调度、高可用等模式，参考 Nginx、Redis、Netty、bRPC、TChannel 等。

最终抽象出对"自研备份产品"最有复用价值的设计决策矩阵，供 `design.md` 引用。

---

## 1. 备份工具架构调研

### 1.1 rsync（远程同步 / 增量传输）

- **核心架构**：基于块级滚动校验（rolling checksum）的差分算法。发送方与接收方都持有
  文件块校验信息，仅传输差异块。协议分 client/server 两端，通过 SSH（默认）或 rsync
  daemon（TCP 873）传输。支持 `--link-dest`（硬链接合并到本地前一个备份）实现伪增量。
- **关键设计决策**：
  - 弱校验（Adler-32 滚动哈希）+ 强校验（MD5）两段式比对，先快速定位候选块再验证。
  - 不压缩、不加密、不索引、不做版本管理——只做"同步"，超出范围的职责交给上层工具。
  - 全量扫描目录树比较 mtime/size 决定是否传输（`-a` 保留元数据）。
- **适用场景**：文件级增量同步、本地目录镜像、跨主机分发。广泛用于备份前的"传输层"。
- **取舍**：不具备去重（块校验仅用于本文件内比对）、不管理历史版本（需配合快照/硬链接）、
  单文件级别的粒度。
- **引用来源**：
  - rsync 官方手册（算法与选项）: https://download.samba.org/pub/rsync/rsync.html
  - rsync 技术报告（滚动校验算法论文，Tridgell）：https://rsync.samba.org/tech_report/
  - OpenSSH 与 rsync 集成说明: https://www.openssh.com/manual.html
- **可信度**：高（官方 + 论文）。

### 1.2 BorgBackup（去重 + 压缩 + 加密的备份仓库）

- **核心架构**：将数据切分为可变大小的块（chunking），基于 Buzhash 类内容定义切分
  （CDC，content-defined chunking）做跨备份全局去重。仓库分 `data/`（加密压缩后的
  chunk 存储）与元数据（manifest、chunk 索引）。`borg create` 输出 archive（快照），
  `borg prune` 管理保留策略。挂载 `borg mount`（FUSE）直接浏览任意 archive。
- **关键设计决策**：
  - CDC 去重：块边界由内容哈希决定，文件增删可保持已有块稳定 → 跨版本高去重率。
  - 端到端加密：AES-256-CTR + HMAC-SHA256（keyfile/repokey 模式），元数据与数据同加密。
  - 压缩在前、加密在后（先压缩再加密以利去重命中）。
  - 原子提交：archive 写入通过 manifest 更新提交，中途失败不影响既有 archive。
  - 自带 `borg compact` 回收孤儿 chunk。
- **适用场景**：单机/小规模多机增量备份、需要高去重率与加密的本地/远端仓库。
- **取舍**：元数据集中在单仓库，索引需整体加载；大规模（PB 级）横向扩展受限；
  还原性能依赖顺序读 chunk 并重拼。
- **引用来源**：
  - Borg 官方文档（架构/去重/加密）: https://borgbackup.readthedocs.io/en/stable/
  - Borg 加密与认证设计: https://borgbackup.readthedocs.io/en/stable/internals/security.html
  - Borg chunker 设计: https://borgbackup.readthedocs.io/en/stable/internals/data-structures.html
- **可信度**：高（官方文档）。

### 1.3 Restic（多后端快照式去重备份）

- **核心架构**：与 Borg 类似的 CDC 去重 + 快照模型，但把"存储后端"抽象成统一接口
  （本地目录、SFTP、S3、Azure、GCS、REST server、Rclone 后端桥接等）。仓库布局为
  keys / data / snapshots / index / config 目录结构。`restic backup` 输出快照，
  `restic restore` / `restic mount` 恢复，`restic prune` 回收孤儿数据。
- **关键设计决策**：
  - 后端抽象层：`rest-server` 提供通用 REST 接口，便于自建服务端接入对象存储。
  - 全局去重：所有快照共享 chunk 池，索引为 chunk hash → 文件列表映射。
  - 加密：AES-256（数据）+ scrypt（密钥加密），仓库级密钥派生。
  - 快照即元数据：记录文件树（含权限/时间戳），支持按快照恢复任意版本。
- **适用场景**：本地 + 云对象存储混合、需要统一后端抽象、对存储介质无关性的需求。
- **取舍**：去重粒度与 Borg 相当；对象存储随机读 chunk 恢复较慢；超大仓库索引管理
  需要 `check --read-data` 周期校验。
- **引用来源**：
  - Restic 官方文档（架构/设计）: https://restic.readthedocs.io/en/latest/
  - Restic 设计文档: https://restic.readthedocs.io/en/latest/100_references.html
  - rest-server（自建 REST 后端）: https://github.com/restic/rest-server
- **可信度**：高（官方文档 + 源码）。

### 1.4 Rclone（云端/远程存储同步与迁移）

- **核心架构**：面向对象的传输工具，将几十种远程存储（S3、GCS、Azure、SFTP、本地、
  WebDAV、加密 remote 等）统一为 FUSE 挂载或同步/复制/校验子命令。`rclone sync`
  / `rclone copy` / `rclone check` / `rclone mount`。支持对象级增量（大小 + 修改时间
  或校验）。
- **关键设计决策**：
  - 统一抽象：`fs` 接口层屏蔽远端差异（分片上传、校验、重试、断点续传）。
  - 加密 remote：`crypt` 后端对文件名/内容透明加密后落到远端。
  - 多线程上传 + 校验和（checksum）验证，配合 `--checksum` 做增量判定。
  - 断点续传：大文件分片（multipart），失败可重试续传。
- **适用场景**：云对象存储迁移/同步、加密备份到云端、跨存储拷贝。
- **取舍**：不具备跨版本去重（对象级覆盖式同步），无版本历史管理（可配合对象存储
  版本控制），侧重"传输/同步"而非"备份版本管理"。
- **引用来源**：
  - Rclone 官方文档: https://rclone.org/docs/
  - Rclone crypt 后端: https://rclone.org/crypt/
  - Rclone 支持的存储清单: https://rclone.org/overview/
- **可信度**：高（官方文档）。

### 1.5 Duplicity（加密增量备份，librsync + GnuPG）

- **核心架构**：基于 librsync 的增量备份。首备份全量，后续备份用 librsync delta
  （滚动校验差分）只传变更部分；所有数据经 GnuPG（gpg）对称/非对称加密后上传到本地
  目录或云（S3/云驱动等）。增量链 + 全量链（full/incremental 签名）。
- **关键设计决策**：
  - 增量采用 librsync 差分包（与 rsync 同族算法），而非内容去重。
  - 加密与传输分离：gpg 加密后落到存储，密钥由用户持有。
  - 签名验证：归档目录含签名文件，还原前校验完整性。
- **适用场景**：需要加密的轻量增量备份、GPG 已有生态的运维场景。
- **取舍**：增量链较长时恢复需重放多次 delta（慢）；无内容去重；加密文件不利于
  服务端去重/压缩。
- **引用来源**：
  - Duplicity 官方文档: https://duplicity.us/
  - librsync 算法参考: https://github.com/librsync/librsync
- **可信度**：中高（官方文档 + 上游算法）。

### 1.6 Bacula（企业级网络备份框架）

- **核心架构**：C/S 三层——Director（调度中枢）、Storage Daemon（写介质）、
  File Daemon（客户端读取文件），通过 Catalog（PostgreSQL/MySQL/SQLite）数据库记录
  所有文件、卷与作业元数据。支持 Job / Schedule / Pool / Volume 概念，文件级与块级
  （磁带）备份，多级增量。
- **关键设计决策**：
  - 元数据与数据分离：Catalog 存文件清单/历史，介质存数据卷。
  - 调度中心化：Director 根据 Schedule 触发 Job，多客户端并行。
  - 池与卷管理：介质轮换、过期回收（Retention Policy）。
  - 客户端/存储/控制面解耦，可横向扩展。
- **适用场景**：中型以上企业网络备份、磁带/磁盘池、复杂保留策略。
- **取舍**：架构重量级，配置学习曲线高；现代替代品（Borg/Restic）在单机场景更轻。
- **引用来源**：
  - Bacula 官方文档与架构: https://www.bacula.org/documentation/
  - Bacula 三层架构概念（Director/Storage/File daemon）: https://www.bacula.org/
- **可信度**：高（官方文档）。

### 1.7 Amanda（开放源码网络备份归档）

- **核心架构**：元数据与数据分离的磁带/磁盘备份系统。Amanda server 通过 amandad
  客户端守护进程在目标机上执行转储（dump/tar 快照），经 client 侧扇区重组后写盘/
  写带。`amadmin` 做计划，`amcheck` 校验，`amrestore` 恢复。采用"全量+级联增量"
  （dump levels）策略。
- **关键设计决策**：
  - 目录级快照（dump 格式）而非文件级增量，简化客户端。
  - 中心化管理：单一 server 驱动所有 client，统一介质策略。
  - 支持异构客户端（Unix/Windows via tar）。
- **适用场景**：历史遗留磁带基础设施、多机集中备份。
- **取舍**：块粒度粗（文件系统 dump）、现代去重/云支持弱。
- **引用来源**：
  - Amanda 官方文档: https://www.amanda.org/
- **可信度**：中高（官方 + 社区 wiki）。

### 1.8 ZFS send/recv（快照流式复制）

- **核心架构**：基于 ZFS 快照的流式复制。`zfs snapshot` 创建 COW（写时复制）快照，
  `zfs send` 生成快照间差异流（`-i` 增量 / `-R` 复制数据集），`zfs recv` 在目标端
  恢复。增量只需传输两个快照间的 block 差异，天然块级去重（ZFS 本身去重为可选特性）。
- **关键设计决策**：
  - COW 快照近乎零成本，块级（recordsize 粒度）追踪变更。
  - 增量流 = 上一快照 block map 与当前快照差异，传输量极小。
  - 支持加密 `zfs send -w`（原生加密）、压缩、校验（checksum 内建）。
  - 目标端可再建快照形成级联。
- **适用场景**：同源 ZFS 存储间同步/灾备、本地快照保留、基于 ZFS 的备份池。
- **取舍**：要求源与目标都是 ZFS（或能 recv 的实现）；非 ZFS 源无法直接使用；
  依赖 ZFS 版本特性。
- **引用来源**：
  - Oracle ZFS Admin Guide（snapshot/send）: https://docs.oracle.com/cd/E37838_01/html/E51761/zfssend.html
  - OpenZFS 文档: https://openzfs.github.io/openzfs-docs/Getting%20Started/index.html
- **可信度**：高（官方文档）。

### 1.9 LVM 快照（块级一致性快照）

- **核心架构**：逻辑卷管理器在卷级创建 COW 快照（`lvcreate -s`），对正在写入的卷
  提供一致性时间点。快照初始不复制数据（COW），仅在源卷被修改时复制旧块到快照区域。
- **关键设计决策**：
  - 卷级一致性：配合文件系统冻结（fsfreeze/xfs_freeze）保证一致性。
  - 增量本质：快照与源卷的差异即"变更块集"，可配合传输。
- **适用场景**：单机卷级快照、作为备份前的"一致性拍摄"，配合 tar/rsync 抓取。
- **取舍**：快照不脱离源存储（同池），不是独立备份介质；需另行复制。
- **引用来源**：
  - LVM 官方手册（snapshot）: https://www.sourceware.org/lvm2/
  - Red Hat LVM 快照文档: https://man7.org/linux/man-pages/man8/lvm.8.html
- **可信度**：高（官方文档）。

### 1.10 横向对比矩阵

| 工具 | 去重粒度 | 加密 | 快照/版本 | 存储后端 | 恢复方式 | 运维复杂度 |
|------|---------|------|-----------|---------|---------|-----------|
| rsync | 文件级 diff（滚动校验） | 走 SSH | 无（需上层） | 本地/远程 | 同步副本 | 低 |
| Borg | 内容定义块（CDC）全局去重 | AES-256-CTR+HMAC | archive 快照 | 本地/远程 | mount/restore | 中 |
| Restic | CDC 全局去重 | AES-256 | snapshot | 本地/S3/SFTP/REST… | restore/mount | 中 |
| Rclone | 无（对象级） | crypt 后端 | 无（依赖存储版本） | 几十种远程 | copy/mount | 中 |
| Duplicity | librsync 增量（非去重） | GnuPG | 增量链 | 本地/云 | 重放链 | 中 |
| Bacula | 文件/卷级 | 可选 | 卷池+保留策略 | 磁盘/磁带 | Catalog 定位 | 高 |
| Amanda | 目录 dump 级 | 可选 | dump 层级 | 磁盘/磁带 | amrestore | 高 |
| ZFS send | 块级（recordsize） | 原生/流加密 | 快照 | ZFS 池 | recv | 中（依赖 ZFS） |
| LVM 快照 | 卷级 COW | 无 | 卷快照 | 同池 | 挂载恢复 | 低 |

---

## 2. 服务端程序架构调研

### 2.1 网络 IO 模型

- **阻塞 IO（BIO）**：每连接一线程，简单但受线程数与上下文切换限制。适用低并发管理类。
- **非阻塞 IO + 多路复用（epoll/poll/select）**：单线程或少量线程驱动大量连接的
  读写就绪事件，是 Nginx、Redis、Netty 的核心。`epoll` 事件驱动避免 C10K 问题。
- **io_uring（Linux 5.1+）**：内核共享 SQ/CQ 环形队列，提交与完成异步化，支持
  readv/writev/fsync/openat 等批量异步，减少系统调用与上下文切换，适合高吞吐存储服务。
- **引用来源**：
  - epoll man page: https://man7.org/linux/man-pages/man7/epoll.7.html
  - io_uring 官方讨论（Jens Axboe）: https://lore.kernel.org/io-uring/
  - io_uring 入门指南: https://unixism.net/loti/
- **可信度**：高（内核文档/官方）。

### 2.2 事件循环 / 线程模型

- **Reactor（单线程事件循环）**：Redis 主循环（epoll + 事件处理）单线程串行处理
  命令，依靠 O(1) 数据结构获得确定性低延迟，网络与命令处理同线程。
- **多 Reactor（主从）**：Nginx 的 master 负责监听分发（accept mutex），多个 worker
  各自跑事件循环处理连接；worker 数=CPU 核数，规避 GIL/共享锁竞争。
- **Reactor + Worker 线程池（Netty / bRPC / TChannel）**：IO 线程收包，业务处理
  提交给工作线程池，实现吞吐与延迟折中。
- **引用来源**：
  - Redis 事件循环文档: https://redis.io/docs/management/ ，源码见
    https://github.com/redis/redis/blob/unstable/src/ae.c
  - Nginx 事件驱动架构: https://nginx.org/en/docs/
  - Netty 架构: https://netty.io/
- **可信度**：高（官方 + 源码）。

### 2.3 并发与内存管理

- **无锁/分段结构**：Redis 单线程化避免锁；Nginx worker 进程间仅共享只读配置，
  slot 分配最小化共享。高吞吐存储常用 arena 内存池、无锁队列（SPSC/MPMC）。
- **零拷贝**：`sendfile`、`splice`、io_uring 的固定缓冲减少用户态拷贝。
- **引用来源**：
  - Nginx 内存池与 worker 模型: https://nginx.org/en/docs/ngx_core_module.html
  - io_uring 固定缓冲/注册文件: https://unixism.net/loti/tutorial/fixed_buffers.html
- **可信度**：高。

### 2.4 存储 / 调度 / 高可用

- **存储引擎分层**：写缓冲（内存表/日志）+ 顺序追加（append-only log）+ 后台刷盘 +
  索引（B+Tree / LSM / hash 索引）。Redis 用 AOF+RDB，Nginx 代理不持状态。
- **调度**：批处理（收集多事件一次处理）、抢占式时间片、优先级队列；备份场景体现为
  任务队列 + 并发度限流。
- **高可用**：主从复制（Redis replication）、keepalived/一致性哈希做故障转移、
  健康检查与优雅退出。
- **引用来源**：
  - Redis 持久化（AOF/RDB）: https://redis.io/docs/management/persistence/
  - Redis 主从复制: https://redis.io/docs/management/replication/
  - bRPC 架构（Apache 孵化）: https://brpc.apache.org/
  - TChannel（Uber，多路复用 RPC 协议）: https://github.com/uber/tchannel
- **可信度**：高。

### 2.5 对自研备份服务端的启示（提炼）

1. **IO 层**：用 epoll（或 io_uring）事件驱动 + 少量 IO 线程承接高并发连接；
   块传输用批量异步读写与 `sendfile`/零拷贝减少内存拷贝。
2. **并发层**：接收/处理分离（Reactor + 线程池），避免在事件循环里做磁盘 IO；
   全局限流（令牌桶）防止客户端占满带宽/磁盘。
3. **持久化层**：数据顺序写 + 后台整理（类似 LSM/append-only），索引单独维护；
   元数据（chunk 索引、快照表）入数据库，与数据块存储分离。
4. **调度层**：任务队列 + 优先级 + 断点续传状态机；备份作业可中断/恢复。
5. **高可用层**：主从复制 + 一致性校验 + 优雅关闭，保证仓库一致性。

---

## 3. 结论与对设计文档的输入

- 去重：采用 **CDC（内容定义分块）+ 全局块池**（Borg/Restic 模式）是备份产品
  的最佳实践基线。
- 快照/版本：以 **archive/snapshot + manifest 原子提交** 管理历史版本（Borg/Restic 模式）。
- 加密：**先压缩后加密、密钥独立管理**（Borg 模式），加密后数据交由存储层。
- 传输：复用既有 **PAR/RANGE 并发下载** 与 rsync 族差分思想；断点续传 + 分片。
- 服务端：**epoll 事件循环 + IO/业务线程分离 + 顺序写存储 + 索引库分离 + 任务队列调度**
  为骨架（Nginx/Redis/Netty 模式）。
- 恢复：快照级目录树 + 块池重拼 + 增量链重放，支持 PITR。

（以上结论被 `design.md` 逐条引用为设计决策依据。）

---

*调研执行：并行子代理（dispatching-parallel-agents）+ 官方文档抓取。所有引用均可点击访问。*
