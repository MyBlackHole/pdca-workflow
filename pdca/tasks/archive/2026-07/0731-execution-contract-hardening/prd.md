# AI 执行循环与技能调用合约加固

## 问题陈述

- **现状**：`flow-do` 的 development 与 bugfix 路径均将编码/修复文字置于 TDD 之后。`tdd` 已说明 Red-Green 与 Seam，但没有机器可读的顺序 oracle。技能的 `invocation: manual` 仅由文档约定；flow 与 automatic skill 仍可直接引用 manual skill，`ask-matt` 还暴露了不存在的 `/grill-me` 入口。
- **目标**：将 test-first 执行顺序、最小验证回执语义、入口别名和调用权限转化为可解析、可验证、可故障注入的仓库合约，降低 AI 对文档顺序和技能名称的猜测。
- **差距**：T0160 的 route contract 只解决 `scenario_type -> Do 路径`，`SKILLS-INDEX` 只展示调用类型；两者都不能验证开发循环顺序或 skill-to-skill/flow-to-skill 调用边。

## 解决方案

新增两个职责分离的版本化 JSON contract、schema、公共 resolver 和文档一致性检查：

1. **AI execution contract**：仅覆盖 `development` 与 `bugfix`，声明 test-first 循环的有序阶段、每个完成切片的定向验证语义、最终全量验证和审查语义。
2. **Skill invocation contract**：以现有 SKILL frontmatter 的 `name` 和 `invocation` 为类型单一事实源，单独声明用户入口别名和允许调用边；禁止 flow 或 automatic asset 指向 manual skill。

两个 contract 都使用真实 resolver、受控临时根目录和故障注入验证，保留现有 route/lifecycle fixture。此任务不新增外部项目运行时、网络调用、第三方依赖，也不修改所有任务的 Do-to-Check phase gate。

## Seam 分析

### 测试接缝

- **公共 CLI seam**：新的 resolver 必须通过命令行消费 contract，不由测试重写业务判断。
- **文档 seam**：resolver 使用真实 `flow-do`、flow 和 skill 文档中的锚点或显式 skill 路径验证 contract 与人类说明一致。
- **调用类型 seam**：frontmatter 解析结果与 invocation contract 独立读取并交叉比较，防止 JSON 复制调用类型后悄然漂移。
- **故障注入 seam**：在最小临时仓库中交换顺序、删除实际被引用文件、制造别名/边漂移，断言稳定错误码。

### 验收可测性

- 每个 resolver 的正常输出和失败输出均为稳定 JSON payload，包含 status、code 和 path。
- 夹具必须证明“标题仍在但顺序/调用边错误”会失败，不能只检查 Markdown 是否含有关键字。
- 文档中的每一条显式 `$PDCA_HOME/skills/<name>/SKILL.md` 调用必须能映射到一个已声明、类型合法的 contract edge。
- 内容 baseline、skills index、doctor 与全量单元测试共同验证不会以更新文档或预算掩盖行为回归。

## 用户故事

1. 作为执行 development/bugfix 的 AI，我能从公共 resolver 获得 test-first 的有序动作和最小回执语义，而不是仅从自然语言段落推测顺序。
2. 作为维护者，我能在 flow 的实际调用边指向 manual skill、未知 skill、错误别名或文档漂移时获得稳定失败，而不是在会话中才发现。
3. 作为用户，我仍可通过已有 manual 入口调用 triage、grill、domain-modeling 和 handoff；内部 flow 则自动调用对应 worker，不改变用户签审位置。
4. 作为评测者，我能用固定 fixture 证明两个新 contract 的正常路径和关键反例，不把结果外推为真实 LLM 成功率。

## 实现决策

- 新增 `pdca/ai-execution-contract.json`、对应 schema 和 resolver；它不扩展既有 route contract，避免把“选择哪条路径”和“路径内如何执行”混成一个事实源。
- execution contract 仅列出 `development` 与 `bugfix`，按每个场景声明 route 锚点、test-first 阶段顺序和 `slice`/`final` 回执策略。resolver 支持按 scenario 查询与实际文档校验。
- 重写 flow A/B 的文档顺序为：约定 Seam/失败测试、最小实现或修复、完成切片的定向验证、最终全量验证、双轴审查。A/B 可保留原有步骤编号以避免 T0160 route contract 迁移，但不得再把编码/修复置于 TDD 之前。
- 新增 `pdca/skill-invocation-contract.json`、对应 schema 和 resolver。contract 只保存 alias 与边；asset 名称和 invocation 类型由现有 frontmatter 读取，不复制。
- 调用规则：flow 与 automatic asset 只能调用 automatic asset；manual asset 可作为用户入口并只指向 automatic asset。resolver 验证所有显式 skill 路径引用都已声明且类型合法，别名只解析到现有 manual entry。
- 将目前被 flow/automatic asset 直接引用的 manual 实现拆为 `triage-work`、`domain-modeling-work`、`handoff-work` 等 automatic worker；原 manual 名称保留为薄壳入口。同步替换 wayfinding 与 grill 的 manual 内部引用。
- 修正 `ask-matt` 的入口别名为 contract 中真实存在的 `/grill`，不保留 `/grill-me` 兼容别名。
- 不给 task schema、transition gate 或外部项目 task 强制新增回执字段。本轮的回执是 execution contract 对 flow 行为的语义约束和 fixture 断言；真实 runner 出现前不伪造逐轮运行数据。

