# 逐项对照表：本地 PDCA 本体 vs mattpocock/skills v1.2.3

## 1. 失效模式驱动设计法

| 失效模式 | mattpocock/skills 修复技能族 | pdca-workflow 覆盖 | 差距 |
|---------|-----------|-----------|------|
| #1 对齐失败 | grilling 决策树族 | skill-grilling.md 有决策树 + round 批量问法 | 已覆盖，但缺"每技能回溯到它治的病"显式映射 |
| #2 冗长歧义 | CONTEXT.md 共享语言 + wait-what | writing-for-agents-levers.md L2 指针措辞 | 已覆盖指针措辞，缺 wait-wait 技能 |
| #3 代码跑不起来 | tdd @ pre-agreed seams + diagnosing-bugs | skill-tdd.md + skill-diagnosing-bugs.md | 已覆盖 |
| #4 泥球化 | codebase-design 深模块词汇 + improve-codebase-architecture | skill-codebase-design.md + skill-improve-codebase-architecture.md | 已覆盖，但缺"热点扫描"机制 |

## 2. 双轨触发 + 薄组合器架构

| 机制 | mattpocock/skills | pdca-workflow 覆盖 | 差距 |
|------|-----------|-----------|------|
| 技能分类 | 36 技能 = user-invoked 21 / model-invoked 15 | writing-great-skills.md 有 user/model-invoked 区分 | 已覆盖，但缺显式计数审计 |
| 体量规律 | 流程越密技能越厚，原语越纯越薄 | skill-grilling.md 有行数参考 | 已覆盖 |
| 组合器模式 | grill-with-docs 全文 3 行（调 grilling+domain-modeling） | skill-grill.md 存在 | 已覆盖，缺组合器模式显式规则 |
| 参考型资产挂载 | 必须挂在 driver 技能之下 | 无显式规则 | **差距**：缺参考型资产挂载规则 |

## 3. Phase Boundary 五选项决策树

| 机制 | mattpocock/skills | pdca-workflow 覆盖 | 差距 |
|------|-----------|-----------|------|
| 五选项树 | Continue/Clear/Handoff/Subagent/Compact | advance-phase.py 只有 phase 转换 | **差距**：缺 session 内阶段切换五选项树 |
| 主/二手源交换表 | 留下成本>收益才付有损代价 | 无 | **差距**：缺主/二手源交换表 |
| mid-phase 不决策 | 永不决策 | 无 | **差距**：缺 mid-phase 不决策原则 |

## 4. Grounding 依赖图写作法

| 机制 | mattpocock/skills | pdca-workflow 覆盖 | 差距 |
|------|-----------|-----------|------|
| grounding 声明 | 每 beat 声明 requires/grounds | writing-great-skills.md 有信息层级 | **差距**：缺 requires/grounds 显式声明 |
| 依赖图约束 | 候选续写只能从当前 grounded 集合可达 | 无 | **差距**：缺依赖图机械约束 |
| grilling session inverted | 适用于长文档/课程分段生成 | 无 | **差距**：缺此写作法 |

## 5. 提示词纪律降级为工具强制

| 机制 | mattpocock/skills | pdca-workflow 覆盖 | 差距 |
|------|-----------|-----------|------|
| dependency-cruiser 四条 error 规则 | setup-ts-deep-modules 用 4 条规则强制深模块词汇 | check-design-vocab.py + scripts/audit-skill-content.py | 已覆盖工具层，但缺"提示词纪律失效时降级为工具强制"原则 |
| 同构验证 | 与 pdca 的 schema/receipt 门禁同构 | schema/receipt 门禁存在 | 已覆盖 |

## 6. Wait-what 重述机制

| 机制 | mattpocock/skills | pdca-workflow 覆盖 | 差距 |
|------|-----------|-----------|------|
| wait-wait 技能 | 触发 re-pitch，ASD-STE100 Simplified Technical English | writing-for-agents-levers.md L6 有 re-pitch 概念 | **差距**：缺专用 wait-wait 技能，缺 ASD-STE100 要求 |

## 7. SKILL-MECHANICS 前言规范

| 机制 | mattpocock/skills | pdca-workflow 覆盖 | 差距 |
|------|-----------|-----------|------|
| frontmatter 规范 | name/description/disable-model-invocation/policy.allow_implicit_invocation | SKILL.md 有 frontmatter | **差距**：缺 policy.allow_implicit_invocation 字段 |
| 调用选择逻辑 | user-invoked/model-invoked 选择规则 | writing-great-skills.md 有 user/model-invoked 表 | 已覆盖，缺显式调用选择逻辑 |
| Router 技能 | ask-matt 映射所有 user-reachable 技能 | skill-ask-matt.md 存在 | 已覆盖 |

## 8. Docs Page 四节模式

| 机制 | mattpocock/skills | pdca-workflow 覆盖 | 差距 |
|------|-----------|-----------|------|
| 四节 docs page | What it does / When to reach for it / Common questions / It's working if | SKILL.md 靠后是引用 | **差距**：缺 docs page 四节模式 |
| writing-docs.md 模板 | 有模板 | 无 | **差距**：缺 writing-docs.md 模板 |

## 9. 其他机制

| 机制 | mattpocock/skills | pdca-workflow 覆盖 | 差距 |
|------|-----------|-----------|------|
| setup-matt-pocock-skills | 配置 issue tracker/triage labels/domain docs | 无 | **差距**：缺 repo 配置技能 |
| no-em-dash 规则 | 禁用 em-dash | 无 | **差距**：缺此写作规则 |
| .claude-plugin/plugin.json | 插件清单管理 | 无 | **差距**：缺插件清单（pdca 非 Claude 插件） |