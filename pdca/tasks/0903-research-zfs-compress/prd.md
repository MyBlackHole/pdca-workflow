# 调研ZFS-Compress：lz4/zstd/gzip压缩与ZIO transform栈compress分支

## 验收标准

- [ ] AC-1 research报告 `records/T0523-0903-research-zfs-compress/research-compress.md` 含 ≥3 mermaid 图（C4 L3/时序/状态机），每图附 `Source: openzfs/zfs file:line`，覆盖 `lz4/zstd/gzip/zle` 算法与 `ZIO_STAGE_WRITE_COMPRESS/DECOMPRESS` 压栈-弹栈及 `lsize→psize` 变换
- [ ] AC-2 `ontology:entity/zfs-zio` 本体 `transform_stack` 属性细化压缩分支：补充 `compress_func` 选型、`zio_compress_info_t`、`compress_empty` 短路，attributes ≥3 且含决策树/正反例/门禁命令，`testable_signal` 含 `grep -q 'zio_compress'`
- [ ] AC-3 证据链完整：`evidence/` 含 `research-compress.md` 与本体 diff，`convergence.json` 回链 `meta.convergence`，`manifest.jsonl` 登记

## 关联本体节点

```
ontology:entity/zfs-zio
ontology:pattern/research-diagram-methodology
ontology:pattern/scientific-research-methodology
```

## 拆分映射

- 压缩/解压时序 -> ontology:entity/zfs-zio
- 压缩算法选型C4 -> ontology:entity/zfs-zio
- 压缩状态机与短路分支 -> ontology:entity/zfs-zio
