# 安装与更新

## 首次安装

需要 Git、curl、POSIX shell、readlink 和 GNU/BSD stat，以及常见文件工具（mkdir、ln、rm、rmdir）。
安装器使用 stat 的设备号/文件号核对目录与链接身份，不需要 Python。HOME 必须是已有目录的绝对路径。
下面的命令把仓库克隆到 `~/.agents/pdca`，然后只把
[运行入口名录](skills/catalog.json)中的九个 PDCA Skill 逐个链接到
`~/.agents/skills/<skill>`：

```bash
curl -fsSL https://raw.githubusercontent.com/MyBlackHole/pdca-workflow/main/install.sh | bash
```

仓库根的 [install.sh](install.sh) 不把整个 `pdca/skills/` 暴露为宿主发现目录。
仓库中的工程参考 Skill 可以继续被文档引用，但安装后只有
`pdca`、`pdca-assist`、四阶段和三个场景入口可被宿主全局发现。这样避免参考材料误触发，
也允许 `~/.agents/skills` 同时保存其他项目的 Skill。

### 路径、入口与冲突规则

- `~/.agents` 必须是普通目录；若是符号链接则拒绝。HOME 中的既有链接先解析到物理目录。
- `~/.agents/pdca` 已存在时拒绝安装，不覆盖、合并或更新。
- `~/.agents/skills` 不存在时在克隆前创建；已有普通目录可复用，保留其他项目内容。
- `~/.agents/skills` 是文件或符号链接时拒绝；九个入口目标中的任一名称（包括悬空链接）冲突时拒绝。
- 克隆前固定发现目录的工作目录；写入和链接回滚都相对此目录进行，不重新跟随可能被替换的发现路径。
- 核对 `.agents`、发现目录和中央根的设备号/文件号，发现替换则报错停止；链接命令显式以 `.` 为目标目录，同名目录突然出现时不向其内部嵌套安装。
- 包内 `skills/` 和每个入口目录必须是普通目录；每个 `SKILL.md` 必须是可读、非空、非符号链接的普通文件。此检查仅验证安装入口，不解释 PDCA 语义。

### 失败与回滚

失败返回非零状态。回滚只删除本次已登记、文件身份与链接目标均未变化的符号链接；
同名条目已被用户替换时保留，不因为链接目标相同就视为本次创建的对象。
创建链接的命令若在完成登记前失败或中断，报告未确认条目，保留现场供检查。

**安装器不再对中央检出目录执行递归删除。** 只尝试移除身份未变且为空的本次新目录。
非空检出、身份不确定的目录，以及其中其他进程新增的数据会保留并打印提示。
因此部分失败后 `~/.agents/pdca` 可能仍然存在；检查保留内容和提示，明确其归属后由用户自行处置，
再重新安装。不要将保留现场当作安装成功，也不要直接覆盖它。原有发现目录不会被删除。

HUP/INT/TERM 和普通错误使用相同回滚路径；SIGKILL、断电等无法执行清理的情况仍需检查现场。
此方式优先避免误删，不承诺目录身份检查与最后一次文件操作是原子的，也不阻挡具有同一用户权限、
可持续修改目录、工具或 Git 配置的恶意进程。请在自己可信的 HOME 中运行，避免安装时并发修改相关路径；
需要强隔离时使用宿主/操作系统权限与沙箱，而不是依赖安装脚本。

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

示例仅适用于 HOME 已是物理路径且没有并发修改的情况；其他路径以安装器打印的实际目标为准：

```bash
for skill in pdca pdca-assist pdca-plan pdca-do pdca-check pdca-act pdca-model pdca-implement pdca-verify; do
    link="$HOME/.agents/skills/$skill"
    if [ -L "$link" ] && [ "$(readlink "$link")" = "$HOME/.agents/pdca/skills/$skill" ]; then
        rm -- "$link"
    fi
done
```

移除发现入口保留整个集中 Git 工作副本及 records、本体和未提交更改。需要另行移除集中根时，
先备份并确认所有记录、秘密、未提交内容和未决资源的去向；安装器不承担数据删除或任务取消。

## 宿主发现与可选引导

### OpenCode

OpenCode 官方 Agent Skills 发现规则包含全局兼容目录 `~/.agents/skills/<name>/SKILL.md`，与本安装器的九个运行入口布局一致；Skill 由宿主按需通过原生 skill 能力加载，而不是把全部正文默认注入每个会话。

