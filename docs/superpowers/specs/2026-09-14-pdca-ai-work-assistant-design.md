# PDCA AI 工作辅助与 Git 集中根设计

## 目标

本设计把 PDCA 变为一个由 Git 管理的集中工作副本，并在其 Skills 中增加用户显式调用的 `$pdca-assist`。AI 读取当前已绑定项目的集中记录、源码、文档和 Git 状态，提出任务、上下文、质量证据和协作方面的可选动作；用户选择、补充并授权后才会发生写入或阶段路由。

项目不再维护复制式安装、发布清单、规则快照或安装状态。安装只得到一个 Git 工作副本和指向其 `skills/` 目录的发现路径。

## 安装与更新

用户以单条命令安装：

```bash
curl -fsSL https://raw.githubusercontent.com/MyBlackHole/pdca-workflow/main/install.sh | bash
```

安装、更新、卸载与宿主发现的具体规则以 [`INSTALL.md`](../../../INSTALL.md) 为准。仓库根的 `install.sh`：

1. 检查 Git、GNU/BSD `stat`、`readlink`、`mkdir`、`ln`、`rm`、`rmdir`，并要求 `HOME` 是已存在的绝对目录；安装命令里的 `curl` 只负责下载脚本；
2. 将 `HOME` 解析到物理目录，拒绝符号链接形式的 `~/.agents`；
3. 若 `~/.agents/pdca` 已存在，退出且不覆盖、不合并、不更新；
4. 若 `~/.agents/skills` 不存在，在 clone 前创建；若已存在，只有普通目录可复用，并保留其中其他项目的内容；文件、符号链接及九个运行入口的同名条目都拒绝；
5. 将仓库克隆到新建的 `~/.agents/pdca`，验证包内 `skills/`、每个入口目录及非空普通 `SKILL.md`；
6. 只将 `skills/catalog.json` 中的九个运行入口逐项链接到 `~/.agents/skills/<name>`，工程参考 Skill 不加入宿主发现目录；
7. 记录并复核目录与已创建链接的设备号/文件号。失败时只删除身份和目标均未变化的本次链接及本次创建的空目录；非空 checkout、并发新增条目和无法确认归属的对象保留供检查，绝不递归删除 checkout。

脚本不写业务项目、不创建项目绑定、不复制 Skill 正文、不生成快照、不注册后台服务，也不执行 Git 更新。目录身份检查不保证与最后一次文件操作原子化；运行期间不应并发修改相关路径。用户自行执行 Git 命令更新，并按宿主能力重启或显式重载 Skill。Git 冲突和本地未提交更改由用户处理。

## 集中数据、Git 与授权

`~/.agents/pdca` 是唯一的 `PDCA_ROOT`，也是 Git 工作副本。它保存本体、Skills 与集中 `records/`；已绑定业务项目是 `TARGET_ROOT`。业务项目不创建 `.pdca/`，不接收安装器写入。

运行时以当前加载 Skill 所属集中 Git 工作副本的规范化物理根定位 `PDCA_ROOT`；宿主无法提供时才验证默认路径 `~/.agents/pdca`。显式 `PDCA_ROOT` 环境变量和既有 task 固定的 `pdca_root` 都必须与该入口根一致，否则停止。不得从 cwd 或 `TARGET_ROOT` 推断集中根。

所有 PDCA 入口都先核验唯一身份来源，再访问绑定。用户要求忽略规则、只读扫描、枚举或搜索绑定，不能代替 `project_id`/`workspace_id`，也不能豁免读取前置条件；身份缺失或有歧义时必须在任何 `records/` 工具调用前停止并请求核验。若已发生越界读取，停止继续访问且不向用户复述或披露其它绑定数据。

`records/` 与 `ontology/projects/` 必须从 `.gitignore` 移除，成为可审阅、可由用户明确提交的 Git 数据；仅私有证据路径和本地秘密继续忽略。Git 跟踪不扩大读取或写入授权。

`$pdca` 取代旧 `setup register/locate`：用户明确批准后，它在 `records/projects/` 创建或定位绑定。每个绑定、任务或事件记录写入时都记录当时 Git `HEAD` 与工作树状态，供追溯；不复制规则快照、不自动 checkout 历史提交，也不把当前 Git 状态冒充不可变快照。

