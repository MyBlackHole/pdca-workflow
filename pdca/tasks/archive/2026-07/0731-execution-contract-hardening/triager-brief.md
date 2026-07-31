# T0161 Triage Brief

## 分类

- 分类：enhancement
- 场景：development
- 来源：对 `mattpocock/skills` 当前实现方式的比较，以及用户确认继续优化。

## 已验证事实

- `flows/flow-do/SKILL.md` 的 development 路径先执行 A2 编码，再执行 A3 TDD；bugfix 路径同样先 B2 修复，再 B3 回归测试，未将测试优先顺序作为可验证约束。
- `skills/tdd/SKILL.md` 已定义预先约定 Seam 和红绿循环，但没有由 flow 的机器可读合约强制其在实现前发生。
- `scripts/generate-skills-index.py` 仅从 frontmatter 生成调用类型展示；当前没有声明或校验 skill-to-skill 调用边的结构化合约。
- `skills/ask-matt/SKILL.md` 映射到 `/grill-me`，但仓库只存在 `grill` 与 `grilling` 两个相关技能目录。
- `pdca/ai-friendliness-route-contract.json` 和 resolver 已能验证场景到 flow 路径，但范围不包括上述两类关系。

## 查重

- 已归档的 T0160 加固了场景路由、生命周期夹具与内容预算；它不覆盖执行循环顺序或技能调用图。
- 搜索 active、archive、knowledge、docs、skills 与 flows，未发现处理该范围的任务。

## 推荐范围

1. 定义 development/bugfix 的测试优先执行合约、最小验证回执和确定性夹具。
2. 定义技能调用图、入口别名与调用权限校验，并修复已证实的失效入口。
3. 保持零模型、零网络、零第三方运行时新增依赖。

## 信息缺口

- 需要用户决定是否禁止 flow 直接调用 manual skill；这决定是否需要将现有 manual skill 拆成薄壳与 automatic worker。
- 需要用户决定回执粒度，以平衡可验证性与每轮 TDD 的记录成本。
