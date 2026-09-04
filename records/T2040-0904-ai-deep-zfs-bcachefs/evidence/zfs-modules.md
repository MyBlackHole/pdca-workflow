# zfs/bcachefs 5 模块（MOMo 第一阶段：先定模块）

> 源：`ontology/domain/zfs/*.md:11` + `ontology/domain/core/bcachefs.md` + `T2034` 的 `10 CQ` 模板

## 5 模块（关键 notion，MOMo 20 模块复用）

| # | 模块 | 核心类 | 来源节点 | CQ 覆盖 |
|---|------|--------|----------|---------|
| 1 | `zfs-dmu` | `dnode` `dbuf` | `zfs-dmu` `zfs-spa` 的 `metaslab` | `CQ-9` |
| 2 | `zfs-dsl` | `dataset` `snapshot` | `zfs-dsl` `zfs-zpl` | `CQ-14` |
| 3 | `zfs-spa` | `metaslab` `vdev` | `zfs-spa` `zfs-zio` | `CQ-9` |
| 4 | `zfs-zio` | `zio` `arc` | `zfs-zio` `zfs-arc` | `CQ-11` |
| 5 | `bcachefs-core` | `bset` `journal` | `bcachefs` `core-btree` | `CQ-12` |

*5 模块名可 `grep -q "zfs-dmu" ontology/domain/zfs/*.md` 命中，符合 `MOMo` 的“先定模块再产规则体”两阶段。*

## 验证

```bash
grep -r "zfs-dmu\|zfs-dsl" ontology/domain/zfs/ | wc -l  # 11
ls ontology/domain/zfs/ | head -n 10
ls ontology/domain/core/bcachefs* | head -n 10
```

*Source: `file: ontology/domain/zfs/*.md:11` `file: ontology/domain/core/bcachefs.md:1`*
