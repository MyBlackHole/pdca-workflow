# 四模块握手跨模块一致性审查（含 dmsbtex 缺帧修复）— 规格文档

## 问题陈述

- **现状**: T0354–T0362 完成四模块（rdbcomm / libobk(sbt) / dmsbtex / rpc）握手协商语义与枚举统一、libobk 握手 body 网络序改造（M5）。但缺少对四模块握手收发的跨模块一致性终审。
- **目标**: 确认四模块握手 body 字节序、白名单/fail-closed、错误帧完整性、测试覆盖的一致性，并修复发现的缺陷。
- **差距**: 审查发现 dmsbtex 服务端 `ca_cn unavailable` 分支未发送 `DM_HS_ERR_CA_CN` 拒绝帧即断开，与同文件另外两条拒绝路径及 rpc/rdbcomm 对齐分支行为不一致。

## 解决方案

从跨模块一致性视角审查四模块握手链路，对发现的不一致缺陷做最小修复（补发拒绝帧 + 补测试），其余一致性结论登记为审查知识。

## Seam 分析

### 测试接缝

review 场景无独立测试产物要求；但本次含 bugfix 处置，修复在 `dmsbtex` 握手测试套件内补回归用例。

## 用户故事

1. 作为维护者，我想要四模块握手错误处理帧语义一致，以便客户端拿到明确错误码、便于诊断。
2. 作为审查者，我想要字节序与白名单一致性结论，以便确认 M5 未引入跨模块回归。

## 实现决策

- 修改模块：`dmsbtex/network.c` 服务端 `ca_cn unavailable` 分支补发 `DM_HS_ERR_CA_CN` 帧。
- 不修改其他三模块（字节序已统一为网络序、白名单已 fail-closed）。

## 测试决策

- 被测模块：`dmsbtex/network.c` 的 `dm_server_handshake`。
- 现有先例：`dmsbtex/test/session_test.c` 已有握手协商与 unknown-algorithm 用例。

## 验收标准

- [ ] AC-1: 四模块握手 body 字节序一致性确认无跨模块差异（rdbcomm 经 sshbuf POKE_U16 大端、dmsbtex/libobk 显式 htons/ntohs、rpc 结构体 htons/ntohs）
- [ ] AC-2: dmsbtex 服务端 `ca_cn unavailable` 分支补发 `DM_HS_ERR_CA_CN` 拒绝帧，与 rpc/rdbcomm 对齐分支行为一致
- [ ] AC-3: `dmsbtex/test/session_test.c` 新增 `ca_cn` 不可用回归用例通过；全量 `xmake test` 无回归

## 范围外

- 错误码命名归一（RDB_HS_ERR_*/DM_HS_ERR_*/HS_ERR_*/OBK_HS_ERR_* 四套前缀）留作后续 follow-up。
- `strncpy` 无 null 终止的边界健壮性（原始遗留）不在此任务修复。
- libobk 外部 oracle 对端网络序升级另排 follow-up（见 T0362 disposition）。

## 备注

- 本次为 review 场景，含 bugfix 处置（Z3 提交代码）。
- 关联：T0362（libobk 网络序 M5）、T0348（握手统一总任务）。

---

*由 to-spec 流程合成。术语表见 `pdca/CONTEXT.md`，架构决策见 `docs/adr/`。*
