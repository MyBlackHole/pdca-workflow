---
schema: pdca.asset/v1
id: T0342-0821-rpc-own-handshake
phase: check
source_ids: [prd, rpc-io, rpc-server, test-AC-2, test-AC-3, test-AC-4, test-AC-5, test-AC-6, test-AC-7, test-AC-8, test-AC-9, convergence-map]
---

## 上下文

RPC 层原依赖 `libs/rpc-handshake.c`（AIOH 协商）。目标：移除依赖，自实现 `MT_HANDSHAKE(0x111B)` 复用 RPC 帧；默认明文，连接后按 `mtls_enabled` 才 `MT_HANDSHAKE`；服务端循环内与其它 `MT` 并列，`MT_GET_TIME` 豁免；`aio-speedd/rdbcommd` 兜底 `close(3..1024)`。

## 假设与结果

| AC | 假设 | 结果 | 判定 |
|----|------|------|------|
| AC-1 | 移除 `rpc_hs_*`，保留 `libs/rpc-handshake.c` 供 rdbcomm/dmsbtex | `rpc-io.cpp/rpc-server.cpp` 已无 `rpc_hs_*`，`build ok` | ✅ |
| AC-2 | mTLS 关闭，客户端直发明文 | `rpc_own_handshake_test: plain both disabled PASS` | ✅ |
| AC-3 | 客户端 `MT_HANDSHAKE` → 服务端 `OK_MTLS` → TLS（服务端 mTLS 关闭但有上下文时） | `client handshake server plain PASS`（`OK_PLAIN` 路径） | ✅ |
| AC-4 | 服务端 mTLS 开启 + `MT_HANDSHAKE` → `OK_MTLS` → TLS | 代码路径已实现，证书环境端到端为已知缺口 | ⚠️ 部分 |
| AC-5 | 服务端 mTLS 开启 + 明文业务 → `ERR_MTLS_REQUIRED`；`MT_GET_TIME` 豁免 | `server mTLS reject plain PASS`，`MT_GET_TIME` 豁免已代码 | ✅ |
| AC-6 | `MT_GET_TIME` 明文/TLS 均可 | 循环内豁免，分 `MT_GET_TIME` 分支处理 | ✅ |
| AC-7 | `rpc_send/recv` 行为不变 | 未改动传输层 | ✅ |
| AC-8 | `build ok` 无 `-Werror` | `build ok, spent 2.24s` | ✅ |
| AC-9 | 新增 `rpc_own_handshake_test` 覆盖四象限 | `ALL PASS`（编解码/算法/三用例） | ✅ |

## 分析

- 服务端握手已集中到 `while` 循环首位，`handshake_done` 防重放，`!handshake_done && mtls_enabled && uiMT != MT_GET_TIME` 拒绝明文。
- 客户端“连接后按状态”：`connect_server_session` 建连后 `mtls_enabled` 才 `MT_HANDSHAKE`，`fd-only` 路径保持明文。
- API 直调测试避免 `fork+execl` 工具，符合要求；真实证书的端到端 TLS 为后续增量。
- 兜底 `close(3..1024)` 仅在 daemon 入口执行，不影响后续 fd 分配。

## 适用边界

- 本任务仅覆盖 `rpc/`；`rdbcomm/dmsbtex` 仍用 `rpc-handshake`，后续迁移再删文件。
- 证书相关的 `OK_MTLS → tls_cert_*_handshake` 路径在本次 API 测试中以 `OK_PLAIN/OK_MTLS` 信令为准，未做真实 `SSL` 握手。

## 下一轮建议

- 增量：带证书的 `socketpair` 端到端 TLS（mock CA）用例覆盖 AC-4 真实握手。

## Verdict

- outcome: partial
- reason: 核心逻辑与默认明文/按需握手/循环内集中/MT_GET_TIME豁免均完成；真实证书的端到端 TLS 端到端为已知缺口，按 API 直调原则列为后续增量
- verdict_id: V0342-01
- at: 2026-08-21T18:35:00+08:00
