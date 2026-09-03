---
schema: pdca.asset/v1
id: ontology:pattern/gm-symmetric-modes
type: pattern
layer: Knowledge
status: active
summary: 国密对称模式选型模式：ECB/CBC/CFB/OFB/CTR/XTS/GCM/CCM 存储适配与 GCM 过滤器
relations:
  specializes:
  - ontology:pattern
  guides:
  - ontology:domain/gm-algorithm-suite
  - ontology:domain/zfs-crypto
  relates_to:
  - ontology:domain/backup-crypto-gm-support-surfaces
attributes:
- name: mode_selection
  desc: 模式选型判定（并行/认证/随机访问/IV约束）
  constraint: 须覆盖 ECB(禁用)/CBC(串行需HMAC)/GCM(AEAD一体，ZFS现货)/XTS(盘加密)/CCM(可替) 的判定
  testable_signal: "运行 grep -q 'GCM.*AEAD' ontology/pattern/gm-symmetric-modes.md 且 grep -q 'XTS.*盘加密' ontology/pattern/gm-symmetric-modes.md 且 grep -q 'ECB.*禁用' ontology/pattern/gm-symmetric-modes.md"
- name: gcm_filter
  desc: GCM 硬筛选：ZFS仅GCM，存量卡ECB/CBC 零收益
  constraint: 采购以 SGD_SM4_GCM(2023版) 为验收项，否则无论性能零收益
  testable_signal: "运行 grep -q 'SGD_SM4_GCM' ontology/pattern/gm-symmetric-modes.md && grep -q 'SDF_GetDeviceInfo' ontology/pattern/gm-symmetric-modes.md"
---

# 国密对称模式选型模式

> Source: `records/T0539-0903-research-zfs-pcie-sm4/evidence/research-report.md:§2.1`（`GM/T 0018-2012/2023` + `ZFS sm4.c:13 GCM-only`）

## 决策树

```mermaid
flowchart TD
    START([新存储加密选型]) --> Q0{是否需认证 AEAD?}
    Q0 -- 是 --> Q1{是否需随机访问?}
    Q1 -- 是 --> GCM[GCM：CTR+GHASH<br/>AEAD 并行 无填充<br/>ZFS现选 sm4-ce-gcm 400<br/>IV 12B绝不可重用]
    Q1 -- 否 --> CCM[CCM：CBC-MAC+CTR<br/>AEAD 串行 需填充<br/>可替GCM 性能略低]
    Q0 -- 否 --> Q2{是否盘/扇区加密?}
    Q2 -- 是 --> XTS[XTS：tweak=LBA<br/>盘加密专用 无额外存储<br/>需双密钥]
    Q2 -- 否 --> Q3{是否流且可预计算?}
    Q3 -- 是 --> CTR[CTR：计数器<br/>均并行 最佳<br/>需外加HMAC]
    Q3 -- 否 --> Q4{是否需隐藏相等性?}
    Q4 -- 是 --> CBC[CBC：链式<br/>加密串行 需HMAC<br/>存量卡主力]
    Q4 -- 否 --> ECB[ECB：独立块<br/>禁用 泄露相等性]

    GCM --> FILT{GCM过滤器<br/>ZFS仅GCM}
    CCM --> FILT
    XTS --> FILT
    CTR --> FILT
    CBC --> FILT
    ECB --> FILT
    FILT -- SGD_SM4_GCM? --> PASS[采购通过<br/>SDF_GetDeviceInfo 含GCM]
    FILT -- 无GCM --> FAIL[存量卡零收益<br/>2023新卡/定制 或 CPU sm4-ce-gcm]
```

## 速查表

| 场景 | 推荐 | 理由 |
|------|------|------|
| ZFS 数据块（`sm4.c GCM-only`） | **GCM** | 唯一 `AEAD` 现货，`sm4-ce-gcm 400` 原生，`PMULL` 加速 |
| 全盘/FDE（`FDE`） | **XTS**（+可选 `HMAC`） | `tweak=LBA` 隐藏同扇区相等性，`fscrypt XTS` 用 |
| 小文件/文件名 | `CFB/CTS` | 流无填充，`fscrypt` 文件名用 |
| IPSec（国际） | `CBC` | 成熟，存量卡 `CBC-HMAC` 主力 |

## GCM 过滤器（硬约束）

- `GM/T 0018-2012` `SDF` 仅 `ECB/CBC/CFB/OFB`，**无 `GCM`**；`2023` 版新增 `SGD_SM4_GCM/CCM/XTS/CTR`，`ZFS` 仅 `SM4-GCM`（`sm4.c:13`），**存量卡 `CBC` 对 `ZFS GCM` 零收益**。
- 采购验收：`SDF_GetDeviceInfo` 的 `SymAlgAbility` **含 `SGD_SM4_GCM`** 否则无论 `22Gbps` 零收益；现货仅 `CPU sm4-ce-gcm`（`1.7GB/s`）与 `2023定制卡`。

## 门禁

- `grep -q 'GCM.*AEAD' ontology/pattern/gm-symmetric-modes.md && grep -q 'SGD_SM4_GCM' ontology/pattern/gm-symmetric-modes.md && grep -q 'XTS.*盘加密' ontology/pattern/gm-symmetric-modes.md`
- `python3 scripts/ontology-validate.py --ontology-dir ontology` 0 issues
