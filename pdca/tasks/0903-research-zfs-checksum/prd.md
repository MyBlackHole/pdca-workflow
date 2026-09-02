# 调研ZFS-Checksum：fletcher4/sha256校验与ZIO transform栈checksum分支

## 验收标准

- [ ] AC-1 research报告 `records/T0522-0903-research-zfs-checksum/research-checksum.md` 含 ≥3 mermaid 图（C4 L3/时序/状态机），每图附 `Source: openzfs/zfs file:line`，覆盖 `fletcher2/4/sha256/sha512/edonr` 算法选型与 `ZIO_STAGE_CHECKSUM_GENERATE/VERIFY` 压栈-弹栈
- [ ] AC-2 `ontology:entity/zfs-zio` 本体 `transform_stack` 属性细化校验分支：补充 `checksum_func` 选型、`zio_checksum_info_t` 表、`abd_checksum` 边界，attributes ≥3 且含决策树/正反例/门禁命令，`testable_signal` 含 `grep -q 'zio_checksum'`
- [ ] AC-3 证据链完整：`evidence/` 含 `research-checksum.md` 与本体 diff，`convergence.json` 回链 `meta.convergence`，`manifest.jsonl` 登记

## 关联本体节点

```
ontology:entity/zfs-zio
ontology:pattern/research-diagram-methodology
ontology:pattern/scientific-research-methodology
```

## 拆分映射

- checksum生成/校验时序 -> ontology:entity/zfs-zio
- checksum算法选型C4 -> ontology:entity/zfs-zio
- 校验失败处理状态机 -> ontology:entity/zfs-zio
