# T0414 对话日志（dialogue-log）

## Plan
- 触发：用户审查后认为 PDCA 本体尚未全流程闭环（证据/结论未锚定、archive 无自检、无 CI 硬门禁），要求立 T0414 补全闭环 + 硬门禁。
- 范围确认：用户选择"立 T0414 补全闭环+硬门禁"。
- 设计：用户确认 B3 参数化（本体为门禁唯一事实源）风格延续；证据锚定 pdca-evidence 子类型、结论锚定 pdca-verdict 三态、archive 跑 ontology-validate+孤岛、ci-ontology-gate 抽共享逻辑供 hook/workflow 复用。
- 非目标：plan/do/check/act 本体消费保持顾问式不阻断；git hook 可选安装不静默改动 .git/hooks。
- 门禁：PRD 含 `## 验收标准` 勾选框；final_confirmation 已登记；transition plan→do 通过。

## Do
- 实现 AC-1：register-evidence 加载 pdca-evidence 子类型建立允许表，命中写 evidence_type_ref，未知 kind 报错。
- 实现 AC-2：新增 verdict-rejected/partial 节点（specializes pdca-verdict）；verdict_anchor_issues 校验 outcome 映射。
- 实现 AC-3：archive_ontology_ready_issues（ontology-validate + 孤岛检查）；transition-phase 到 archive 时拦截。
- 实现 AC-4：ci-ontology-gate.py + install-git-hook.sh + .github/workflows/ontology-gate.yml。
- 实现 AC-5：ADR-0036、ontology/README.md §10、ONTOLOGY_GUIDE.md §13、flow-act SKILL Ac8。
- 实现 AC-6：本体相关既有测试 36 通过；ontology-validate OK、无孤岛；ci-gate OK。
- 调试插曲：archive_ontology_ready_issues 曾误用全局 ROOT 且 ontology_graph 参数误用 `--ontology-dir`（应为 `--root`）；修复并补测试通过。
- 证据：登记 19 条，收敛图 valid:true。

## Check
- conclusion.md 逐条 AC ✅ 并回链证据 ID。
- verdict.outcome=confirmed（verdict_id=T0414-verdict-001）。
- check_confirmation 已登记（confirmed）。

## Act
- knowledge_decision=skipped（交付物已是可复用资产，无需孤立知识条目）。
- disposition=projected。
- journal 2026-08-30.md 已写；本 dialogue-log 已写。

## 已知债
- `tests/test_ontology_validate.py` 3 例因 T0413 节点化后临时本体缺 6 个 rule 节点而失败，非本任务范围，建议另立任务修复。
