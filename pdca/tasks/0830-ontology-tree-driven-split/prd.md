# T0416 本体关系树驱动任务拆分（to-tickets WBS 生成）

- 任务 ID：T0416
- 依赖：T0415（本体下沉到任务表达层，已完成）
- 场景类型：development

## 背景与问题

T0415 让 `to-tickets` 具备了本体重名检查与 `ontology_fragment`/`ontology_node_type` 字段继承，但拆分逻辑仍由 PRD 章节**人工划分**，本体仅起"防重名"作用，未兑现 `ontology/README.md` §1 承诺的"特殊化/组合关系树自底向上驱动 WBS 拆分，每个实体实现可独立收敛"。

具体缺口：
1. 拆分边界与本体 `composed_of` 关系树脱节——PRD 章节与本体实体无结构对应。
2. 子任务的 `ontology_node_type` 仍需人工在 `task_identity.py` 创建时显式传入（T0415 仅做了透传+继承，未自动推导）。

## Seam 分析

### 测试接缝
- `scripts/ontology-tree-split.py`：关系树解析 + PRD 映射校验 + WBS 候选生成。
- `skills/to-tickets/SKILL.md`：集成调用（顾问式，输出候选不落盘）。

### 声明的测试接缝
- seam: tests/test_ontology_tree_split.py -> scripts/ontology-tree-split.py
- seam: tests/test_to_tickets_tree_split.py -> skills/to-tickets/SKILL.md

## 设计概览

### Part 1 关系树解析器 `scripts/ontology-tree-split.py`
- 读取父任务 `meta.ontology_fragment` 指向的本体目录，构建实体关系图：
  - `specializes` 形成类型树（is-a 层级）；
  - `composed_of` 形成组合树（整体-部分）。
- 解析 PRD `## 拆分映射` 机器可读小节：每行 `- <PRD 章节标题> -> ontology:<node-id>`，声明章节对应本体节点。
- 校验：映射节点须存在于本体图；被映射节点若在 `composed_of` 中作为父（即被其他节点 `composed_of`），则其直接子实体节点即子任务候选。
- 输出候选 WBS（JSON）：每个子实体 → 子任务候选（`slug` 派生自 node id、`title` 来自节点 summary、`ontology_node_type` = 节点 `type`、`dependencies` 按 `composed_of` 父子/层序推导为直接前置）。

### Part 2 to-tickets 集成（顾问式）
- 拆解时若 PRD 含 `## 拆分映射` 且父任务有 `ontology_fragment`，则调用 `ontology-tree-split.py` 生成候选子任务清单（proposal）打印供确认；**不自动落盘**（保持 P6 终审前不调度）。
- 确认后由调用方经 `task_identity.py` 逐个创建（node_type/依赖已自动推导，无需人工传参）。
- 未声明 `## 拆分映射` 时保持原有行为（章节人工划分 + 重名提示 + 字段继承），不强制。

### Part 3 PRD 模板与 Plan 提示
- `templates/to-spec/SPEC.md` 新增可选 `## 拆分映射` 小节。
- `flows/flow-plan/SKILL.md` P4 提示：若任务含 `ontology_fragment`，可在 PRD 声明拆分映射以启用关系树驱动拆分。

### Part 4 测试
- `tests/test_ontology_tree_split.py`：树解析、`composed_of`/`specializes` 成环与缺失节点报错、WBS 候选生成（node_type/依赖正确）。
- `tests/test_to_tickets_tree_split.py`：声明映射时触发候选生成、未声明时原行为不变。

## 验收标准

- [ ] AC-1（关系树解析）：`ontology-tree-split.py` 读取本体目录构建 specializes/composed_of 图，解析 PRD 拆分映射，输出候选子任务（含 `ontology_node_type` 与依赖边）。
- [ ] AC-2（校验）：映射节点不存在、`composed_of` 循环、`specializes` 成环时给出明确错误且不生成错误骨架。
- [ ] AC-3（集成顾问式）：to-tickets 在声明拆分映射时调用并输出候选（不自动落盘）；未声明则原行为不变。
- [ ] AC-4（模板+测试）：SPEC.md 含 `## 拆分映射` 小节、flow-plan 提示；新增测试覆盖解析/校验/生成。

## 非目标

- 不强制所有拆分走关系树；保持顾问式，避免 YAGNI。
- 不改 `compute-frontier.py` DAG 语义（依赖边仍由其校验）。
- 不自动推断 PRD 章节↔本体节点对应（映射由作者显式声明，避免误对齐）。

## 风险与缓解

- 误对齐：映射显式声明，工具不猜测章节↔节点对应。
- 循环：解析器拒绝成环图并报错。
- 破坏既有 to-tickets 调用：新映射小节可选，默认行为不变，测试覆盖默认路径。

## 关联本体节点

ontology:concept/pdca-task
ontology:concept/ontology-asset
ontology:concept/entity
