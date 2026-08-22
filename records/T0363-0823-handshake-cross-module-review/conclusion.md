# 结论 — T0363 四模块握手跨模块一致性审查

## 结论

四模块（`rdbcomm` / `libobk`(sbt) / `dmsbtex` / `rpc`）握手 body 字节序已统一为网络序：
`rdbcomm` 经 sshbuf `POKE_U16` 大端，`dmsbtex`/`libobk` 显式 `htons`/`ntohs`，`rpc` 结构体 `htons`/`ntohs`。
M5 仅改 libobk 是对齐其余三模块，无跨模块字节序回归。

审查发现 `dmsbtex` 服务端 `ca_cn unavailable` 分支未发送 `DM_HS_ERR_CA_CN` 拒绝帧即断开，
与同文件 `no-TLS-context` / `unknown-algorithm` 分支及 `rpc`/`rdbcomm` 对齐分支行为不一致
（MEDIUM，功能上不降级但缺明确错误码、可诊断性弱），已在本任务修复并补测试。

## 验收

- **AC-1**：四模块握手字节序一致性确认无跨模块差异 — `EVID-CODE-REVIEW` ✅
- **AC-2**：`dmsbtex` 服务端 `ca_cn unavailable` 补发 `DM_HS_ERR_CA_CN` 拒绝帧，与 rpc/rdbcomm 对齐 — `EVID-CODE-DIFF` ✅
- **AC-3**：`dmsbtex/test/session_test.c` 新增拒绝码可达性断言通过；全量 `xmake test` 40/40 无回归 — `EVID-TEST-RESULT` ✅

## 风险与建议

- **MEDIUM（已修复）**：`dmsbtex` 缺帧。
- **LOW（follow-up）**：错误码命名归一（`RDB_HS_ERR_*`/`DM_HS_ERR_*`/`HS_ERR_*`/`OBK_HS_ERR_*`）归一到 `libs`；`strncpy` 复制 `ca_cn` 未强制 `\0` 边界；`ca_cn unavailable` 运行时分支补集成测试；libobk 外部 oracle 对端网络序升级（见 T0362 disposition）。

## verdict

`outcome = confirmed`；AC-1/2/3 收敛闭环，代码修复已落地并通过全量测试。
