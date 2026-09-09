# 存储国密加密方案落地调研（T2107·纯调研）

## 背景

依据《存储国密加密技术方案.md》（`/home/black/Public/aio/F/143/存储国密加密技术方案.md`），调研其在本项目（`/home/black/Public/aio/aio-tools/6200/F/143`）的落地差距。ZFS内核不在本仓，只做承接（记外部依赖）。

Grill对齐（round1-2，均captured:true）：范围=三类全覆盖；深度=行号级定位、结论可复核。

## 目标

产出`research-report.md`：三类差距定位到文件行号、落改点清单、Y1-Y7对齐矩阵。不改代码。

## 范围

输入：方案文档 + 本仓源码（s3tools、rpc等）。
输出：`research-report.md`（≥3 mermaid图、≥3 Source、含http来源）。
不做：不改代码、不跑实测、不涉及容量与密钥轮换。

## 验收标准

- [ ] AC-1 三类差距均定位到文件行号，`grep`+`Read`可重走
- [ ] AC-2 落改点清单完整（参数、元数据、分支语义、清单字段）
- [ ] AC-3 Y1-Y7对齐矩阵完整，外部依赖与非目标与方案一致
- [ ] AC-4 报告通过先调研门禁（mermaid≥3、Source≥3、http Source≥1、URLs≥2）
- [ ] AC-5 全程零代码改动（`git status`干净可验）
- [ ] AC-6 本体沉淀可验收：结论含`## 本体沉淀`节并点名`ontology:`节点决策，`disposition.reason`含`ontology:`，有ontology文件反向引用本record

## 关联本体节点

```
ontology:pattern/sm4-storage-encryption
ontology:pattern/sm4-s3-encryption
ontology:pattern/sm4-zfs-encryption
ontology:concept/pdca-task
ontology:concept/pdca-evidence
ontology:concept/pdca-verdict
```

本体产出计划：Check结论给出沉淀决策——若落改点有可复用模式增量则给`ontology:pattern/sm4-storage-encryption`加修订记录R3（或补`sm4-s3`落改细节），否则`records-only`并写明理由；Act满足沉淀校验（conclusion`## 本体沉淀`节 + `disposition.reason`含`ontology:` + 有ontology文件反向引用本record）。

## 拆分映射

- 差距定位与落改点清单 -> ontology:concept/pdca-task
- Y对齐矩阵与外部依赖 -> ontology:concept/pdca-evidence
- 报告门禁与零改动验证 -> ontology:concept/pdca-verdict
