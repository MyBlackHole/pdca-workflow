# T0528 结论：存量6叶补图至 gate --all OK

## 假设验证

成立。`zfs-arc/dmu/dsl/spa/zio/zpl` 各 `mermaid 2→3`（补缺 C4/状态机各1图且每图1 Source），`zfs-crypto` 亦 `2→3`， `gate --check diagram --node` 各 `PASS`，`validate 0` `islands:0` `scaffold` 6叶可产，`gate --all` 图项转 `OK`（此前因存量 `FAIL`）。

## 结果

- AC-1 6叶mermaid：`grep -c mermaid` 各≥3 `Source≥3` `gate --check diagram` PASS（E0528-*）
- AC-2 门禁完整：`wc -l≥60` 且 `正例/反例/门禁` 完整（E0528-*）
- AC-3 全绿：`validate 0` `islands:0` `scaffold` 可产（E0528-*）
- AC-4 gate --all：实体叶 `diagram` 均 `PASS`，`gate --all` 图项 `OK`（E0528-zfs-arc）
- AC-5 收敛 valid:true

## 边界与下一轮

- `zfs-crypto` 亦补图，重构后 `gate --all` 10节点全 `PASS`
- 无属性改动，仅补图，风险低

## 本体沉淀

`ontology/entity/zfs-arc/dmu/dsl/spa/zio/zpl` 升级至3 mermaid，`domain/zfs-crypto` 升级至3，来源 T0528-0902-zfs-legacy-upgrade

## 证据索引

- E0528-zfs-arc/dmu/dsl/spa/zio/zpl/crypto / convergence-map（5/5）

**verdict**: confirmed