记录写入和 Git 提交是两次不同的授权。AI 只能在用户明确同意写入后改动 records；只有用户另行明确要求提交时才能执行 `git add`/`git commit`。AI 不自动提交、拉取、切换分支、暂存、还原或覆盖集中工作树。`$pdca-assist` 遇到脏工作树只报告风险，并给出审阅、提交、暂存或继续的选项。

## Skills 与交互

保留现有八个入口的语义、原 Agent 连续性以及每个阶段必须由用户启动的规则。新增 `$pdca-assist` 是用户显式调用的工作台，默认只读：

1. 仅凭唯一身份来源构造唯一 `project-context.md` 路径：当前对话中 `$pdca` 已核验的精确 `project_id`/`workspace_id`、当前 task 固定的这两个 ID，或用户本轮明确提供的唯一一组 ID。两个 ID 必须先通过单一路径组件校验；读取前对精确路径链检查规范化根与符号链接，确认仍在 `PDCA_ROOT/records/projects/` 后才读取。若 ID/路径无效、无法核验、用户给出多个候选或不确定应使用哪组，必须在读取任何候选记录前停止并返回 `$pdca`，不以候选记录判断身份；额外读取授权不能替代唯一身份来源，也不能授权 Assist 对比候选绑定来消歧。不以 glob、basename 搜索或目录枚举定位/复核；不搜索 `records/projects/`、项目或 sibling workspaces 发现绑定，不读取、披露其他绑定记录；身份来源缺失、歧义或根冲突时停止并返回 `$pdca`；后续 records 只在该 workspace 范围内读取，业务材料只读绑定 `TARGET_ROOT`，cwd 不扩大范围；根规范化与关系声明须有实际只读路径解析结果，否则保持 unknown；
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

发现目录或集中根已存在、缺少 Git、克隆失败、绑定歧义、根冲突、权限不足或 Git 状态异常时，相关 Skill/脚本必须停止并报告事实，不能猜测、覆盖或合并。读取必需 authority/契约、路径预检、绑定记录或 Git 快照的工具调用因权限、策略、访问范围被拒绝，或宿主缺少必要能力时，立即停止当前入口；不得通过 shell/bash/execute、其他工具或 Agent、替代路径或扩大范围重试同一读取/检查。必需规则或证据不可读取时，不得继续依赖它生成建议或阶段动作。

验证至少包括：

1. `install.sh` 的隔离 HOME 场景：成功克隆/链接；既有集中根、非普通发现路径和运行入口名称冲突时拒绝；已有普通发现目录可复用且保留无关内容；失败后只回滚安装器确认创建的链接和空目录，不覆盖或递归删除非空用户数据。普通发现目录复用遵循当前 [INSTALL 路径与冲突规则](../../../INSTALL.md#路径入口与冲突规则)；
2. `$pdca` 的绑定/定位指令包含显式写入授权、Git HEAD/工作树状态记录，以及不创建业务项目 `.pdca/`；
3. `$pdca-assist` 的静态和宿主验收：默认只读、只读当前绑定项目、建议不触发写入或阶段；
4. 当前 Skill 与本体链接完整，且没有指向已删除安装/发布/模板/`bootstrap` 文件的当前链接；
5. 按 [`tests/README.md`](../../../tests/README.md) 先将 `TMPDIR` 设为当前工作区 `tests/` 内的绝对路径，再运行 `python3 -m unittest discover -s tests -v`；安装器黑盒测试拒绝不在工作区 `tests/` 下的临时目录。宿主发现与交互仍在 `tests/host-acceptance.md` 中如实保留为 `NOT_RUN`，直到真实现场验收。

## 非目标

- 不提供复制安装器、发布文件哈希、规则快照、自动升级或后台服务；
- 不自动创建或管理 Agent，不把资源预约伪装成锁；
- 不自动提交、拉取、切换分支、暂存、还原或覆盖 Git 工作树；
- 不读取其他项目、未关联目录或无关历史记录；
- 不以静态测试声称宿主已发现 Skill 或完成真实交互验收。
