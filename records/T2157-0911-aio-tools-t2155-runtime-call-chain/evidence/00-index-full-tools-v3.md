# 文档索引与需求路由矩阵

本文件是 rdb-tools-design 的路由核心:先按 §〇 选定版本文件,再按「需求类型」定位分册,再按「能力 × 任务链」定位章节,最后按「行号」精准 Read,避免全量加载。

> **第一件事:先定版本,再读地图**。代码地图(01–05)以 aio-tools 版本目录为基线、随代码版本变化。任何涉及 01–05 的定位,先按 §〇 选定版本文件,并把判定结论写进输出。

## 〇、版本路由(先读,每次必做)

### 0.1 版本地图的文件组织

- 01–05 各为一个目录,目录内**每个版本一个文件**:`01-fs-backup-knowledge-map/<tag>.md` 等
- 同一子系统的版本文件保持**同一章节编号骨架**;该版本未引入的能力,章节保留并注明「该版本未引入」——跨版本章节号不漂移
- 已建版本梯:**6.2.0.0**(目录 `6200/release`)

### 0.2 三步选定版本文件

1. **取代码基线版本**:代码在版本目录内时,以目录名为准(如 `6200` 即 6.2.0.0);用户/环境告知产品版本时以告知为准
2. **向下取底**:取 ≤ 该版本的最近已建版本,读其文件。例:基线 6.1.x → 暂无更低版本,按第 3 步处理
3. **无更低版本 / 非 6.2.0.0**:读 `6.2.0.0.md`,并在定位结论注明「代码版本与地图基线不一致,以代码实证为准」

### 0.3 判定结论写入输出

定位结论开头注明 `<子系统> @ <基线版本> → <版本文件>`(例:`fs-backup @ 6.2.0.0 → 01/6.2.0.0.md`),供评审环节复核。

### 0.4 已建版本清单(2026-09-10 起版本化)

| 版本 | 01 fs-backup | 02 rpc-rdbcomm | 03 libs | 04 s3-xbsa | 05 build-release |
|---|---|---|---|---|---|
| 6.2.0.0 | ✅ | ✅ | ✅ | ✅ | ✅ |

## 一、各分册章节速查(含行号,支持 offset 定位)

> 01–05 的行号表以 6.2.0.0 版为基准;其余版本章节编号一致、行号随版本不同。

### 01-fs-backup-knowledge-map/6.2.0.0.md(190 行;版本化目录,每版本一文件,其他版本见 §〇)

| 章节 | 内容 | 行号 |
|---|---|---|
| §1 | 模块组织总览(fsclient/fsdeamon/public/kernel/doc) | 13-29 |
| §2 | 能力总览(能力 → 代码 → 使用方) | 31-45 |
| §3 | 核心任务链(3.1 快照 / 3.2 备份 / 3.3 恢复 / 3.4 删除 / 3.5 监控增删 / 3.6 内核监控) | 47-113 |
| §4 | 协议契约(method 字符串 / FS_ 命令字 / ioctl 字 / 端口与路径) | 115-143 |
| §5 | 新能力如何复用或扩展 | 145-164 |
| §6 | 影响范围 | 166-176 |
| §7 | 孤岛与冗余 | 178-186 |
| §8 | 分支差异 | 188-190 |

### 02-rpc-rdbcomm-knowledge-map/6.2.0.0.md(186 行;版本化目录,每版本一文件,其他版本见 §〇)

| 章节 | 内容 | 行号 |
|---|---|---|
| §1 | 模块组织总览(rpc/rdbcomm/rpc-keygen) | 13-35 |
| §2 | 能力总览(会话/持久连接/鉴权/块传输/rdb 模块) | 37-52 |
| §3 | 核心任务链(3.1 短会话 / 3.2 持久连接 / 3.3 服务端分发 / 3.4 rdbcomm / 3.5 key 生成) | 54-109 |
| §4 | 协议契约(端口常量 / MT_ 消息号 / 帧与握手 / timed_key / 超时重试) | 111-146 |
| §5 | 新能力如何复用或扩展 | 148-160 |
| §6 | 影响范围 | 162-171 |
| §7 | 孤岛与分叉 | 173-182 |
| §8 | 分支差异 | 184-186 |

