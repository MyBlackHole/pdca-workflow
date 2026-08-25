---
schema: pdca.asset/v1
id: T3961-0825-server-alg-lock
phase: check
source_ids: [ac1-mixed-lock, ac1-summary, ac2-libobk-lock, ac2-dmsbtex-lock, ac3-e2e-lock, ac4-compat, ac5-grep]
---

## 上下文

用户需求：服务端算法锁定——"配置了 tls_algorithm 就代表只允许使用此算法"，且服务端 tls_algorithm **无默认值**（未配置=未设置）；同步消除 rpc `cli_algorithm`/`tls_algorithm` 冗余字段。实施中用户纠正 rdbcomm 不引入 algorithm_locked 派生字段，统一"algorithm_name 非空即锁"语义。commit 5a6017f7。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 显式配置 tls_algorithm 后错配客户端被 HS_ERR_ALGORITHM 拒绝 | 成立：rpc 链接级 AC-8、libobk/dmsbtex session_test 锁定用例全过 |
| 匹配算法客户端正常升级通行 | 成立：AC-9（锁 AES + client AES 完整 TLS 升级+业务往返）、e2e S18 |
| 未显式配置时行为与现状一致（向后兼容） | 成立：e2e S1-S17 全过；dmsbtex AC-2b 断言更新为"未设置"语义 |

## 分析

- **AC-1** ✅ mixed_mtls_integration AC-8 锁 SM4 拒 AES / AC-9 锁 AES 放行匹配，全部通过；server_serve 复刻同步真实协商语义（ac1-mixed-lock、ac1-summary）
- **AC-2** ✅ libobk session_test 锁定用例（SM4 错配回 OBK_HS_ERR_ALGORITHM+不升级；AES 匹配完整升级）exit=0；dmsbtex session_test 锁定用例通过且 ALL PASS（ac2-libobk-lock、ac2-dmsbtex-lock）
- **AC-3** ✅ e2e S18（锁 SM4 放行 SM4 客户端）/S19（拒 AES 客户端且输出含 algorithm 文案）通过（ac3-e2e-lock）
- **AC-4** ✅ e2e 场景矩阵 19/19——现有 S1-S17 不受影响即"未配置不锁"的向后兼容证明（ac4-compat）
- **AC-5** ✅ rpc_config cli_algorithm 代码残留为 0（仅说明性注释）；四模块协商层过滤分支确认（rpc-server.cpp:261 / rdbcomm server.c name 非空 / dmsbtex+libobk cfg->algorithm!=0）；服务端算法 sec_resolve_str default=NULL 确认（ac5-grep）

Grill 追问：
1. rdbcomm 为何最终用 algorithm_name 而非数值字段？→ 用户裁定统一"name 非空即锁"，消除派生字段，日志可直接打印配置名。
2. libobk 测试曾挂起/失败的原因？→ 匹配 probe 多发外部帧与 sbt_session_client_init 自带协商流程冲突；已修正为自包含流程。另发现 SM2_Test_CA 缺 T0388 前缀布局文件，锁定用例取 AES 规避并在注释注明。
3. 存量显式配置部署的影响？→ 协商从"偏好"收紧为"强制"正是需求本意；拒绝帧复用既有码，客户端经 T3956 文案可读。

## 适用边界

锁定仅在 mTLS 握手路径生效（明文模式无协商）；未设置算法的服务端无约束。rdbcomm 的 server_options.algorithm_name 由调用方持有生命周期（指向 sec_resolve 静态存储或 argv）。

## 下一轮建议

- 工作区遗留的用户改动（dmsbtex/sbt.c、libs/rdb-config.c/h 删除 sec_tls_client_cert_paths、dmsbtex/xmake.lua add_deps(tools)）未纳入本提交，待其完成后自行提交。
- libs/tests/certs/SM2_Test_CA 若需支持 SM2 客户端锁定测试，应补齐 sm2_ 前缀布局资产。

verdict: {"outcome": "confirmed", "reason": "五条 AC 全过：四模块锁定过滤+去重+兼容性均有自动化证据支撑", "verdict_id": "T3961-check-v1", "at": "2026-08-25T16:40:00+08:00"}
