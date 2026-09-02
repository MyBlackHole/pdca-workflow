# 新建zfs-ddt实体：DDT表/LRU及BRT与dedup

## 背景
`ddt.c/ddt_zap.c/brt.c` `dedup/nopwrite` 在 `zfs-zio` 仅 `flag` 提及，未独立建模 `ddt_entry_t` `ddt_phys_t` `brt` 削零表与 `ZCHECKSUM_FLAG_DEDUP` 选型，`zfs-crypto` 的 `dedup` 确定性 `HMAC` 缺持久表可测点。需按 `templates/production-entity.md` 新建 `entity/zfs-ddt`。

## 目标
- `ontology/entity/zfs-ddt.md` ≥80行，3 attributes：`ddt_table`/`ddt_lru`/`brt_nopwrite` 双源 `records + /tmp/zfs/module/zfs/ddt.c` `brt.c`
- `C4 L3(ddt_table→ddt_entry→brt) + 时序(dedup write→ddt_lookup→brt_add) + 状态机(entry REFD/HOLE)` 3×`mermaid`且每图1 `Source`
- `决策树(dedup开/关→BRT→ZIL) + 正例(ddt_lookup配对) + 反例(漏brt)` + `gate --node PASS`

## 范围
- 输入：`module/zfs/ddt.c` `brt.c` `include/sys/ddt.h` `zio.c dedup`
- 输出：`zfs-ddt.md` + `validate 0` + `gate PASS`
- 不做：不改 zio 存量

## 功能需求
1. 三属性：`ddt_table`（`ddt_phys_t` `zap` 持久）、`ddt_lru`（`arc` 协同）、`brt_nopwrite`（`brt` 削零）
2. 三图：`C4 L3` `时序` `状态机 REFD/HOLE/EVICT`
3. 决策树：`dedup→brt→slog` 分流；正例：`ddt_lookup + brt_add` 配对

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
ontology:entity/zfs-ddt
ontology:entity/zfs-zio
ontology:domain/zfs-crypto
```

## 拆分映射
- 三属性 -> attributes
- 三图 -> mermaid
