# T0407 结论（Check 阶段）

- record: T0407-0829-ontology-guide-adopt
- 阶段结论：ONTOLOGY_GUIDE 采纳落地完成，证据链收敛验证通过。

## 验收对照
| AC | 内容 | 证据 |
|----|------|------|
| AC-1 | `docs/ONTOLOGY_GUIDE.md` 正式版（兼容吸收，语义权威=frontmatter+relations） | `t0407-guide` |
| AC-2 | `ontology/_meta.yaml` 声明语义权威与文件夹索引角色 | `t0407-meta` |
| AC-3 | `scripts/ontology_graph.py` 导出 Obsidian 图谱 + 孤岛检测 | `t0407-graph` |
| AC-4 | ≥3 样本节点补 `docType`/`tags`（x509-certificate、pdca、pattern、principle），validate 仍通过 | `t0407-fields` |
| AC-5 | `docs/adr/ADR-0033-ontology-guide-adoption.md` | `t0407-adr` |
| AC-6 | `ontology-validate` OK + 15 测试通过 + 证据收敛 | `t0407-validation` + `convergence-map2` |

`validate-convergence`：`valid: true`。

## 关键决策（与 T0406 衔接）
- **本体论合规落点**：`ONTOLOGY_GUIDE.md` 置于 `docs/`（非 `ontology/` 内），因 `ontology-validate` 扫描 `ontology/**.md` 并要求节点 frontmatter；根级 `.md` 无法满足 `type==目录名`，会破坏校验门禁。指南是文档而非节点。
- `domain` 字段是**受控引用列表**（须指向已存在的 `domain/*` 节点），非自由文本；样本节点仅用自由的 `docType`/`tags`，避免 DANGLING_REF。
- `_meta.yaml` 为 `.yaml` 不被 `.md` 扫描，留在 `ontology/` 根合法。

## 副作用修复
- 初版样本节点误用 `domain: TLS/mTLS` 自由文本，触发 `ontology-validate` DANGLING_REF 并导致 `test_ontology_induction.py::test_ac2_no_cycle_dangling` 失败；已改回仅用 `docType`/`tags`，校验与测试恢复全绿（15 passed）。

## Verdict
- outcome: **confirmed**
- 未改动 SSOT v3 / `task.schema.json` / `ontology-validate.py` / `transition-phase.py` / `ontology_reason.py` / `ontology_gate.py`；纯新增文档、脚本与可选字段。
