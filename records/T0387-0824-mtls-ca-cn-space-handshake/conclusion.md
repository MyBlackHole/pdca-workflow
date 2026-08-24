---
schema: pdca.asset/v1
id: T0387-0824-mtls-ca-cn-space-handshake
phase: check
source_ids: [fix-patch, verify-log, keygen-test-src]
---

## 上下文

aio-speed mTLS 握手失败（tls_cert_init_client failed, ca_cn="My SM2 Root CA"）。用户裁决修复方向：keygen 强制无空格 CN、客户端校验保持严格、SM2 布局缺口不处理。

## 假设与结果

- **假设**：CN 校验收敛到生成源头即可恢复握手链路。→ **成立**：重签部署后实机握手成功。
- **假设**：改动不引入回归。→ **成立**：核心测试全绿；3 个环境性失败经 stash 基线对照证实与本次无关。

## 分析

- **AC-1** ✅ tls_keygen_test 5/5 通过：空格 CN 拒绝、合法字符集通过、".." 与元字符拒绝（keygen-test-src + verify-log）
- **AC-2** ✅ CLI 黑盒：`ca -n "My SM2 Root CA"` exit=1 且输出合法字符集提示与改名示例；合法 CN exit=0（verify-log）
- **AC-3** ✅ 重签 My_SM2_Root_CA CA 并按双布局部署后，`aio-speed --mtls-enable 1` 以 TLS_SM4_GCM_SM3 完成握手并返回 `ls -alh` 结果（verify-log）
- **AC-4** ✅ tls_cert_test All PASSED / rdb_config_test 16 passed / rdbcomm_handshake_session ALL PASS；rpc_handshake_test、rpc_own_handshake_test、rdbcomm_tool_integration 为既有环境性失败（基线对照一致，非本次引入）（verify-log）

可复核途径：records/T0387-0824-mtls-ca-cn-space-handshake/evidence/verify.log 含全部命令与退出码。

## 适用边界

- 行为变更：keygen 从此拒绝含空格 CN 的 ca/create/sign——依赖旧命名的自动化脚本需改用 [A-Za-z0-9._-] 命名。
- 存量带空格 CN 的证书必须重签（本次已为 /opt/aio/cfg/certs 完成并备份至 certs_bak_20260824）。
- SM2 文件名布局缺口（客户端仅找 cert_dir/<ca_cn>/host.*）仍存在——本轮裁决不处理，部署时需将 sm2_host.* 摆放为 host.*。

## 下一轮建议

- 布局缺口若后续要收敛，建议以"解析侧回退 sm2_host.*"立项（对称 ED25519 pick 模式）。
- rpc_handshake_test 等 3 个环境性失败的根因值得单独 triage。

## verdict

```json
{
  "outcome": "confirmed",
  "reason": "四条 AC 全部有证据支撑：TDD 单测绿、CLI 黑盒符合预期、实机 mTLS 握手成功、回归无新失败",
  "verdict_id": "T0387-verdict-001",
  "at": "2026-08-24T11:09:30+08:00"
}
```
