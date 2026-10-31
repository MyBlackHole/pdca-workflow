---
name: pdca-assist
description: 仅在用户显式调用 pdca-assist，为当前已绑定项目选择下一步工作建议时使用。普通请求不自动启用。
metadata:
  version: 5.0.0-rc.3
---

# PDCA Assist：只读候选建议

用户显式调用才进入。只读取和展示候选；不创建 record/task/Agent/phase/resource，
不写 TARGET_ROOT、不运行测试/构建/安装、不修改 Git。候选被用户选中也不是后续动作授权。

## 身份门禁是加载后的第一步

完成本 Skill 加载后，先且只根据当前对话中已经出现的核验结果、已固定 task 身份或用户本轮明确提供的信息，判断是否存在唯一 `project_id`/`workspace_id` 对。此判断不得调用工具。

若身份来源缺失或有歧义，立即停止并只输出下面这一行；不得先读项目绑定契约、检查 `PDCA_ROOT`/cwd/`TARGET_ROOT`、执行 Git/path 诊断、搜索绑定、读取任何文件，或在答复后补充受阻操作说明：

`身份门禁未通过：请提供精确 project_id 与 workspace_id；若续做既有 task，再提供唯一 task_id。也可先调用 $pdca 核验绑定。本次未读取 records，未产生候选。`

只有唯一身份来源已经成立，才继续“最小读取”中的根规范化、路径预检和绑定读取。该身份优先规则覆盖后文所有关于 `PDCA_ROOT`、契约和读取顺序的说明。

## 路径与环境核验的 shell 输出格式

身份门禁通过后，在任何用 shell 核验 `PDCA_ROOT`、`TARGET_ROOT` 或 cwd 之前，必须用下面这一条命令分别标注三项值：

```sh
printf 'PDCA_ROOT=%s\nTARGET_ROOT=%s\nPWD=%s\n' "${PDCA_ROOT-<unset>}" "${TARGET_ROOT-<unset>}" "$(pwd -P)"
```

不得用 `printenv PDCA_ROOT TARGET_ROOT`、多条无标签 `printenv` 或裸 `pwd` 来采集这些值。若已得到无标签输出，必须丢弃其位置推断，并先运行上面的带标签命令再继续；`<unset>` 只表示该环境变量未设置。`TARGET_ROOT` 的业务权威值仍只来自已核验的绑定记录，不能由环境变量替代。

## 相对链接按物理 Skill 路径解析

读取本 Skill 中的契约或 authority 相对链接前，必须按有数据依赖的顺序完成两步：先单独调用 `realpath -e <Skill Base directory>` 并取得其物理绝对路径；再在后续工具调用中，以这次返回的精确物理路径为前缀解析相对链接。例如，若第一步返回 `/central/skills/pdca-assist`，第二步才可解析 `/central/skills/pdca-assist/../../ontology/contracts/project-workspace.md`，并读取第二步返回的规范化文件路径。

不得把两步合并为一个 shell 调用，也不得只并列打印物理 Skill Base、却仍用 `.agents/skills` 等词法软链接路径拼接相对链接。第二步的路径参数必须实际使用第一步输出的物理路径；不能依赖 `realpath` 在路径遍历时自行跟随软链接来替代该顺序。若第一步失败、物理路径不唯一或无法从物理路径解析 authority，停止并返回 `$pdca`；不得试探备用位置、列目录或搜索同名文件。

## 最小读取

