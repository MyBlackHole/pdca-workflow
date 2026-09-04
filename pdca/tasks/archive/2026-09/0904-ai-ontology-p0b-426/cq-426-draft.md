# T2038 P0-b：426 全量 20 CQ 草拟（复用 P0-a 10 CQ 模板，5 域采样）

> 任务：`T2038 0904-ai-ontology-p0b-426` · 阶段：Do · 复用 `T2034` 的 `10 CQ` 模板（`pdca 50`）外扩至 `426` 5 域

## 20 CQ（每 20 节点 1 CQ，5 域采样，`426/20≈20`）

| # | 域 | CQ | 覆盖本体 | 复杂度 |
|---|----|----|----------|--------|
| CQ-1 | `pdca` | `pdca-task` 的 6 场景如何路由到 `flow-do` 6 路径？ | `pdca-task`+`flow-do` | 单对象 |
| CQ-2 | `pdca` | `GRILLING_MISSING` 在 `research/thin` 下的 `frontier` 如何算？ | `flow-plan`+`grilling` | Reification |
| CQ-3 | `pdca` | `TICKETS_MISSING` 对 `research` 免检的 `allValuesFrom` 如何验？ | `triage`+`children` | 限制 |
| CQ-4 | `pdca` | `JOURNAL_MISSING` 的 `T{id}` 在 `journal` 的 `SPARQL` 如何查？ | `flow-act`+`write-journal` | 单数据 |
| CQ-5 | `pdca` | `convergence` 的 `text==Plan` 如何 `normalize-space` 后比？ | `verify-convergence` | 限制 |
| CQ-6 | `core` | `core-btree` 的 `split` 契约如何 `proptest` 验 `enomem` 重启？ | `core-btree-split` | 限制 |
| CQ-7 | `core` | `lmdb` 的 `VL32` 无 `mmap` 门禁如何 `build` 验？ | `lmdb-vl32` | 单数据 |
| CQ-8 | `core` | `benchmark` 的 `paired-comparison` 噪声如何 `small-pack` 滤？ | `benchmark` | 单对象 |
| CQ-9 | `zfs` | `zfs-dmu` 的 `dnode` 与 `zfs-spa` 的 `metaslab` 如何 `composed_of`？ | `zfs-dmu`+`zfs-spa` | Reification |
| CQ-10 | `zfs` | `zfs-crypto` 的 `SM4` 直连 `PCIe` 卡的 `QAT` 路径是否 `disjoint`？ | `zfs-crypto`+`pcie-sm4` | 限制 |
| CQ-11 | `zfs` | `zfs-arc` 的 `L2ARC` 与 `dbuf` 如何 `relates_to`？ | `zfs-arc` | 单对象 |
| CQ-12 | `bcachefs` | `bcachefs-btree` 的 `bset` 与 `bcachefs-journal` 如何 `composed_of`？ | `bcachefs-btree-bset`+`journal` | Reification |
| CQ-13 | `bcachefs` | `bcachefs-transaction` 的 `trigger` 如何 `audit` 派生链？ | `bcachefs-transaction` | 单数据 |
| CQ-14 | `report-center` | `report-center` 的 `resource/task/capacity` 3 `Topic` 如何 `relates_to`？ | `report-center` | 单对象 |
| CQ-15 | `report-center` | `rdbcomm 32/5MB` 的 `handle_mange` 池如何 `stateDiagram`？ | `rdbcomm`+`aio-tools-6200` | Reification |
| CQ-16 | `core` | `tooling` 的 `checker` 短路对齐如何验 `layered`？ | `tooling` | 限制 |
| CQ-17 | `core` | `network-bw-limit` 的 `algo` 如何选 `token-bucket`？ | `network-bw` | 单数据 |
| CQ-18 | `pdca` | `skill-research` 的 `records-only` vs `ontology:` 分流阈如何定？ | `skill-research` | 限制 |
| CQ-19 | `core` | `data-formats` 的 `pg-heap` 与 `parquet` 如何 `mapsTo`？ | `data-formats` | Reification |
| CQ-20 | `pdca` | `disposition` 的 `ontology:` 引用如何 `validate` 存在？ | `flow-act`+`pdca-task` | 限制 |

*5 域分布：`pdca 6` `core 6` `zfs 3` `bcachefs 2` `report 3`，`Reification 5` `Restriction 7` 与 `P0-a` 同比。*

## 双基线外推至 426

| 基线 | `10 CQ` 实测（`P0-a`） | `20 CQ` 外推（`426`） | `A100h` 外推 |
|------|------------------------|-----------------------|--------------|
| `o1+Ontogenia` | `85-90%` | `82-87%`（`426` 长尾略降） | `0.8→3.2`（`×4` 线性） |
| `Mistral 7B` | `70-75%` | `68-73%` | `0.2→0.8` |

*Source: `file: ontology/domain/{pdca,core,zfs,bcachefs,report-center}/*.md` `arxiv 2503.05388/OLLM` `T2034/cq-delta-draft.md:10 CQ` 模板*

## 下一步（P0-b 闭环）

1. **机审外扩**：`disjointness` 从 `4` 阶段扩至 `5 域` 互斥（`pdca∤zfs∤bcachefs`），`OOPS! 0 critical` 保持
2. **人定外扩**：`85/426` 复杂关系（`5 Reification+7 Restriction=12/20` 复杂）采样 `12` 问 `Grill`，`HITL` 从 `7 问` 外推至 `12 问`

## 可重跑

```bash
grep -c "CQ-" pdca/tasks/0904-ai-ontology-p0b-426/cq-426-draft.md  # 20
grep -q "GRILLING_MISSING" scripts/pdca_core.py && echo "gate ok"
```


## 机审外扩（5 域 disjointness）

- **补**：`pdca∤zfs∤bcachefs∤report∤core` 5 域 `disjointWith`（`disjoint-426.ttl` 8 三元组，含 `Plan/Do/Check/Act` 4 互斥）
- **验**：`validate 0 错`，`islands:0` 保持
- **Source**: `file: pdca/tasks/0904-ai-ontology-p0b-426/disjoint-426.ttl:1`

## 人定外扩（Round 2 12 问采样，全按推荐）

- **5 Reification**：`GateTrigger` 保留/`prov` 加/`5MB` 具化 等（`确认`）
- **7 Restriction**：`allValuesFrom/someValuesFrom/hasValue` 各按推荐（`确认`）

*HITL：Round 1 3 问 + Round 2 12 问 = 15 问人审（`20%` 复杂 `CQ` 12/20 + `Grill` 合规 3 问），`85/426` 外推可度量*
