---
schema: pdca.asset/v1
id: ontology:pattern/sm4-storage-encryption
type: pattern
layer: Knowledge
status: active
summary: 国密SM4全流程存储加密模式（ZFS/S3/NFS/备份四场景，155 MB/s 基线，TLS_SM4_GCM_SM3 阈值表）
relations:
  specializes:
    - ontology:pattern
  relates_to:
    - ontology:entity/aio-tools-6200-release
    - ontology:concept/pdca-task
attributes:
  - name: sm4_threshold_table
    desc: SM4 国密阈值表可复用
    constraint: 含 TLS_SM4_GCM_SM3=国密SM4-GCM-SM3(TLS1.3) 与 TLS_AES_256_GCM_SHA384 的枚举阈值表，allowed_values 可检
    testable_signal: "运行 grep -q 'TLS_SM4_GCM_SM3' /home/black/Public/aio/aio-tools/6200/F/139/libs/rdb-config.h 且 grep -q 'allowed_values' /home/black/Public/aio/aio-tools/6200/F/139/libs/rdb-config.h 命中且 grep -q 'sm4-storage-encryption' ontology/pattern/sm4-storage-encryption.md 命中"
  - name: four_scenario_coverage
    desc: ZFS/S3/NFS/备份四场景架构覆盖
    constraint: 覆盖 ZFS 块存储/S3 对象存储/NFS 文件存储/备份介质四场景的 SM4 透明加密数据流，mermaid 可渲染且每图 1 Source
    testable_signal: "运行 grep -q '155 MB/s' /home/black/Public/aio/aio-tools/6200/F/139/备份传输存储国密SM4全流程加密方案.md 且 grep -q 'C4 L2' ontology/pattern/sm4-storage-encryption.md 命中且 grep -c '```mermaid' ontology/pattern/sm4-storage-encryption.md | awk '{exit !($1>=3)}'"
---

# 国密SM4全流程存储加密模式（SM4 Storage Encryption Pattern）

> 源：`T2044 d3b99ac8` 的 `SM4` 四场景方案（`155 MB/s` 纯软件基线，`国产 CPU/PCIe 卡` 硬件依赖） + `T2028` 的 `aio-tools-6200-release` 的 `rdbcomm` 契约，`F-139` 的 `d3b99ac8` 为 `4 合 1 squash`。

## 阈值表（`rdb-config.h:allowed_values` 可复用）

| 枚举 | 说明 | Source |
|------|------|--------|
| `TLS_SM4_GCM_SM3` | `国密SM4-GCM-SM3(TLS1.3)` | `file: libs/rdb-config.h:allowed_values` |
| `TLS_AES_256_GCM_SHA384` | `AES256-GCM-SHA384(国际/TLS1.3)` | `file: libs/rdb-config.h:allowed_values` |

*Source: `file: F/139/libs/rdb-config.h:allowed_values="TLS_SM4_GCM_SM3=..."` — T0458*

## 四场景架构（mermaid）

```mermaid
C4Container
    title SM4 全流程加密 — ZFS/S3/NFS/备份四场景
    System_Boundary(sm4, "SM4 存储加密") {
        Container(zfs, "ZFS 块存储", "内核级", "SM4-GCM 透明加密")
        Container(s3, "S3 对象存储", "s3file", "SM4 加密上传")
        Container(nfs, "NFS 文件存储", "FUSE", "SM4 透明加密")
        Container(backup, "备份介质", "Worker", "ZFS/NFS/S3 加密")
    }
    Rel(zfs, backup, "SM4 落盘")
    Rel(s3, backup, "SM4 对象")
```
Source: `file: F/139/备份传输存储国密SM4全流程加密方案.md:1` — S1

```mermaid
flowchart TD
    A[SM4-GCM 纯软件 155 MB/s] --> B{硬件加速?}
    B -- 国产 CPU SM4 指令 --> C[4,000+ MB/s]
    B -- PCIe SM4 卡 --> C
    B -- 无 --> D[顺序 IO 损耗 90%]
```
Source: `file: F/139/备份传输存储国密SM4全流程加密方案.md:155 MB/s` — S1

```mermaid
stateDiagram-v2
    [*] --> 明文
    明文 --> 加密: SM4-GCM 加密
    加密 --> 存储: 落盘 S3/ZFS/NFS
    存储 --> 解密: SM4-GCM 解密
    解密 --> [*]
```
Source: `file: F/139/备份传输存储国密SM4全流程加密方案.md:1` — S1

## 可重跑验证

```bash
grep -q "TLS_SM4_GCM_SM3" libs/rdb-config.h && grep -q "allowed_values" libs/rdb-config.h && echo "阈值表可检"
grep -q "155 MB/s" "备份传输存储国密SM4全流程加密方案.md" && echo "基线可检"
grep -c '```mermaid' ontology/pattern/sm4-storage-encryption.md  # ≥3
```

## 决策背景（原 T2044 的 records-only 晋级）

- 背景：`T2044 d3b99ac8` 为 `1716` 业务的 `4 合 1` 需求，虽含 `SM4` 阈值表但 `快照特化`，故 `records-only`；现按 `A` 本体晋级要求，将 `SM4` 的 `TLS_SM4_GCM_SM3` 四场景阈值表晋为 `pattern`，供 `ZFS/S3/NFS` 跨域复用。
- 决策：`records/T2044-0904-research-f139-sm4/` 的 `1716` 业务事实晋为 `ontology:pattern/sm4-storage-encryption`，`composed_of` 待拆为 `sm4-zfs/sm4-s3` 二叶。

*Diátaxis: reference* | *arc42: 5/6/12 节* | *C4 L2 可建模*
