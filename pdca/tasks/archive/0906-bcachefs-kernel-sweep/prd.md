# bcachefs 内核遗漏扫描与本体优化

## 背景
T0488（12 子系统概览）+ T0490（数据面/可观测/用户态）后，内核仍有未深挖处（btree 深入/journal 深入/alloc 深入/sb/snapshots/vfs/压缩加密/closure-six 深入）。本次全范围遗漏扫描并产出本体。

## 目标
内核全范围扫遗漏巧思（含 btree 深入）；新增至少 3 个不重复 domain 节点；优化项分析后经用户确认再执行（单向关联原则）。

## 功能需求
1. 分片并行扫描内核各子系统遗漏点，每条带 file:line 佐证
2. 新增至少 3 个 domain 节点，specializes ontology:domain/core
3. 优化清单分析后请用户确认，关联必须单向无环
4. 全量 ontology-validate.py 0 issues

## 非功能需求
- 只读分析 bcachefs-tools；本体只增修 .md
- 不碰 T0490 已定结论；时间戳用真实时间（T0490 教训）

## 验收标准
- [ ] AC-1 遗漏扫描覆盖内核各子系统，每条有代码位置佐证
- [ ] AC-2 新增至少 3 个不重复 domain 节点且 frontmatter 合法
- [ ] AC-3 优化项逐条落实，关联单向无环，有据可查
- [ ] AC-4 validate 全量 0 issues，信号非泛化，引用无空悬

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-*.md（新增与改动节点）

## 风险与对策
- 风险：与现有 40+ core-* 节点重复。对策：动笔前 Read 比对
- 风险：双向关联成环。对策：只做单向关联（T0490 教训）
- 风险：时间戳门禁。对策：全部用真实时间（T0490 教训）
