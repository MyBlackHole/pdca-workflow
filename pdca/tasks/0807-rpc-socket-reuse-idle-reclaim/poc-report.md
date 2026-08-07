# POC 验证结果 — rpc 复用空闲回收时序

独立仓库：https://github.com/MyBlackHole/POC （私有，2026-08-07）
记录：T0225 rpc 复用 socket 无关闭时机空闲回收（research）

## 方式

为验证 ADR-0016 方案的技术前提，用独立 C 程序（镜像 F/131 `libs/common.c`
`read_is_ready` 与 `StartRPCServiceWorker` 语义）模拟双向时序，不改 F/131 源码。
仓库按验证场景分目录，`make test` 聚合回归。

## 结果（4 场景全部 PASS，2026-08-07）

| 场景 | 断言 | 结果 |
|------|------|------|
| 01-client-fin-fin | V1 close 后 poll 立即唤醒（POLLRDHUP，非 120s 超时） | PASS |
| 01-client-fin-fin | V2 recv=EOF 识别为正常关闭非坏网络 | PASS |
| 02-eof-vs-error | E1 正常关闭判定为 EOF（0）不当作网络错误 | PASS |
| 03-rdhup-residual-data | P2 残留完整消息先读出（12 字节）+ P3 再 recv=EOF 不丢数据 | PASS |
| 04-idle-reconnect | R1 客户端 idle 回收后服务端立即回收(waited=0s) | PASS |
| 04-idle-reconnect | R2 客户端空闲后自动重连成功，新连接可收发 | PASS |

## 结论

实证证实方案基础成立：客户端主动 FIN 立即唤醒服务端（非 wait 超时）、EOF
可正常判定、残留数据与关闭信号并存不丢数据、空闲回收后可自动重连。与
research-report.md 结论及 ADR-0016 一致。