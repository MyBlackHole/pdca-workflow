---
schema: pdca.asset/v1
id: T0388-0824-client-cert-name-by-algorithm
phase: check
source_ids: [fix-patch-v2, verify-log-v2]
---

## 上下文

T0387 遗留的 SM2 布局缺口转为正式需求：tls_cert_init_client 按算法获取对应证书名。用户裁决：SM2 仅前缀子目录布局（含 CA）、ED25519 现状不动；Do 中途追加"keygen sign -n 拷贝 CA 进输出目录"。

## 假设与结果

- **假设**：SM2 布局内聚于 build_client_profile 即可，无需动 slot_create。→ **成立**：仅前缀策略下无回退分支需求。
- **假设**：改动不影响 ED25519 与服务端。→ **成立**：既有断言零修改通过，实机双算法协商正常。

## 分析

- **AC-1** ✅ SM4 下 build_client_profile 返回 cert_dir/<ca_cn>/sm2_ca.crt、sm2_host.crt、sm2_host.key（路径断言通过）（verify-log）
- **AC-2** ✅ 新增 tls_cert_init_client_sm2_prefixed_layout 集成用例：临时目录仅 sm2_* 三件套 init 成功；实机 My_SM2_Root_CA 目录按新布局握手成功返回 mtls-ok（verify-log）
- **AC-3** ✅ tls_ed25519_dual_format 等既有用例零修改通过，ED25519 路径与回退行为不变（verify-log）
- **AC-4** ✅ tls_cert_test All PASSED / rdb_config_test 16 passed / rdbcomm_handshake_session ALL PASS / 全量构建无错误（verify-log）
- **AC-5** ✅ sec_tls_client_cert_paths 注释标注布局边界（仅 host.* 旧布局）；Go 侧 oss 为独立场景（cert_dir/<前缀>_host.*），三者差异已在注释与本文档留痕（fix-patch）

可复核途径：records/T0388-0824-client-cert-name-by-algorithm/evidence/verify.log。

## Check 阶段用户质询修正（build_client_profile 问题）

用户指出 build_client_profile 有问题，实测复现：ED25519 场景 CA 固定取 cert_dir 根、cert/key 固定无前缀 host.*，
在现网 MySM2RootCA 目录（仅 sm2_host.*）下双双落空。已修正为与 SM2 对称的子目录布局：
- ED25519 返回 `<ca_cn>/ed25519_ca.crt + ed25519_host.{crt,key}`；先查前缀名，缺失由 slot_create
  pick_ed25519_* 下沉同目录 ca.*/host.*（用户澄清语义，既有机制保留）；
- 7 处测试 fixture 同步补子目录 CA；identity_binding 用例等价迁移至子目录拼接构造；
- ED25519 实机：客户端新布局 init 成功，握手仍被服务端 alert 拒绝——服务端协商下发
  ca_cn=MySM2RootCA 与 AES 组合不匹配所致，改动前该场景更早失败（缺文件），非本次回归；
  服务端协商策略建议另行 triage。

## 适用边界

- SM2 客户端自此仅认 `cert_dir/<ca_cn>/sm2_ca.crt + sm2_host.{crt,key}` 自包含布局；旧的根目录 CA + 子目录 host.* 组合对 SM2 不再生效。
- keygen sign -n 输出目录新增 CA 拷贝件（sm2_ca.crt），目录自包含。
- Go oss 工具与 rdb-config sec_tls_client_cert_paths 布局语义未变。
- ED25519 证书名选择顺序（用户澄清确认）：先默认检查 `ed25519_ca.*`/`ed25519_host.*`，文件缺失时下沉使用同目录 `ca.crt`/`host.*`（slot_create pick_ed25519_* 实现的语义，本次零改动保留）。SM2 仅认 sm2_* 前缀，无下沉。

## 下一轮建议

- 存量 UUID 目录（ca.crt+host.* 无前缀布局）如需迁移到 SM2 新布局，可考虑 keygen 提供 migrate 子命令（本轮范围外）。

## verdict

```json
{
  "outcome": "confirmed",
  "reason": "五条 AC 全部有证据支撑：路径断言、集成用例、实机新布局握手、回归全绿、一致性差异留痕",
  "verdict_id": "T0388-verdict-001",
  "at": "2026-08-24T11:29:00+08:00"
}
```