仓库的 `.github/workflows/opencode-smoke.yml` 在隔离 HOME 中运行真实 `install.sh`，下载并校验固定 OpenCode CLI，然后以 OpenCode 自带的 `opencode debug skill` 作为兼容门禁。当前对 **OpenCode v1.18.32** 的真实 Actions 结果已经确认：九个 PDCA runtime Skill 都能从安装器生成的 `~/.agents/skills/<name>/SKILL.md` 路径被发现、解析，并读取到实际 Skill 正文。

headless `opencode serve` 的 `/api/skill` 在同一 Actions 环境中只返回内置 Skill，没有暴露 external PDCA Skills；该路径目前仅保留为非门禁诊断，不能据此否定 CLI 发现能力，也不能声称 server/session 集成已通过。

兼容 smoke 不读取用户提供的 provider 凭据。OpenCode v1.18.32 在无 `OPENCODE_API_KEY` 时可通过 public provider 路径访问启用的免费模型；真实 Actions 已使用 `opencode/mimo-v2.6-flash-free` 完成 bounded-counter ontology-core-only 推理，并验证模型实际调用原生 `skill(pdca)`。随后又用 `candidate-0.3.0` 的纯 ontology core 启动两个独立 `opencode run` session：两次 session ID 不同、Section 1–7 中 `NODE-*` 泄漏为 0，但恢复出的 composition、producer/consumer dependency、三类 work-instance responsibility 与 `ready=false` 归一化后完全一致。另一个运行时探针使用只在当次 job 生成的随机 token 建立会话，再通过 `opencode run --session <id>` 显式续接同一 session；第二轮保持相同 session ID、恢复前一轮状态，并拒绝 repository/file/search tool 读取。宿主侧随后用 `opencode session list --format json` 与 `opencode export <session-id>` 直接检查持久化会话：export 的 `info/messages` 中存在两条真实 user turn，第一轮的 native Skill tool interaction 作为独立 assistant message 被保留，第二条 user 没有重新注入 runtime token，而续接后的 assistant 从同一 session 历史恢复了 token。free-model probe 保持非阻断，因为公共免费端点可能限流或下线；证据见 [单次 public-model recovery](docs/reviews/2026-09-27-opencode-public-model-recovery.md)、[fresh-session recovery](docs/reviews/2026-09-27-opencode-fresh-session-recovery.md)、[session continuity](docs/reviews/2026-09-27-opencode-session-continuity.md) 与 [persisted session transcript](docs/reviews/2026-09-27-opencode-session-transcript.md)。

这仍不等于正式 PDCA fresh-Agent host acceptance：虽然 OpenCode CLI 的指定 session 续接与 host-side transcript persistence 已有真实运行证据，但 v1.18.32 的 persisted UserMessage 只记录 user role、session、agent/model、时间等信息，没有外部 sender/actor/ingress/transport provenance；因此 `role=user` 不能单独证明真人来源。CI prompt 也不是正式 task 的真实用户 `phase_start`，仍没有 root Modeling 的 Plan/Do/Check/Act fixation、fixed task/assignment/context 初始化、真实用户消息来源与路由绑定、任务级 suspend/continue 对账或完整 implement/verify scene。因此 H1/H10/H11/H18 与其余现场验收仍按实际清单保持未执行。该来源边界见 [OpenCode user-message provenance](docs/reviews/2026-09-27-opencode-user-message-provenance.md)，基础 CLI discovery 证据见 [OpenCode 兼容性审查](docs/reviews/2026-09-27-opencode-compatibility.md)。

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
各阶段由用户明确启动；Plan/Do/Check 完成后报告并等待下一真实操作，Act 完成后同一授权下 terminalize/archive；不自动跨阶段、返工、任务或场景推进。
恢复失败、身份改变或能力不足时阻断；取消与安全收尾优先。
```

正式任务需要现场验证创建、用户交互、继续原实例、挂起/取消、写域和事件回执的真实语义。
工具名相似不证明能力等价；没有可交互、可继续原实例的宿主能力时阻断，不由父 Agent 接管。
核验细节在 [能力契约](ontology/concept/capability-protocol.md)，当前现场状态见
[验收清单](tests/host-acceptance.md)。

安装发现与工作方法分离借鉴既有工具的组织方式，没有从上游复制运行时代码。
集中资源管理来自本项目要求，并非 Agent Skills 规范强制要求。