## 测试决策

- 在现有 AI-friendliness 单元测试与公共 fixture harness 上扩展，不建立平行测试框架。
- execution contract 覆盖 development/bugfix 正常解析、非法 scenario、缺失实际文档、缺失锚点、阶段顺序漂移和 route/步骤不一致。
- invocation contract 覆盖正常 alias/edge 解析、未知 asset、未知或重复 alias、automatic-to-manual 非法边、未声明显式引用、文档引用漂移和 frontmatter invocation 漂移。
- 对临时根目录进行故障注入，并确保 fixture 调用公共 resolver 而非测试内部复制判断。
- 更新 `SKILLS-INDEX.md`、逐资产 bytes baseline 和 `audit-skill-content.py` 的确定性检查接入；完整测试包含 fixture、budget、doctor、索引和 Python compile。

## 验收标准

- [ ] AC-1：`ai-execution-contract` schema 只接受 versioned、路径安全且完整的 development/bugfix 执行定义，并拒绝重复、未知或顺序不完整的阶段。
- [ ] AC-2：公共 execution resolver 能稳定解析 development/bugfix 的有序循环和 slice/final 回执语义，并为非法 scenario 返回稳定错误码。
- [ ] AC-3：execution resolver 的文档验证读取实际 `flow-do`，拒绝缺失引用、缺失锚点或保持标题但交换 test-first 顺序的漂移。
- [ ] AC-4：`flow-do` 的 A/B 路径在编码/修复前明确安排 Seam 与失败测试，并在完成切片后要求定向验证、结束时要求全量验证和双轴审查。
- [ ] AC-5：新增 `skill-invocation-contract` schema 与 resolver，frontmatter 保持 name/invocation 类型的唯一来源，contract 不复制该类型。
- [ ] AC-6：调用 resolver 只允许 flow/automatic -> automatic 和 manual -> automatic 边，拒绝未知 asset、自动调用 manual、重复/未知 alias 与未声明边。
- [ ] AC-7：resolver 对 flow/skill 文档中的每个显式 skill 路径调用执行实际引用校验，且文档漂移产生稳定错误码。
- [ ] AC-8：所有现有 flow 和 automatic skill 不再直接引用 manual skill；必要的 triage、domain-modeling 与 handoff 行为通过 automatic worker 执行，manual 入口保留为薄壳。
- [ ] AC-9：`ask-matt` 仅展示 contract 中存在的 manual 入口，`/grill-me` 不再出现，`/grill` 可解析。
- [ ] AC-10：公共 fixture harness 对两个 contract 的正常路径和关键故障注入均调用实际 resolver；既有 route 与生命周期 fixture 保持通过且可重复。
- [ ] AC-11：单元测试覆盖 contract/schema/resolver 的正常和失败分支；`SKILLS-INDEX.md`、逐资产 bytes baseline 和内容审计同步更新并通过。
- [ ] AC-12：全量 unittest、AI-friendliness fixture、内容预算、skills index、doctor 和 Python compile 通过；新增运行时依赖、网络调用和全局 phase-gate 变更均为零。

## 范围外

- 子任务 blocker/DAG、ready frontier 调度和 tracker 发布。
- 外部项目 build/test/typecheck 画像或 setup 向导。
- GitHub/Linear 等平台绑定。
- 真实模型成功率、token、延迟、成本或多 Agent runner 对照实验。
- 对非显式自然语言技能提及进行启发式语义解析。

## 备注

该任务提升的是流程合约的可判定性、导航正确性和故障可诊断性。它不构成对真实 LLM 任务成功率的因果声明；该结论需要固定 runner、保留任务集和前后配对实验。

---

*术语表见 `pdca/CONTEXT.md`，相关架构决策见 `docs/adr/`。*
