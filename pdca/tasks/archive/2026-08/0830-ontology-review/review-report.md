# 本体融入与知识正确性审查报告

**任务**: T0425 审查本体融入缺口与本体知识正确性
**审查日期**: 2026-08-30
**审查范围**: `ontology/domain/`, `ontology/concept/`, `ontology/entity/`, `ontology/fact/`, `ontology/pattern/`, `ontology/principle/`, `ontology/pitfall/`, `ontology/decision/`, `ontology/process/`

## 审查范围

- 全部本体节点 frontmatter 合法性
- 关系引用完整性（无空悬）
- 本体图连通性（islands=0）
- `knowledge/` 残留引用清理状态
- manifest 索引完整性
- SSOT v3 与实际节点一致性
- T0399 / T0403 进度影响

## 审查方法

1. `ontology-validate.py` 全量校验
2. `ontology_graph.py --format summary` 图连通性检查
3. `knowledge/` 残留引用 grep 扫描
4. frontmatter 结构化检查（type==目录名, id 存在性）
5. manifest.jsonl 覆盖度检查

## 标准轴发现

| # | 严重度 | 类别 | 描述 | 建议修复 |
|---|--------|------|------|----------|
| F-1 | major | 迁移残留 | 43 个本体文件含 `knowledge/` 路径引用（历史迁移标记），`knowledge/` 目录已删除但引用未清理 | 替换为 `ontology/domain/` 路径或改为纯描述性"已迁移"注释 |
| F-2 | major | 索引缺失 | `ontology/manifest.jsonl` 不存在，manifest 索引未按 T0403 计划重建 | 执行 T0403 重建 manifest.jsonl，派生 `ontology_type`/`specializes`/`domain` 等索引字段 |
| F-3 | major | 任务依赖 | T0399（知识表达按本体论重构）仍处于 `do` 阶段，未完成 | 推进 T0399 至 check→act→archive |
| F-4 | major | 任务依赖 | T0403（全量迁移其余域与 manifest 索引重写）仍处于 `plan` 阶段 | 推进 T0403 至 do→check→act→archive |
| F-5 | minor | 文档一致性 | `knowledge/` 迁移后，部分领域实体的「子主题」列表未回填 | 后续维护 `ontology/domain/out-of-scope.md` 等域根节点的子主题列表 |
| F-6 | minor | 引用清理 | `ontology/domain/out-of-scope.md` 根节点的「子主题」列表未自动回填 | 由 T0424 后续任务选择性维护 |

## 规范轴发现

| # | 严重度 | 类别 | 描述 | 建议修复 |
|---|--------|------|------|----------|
| S-1 | minor | 校验覆盖 | `ontology-validate.py` 未校验 `knowledge/` 残留引用的清理状态 | 在校验器中添加 `KNOWLEDGE_REF_CLEANUP` 规则 |
| S-2 | minor | 属性覆盖 | 部分 KnowledgeArtifact 实例可能缺少结构化 `attributes`（applicability/constraints/testable_signal） | 按 SSOT v3 §6 AC-5/AC-6 补充 |
| S-3 | minor | 关系丰富度 | 部分 KnowledgeArtifact 可能缺少 `guides` 或 `relates_to` | 按 SSOT v3 §6 AC-5 补充 |

## 风险评级

- **Critical**: 无
- **Major**: F-1, F-2, F-3, F-4（需推进 T0399/T0403）
- **Minor**: F-5, F-6, S-1, S-2, S-3

## 建议

1. 优先推进 T0399 至完成（act→archive）
2. 推进 T0403 至 do→check→act→archive（manifest 索引重建）
3. 清理 `knowledge/` 残留引用
4. 补充 KnowledgeArtifact 的结构化 attributes 和关系
5. 在 `ontology-validate.py` 中添加 `knowledge/` 引用清理校验规则

## 结论

本体图结构健康（239 nodes, 489 edges, 0 islands），frontmatter 合法性通过，无悬空引用。但本体融入尚未闭环：T0399 和 T0403 仍在进行中，`knowledge/` 残留引用和 manifest 索引缺失是主要缺口。