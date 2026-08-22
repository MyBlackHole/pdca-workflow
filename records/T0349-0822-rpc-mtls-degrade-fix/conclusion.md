---
schema: pdca.asset/v1
id: T0349-0822-rpc-mtls-degrade-fix
phase: check
source_ids: ["integration-7case", "regression"]
---

## 上下文

T0348 审查发现 F1/F2/F3 三缺陷。F3 语义经用户澄清：证书 init 失败无需阻止服务启动，只需使客户端 mTLS 不可用。

## 假设与结果

- **AC-1 (F1)** client mtls=1 收 PLAIN：`PASS` — ErrorLog "downgraded to plain" 且 exit 255 非 0
- **AC-2 (F2)** 空 ca_cn：`PASS` — server 回 HS_ERR_CA_CN(0x8006) 且 ErrorLog 含 cert_dir/算法
- **AC-3 (F3)** cert init 失败不 exit：`PASS` — WarningLog "serving plain only" 后正常监听
- **AC-4** 强制拒绝路径：`PASS` — !sctx 握手补发 MTLS_REQUIRED（原静默断开），client 业务命令 exit 255
- **AC-5** 回归：`PASS` — plain/mixed/forced 全通，tls_cert_test 8 用例无回归

## 分析

7 用例集成测试全绿；关键行为变化：server 侧错误留在 server 日志可诊断位置，client 语义化失败而非静默降级。

## 适用边界

仅 rpc 目录；libs/tls_cert.c 本轮未动（可观察性已由 T0346 交付）。

## 下一轮建议

- execute_shell_script 帧校验模式推广至 download/upload 等 recv 点。
