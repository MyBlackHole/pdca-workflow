---
schema: pdca.project-workspace-contract/v2
extension_revision: cross-project.2
protocol_revision: 3.4.11
authority_refs:
- CONTRACT-01
- RESOURCE-01
- EVIDENCE-01
- CONTEXT-01
adoption: explicit_per_work
---

# 跨项目双目录契约

这是[CONTRACT-01](../concept/pdca-execution-contract.md)、[RESOURCE-01](../concept/resource-ownership.md)、[EVIDENCE-01](../concept/pdca-evidence.md)与[CONTEXT-01](../process/select-task-subgraph.md)在跨项目环境的应用投影，不另立门禁或第29项权威。只对明确采用此附件的工作适用；旧单目录工作不自动迁移。采用对象固定本附件版本与摘要，不能只写“当前最新版”。

## PX-ROOT：入口cwd推导一次，之后固定双根

新工作的TARGET_ROOT为入口真实cwd。PDCA_ROOT只读取同名环境变量：未设置或空字符串取入口cwd；非空值相对入口cwd解析后取真实目录。先核验入口/规则/发布清单/本契约存在、可读且版本匹配，再形成绑定。非空错误配置必须报错，不能回退、自动安装或猜测其他目录。只记录该变量，不记录整份环境；不eval或隐式展开变量文本。

PDCA_ROOT与TARGET_ROOT规范化后相同则root_mode=shared，互不相同且互不包含则root_mode=split；严格嵌套仍不支持。根别名指向同一实际目录归为shared，不得报告独立隔离。两类根在绑定和任务上下文中保持显式值，用户不需要再配置TARGET_ROOT。

后续cd不重新定义目标。新Agent和恢复沿用父派发/原任务的固定context，不以自己的默认cwd或当前环境覆盖它。新工作才重新读取入口环境。Git toplevel与TARGET_ROOT分开；子目录启动不会自动扩大为全仓库，必须固定其所属Git身份和范围。元数据读范围不等于源码写范围。

捕获入口值只解决定位，不授予访问或动作许可。通用全局加载提示见[bootstrap](../../bootstrap/global-entry.md)，需要宿主真实加载一次；纯环境变量不能凭空触发所有Agent读文件。已有本地指导仍需按宿主规则读取。

一个attempt默认绑定一个目标。资料路径保持PDCA_ROOT/records/<task-id>和records/works/<work-id>；项目索引只引用原记录，不创建第二份活动记录副本。

## PX-ENTRY：实际加载与路径锚定

入口加载补充见[entry-check](../../bootstrap/entry-check.md)。已加载的全局规则将本会话非空 PDCA_ROOT 视为启用选择；没有加载规则的宿主不因此自动执行。USE-PDCA 后必须明确交接到 ontology/README 和当前规则，不能期待外部目标自动发现本库 AGENTS。用户明确不采用时不得强制启用。

协议正文中的 ontology/...、templates/...、tests/... 和新 records/... 是 PDCA 根内布局，不相对开发 cwd。Markdown 相对链接锚定链接所在文件，已有记录的 ref 保留原语义。开发命令保持固定目标 cwd；根不随读取动作改变。该补充不迁移旧绑定、不改 v2 双根/身份语义，不增加业务授权。

<a id="px-id"></a>
## PX-ID：标识内部生成，不增加用户配置

先按规范化根、target_kind、完整target_identity查找可唯一核验的旧workspace绑定；命中则复用其既有ID，不因新的自动命名规则改写旧目录。旧绑定冲突、已占用ID身份不同或歧义时阻断，不覆盖。

没有旧绑定时采用local-root/v1默认标识：project_key为Git common_dir，非Git为目标真实根；workspace_key为目标真实根。project_id=`p-`+SHA256(UTF-8("pdca-project/v1\0"+project_key))前20个十六进制字符；workspace_id=`w-`+SHA256(UTF-8("pdca-workspace/v1\0"+workspace_key))前20个十六进制字符。此处\0表示单个NUL字节，不是反斜杠与0两字节。

短ID只是本PDCA库内定位键，必须同时保存并比较完整身份；它不是全球仓库身份/授权，也不证明哈希不会冲突。不同linked worktree共享project_key但有不同workspace_key；同名目录不同路径不合并；移动目录生成新绑定并显式接续，不能偷偷更新旧路径。自定义显示名称只作标签。

