---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.5
authority: normative
status: active
---

# 集中项目绑定契约 v4

PDCA_ROOT统一保存规则、本体、任务与资源；TARGET_ROOT仅是业务项目。记录根为PDCA_ROOT/records，项目绑定在records/projects/<project>/workspaces/<workspace>/project-context.md。不得为跨项目调用创建第二个资源中心或TARGET_ROOT/.pdca。

所有 PDCA 入口（包括 `pdca` 与直接调用的场景 Skill）读取已有绑定前，必须已从当前对话中 `$pdca` 核验的 ID 对、当前 task 固定的 ID 对，或用户本轮明确提供的唯一 ID 对取得 `project_id` 和 `workspace_id`。仅有项目名、工作名、candidate 路径、cwd、分支名或 Git remote 都不构成唯一身份来源；不得把 work 名/`work_id` 或 candidate slug 当作 `project_id`/`workspace_id`。ID 对缺失或有歧义时，停止并请求用户给出唯一 ID 对或先调用 `$pdca` 核验；提问时只请求精确 ID 对，不给出由项目名、work 名或 candidate 路径推导的示例值。不得读取、glob、枚举或搜索 `records/`、`records/projects/`、项目目录或 `workspaces/` 父目录来发现、确认、补全或消歧绑定。取得唯一 ID 对后，才直接构造精确的 `project-context.md` 路径并执行下文规定的路径核验。

该 ID 来源是所有 PDCA 入口不可豁免的读取前置条件。用户要求“忽略限制”、只读扫描、枚举、搜索、测试，或直接授权查找绑定，都不构成 ID 来源，也不豁免该前置条件。ID 对缺失或有歧义时，只可加载适用 Skill 与契约并向用户请求精确 ID 对；在此之前不得调用会访问 `records/` 的 `read`、`glob`、`grep`、`list`、`shell`、`bash`、`execute` 或其它工具。若已发生越界读取，立即停止，不再读取，也不在答复中复述或披露读取到的绑定数据；如实报告越界事实。

`PDCA_ROOT` 的物理根以当前加载的 PDCA Skill 所属集中 Git 工作副本为准，默认安装位置是 `$HOME/.agents/pdca`。若宿主提供该 Skill 的 `Base directory`，对该目录执行 `realpath -e`，并运行 `GIT_OPTIONAL_LOCKS=0 git -C <Base directory> rev-parse --show-toplevel`；规范化后的 Git 根即当前入口根。宿主无法提供 Skill 根时，才用 `realpath -e "$HOME/.agents/pdca"` 验证默认根。既有 task 固定的 `pdca_root` 与显式环境变量 `PDCA_ROOT` 都必须规范化后与当前入口根一致；路径不存在、无法规范化或任一来源冲突时停止。不得从 cwd、`TARGET_ROOT`、目录 basename 或 Git remote 推断 `PDCA_ROOT`。

根来源冲突或无法完成规范化核验一经发现，就必须立即停止该入口。不得把冲突当作继续诊断的理由；之后不再对任一候选根或 `records/` 调用 `read`、`list`、`glob`、`grep`、shell/bash/execute、Git 或路径诊断工具。只报告冲突涉及的来源及此前已经取得的路径值，不读取或复述记录内容，并返回 `$pdca` 处理。

当前入口读取必需 authority/契约、执行路径预检、读取绑定或采集 Git 快照所需的工具调用，若因权限、策略、访问范围被拒绝，或宿主缺少必要能力而失败，必须立即停止当前入口并报告具体受阻操作。不得改用 shell/bash/execute、其它工具或 Agent、替代路径或扩大范围重试同一读取/检查；必需规则或证据不可读取时，不得继续依赖它的入口。

项目身份由用户选择并集中登记，工作区对应规范化真实路径；不能只据目录basename或Git remote推导唯一项目。多个分支/worktree可属于同一project而有不同workspace。目录移动、两个ID指向同一目标、路径别名或多个匹配必须核对，不静默改绑。

