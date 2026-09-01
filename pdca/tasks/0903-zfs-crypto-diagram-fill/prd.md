# 回补T0500 ZFS Crypto多图：C4 L2+ZIO pipeline+TXG状态机

## 背景

T0500-0901-research-zfs-crypto 难理解因缺架构图/逻辑图/生命周期图。T0501已沉淀 `research-diagram-methodology` 多图模板（P0 C4 L2+时序+状态机 mermaid，每图Source），T0503以同模板产8图全栈可验证。现以同方法论回补T0500，使其 `grep mermaid≥3` 可检。

## 目标

- 为T0500报告补P0三图 `mermaid`：`C4 L2`（ZFS Crypto容器）+ `ZIO pipeline`（encrypt/compress/checksum分支）+ `TXG/key生命周期状态机`，各1条 `Source: openzfs/zfs file:line`
- 产出回补件 `records/T0504/research-crypto-diagrams.md` 可直接合入T0500

## 范围

- 输入：T0500原文 + openzfs/zfs ZFS Crypto（`module/zfs/zio.c:ENCRYPT` / `zfs_crypto.c` / `spa_crypto`）+ 多图模板
- 输出：1回补件6图 + 本体沉淀 `ontology/pattern/research-diagram-methodology` 关联
- 不做：不重写T0500全文，不改本体树结构

## 功能需求

1. C4 L2：ZFS Crypto容器（ZPL/DMU/ZIO/SPA/Keystore）`graph TD`
2. ZIO pipeline：`ZIO_STAGE_ENCRYPT/COMPRESS` 分支时序 `sequenceDiagram`
3. TXG/生命周期：`key→TXG→SPA sync` 状态机 `stateDiagram-v2`
4. 每图1条 `Source:` 可复核

## 非功能需求

- `mermaid` 可渲染，`Source` 可点击至 `file:line`

## 验收标准

- [ ] AC-1 回补件多图：含3图 `mermaid` ≥3且每图含 `Source:`
- [ ] AC-2 方法论一致：`grep research-diagram-methodology` 可命中
- [ ] AC-3 可合入：`diff` 可直接 `patch` 入T0500
- [ ] AC-4 本体沉淀：`disposition ontology:pattern/research-diagram-methodology` 回链
- [ ] AC-5 全绿 `islands:0` `valid:true`

## 关联本体节点

```
ontology:pattern/research-diagram-methodology
ontology:pattern/scientific-research-methodology
ontology/entity/zfs-system
```

## 拆分映射

- 回补件 -> ontology:pattern/research-diagram-methodology
