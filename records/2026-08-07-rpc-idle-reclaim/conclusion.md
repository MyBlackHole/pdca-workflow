---
schema: pdca.asset/v1
id: 2026-08-07-rpc-idle-reclaim
phase: check
source_ids: [report, adr-0016, poc-report]
---

## 上下文

任务 T0225：为 F/131 rpc 复用 socket 缺少的"关闭时机"设计并选定空闲回收
方案。交付为研究产出（research），不落代码。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 复用连接无确定空闲关闭时机（AC-1/AC-2） | 成立：持有形态为每调用方单 conn（rpc.cpp:2378），回收仅两个触发器（read_timeout 或对端关闭，rpc-server.cpp:215） |
| 客户端主动告知无需协议（AC-3） | 成立：`read_is_ready` poll 已含 `POLLRDHUP|POLLHUP`（libs/common.c:17），close→FIN→立即唤醒，无需 MT_* 协议（ADR-0016） |
| 回收时机驱动方=客户端闲时 FIN 主导 + 服务端 read_timeout 兜底（AC-4） | 成立：idle_timeout 可配置（<120s read_timeout） |
| POLLRDHUP 前提与残留数据（AC-5） | 成立：无 SO_LINGER→优雅 FIN；POLLIN 优先读完残留再轮询 RDHUP；空闲回收与半包竞态实质无冲突 |
| EOF 判定并入（AC-06） | 成立：空发日志证实 EOF 被当错误，nread==0 应返回 EOF 语义而非 -100（rpc-io.cpp:44） |

## 分析

- 方案收敛为单条最优解：客户端空闲超时主动 FIN 主导，服务端 read_timeout 兜底，
  不新增协议、不引入服务端巡检/连接池。
- 放弃备选：服务端独立巡检（会打断挪用连接）、显式 MT_* 消息（重复造
  POLLRDHUP 已有语义）、仅 TCP keepalive（不反映业务空闲）。
- 并归既有瑕疵：客户端正常 close 被误报 "bad network"，因 rpc_recv 将
  nread==0(EOF) 当错误（-100）。已在 PRD/ADR 置入收口（AC-6）。
- **POC 实证**（独立仓库 poc-rpc-idle-timing/POC，4 场景全 PASS）：客户端
  FIN 立即唤醒服务端（非 120s）、EOF 正常判定、残留数据并存不丢、空闲回收后
  自动重连。方案技术前提获实证支持。

## 适用边界

- 结论面向 F/131 rpc_conn / StartRPCServiceWorker 结构，非通用连接池设计。
- 未落代码，为方案决策；实现与回归留待后续任务。
- 未对"阈值调优对性能影响"做实测；数值由实现期验证。

## 下一轮建议

1. 实现任务：rpc_conn 增 last_used/idle_timeout，reconn_send_msg 懒回收。
2. rpc-config 增 idle_timeout（默认 <120s），两端超时对齐。
3. rpc_recv 区分 EOF 与错误消除 3 条 Error 噪音，回归测试新加。
4. 提交时引用本记录的决策方向与 ADR-0016。