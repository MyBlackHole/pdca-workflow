# 审查报告 — 四模块握手跨模块一致性（T0363）

## 审查范围

- 模块：`rdbcomm` / `libobk`(sbt) / `dmsbtex` / `rpc` 握手收发链路
- 关联改动：T0354–T0362（握手协商语义与枚举统一、libobk 网络序 M5）
- 维度：字节序一致性、白名单/fail-closed、错误帧完整性、测试覆盖

## 标准轴发现

| # | 文件 | 严重度 | 问题 | 状态 |
|---|------|--------|------|------|
| S1 | `dmsbtex/network.c:242-244` | MEDIUM | 服务端 `ca_cn unavailable` 分支未发送 `DM_HS_ERR_CA_CN` 拒绝帧即断开，与同文件 no-TLS-context / unknown-algorithm 分支及 rpc/rdbcomm 行为不一致 | 已修复（AC-2） |
| S2 | 四模块 | — | 字节序已统一为网络序（rdbcomm 经 sshbuf `POKE_U16` 大端；其余显式 `htons/ntohs`） | 无问题 |
| S3 | `dmsbtex/network.c:250`、`rpc-server.cpp:303` | LOW | `strncpy` 复制 `ca_cn` 未强制 `\0` 终止（原始遗留，非本次引入） | 记录 follow-up |

## 规范轴发现（对照 PRD）

- AC-1（字节序一致）：四模块均网络序，M5 仅改 libobk 是对齐，无跨模块回归。✅
- AC-2（dmsbtex 补帧）：原缺帧，已补 `DM_HS_ERR_CA_CN` 并与其余三模块对齐。✅
- AC-3（测试+全量）：新增拒绝码可达性断言；全量 `xmake test` 40/40 PASS。✅

## 风险评级

- **MEDIUM**：S1 缺帧——功能上客户端仍失败（不降级、无安全漏洞），但与"四模块无降级语义一致"目标不符，且客户端拿不到明确错误码、可诊断性弱；已在本任务修复。
- **LOW**：S3 边界健壮性，留作后续技术债。

## 建议

1. dmsbtex 补帧已落地（见 `code-diff.md`），建议随本任务合入。
2. 错误码命名归一（`RDB_HS_ERR_*`/`DM_HS_ERR_*`/`HS_ERR_*`/`OBK_HS_ERR_*`）建议归一到 `libs` 单一来源（follow-up）。
3. `ca_cn unavailable` 运行时分支建议补集成测试（需"ctx 有效但 ca_cn 为空"证书环境）。
4. libobk 外部 oracle 对端网络序升级另排 follow-up（见 T0362 disposition）。
