---
schema: pdca.asset/v1
id: T0391-0824-certs-reprovision-dual-algo
phase: check
source_ids: [verify-log]
---

## 上下文

T0390 遗留事项①②：现网证书数据混乱导致 ED25519 链无效（连带协商下发错误 ca_cn）。本任务以 keygen 统一重签并规范化目录，双算法 mTLS 全链路恢复。

## 假设与结果

- **假设**：遗留②（协商 ca_cn 解耦）无需代码改动。→ **成立**：协商按算法取 profile CA CN 逻辑正确，重签消除数据污染后 ED25519 实机握手恢复。
- **假设**：SM2 根沿用可减少变更面。→ **成立**。

## 分析

- **AC-1** ✅ 根四件套链正确：sm2_host issuer=My_SM2_Root_CA；ed25519_host issuer=My_ED25519_Root_CA 且 openssl verify OK（sm2 CLI verify 需 SM2 provider 参数，以实机为准）（verify-log）
- **AC-2** ✅ My_SM2_Root_CA/ 与 My_ED25519_Root_CA/ 子目录各自自包含三件套且与根同源（sign -n 自动拷贝）（verify-log）
- **AC-3** ✅ 服务端日志 plain only/skipped/setup failed 计数 0（verify-log）
- **AC-4** ✅ 双算法实机握手成功：SM4 返回 sm2-final-ok、AES/ED25519 返回 ed-final-ok——遗留②实机关口打通（verify-log）
- **AC-5** ✅ certs 根仅保留规范文件与两个 CA 目录；残留移入 certs.migrated_20260824 / certs_bak_20260824_pre_t0391（verify-log）

可复核途径：records/T0391-0824-certs-reprovision-dual-algo/evidence/verify.log。

## 适用边界

- 主机证书 subject CN 为机器 UUID（create 流程从配置读取 CN），功能无碍；如需业务命名需调整 keygen create 的 CN 来源。
- 备份目录保留于 /opt/aio/cfg/ 下，确认稳定后可人工清理。

## 下一轮建议

- keygen create 的 CN 来源与 -n 参数语义可考虑统一（本轮范围外）。

## verdict

```json
{
  "outcome": "confirmed",
  "reason": "五条 AC 全部达成：链校验正确、目录自包含规范、服务端零降级、双算法实机握手成功",
  "verdict_id": "T0391-verdict-001",
  "at": "2026-08-24T13:41:00+08:00"
}
```
