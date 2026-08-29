# T0414 PRD：本体全流程闭环 + 硬门禁

- 任务 ID：T0414
- 父任务 / 依赖：T0413（validator 已节点化驱动）；T0412（meta-ontology 门禁节点）
- 场景类型：development

## 背景与问题

审查结论（见对话）：PDCA 元本体已"生命周期感知"——plan/do/check/act 均有软消费，转换合法性与本体创建两道硬门禁已就位；但**尚未全流程闭环**，缺口有三：
1. **证据/结论未锚定本体**：`register-evidence --kind` 是自由字符串，未与 `pdca-evidence` 子类型（`evidence-convergence-map`/`evidence-review`/`evidence-test-result`）对齐；`pdca-verdict` 仅有 `verdict-confirmed` 一个子类型，缺 `rejected`/`partial`。结论（verdict）与证据目前只是 task 字段/文件，未与本体节点机器锚定。
2. **archive 阶段无本体自检**：归档前不跑 `ontology-validate`/孤岛检查，本体可能在归档瞬间已损坏而无人察觉。
3. **无 CI/git hook 硬门禁**：所有门禁在提交时都是软的，可绕过。

目标：把上述三类缺口补上，使本体成为**提交级、全阶段闭环**的权威（即"全流程生命周期化"）。

## 设计概览

### Part 1 证据锚定（register-evidence 对齐 pdca-evidence 子类型）
- `scripts/register-evidence.py` 启动/校验时从 `ontology/` 加载 `pdca-evidence` 的全部子类型（按 `specializes: pdca-evidence` 枚举），建立 `kind 短名 → 本体节点 id` 的允许表（含向后兼容别名：convergence-map→evidence-convergence-map、review→evidence-review、test-result→evidence-test-result、test→evidence-test-result 等）。
- `--kind` 必须在允许表内；命中子类型时置 `evidence_type_ref = 本体节点 id` 并校验该引用可解析（否则报错）。未知 kind 直接报错——证据自此机器锚定到本体。
- 既有支持型 kind（document/concept/script/adr/skill/validation-report/documentation）保留为"未定型支持证据"，不强制子类型，但同表内须可解析或显式豁免。

### Part 2 结论锚定（verdict 映射 pdca-verdict 子类型）
- 补全 `pdca-verdict` 子类型：新增 `ontology/entity/verdict-rejected.md`、`ontology/entity/verdict-partial.md`（specializes `pdca-verdict`），与现有 `verdict-confirmed` 构成完整三态。
- `meta.verdict.outcome` ∈ {confirmed, rejected, partial} 必须映射到已存在的 `verdict-<outcome>` 节点；提供轻量校验（在 `write-conclusion` 或 transition 入口）确保结论锚定本体，映射失败时阻断。

### Part 3 archive 本体自检
- `flows/flow-act/SKILL.md` Ac8 增加：归档前运行 `python3 scripts/ontology-validate.py` 与 `python3 scripts/ontology_graph.py --format summary`（islands==0）；任一失败则停止归档并报告。
- `transition-phase.py` 在目标为 `archive` 时于 disposition 校验后追加 ontology-readiness 检查（复用 ontology_gate 的校验精神），本体不合法则拒绝转换。

### Part 4 提交级硬门禁（CI + git hook）
- 新增 `scripts/install-git-hook.sh`：安装 `.git/hooks/pre-commit`，仅当 `ontology/**` 变更时运行 `ontology-validate.py` + 对应任务 `validate-convergence.py`，非零退出即阻断提交（可选安装，不强制，避免惊扰）。
- 新增 `.github/workflows/ontology-gate.yml`（若仓库走 GitHub Actions）：push/PR 时跑同样检查，作为远端硬门禁。
- 硬门禁逻辑抽为 `scripts/ci-ontology-gate.py`（接收变更文件列表，跑校验并返回退出码），供 hook 与 workflow 共用，便于测试。

## 验收条件（AC）