### 03-libs-knowledge-map/6.2.0.0.md(139 行;版本化目录,每版本一文件,其他版本见 §〇)

| 章节 | 内容 | 行号 |
|---|---|---|
| §1 | 模块组织总览(文件组 × 能力域) | 13-35 |
| §2 | 能力总览(序列化/鉴权/TLS/KV/线程池/管理通道/总开关) | 37-53 |
| §3 | 关键机制(timed_key / TLS / rpc-net / 线程池 / 版本注入) | 55-77 |
| §4 | 继承与分层:调用方向 | 79-90 |
| §5 | 新能力如何复用或扩展 + 不该放入 libs 的边界 | 92-109 |
| §6 | 影响范围 | 111-123 |
| §7 | 孤岛与未确认 | 125-135 |
| §8 | 分支差异 | 137-139 |

### 04-s3-xbsa-knowledge-map/6.2.0.0.md(150 行;版本化目录,每版本一文件,其他版本见 §〇)

| 章节 | 内容 | 行号 |
|---|---|---|
| §1 | 模块组织总览(s3-tool/s3tools/huawei/xbsa/libobk/dmsbtex/bwlimit) | 13-27 |
| §2 | 能力总览(S3/XBSA/SBT/限速) | 29-41 |
| §3 | 核心任务链(3.1 s3-tool / 3.2 s3file / 3.3 FUSE / 3.4 xbsa / 3.5 libobk / 3.6 dm-ftp) | 43-94 |
| §4 | 对外契约(XBSA/SBT/S3/带宽库接口摘录) | 96-105 |
| §5 | 新介质如何接入 | 107-120 |
| §6 | 孤岛清单 | 122-136 |
| §7 | 影响范围 | 138-146 |
| §8 | 分支差异 | 148-150 |

### 05-build-release-knowledge-map/6.2.0.0.md(102 行;版本化目录,每版本一文件,其他版本见 §〇)

| 章节 | 内容 | 行号 |
|---|---|---|
| §1 | 构建体系总览(xmake 版本/分工/风格) | 13-21 |
| §2 | 产物清单(target → 产物 → 落点) | 23-50 |
| §3 | 版本机制(变量 → configvar → 渲染 → 分发) | 52-63 |
| §4 | 内核模块构建(与 xmake 解耦) | 65-73 |
| §5 | 装配与发布(install 分仓 / CI 流水线 / third_party) | 75-86 |
| §6 | 新模块接入构建三件套 | 88-98 |
| §7 | 分支差异 | 100-102 |

## 二、需求类型 → 文档路由

> 下表中 01–05 均指经 §〇 版本路由选定的版本文件;章节号跨版本一致。

| 需求类型 | 必读 | 选读 |
|---|---|---|
| 文件备份/恢复/快照/监控目录增删 | 01 §2+§3+§4 | 02 §3(传输段)+ 03 §2(线程池/LMDB) |
| fs-cli 新增命令或 method 行为变更 | 01 §3+§4+§6 | 05 §2(产物落点) |
| 远端执行/文件传输/握手鉴权 | 02 §2+§3+§4 | 03 §3(timed_key/TLS) |
| 协议常量(MT_/FS_/ioctl/端口)核对 | 01 §4 + 02 §4 | — |
| 公共能力复用/扩展(libs 加函数) | 03 §2+§5+§6 | 02/01(调用方影响) |
| 新存储介质(S3/XBSA/SBT)接入 | 04 §2+§5+§6(先过孤岛清单) | 05 §6(构建接入) |
| 限速行为调整 | 04 §2(bwlimit 行)+ 02 §4(超时重试) | 02 §6 |
| 构建/发版/升版本/新增模块 | 05 §2+§3+§6 | 04/01(模块归属) |
| 内核模块监控项变更 | 01 §3.5+§3.6+§4.3 + 05 §4 | 02 §3(rpc 转发段) |
| Bug 修复(先定子系统再进链) | 本表 + 对应分册 §3 | 对应分册 §7/§6(先排除孤岛/废弃) |