读取绑定前必须先有一个**唯一**、精确、可信的身份来源，且它只指向一组
`project_id`/`workspace_id`：当前对话中 `$pdca` 已核验并给出的 ID 对、当前 task 已固定的 ID 对，或用户本轮明确提供的唯一 ID 对。
若用户给出多个候选 project/workspace ID、多个 ID 对，或表示不确定当前应使用哪一组，身份来源有歧义；这些候选不能分别视为有效来源。
此时必须在读取任何候选绑定记录前停止，并请用户先通过 `$pdca` 核验一个唯一 ID 对。额外读取授权不能替代唯一身份来源；不得建议以 Assist 对比多个候选绑定来消歧。
构造绑定路径前，先按[项目绑定契约](../../ontology/contracts/project-workspace.md)确定并规范化 `PDCA_ROOT`；不得从 cwd 或 `TARGET_ROOT` 推断集中根。显式环境变量和 task 固定根都必须与当前入口根一致。根来源冲突或无法完成规范化核验一经发现，立即停止；之后不再对任一候选根或 `records/` 调用 `read`、`list`、`glob`、`grep`、shell/bash/execute、Git 或路径诊断工具来调查冲突。只报告此前已取得的根来源及路径值，不读取或复述记录内容，并返回 `$pdca`。冲突答复只用一行纯文本，不得用引号、代码块、表格或列表包装：`根来源冲突：<来源>=<路径> 与 <来源>=<路径> 不一致。已停止，未读取 records/，未产生候选。请返回 $pdca。`；无法规范化时只用：`根规范化核验未完成：<来源>=<已知路径> 无法核验。已停止，未读取 records/，未产生候选。请返回 $pdca。`不得附加状态清单、冲突原因展开、修复方案或未来步骤。
在构造路径前，逐项验证 `project_id` 与 `workspace_id` 是当前宿主可表示的安全单一路径组件：非空、非 `.`/`..`、非绝对/盘符路径、不含 `/`、`\`、NUL 或控制字符；不安全值不得规范化或改写后使用。然后以规范化 `PDCA_ROOT` 只检查唯一预期路径链：逐级确认 `records/projects/<project_id>/workspaces/<workspace_id>` 是无符号链接的普通目录，`project-context.md` 是无符号链接的普通文件；对该精确文件执行 path resolution，要求解析路径与预期路径完全一致且位于 `PDCA_ROOT/records/projects/` 下。可用 `lstat`/`realpath -e` 或宿主等价能力，不枚举目录。任一检查不可用或失败时，在 `read` 绑定文件前停止并返回 `$pdca`，不得尝试其他路径。
只用该来源直接构造路径 `PDCA_ROOT/records/projects/<project_id>/workspaces/<workspace_id>/project-context.md`，
并在上述路径检查通过后对该文件执行一次直接读取，再按[项目绑定契约](../../ontology/contracts/project-workspace.md)核对 ID、规范化根路径与只读
Git 快照。不得用 `glob`、目录枚举或按 `project-context.md` basename 搜索来定位或复核该记录；直接读取失败、记录不匹配、
根冲突或权限不足时停止并让用户回 `$pdca` 处理，不自动改绑。

该停止规则同样适用于读取本 Skill 指定的 authority/契约、路径预检和 Git 快照：任一必需工具调用因权限、策略、访问范围被拒绝，或宿主缺少所需能力时，停止当前 Assist 并说明受阻操作。不得通过 shell/bash/execute、其它工具或 Agent、替代路径或扩大范围重试同一读取/检查；不能读取必需规则或证据时不得继续生成候选。

不得 glob、列举或搜索 `records/projects/`、project 父目录或 `workspaces/` 父目录来发现“当前”绑定；不得读取其他绑定记录来猜测、消歧或补全身份，
也不得向用户披露无关项目路径。没有精确身份来源时，说明需要先由 `$pdca` 核验项目真实路径及两个 ID，
然后再显式调用 `$pdca-assist`。

身份核对后，records 读取限于该 `project_id/workspace_id` 对应的 workspace 目录及当前候选真正需要的引用；
不得列举 `records/projects/<project_id>/` 或其 `workspaces/` 父目录来检查其他 workspace。业务文件读取只限绑定记录中的
`TARGET_ROOT` 与明确获准材料。若会话 `cwd` 与 `TARGET_ROOT` 不同，只报告已知路径差异；必要时只解析路径本身，
不得列目录、读文件或在未绑定 cwd 采集 Git 状态。cwd 不扩大 Assist 的读取范围。

闭合范围判断只看是否有明确排他措辞，不看清单有几项：

| 当前请求/权威来源的表述 | 是否闭合 | 读取方式 |
|---|---|---|
| `Read-only target materials explicitly in scope for this probe are ...`、材料“in scope/已授权”、只读要求或候选数量上限 | 否 | 所列材料可读；仍按最小项目导航规则读取必要导航 |
| “封闭 allowlist”“只读取这些文件”“仅限以下来源”“不得读取清单外路径” | 是 | 不得为导航或反重复检查读取清单外文件、`ontology_root` 或 records；缺少事实标 `unknown` 并说明所需授权 |

不能把第一行解释成第二行。非闭合读域仍不得扫描整个 ontology/source tree/history。

封闭 allowlist 中的业务文件读取路径，必须逐字使用已读取绑定记录的 `target_root` 值，并仅拼接清单中的相对文件路径；调用 `read` 前核对完整路径前缀与绑定值逐字符一致。不得凭记忆重输根路径、从 cwd 推导或试探日期/目录变体。任何 `read` 调用失败后，本轮 Assist 立即停止文件读取并报告该次精确路径与错误；即使你认为原因是自己输入笔误，也不得改正后重试、改猜相邻路径或换工具重读。下一次尝试须由用户发起新的 Assist 请求。

采集并报告路径/环境事实时，shell 输出必须逐项带标签（例如 `PDCA_ROOT=...`、`TARGET_ROOT=<unset>`、`PWD=...`），不得用多条无标签输出按位置推断变量值。空值或 `<unset>` 只表示该环境变量为空/未设置；不得把相邻的 `PWD`、`PDCA_ROOT` 或绑定字段当作环境变量值。业务 `TARGET_ROOT` 的权威值始终来自已核验绑定记录；若检查了同名环境变量，须与绑定字段分开报告，不能用环境变量替代绑定值。

只读 Git 快照必须在 `PDCA_ROOT` 与获准的绑定 `TARGET_ROOT` 分别执行项目契约规定的
`GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD` 和 `GIT_OPTIONAL_LOCKS=0 git status --porcelain`。
不得用未设置 `GIT_OPTIONAL_LOCKS=0` 的 Git 状态命令采集快照；TARGET_ROOT 不是 Git 仓库或命令失败时只报告事实。
声称根路径已规范化、没有符号链接别名或互不重叠前，必须实际取得 `PDCA_ROOT` 与 `TARGET_ROOT` 的只读规范化路径结果
（例如 `realpath -e` 或宿主等价能力）。仅字符串不同不能证明规范化后不重叠；工具不可用或解析失败时将该结论标 unknown，
不得声称执行过未发生的路径检查。比较 cwd 时最多解析路径本身，不检查未绑定 cwd 内容。

只读取当前候选真正需要的项目导航、相关 records 与获准业务材料；不扫描其他项目，
不默认遍历整个 ontology/source tree/history。候选依赖已有 task 的阶段、待回应请求或恢复连续性时，
才按 [entry-recovery](../../ontology/contracts/entry-recovery.md)读取该 task 的必要状态。

## 候选

从以下视角中只输出**有事实依据**的项，每个最多一个、总数最多四个：

- **任务地图**：实际 task/phase、明确依赖或待用户事项；
- **项目上下文**：与当前目标直接相关的绑定、源码、文档或 records 缺口；
- **证据审阅**：现有 evidence 与固定 AC/oracle 的具体缺口；
- **协作交接**：原 Agent、待回应请求或固定 deliverable/interface 的交接缺口。

四个视角不是输出配额；没有独立、可行动的缺口时可以不输出该视角。“无活动 task”或“无交接对象”本身只是状态事实，不单独构成候选，也不得仅为覆盖视角而重复呈现。协作交接候选必须有允许读取的证据表明交接确实待发生，例如明确待回应请求、具名接收方、固定 deliverable/interface 中写明的接收或验收义务，或 phase/event 中待原 Agent 处理的事项。单独存在一份草稿/未跟踪文件、缺少写入授权、目标目录不是 Git 仓库、没有活动 task，均不构成待交付或交接义务；不得把这些事实拼成协作候选。读域中没有上述正面证据时省略协作视角，或把相关事实标为 unknown。

每个候选只写：事实依据、建议动作、影响对象、继续所需授权。发现新的 ontology responsibility 时，只说明应回 modeling 形成 EVOLVE/TREE/NODE candidate；经 Modeling Check/Act 固定为 formal node 后，才可由 DECOMP 形成 task seed。Assist 本身不创建任何结构。

只对当前候选做反重复检查：获准读域已有等价实现/决定时优先复用；同一候选已有明确拒绝/wontfix 时说明原因，
除非用户重提或事实变化不再推动。无法从最小读集判断时标 unknown，不扩大扫描来“证明没有”。

报告 Git 快照时区分 HEAD 与工作树状态。比较记录与当前 porcelain 时，无法逐项核对就只报告状态是否漂移，不估算文件数量；确需数量时只按原始 porcelain 行精确计数并说明计数对象。`??` 或修改状态只作为快照事实，不单独证明某路径必须纳入 Git 跟踪，也不单独形成候选；只有当前目标或固定任务明确要求版本控制/可恢复性，且存在具体阻塞时，才提出相应候选。

## 停止

展示候选后停止。创建 task、写记录/业务对象、发送交接、运行验证或启动 phase 都需后续明确用户操作；
Assist 不把建议、选择或“看起来合理”转换成授权。
