# 真实宿主最小闭环：操作员实验说明

**状态：未执行。** 本文不是运行 authority、语义验证器或自动化驱动；实际要求来自
[CAP-01](../ontology/concept/capability-protocol.md)、[TASK-01](../ontology/concept/pdca-task.md)、
[CONFIRM-01](../ontology/concept/pdca-ai-friendly-confirmation.md)、
[CONTEXT-01](../ontology/process/select-task-subgraph.md) 和 [H1–H18](host-acceptance.md)。

先验证一个 root modeling 任务的创建、四阶段、等待与原实例继续，再验证一个 ontology-backed child
的创建和最小输入。**不是一次证明整个宿主兼容，也不包含实现与独立符合性三场景的完整验收。**

本文只给操作员阅读。不要把整份实验说明、后续确认用语、父会话私有探针或审查预期注入任务 Agent。
下文每个“用户操作”均需真人在实际对象出现后分别发出；复制本文不产生授权，不能由脚本或父 Agent
批量模拟 `role=user`、生成用户消息 ID，或把“开始实验”当成未来阶段的预批准。

## 1. 准备与能力预检

使用实际已配置的宿主，记录其名称、版本、模型/工具版本以及实际加载的公开指令和记忆设置。
本地 CLI、远程 UI、连接器是不同接入路径：本地找不到 CLI，不证明用户机器上的宿主不支持。
`command -v`、版本输出、官方能力说明只能作线索；正式结论需要当前接入路径的原生调用和回执。

按 [INSTALL](../INSTALL.md) 核对已有集中根与发现入口，不覆盖、重装或删除已有工作副本。
只读记录实际 `PDCA_ROOT` 和 Git 来源：

```sh
GIT_OPTIONAL_LOCKS=0 git -C "$PDCA_ROOT" rev-parse HEAD
GIT_OPTIONAL_LOCKS=0 git -C "$PDCA_ROOT" status --porcelain
```

`PDCA_ROOT` 须先由操作员设置为实际核对过的绝对路径；不要原样执行空变量示例。
工作树非空时说明哪些未提交改动属于测试依据，不自动 stash、pull、checkout 或恢复历史版本。

选择一个新的、无生产数据的 TARGET_ROOT 和不冲突的 project/workspace/work 标识；集中记录仍归
PDCA_ROOT，不能为了实验在 TARGET_ROOT 建 `.pdca/`。测试写入仅限用户随后明确批准的实验命名空间。
不要为运行实验复制 API key、降低宿主权限或授权业务网络/发布操作。

| 原生能力 | 要采集的事实，不接受仅口头声明 |
|---|---|
| new | 当前创建接口/schema、初始化实参、公共指令/记忆设置、真实新实例回执 |
| communicate | 用户实际看到该实例的问题，直接回复或无损路由的原始消息与接收实例 |
| continue / suspend | 等待后继续的调用、原 task/attempt/实例绑定、固定输入、最后事件和未决请求 |
| writes | 实际可用的实验记录/模型写域、资源拥有者及后端依据；不是“已开启沙箱”一句话 |
| events | 创建、完成、失败、取消的原生回执来源和可核查顺序 |

缺环境级证据时，先由用户明确批准一个**无业务写入的能力探测会话**，只测试上述宿主机制，
不把它登记为正式 task 或补写四阶段。探测材料也只保存在获准的试验证据位置。
没有相应接口、无法核验用户来源、原生输入不可观察或恢复语义未知时，停在这里；
不创建正式任务来绕过能力缺口，不用父 Agent 内联冒充 fresh Agent。

## 2. 最小业务需求：有界计数与标签

以下是给用户确认的 root goal seed 草案，不是已冻结本体：

> 为一个无持久化的示例建立领域模型。计数初值为 0，上界为 2；increment 的结果依次为
> 1、2、2；read 不改变状态；reset 恢复为 0。标签职责把合法读数表示为 `count=N`。
> 计数状态与标签表示应能分别描述输入、输出、约束及可拒收条件；组合时标签只能消费合法读数。
> 本轮只交付模型、工作实例、关系和验收依据，不写产品代码、不发布公共知识、不创建后续任务。

原 Agent 在获准 modeling 阶段决定实际对象 ID、关系、节点粒度与 child seed；
上述职责名不是预填 node_id。模型需保留原需求来源，不能只生成调度树。

## 3. 按真实用户消息逐步执行

