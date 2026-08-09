# PRD — PDCA 流程实现审查（CI 落地前置）

## 背景

T0242 判定 CI 基础设施为"候选"（依赖平台决策）。用户选择先审查 PDCA 流程
实现现状，识别门禁/测试/doctor 覆盖缺口，评估 CI 落地前置条件，产出报告
后再决定是否建 CI 任务。

## 需求

### R1 门禁完整性审查
审查 `scripts/transition-phase.py` 的 gate 检查项与各阶段转换约束：
- 列出全部 gate 项（schema/final_confirmation/convergence/disposition/verdict
  等），确认与 flow-plan/do/check/act 描述一致
- 识别缺失的 gate 或可绕过的路径

### R2 测试覆盖审查
审查 `tests/` 对门禁/契约/doctor 行为的覆盖：
- 全量 157 passed 覆盖哪些行为域（operations/seam/ci-gate/convergence/audit/
  flow-issues 等）
- 识别未覆盖的高风险路径（如 transition 异常、doctor 失败聚合）

### R3 doctor 覆盖审查
审查 `scripts/pdca-doctor.py --json` 现有段：
- 列出现有段（capabilities/references/task_timeline/seam_contracts 等）
- 对比全部门禁项，识别未纳入 doctor 的检查（CI 应触发哪些）

### R4 CI 落地前置缺口
基于 R1-R3 产出 CI 前置清单：
- 哪些项必须先在 CI 前修复（依赖声明、路径假设、网络、权限）
- CI workflow 建议的最小命令集
- 无法在 CI 验证的项（需本地/交互）明示排除

### R5 审查报告
产出 `research-report.md`，含逐维发现、缺口表、CI 就绪度结论。

## 验收标准

- [ ] AC-1: 门禁清单完整（R1），与 flow 文档一致，含可绕过路径识别
- [ ] AC-2: 测试覆盖域表（R2），含未覆盖高风险路径清单
- [ ] AC-3: doctor 段清单 + 未纳入检查清单（R3）
- [ ] AC-4: CI 前置缺口表 + 最小命令集 + 排除项（R4）
- [ ] AC-5: research-report.md 产出，含 CI 就绪度结论与建议（R5）

## 收敛条件

- [ ] CC-1: 上述 AC 全部满足
- [ ] CC-2: 报告给出明确建议：可直接落地 CI / 需先修 X 再 CI / 不建议 CI

### 声明的测试接缝

（research 场景，无 seam 声明——审查产出报告不修改代码）
