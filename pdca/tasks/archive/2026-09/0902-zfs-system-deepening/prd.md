# 深化zfs-system聚合：补C4 L2/决策树并增vdev使gate --all PASS

## 背景
`ontology/entity/zfs-system.md:43` 单薄（无决策树/正反例/门禁，`wc -l 43`），`composed_of` 6叶缺 `zfs-vdev`，导致 `production-ontology-gate --all` 因 `diagram FAIL` 与 `hundred` 未100% 而 `FAIL`（`records/T0525-.../report.md:12`）。需按 `templates/production-system.md:120` 八段模板一次补齐，使 `gate --all` 转 `OK`。

## 目标
- 以 `templates/production-system.md` 为母本，`zfs-system` 补至 `≥80行`，含 `C4 L2 + 时序 + 聚合决策树` 3×`mermaid`且每图1 `Source: openzfs/zfs file:line`
- `composed_of` 增 `ontology:entity/zfs-vdev`，`gate --check hundred --node zfs-system` `coverage≥95%` PASS
- 补 `正例/反例/门禁` 使 `wc -l≥80` 且 `gate --node zfs-system` `GATE OK`

## 范围
- 输入：`ontology/entity/zfs-system.md` 现状、`ontology/entity/zfs-vdev.md:179` 参照、`templates/production-system.md`
- 输出：深化后 `zfs-system.md` + `validate 0` + `gate --node/--all` 相关项 PASS + `scaffold` 可产
- 不做：不改6叶内容，仅聚合层

## 功能需求
1. C4 L2 全栈图：`graph TD: User→ZPL→DMU→DSL→SPA→ZIO→VDEV` 横切 ARC/ZIL，`Source: spa_impl.h:80`
2. 聚合决策树：新维度归属判定（已有叶/新叶三准绳/Yo-Yo），见 `pattern/production-ontology-scientific-gate.md:120`
3. `composed_of` 增 `zfs-vdev`，`attributes.six_leaf_completeness` 约束更新为7叶（或8叶含zfs-vdev）且 `testable_signal` 双源 `records + /tmp/zfs` PASS
4. 正例：按模板新增叶流程；反例：堆砌不建叶导致 `hundred FAIL`

## 非功能需求
- 中文；每图 `Source:` 可 `grep -q`；`validate 0` 且 `islands:0`

## 验收标准
- [ ] AC-1 C4 L2+决策树：`mermaid≥3` 且 `Source≥3` 且 `grep -q 'C4 L2'`
- [ ] AC-2 composed_of：`grep -q 'zfs-vdev' ontology/entity/zfs-system.md` 且 `gate --check hundred --node zfs-system` PASS
- [ ] AC-3 正反例门禁：`wc -l≥80` 且 `grep -q '正例' && grep -q '反例' && grep -q '门禁'`
- [ ] AC-4 全绿：`validate 0` + `islands:0` + `scaffold` 可产 + `gate --node zfs-system` GATE OK 且 `--all` 相关项不因 system 而 FAIL
- [ ] AC-5 收敛 valid:true

## 关联本体节点
```
ontology:entity/zfs-system
ontology:entity/zfs-vdev
ontology:pattern/production-ontology-scientific-gate
```

## 拆分映射
- 聚合图/决策树 -> 独立 mermaid 补
- composed_of -> relations 增
- 正反例门禁 -> 正文补
