# 安装与更新

## 首次安装

需要 Git、curl 和 POSIX shell。下面的命令把仓库克隆到 `~/.agents/pdca`，然后只把
[运行入口名录](skills/catalog.json)中的九个 PDCA Skill 逐个链接到
`~/.agents/skills/<skill>`：

```bash
curl -fsSL https://raw.githubusercontent.com/MyBlackHole/pdca-workflow/main/install.sh | bash
```

仓库根的 [install.sh](install.sh) 不把整个 `pdca/skills/` 暴露为宿主发现目录。
仓库中的工程参考 Skill 可以继续被文档引用，但安装后只有
`pdca`、`pdca-assist`、四阶段和三个场景入口可被宿主全局发现。这样避免参考材料误触发，
也允许 `~/.agents/skills` 同时保存其他项目的 Skill。

### 路径与冲突规则

- `~/.agents/pdca` 已存在时拒绝安装，不覆盖、合并或更新。
- `~/.agents/skills` 不存在时由安装器创建；已经是普通目录时允许复用，并保留其中无关内容。
- `~/.agents/skills` 是文件或符号链接时拒绝安装，避免跟随未知路径写入。
- 九个运行入口中的任一目标名已存在时，在克隆前拒绝安装；不会覆盖其他项目的同名 Skill。
- 克隆期间若发现目录或入口路径被其他进程创建，安装器停止并只回滚本次创建的 PDCA 根与链接。

克隆失败、运行入口缺失或链接失败时，安装器只删除本次创建的
`~/.agents/pdca` 和本次已经创建的九个链接；不会删除原有
`~/.agents/skills` 目录或其中的其他内容。

安装完成后，按宿主能力重启或显式重载 Skill，再在新会话中调用 `$pdca`。
入口见 [Skill 索引](skills/README.md)。链接存在不等于宿主已经完成真实发现和交互验收；
现场检查仍见 [host-acceptance](tests/host-acceptance.md)。

## 更新

集中根是普通 Git 工作副本。需要更新时由用户自行运行：

```bash
git -C "$HOME/.agents/pdca" pull
```

九个发现链接指向该工作副本内的固定 Skill 目录，因此更新仓库后无需重新复制 Skill。
Git 冲突和本地未提交更改由用户处理；更新后按宿主能力重启或显式重载 Skill。
安装器没有自动更新、强制覆盖或后台服务模式。

`records/` 与 `ontology/projects/` 是可审阅、可提交的 Git 数据；更新前先检查本地修改与提交策略。
AI 对记录的写入授权不包含 Git 提交或更新授权。活动任务按原绑定、Git 来源与原批准恢复；
规则冲突或原依据缺失时停止，不自动搬迁旧记录或切换历史提交。

## 卸载发现入口

先核对九个运行入口是否确实指向 `~/.agents/pdca/skills/<skill>`，再逐个删除对应符号链接。
不要直接删除整个 `~/.agents/skills`，因为其中可能包含其他项目的 Skill。

示例：

```bash
for skill in pdca pdca-assist pdca-plan pdca-do pdca-check pdca-act pdca-model pdca-implement pdca-verify; do
    link="$HOME/.agents/skills/$skill"
    [ -L "$link" ] && rm -- "$link"
done
```

移除发现入口保留整个集中 Git 工作副本及 records、本体和未提交更改。需要另行移除集中根时，
先备份并确认所有记录、秘密、未提交内容和未决资源的去向；安装器不承担数据删除或任务取消。

## 宿主发现与可选引导

安装器只注册九个运行入口。宿主是否支持用户级发现路径、符号链接、显式调用和重载，
要以现场版本与实际工具为准；不能从文件存在推导“宿主一定发现”。

安装器不改宿主全局指令、项目 AGENTS.md 或 hooks。用户可把以下短段放入宿主明确支持且实际加载的全局入口：

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

正式任务需要现场验证创建、用户交互、继续原实例、挂起/取消、写域和事件回执的真实语义。
工具名相似不证明能力等价；没有可交互、可继续原实例的宿主能力时阻断，不由父 Agent 接管。
核验细节在 [能力契约](ontology/concept/capability-protocol.md)，当前现场状态见
[验收清单](tests/host-acceptance.md)。

安装发现与工作方法分离借鉴既有工具的组织方式，没有从上游复制运行时代码。
集中资源管理来自本项目要求，并非 Agent Skills 规范强制要求。
