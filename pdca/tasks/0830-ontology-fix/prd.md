# 清理本体 knowledge/ 残留引用并重建 manifest 索引

## 背景
T0425 审查发现本体融入存在以下缺口：
- 43 个本体文件含 `knowledge/` 残留引用（历史迁移标记）
- `ontology/manifest.jsonl` 缺失，未按 T0403 计划重建
- T0399 仍处于 `do` 阶段，T0403 仍在 `plan` 阶段

本任务修复这些问题，完成本体融入闭环。

## 目标
1. 清理所有本体文件中的 `knowledge/` 残留引用
2. 重建 `ontology/manifest.jsonl`
3. 推进 T0399 至完成
4. 推进 T0403 至完成

## 验收标准
- [ ] AC-1：所有本体文件不再含 `knowledge/` 路径引用（改为 `ontology/domain/` 或描述性注释）
- [ ] AC-2：`ontology/manifest.jsonl` 重建，包含 `ontology_type`/`specializes`/`domain`/`entity_refs`/`attributes` 索引字段
- [ ] AC-3：`ontology-validate.py` 通过（含新增 `KNOWLEDGE_REF_CLEANUP` 规则）
- [ ] AC-4：ontology_graph 无新增孤岛
- [ ] AC-5：`tests/test_ontology_validate.py` 通过
- [ ] AC-6：登记证据 + 收敛映射 valid:true

## 关联本体节点
```
ontology:concept/pdca-task
ontology:domain/out-of-scope
```

## 非目标
- 不改动本体节点内容（除引用路径更新外）
- 不重新迁移知识

## 设计要点
- `knowledge/` 引用替换策略：历史迁移标记改为 `ontology/domain/` 路径或纯描述性注释
- manifest.jsonl 重建：从 `ontology/domain/*.md` 和 `ontology/concept/*.md` 等目录派生
- 校验器新增规则：扫描本体文件内容，检测到 `knowledge/` 字符串即报错