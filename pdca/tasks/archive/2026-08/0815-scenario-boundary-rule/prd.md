# 模式边界判定规则：research/development 场景归属裁决

## 问题

六种 `scenario_type` 覆盖需求分类足够，但边界情形无明确归属规则。元审查系列 T0268-T0272 均标 `research`，实际却产出可测试工具代码（脚本 + 测试 + 全量回归），与 research 路径 C（仅调研+报告）不符，实际按 development 流程执行。triage 阶段缺少机械判定手段。

## 方案

新增独立检查脚本，为场景归属提供机械判定；接入 triage 校验器链可执行验证。判定标准：**含可测试代码产出 → development；纯结论性调研 → research**。历史错配任务（T0268-T0272）不改，仅作为回归夹具验证脚本输出。

## 用户故事

- 作为 triager，当我分类含工具代码产出的分析类任务时，判定脚本能明确归入 development，避免 research 路径缺 TDD/回归验证。
- 作为校验器，当我运行检查时，能对历史错配任务输出与期望一致的归属。

## 验收标准

- [ ] AC-1: 新增 `scripts/scenario-boundary-check.py`，输入任务描述或 brief，输出场景归属判定（development/research 等）与依据
- [ ] AC-2: 判定规则实现：含可测试代码产出信号（脚本/测试/可回归验证）→ development；纯结论性调研 → research
- [ ] AC-3: 对历史错配任务 T0268-T0272 运行检查，输出全部判定为 development，与期望一致
- [ ] AC-4: 对纯 research 任务（如 T0249 kernel-nfs-gm-research）运行检查，输出判定为 research
- [ ] AC-5: 判定脚本接入 triage 校验器链，`validate-gate.sh` 或等价全量验证覆盖
- [ ] AC-6: 新增测试覆盖判定规则（含边界用例：含报告但无代码产出、含工具代码无报告、两者皆无），全量测试通过且无回归

## Seam 分析

### 声明的测试接缝
- seam: tests/test_scenario_boundary_check.py -> scripts/scenario-boundary-check.py

## 实现/测试决策

- 判定输入用结构化信号（产出的脚本/测试文件存在性 + 描述关键词），优先用真实任务证据（scripts/ 目录、tests/ 目录、产出文件后缀）而非纯关键词。
- 回归夹具从归档任务元数据构造：T0268-T0272（期望 development）、T0249 等纯 research（期望 research）。
- 校验器接入点：参考 check-triage-brief.py 的接入方式，避免重复扫描。

## 范围外

- 不改六种场景的步骤内容（flow-do A-F 路径）
- 不重分类历史归档任务的 scenario_type
- 不扩展六场景之外的第七种模式

## 备注

- 来源：T0272 自我审查发现 5/25 research 任务实际执行 development 工作，根因是边界判定缺失。
- 与 T0139（六场景 harness）、T0244（流程实现审查）不重复：二者未覆盖归属判定规则。
