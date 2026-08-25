---
schema: pdca.asset/v1
id: T3959-0825-fta-mtls-cli-args
phase: check
source_ids: [ac1-help, ac2-invalid-exit, ac3-cli-override, libobk-session-test, ac4-e2e-matrix]
---

## 上下文

用户报告 dm-ftp/FileTransferAgent 缺少 mTLS/算法 CLI 参数。对齐 aio-speedd/rdbcommd 既有 CLI 覆盖模式实施：main.c 新增严格校验的长选项，sbt_server_tls_config_init 签名扩展支持 CLI 覆盖（commit 1259994f，libobk 1.0.1.5）。

## 假设与结果

| 假设 | 结果 |
|------|------|
| CLI 显式值覆盖 sec_resolve 解析值，未指定时行为不变 | 成立：场景 C（env=0+CLI=1→255）/B（无参数→124 对照） |
| 非法值 fail-closed 非零退出 | 成立：=2/=abc/TLS_BOGUS 均 255 并输出明确错误 |
| 算法 CLI 覆盖生效 | 成立：场景 E（env 非法算法+CLI 合法→正常监听 124），D（env 非法无 CLI→255） |

## 分析

- **AC-1** ✅ --help 含 --mtls-enable/--tls-algorithm 说明与优先级文档（ac1-help）
- **AC-2** ✅ 三组非法值均 exit=255 且输出 "invalid ..." 明确错误（ac2-invalid-exit）
- **AC-3** ✅ 行为级验证：CLI mtls=1+坏证书目录 → prepare 失败退出；CLI 覆盖 env 直接证据（场景 C/E）（ac3-cli-override）。注：Info 日志全缓冲且 Info 级不主动 flush，"日志含 mTLS enabled"改用 prepare 行为差异验证（更硬的信号）
- **AC-4** ✅ 不传新参数行为不变（对照场景 B）；libobk_session_test/dmsbtex_session_test/e2e 17/17 回归通过（libobk-session-test、ac4-e2e-matrix）；session_test 两处旧签名调用已同步
- **AC-5** ✅ getopt 层 strtol 全串校验（0/1）+ 算法白名单 strcmp，非法无法进入配置层（ac2-invalid-exit）

Grill 追问：
1. 为何 AC-3 用行为验证而非日志文本？→ logger 文件模式全缓冲、Info 级不 flush，SIGTERM 下丢失；prepare 失败/成功是更强且稳定的行为信号。
2. args_process 返回值此前被忽略是否属缺陷？→ 是既有问题，本任务因新校验需要而补上检查；default 分支 exit(0) 的历史行为保持不变（范围外）。
3. cert-dir 无 CLI 是否影响可用性？→ env RPC_TLS_CERT_DIR/ini 已可配置，与 aio-speedd 服务端一致（其亦无 cert-dir CLI）。

## 适用边界

适用于 FileTransferAgent 单次启动覆盖；持久配置仍走 env/ini。sbt_server_tls_config_init 新签名的调用方必须显式传 (-1, NULL) 表示不覆盖。

## 下一轮建议

- 可选：default 分支 `exit(0)` 改为非零（历史行为，涉及所有工具 usage 一致性，宜统一处理）。
- 可选：FileTransferAgent 纳入 e2e 场景矩阵常态化回归。

verdict: {"outcome": "confirmed", "reason": "五条 AC 全过：CLI 参数/白名单校验/覆盖优先级/回归均由行为级证据支撑", "verdict_id": "T3959-check-v1", "at": "2026-08-25T14:54:00+08:00"}
