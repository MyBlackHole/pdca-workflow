# T0527 结论：新建 zfs-zil 实体一次做对

## 假设验证

成立。`zfs-zil` 已按 `templates/production-entity.md` 新建 168行，三属性 `zil_lwb/slog/replay` 双源可回归，`C4 L3 + 时序 + 状态机 + 决策树` 4×`mermaid`且每图1 `Source: openzfs/zfs`，`gate --node zfs-zil` `GATE OK`（6维全 PASS），`validate 0` `islands:0` `scaffold`可产。

## 结果

- AC-1 三属性：`attributes 3` 每条含 `grep -q` + 双源且 `gate --check signal` PASS（E0527-zil）
- AC-2 三图：`mermaid 5` `Source 9` `grep -q 'C4 L3'` PASS（E0527-zil）
- AC-3 决策树正反例：`grep -q '决策树' && 正例 && 反例` PASS（E0527-zil）
- AC-4 全绿：`validate 0` `islands:0` `scaffold`可产 `gate --node` GATE OK（E0527-zil）
- AC-5 收敛 valid:true

## 边界与下一轮

- `zfs-zil` 与 `zfs-zpl` 已 `relates_to` 解耦，`system` 8叶聚合待 T0526 后续增 `zfs-zil`
- 未接入 `slog` 实测，仅静态源码追溯

## 本体沉淀

`ontology:entity/zfs-zil` 已沉淀（LWB四态+slog分流+claim/replay），来源 T0527-0902-zfs-zil-entity

## 证据索引

- E0527-zil / convergence-map（5/5）

**verdict**: confirmed
