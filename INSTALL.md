# 安装与更新

## 首次安装

需要 Git，以及用于下面下载命令的 curl 和 Bash。执行下面的一条命令会把 Git 工作副本克隆到
`~/.agents/pdca`，并创建 `~/.agents/skills -> ~/.agents/pdca/skills`
的发现链接：

```bash
curl -fsSL https://raw.githubusercontent.com/MyBlackHole/pdca-workflow/main/install.sh | bash
```

仓库根的 [install.sh](install.sh) 检查路径、克隆仓库并创建发现链接，不写入业务项目、创建项目绑定、复制安装文件、注册后台服务或更新已有工作副本。

若 `~/.agents/pdca` 已存在，安装器会拒绝执行，绝不覆盖或合并其中内容。若
`~/.agents/skills` 已存在（无论是目录还是符号链接），它同样会拒绝执行，绝不
替换或合并发现路径。请先人工核对现有内容；安装器不会清理冲突路径。

克隆前，安装器先创建并取得本次新的集中目录；创建失败立即停止，不进入清理。克隆失败时，清理本次新建目录并保留 Git 的失败状态，不创建发现链接，也不清理相邻内容。已有集中库包含记录或知识时不能为重装而删除它。

安装完成后，按宿主能力重启或显式重载 Skill，再在新会话中调用 `$pdca`。九个入口见 [Skill 索引](skills/README.md)，绑定与使用见 [README](README.md)。链接存在不等于宿主已经发现或完成交互验收；现场检查仍见 [host-acceptance](tests/host-acceptance.md)。

## 更新

集中根是普通 Git 工作副本。需要更新时由用户自行运行：

```bash
git -C "$HOME/.agents/pdca" pull
```

Git 冲突和本地未提交更改由用户处理。更新后按宿主能力重启或显式重载 Skill。
安装器没有更新、卸载或强制覆盖模式。

`records/` 与 `ontology/projects/` 是可审阅、可提交的 Git 数据；更新前先检查本地修改与提交策略。AI 对记录的写入授权不包含 Git 提交或更新授权。活动任务按原绑定、Git 来源与原批准恢复，规则冲突或原依据缺失时停止；更新不自动搬迁旧记录或切换历史提交。

## 卸载发现入口

先通过 `ls -ld "$HOME/.agents/skills"` 与 `readlink "$HOME/.agents/skills"` 核对发现路径确为指向 `~/.agents/pdca/skills` 的符号链接。确认后，用户可执行 `unlink "$HOME/.agents/skills"`，再按宿主能力重启或显式重载。若发现路径是其他目录或链接，停止并核对归属。

移除发现链接保留整个集中 Git 工作副本及 records、本体和未提交更改。需要另行移除集中根时，先备份并确认所有记录、秘密、未提交内容和未决资源的去向；本安装器不承担数据删除或任务取消。

## 宿主发现与可选引导

发现目录只链接到集中根的 `skills/`。宿主是否支持用户级发现路径、符号链接、显式调用和重载，要以现场版本与实际工具为准。无自动重载能力时使用显式 Skill 调用；不能承诺宿主永不遗忘。

安装器不改宿主全局指令、项目 AGENTS.md 或 hooks。用户可把以下短段放入宿主明确支持且实际加载的全局入口，并替换真实集中根；该引导不授权任务创建、阶段执行或读取全部项目：

```text
用户显式选择 PDCA 或恢复既有任务时，加载相应 pdca Skill。
只有用户显式调用 pdca-assist 时，才进入当前绑定项目的只读辅助。
集中根为 <PDCA_ROOT>；从具名 records/projects 工作区绑定定位原 task。
每次恢复核对 Git 来源、原会话、最后完整事件、当前授权与未决资源。
绑定冲突或多个任务时停止询问，不在业务项目创建 .pdca 或复制规则。
阶段 Skill 不换 Agent；父会话只路由用户原始消息，不监工、不代执行。
各阶段由用户明确启动，完成后报告并等待；不自动跨阶段或场景推进。
恢复失败、身份改变或能力不足时阻断；取消与安全收尾优先。
```

正式任务需要现场验证创建、用户交互、继续原实例、挂起/取消、写域和事件回执的真实语义。工具名相似不证明能力等价；没有可交互、可继续原实例的宿主能力时阻断，不由父 Agent 接管。核验细节在 [能力契约](ontology/concept/capability-protocol.md)，当前现场状态见 [验收清单](tests/host-acceptance.md)。

安装设计的查阅来源保留如下，供核对具体宿主版本；这些资料不是现场已通过的证据，也不授予读取或写入权限：

- [Agent Skills 规范](https://agentskills.io/specification)：Skill 目录、名称、描述和按需正文。
- [OpenAI Codex Skills 文档](https://developers.openai.com/codex/skills/)：用户级发现与显式技能调用。
- [OpenCode Skills 文档](https://opencode.ai/docs/skills/)：发现路径、加载与权限。
- [Claude Code Skills 文档](https://code.claude.com/docs/en/skills)：宿主发现和执行上下文；阶段入口保持原 Agent，不设置阶段 fork。

安装发现与工作方法分离借鉴既有工具的组织方式，没有从上游复制运行时代码。集中资源管理来自本项目要求，并非 Agent Skills 规范强制要求。
