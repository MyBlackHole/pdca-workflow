# bcachefs 内核第四轮纵深与本体优化

## 背景
T0488/T0490/T0491 后剩余：候选未建三项（EC 修复状态机、journal 空间记账、快照删除执行）与并发原语深入（closure/six/btree_gc/interior）。本次全做。

## 目标
深挖两方向；新增至少 3 个不重复 domain 节点；优化项分析后经用户确认（单向关联原则）。

## 功能需求
1. 两方向并行深挖，每条带 file:line 佐证，避开已建 15 节点主题
2. 新增至少 3 个 domain 节点，specializes ontology:domain/core
3. 优化清单分析后请用户确认，关联单向无环
4. 全量 ontology-validate.py 0 issues

## 非功能需求
- 只读分析；真实时间戳；只增修 .md

## 验收标准
- [ ] AC-1 两方向深挖每条有代码位置佐证
- [ ] AC-2 新增至少 3 个不重复 domain 节点且 frontmatter 合法
- [ ] AC-3 优化项逐条落实，关联单向无环，有据可查
- [ ] AC-4 validate 全量 0 issues，信号非泛化，引用无空悬

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-*.md（新增与改动节点）

## 风险与对策
- 风险：与 20 个已建节点重复。对策：prompt 明确排除主题，动笔前比对
- 风险：双向关联成环。对策：单向原则（T0490 教训）
