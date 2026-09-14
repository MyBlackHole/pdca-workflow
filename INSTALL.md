# 安装与集中使用

## 依赖和实际范围

本版安装工具使用 Linux/POSIX 的 Python 3.10+ 标准库与 `flock`，不需要 pip、Bun、Node、后台服务或网络下载。其他系统未验收。安装不是 Agent Runtime，不签发阶段批准、不提供业务对象锁、不证明宿主已经加载技能。

默认集中根 `~/.agents/pdca`，默认发现目录 `~/.agents/skills`。八个 Skill 导出完整可执行正文，统一指向集中根和固定规则快照。Codex/OpenCode 的共享发现目录已按官方文档核对，真实版本还需现场验证；来源见 [安装设计来源](bootstrap/install-sources.md)。

## 首次安装

在解压后的源码根执行：

```bash
# 无写入预览
./setup
# 真正安装；不修改任何业务项目
./setup --apply
# 核对安装文件、八个导出和规则快照
./setup check
```

若原来的集中根就在当前源码目录，用 `./setup --root "$PWD" --apply` 原地注册。明确的集中根只能是一处；不要把整个中心放在技能发现目录内部。使用自定义根或发现目录时，后续命令始终传相同参数：

```bash
./setup --root /path/to/central-pdca --skills-dir "$HOME/.agents/skills" --apply
./setup check --root /path/to/central-pdca --skills-dir "$HOME/.agents/skills"
```

Claude Code 可明确指定 `--skills-dir "$HOME/.claude/skills"` 注册同一中心的八个入口。不自动写项目/global AGENTS.md、CLAUDE.md或插件配置；可选短引导见 [global-entry](bootstrap/global-entry.md)。同一宿主扫描多个入口位置时避免重复同名注册。本版不提供伪装成原生插件的清单。

安装器拒绝已存在的非所属目录、修改过的技能导出、符号链接托管路径或不同集中根的同名入口；不会使用 `rm -rf` 清理冲突。可先保留旧安装并人工核对，不能强制覆盖。确认已由其他插件管理器安装的入口，应通过原管理方式卸载或解除注册，不删业务资源。

## 登记一个项目：只写集中根

```bash
cd "$HOME/.agents/pdca"
./setup register --project /path/to/project-a --project-id project-a --workspace-id main
./setup register --project /path/to/project-a --project-id project-a --workspace-id main --apply
./setup locate --project /path/to/project-a
```

登记位置是 `records/projects/project-a/workspaces/main/project-context.md`。项目目标可为空目录；工具不在目标内创建 `.pdca/`，不修改其指令、ignore、源码或Git元数据。检测到旧项目本地 `.pdca/project-context.md` 时拒绝新增绑定，先按迁移说明核对，不能建立双中心。项目和工作区ID是显式小写slug；同一真实路径不能静默登记成另一个身份，移动项目不能复用旧context冒充原位置。

登记只固定身份和集中规则快照，没有新任务、Agent、阶段批准或业务写权。相同登记重复执行保持原版本；更新全局入口不会更新已有context。已有手工登记采用不同格式时阻断并要求显式迁移，不猜测读取内容。

## 调用

在目标项目的新宿主会话中使用 `pdca` 做接入检查，只报告集中根、绑定、任务和待确认事项，不执行业务。宿主支持显式技能选择时可以选完整名字，例如 Codex 输入 `$pdca`；OpenCode请求原生skill工具加载`pdca`。名称列表见 [八个入口](skills/README.md)。

随后针对已具名的任务使用 `pdca-plan`、`pdca-do`、`pdca-check`、`pdca-act`，每次只批准展示过的阶段对象。主会话中的调用必须路由回原任务会话，不能在主会话接管阶段。三个本体场景入口不是三个阶段，也不自动串联。

安装后能够读取八个SKILL.md，不等于宿主发现、可交互子Agent、权限和恢复都已通过。现场按 [host-acceptance](tests/host-acceptance.md)逐项核验；没有自动重载能力时显式加载，不能承诺永不遗忘。

## 更新与卸载

从**另一份干净的新版本源码**执行 `./setup --update --apply`，沿用原root/skills-dir参数。没有`--update`不跨发布更新；原安装文件存在本地改动或新发布碰撞非所属文件时仍然拒绝。不要先直接覆盖安装目录再期待安装器识别并安全更新；维护源改动后须重新构建清单，审核后按新版本安装。

旧集中规则快照、业务records、ontology/projects、用户额外文件始终保留，已有任务继续固定版本。软件成员被新版本移除时也不自动清理旧文件；它们不属于新active读集。规则发布和任务迁移是两件事。

```bash
./setup uninstall            # 预览移除的八个注册入口
./setup uninstall --apply    # 只移除所属且未修改的导出及标记
```

卸载不会删除PDCA_ROOT、records、本体或规则快照，也不撤销正在运行的Agent/资源。卸载前活动任务的终止或迁移由用户另行处理。本工具不提供“清空中心”选项。

每次文件写入使用临时文件、fsync及rename；一般异常尽量回滚本次修改，安装命名空间使用锁避免双写。**这不是断电下整个安装事务的原子保证**；中断后 `check` 不通过应先保留现场、恢复或人工核对，不强行更新、不运行校验失败的入口。锁只协调安装/登记，不是业务资源锁。
