# PRD — 本体创建预防门禁：确保未来本体内容符合实际

> 任务：T2068 / 0907-ontology-prevention-gate / scenario: development / phase: plan

## 背景与问题

本体保真度治理（T0534）和全量符合度审计（T0545）已分别完成存量本体治理与审计清零。但核心问题尚未从**源头预防**层面解决：

**"本体内容不符合实际"的根因**：

1. **创建无 grounding**：新本体节点可在无代码/证据来源的情况下被创建，导致"无源之水"
2. **fidelity 检查未覆盖创建环节**：`ontology-validate.py` 在创建时未被强制调用，开发者可绕过
3. **Grill 事实验证缺失**：Grill 阶段未强制要求验证本体所描述特性的真实代码存在性
4. **Provenance 投影纪律未硬化**：知识可在任意阶段被创建，未强制"先证据后本体"

T0534 解决了"已有本体怎么修"，T0545 解决了"现有本体哪些不合格"，本任务解决"**以后创建的本体如何规避**"——从源头建立不可绕过的预防机制。

## 现有防线盘点（T0534/T0545 遗留）

| 防线 | 状态 | 缺口 |
|------|------|------|
| `ontology-validate.py` AC-1~AC-6 | ✅ 已有 | 未在创建时强制调用 |
| fidelity 七项清单 | ✅ `ontology:concept/ontology-fidelity-criterion` 已建 | 未在 CI 中默认启用 |
| `ontology-rule-fidelity-*` 节点 | ✅ 已建 | rule_spec 已锚定 |
| `ontology-creation-gate` | ✅ 已建 | 人工入口 `ontology-check` skill 存在但未被强制 |
| `knowledge-provenance` | ✅ 已建 | Act 投影纪律未硬化到创建环节 |
| `grounding-dependency` | ✅ 已建 | 未在创建时强制检查 grounding 来源 |
| CI/hook 门禁 | ✅ `ci-ontology-gate.py` / `install-git-hook.sh` | hook 未默认安装 |

## 目标

建立**创建即防护**的本体预防门禁体系，确保：

1. **任何新本体节点创建时，必须通过 grounding 检查**——有代码/证据来源才能入图
2. **任何新本体节点创建时，fidelity 检查自动生效**——泛化 signal、缺 source、无正反例直接阻断
3. **CI/hook 门禁默认启用**——提交即校验，不依赖人工自觉
4. **Grill 阶段强制事实验证**——可验证的事实不由用户回答，由 agent 自行查找

## 非目标

- 不重新审计存量本体（T0545 已完成）
- 不修改本体格式/结构定义（SSOT v3 已定）
- 不修改 PDCA 元本体结构

## 方案方向

### 1. 创建前置检查（grounding gate）

在 `task_identity.py create` 或 `ontology-check` skill 中增加 grounding 验证步骤：
- 新本体节点必须声明 grounding 来源（代码文件路径 + 行号，或 records/ 证据 ID）
- `scripts/ontology-validate.py` 新增 `--check grounding` 模式，验证 grounding 来源存在性

### 2. 创建即 fidelity 校验

- `ontology-check` skill 被调用时自动运行 `ontology-validate.py --check fidelity`
- 增量提交（含新本体节点的 PR）自动触发 fidelity 校验
- 确认 `pre-commit` hook 已安装且 fidelity 检查在默认配置中

### 3. Grill 事实验证强制

- `skill-grilling.md` 规则 4 强化：Grill 中涉及本体特性的问题，必须由 agent 自行验证代码/证据，不允许向用户猜测
- Grill 记录中必须包含 `verified: true` 标记（通过 `scripts/append-confirmation.py` 验证）

### 4. CI/hook 默认启用

- `scripts/install-git-hook.sh` 默认安装 pre-commit hook
- `.github/workflows/ontology-gate.yml` 确保 fidelity 检查在 CI 中默认启用
- `ci-ontology-gate.py` 增加 `--enforce-fidelity` 标志

## 验收标准

- [ ] AC-1：scripts/ontology-validate.py --check grounding 可执行，验证新本体节点的grounding来源存在性；ontology-check skill调用时自动运行grounding检查
- [ ] AC-2：ontology-check skill调用时自动运行ontology-validate.py --check fidelity；含泛化signal/缺Source的本体被门禁拒绝
- [ ] AC-3：install-git-hook.sh安装后pre-commit包含--enforce-fidelity；ci-ontology-gate.py --enforce-fidelity可执行
- [ ] AC-4：skill-grilling.md规则4增加verified:true要求；append-confirmation.py支持--verified；clarifications.jsonl中Grill记录含verified:true标记
- [ ] AC-5：端到端验证通过——创建测试本体含/不含grounding来源和泛化signal，门禁行为正确，--check all通过

## 约束

- 预防机制必须**不可绕过**——不依赖开发者自觉
- 存量豁免清单（`.fidelity-exempt.json`）继续有效，不影响存量节点
- 所有新增检查须有 `rule_spec` 本体锚定（符合 README §9）
- 不得改变 `ontology-validate.py` 现有 AC-1~AC-6 行为

## 依赖

- 前置任务：T0534（本体保真度治理）、T0545（本体符合度全量审计）已完成
- 本任务产出可被后续本体创建任务消费
