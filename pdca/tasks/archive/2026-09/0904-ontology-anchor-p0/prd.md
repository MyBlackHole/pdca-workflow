# P0本体锚补齐：AGENTS路由与PHASE_STATUS/knowledge欠账清零

## 背景

`T2045` 审查确认 `本体到代码单向`（本体是源、代码是投射），但 P0 欠账未清：`AGENTS.md:27-30` 4 处 `ontology/domain/skill-*.md` 引用不存在（实文件在 `ontology/domain/pdca/`），`pdca_core.py:19` 的 `PHASE_STATUS` 映射无本体节点，`pdca_core.py:26` 保护不存在的 `knowledge/` 目录。`pdca-doctor valid:false`（`missing 4 + identity false`）。

输入锚点：
- `file: AGENTS.md:27` — 4 处缺失引用
- `file: scripts/pdca_core.py:18` — PHASES/PHASE_STATUS/PROTECTED_PREFIXES 硬编码
- `file: scripts/pdca-doctor.py:1` — missing_references 探针
- `file: ontology/concept/pdca-phase.md:1` — 阶段元概念（待补 status 映射）
- `file: scripts/ontology-validate.py:1` / `scripts/ontology_graph.py:1` — validate/islands 门禁

## 目标

最小切片清零 P0 欠账：AGENTS 路由归位 + PHASE_STATUS 本体化 + knowledge 保护删除，全量 `三检` 可重跑。

## 范围

- 输入：`AGENTS.md`、`scripts/pdca_core.py`、`ontology/concept/pdca-phase*.md`
- 输出：`AGENTS.md` 路由修复 + `ontology:concept/pdca-phase-status` 新节点 + `pdca_core.py` 溯源注释与保护删除 + 回归验证
- 不做：43 个零引用 py 的批量溯源（放 P2）；不改门禁语义，仅补锚与删死码

## 功能需求

1. **AGENTS路由归位**：4 处 `ontology/domain/skill-{advance-phase,to-tickets,grilling,register-evidence}.md` 改为实路径 `ontology/domain/pdca/skill-*.md`，`generate-skills-index.py` 重跑无漂移
2. **PHASE_STATUS本体化**：新建 `ontology:concept/pdca-phase-status`（`phase→status/active` 映射表 + testable_signal），`pdca_core.py:19` 加 `ontology:` 溯源注释
3. **knowledge删保护**：`PROTECTED_PREFIXES` 去掉 `knowledge`，认 `ontology/` 为唯一知识载体，附理由注释

## 验收标准

- [ ] AC-1 AGENTS路由已修：`python3 scripts/pdca-doctor.py --json | jq .missing_references==[]`，且 `grep -q ontology/domain/pdca/skill-advance-phase AGENTS.md` 命中
- [ ] AC-2 本体锚欠账已清：`ontology/concept/pdca-phase-status.md` 存在且 `ontology-validate OK`，`pdca_core.py` 含 `ontology:concept/pdca-phase-status` 引用，`PROTECTED_PREFIXES` 无 `knowledge`，且 `validate OK + islands:0` 可重跑

## 关联本体节点

```
ontology:concept/pdca-architecture
ontology:concept/pdca-phase
ontology:concept/knowledge-artifact
```

## 拆分映射

- AGENTS路由归位 -> T2046a 路由
- PHASE_STATUS本体化+knowledge删保护 -> T2046b 锚