- [x] AC-1（证据锚定）：`register-evidence` 从 `pdca-evidence` 子类型派生允许 kind 表并校验；命中子类型时写入 `evidence_type_ref` 且引用可解析；未知 kind 报错。新增 `tests/test_register_evidence_anchor.py` 覆盖命中/未命中/未知 kind。
- [x] AC-2（结论锚定）：新增 `verdict-rejected.md`/`verdict-partial.md` 节点（specializes pdca-verdict）；`meta.verdict.outcome` 必须映射到存在的 `verdict-<outcome>` 节点，否则阻断；新增测试覆盖三态映射与缺失阻断。
- [x] AC-3（archive 自检）：`flow-act` Ac8 与 `transition-phase` 到 archive 时运行 `ontology-validate` + 孤岛检查，本体不合法则拒绝归档；测试模拟本体损坏时 archive 被拒。
- [x] AC-4（硬门禁）：`scripts/ci-ontology-gate.py` 实现共享门禁逻辑；`install-git-hook.sh` 安装 pre-commit；`.github/workflows/ontology-gate.yml` 落地；`tests/test_ci_ontology_gate.py` 断言坏本体非零退出、好本体零退出。
- [x] AC-5（文档）：`docs/ONTOLOGY_GUIDE.md`、`ontology/README.md` §9、`flows/flow-act/SKILL.md` 更新"全流程闭环 + 硬门禁"说明；新建 `docs/adr/ADR-0036-ontology-full-lifecycle-gate.md` 记录决策。
- [x] AC-6（回归）：现有 `test_ontology_reason/induction/pdca_ontology_correct/meta_ontology/ontology_validator_from_nodes` 全量通过；当前 `ontology/` 经 `ontology-validate` OK、无孤岛；`validate-convergence` 对既有归档任务仍 valid。

## 验收标准

- [x] AC-1（证据锚定）：`register-evidence` 从 `pdca-evidence` 子类型派生允许 kind 表并校验；命中子类型时写入 `evidence_type_ref` 且引用可解析；未知 kind 报错；`tests/test_register_evidence_anchor.py` 覆盖命中/未命中/未知 kind。
- [x] AC-2（结论锚定）：新增 `verdict-rejected.md`/`verdict-partial.md` 节点（specializes pdca-verdict）；`meta.verdict.outcome` 必须映射到存在的 `verdict-<outcome>` 节点否则阻断；测试覆盖三态与缺失阻断。
- [x] AC-3（archive 自检）：`flow-act` Ac8 与 `transition-phase` 到 archive 时运行 `ontology-validate` + 孤岛检查，本体不合法则拒绝归档；测试模拟损坏时 archive 被拒。
- [x] AC-4（硬门禁）：`scripts/ci-ontology-gate.py` 实现共享门禁逻辑；`install-git-hook.sh` 安装 pre-commit；`.github/workflows/ontology-gate.yml` 落地；`tests/test_ci_ontology_gate.py` 断言坏本体非零退出、好本体零退出。
- [x] AC-5（文档）：`docs/ONTOLOGY_GUIDE.md`、`ontology/README.md` §9、`flows/flow-act/SKILL.md` 更新闭环+硬门禁说明；新建 `docs/adr/ADR-0036-ontology-full-lifecycle-gate.md`。
- [x] AC-6（回归）：既有 `test_ontology_reason/induction/pdca_ontology_correct/meta_ontology/ontology_validator_from_nodes` 全量通过；当前 `ontology/` 经 `ontology-validate` OK、无孤岛；既有归档任务 `validate-convergence` 仍 valid。

## 非目标（范围边界）

- 不把 plan/do/check/act 的本体消费改成阻断式（保持顾问式，避免 YAGNI 与吞吐损失）。
- 不改动 `ontology-validate.py` 的 AC 逻辑（T0413 已节点化）。
- git hook 为可选安装，不自动写入用户 `.git/hooks`（避免静默改变提交行为）。

## 风险与缓解

- **破坏既有 register-evidence 调用**：用向后兼容别名表，仅未知 kind 报错；既有 kind（document 等）保留为支持证据不强制子类型。
- **archive 自检误伤**：仅在校验器本身报错时阻断，孤岛/无环为标准健康度；现有本体已通过，不会误伤。
- **hook 惊扰**：install 脚本显式调用才安装，并提示如何卸载。