## 三、能力 × 任务链 → 章节行号(6.2.0.0 基准)

| 能力 × 任务链 | 章节行号 |
|---|---|
| 备份任务链(cli → daemon → 内核 → 拉数据) | 01 §3.1-3.2(47-71 行) |
| 恢复/合并任务链(纯本地) | 01 §3.3-3.4(73-91 行) |
| 监控增删直达内核链 | 01 §3.5(93-103 行) |
| rpc 短会话/持久连接/服务端分发 | 02 §3.1-3.3(54-85 行) |
| rdbcomm 文件/模块通道 | 02 §3.4(87-95 行) |
| timed_key 生成/校验/总开关 | 02 §3.5+§4.4(97-109, 131-137 行) + 03 §3.1(55-59 行) |
| 线程池并发 / LMDB 持久队列 | 03 §2(37-53 行) + 03 §3.4(71-73 行) |
| S3 上传/快照流/FUSE 挂载 | 04 §3.1-3.3(43-65 行) |
| XBSA/SBT 介质库 | 04 §3.4-3.6(67-94 行) + 04 §4(96-105 行) |
| 版本注入/产物装配/CI | 05 §3+§5(52-63, 75-86 行) |
| 新模块接入(含构建三件套) | 04 §5(107-120 行) + 05 §6(88-98 行) |

## 四、新需求分析入口(路由流程)

```
需求
 → 先按 §〇 选定版本文件，定位结论开头注明 <子系统> @ <基线版本> → <版本文件>
 → 判断子系统(01 fs-backup / 02 通道 / 03 公共库 / 04 介质 / 05 构建)
 → 按「二、需求类型」表选必读分册与章节，按行号 Read 指定段
 → 先过孤岛裁决(SKILL §4 + 01 §7 / 02 §7 / 03 §7 / 04 §6)：命中孤岛即停，换现行路径
 → 走任务链定位到函数级路径，每条过三项实证(存在/现行/逐字)
 → 涉通道即核对契约(01 §4 / 02 §4 / 04 §4)
 → 输出定位结论(版本判定 + 文档依据 + 代码实证 + 复用判断 + 契约结果)
```

## 五、调用链入口矩阵(执行顺序与失败回退)

| 入口类别 | 首读路由 | 调用链展开顺序 | 必核对契约 | 缺失时回退 |
|---|---|---|---|---|
| fs-backup 文件备份/恢复 | 01 §3 | fsclient/fs-cli → fsdeamon → kernel 或本地实现 → 数据回写 | method、FS_、ioctl、端口 | 回到 01 §2 能力表，排除 tools/孤岛 |
| rpc/rdbcomm 远端通道 | 02 §3 | client/session → rpc 分发 → rdbcomm 或传输实现 → 响应/文件 | MT_、握手字段、timed_key、端口 | 回到 02 §4 契约表，未核对则标记无法确认 |
| libs 公共能力 | 03 §2-§5 | 调用方 → libs 能力函数 → 返回值/资源释放 → 影响面 | 头文件声明、调用方、线程/错误语义 | 回到现行调用方，不将业务逻辑下沉到 libs |
| s3/xbsa/SBT 介质 | 04 §2-§6 | 业务入口 → 介质适配层 → 数据流/快照 → 介质结果 | S3/XBSA/SBT 接口、产物归属 | 先查孤岛清单；无现行引用不得作为落点 |
| build/release 装配 | 05 §2-§6 | xmake target → 版本注入 → install 分仓 → CI/发布产物 | target 名、版本变量、安装路径 | 回到 05 §2 产物表，避免只改脚本不改装配链 |

