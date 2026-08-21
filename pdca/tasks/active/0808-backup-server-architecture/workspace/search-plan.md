# 搜索计划 — 备份工具与服务端程序架构调研

任务：T0218-0808-backup-server-architecture
范围：全量备份生态 + 服务端程序架构
产出：research-report.md（调研）+ design.md（设计）

## 子问题 1：备份工具架构（本地/增量/去重）
- 关键词（中英）：rsync 架构 rsync algorithm; borg backup architecture dedup chunking; restic design dedup content-addressable storage; bacula bareos architecture daemon; amanda backup architecture
- 目标：rsync（delta 算法）、Borg（可变分块+去重+压缩）、Restic（内容寻址+去重）、Bacula/Bareos（C/S 守护进程架构）、Amanda（多客户端调度）

## 子问题 2：云备份/对象存储备份工具
- 关键词：rclone architecture; duplicity design encryption; restic S3 backend; cloud backup architecture object storage
- 目标：Rclone（统一对象存储封装）、Duplicity（增量+加密卷）、云备份（S3/对象存储分片上传）

## 子问题 3：快照/块级备份（文件系统层）
- 关键词：ZFS send receive architecture snapshot; LVM snapshot backup; btrfs send receive; block-level backup dedup
- 目标：ZFS send/receive（增量快照流）、LVM（块快照）、btrfs send（增量流）、块级备份与去重

## 子问题 4：服务端程序架构（网络 IO / 并发模型）
- 关键词：high performance server architecture epoll reactor; io_uring server design; nginx architecture worker process; redis single thread model event loop; netty reactor model
- 目标：epoll/reactor 模型、io_uring、多进程/多线程/事件驱动、Nginx/Redis/Netty 架构模式

## 子问题 5：存储/去重/索引/调度设计
- 关键词：content defined chunking CDC dedup; backup deduplication index design; backup scheduling throttle bandwidth; point in time recovery design
- 目标：内容定义分块（CDC）、去重索引、备份调度与节流、PITR 恢复设计

## 子问题 6：完整备份产品参考（综合）
- 关键词：backup software architecture overview comparison; enterprise backup architecture design
- 目标：综合性架构综述，提炼 5 大子系统（客户端/服务端/存储/调度/恢复）设计模式