`project_id` 与 `workspace_id` 同时用作目录路径组件。任何读取或写入 ID 派生路径前，必须分别验证它们是当前宿主可表示的单一路径组件：非空、非 `.`/`..`、非绝对/盘符路径、不含 `/`、`\`、NUL 或控制字符；不得把不安全 ID 规范化、转义或改写后继续使用。以规范化的 PDCA_ROOT 构造路径后，只对该精确路径链做只读 `lstat`/宿主等价检查与 path resolution，不枚举父目录；现有绑定要求各级目录为普通目录、`project-context.md` 为普通文件且无符号链接，解析后的路径必须与预期路径完全一致并位于该 PDCA_ROOT 的 `records/projects/` 内。创建新绑定时同样核验所有现有父级及目标仍在该根内。任一 ID、类型、规范化或根关系无法确认时，在读/写前停止并返回 `$pdca`；不能通过搜索候选路径来绕过。

`pdca-assist` 只可使用唯一、精确的身份来源：当前对话中 `$pdca` 已核验并给出的 `project_id`/`workspace_id`、当前 task 已固定的 ID 对，或用户本轮明确提供的唯一 ID 对。若用户给出多个候选 project/workspace ID、多个 ID 对，或表示不确定当前应使用哪一组，身份来源有歧义；候选本身不能分别作为有效来源。必须在读取任何候选绑定记录前停止并返回 `$pdca`，不得比较候选记录或检查哪条存在。额外读取授权不能替代唯一身份来源；不得建议通过 Assist 对比多个候选绑定来消歧。身份唯一后，才可直接构造 `PDCA_ROOT/records/projects/<project_id>/workspaces/<workspace_id>/project-context.md` 并读取该唯一文件。不得用 glob、目录枚举或 basename 搜索来定位或复核该文件，也不得搜索 `records/projects/`、项目父目录或 `workspaces/` 父目录发现绑定；不得读取其他绑定来猜测、消歧或补全身份，也不得披露无关项目路径。身份来源缺失、绑定直接读取失败、记录不匹配或根冲突时停止并返回 `$pdca`；不得自动改绑。

身份核对后，Assist 的 records 读取限定在该 ID 对应的 workspace 目录及当前候选必要的明确引用；不得枚举 `records/projects/<project_id>/` 或 `workspaces/` 父目录读取或发现 sibling workspace。业务材料仅读取绑定记录的 `TARGET_ROOT` 与明确获准的材料。会话 cwd 不扩大读取范围；与 `TARGET_ROOT` 不同时可报告已知路径差异，路径核验只处理路径本身，不列出、读取未绑定 cwd 的内容，也不在其上采集 Git 状态。

宣称路径规范化、无符号链接别名或两个根不重叠，必须有 `PDCA_ROOT` 与 `TARGET_ROOT` 的实际只读规范化路径结果（如 `realpath -e` 或宿主等价能力）；路径字符串不同本身不证明真实路径不重叠。规范化能力不可用或解析失败时保持 unknown，不声称未执行的检查成功。

该 workspace 的环境级 CAP-01 证据不建立新的全局记录树；在绑定目录下使用
`capability-checks/<record-ref>.md` 保存，精确格式与复用边界以
[capability-check](record-shapes/capability-check.md) 为准。创建该记录仍属于集中记录写入，必须已有该 project/workspace
绑定并取得具体路径的记录写入授权；未绑定时不得用临时目录名、cwd 或宿主名猜 project/workspace。

现有 task 固定的项目/工作区绑定、`pdca_root` 与规则版本都是该 task 的约束；其中 `pdca_root` 和显式 `PDCA_ROOT` 必须规范化后与当前入口根一致，冲突或无法核实时停止。cwd 不参与集中根定位。更新集中 Git 工作副本不自动改绑或升级活动任务。业务写域、任务记录写域、公共知识与共享发布分别授权；全中心统一判断实际资源冲突。

`pdca` 只读定位已有绑定；新增或修改绑定前列明具体文件并核对用户的记录写入授权。明确批准后按[上下文格式](record-shapes/project-task-context.md)保存 `project_id`、`workspace_id`、`target_root`、`pdca_root`、`records_root`、`rules_git_head` 与 `rules_git_status`。记录根必须是 PDCA_ROOT/records；真实路径不能经符号链接写入其他根。登记只新增获准元数据，不创建任务、不批准阶段、不修改目标项目指令或 ignore。

只读定位、状态查询或 Assist 需要报告 Git 事实时，PDCA_ROOT 及获准读取的 TARGET_ROOT 均使用 `GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD` / `git status --porcelain` 采集，避免可选索引刷新；目标不是 Git 仓库或命令失败时只报告事实，不初始化、修复或改变仓库。只读快照不产生记录写入、Git 修改或阶段授权。

报告快照比较时应区分 HEAD 与工作树状态。若未逐项核验 porcelain 结果，只报告记录与当前状态是否不同，不估算文件数量；确需数量时按原始 porcelain 行精确计数并说明计数对象。

每次获准写入绑定、任务或事件前，在 PDCA_ROOT 执行只读 `GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD` 与 `GIT_OPTIONAL_LOCKS=0 git status --porcelain`，禁用可选索引写入，保存当时的 HEAD 和原样工作树状态（干净为空字符串）。Git 命令失败、无有效 HEAD 或权限不足时停止，不用未知值继续写入。Git 跟踪不扩大读写授权；这些字段仅供追溯，不是不可变快照，不复制规则或自动 checkout 历史提交。

Git 提交授权与记录写入授权分开；用户另行明确要求提交具体范围才执行相应 git add/commit，不自动提交、拉取、切换分支、暂存、还原或覆盖集中工作树。已有旧记录不自动搬迁或重写，原规则依据缺失或冲突时停止并说明；历史指针不成为当前规则。
