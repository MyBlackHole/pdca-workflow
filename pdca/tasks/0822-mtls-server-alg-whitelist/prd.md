# 跟进：服务端握手算法白名单校验（H1+M4+N3，T0348）

## 问题陈述

- **现状**: 三模块服务端对客户端协商算法值零校验（任意 u16 直接使用）；`libs/tls_cert.c:366-368` 的 `tls_cert_find_slot()` 对 NULL/空 algorithm 静默回落 slots[0]，导致协商字段可被绕过；`rdbcomm/server.h:16` 的 `server_opts.tls_algorithm` 为死字段；错误码 `*_HS_ERR_ALGORITHM(0x8005)` 各处已定义但从未使用。
- **目标**: 服务端在握手入口白名单校验客户端算法值，非法即回显式错误码并断开。
- **差距**: T0348 审查报告 H1/M4/N3。

## 修复范围

| 模块 | 位置 | 动作 |
|------|------|------|
| libobk | `oracleCmdTbl.c:859-871` | halg ∈ {SM4, AES} 校验，非法回 OBK_HS_ERR_ALGORITHM |
| rdbcomm | `server.c:484-529` | 同上，回 RDB_HS_ERR_ALGORITHM |
| dmsbtex | `main.c:235-248` + `network.c dm_server_handshake` | 同上，回 DM_HS_ERR_ALGORITHM |
| rpc | `rpc-server.cpp:244-249` | 已有回落逻辑，改为非法即拒绝（与全局语义一致） |
| libs | `tls_cert.c find_slot` | 评估取消空算法回落或加显式告警（需评审调用方影响） |
| rdbcomm | `server.h:16` 死字段 | 删除或接入校验 |

### 声明的测试接缝
- seam: rdbcomm/tests/handshake_session_test.c -> rdbcomm/server.c
- seam: libobk/test/session_test.c -> libobk/lib/logic/oracleCmdTbl.c
- seam: dmsbtex/test/session_test.c -> dmsbtex/network.c

## 验收标准

- [ ] AC-1: 四模块服务端收到非法算法值（0、0xFFFF 等）时返回各自 ERR_ALGORITHM 错误码并断开，不再触发 slot 回落
- [ ] AC-2: 合法算法值（SM4=1/AES=2）握手行为不变，既有会话测试全部通过
- [ ] AC-3: 新增回归测试覆盖畸形 halg 帧场景

## 备注

来源：`$PDCA_HOME/knowledge/tls/mtls-param-review-findings.md` 陷阱 1；审查报告 `$PDCA_HOME/pdca/tasks/archive/2026-08/T0348-0822-mtls-state-alg-review/review-report.md`
