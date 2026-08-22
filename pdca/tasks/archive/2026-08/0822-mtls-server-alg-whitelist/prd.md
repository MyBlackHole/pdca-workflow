# 跟进：服务端握手算法白名单校验（H1+M4+N3，T0348）

## 问题陈述

- **现状**: 三模块服务端对客户端协商算法值零校验（任意 u16 直接使用）；`libs/tls_cert.c:366-368` 的 `tls_cert_find_slot()` 对 NULL/空 algorithm 静默回落 slots[0]，导致协商字段可被绕过；错误码 `*_HS_ERR_ALGORITHM(0x8005)` 三处已定义却从未使用（rpc 侧缺定义）。
- **目标**: 服务端在握手入口白名单校验客户端算法值（仅接受 SM4=1/AES=2），非法即回显式错误码并断开。
- **差距**: T0348 审查报告 H1/M4/N3。

## 解决方案

| 模块 | 入口 | 动作 |
|------|------|------|
| libobk | `oracleCmdTbl.c:859-871` | halg ∈ {SM4,AES} 校验；非法发 `OBK_HS_ERR_ALGORITHM`(0x8005) 响应帧并断开 |
| rdbcomm | `server.c:484-494` | 同上，`send_handshake_resp(..., RDB_HS_ERR_ALGORITHM, ...)` |
| dmsbtex | `network.c dm_server_handshake` 开头 | 非法发 `DM_HS_ERR_ALGORITHM` 响应帧，return -1 |
| rpc | `rpc-server.cpp:244-249` | 删除"非法回落服务端配置"逻辑，非法回 `HS_ERR_ALGORITHM`（补 rpc-protocol.h 定义）；合法值仍采纳客户端算法 |
| libs/tls_cert.c | — | **不修改**：入口白名单后 NULL 不可达，find_slot 回落保留为防御层（评估结论入报告） |

客户端兼容性：各客户端发出值经配置校验必为 1/2，收到非 OK_MTLS 一律走既有失败路径，无需改动。
sec_resolve_int 并入项裁决：T0361 后安全布尔全部迁移 sec_resolve_bool，sec_resolve_int 无剩余安全调用方，**无需修改**（Check 结论记录）。

### 声明的测试接缝
- seam: rdbcomm/tests/handshake_session_test.c -> rdbcomm/server.c
- seam: libobk/test/session_test.c -> libobk/lib/logic/oracleCmdTbl.c
- seam: dmsbtex/test/session_test.c -> dmsbtex/network.c
- seam: rpc/tests/rpc_own_handshake_test.cpp -> rpc/rpc-server.cpp（模拟服务端同步拒绝语义）

## 验收标准

- [ ] AC-1: 四模块服务端收到非法算法值（0、0xFFFF 等）时返回各自 ERR_ALGORITHM 错误码并断开，不再触发 slot 回落
- [ ] AC-2: 合法算法值（SM4=1/AES=2）握手行为不变，既有会话测试全部通过
- [ ] AC-3: 新增回归测试覆盖畸形 halg 帧（至少 0 与 0xFFFF 两类）
- [ ] AC-4: xmake test 全量 40+ 用例 PASS（以全量重建为准）

## 范围外

- 协商语义统一（flags 表达/强一致决策树）归 T0359
- 不修改通用 sec_resolve_int 行为

## 备注

来源：T0348 报告 H1/M4/N3；知识库 tls/mtls-param-review-findings.md 陷阱 1。M4 死字段已在 T0360 删除，本任务不涉及结构体变更。
