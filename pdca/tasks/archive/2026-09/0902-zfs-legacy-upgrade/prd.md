# 存量6叶补图至3 mermaid使gate --all转OK

## 背景
`production-ontology-gate --all` 当前因 `zfs-arc/dmu/dsl/spa/zio/zpl` `mermaid 2<3` 而 `FAIL`（`ontology/entity/zfs-arc.md:2` 等），虽新叶 `zfs-vdev:5` `zfs-zil:5` `system:6` `pattern:3` 已 `PASS`，但存量未达 `pattern/production-ontology-scientific-gate.md:46` 三图 `P0` 要求，CI 硬拦前必须清零。

## 目标
- `zfs-arc/dmu/dsl/spa/zio/zpl` 各增 1×`mermaid`（补缺的 C4/状态机）至 `mermaid≥3` 且 `Source≥3`，`gate --check diagram --node` 各 `PASS`
- 保持 `正例/反例/门禁` 八段完整，`wc -l≥60`，`validate 0` `islands:0` `scaffold`可产
- `gate --all` 图项转 `OK`（仅 `zfs-crypto:2` 域节点可暂豁免，实体叶必 `PASS`）

## 范围
- 输入：6叶 `ontology/entity/zfs-*.md` 现状（各2 mermaid）
- 输出：6叶升级后 `mermaid≥3` + `validate 0` + `gate --all` 图项 `PASS`
- 不做：不改 attributes 约束，仅补图

## 功能需求
1. `zfs-arc` 补 `C4 L3: buf_hash→ARC_state→L2ARC` 图
2. `zfs-dmu` 补 `状态机: DB_CACHED/FILL/READ/EVICTING` 图
3. `zfs-dsl` 补 `C4 L3: pool→dir→dataset` 图
4. `zfs-spa` 补 `状态机: TXG open/quiescing/syncing` 图
5. `zfs-zio` 补 `状态机: transform栈压弹` 图（若已有则补时序）
6. `zfs-zpl` 补 `C4 L3: zpl→znode→dnode` 图

## 非功能需求
- 中文；每图1 `Source: openzfs/zfs file:line`；`validate 0`

## 验收标准
- [ ] AC-1 6叶mermaid：`for f in zfs-arc/dmu/dsl/spa/zio/zpl; do grep -c mermaid ontology/entity/$f.md | awk $1>=3` PASS
- [ ] AC-2 门禁完整：`wc -l≥60` 且 `grep -q 正例 && 反例 && 门禁`
- [ ] AC-3 全绿：`validate 0` + `scaffold 6叶` + `gate --node` 各 PASS
- [ ] AC-4 gate --all：`gate --all` 图项不因存量 FAIL（实体叶 PASS）
- [ ] AC-5 收敛 valid:true

## 关联本体节点
```
ontology:entity/zfs-arc
ontology:entity/zfs-dmu
ontology:entity/zfs-dsl
ontology:entity/zfs-spa
ontology:entity/zfs-zio
ontology:entity/zfs-zpl
```

## 拆分映射
- 6叶各增1图 -> 并行编辑
