---
schema: pdca.asset/v1
id: T0533-0902-research-bcachefs-tools
phase: check
source_ids: [research-report2, bcachefs-system-v2, bcachefs-format-v2, bcachefs-journal-v2, bcachefs-btree-bset-v3, bcachefs-alloc-v2, bcachefs-transaction-v2, bcachefs-btree-v2, bcachefs-journal-rewind, bcachefs-cli, bcachefs-device, bcachefs-fsck, bcachefs-mount, bcachefs-super, gate-pattern-v2, convergence-map3]
---

# T0533 结论：bcachefs-tools 全栈调研 — 可实现规约交付

## 假设验证

假设：bcachefs-tools 为 Rust(Cargo)+C(Make/DKMS) 双语言、单一二进制分发 30+ 子命令、经 wrappers 直达 fs 引擎（journal/btree/alloc/super/recovery），可被提炼为“可实现规约”——即按本体即可直接写出创建/销毁/持久化/并发/校验全链，且错误可证伪。

结果：假设全部成立。见 AC-1..6 逐项对照与证据索引。

## 结果

- AC-1 多图（≥6 mermaid 且 ≥6 Source 且每图 file:line，含一致性/journal/bset/空间/并发 5章各≥1图）✅ — `research-report2` 23 mermaid / 47 Source，深化5章各≥1图且每图含 `Source: /home/black/Documents/bcachefs-tools/... file:line`
- AC-2 本体最大化（≥10 且 scaffold 可产且 gate 各GATE OK）✅ — `bcachefs-*.md` 13 文件（12叶+system），`btree` 重定义为引擎本体`composed_of btree-bset`（实现无缺口），`journal` 补 16类型全表，全部 13 `GATE OK` 七维`realization`、 `scaffold` 可产
- AC-3 工具链（Cargo/Make/DKMS 可追溯）✅ — `Cargo.toml:1 workspace / Makefile:13 VERSION:= / Makefile:22 DKMSDIR / bch_bindgen/build.rs:404 + fs/build.rs:1 / -rdynamic` 三构建均`grep -q`命中
- AC-4 一致性/journal/btree/bset深化且可追溯 ✅ — `数据一致性`+ `journal(BCH_JSET_ENTRY_TYPES 16)`+ `btree(BCH_BTREE_IDS 29森林，但引擎为单一实例化参数)+bset` + `btree_types` 族均在报告 `§4-5` 与本体中表格化且每图溯源
- AC-5 空间/并发深化且可追溯 ✅ — `空间管理`+ `alloc(bucket四态/WFQ/copygc)+transaction(six三态+25 restart+ring[4])` 在报告 `§6-7` 与本体中覆盖
- AC-6 全绿 ✅ — `validate 0 / islands:0 / 13 GATE OK / convergence valid:true / scaffold 可产`

## 本体沉淀

本次新增约束：`production-ontology-scientific-gate` 第七维 `realization_verifiable_implementation`——本体即实现规约，结构/行为/校验三完整且派生夹具可证伪（按本体实现必绿、违背必红）。`btree` 首个示范引擎-容器主从（`btree composed_of btree-bset`），修正“清单当本体”的为了写而写。

关联本体节点：`ontology:entity/bcachefs-system` 聚合12叶，`ontology:entity/bcachefs-btree`（引擎）与 `bcachefs-btree-bset`（物理容器子概念）主从，`ontology:pattern/production-ontology-scientific-gate` 七维。

## 证据索引

- research-report2 / research-report-v2.md — AC-1,3,4,5
- bcachefs-*-v2 / bcachefs-*-v3 / bcachefs-*.md — AC-2
- gate-pattern-v2 — AC-6 + 第七维
- convergence-map3 / convergence3.json — AC-1..6 回链

## 失败原因

无（verdict 为 confirmed 范畴）。

## 适用边界

- 研究为源码静态+门禁验证，未跑 `mkfs` 实盘压测；`verus-proofs` 仅提及来源。
- 29 btree_id 森林为参数化实例，未对每 btree 的 `KEY_TYPE_*` 逐类形式化校验（覆盖于 `BCH_BTREE_IDS` 表格层面）。

## 下一轮建议

- Check 确认后进 Act 完成 `journal` 与 `disposition`，归档后可派生 `to-tickets` 叶并行开发（叶 12 并行、根串行聚合）。

**verdict**: confirmed
