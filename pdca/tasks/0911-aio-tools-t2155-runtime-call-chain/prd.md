# 补充 T2155 的 6200 工具运行时调用链

## 目标

在 T2155 的调用链协议基础上补齐 6200/release 中实际存在但索引表达不足的运行时链路，保持 T2154 的 6.2.0.0 版本基线和现有分册结构。

## 范围

- 在 01 分册补充 `fsdeamon -> BackupHelper -> backup.sock -> 本地快照/meta/data` 链。
- 在 01 分册补充 `fs-cli method -> FS_* -> fsdeamon handler` 完整对照入口。
- 在 02/01 分册明确 `rdbcomm/rdbcommd=6610` 与 `aio-speedd=6611` 的边界。
- 在 00-index/05 分册补充根 xmake 聚合、service/soft-link、`makeFsbackup` 内核装配链，并区分“构建交付存在”和“仓内业务调用存在”。
- 将每个可交付工具作为独立调用链入口登记，不再只按五个子系统大类概括。至少覆盖：`fs-cli`、`fsdeamon`、`fsbackup_tools`、`makeFsbackup`、`aio-speed`、`aio-speedd`、`rpc-keygen`、`rdbcomm`、`rdbcommd`、`s3-tool`、`s3file`、`s3mount`、`afsd`、`afs-cli`、`xbsa64`、`rch-tools`、`sbt`、`FileTransferAgent`、`dmsbtex`、`dm-ftp`、`bwlimit_tools`、`tls-keygen`。
- 每个工具统一记录“入口参数/子命令 → 分发函数或 target → 核心实现 → 输出、文件、socket、端口或安装副作用 → 仓内调用方/外部消费者状态”。

## 非目标

不修改 C/C++/Go 行为，不重新审计 T2154 五份分册的全部代码事实，不把对外交付模块误判为仓内业务消费者。

## 验收标准

- [ ] AC-1：01 分册给出 BackupHelper 的进程、socket、JSON method、快照结果落盘链，并含源码 `file:line` 锚点。
- [ ] AC-2：01 分册给出 fs-cli method、FS_*、服务端分发入口和未映射项，覆盖 `main.cpp:506-529` 的现行表。
- [ ] AC-3：端口表区分 rdbcomm/rdbcommd 6610、aio-speedd 6611、fsdeamon 8901，并注明默认值来源。
- [ ] AC-4：00-index/05 分册补充 root xmake、`fsbackup.ko`、`fsbackup_tools`、运行时 service/soft-link、`makeFsbackup` 装配链，并明确 build-only 与 runtime-consumer 两种状态。
- [ ] AC-5：00-index 或 05 分册提供完整可交付工具清单，至少独立列出 `fsbackup.ko`、`fsbackup_tools` 及全部用户确认的工具；清单中的每个工具都有独立调用链锚点和状态标记；不得以“其他工具”合并隐藏入口。
