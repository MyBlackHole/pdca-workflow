# 补充 dmsbtex/libobk 会话路径独立集成测试：TLS 配置经 cfg 显式入参生效 — 规格文档

## 问题陈述

- **现状**: T0333 重构后，`sbt-session.c/h` 删除，会话 TLS 功能并入 `dmsbtex/network`（`sbt_session_client_init`/`sbt_session_server_prepare`/`sbt_session_server_accept` 均改为携带 `dmsbtex_tls_config_t`/`libobk_tls_config_t` 显式入参）。但现有 `dmsbtex/test/session_test.c` 与 `libobk/test/session_test.c` 仅通过 `socketpair` 做明文 echo 传输测试，**未覆盖 TLS 配置经 cfg 字段显式入参生效**的路径。
- **目标**: 为 dmsbtex/libobk 会话路径补充独立集成测试，验证 TLS 配置（mtls 开关、算法名、CA/客户端/服务端证书路径）经 cfg 结构体字段传入后正确生效。
- **差距**: 无测试保障"cfg 显式入参 → 会话 TLS 生效"这一 T0333 的核心交付；重构后回归风险未闭合。

## 解决方案

构造显式 cfg 结构体驱动会话测试：
1. **mTLS 启用路径**：填充 `dmsbtex_tls_config_t`/`libobk_tls_config_t` 的 `mtls_enabled`、`algorithm`/`algorithm_name`、`ca_cert`、`client_cert`/`client_key`、`server_cert`/`server_key`，经 `sbt_session_server_prepare/accept` + `sbt_session_client_init` 完成 TLS 握手，断言会话建立成功、数据可往返。
2. **明文路径**：`mtls_enabled=0` 时，现有 socketpair echo 行为保持。
3. **失败路径**：mTLS 启用但证书路径缺失/无效时，`server_prepare` 或 `client_init` 返回失败。
4. 测试仅驱动公开会话 API，不触碰内部实现。

## Seam 分析

### 测试接缝
- 测试直接调用 `sbt_session_server_prepare/accept`、`sbt_session_client_init`、`sbt_session_cleanup`（dmsbtex/network.h、libobk oracleCmdTbl.h 声明的公开接口）。
- 现有 `dmsbtex_session_test`/`libobk_session_test` 目标已注册（xmake），可增量扩展，无需新增构建目标。
- 证书材料：测试内生成自签 CA/服务端/客户端证书（复用 `tls_keygen`/`tls_cert` 工具链或仓库内既有测试证书），隔离外部依赖。

### 声明的测试接缝
- seam: dmsbtex/test/session_test.c -> dmsbtex/network.c
- seam: libobk/test/session_test.c -> libobk/lib/sbt/libobk.c

### 验收可测性
- 每个用例有明确 pass/fail：握手返回值、`rpc_hs_session_t` 状态、数据往返一致。
- 边界：mTLS 开/关、证书缺失、算法名非法，均可独立构造。
- 分层：会话级集成测试补充单元测试（rdb_config_test 已覆盖解析层）。

## 用户故事

1. 作为维护者，我希望 dmsbtex 会话测试覆盖"cfg 显式入参 → mTLS 握手成功"，以便重构后该路径有回归保障。
2. 作为维护者，我希望 libobk 会话测试覆盖 `struct sbtctx` TLS 字段与 `libobk_tls_config_t` 显式入参生效，以便 sbt 库 TLS 路径可信。
3. 作为维护者，我希望明文与失败路径均有断言，以便配置错误被及时暴露。

## 实现决策

**不涉及生产代码修改**（纯测试补充）。若测试暴露缺陷，修 bug 并记录。

- 被测模块：`dmsbtex/network.c`（`sbt_session_client_init`/`server_prepare`/`server_accept`）、`libobk/lib/sbt/libobk.c`（`sbt_client_tls_config_init`、`sbtinit2` 连接路径）、`libobk/lib/logic/oracleCmdTbl.c`（`sbt_session_server_prepare/accept`）。
- 新增/修改文件：仅 `dmsbtex/test/session_test.c`、`libobk/test/session_test.c`（及必要测试证书材料）。
- 技术澄清：证书生成方式沿用仓库既有 TLS 测试材料/工具；不引入外部网络。
- 架构决策：无（不改变生产架构）。

## 测试决策

- 好测试定义：仅测公开会话 API 外部行为（握手成功/失败、数据往返），不测内部实现细节。
- 被测模块：dmsbtex 会话层、libobk sbt 会话层。
- 先例：`rdbcomm_tool_integration`、`rpc_time_integration` 集成测试风格；`dmsbtex_session_test`/`libobk_session_test` 现有目标。

## 验收标准

- [ ] AC-1: dmsbtex 会话测试：构造 `dmsbtex_tls_config_t`（mtls_enabled=1、有效算法、CA/服务端/客户端证书路径），经 `sbt_session_server_prepare/accept` 与 `sbt_session_client_init` 完成握手，断言 mTLS 会话建立且数据往返一致。
- [ ] AC-2: libobk 会话测试：构造 `libobk_tls_config_t`（服务端）与 `struct sbtctx` TLS 字段（客户端），经 `sbt_session_server_prepare/accept` 与 `sbt_client_tls_config_init`+连接路径完成握手，断言 TLS 会话建立。
- [ ] AC-3: mtls_enabled=0 时，明文会话通道正常（现有 socketpair echo 行为保持），断言数据往返一致。
- [ ] AC-4: mtls_enabled=1 但证书路径缺失/无效时，`sbt_session_server_prepare` 或 `sbt_session_client_init` 返回失败，断言显式失败路径。
- [ ] AC-5: `xmake build` 与 `xmake test` 全部通过，扩展后的会话测试纳入全量测试集且无回归。

## 范围外

- 不修改 TLS 证书加载、握手协议、profile 模型。
- 不新增生产代码模块；不改变 rdb-config 通用解析 API。
- 不做性能/压测。

## 备注

- 源自 T0333 conclusion.md 下一轮建议：为 dmsbtex/libobk 会话路径补充独立集成测试（grill 曾判定非必需，现作为独立改进轮执行）。
- 复用 T0333 的 `dmsbtex_tls_config_t`/`libobk_tls_config_t`/`struct sbtctx` TLS 字段定义。

---

*由 to-spec 流程合成。术语表见 `pdca/CONTEXT.md`，架构决策见 `docs/adr/`。*