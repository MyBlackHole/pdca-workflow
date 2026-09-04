---
schema: pdca.asset/v1
id: ontology:domain/linux-epoll-eventloop-rpc-conn-idle-reclaim
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/linux-epoll-eventloop-rpc-conn-idle-reclaim/1.0.0
summary: rpc 复用连接空闲回收与时序（POLLRDHUP/EOF）
domain:
- ontology:domain/linux-epoll-eventloop
relations:
  specializes:
  - ontology:domain/linux-epoll-eventloop
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "运行 grep -q 'rpc 复用连接空闲回收与时序（POLLRDHUP/EOF）' ontology/domain/core/linux-epoll-eventloop-rpc-conn-idle-reclaim.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


# rpc 复用连接空闲回收与时序（POLLRDHUP/EOF）

## 来源
- 记录：`records/2026-08-07-rpc-idle-reclaim/conclusion.md`（研究/决策）
- 记录：`records/2026-08-07-rpc-conn-idle-implement/conclusion.md`（EOF 判定实现）
- （相关决策已随 ADR 机制退役删除，见上方 records/ 记录）
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

## 4. 既有瑕疵与已落地修复

- 症状：客户端正常关闭→服务端 `rpc_recv` 打 3 条 Error 噪音
  （`receive failure nread:0` / `bytes:0!=4` / `recv request failure for bad
  network`、rpc-io.cpp:47,57 / rpc-server.cpp:222），把 EOF 当坏网络。
- 修复（已落地，T0226，rpc-io.h/cpp + rpc-server.cpp）：
  - `rpc_recv` 区分 `nread==0`（EOF）与 `nread<0`（网络错误）；EOF 返回专用负值
    枚举 `IO_EOF`（`0xfffffffd`，-3，区别于网络错误 -100/-200/IO_TRUNCATE）。
  - 库函数内部 EOF 不打日志（静默，由调用方语义化）。
  - 服务端 worker 主循环显式识别 `bytes==(int)IO_EOF`→`Info("connection closed
    by peer (EOF)")`→`return`（rpc-server.cpp），不再误打 bad network。
  - 既有调用点 `<0`/`<1` 判定行为不变（IO_EOF<0），零调用点改动，编译与回归通过。

## 局限

- 阈值调优对性能的影响未实测；POC 用独立程序（镜像 read_is_ready），未在
  F/131 真实代码中隔离回归。
- 面向"每调用方单连接"形态，非集中式连接池；若有多空闲连接池需另设计后台
  巡检。
- 空闲主动回收（客户端 last_used/idle_timeout）仍为实现方向，未落地（T0226
  收缩为只修 EOF；如需主动回收另立任务）。