---
schema: pdca.asset/v1
id: ontology:pattern/gm-symmetric-modes
type: pattern
layer: Knowledge
status: active
summary: 对称模式选型模式：按认证/随机访问/盘加密三力权衡 ECB/CBC/CTR/XTS/GCM/CCM
relations:
  specializes:
  - ontology:pattern
  guides:
  - ontology:domain/gm-algorithm-suite
  relates_to:
  - ontology:domain/backup-crypto-gm-support-surfaces
attributes:
- name: decision_coverage
  desc: 三力决策覆盖（是否需AEAD/是否需随机访问/是否盘加密）
  constraint: 须覆盖 ECB(禁用)/CBC(串行需HMAC)/CTR(并行需HMAC)/XTS(盘加密)/GCM(AEAD一体)/CCM(可替) 的判定路径
  testable_signal: "运行 grep -q '是否需认证' ontology/pattern/gm-symmetric-modes.md && grep -q '盘.*加密' ontology/pattern/gm-symmetric-modes.md && grep -q 'GCM' ontology/pattern/gm-symmetric-modes.md"
- name: gcm_completeness
  desc: GCM/CCM 的 AEAD 一体性与 IV 唯一性约束
  constraint: 须含 GCM(CCM 为 AEAD，IV/nonce 不可重用，ZFS 12B 约束为实例)
  testable_signal: "运行 grep -q 'AEAD' ontology/pattern/gm-symmetric-modes.md && grep -q '不可重用' ontology/pattern/gm-symmetric-modes.md"
---

# 对称模式选型模式

## 上下文

存储或传输场景需为 `SM4/AES` 等分组密码选择工作模式，面临 `认证 / 并行 / 随机访问 / 填充 / IV` 五力权衡；`GM/T 0018` 的 `SDF` 版本差异（`2012` 仅 `ECB/CBC`，`2023` 增 `GCM`）进一步约束可选集。

## 问题

如何在 `ECB/CBC/CFB/OFB/CTR/XTS/GCM/CCM` 中选择满足 `认证 / 随机访问 / 盘加密` 的模式，避免 `ECB` 泄露、`CBC` 串行、`OFB` 预计算失效及 `GCM/CCM` 的 `IV` 重用灾难。

## 解

按三力逐级分流，`认证` 为首要分水岭：

```mermaid
flowchart TD
    START([新存储加密选型]) --> Q0{是否需认证 AEAD?}
    Q0 -- 是 --> Q1{是否需随机访问?}
    Q1 -- 是 --> GCM[GCM：CTR+GHASH<br/>AEAD 并行 无填充<br/>IV 12B不可重用]
    Q1 -- 否 --> CCM[CCM：CBC-MAC+CTR<br/>AEAD 串行 需填充]
    Q0 -- 否 --> Q2{是否盘/扇区加密?}
    Q2 -- 是 --> XTS[XTS：tweak=LBA<br/>盘加密专用<br/>需双密钥 窃取法]
    Q2 -- 否 --> Q3{是否流且可预计算?}
    Q3 -- 是 --> CTR[CTR：计数器<br/>均并行 需HMAC]
    Q3 -- 否 --> Q4{是否需隐藏相等性?}
    Q4 -- 是 --> CBC[CBC：链式<br/>加密串行 需HMAC]
    Q4 -- 否 --> ECB[ECB：独立块<br/>禁用 泄露相等性]
```

`GCM`（`CTR+GHASH` 并行）与 `CCM`（`CBC-MAC+CTR` 认证串行）为唯二 `AEAD` 一体方案；`XTS`（`tweak=LBA` 窃取法）为盘加密专用无需额外存储；`CTR` 为并行最佳但需外加 `HMAC`；`CBC/CFB/OFB` 为流/链式，无认证且分别串行。

## 后果

- `ECB` 任何存储场景禁用（同明文同密文）；`CBC/CFB/OFB` 无认证，需 `HMAC` 补且 `OFB` 完全串行、`CBC` 加密串行。
- `GCM/CCM` 的 `IV/nonce` 绝不可重用（`GCM` 重用泄露 `GHASH` 密钥，`ZFS` 为 `12B` 约束）；`CCM` 认证串行略低于 `GCM`。
- `2012` 版 `SDF` 仅 `ECB/CBC`，若目标仅 `GCM`（如 `ZFS SM4 GCM-only`）则存量卡零收益，需 `2023` 版 `SGD_SM4_GCM` 或 `CPU sm4-ce-gcm`。

## 实例

| 场景 | 推荐 | 理由 |
|------|------|------|
| 块存储 `AEAD` 随机访问 | **GCM** | 唯一 `AEAD` 并行一体，现货 `sm4-ce-gcm` |
| 全盘 `FDE` | **XTS**（+可选 `HMAC`） | `tweak=LBA` 隐藏同扇区相等性 |
| 文件名/小流 | `CFB/CTS` | 流无填充 |
| 存量卡 `CBC` | `CBC+HMAC` | 成熟但串行 |

## 门禁

- `grep -q '是否需认证' ontology/pattern/gm-symmetric-modes.md && grep -q 'GCM' ontology/pattern/gm-symmetric-modes.md && grep -q 'AEAD' ontology/pattern/gm-symmetric-modes.md`
- `python3 scripts/ontology-validate.py --ontology-dir ontology` 0 issues
