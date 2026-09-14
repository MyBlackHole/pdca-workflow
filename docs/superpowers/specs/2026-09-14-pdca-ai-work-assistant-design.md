# PDCA AI 工作辅助与 Git 集中根设计

## 目标

本设计把 PDCA 变为一个由 Git 管理的集中工作副本，并在其 Skills 中增加用户显式调用的 `$pdca-assist`。AI 读取当前已绑定项目的集中记录、源码、文档和 Git 状态，提出任务、上下文、质量证据和协作方面的可选动作；用户选择、补充并授权后才会发生写入或阶段路由。

项目不再维护复制式安装、发布清单、规则快照或安装状态。安装只得到一个 Git 工作副本和指向其 `skills/` 目录的发现路径。

## 安装与更新

用户以单条命令安装：

```bash
curl -fsSL https://raw.githubusercontent.com/MyBlackHole/pdca-workflow/main/install.sh | bash
```

仓库根的 `install.sh` 只执行以下操作：

1. 检查当前系统提供 `git`；
2. 若 `~/.agents/pdca` 已存在，退出且不修改它；
3. 克隆 `https://github.com/MyBlackHole/pdca-workflow.git` 到 `~/.agents/pdca`；
4. 若 `~/.agents/skills` 已存在（包括目录或符号链接），退出且不合并、不替换；
5. 创建 `~/.agents/skills -> ~/.agents/pdca/skills` 符号链接；
6. 输出集中根、发现路径、显式 Skill 调用和更新说明。

脚本不写业务项目、不创建项目绑定、不复制文件、不生成快照、不注册后台服务，也不执行 Git 更新。用户自行执行 Git 命令更新，并按宿主能力重启或显式重载 Skill。Git 冲突和本地未提交更改由用户处理。

## 集中数据、Git 与授权

`~/.agents/pdca` 是唯一的 `PDCA_ROOT`，也是 Git 工作副本。它保存本体、Skills 与集中 `records/`；已绑定业务项目是 `TARGET_ROOT`。业务项目不创建 `.pdca/`，不接收安装器写入。

`$pdca` 取代旧 `setup register/locate`：用户明确批准后，它在 `records/projects/` 创建或定位绑定。每个绑定、任务或事件记录写入时都记录当时 Git `HEAD` 与工作树状态，供追溯；不复制规则快照、不自动 checkout 历史提交，也不把当前 Git 状态冒充不可变快照。

记录写入和 Git 提交是两次不同的授权。AI 只能在用户明确同意写入后改动 records；只有用户另行明确要求提交时才能执行 `git add`/`git commit`。AI 不自动提交、拉取、切换分支、暂存、还原或覆盖集中工作树。`$pdca-assist` 遇到脏工作树只报告风险，并给出审阅、提交、暂存或继续的选项。

## Skills 与交互

保留现有八个入口的语义、原 Agent 连续性以及每个阶段必须由用户启动的规则。新增 `$pdca-assist` 是用户显式调用的工作台，默认只读：

1. 核验一个已绑定项目及当前 Git 状态；歧义或根冲突时停止；
2. 只读取该项目的集中 records，且在宿主权限允许时读取该 `TARGET_ROOT` 的源码、文档与 Git 状态；
3. 针对任务地图、项目上下文、证据审阅和协作交接各给出少量候选动作；
4. 对每个候选动作标明影响与所需授权；
5. 等待用户选择；不因分析创建记录、任务、Agent、资源预约、阶段或业务写入。

首版不预先增加多个专项 Skill。只有某一视角形成稳定的输入、输出、写入边界和独立调用价值时，才从 `$pdca-assist` 拆出专项方法；它们不得自动串联或替代 Plan、Do、Check、Act。

## 内容收敛

删除并不再替代下列旧安装/发布层：

- `setup`、`scripts/install.py`、`scripts/common.py`、`scripts/build_manifest.py`、`scripts/check_release.py`；
- `release-manifest.md`、`protocol-release.md`、根 `SKILL.md`、`USE-PDCA.md`、`migration/v4.0.0-rc.2-MIGRATION.md`；
- 整个 `bootstrap/`；其中仍有效的恢复、派发和能力规则迁入各自拥有的本体契约；
- 整个 `templates/`：41 个已废弃模板直接删除，其余 18 个现行格式迁入相应 `ontology/contracts/record-shapes/`，使契约成为唯一权威；
- 仅服务于上述复制安装器和发布快照的测试，替换为 `install.sh` 与 Skill 链接的测试。

`README.md` 是唯一的使用概览，`INSTALL.md` 是唯一的安装、更新、卸载与宿主发现说明。安装来源说明、可选全局引导与宿主能力提示并入其中或相应本体文件。删除前必须迁移所有当前链接；Git 历史保留已删除源文件的可追溯性。

`legacy/` 与非当前读取链的参考知识目录不在本次删除授权中；它们需另行确定该仓库是否继续承担知识库职责后再处理。

## 失败处理与验证

发现目录或集中根已存在、缺少 Git、克隆失败、绑定歧义、根冲突、权限不足或 Git 状态异常时，相关 Skill/脚本必须停止并报告事实，不能猜测、覆盖或合并。

验证至少包括：

1. `install.sh` 的临时目录场景：成功克隆/链接、已有集中根拒绝、已有发现目录拒绝、失败时没有覆盖；
2. `$pdca` 的绑定/定位指令包含显式写入授权、Git HEAD/工作树状态记录，以及不创建业务项目 `.pdca/`；
3. `$pdca-assist` 的静态和宿主验收：默认只读、只读当前绑定项目、建议不触发写入或阶段；
4. 当前 Skill 与本体链接完整，且没有指向已删除安装/发布/模板/`bootstrap` 文件的当前链接；
5. `python3 -m unittest discover -s tests -v` 通过；宿主发现与交互仍在 `tests/host-acceptance.md` 中如实保留为 `NOT_RUN`，直到真实现场验收。

## 非目标

- 不提供复制安装器、发布文件哈希、规则快照、自动升级或后台服务；
- 不自动创建或管理 Agent，不把资源预约伪装成锁；
- 不自动提交、拉取、切换分支、暂存、还原或覆盖 Git 工作树；
- 不读取其他项目、未关联目录或无关历史记录；
- 不以静态测试声称宿主已发现 Skill 或完成真实交互验收。
