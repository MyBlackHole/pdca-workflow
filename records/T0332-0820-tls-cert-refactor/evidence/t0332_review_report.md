# T0332 tls_cert 重构 — 双轴代码审查报告

对比基点：`HEAD`（22dc3935）→ 工作区改动（25 文件，+1297/-1658）
规范来源：`prd.md`（本任务规格文档）
标准来源：仓库无独立 CODING_STANDARDS.md，采用 Fowler 坏味基线

## 标准轴

审查范围：tls_cert.c/h（核心重写）、rdb-config 新增 helper、8 个调用方适配。

- `tls_cert.c`：无全局状态、无缓存、无锁、无 getenv；slot 生命周期（init→create→cleanup）错误路径全部释放，无泄漏路径；`tls_cert_find_slot` 对 NULL ctx 安全；握手审计日志记录证书 CN/IP/端口，符合安全基线。
- `strncpy` 复制算法名未显式 NUL 终止（`sizeof-1`）：算法名均为短常量（<64），`calloc` 已清零，实际安全，但属易错模式（Info）。
- `sec_tls_client_cert_paths` 的 `snprintf` 截断判断 `ret < (int)sz`：`snprintf` 返回 `>= sz` 才溢出，`== sz-1` 是合法完整写入，逻辑正确。
- 调用方（rdbcomm/rpc/libobk/dmsbtex/sbt-session/timed_net_key）：ctx 生命周期管理一致（init→握手→cleanup 或校验后 cleanup）；fs-backup 删除无效 init 调用正确。
- `sbt_session_server_prepare` 重复调用会覆盖泄漏前 ctx：当前仅启动时调用一次，无实际风险（Info）。
- dmsbtex 与 libobk 存在同名 extern `sbt_session_*` 符号：为 HEAD 既有现象，两库独立链接，非本任务引入（Info）。
- 无重复代码、无消息链、无过度工程；profile/slot 结构清晰。

标准轴结论：无 Blocking，2 条 Info。

## 规范轴

对照 prd.md 逐条审查：

- AC-1（服务端单 ctx 多 profile 并存 + 按算法取 SSL_CTX）：`tls_server_multi_profile`、`tls_multi_profile_handshake` 测试覆盖，实现满足。✔
- AC-2（客户端多 profile + 非法算法/缺失证书/缺失 CA 错误码）：`tls_client_multi_profile`、`tls_cert_init_invalid_algorithm/missing_ca/missing_cert` 覆盖，错误码与文档一致。✔
- AC-3（普通/SM2 成功失败矩阵 + 7 接口删除）：`tls_sm2_handshake`（真实 SM2 双端握手）、`tls_mtls_handshake`、`tls_server_missing_*` 覆盖；删除接口 grep 计数为 0（见静态证据）。✔
- AC-4（全部调用方构建 + 集成握手 + 旧入口无残留）：`rdbcomm_tool_integration`（7 用例：明文/mTLS/SM2/失败矩阵）、`rpc_tool_integration`、`rpc_time_integration`、`libobk_session_test` 通过；旧 from_env 接口 grep 为 0。✔
- AC-5（无缓存/无锁/无 getenv/构建无警告）：静态指标满足，`git diff --check` clean，xmake 构建无新增警告。✔

偏差（Warning）：
- prd.md 接口定义中 `tls_cert_get_ssl_ctx(tls_cert_ctx_t *ctx)` 为单参，实现为双参
  `(ctx, algorithm)`。双参为 AC-1"按算法分别获取"所必需，且测试按双参调用，
  判定 prd.md 接口清单为文档笔误，实现正确。建议同步修正 prd.md 接口清单。
- `sec_tls_client_cert_paths` 最初含 sm2 参数，审查中发现算法不改变客户端
  证书文件名（统一 host.crt），已移除死参数并简化 8 处调用方，回归测试全通过。

规范轴结论：无 Blocking，1 条 Warning（prd 接口清单笔误，非代码缺陷）。

## 门禁判定

- Blocking = 0 → 通过
- Warning = 1（prd.md 文档笔误，建议修正文档）
- Info = 3

最严重问题：无。重构符合 PRD 目标（确定性模块、多 profile、配置外移、死代码清理）。