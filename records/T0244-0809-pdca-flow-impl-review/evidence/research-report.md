# Research Report — PDCA 流程实现审查（CI 落地前置）

## 结论速览

| 维度 | 状态 | 关键发现 |
|------|------|---------|
| R1 门禁完整性 | ✅ 完整 | gate_issues 覆盖 5 阶段 16 项检查，无可绕过路径 |
| R2 测试覆盖 | ✅ 良好 | 39 测试类 / 157 用例，门禁主流程有操作级测试 |
| R3 doctor 覆盖 | ⚠️ 有缺口 | doctor 不检查任务门禁合规（convergence/verdict/disposition） |
| R4 CI 前置 | ⚠️ 1 个必修 | doctor 需补门禁检查或 CI 需加 validate 步骤 |

**CI 就绪度：可以直接落地 CI，但需补 1 个检查项**（R3 缺口）。若不补，
CI 跑 doctor 会漏掉任务门禁违规。

## R1 门禁完整性

`scripts/pdca_core.py:534 gate_issues()` 按阶段检查：

| 阶段 | gate 项 |
|------|---------|
| 通用 | SCHEMA_INVALID、FINAL_CONFIRMATION_TIME_ORDER、STATE_TIME_ORDER |
| plan | FINAL_CONFIRMATION_MISSING |
| do | PRD_MISSING、evidence_issues（CONVERGENCE_* 系列 8 项） |
| check | CONCLUSION_MISSING、VERDICT_MISSING、CHECK_CONFIRMATION_MISSING |
| act | DISPOSITION_MISSING |
| archive | task_issues 全量（含 phase 约束） |

无缺失 gate，无已知可绕过路径。`validate-workflow.py --gate` 可对单任务
执行全量门禁批检（validate-gate.sh 为稳定入口）。

## R2 测试覆盖域

39 测试类 / 157 用例 + 13 subtests，按行为域：

| 域 | 测试类 | 用例数 |
|----|--------|--------|
| transition/gate 主流程 | OperationsTest、PlanTimestampBackfillTest | ~45 |
| seam 契约 | SeamParse/SeamFileExistence/FlowPlanSeamGate/SpecTemplate | ~20 |
| CI 门禁 | CheckSeamContractsTest | 5 |
| convergence | ConvergenceContractTest | ~10 |
| grilling | BatchRoundsModel/GrillingDocument/SourceConsistency/... | ~25 |
| ticket-dag/ready-set | ComputeReadySet/TaskSchema/ComputeFrontier/DesignVocab | ~25 |
| 状态机 | StateTimeOrderGuidanceTest、ContractTest(state) | ~10 |
| flow-issues/audit | FlowIssueCliTest、FlowAuditTest | ~15 |
| ai-friendliness | AiFriendlinessHardeningTest | ~8 |
| content-audit | ContentAuditTest、ContentAuditContractTest | ~6 |
| execution/invocation | Execution/Invocation/ContentAuditContract | ~12 |
| diagnosing-bugs 增强 | 6 个契约测试类 | 10 |

覆盖良好。门禁主流程（plan→do→check→act→archive）有操作级回归测试。

## R3 doctor 覆盖缺口

`scripts/pdca-doctor.py --json` 现有段：

- capabilities / references_checked / missing_required / missing_references
- task_timeline / seam_contracts / warning

**关键缺口**：doctor 不调用 `gate_issues()`——**不检查任务门禁合规**
（convergence map、verdict、disposition、PRD 存在性、conclusion 存在性）。
doctor 是"体检"（文件/引用/时间线/seam），不是"门禁"（阶段合规）。

## R4 CI 落地前置

### 必修项
1. **doctor 补门禁检查**（或在 CI 中加 validate 步骤）：若 CI 只跑
   `pdca-doctor.py --json`，会漏掉任务门禁违规。两个方案：
   - A：doctor 新增 `gate` 段，聚合全部活跃任务的 gate_issues（与
     seam_contracts 同构，复用 pdca_core.gate_issues）
   - B：CI workflow 额外跑 `python3 scripts/check-task-gates.py`（新脚本）或
     遍历活跃任务跑 validate-workflow.py --gate

### 建议 CI 最小命令集
```yaml
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with: { python-version: '3.11' }
  - run: pip install pytest
  - run: python3 -m pytest tests/ -q
  - run: python3 scripts/pdca-doctor.py --json
  - run: python3 scripts/audit-skill-content.py --check-budget --root .
  - run: python3 scripts/check-seam-contracts.py --root .
```

### 排除项（无法在 CI 验证）
- 需要真实模型/外部环境的 grilling 轮次演示
- 需交互确认的 check_confirmation / final_confirmation 语义
- 外部项目（apps/）的 seam（生命周期可能随外部 repo 变动）

### 依赖
- 仓库纯 Python 标准库 + pytest，无第三方依赖，CI 安装成本极低。
- 脚本均用 `Path(__file__).parent` 定位（T0241 已解耦），无 cwd 假设。

## 建议

**方案 A（推荐）**：doctor 新增 `gate` 段聚合活跃任务门禁 → CI 一行
`pdca-doctor.py --json` 即可覆盖全部检查（体检 + 门禁 + seam + budget）。
可作为独立小任务（T0245）实现，或直接并入 CI 落地任务。

**落地路径**：T0244 报告确认 → T0245 建 .github/workflows/ci.yml +
（可选）doctor gate 段 → 推送验证。
