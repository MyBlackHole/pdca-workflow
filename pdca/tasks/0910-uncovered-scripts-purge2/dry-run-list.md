# dry-run 分级清单（T2130 第二轮purge）

判据：沿用T2127四类保留（运行时导入 / kept调用 / CI链 / 他人在途）。任一命中即保留。

## 候选删除（1项，需用户逐项确认）

- [ ] D-1 `scripts/validate-gate.sh` —— 全仓零引用（文档/tests/脚本/.github/根文档均无引用）；仅为 `validate-workflow.py --gate` 的薄包装，功能无损（`validate-workflow.py` 本体保留，4处本体引用）。

## 保留（49项，证据摘要）

- 高引用核心：ontology-validate.py（447本体引用）、production-ontology-gate.py（34）、ontology_test_scaffold.py（35）、ontology_graph.py（26）、pdca_core.py（18跨脚本import+15测试引用）、compute-frontier.py、validate-convergence.py、check-design-vocab.py、audit-ontology-fidelity.py（本体+测试+互引）。
- 门禁链：transition-phase.py、task_identity.py、append-confirmation.py、register-evidence.py、check-research-web-evidence.py、check-research-ontology-settlement.py、check-seam-contracts.py、check-skill-structure.py、check-ticket-claims.py、check-triage-brief.py、ci-ontology-gate.py（.github+hook）、ontology-clash-check.py、scenario-boundary-check.py、ontology_tree_split.py、ticket_dag.py、out-of-scope-manager.py、recall-brief-decisions.py、remediate-gate-compliance.py、audit-gate-compliance.py（本体/测试/互引覆盖）。
- 弱引用但有覆盖：check-ontology-thoroughness.py（skill-ontology-check引用）、check-ontology-topic-coverage.py（scenario-research-first-gate引用）、wizard-template.sh（skill-wizard引用）、grilling-rounds-demo.py（本体+test_grilling_efficiency引用）、create-improvement-candidate.py（auto-induce-flow-trigger+ontology_gate.py调用）、self-audit.py（2本体+test_self_audit引用）、seam_contract.py（3本体引用）、ontology_gate.py（12引用）、ontology_induction.py、ontology_reason.py（6跨脚本import）、pdca_context.py、pdca-doctor.py、flow_audit.py、flow_issues.py（6引用）、arch_review.py、audit-skill-content.py、generate-skills-index.py、run-ai-friendliness-fixtures.py、resolve-ai-*（3件互引覆盖）、rollback-phase.py/.sh、init-external.sh（AGENTS外部项目模式引用）、install-git-hook.sh（hook自引）、validate-workflow.py。

## 观察项（非删除对象，另起任务）

- O-1 `scripts/oops_scan.py`：`ontology/pattern/ontology-evaluation-oops.md` 有覆盖声明但文件缺失（悬空引用），需修文档或补脚本。
- O-2 `scripts/proto_ontology_to_owl.py`：`ontology/README.md` 有覆盖声明但文件缺失（悬空引用），同上。

## 基线

- 删前 pytest：51 failed / 371 passed（见 `baseline-failures.txt`，多为历史预存失败，与T2059腐烂线相关）。
- 删后要求：失败集与基线一致（`diff` 为空），validate 通过。

## tests/ 覆盖扫描（范围追加，2026-09-09）

- 方法：逐文件提取 `scripts/*` 引用（import/subprocess/ROOT拼接）核对存在性；零引用文件深查其断言的本体节点/模板存在性。
- 结论：63个测试文件全部有覆盖，**零候选删除**。
  - 48个直接引用现存脚本（import/subprocess/ROOT拼接，目标全部存在）。
  - 15个零脚本引用：深查后覆盖对象均存在（skill-design-it-twice / skill-resolving-merge-conflicts / skill-diagnosing-bugs / skill-writing-great-skills / templates/to-spec/SPEC.md / ontology-clash-check.py / recall-brief-decisions.py / register-evidence.py / check-research-web-evidence.py / check-triage-brief.py / audit-gate-compliance.py / remediate-gate-compliance.py / check-skill-structure.py / ontology_tree_split）。
- 观察项（非删除对象）：
  - O-3 `tests/test_diagnosing_bugs_enhance.py::test_hitl_template_file_exists` 恒失败：断言 `ontology/domain/diagnosing-bugs/hitl-loop.template.sh` 存在，但该目录缺失。测试本体覆盖完备（skill-diagnosing-bugs.md存在），缺的是被测对象；正确处置是补模板或修测试，另起任务，不删测试掩盖缺口。

## 测试用例本体对应审查（2026-09-09，63/63）

- 方法：逐文件提取 scripts 引用（`scripts/`前缀/import/ROOT拼接/importlib）+ 本体引用（字面量/ROOT链）+ 模板引用，逐项核对存在性；GAP 项人工复核原文。
- 结论：**63/63 全部有 PDCA 本体对应逻辑，测试侧零缺口**。初筛 11 GAP 经复核全为误报：
  - 测试内临时夹具（arch hotspots 的 big/small、gate_negative/scenario_boundary 的 check/tool/x 传参）：`tmp_path` fixture 或 CLI 虚构参数，非真实引用。
  - ROOT 链式拼接还原误差（deepening/gotchas/merge/out_of_scope 等）：目标 `ontology/domain/pdca/skill-*.md` 全部存在。
  - execution/invocation 测试自建隔离 fixture（`write_asset` 自造 skill 文档断言解析逻辑），真实本体文件齐备。
- 矩阵见 `test-ontology-matrix.txt`。本体/脚本侧缺口仍为 O-1/O-2/O-3（文档有声明无文件 / 被测模板缺失），属被测对象侧，不归因测试。
