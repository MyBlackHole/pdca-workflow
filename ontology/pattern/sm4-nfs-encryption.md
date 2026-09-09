---
schema: pdca.asset/v1
id: ontology:pattern/sm4-nfs-encryption
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-09
dcterms_modified: 2026-09-09
owl_versionIRI: http://pdca.local/ontology/sm4-nfs-encryption/1.0.0
summary: SM4 NFS 文件存储加密子模式（aio-speed预加密落盘，原文件名+管理侧清单）
relations:
  specializes:
    - ontology:pattern/sm4-storage-encryption
  relates_to:
    - ontology:entity/aio-tools-6200-release
attributes:
  - name: nfs_sm4_preencrypt
    desc: NFS客户端SM4预加密后落盘可测
    constraint: aio-speed新增--enc-algo语义，密文按原文件名写入NFS，算法/nonce/长度/校验和由管理侧清单维护
    testable_signal: "运行 grep -q 'enc-algo' records/T2125-0910-guomi-storage-research2/evidence/research-report.md 命中且 grep -q 'sm4-nfs-encryption' ontology/pattern/sm4-nfs-encryption.md 命中"
---

# SM4 NFS 文件存储加密子模式

> 源：`sm4-storage-encryption` 的 `NFS` 四场景之一；落改重验 `records/T2125-0910-guomi-storage-research2/`（结论 `confirmed`）

## 架构

```mermaid
flowchart LR
    SRC["数据源"] -->|"TLS-SM4已具备"| WK["Worker aio-speed"]
    WK -->|"enc-algo预加密"| NFS["NFS密文+管理侧清单"]
    NFS -->|"按清单解密"| RST["恢复写回"]
```
Source: `file: records/T2125-0910-guomi-storage-research2/evidence/research-report.md:§3.3`

## 落改要点（F/143）

- 现状：全仓无 `--enc-algo`；`--encrypt` 系静态 XOR（`rpc-common.cpp:446`），不得计入合规；传输 `--tls-algorithm TLS_SM4_GCM_SM3` 已具备不动。
- 清单四字段：算法/nonce/长度/校验和由备份管理侧维护；半写按清单识别清理重传。
