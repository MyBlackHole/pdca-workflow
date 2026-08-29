# ADR-0036: 本体全流程闭环与提交级硬门禁

日期: 2026-08-29
状态: Accepted

## 背景

ADR-0034（T0412）把本体创建门禁建模为 `meta-ontology` 节点；ADR-0035（T0413）让 `ontology-validate.py` 运行时读取 `ontology-rule-*` 节点 `rule_spec` 作为检查参数唯一来源。至此"创建时"门禁已本体制化。但审查（对话）发现**尚未全流程闭环**，三类缺口：

1. **证据/结论未锚定本体**：`register-evidence --kind` 是自由字符串，未与 `pdca-evidence` 子类型对齐；`pdca-verdict` 仅有 `verdict-confirmed` 一个子类型，缺 `rejected`/`partial`，结论与证据只是 task 字段/文件，未与本体节点机器锚定。
2. **archive 阶段无本体自检**：归档前不跑 `ontology-validate`/孤岛检查，本体可能在归档瞬间已损坏而无人察觉。
3. **无 CI/git hook 硬门禁**：所有门禁在提交时都是软的，可绕过。

目标：把上述缺口补上，使本体成为**提交级、全阶段闭环**的权威。

## 决策

1. **证据锚定（AC-1）**：`scripts/register-evidence.py` 启动时从 `ontology/` 枚举 `pdca-evidence` 全部子类型，构建 `kind 短名 → 本体节点 id` 允许表（含别名 `test`→`evidence-test-result` 等）。`--kind` 必须在表内；命中子类型写 `evidence_type_ref = 本体节点 id` 并校验引用可解析；未知 kind 直接报错。既有支持型 kind（`document`/`concept`/`script`/`adr`/`skill`/`validation-report`/`documentation`）保留为"未定型支持证据"，不强制子类型。
2. **结论锚定（AC-2）**：新增 `ontology/entity/verdict-rejected.md`、`ontology/entity/verdict-partial.md`（均 `specializes: pdca-verdict`），与 `verdict-confirmed` 构成完整三态。`scripts/ontology_gate.verdict_anchor_issues` 在 `check/act/archive` 阶段校验 `meta.verdict.outcome` 映射到的 `verdict-<outcome>` 节点必须存在，缺失则阻断转换。
3. **archive 本体自检（AC-3）**：`scripts/ontology_gate.archive_ontology_ready_issues` 跑 `ontology-validate.py`（通过）+ `ontology_graph.py --format summary`（`islands == 0`）；`scripts/transition-phase.py` 在目标为 `archive` 时于 disposition 校验后追加该检查，本体不合法则拒绝转换。
4. **提交级硬门禁（AC-4）**：共享逻辑 `scripts/ci-ontology-gate.py`（收变更文件列表，跑 `ontology-validate` + 相关任务 `validate-convergence`，返回退出码）；`scripts/install-git-hook.sh` 可选安装 `pre-commit` 钩子（仅当 `ontology/**` 或 `pdca/tasks/**` 变更时运行，非零退出阻断提交）；`.github/workflows/ontology-gate.yml` 在远端 push/PR 复跑同一检查。三者共用 `ci-ontology-gate.py`，便于测试与一致。
5. **保持顾问式消费**：plan/do/check/act 的本体"消费"（如 do 阶段 `ontology-ready` 片段校验）保持非阻断，仅创建门禁、证据/结论锚定、archive 自检、CI/hook 为硬门禁——避免 YAGNI 与吞吐损失。

## 影响

- 证据自此机器锚定到 `pdca-evidence` 子类型，结论锚定到 `pdca-verdict` 三态；本体节点缺失即阻断，消除"字段自由字符串"漂移。
- 归档动作受本体健康度硬约束，本体损坏会在归档前被拦截。
- 普通提交（改动 `ontology/`）将被 pre-commit / CI 跑门禁拦截，门禁不可绕过；`install-git-hook.sh` 显式调用才安装，不静默改动用户 `.git/hooks`。
- 测试证据：`tests/test_register_evidence_anchor.py`（证据锚定三态）、`tests/test_ontology_full_lifecycle.py`（结论锚定、archive 自检、CI 门禁）、`tests/test_ci_ontology_gate.py` 逻辑内嵌于前者。
- 衔接：本 ADR 是 T0414 的落地授权；与 ADR-0034/0035 共同构成"创建→运行→全周期闭环"的本体门禁体系。
