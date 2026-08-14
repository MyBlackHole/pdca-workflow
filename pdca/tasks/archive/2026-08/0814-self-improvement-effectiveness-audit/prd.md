# PDCA 自我提升机制有效性检查 — 规格文档

## 问题陈述

- **现状**: T0159 已实现并验证自我优化闭环的 schema、CLI、确定性夹具与门禁，但其 Check 结论明确要求在真实使用周期继续观察。
- **目标**: 提升本项目使用 AI 的效率；先用真实 AI 使用记录识别并证明可优化问题，再判断现有自我提升机制能否把这些事实转化为受控改进和跨周期效果验证。
- **差距**: 当前尚未证明 flow occurrence 与 AI 效率损失之间的对应关系，也未验证现有记录方式是否能发现、定位和推动真实问题，而不是只积累无行动价值的记录。

## 已知事实

- `pdca/improvements/flow-issue-cutover.json` 于 2026-07-30 启用 v1 机制。
- 当前仓库存在 199 个 `flow-events` occurrence；最晚 occurrence 时间为 2026-08-14。
- 当前 `flow-issue-backlog.json` 仅包含 14 个 issue、34 个 occurrence，事件时间止于 2026-07-31，明显未覆盖全部现存 occurrence。
- `records/*/flow-improvements/*` 当前没有 decision、candidate 或 effectiveness verdict 文件。
- `pdca-doctor.py --json` 当前返回 `valid: false`，并报告多项任务 schema/timeline 与 seam contract 异常。

## 解决方案

执行只读有效性审计：先从非 flow-event 的真实任务产物独立建立效率损失参照集，再检查现有记录方式能否捕获、定位、聚合并推动这些问题进入受控改进与效果验证。区分直接观测、代理指标、夹具和猜测，对漏报、噪声、陈旧投影和转化缺口给出可追溯根因及建议处置。本任务不自动修改权威流程或修复被审计问题。

## Seam 分析

research 场景不产生开发测试 seam。审计命令与生成的报告将作为证据登记；如运行现有测试，仅用于确认机制仍可执行，不作为真实运行有效性的替代证据。

## 用户故事

1. 作为 AI 工作流使用者，我想从真实任务记录中识别反复返工、交互或恢复成本，以便只优化确实影响效率的问题。
2. 作为流程所有者，我想验证现有记录方式能否发现、定位和聚合这些问题，以便避免维护没有行动价值的记录系统。
3. 作为流程治理者，我想知道已发现问题是否进入候选、实施和效果验证，以便定位自我提升闭环的首个阻断点。
4. 作为后续改进负责人，我想获得有证据边界的候选排序和观察计划，以便决定是否另开 Improvement Task。

## 实现决策

- 审计对象为 T0159 定义的完整链路：occurrence → backlog issue → decision → candidate → Improvement Task → post-change observations → effectiveness verdict。
- AI 使用效率定义为完成合格任务所需的 AI 与用户投入，分别观察一次成功/返工、交互轮次、门禁失败与恢复，以及有真实遥测支持的 token、耗时和工具调用。
- 合格真实证据必须来自非 fixture 任务，并具备 task/record ID、时间、具体事实和可复查产物；缺失的遥测指标保持 `unknown`。
- 从 clarifications、阶段回退/重试、rejected/partial 结论、journal 和可复查失败证据建立独立参照集，再与 flow occurrence 交叉匹配。
- 将“实现正确性”“真实采用情况”“AI 效率损失”和“跨周期改进效果”分层评价。
- 使用仓库内不可变记录、活跃/归档任务、backlog 与现有 CLI 输出；不以控制产物自证效果。
- 只有同类损失出现在至少两个独立真实任务，或单次严重阻断具有明确因果链且排除替代解释，才列为真实可优化候选。
- 记录发现能力按覆盖、信噪、可行动性和转化及时性评价，并显式报告漏报。
- 记录方式只有在至少发现一个满足候选门槛、经独立证实且足以支持后续验证的真实效率问题时才可判定 effective；有真实发现但存在严重漏报、陈旧投影、噪声或无治理转化时判为 partial；无记录通过门槛时判为 ineffective。
- 结论采用明确等级和逐环节 pass/fail；输出证据排序的候选清单和验证计划，不创建正式 Improvement Candidate。

## 测试决策

- 对计数、时间范围、引用完整性和链路可达性使用可重复的只读命令。
- 必要时运行现有 flow issue 测试/fixture，确认“当前仍可运行”；与真实记录审计分别报告。
- 对 backlog 输入摘要与实际 occurrence 集合做一致性/新鲜度检查。
- 独立参照集先于 occurrence 匹配生成；匹配结果至少区分 true positive、false negative、未能独立证实和重复记录。
- 对每个候选保留反证栏，检查任务自身缺陷、旧 schema、人工违规或同一根事件重复上报等替代解释。

## 验收标准

- [ ] AC-1: 报告区分机制实现正确性、真实采用情况和跨周期效果，不以 fixture 代替真实使用证据。
- [ ] AC-2: 建立真实 AI 使用记录清单，并按一次成功/返工、交互轮次、门禁失败与恢复、真实 token/耗时/工具调用报告可测与 unknown 指标。
- [ ] AC-3: 给出 cutover 后 occurrence 的总量、时间范围、来源/问题分布，并验证 backlog 的覆盖率与新鲜度。
- [ ] AC-4: 逐项盘点 issue、decision、candidate、Improvement Task、post-change observation 和 effectiveness verdict，引用可复查路径或命令输出。
- [ ] AC-5: 至少运行一组现有确定性验证，说明机制当前是否仍可执行，并将其结果与真实 AI 使用效率分开。
- [ ] AC-6: 从非 flow-event 真实任务产物建立独立效率损失参照集，并给出其与 occurrence 的匹配、漏报及证据限制。
- [ ] AC-7: 按覆盖、信噪、可行动性和转化及时性评价记录方式，不以记录数量替代发现价值。
- [ ] AC-8: 仅将满足重复性或单次严重因果门槛、且已检查替代解释的问题列为优化候选；每项绑定真实任务证据。
- [ ] AC-9: 对候选按证据强度和潜在效率影响排序，并给出 baseline、指标与后续观察计划；不创建正式 Improvement Candidate。
- [ ] AC-10: 分别对记录发现能力和完整改进闭环给出 effective、partial 或 ineffective 结论，并指出首个阻断点。
- [ ] AC-11: 对发现的每个关键缺口给出证据限制和最小后续动作；不可测指标明确标记 unknown，不作猜测。
- [ ] AC-12: 将审计证据通过 register-evidence 登记，并在 Check 阶段对照 PRD 写入 conclusion 后请求用户确认。

## 范围外

- 不修改 `flows/`、`skills/`、schema、gate 或现有自我提升脚本。
- 不自动创建或晋级 Improvement Candidate/Task。
- 不修复 doctor 报告的任务、时间线或 seam 异常。
- 不用单次审计推断长期模型成功率或跨平台行为。
- 不把 UTF-8 bytes、fixture 轮数模型或文件 mtime 称为真实 token、耗时或模型成功率。

## 备注

- 任务分类：enhancement / research。
- 查重结果：T0159 是被验证的既有实现，不与本次“真实运行有效性复查”重复。
- `PDCA_HOME` 未设置，本轮使用仓库根目录 fallback。
- P4 拆解判断：所有分析步骤共享同一真实任务总体和同一证据矩阵，任一部分都不足以构成独立 PDCA 周期，因此保持单一任务，不创建子任务。
