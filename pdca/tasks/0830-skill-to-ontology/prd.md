# 删除 skills 目录，skill 知识转到本体表达

## 问题陈述

`skills/` 目录存放 41 个 SKILL.md 文件，与 `ontology/domain/` 和 `ontology/concept/` 存在大量语义重叠。Skill 本质是知识的可执行表达，应统一到本体中，消除双源维护成本。参照 T0423（knowledge/ → ontology/domain/）和 T0429（flows/ → ontology/process/）的迁移模式，将 skill 知识迁入本体，删除 `skills/` 目录。

## 解决方案

### 阶段一：创建本体域节点（41 个 skill → ontology/domain/skill-<name>.md）

将每个 `skills/<name>/SKILL.md` 的知识内容（name、description、invocation、relations、正文）迁移为 `ontology/domain/skill-<name>.md` 节点，frontmatter 使用 `pdca.asset/v1` schema，`type: domain`，`specializes: ontology:concept/pdca-task`。

### 阶段二：更新引用

- `scripts/resolve-skill-invocation.py`：SKILL_REFERENCE_RE 和 read_asset 改为读取 `ontology/domain/`
- `scripts/generate-skills-index.py`：从 `ontology/domain/` 读取
- `scripts/check-skill-structure.py`：改为检查 `ontology/domain/`
- `scripts/run-ai-friendliness-fixtures.py`：更新 paths
- `AGENTS.md`：更新所有 `$PDCA_HOME/skills/` 引用
- `SKILLS-INDEX.md`：由 generate-skills-index.py 重新生成
- `scripts/ontology-check`：更新引用
- 测试文件：更新 `skills/` 路径引用

### 阶段三：删除 `skills/` 目录

确认所有引用已更新后，删除 `skills/` 目录及其全部 41 个子目录。

## 验收标准

- [ ] AC-1：41 个 `ontology/domain/skill-*.md` 节点均已创建，frontmatter 合法
- [ ] AC-2：`ontology-validate` 通过
- [ ] AC-3：`ontology_graph --format summary` 无孤岛节点
- [ ] AC-4：`skills/` 目录已删除
- [ ] AC-5：`scripts/resolve-skill-invocation.py` 从 `ontology/domain/` 读取
- [ ] AC-6：`scripts/generate-skills-index.py` 从 `ontology/domain/` 读取
- [ ] AC-7：`scripts/check-skill-structure.py` 从 `ontology/domain/` 读取
- [ ] AC-8：`AGENTS.md` 无 `$PDCA_HOME/skills/` 残留引用
- [ ] AC-9：所有测试文件引用已更新，`python3 -m pytest tests/` 通过
- [ ] AC-10：`scripts/run-ai-friendliness-fixtures.py` 无 `skills/` 残留路径

## 关联本体节点

```
ontology:domain/skill-*
ontology:domain/skills
```

## 范围外

- 不改变 skill 的语义内容
- 不引入新的受控类型词汇
- 不修改 flow 目录

## 依赖

- T0423（knowledge/ → ontology/domain/）迁移模式
- T0429（flows/ → ontology/process/）迁移模式
- T0432（AI 提效缺口补齐）已添加的 writing-for-agents 概念