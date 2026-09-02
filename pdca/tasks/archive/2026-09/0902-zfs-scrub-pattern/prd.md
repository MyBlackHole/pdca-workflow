# 沉淀scrub/resilver运维pattern及tunable pitfall

## 背景
`scrub/resilver/vdev_remove/pool_import` `spa_feature` 及 `zfs_txg_timeout/metaslab_weight/arc_p/l2arc_write_max` 等 `tunable` 在 `zfs-spa/arc` 仅参数提及，未沉淀为 `pattern` `pitfall`，运维可测性缺失。需按模板沉淀 `pattern/zfs-scrub-resilver` + `pitfall/zfs-tunable-misconfig`。

## 目标
- `ontology/pattern/zfs-scrub-resilver.md` ≥80行，3 attributes：`scrub_scan`/`resilver_queue`/`repair` 双源 `records + /tmp/zfs/module/zfs/dsl_scan.c` `vdev.c`
- `ontology/pitfall/zfs-tunable-misconfig.md` ≥60行，含 `arc_p/metaslab_weight` 阈值联动反模式
- `C4+时序+状态机` 3×`mermaid`且每图1 `Source`，`gate --node` PASS

## 范围
- 输入：`module/zfs/dsl_scan.c` `vdev.c` `spa.c` `arc.c`
- 输出：`pattern` + `pitfall` 各1 + `validate 0` + `gate PASS`
- 不做：不改存量 entity 约束

## 功能需求
1. pattern 三属性：`scrub_scan`（`dsl_scan`）、`resilver_queue`（`vdev_queue`）、`repair`（`zfs_ereport`）
2. pitfall 三阈值：`arc_p` `metaslab_weight` `l2arc_write_max` 误配反例
3. 三图：`C4 scan→queue→repair` `时序 scrub→resilver` `状态机 SCANNING/FINISHED`

## 非功能需求
- 中文；`validate 0` `islands:0`

## 验收标准
- [ ] AC-1 三属性：`attributes≥3` 且每条含 `grep -q` + 双源且 `gate --check signal` PASS
- [ ] AC-2 三图：`mermaid≥3` 且 `Source≥3`
- [ ] AC-3 决策树正反例：`grep -q '决策树' && 正例 && 反例`
- [ ] AC-4 全绿：`validate 0` + `scaffold`可产 + `gate --node` GATE OK
- [ ] AC-5 收敛 valid:true

## 关联本体节点
```
ontology:pattern/zfs-scrub-resilver
ontology:pitfall/zfs-tunable-misconfig
```

## 拆分映射
- pattern -> 三属性三图
- pitfall -> 阈值反模式
