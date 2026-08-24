---
schema: pdca.asset/v1
id: T0390-0824-server-partial-profile-degrade
phase: check
source_ids: [fix-patch, verify-log]
---

## 上下文

用户质询"默认不是使用国密的吗"——服务端 init_server 全有或全无语义使无效的 ED25519 链连坐国密 SM4，mTLS 整体不可用（plain only）。

## 假设与结果

- **假设**：降级为尽力收集即可恢复国密。→ **成立**：实机 plain only 消失、国密握手成功。
- **假设**：循环改造不影响既有行为。→ **修正一次**：tmp_slot 中转版曾致 mtls_handshake 行为漂移，改为保持原直接写槽+失败 memset 回滚的保守实现后全绿；基线对照确认非数据问题。

## 分析

- **AC-1** ✅ tls_cert_init_server_partial_degrade：SM4 有效+ED25519 缺失时 init OK、get_ssl_ctx(SM4)!=NULL、get_ssl_ctx(AES)==NULL（verify-log）
- **AC-2** ✅ 双算法全缺失目录 init 返回非 OK 且 ctx=NULL，plain only 兜底保留（verify-log）
- **AC-3** ✅ 实机重启 aio-speedd：日志 serving plain only 出现 0 次，aio-speed 默认国密 mTLS 握手成功执行 ls -alh（verify-log）
- **AC-4** ✅ tls_cert_test All PASSED / rdb_config_test 16 passed / rdbcomm ALL PASS / 全量构建无错误（verify-log）

可复核途径：records/T0390-0824-server-partial-profile-degrade/evidence/verify.log。

## 适用边界

- 服务端日志对失败 profile 输出 ErrorLog（算法名可见）；部分成功时 main.cpp 不再打 "serving plain only"。
- 现网 ED25519 根目录证书数据仍无效（ed25519_ca.crt 实为 MySM2RootCA 内容、host.crt 由无关 UUID CA 签发），AES mTLS 在修复数据前持续跳过——属运维事项。

## 下一轮建议

- 现网证书体系混乱（多 CA 混名），建议以 keygen 统一重签并文档化目录规范。
- 服务端协商 ca_cn 与客户端算法偏好的解耦问题（T0388 遗留）待单独 triage。

## verdict

```json
{
  "outcome": "confirmed",
  "reason": "四条 AC 证据齐备：单测覆盖降级与兜底两分支、回归零失败、实机国密恢复",
  "verdict_id": "T0390-verdict-001",
  "at": "2026-08-24T12:37:30+08:00"
}
```
