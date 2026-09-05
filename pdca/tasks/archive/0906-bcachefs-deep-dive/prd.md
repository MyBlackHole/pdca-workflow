# bcachefs 纵深分析与本体优化

## 背景
T0488 覆盖 12 子系统但 EC 深入/可观测/用户态工具未充分挖掘；T0489 建 5 节点后仍有缺口。本次纵深分析三大方向并产出新节点 + 优化已有节点。

## 目标
深挖 EC 与数据路径、可观测与调试体系、用户态工具三个方向；新增至少 3 个不重复 domain 节点；优化项分析后定并逐条落实。

## 功能需求
1. 三方向并行深挖，每条结论带 file:line 代码佐证
2. 新增至少 3 个 domain 节点，specializes ontology:domain/core，与现有节点不重复
3. 优化已有 core-* 节点（候选分析后定，如补强 testable_signal、补边界说明）
4. 全量 ontology-validate.py 0 issues

## 非功能需求
- 只读分析 bcachefs-tools；本体只增修 .md，不动脚本与流程
- 优化已有节点时保留原 id 与 specializes 不变，只增补内容

## 验收标准
- [ ] AC-1 新分析覆盖三方向，每条有代码位置佐证
- [ ] AC-2 新增至少 3 个不重复 domain 节点且 frontmatter 合法
- [ ] AC-3 优化项逐条落实且有依据（代码或既有结论），优化前后可 diff 说明
- [ ] AC-4 validate 全量 0 issues，新增/改动信号非泛化，引用无空悬

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-*.md（新增与改动节点）

## 风险与对策
- 风险：与现有节点重复。对策：动笔前 Read 比对，relates_to 显式关联
- 风险：优化破坏历史结论。对策：只增补不改原语义，diff 可审
