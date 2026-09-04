---
schema: pdca.asset/v1
id: ontology:domain/tls-handshake-reject-frame-consistency
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/tls-handshake-reject-frame-consistency/1.0.0
summary: 跨模块握手错误帧一致性审查要点
domain:
- ontology:domain/tls
relations:
  specializes:
  - ontology:domain/tls
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# 跨模块握手错误帧一致性审查要点

## 统一范式（rdbcomm / dmsbtex / rpc / libobk）

- **握手 body 网络序**：`rdbcomm` 经 sshbuf `POKE_U16`/`PEEK_U16` 大端写读
  （`libs/buf.h`）；`dmsbtex`/`libobk` 显式 `htons`/`ntohs`；`rpc` 结构体 `htons`/`ntohs`。
- **每条拒绝分支必须回送明确错误码帧**，不允许直接断开；且与同协议其他拒绝路径
  及对端模块行为一致（fail-closed，不降级）。
- 拒绝码枚举尚未归一：`RDB_HS_ERR_*` / `DM_HS_ERR_*` / `HS_ERR_*` / `OBK_HS_ERR_*`
  （follow-up：归一到 `libs` 单一来源）。

## 审查易漏点（清单）

- 服务端某拒绝分支（如 `ca_cn unavailable`）漏发帧，与其余分支/对端不一致 →
  客户端拿不到明确错误码、可诊断性弱。审查时逐分支核对「每条错误路径都回送帧」。
- 仅改单模块网络序时，须确认其余模块已同构，避免跨模块字节序错位。

## 关联

- T0362：libobk 握手 body 网络序改造（M5）。
- T0363：dmsbtex `ca_cn` 缺帧修复 + 四模块一致性审查（本知识来源）。