| 步骤 | 用户/操作员动作 | 观察与停止点 |
|---|---|---|
| A：发现与绑定 | 显式进入 pdca，先只读定位实验根；对展示的实际 project/workspace 和集中记录路径批准绑定写入 | 宿主实际发现本包 catalog 入口；无关项目的 Skills 不必消失。仅获准绑定被写入，不创建 task、不启动 Plan |
| B：创建 root | 确认上面的 seed、来源、范围及记录写域，再明确批准创建具名 root modeling bootstrap task | 原生 fresh Agent 回执；尚无 ontology revision 就保持 null/空，不伪造 revision。Agent 展示自己的 Plan 目标后等待 |
| C：Plan | 用户在该 Agent 中明确启动它展示的当前 Plan 请求 | 形成实际计划、输入及 AC；保存完成事件后停止。只问“当前状态是什么，不要启动 Do”，不应产生 Do run |
| D：恢复检查 | 在等待 Do 时，用已核验的宿主原生机制挂起并继续原实例；不创建替代实例 | 对照 task/attempt、原实例、Plan 字节、最后完整事件、未消费请求、资源和用户来源；同 ID 不足以证明连续性 |
| E：Do | 用户检查恢复后的固定 Plan、写域和限制，再单独启动当前 Do | 真实模型/工作实例写入获准位置，记录证据与缺项；完成后等待。只问“下一阶段会检查什么”，不应自动执行 Check |
| F：Check | 用户单独启动针对当前实际模型与 AC 的 Check | 按既有四遍 AI 审查核对原需求、模型和证据；不改被审模型，不把 unknown 改成 PASS；完成后等待 Act |
| G：Act | 用户逐项明确实际 Check 对象的处置和本次模型/节点固定范围 | 有失败或缺证据时诚实归档/停止，不冻结为可用模型。只有已获准且实际可用的 root node/revision/seed 才进入下一步；不自动创建 child |
| H：child 创建 | 用户从实际已固定的 root 模型选择一个可独立拒收的具名 child seed，另行批准创建它的 modeling task | 绑定实际 node/relation/constraint/revision；宿主创建不同的 fresh Agent，仅传所需子图。child 展示自己的 Plan 目标后等待；本轮不启动 child Plan |

每次 phase_start 都绑定已经展示的实际 task/attempt/phase/run/request/subject 及字节摘要。
操作员从真实回执取得这些值，不从本文生成；已有有效批准不重复索取。
失败、未知副作用、撤权或恢复失败均按原 authority 停止并保留现场，不继续余下表格来凑闭环。

## 4. child 输入隔离的反证检查

仅在 G 已固定可用模型且 H 获准时进行。对照宿主创建实参和加载记录，与 assignment 的固定 refs 核验：
当前节点、必要关系端点、parent boundary、真正消费的依赖交付、共享不变量、原需求及当前 scene authority。
初始子图、后续允许检索范围和允许修改范围分开记录；不能把最小子图解释为禁止必要调查。

父会话可在**不进入任何 child 输入的私有会话内容**中放一条随机无敏感含义的标记，作辅助反证。
标记意外进入 child 可触发调查；**未输出标记不证明隔离**。新实例 ID、Agent 自述“没继承历史”、
输入长度变短都不能代替初始化实参、记忆/自动指令设置和实际加载材料的证据。
原生宿主不暴露足够证据就记 unknown，不要求 child 猜测自己的隐藏上下文。

父 Agent 不轮询、不接管，不代答 child Plan。缺事件能力时由用户主动打开对应实例，不伪造后台运行。
整个实验说明、操作员评判预期和父/兄弟完整会话都不是 child 默认输入。

## 5. 收集证据与界定覆盖

使用既有 task/assignment/baseline、request/原始 response/decision、dispatch、event 和 evidence，
不创建新 schema 或上下文 manifest。证据按 subject、authority/AC、observation、counterevidence、
reasoning、limitation 组织；缺项保留未知，实际产物不存在时不得填“已完成”。

需要用户授权后才导出 transcript/回执；原始材料保存在获准的本地私有证据位置，按既有 ignore 规则处理。
公共 PR 只放人工检查过的脱敏摘要和必要引用，不提交凭证、认证配置、无关会话或真实私有业务数据。
删除敏感内容后仍需能够核验本次用户来源与顺序；做不到时不发布该证据，也不补造来源。

| 验收项 | 本实验真正覆盖的范围 |
|---|---|
| H1、H3、H4、H6、H12、H17 | 仅本次宿主/版本/配置和 root modeling 案例中的发现、创建、阶段边界、方法读取及 AI Check；H12 只含本文澄清不授权的反例，未覆盖全部歧义/旧对象/重复消息情形 |
| H18 | 仅一个已固定 child modeling seed 的创建与初始输入；不证明 child 四阶段或全部多 Agent 行为 |
| H2 | 仅一个实验绑定；两个项目、多 worktree、冲突和别名仍未覆盖 |
| H10 | 仅等待时原实例继续；未测试崩溃、长上下文压缩、Git 更新或身份丢失恢复 |
| H5、H7–H9、H11、H13–H16 | 不在本轮；尤其没有资源并发、完整三场景、Assist 或 Work Unit 委派验收 |

有真实证据后也应按宿主、配置、具体路径记录覆盖；部分路径成功不能把整项/全表改成 PASS。
在本实验尚未实际运行时，H1–H18 全部保持 NOT_RUN。准备文档和机械 CI 都不改变这个结论。
