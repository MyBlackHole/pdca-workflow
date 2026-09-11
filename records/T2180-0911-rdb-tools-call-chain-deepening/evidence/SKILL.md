---
name: rdb-tools-design
description: 定位 aio-tools 6.2.0.0 工具的逐操作真实调用链、跨端协议与运行状态。用于 fs-backup、rpc/rdbcomm、S3/FUSE、XBSA/SBT、公共工具或构建发布的需求分析、设计与故障定位；不用于脱离源码基线的通用备份产品咨询。
---

# rdb-tools-design：需求/故障 → 逐操作调用链

本 skill 把需求路由到 aio-tools `6200/release`（产品版本 6.2.0.0）的真实操作链。知识地图负责定位，源码负责裁决；不得用 target、目录名或“一行入口 → 核心 → 输出”代替运行时调用链。

## 强制流程

1. 完整读取 [总索引](references/00-index.md)，按“工具 + 操作”或“需求类型”选中一个版本分册。
2. 只读取命中分册的逐操作章节。先判断入口状态：`current`、`external`、`operator`、`build-only`、`isolated` 或 `deprecated`。
3. 沿链核对每个 `path:symbol`：入口 → 参数/请求构造 → `switch/if/method/opcode` 分发 → 核心函数 → 进程/内核/SDK 边界 → 对端 handler/结果落点 → 返回/回写。
4. 跨端契约必须两侧逐字核对：发送函数与常量/字段、传输边界、接收分支、响应常量/字段。缺少接收端时明确写“未闭合”，不得推测。
5. 输出所选基线、完整链、分支条件、状态、契约核对和无法确认项；行号只作复核提示，稳定导航使用路径与符号。

## 分册路由

- 文件备份、内核监控：读 [01 fs-backup](references/01-fs-backup-knowledge-map/6.2.0.0.md)。
- `aio-speed`、`aio-speedd`、`rpc-keygen`、`rdbcomm`：读 [02 rpc/rdbcomm](references/02-rpc-rdbcomm-knowledge-map/6.2.0.0.md)。
- `bwlimit_tools`、`tls-keygen` 及其公共库下游：读 [03 libs](references/03-libs-knowledge-map/6.2.0.0.md)。
- S3/FUSE、XBSA、OceanBase SBT、达梦 SBT：读 [04 S3/XBSA](references/04-s3-xbsa-knowledge-map/6.2.0.0.md)。
- target、依赖、安装落点、版本注入：读 [05 build/release](references/05-build-release-knowledge-map/6.2.0.0.md)，再回到对应运行链；构建 target 不是运行链。

## 事实与状态边界

- 事实源固定为 `/home/black/Public/aio/aio-tools/6200/release`；其他版本只能作差异核对。
- `external` 表示仓内无主业务调用者、由数据库或部署侧消费，不等于无调用链；从导出 ABI 或服务入口开始追踪。
- `isolated` 表示实现存在但仓内生产链不可达；`build-only` 表示只有构建装配证据；二者不能推荐为现行修改落点。
- `xbsa/`、`libobk/`、`dmsbtex/` 的相似 API 名不代表兼容；以各自头文件签名与协议为准。
- 静态阅读不能证明真实端口可达、内核模块可装载、备份可恢复或第三方 ABI 联调成功，相关结论写“无法确认”。

## 输出最小记录

```text
基线: 6.2.0.0 -> <分册 §工具/操作>
入口: <path:symbol>
链路: <参数/请求> -> <分发条件> -> <核心> -> <边界/对端> -> <结果> -> <返回>
契约: <生产端 path:symbol> <-> <消费端 path:symbol> | 已闭合/未闭合
状态: current / external / operator / build-only / isolated / deprecated
无法确认: <静态源码之外仍需联调的事实>
```
