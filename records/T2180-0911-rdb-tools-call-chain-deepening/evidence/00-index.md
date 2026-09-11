# 6.2.0.0 调用链索引与需求路由

事实基线：`/home/black/Public/aio/aio-tools/6200/release`（产品 6.2.0.0）。本索引只路由到现有五份版本地图；没有 23 个独立工具页。每次先定工具和操作，再按章节读取，最后回到源码复核 `path:symbol`。

## 版本与状态约定

本版只描述 6.2.0.0。状态含义：`current`=仓内现行运行链；`external`=对外交付、消费方在仓外；`operator`=人工运维入口；`build-only`=只有构建装配证据；`isolated`=实现存在但生产链不可达；`deprecated`=源码残留/不可达旧链。一个工具可同时具有多个状态，例如 `rpc-keygen` 是 `operator + build-only`。

## 工具 → 操作 → 调用链章节

| # | 工具 | 公开操作/分发 | 状态 | 调用链 |
|---:|---|---|---|---|
| 1 | `fs-cli` | 21 个 method：list/snapshot/merge/backup/restore/source/trackup/exclude/config/ioctl | current client | [01 §10.1/§10.3–§10.6](01-fs-backup-knowledge-map/6.2.0.0.md#101-fs-cli-入口与全部-method-清单) |
| 2 | `fsdeamon` | 8901 `FS_*`、全局 source 分发、每 source 分发、helper JSON | current service | [01 §10.2–§10.5](01-fs-backup-knowledge-map/6.2.0.0.md#102-fsdeamon-启动协议分发与返回) |
| 3 | `fsbackup_tools` | block/done/ioctl/ioctl_meta/fs_meta | operator | [01 §11](01-fs-backup-knowledge-map/6.2.0.0.md#11-fsbackup_tools-逐子命令调用链) |
| 4 | `fsbackup.ko` | open/release/read/ioctl；10 个 ioctl 常量（9 个 case group）；文件事件 hook | current kernel runtime | [01 §12](01-fs-backup-knowledge-map/6.2.0.0.md#12-fsbackupko-内核入口调用链) |
| 5 | `makeFsbackup` | 卸载旧模块、解包、编译、安装、验版、装载 | operator installer | [01 §13](01-fs-backup-knowledge-map/6.2.0.0.md#13-makefsbackup-装载链) |
| 6 | `aio-speed` | 新 backup/restore/meta 操作；旧 download/upload/tree/rsync/nc/cmd/config | current client | [02 §9.1–§9.4](02-rpc-rdbcomm-knowledge-map/6.2.0.0.md#9-aio-speed-aio-speedd-逐操作调用链) |
| 7 | `aio-speedd` | 19 个 `MT_*`、19 个 persistent-connection opcode、unix config | current service | [02 §9.2–§9.5](02-rpc-rdbcomm-knowledge-map/6.2.0.0.md#9-aio-speed-aio-speedd-逐操作调用链) |
| 8 | `rpc-keygen` | dba/ops 时效 key 生成 | operator + build-only | [02 §10](02-rpc-rdbcomm-knowledge-map/6.2.0.0.md#10-rpc-keygen-调用链) |
| 9 | `rdbcomm` | download/upload/cmd/register/unregister/start/stop/list | external client | [02 §11.1–§11.3](02-rpc-rdbcomm-knowledge-map/6.2.0.0.md#11-rdbcomm-rdbcommd-逐操作调用链) |
| 10 | `rdbcommd` | INIT/OPEN/CLOSE/READ/WRITE/模块/cmd handler | external service | [02 §11.2–§11.4](02-rpc-rdbcomm-knowledge-map/6.2.0.0.md#11-rdbcomm-rdbcommd-逐操作调用链) |
| 11 | `s3-tool` | upload/download/list/S3-to-S3 | external/operator | [04 §9](04-s3-xbsa-knowledge-map/6.2.0.0.md#9-s3-tool-逐操作调用链) |
| 12 | `s3file` | get/up/rm/upload/check/destroy snapshot | external/operator | [04 §10](04-s3-xbsa-knowledge-map/6.2.0.0.md#10-s3file-逐操作调用链) |
| 13 | `s3mount` | mount-file/mount-snapshot；两套 FUSE callback 表 | external/FUSE | [04 §11](04-s3-xbsa-knowledge-map/6.2.0.0.md#11-s3mount-fuse-调用链) |
| 14 | `afsd` | FUSE callback 表 | external/FUSE service | [04 §12](04-s3-xbsa-knowledge-map/6.2.0.0.md#12-afsd-fuse-调用链) |
| 15 | `afs-cli` | 18 个 method；6 个网络 method 未闭合到 afsd | external client | [04 §13](04-s3-xbsa-knowledge-map/6.2.0.0.md#13-afs-cli-逐-method-调用链) |
| 16 | `xbsa64` | 16 个 XBSA ABI | external shared ABI | [04 §14](04-s3-xbsa-knowledge-map/6.2.0.0.md#14-xbsa64-导出-abi-调用链) |
| 17 | `rch-tools` | data/xlog 两类解析 | external/operator | [04 §15](04-s3-xbsa-knowledge-map/6.2.0.0.md#15-rch-tools-逐类型调用链) |
| 18 | `sbt` | OceanBase SBT2 init/backup/read/write/info/remove/end | external shared ABI | [04 §16](04-s3-xbsa-knowledge-map/6.2.0.0.md#16-sbt-filetransferagent-调用链) |
| 19 | `FileTransferAgent` | 6 个 activeio opcode handler | external service | [04 §16.2](04-s3-xbsa-knowledge-map/6.2.0.0.md#162-filetransferagent-对端分发) |
| 20 | `dmsbtex` | 13 个 DMSBT ABI | external shared ABI | [04 §17](04-s3-xbsa-knowledge-map/6.2.0.0.md#17-dmsbtex-dm-ftp-调用链) |
| 21 | `dm-ftp` | 6 个 `CMD_*` handler | external service | [04 §17.2](04-s3-xbsa-knowledge-map/6.2.0.0.md#172-dm-ftp-对端分发) |
| 22 | `bwlimit_tools` | meta/reset/set_bandwidth/version | operator；library current | [03 §9](03-libs-knowledge-map/6.2.0.0.md#9-bwlimit_tools-逐子命令调用链) |
| 23 | `tls-keygen` | create/ca/sign/version/help | operator | [03 §10](03-libs-knowledge-map/6.2.0.0.md#10-tls-keygen-逐子命令调用链) |

## 需求类型 → 主调用链

| 需求信号 | 主链 | 必须联查 |
|---|---|---|
| 文件快照、备份、恢复、source 管理 | 01 §10 | FS_* 两端；helper JSON；备份数据另跨 6611 到 02 §9 |
| 监控目录、排除目录、日志切换 | 01 §10.3/§12 | `dev_ioctl.h` 三份常量 + rpc `MT_EXECUTE_IOCTL_FSBACKUP` |
| 远端命令、文件/块传输、断点/批量传输 | 02 §9 | 短会话 `MT_*` 与 persistent opcode 不能混写 |
| rdbcomm 文件与模块通道 | 02 §11 | 消息长度前缀、INIT 鉴权、DATA/STATUS/HANDLE 返回 |
| S3 普通对象操作 | 04 §9/§10/§13 | 选定实际 fork 的 `S3Service`，不要跨目录推定同源 |
| S3 快照上传/销毁/挂载 | 04 §10–§13 | bitmap/对象清单/FUSE callback 与 SDK 边界 |
| XBSA/SBT 数据库介质 | 04 §14/§16/§17 | 先按 ABI 签名选家族；仓外数据库调用者需真实联调 |
| 鉴权 key 或 TLS 证书 | 02 §10 / 03 §10 | key 生成端与 rpc/rdbcomm 校验端；证书输出与 `tls_cert` 消费路径 |
| 构建、版本或安装落点 | [05 §8](05-build-release-knowledge-map/6.2.0.0.md#8-target-运行调用链-安装交付映射) | 必须再读对应运行链，不能以 target 代替调用链 |

## 关键跨端契约

- `fs-cli ↔ fsdeamon`：`fs-backup/public/fs_service_proto.h` 的 `FS_*`，生产端 `fs-backup/fsclient/main.cpp:handlers`，消费端 `fs-backup/fsdeamon/fs_service.cpp:FsService::CLIService`。
- `fsdeamon ↔ fsbackup.ko`：用户态 `fs-backup/fsdeamon/fs_kernel_sync.cpp:call_dev_ioctl`（可经 rpc 转发）与内核 `fsbackup_kernel_4.x/device/fsbackup_driver.c:fsbackup_dev_ioctl`。
- `aio-speed ↔ aio-speedd`：`rpc/rpc-protocol.h` 的 `MT_*` 与 `rpc/rpc-server.cpp:RpcService::StartRPCServiceWoker`；persistent 子协议见 `rpc/rpc.h:NEW_CONN_TMP_*` 与 `rpc/rpc-server.cpp:new_conn`。
- `rdbcomm ↔ rdbcommd`：`rdbcomm/rdbcomm.h` 的操作码，客户端 `rdbcomm/client.c` 与服务端 `rdbcomm/server.c:handlers`。
- `afs-cli ↔ afsd`：客户端确有长度前缀 JSON method，但 6.2.0.0 `afsd` 未找到 TCP listen/handler，网络链显式未闭合。
- 外部 ABI：自带 test/simulator 只证明示例消费，不能替代真实数据库进程联调。
