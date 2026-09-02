# T0532 结论：scrub/resilver pattern + tunable pitfall

## 假设验证

成立。`pattern/zfs-scrub-resilver:125行` 三属性 `scrub_scan/resilver_queue/repair` + `pitfall/zfs-tunable-misconfig:124行` 三阈值反模式，各 `mermaid 4` `Source 8`，`gate --node` 均 `GATE OK`，`validate 0` `islands:0` `scaffold`可产。

## 结果

- AC-1 三属性：`attributes 3` 且每条含 `grep -q` + 双源且 `gate --check signal` PASS（E0532-scrub/tunable）
- AC-2 三图：`mermaid 4` `Source 8`（E0532-scrub）
- AC-3 决策树正反例：`grep -q 决策树 && 正例 && 反例` PASS（E0532-scrub）
- AC-4 全绿：`validate 0` `islands:0` `scaffold`可产 `gate --node` GATE OK（E0532-scrub）
- AC-5 收敛 valid:true

## 边界与下一轮

- 运维可测性已 pattern/pitfall 化，`ci-gate` 已含六维，后续生产无需再补

## 本体沉淀

`ontology:pattern/zfs-scrub-resilver` + `ontology:pitfall/zfs-tunable-misconfig` 已沉淀，来源 T0532-0902-zfs-scrub-pattern

## 证据索引

- E0532-scrub/tunable / convergence-map（5/5）

**verdict**: confirmed
