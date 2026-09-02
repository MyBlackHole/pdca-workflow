# 新建zfs-zil实体：LWB/slog/重放三态与ZPL解耦

## 背景
`ontology/entity/zfs-zpl.md:25` 将 `ZIL` 仅作 3行约束子节，`zil.c` `800-1050` 的 `LWB_OPEN→ISSUED→WRITE_DONE→DONE` 与 `slog` 分流、`zil_claim` 重放未独立建模，导致同步写耐久无法独立派生测试。需按 `templates/production-entity.md:131` 新建 `entity/zfs-zil`，验证三件套对第二叶的普适性（继 `zfs-vdev:179行` 后）。

## 目标
- `ontology/entity/zfs-zil.md` ≥80行，3 attributes：`zil_lwb`/`slog_separate`/`claim_replay`，每条 `testable_signal` 双源 `records + /tmp/zfs/module/zfs/zil.c`
- `C4 L3(zilog→lwb→slog) + 时序(zil_commit→lwb_write_issue→slog/zio) + 状态机(LWB四态)` 3×`mermaid`且每图1 `Source: openzfs/zfs file:line`
- `决策树(slog有无/同步异步) + 正例(commit配对) + 反例(漏claim)` + `gate --node zfs-zil` `GATE OK`

## 范围
- 输入：`ontology/entity/zfs-zpl.md` 现状、`module/zfs/zil.c` `include/sys/zil.h`、`templates/production-entity.md`
- 输出：`zfs-zil.md` + `validate 0` + `gate --node PASS` + `scaffold` 可产
- 不做：不改 ZPL 存量，仅新增独立实体并与 ZPL `relates_to` 互链

## 功能需求
1. 三属性：`zil_lwb`（LWB四态）、`slog_separate`（slog/主池分流）、`claim_replay`（`zil_claim` 重放），约束含 `C4/时序/状态机可一图建模`
2. 三图：`C4 L3: zilog→lwb_list→slog`，`时序: zfs_log_write→zil_commit→lwb_write_issue→slog vdev`，`状态机: OPEN→ISSUED→WRITE_DONE→DONE`
3. 决策树：`同步写→slog有无→LWB路径`；正例：`zfs_log_write + zil_commit` 配对；反例：漏 `zil_claim` 重放导致掉电丢

## 非功能需求
- 中文；`validate 0` 且 `islands:0`；`guides` 合法

## 验收标准
- [ ] AC-1 三属性：`attributes≥3` 且每条含 `grep -q` + 双源且 `gate --check signal --node zfs-zil` PASS
- [ ] AC-2 三图：`mermaid≥3` 且 `Source≥3` 且 `grep -q 'C4 L3'`
- [ ] AC-3 决策树正反例：`grep -q '决策树' && grep -q '正例' && grep -q '反例'`
- [ ] AC-4 全绿：`validate 0` + `islands:0` + `scaffold` 可产 + `gate --node zfs-zil` GATE OK
- [ ] AC-5 收敛 valid:true

## 关联本体节点
```
ontology:entity/zfs-zil
ontology:entity/zfs-zpl
ontology:pattern/production-ontology-scientific-gate
```

## 拆分映射
- 三属性 -> attributes
- 三图 -> mermaid
- 决策树正反例 -> 正文
