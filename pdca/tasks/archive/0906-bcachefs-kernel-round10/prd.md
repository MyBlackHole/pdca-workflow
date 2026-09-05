# bcachefs 内核第十轮纵深与本体优化

## 背景
T0488-T0497 后已建 43 个 core 节点。本次双轨：落选备选三项（str_hash/ACL 短路/读提升分层）+ 全扫三轮复核。

## 目标
深挖两轨；新增至少 2 个不重复 domain 节点；优化项分析后经用户确认（单向关联原则）。

## 功能需求
1. 两轨并行深挖，每条带 file:line 佐证，且论证确为 43 节点未覆盖
2. 新增至少 2 个 domain 节点，specializes ontology:domain/core
3. 优化清单分析后请用户确认，关联单向无环
4. 全量 ontology-validate.py 0 issues

## 非功能需求
- 只读分析；真实时间戳；只增修 .md

## 验收标准
- [ ] AC-1 两轨条目确为遗漏，每条有代码佐证
- [ ] AC-2 新增至少 2 个不重复 domain 节点且 frontmatter 合法
- [ ] AC-3 优化项逐条落实，关联单向无环，有据可查
- [ ] AC-4 validate 全量 0 issues，信号非泛化，引用无空悬

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-*.md（新增与改动节点）

## 风险与对策
- 风险：三轮复核找不出足量。对策：如实报告，不足即收缩 AC-2（经用户确认）
- 风险：重复已建主题。对策：prompt 附 43 节点清单，动笔前比对
