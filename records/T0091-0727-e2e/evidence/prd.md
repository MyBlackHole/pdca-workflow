# 技能索引生成

## 问题陈述
28 个技能文件分散在 `skills/` 目录下，没有统一的查阅入口。新用户或 AI 无法快速了解可用技能的名称、类型、行数、引用关系。

## 解决方案
在项目根目录生成 `SKILLS-INDEX.md`，包含每个技能的元数据表。

## 用户故事
作为 PDCA 用户，我希望查看 SFILE-INDEX.md 能一目了然看到全部技能的名称、类型（user-invoked / model-invoked）、行数、引用者和摘要。

## 实现决策
- 用 bash 脚本提取 YAML front matter（name, description, disable-model-invocation）
- 用 `wc -l` 统计行数
- 用 `grep -c` 统计外部引用次数
- 输出为 Markdown 表格

## 测试决策
- 生成的 SKILLS-INDEX.md 应包含所有 skills/*/SKILL.md 条目
- user-invoked 技能应有 disable-model-invocation 标记
- 表格应包含：名称、类型、行数、引用数、摘要

## 范围外
- 不修改技能文件本身