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
    testable_signal: "运行 grep -q 'enc-algo' /home/black/Public/aio/F/143/存储国密加密技术方案.md 命中且 grep -q '管理侧清单' /home/black/Public/aio/F/143/存储国密加密技术方案.md 命中且 grep -q 'sm4-nfs-encryption' ontology/pattern/sm4-nfs-encryption.md 命中"
---

# SM4 NFS 文件存储加密子模式

> 源：`sm4-storage-encryption` 的 `NFS` 四场景之一；方案文档`§3.3`

## 架构

```mermaid
flowchart LR
    SRC["数据源"] -->|"TLS-SM4已具备"| WK["Worker aio-speed"]
    WK -->|"enc-algo预加密"| NFS["NFS密文+管理侧清单"]
    NFS -->|"按清单解密"| RST["恢复写回"]
```
Source: `file: /home/black/Public/aio/F/143/存储国密加密技术方案.md:§3.3`

## 落改要点（F/143）

- 现状约束：全仓无 `enc-algo` 语义；静态 XOR 非合规，不计入合规；传输 TLS 已具备，保持不变。
- 清单模型：算法/nonce/长度/校验和四字段由管理侧清单维护；半写按清单识别清理，下次重传收敛。
