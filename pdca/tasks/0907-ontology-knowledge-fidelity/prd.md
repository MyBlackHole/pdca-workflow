# PRD — 知识类本体保真：防止 pattern/principle/pitfall/fact/decision 空洞化

> 任务：T2070 / 0907-ontology-knowledge-fidelity / scenario: development / phase: plan
> 前置任务：T2068（本体创建预防门禁）、T2069（本体全生命周期保真）已完成

## 背景与问题

知识类本体（`pattern/`、`principle/`、`pitfall/`、`fact/`、`decision/`）是抽象知识实体，与 domain/entity 不同——它们描述的是**方法论、准则、易错点、稳定事实**，而非代码结构。

**核心问题**：知识类本体比 domain/entity 更容易空洞化：

1. **抽象性**：知识类本体没有直接代码引用，`testable_signal` 难以定义
2. **主观性**：知识类本体的正确性依赖领域专家判断，无法通过 `grep -q` 验证
3. **缺乏 grounding**：知识类本体通常不引用具体代码文件，难以声明 grounding 来源
4. **编写动机不纯**：知识类本体容易成为"为了知识而知识"的产物，缺乏实际指导价值
5. **验证缺失**：现有 `ontology-validate.py --check fidelity` 对知识类本体的检查不够精准（如"正反例"在 principle 中不适用）

T2068/T2069 已解决 domain/entity 的创建预防和全生命周期保真，本任务解决**知识类本体的特殊性**——确保它们不是空洞的知识堆砌。

## 目标

建立知识类本体保真机制，确保每个知识类本体：

1. **有可验证的指导价值** — 不是抽象理论，而是可操作的实践指南
2. **有明确的适用场景** — 知道什么时候该用、什么时候不该用
3. **有正反例或证据支撑** — 知识不是凭空而来，有来源可追溯
4. **有可执行信号或等效验证** — 即使不能用 `grep -q`，也有替代验证方式
5. **有领域专家确认** — 关键知识需经专家验证标记

## 非目标

- 不重写 T2068/T2069 的门禁（T2068/T2069 已覆盖所有本体节点）
- 不修改知识类本体的格式定义

## 验收标准

- [ ] AC-1：每个pattern/principle/pitfall/fact/decision节点必须声明applicability和boundary，scripts/ontology-knowledge-applicability.py可执行，缺失适用场景的节点被拒绝
- [ ] AC-2：每个知识类本体必须声明evidence_source，scripts/ontology-knowledge-evidence.py可执行，允许非代码验证方式（expert-review/experiment/case-study）
- [ ] AC-3：新增verification_method字段（code-grep/expert-review/experiment/case-study），scripts/ontology-knowledge-backtest.py可执行，对code-grep类信号执行代码验证，对其他类输出验证报告
- [ ] AC-4：pattern/principle必须有case_study，pitfall必须有counterexample，fact必须有source_record，scripts/ontology-knowledge-examples.py可执行检查案例完备性
- [ ] AC-5：frontmatter新增reviewer字段，scripts/ontology-knowledge-review.py可执行，未经确认的节点标注pending-review
- [ ] AC-6：scripts/ontology-knowledge-quality.py可执行，统计适用场景覆盖率、案例覆盖率、专家确认率、空洞节点比例
- [ ] AC-7：6个方向全部通过validate-convergence

## 约束

- 不改变知识类本体的现有格式（向后兼容）
- `verification_method` 字段须有 `rule_spec` 本体锚定
- 知识类本体的 `testable_signal` 允许使用非代码验证方式，但不可为空

## 前置依赖

- T2068（本体创建预防门禁）已完成
- T2069（本体全生命周期保真）已完成
- `ontology:concept/ontology-fidelity-criterion` 已存在