每次调用链输出至少包含：入口类别、`6.2.0.0` 基线与版本文件、四段链路、每个路径的 `file:line` 实证、契约结果、未确认项和回退节点。版本文件路径统一写为 `references/<分册目录>/6.2.0.0.md`，以保持 T2154 的版本追溯关系。

## 六、全量可交付工具调用链清单

下表中的每一项都是独立入口；“仓内无调用方”只能作为状态字段，不能合并或删除该链。

| 工具 | 独立入口 → 核心 → 输出/副作用 | 代码/构建锚点 | 调用方状态 |
|---|---|---|---|
| `fs-cli` | method → FS_* → 8901 请求、6611 数据 | `fs-backup/fsclient/main.cpp:506-529` | runtime-consumer |
| `fsdeamon` | requestType → FsSource → BackupHelper/kernel/meta | `fs-backup/fsdeamon/fs_service.cpp:187-228` | runtime-consumer |
| `fsbackup_tools` | 子命令 → ioctl/meta/done/fs_meta | `fs-backup/tools/main.cpp:7-49` | operator |
| `fsbackup.ko` | module init → hook/driver → 监控日志/设备 | `fsbackup_kernel_4.x/Makefile:1-17` | kernel runtime |
| `makeFsbackup` | Go embed → make/cp/insmod → kernel install | `main.go:73-119` | installer |
| `aio-speedd` | main → StartRpcService → 6611/TLS/socket | `rpc/main.cpp:302-393` | runtime-consumer |
| `aio-speed` | CLI → rpc session/SCP → 文件与 meta | `rpc/rpc-client.cpp:672-850` | runtime-consumer |
| `rpc-keygen` | CLI → timed_key_create → key 输出 | `rpc-keygen/main.c:35` | operator |
| `rdbcommd` | main → server INIT/OPEN/READ/WRITE/CLOSE → 6610 | `rdbcomm/rdbcommd-main.c:19-49` | external/runtime |
| `rdbcomm` | CLI flags → client handlers → 命令/模块/文件结果 | `rdbcomm/rdbcomm-main.c:16-77` | external/runtime |
| `s3-tool` | CLI → S3 service → upload/download/list | `s3-tool/main.cpp:76-105` | external/operator |
| `s3file` | subcommand → snapshot/file transfer → S3 objects | `s3tools/s3file/main.cpp:396` | external/operator |
| `s3mount` | mount-snapshot → FUSE operations → mounted filesystem | `s3tools/s3mount/fuse.cpp:180-222` | external/operator |
| `afsd` | FUSE service → S3 public library → filesystem/object | `huanweicloun-sdk-s3-data-backup/my-fuse/xmake.lua:4` | external/operator |
| `afs-cli` | CLI → S3 public library → filesystem/object | `huanweicloun-sdk-s3-data-backup/my-fuse/xmake.lua:54` | external/operator |
| `xbsa64` | XBSA API → shared library → external backup consumer | `xbsa/src/xbsa/xmake.lua` | external |
| `rch-tools` | utility/parser → external backup result | `xbsa/src/rch/xmake.lua` | external |
| `sbt` | SBT API → shared OBK transport library | `libobk/xmake.lua:2-12` | external |
| `FileTransferAgent` | service → OBK transport on port 12000 | `libobk/xmake.lua:15-25` | external |
| `dmsbtex` | DMSBT API → shared database-backup library | `dmsbtex/xmake.lua:3-13` | external |
| `dm-ftp` | service → database-backup transport on port 1255 | `dmsbtex/xmake.lua:16-25` | external |
| `bwlimit_tools` | CLI → shared-memory bwlimit → rate control | `bwlimit/xmake.lua:4-11` | operator/runtime |
| `tls-keygen` | main → TLS certificate/key generation | `libs/xmake.lua:6-18` | operator |

独立链路的固定格式为：`入口参数/子命令 → 分发函数或 target → 核心实现 → 输出/副作用 → 调用方状态`。构建 target 存在但仓内没有消费者时，必须保留链路并标记 `external`、`operator` 或 `build-only`，不得标记为“无链路”。