本附件的新路径对象为 `{root: pdca|target, path: 根内相对路径}`。禁止裸相对路径、绝对 path、`..`、空组件、反斜线/盘符混用；cwd 可以用 path="."。原模板的 ref 仍相对记录文件或原显式固定根解析，不能把所有旧 ref 重新解释为相对 cwd。新路径对象不是新的 URI 执行器。

根身份解析后，每次动作前仍须复核实际路径、链接/挂载别名和写域。新文件检查全部已存在父组件与最终目标；拒绝未授权符号链接或多硬链接写入。通用检查的 realpath/文件身份对比不是原子沙箱，不证明不存在检查后替换，保证等级仍由宿主证明。共享 Git common-dir、远程服务及设备作为另外的实际资源登记。

## PX-STORAGE：流程资料只写 PDCA，业务产物只写目标

binding/项目索引、任务/基线、目标定义/设计、测试规范、确认、issue、日志、审查、原始观测、证据快照、交付清单与导出补丁均保存在 PDCA_ROOT/records/ 的批准范围。SOURCE/TARGET 只保存批准的源码、产品测试代码、产品构建输出，以及明确要求修改的具体产品文档。按用途而不是扩展名分类。

split模式目标项目内默认不生成 .pdca、records、任务报告或复制的规则；shared模式复用自身records，不再创建一套资料库。shared的目标产品写域不得与records及Git元数据重叠，输入快照应排除当前记录输出，避免自包含。已有产品文档不自动迁移。工具在目标目录自动产生 junit XML/coverage 报告时，应优先配置输出到 PDCA 任务目录；不可配置的生成路径须预先声明为临时开发输出，保留实际副作用记录，归档证据后按授权清理，不能声称从未在目标生成资料。

split模式普通任务对 PDCA ontology/templates/tests 只读；shared自维护可把明确要求修改的规则/模板列为目标产品写域，但采用版本须先固定保留，不能改写本次基线或旧记录。能够写 PDCA_ROOT 不意味着有共享规则发布权。节点只能写自己获权的 task 区域；work/project 索引由已有宿主单写者更新，不赋予所有孩子共同写权。原始业务资料可能含敏感内容，按既有脱敏/访问范围保存；不自动 git add 或发布整个 records。

## PX-INPUT：工作树和初始修改属于输入

Git 项目区分 TARGET_ROOT、Git toplevel、per-worktree git-dir 与 shared common-dir；固定 HEAD、branch（detached 时明确 null）及实际状态。远端 URL、项目名、分支名不能单独证明身份。不读取凭据作为身份，不要求有远端。

初始状态保存 tracked/index/worktree 的差异、未跟踪文件列表以及验收必需的实际内容/摘要；忽略文件按输入依赖明确纳入或有据排除。不得执行 reset/clean/stash 或自动提交来换取“干净”基线。已有用户修改只作输入，不自动归属本任务；与本任务允许写域重叠时，先明确保留/修改意图再确认，不得无授权覆盖。

未使用 Git 的项目可以采用 target_kind=directory，固定路径身份及逐成员输入清单；不伪造 HEAD 或提交号，也不静默 git init。目录模式没有可取得的旧字节时必须保存必要副本，单有 hash 不够恢复。

固定基线是输入，不限制 Do 合法修改源码。每次测试绑定新产物摘要；检查点区分预期输出变化与外部 HEAD/分支/路径/版本漂移。目标 worktree 变更、基线身份漂移或写域扩大必须先阻断并按既有返工/确认规则处理；不能修改旧上下文来让检查通过。

## PX-BIND：派发、基线、运行与交付连成同一上下文

先写不可变 binding，再写 task 的 project-context；context.entry_context固定entry_cwd、pdca_root_source、pdca_root_input、有效双根和root_mode。二者都不能引用未来批准或未来 run。task 用已有 `extensions.project_workspace` 记录 context_ref/context_digest；baseline 用已有 resource_scope 中的两类资源条目和 constraints 正文固定同一 context 及其摘要；派发通过既有 capability-check 证据传递该上下文。不要向旧正式模板添加未经定义的顶层字段。

