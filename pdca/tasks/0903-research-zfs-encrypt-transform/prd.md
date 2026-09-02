# 调研ZFS-Encrypt-Transform：AES-GCM/SM4-GCM加密与ZIO transform栈encrypt分支

## 验收标准

- [ ] AC-1 research报告 `records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md` 含 ≥3 mermaid 图（C4 L3/时序/状态机），每图附 `Source: openzfs/zfs file:line`，覆盖 `AES-128/256-GCM/CCM + SM4-GCM` 套件与 `ZIO_STAGE_ENCRYPT/DECRYPT` 压栈-弹栈及 `abd` 替换
- [ ] AC-2 `ontology:domain/zfs-crypto` 本体 transform视角深化：补充 `encrypt_func` 选型、`zio_crypt_table`、IV/salt 生成与 `ZIO transform` 协同，attributes ≥3 且含决策树/正反例/门禁命令，`testable_signal` 含 `grep -q 'zio_crypt'`
- [ ] AC-3 证据链完整：`evidence/` 含 `research-encrypt-transform.md` 与本体 diff，`convergence.json` 回链 `meta.convergence`，`manifest.jsonl` 登记

## 关联本体节点

```
ontology:domain/zfs-crypto
ontology:entity/zfs-zio
ontology:pattern/research-diagram-methodology
ontology:pattern/scientific-research-methodology
```

## 拆分映射

- 加密/解密时序 -> ontology:domain/zfs-crypto
- 加密套件C4 -> ontology:domain/zfs-crypto
- 加密状态机与IV分支 -> ontology:entity/zfs-zio
