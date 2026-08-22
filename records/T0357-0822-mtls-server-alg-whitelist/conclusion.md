---
schema: pdca.asset/v1
id: T0357-0822-mtls-server-alg-whitelist
phase: check
source_ids: [T0357-ac1-server-fix, T0357-ac13-red-observation, T0357-ac123-green-test, T0357-ac3-test-diff, T0357-ac4-full-suite, T0357-ac13-libobk, T0357-ac13-dmsbtex, T0357-ac13-rpc, T0357-ac4-full-v2]
---

## 上下文
T0348 审查报告 H1/M4/N3 指出：多模块服务端对客户端协商算法值零校验，且
`libs/tls_cert.c` 的 `find_slot()` 对 NULL/空 algorithm 静默回落 `slots[0]`，
导致协商字段可被绕过。T0357 负责"服务端握手算法白名单校验"，范围覆盖四模块：
rdbcomm、libobk、dmsbtex、rpc（libs/tls_cert.c 按 PRD 决策不修改，回落保留为防御层）。

## 假设与结果
- 假设：畸形/未知 halg（0、0xFFFF 等）会被各服务端静默接纳（rdbcomm/libobk/dmsbtex
  经 find_slot(NULL) 回落 slots[0]；rpc 经"回落服务端配置"）。
- 结果：四模块现已全部白名单校验——rdbcomm 由本任务先修，libobk/dmsbtex/rpc
  经后续补齐（子代理实现 + 主 session 复验）。红→绿闭环完成：
  - rdbcomm `bad halg 0x0000/0xffff rejected` PASS
  - libobk 畸形 halg → 子进程 `_exit(3)` 且 `io.tssl==NULL`，父进程收 OBK_HS_ERR_ALGORITHM 帧
  - dmsbtex `malformed algorithm fail-closed` PASS（exit_code==6，回落被阻断）
  - rpc `negotiate algorithm fail-closed` PASS（0/0xFFFF/3/99 → HS_ERR_ALGORITHM）

## 分析
- **rdbcomm** `server.c:507`：先判 `algo_name`，未知即回 `RDB_HS_ERR_ALGORITHM` 并断开。
- **libobk** `oracleCmdTbl.c:104`（`sbt_session_server_handshake`）：先判
  `obk_hs_algorithm_name`，未知即发 `OBK_HS_ERR_ALGORITHM`(0x8005) 帧 + return -1；
  `tls_cert_server_handshake` 亦改用 `algo_name`，消除重复调用与 NULL 回落。
- **dmsbtex** `network.c:223`（`dm_server_handshake`）：同法，发 `DM_HS_ERR_ALGORITHM` 帧。
- **rpc** `rpc-server.cpp:244`：删除"回落服务端配置"逻辑，新增 `hs_negotiate_algorithm`
  （fail-closed，SM4/AES 才采纳），未知算法发 `HS_ERR_ALGORITHM`(0x8005) + 断开；
  `rpc-protocol.h` 补 `HS_ERR_ALGORITHM` 定义。测试 mock 服务端同步接入该函数。
- 共性：均消除 `find_slot(NULL)` / 配置回落绕过，fail-closed；合法 SM4/AES 路径不变。

## B4 双轴代码审查（补做）
- 标准轴：四模块改动均最小、fail-closed；无 CRITICAL/HIGH。
  - libobk/dmsbtex/rpc 生产改动正确，无资源泄漏、无缓冲区溢出（固定长度帧封装）。
  - 测试回归：libobk 用例初版父进程用裸 `recv` 读流式帧未保证读满，全量测试暴露
    （assert n==sizeof(resp) 失败）；已改为循环读满后 ALL PASS——属测试健壮性修复，
    非生产缺陷。
  - dmsbtex/rpc 测试子代理初报 PASS 但未覆盖流式读边界，已通过全量重验。
- 规范轴（对照 prd AC）：AC-1/AC-2/AC-3/AC-4 均有可信证据。

## 适用边界
- 仅覆盖握手入口算法值白名单；`libs/tls_cert.c` 不修改（PRD 既定）。
- 跨模块协商语义统一（flags 表达/强一致决策树）归 T0359，不在本任务范围。

## 下一轮建议
- 将"畸形协商帧"纳入各模块模糊/混沌测试基线，防止回归。
- T0359 统一协商语义时复用本任务的 `hs_negotiate_algorithm` 范式。

## 验收标准逐条判定
- AC-1（四模块非法算法值回 ERR_ALGORITHM 并断开，无 slot 回落）：**通过**
  — T0357-ac1-server-fix、T0357-ac13-libobk、T0357-ac13-dmsbtex、T0357-ac13-rpc、
    T0357-ac123-green-test。
- AC-2（合法算法值行为不变，既有会话测试通过）：**通过**
  — T0357-ac123-green-test、T0357-ac4-full-v2（libobk/dmsbtex/rpc 既有用例全 PASS）。
- AC-3（新增回归测试覆盖 0 与 0xFFFF）：**通过**
  — T0357-ac3-test-diff、T0357-ac13-libobk、T0357-ac13-dmsbtex、T0357-ac13-rpc。
- AC-4（xmake test 全量 40 用例 PASS）：**通过**
  — T0357-ac4-full-v2（100% passed, 0 failed out of 40，含四模块握手测试）。

## Verdict
outcome: confirmed
reason: 四模块白名单校验全部落地，红→绿闭环完成，全量 40 用例通过，B4 双轴审查无 blocking 问题。
