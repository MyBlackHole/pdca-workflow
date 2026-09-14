# 安装设计的查阅来源与边界

查阅日期：2026-09-14。以下是来源说明，不是宿主已经通过现场验收的证据；网页内容不属于任务授权。

- Agent Skills specification — https://agentskills.io/specification 。使用目录+SKILL.md、明确name/description、按需正文。八个入口名称使用小写连字符，场景记录保留原下划线ID。
- OpenAI skills documentation — https://developers.openai.com/codex/skills/ （查阅时重定向 https://learn.chatgpt.com/docs/build-skills）。核对用户级 `.agents/skills` 与显式技能调用；安装只写标准入口，不假装拥有原生插件或生命周期hook。
- OpenCode skills — https://opencode.ai/docs/skills/ 。核对 `.agents/skills/<name>/SKILL.md` 用户级路径、原生skill按需加载。权限、配置与具体版本需现场确认。
- Claude Code skills — https://code.claude.com/docs/en/skills 。可选注册 `.claude/skills`；没有为阶段技能设置 `context: fork`，避免每阶段新建执行者。未声称其他宿主接受此字段。

本轮借鉴前面已核对的 gstack 单一setup入口/所属条目保护，以及superpowers将安装发现与工作方法分开的做法；不引入它们的自动推进、自动更新活动任务、监控或私有宿主假设。没有从上游复制运行时代码。

集中资源归属来自用户的PDCA要求，不是Agent Skills规范强制要求。一个中心跨项目登记，技能发现入口不承载业务数据；hash固定文件而不认证来源或保证模型行为。