run 的 environment_ref 指向保存于 PDCA 的实际环境记录，记录相同 context_ref/digest、真实 cwd/argv、环境变化、输入/产物摘要与退出状态；不是把一个计划命令当成已执行。delivery 的固定产物清单记录目标 origin 与 PDCA 保存副本，两类路径不得互换。现场 patch 本身是资料，真正被测试的源码在目标工作树。

原有维护 formal profile 不会自动核验新附件；跨项目工作必须额外核验双根/写域/版本绑定，覆盖报告分别列出 not_run/unknown。创建 binding、目录或正确路径不产生 Agent、授权、PASS、冻结或发布资格。

## PX-EXEC：显式 cwd 与分离写权

开发读取/修改/编译/测试明确使用 TARGET_ROOT（或目标内批准子目录）作为 cwd，所有流程输出给出 PDCA 绝对位置。流程索引维护/证据归档明确使用 PDCA_ROOT；不能依赖上一个工具调用留下的 shell cwd。命令参数、重定向、生成器、缓存、Git 元数据及子进程的副作用均受写域限制，正确 cwd 不等于命令安全。

派发前核验宿主能读固定规则、写专属资料区、访问目标授权区，并能维持原有隔离/确认/控制保证。缺少任一必要权限则不在另一目录兜底写文件。Plan 探测副作用和共享 Git 元数据修改另行授权，业务批准不自动覆盖 PDCA 共享库。

不同工作树/开发根使用各自workspace_id；同一目录切换分支不自动换workspace_id，但必须处理当前任务HEAD/branch漂移。不同目录名或分支名不证明独立。多个工作共享实际目标时沿用 RESOURCE-01 的冲突与串行/排他规则。临时 Git worktree 的创建及删除不是自动接入步骤，需明确授权并作为新绑定登记。

## PX-RECOVER：资料归档、恢复与迁移

旧证据固定在 PDCA，可由目标源版本与副本/差异核验；同名活跃目标文件不能替代原字节。split时PDCA与目标各自提交，不宣称双仓库原子提交；shared时是一个仓库，仍按产品/资料精确路径和授权分别核对，不假装存在两个独立仓库；报告精确版本、差异与未提交状态，不用“两个最新版本”代替对应关系。目标目录不可用不应使已经归档的证据消失。

根路径移动、worktree 更换、并发写者变化创建新绑定/新接续事实；不倒填历史绝对路径、摘要、确认或写权。索引可更新定位，但旧对象仍不可变。可选工具定位链接不是业务写域，也不得在递归扫描源码时跟入；不自动移动已有 .trellis 等目录。

## 有限维护检查范围

独立附件的 project_workspace_check.py 核验真实本地目录、入口推导、Git 工作树/子目录定位、路径约束、批准路径集合、初始成员摘要和命令所声明 cwd/输出。它不执行被审命令，不认证用户/Agent/写权，不是运行器，也不解析任意 shell 的全部副作用。readiness 结果只代表这些机械检查；生产资格始终未由它证明。

## 版本采用

新绑定及上下文使用project-workspace/v2、project-task-context/v2与cross-project.2。v1历史绑定保留原双根分离规则；不把旧相等根错误追溯变成合法，也不覆写旧摘要。旧binding可继续按固定v1快照读取；迁移先保留其原契约，再按新工作实际入口生成v2绑定/上下文并引用接续事实。本文件 frontmatter 的 protocol_revision 表示它所属的当前发行投影，须与本工作固定的 protocol-release 一致；cross-project.2 表示扩展语义版本，v2 表示记录 schema，三者独立。历史绑定仍比较其原快照，不与当前磁盘上的发行号混比；本次仅修正发行投影，不扩大 v2 的授权或目录语义。

## 独立任务派发与并行资料区

采用[agent-dispatch.1](agent-dispatch.md)时，每个新任务取得自己的固定project-context并作为任务书输入；同一binding的双根可共享，task/attempt、记录区和写权不得共享。子Agent默认cwd、环境或另一项目的目录名不改变该上下文。业务只读采用固定输入快照；共享索引串行发布不意味着各任务的私有研究/记录也必须串行。

目标写域、临时输出、记录写域的实际新增文件均需纳入对应授权/范围；不能只声明一个报告路径却无限扩写同目录。发现旧范围不一致保留原事实，新的attempt核验自己的实际范围，不倒填旧授权。
