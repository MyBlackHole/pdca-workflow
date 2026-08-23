# Triage Brief — 0823-skills-ai-enhancement

- **category**: enhancement
- **scenario_type**: research
- **summary**: 深度分析 skills 项目如何提升 AI 能力
- **current behavior**: skills 项目作为 Matt Pocock 的 AI 工程技能集合，其提升 AI 的机制分散在各 SKILL.md 与 README 四大失效模式叙述中，缺乏系统性中文深度分析
- **desired behavior**: 产出结构化研究报告，量化扫描全量 skill、映射失效模式、拆解核心机制、推演主流程、提炼可迁移原则并给出在 pdca-workflow 的落地建议
- **key interfaces**: skill 指令模块、grilling 追问机制、domain-modeling 共享语言、tdd 测试驱动、codebase-design 深模块设计、wayfinder 决策地图
- **acceptance criteria**: 运行 cat records/T0370-0823-skills-ai-enhancement/report.md 得到包含 6 项 AC 覆盖的完整报告；运行 cat pdca/tasks/0823-skills-ai-enhancement/evidence.jsonl 得到已登记的 evidence 记录
- **out of scope**: 不修改 skills 或 pdca-workflow 代码；不执行真实安装验证；不产出可执行脚本
- **information gaps**: 无，skills 项目文件已可静态读取
- **dedup results**: 检索 pdca/tasks/**/task.json 与 knowledge，未发现同主题深度分析任务
- **recommended next steps**: 按 research 路径执行：全量扫描→失效模式映射→核心技能拆解→流程推演→原则提炼→报告撰写→证据登记
