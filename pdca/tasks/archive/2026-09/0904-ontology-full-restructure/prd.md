# 全面重构 ontology 目录：FAIR+MOMo 全量（426 节点 100% 迁移，零兼容）

## 背景

用户定性“`ontology` 无价值因不全面”且明确“不要最新改动要全面正确改动”。前序增量（`P0-a` 单域）不符合要求，需一次性全量达 **FAIR Template（modules/patterns/versions/CQ/provenance） + OBO（YAML+Markdown） + IOF（单职责/DAG） + OMNIMOD（Sub(R) 聚类） + MOMo（关键 notion 模块）** 合规，`426 节点` 100% 迁移，**零兼容旧 6 桶**。

输入锚点：
- `file: ontology/manifest.jsonl:1` — 426 节点清单（`domain 208` 平铺为核心债务）
- `file: scripts/ontology-validate.py:1` + `scripts/ontology_graph.py:1` — 现仅验 `validate+islands`，未验 FAIR/MOMo
- 网络：`LA3D FAIR Template/github`、`OBO Foundry`、`Rector OWL 模块化`、`OMNIMOD WEBIST 2024`、`MOMo LLM4KGOE 2024`

## 目标

产 **新顶层**（`modules/patterns/versions/CQ/provenance/documentation/catalog` 全桶）+ **MOMo 模块化**（`domain 208→modules/{pdca,zfs,bcachefs,report-center,core}` 聚类，DAG 无环）+ **FAIR 全量头**（`dcterms:license/created` 等 426 节点补）+ **一次全量迁移**（`426/426`，零 symlink），`validate+islands:0+askwol` 全绿。

## 范围

- 输入：`ontology/` 全量 `426 节点`（`concept 118` `domain 208` `entity 56` 等）
- 输出：新顶层 8 桶 + `426 节点` 新址 + `manifest.jsonl` 重写 + `START-HERE.owl` + `catalog-v001.xml` + `CQ-*.rq` + `pyLODE index.html`
- 不做：不改节点语义，仅重组目录与头；`pdca_core.py` 等引用点同步全改（一次性）

## 功能需求

1. **新顶层**：建 `modules/patterns/versions/competency_questions/provenance/documentation` + `catalog-v001.xml`，`ontology-validate` 适配新桶
2. **MOMo 聚类**：`domain 208` 按 `pdca/zfs/bcachefs/report-center/core` 5 关键 notion + `Sub(R)` 聚类，一次性搬 `modules/`，`islands:0` 且 DAG 无环（`grep -r imports` 无环）
3. **FAIR 全补**：`426 节点` 补 `dcterms:license/created/modified/publisher` + `owl:versionIRI`（`askwol` 必检），`_meta.yaml` 增 `license`
4. **CQ/版本/文档**：每 `module` 至少 1 `CQ-*.rq`，`versions/2026-09-04/` 快照含 `ontology.owl`，`documentation/index.html` 由 `pyLODE` 生成
5. **零兼容迁移**：旧 `domain/concept` 等 6 桶路径废弃（删目录，不留 symlink），`pdca_core.py` `ontology_reason` 等引用点全量 `modules/` 适配，`426/426` 迁移可 `find ontology -name "*.md" | wc -l` 检

## 验收标准

- [ ] AC-1 新顶层可检：`ls ontology/{modules,patterns,versions,competency_questions,provenance,documentation} && cat ontology/catalog-v001.xml` 均命中且 `ontology-validate OK`
- [ ] AC-2 MOMo 聚类可检：`ls ontology/modules/{pdca,zfs,bcachefs,report-center,core} | wc -l` 合计 `208` 且 `ontology_graph: islands:0` 且 `grep -r "imports" ontology/modules` 无环
- [ ] AC-3 FAIR 全检通过：`askwol` 对 `426 节点` 的 `dcterms:title/description/creator/versionInfo/license` 全检通过（`grep -q dcterms:license ontology/*/*.md | wc -l` == 426）
- [ ] AC-4 100% 迁移：`find ontology -name "*.md" | wc -l` == 426 且 `manifest.jsonl` 重写后 `grep -c "modules/" manifest.jsonl` == 208 且旧 `domain/` 已删
- [ ] AC-5 零兼容：`ls ontology/domain 2>&1 | grep "No such"` 命中且 `grep -r "ontology/domain" scripts/ ontology/ | wc -l` == 0（引用点全改）

## 关联本体节点

```
ontology:process/flow-do
ontology:concept/pdca-task
```

## 拆分映射

- 新顶层+MOMo 聚类 -> ontology/modules/* + validate
- FAIR 头+CQ/版本/文档 -> 426 节点头 + CQ/versions
- 零兼容迁移 -> manifest + 引用点全改
