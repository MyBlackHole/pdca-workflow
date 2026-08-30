# 审查本体融入缺口与本体知识正确性

## 背景
T0399（知识表达按本体论重构）完成了知识库从 topic 到 ontology 的迁移，建立了本体校验（ontology-validate.py）和 SSOT v3。但 T0399 仍处于 `do` 阶段，T0403（全量迁移其余域与 manifest 索引重写）尚在 `plan`，本体融入尚未闭环。需要系统审查：
1. 本体融入还差哪些未完成项；
2. 已迁移的本体知识是否正确（frontmatter、关系、属性、引用）。

## 目标
审查本体图（ontology/domain/* + ontology/concept/* 等）的完整性与正确性，识别融入缺口和知识错误，输出问题清单与修复计划。

## 验收标准
- [ ] AC-1：列出所有本体融入缺口（如未迁移域、缺失节点、悬空引用、残留 knowledge/ 引用等）
- [ ] AC-2：验证所有本体节点 frontmatter 合法性（type==目录名、id 合法、layer/specializes/domain 正确）
- [ ] AC-3：验证所有关系引用非空悬（specializes/composed_of/relates_to 目标均存在）
- [ ] AC-4：验证 ontology-validate 通过（nodes 不降、islands=0、无 AC 违规）
- [ ] AC-5：审查 SSOT v3 与实际节点的一致性（旧 taxonomy 产物是否标注"已被 v3 取代"）
- [ ] AC-6：登记问题清单（按严重度分级），通过本体校验

## 关联本体节点
```
ontology:concept/pdca-task
ontology:domain/out-of-scope
```

## 范围
- 审查 `ontology/domain/`、`ontology/concept/`、`ontology/entity/`、`ontology/fact/`、`ontology/pattern/`、`ontology/principle/`、`ontology/pitfall/`、`ontology/decision/`、`ontology/process/` 下所有节点
- 审查 `ontology-validate.py` 校验逻辑是否覆盖 SSOT v3 全部规则
- 不改动本体节点内容（仅审查，问题清单作为 Do 阶段输出）

## 非目标
- 不直接修复本体节点（修复由后续任务执行）
- 不重新迁移知识

## 设计要点
- 审查方法：`ontology-validate.py --all` + 人工抽样 + 关系图遍历
- 问题清单格式：严重度（critical/major/minor）+ 类别（frontmatter/relations/references/coverage）+ 描述 + 建议修复