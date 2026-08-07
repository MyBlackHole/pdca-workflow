# rpc 复用连接空闲回收与时序（POLLRDHUP/EOF）

## 来源
- 记录：`records/2026-08-07-rpc-idle-reclaim/conclusion.md`
- ADR：`docs/adr/ADR-0016-rpc-conn-idle-reclaim.md`
- POC 实证：私有仓库 `POC`（2026-08-07，4 场景全通过）
- 适用范围：F/131 rpc（及同类"客户端复用长连接 + 服务端 worker 长驻"模型）

## 1. 核心问题

复用连接缺少确定的空闲关闭时机。仅有错误/超时触发回收，业务空闲的连接悬挂
占 fd 与服务端 worker 线程。

## 2. 方案：客户端主动 FIN 主导

- 客户端复用 `rpc_conn` 增加空闲判定（`last_used` + `idle_timeout`），空闲超
  阈值主动 `close()` 发 FIN。
- 服务端 `read_is_ready` 的 poll 事件含 `POLLRDHUP|POLLHUP`
  （libs/common.c），客户端 close 即立即唤醒 worker，`recv` 读到 EOF 走
  `return__` 关闭。**无需新增协议消息**（FIN+POLLRDHUP 已是天然通道）。
- 服务端 `read_timeout`(默认 120s) 对齐为兜底；客户端 `idle_timeout` 应
  < read_timeout，避免服务端抢先超时回收。

## 3. 关键时序结论（已 POC 实证）

| 断言 | 结论 |
|------|------|
| close 后服务端是否必然触发 POLLRDHUP？ | 是。无 SO_LINGER→优雅 FIN→poll 立即唤醒，不走 120s 超时 |
| POLLRDHUP 与残留数据并存？ | 并存时 poll 按可读优先，先读走残留完整消息再轮询 RDHUP；单 poll 单次 recv 循环自洽，不丢数据 |
| EOF 判定 | `recv` 返回 0 是"正常关闭"，不应与 `recv<0`（网络错误）混淆 |

## 4. 既有瑕疵与修复方向

- 症状：客户端正常关闭→服务端 `rpc_recv` 打 3 条 Error 噪音
  （`receive failure nread:0` / `bytes:0!=4` / `recv request failure for bad
  network`、rpc-io.cpp:47,57 / rpc-server.cpp:222），把 EOF 当坏网络。
- 修复：`rpc_recv` 区分 `nread==0`（EOF，返回非错语义）与 `nread<0`（错误）；
  worker 对正常 FIN 走干净关闭路径。

## 局限

- 阈值调优对性能的影响未实测；POC 用独立程序（镜像 read_is_ready），未在
  F/131 真实代码中隔离回归。
- 面向"每调用方单连接"形态，非集中式连接池；若有多空闲连接池需另设计后台
  巡检。