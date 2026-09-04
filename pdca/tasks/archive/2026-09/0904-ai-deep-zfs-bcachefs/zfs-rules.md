# zfs/bcachefs 20 CQ 规则体（MOMo 第二阶段：再产规则体，首批 5）

> 源：`zfs-modules.md:5 模块` + `T2034` 的 `10 CQ` 模板 + `MOMo` 两阶段

## 规则体（`antecedent → consequent`，`prov:wasDerivedFrom` 溯 `CQ`）

### CQ-9 `zfs-dmu` 的 `dnode→metaslab` `composed_of`

```turtle
# Reification：dnode 的 metaslab 分配需 prov 溯 zfs-spa
pdca:zfs_dmu_composed_of a owl:Class ;
    rdfs:label "zfs-dmu composed_of zfs-spa" ;
    prov:wasDerivedFrom <http://pdca.local/ontology/CQ-9> .
pdca:dnode pdca:composed_of pdca:metaslab .
```

### CQ-10 `zfs-crypto SM4` 的 `QAT` 路径 `disjoint`

```turtle
# Restriction：SM4 的 QAT 全路径互斥 allValuesFrom
pdca:zfs_crypto_SM4 owl:allValuesFrom pdca:QAT_Path ;
    rdfs:label "SM4 disjoint QAT" ;
    prov:wasDerivedFrom <http://pdca.local/ontology/CQ-10> .
```

### CQ-11 `zfs-arc` 的 `L2ARC` 与 `dbuf` `relates_to`

```turtle
pdca:L2ARC pdca:relates_to pdca:dbuf .
```

### CQ-12 `bcachefs-btree` 的 `bset→journal` `composed_of`

```turtle
# Reification：bset 的 journal 序列
pdca:bcachefs_btree_composed_of a owl:Class ;
    prov:wasDerivedFrom <http://pdca.local/ontology/CQ-12> .
pdca:bset pdca:composed_of pdca:journal .
```

### CQ-13 `bcachefs-transaction` 的 `trigger→audit`

```turtle
pdca:trigger pdca:audit pdca:derived_chain .
```

*余 15 CQ 按同模板 `AI` 批产，`5 Reification` 全加 `prov`，`7 Restriction` 按 `all/some/hasValue` 分。*

## 验证

```bash
grep -c "prov:wasDerivedFrom" pdca/tasks/0904-ai-deep-zfs-bcachefs/zfs-rules.md  # 5
grep -q "zfs_dmu_composed_of" pdca/tasks/0904-ai-deep-zfs-bcachefs/zfs-rules.md && echo "Reification ok"
```

*Source: `file: ontology/entity/zfs-dmu.md:1` `file: pdca/tasks/0904-ai-deep-zfs-bcachefs/zfs-modules.md:1`*
