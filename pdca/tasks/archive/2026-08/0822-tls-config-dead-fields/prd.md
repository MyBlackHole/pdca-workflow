# 跟进：TLS 配置结构体死字段清理（T0360，T0358 发现）

## 问题陈述

- **现状**: tls-cert 体系重构收敛为 `cert_dir + algorithm + ca_cn(服务端握手响应下发)` 唯一路径后，各模块 TLS 配置结构体中的显式证书路径/CA 名字段成为死数据——填充后全仓库零读取。
- **目标**: 审计并删除全部死字段及其填充代码，配置结构体最小化。
- **差距**: 用户在 T0358 Check 阶段指出"工具这些参数多余"，经 grep 核实属实。

## 已核实的死字段清单（待 Do 阶段全仓复核）

| 结构体 | 字段 | 现状 |
|--------|------|------|
| `g_rpc_config`（rpc/rpc-config.h:27-33） | `ca_cn[256]` | 无赋值无消费 |
| 同上 | `ca_cert` / `server_cert` / `server_key` | 仅 rpc-config.cpp:198-205 填充，零读取 |
| `dmsbtex_tls_config_t`（dmsbtex/network.h:49-52） | `ca_cn[256]` / `ca_cert[512]` / `server_cert` / `server_key` | sbt_tls_config_init 填充后零消费 |
| rdbcomm `client_options`/`rdbcomm_conn`/`server_options` | `ca_cert`、`ca_cn` 及拷贝链 | conn->ca_cert 拷贝后零消费 |

注意：`client_cert`/`client_key`/`cert_dir` 需逐一核实消费点后再定去留（cert_dir 有确认消费；libobk 侧 sbt_client_cert_paths 为 unused static）。

### 声明的测试接缝
- seam: rpc/tests/mixed_mtls_integration.cpp -> rpc/rpc-config.cpp
- seam: dmsbtex/test/session_test.c -> dmsbtex/network.c
- seam: libobk/test/session_test.c -> libobk/lib/sbt/libobk.c
- seam: rdbcomm/tests/handshake_session_test.c -> rdbcomm/client.c

## 验收标准

- [ ] AC-1: 死字段及关联填充代码删除，全量构建通过
- [ ] AC-2: 六套既有测试回归 PASS（握手/会话/集成）
- [ ] AC-3: 结构体中每个保留字段均有可指认的消费点（审计清单入报告）

## 备注

来源：T0358 Check 阶段用户意见 + grep 核实。sec_resolve_int env 层 atoi 缺陷已决定并入 T0357。
