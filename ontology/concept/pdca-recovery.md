---
schema: pdca.asset/v2
id: ontology:concept/pdca-recovery
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.10
summary: 当前任务恢复与失败处置
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
dcterms_modified: '2026-09-14'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-transition
  - ontology:concept/pdca-task
  - ontology:concept/pdca-verdict
  - ontology:concept/task-control
  - ontology:concept/resource-ownership
  - ontology:concept/pdca-phase-status
---

# 恢复事实、控制状态与安全接续

## RECOVERY-01

恢复只读当前任务固定记录、可信control/dispatch/request-decision、transitions、基线、tests/runs、证据及显式授权的外部operation查询。不得读取其他任务活动对话猜进度，也不把宿主会话名字相同当原Agent恢复。

先读任务固定协议版本和CONTROL-01控制视图，检查记录写权、终止状态、时间域和资源保留。终止attempt不恢复成running；有stop_pending先完成安全停止，不被旧task快照覆盖。控制文件损坏或来源未知时禁止新副作用。

## 合法阶段链与快照

按(task_id,sequence)核对固定1—4边、实际前驱digest、基线/输入、写入者/准入证据和当时有效确认。无正常转换回执只表示未离开Plan，不能推断Plan未执行或业务从未发生。不能只看phase值或文件存在。

| 状态 | 处置 |
|---|---|
| 完整有效回执、快照旧 | 同一合法写入者或真实交接后的宿主修复快照到最后to；不再执行工具 |
| 快照超前、回执缺失/部分写 | 禁止推进，保留异常；核查实际提交，缺证不能补齐 |
| 同task同seq分叉 | 保留分叉并阻断；不按mtime/大小选一个 |
| 已consumed请求尚未反映在任务中 | 核对决策身份、当前控制资格，幂等消费已有决策；expired/取消后不得消费迟到消息 |
| confirmation通过后control已停止 | 停止优先，旧批准不能免除后续取消 |
| 工具/权限/环境改变 | 新CAP证据解除实际blocked_reason，原契约无变且原Agent可恢复才继续 |
| 原Agent无法恢复 | CONTROL-01安全终止，撤权并核查所有在途影响；新attempt必须新Agent |
| 外部调用结果未知 | 用operation_id和目标状态对账；无安全依据不盲重试；必要时隔离资源并保留影响 |
| archive/interrupted材料后来损坏 | 独立integrity记录隔离，不重开原attempt或修改旧失败 |

历史门禁核查当时固定对象，不用工作版conclusion后来增加的Act文字重算旧确认。过期构建、旧suite和输入版本不证明当前实现通过。

## blocked可恢复与终止不可复活

blocked不是取消：只在实际缺项补齐、宿主解除控制限制、资源/身份有效且未改变授权或期望时，由原绑定Agent继续原phase；新增范围/目标走REWORK-01新基线。stopping不能因迟到确认自动回running；termination真实生效后只能新attempt。

后继启动不以active=false或archive为唯一条件，而是STATE/CONTROL/RESOURCE/SCHED共同决定。原任务可以未完整PDCA而合法interrupted，必须保留取消来源和未完成阶段；不得为快点返工补造Act/Archive。

没有宿主事务时只声明已验证范围内的尽力恢复。外部operation的幂等与回执幂等分离，不能从恢复测试通过宣称生产断电安全。

## 历史异常的只读复核

使用[integrity-event](../../templates/integrity-event.md)记录当前实际看到的字节/摘要、缺失项、原报告声称、可证事实与unknown，以及受影响采用/冻结范围。旧task/response/run/manifest保持原字节；事件不是替代历史基线或终态证据。

旧材料有用但合法结束不可证明时，按证据范围作为candidate_reference而非可用交付。必须新执行的部分由新attempt和新Agent承担；后继仍需RESOURCE/CONTROL真实结清。不可恢复的旧版本/临时输出保留unavailable，不把当前重建样本叫原运行复现。

<a id="recovery-capsule"></a>
## 压缩后先恢复必要事实，不信摘要中的批准

压缩前可从原记录整理一段恢复导航，放在获权的现有工作记录或会话摘要中；不是新checkpoint、状态来源或确认对象。不能复制其他任务活动对话。它只保留以下指针及当时已知事实：

| 保留项 | 接续时重新核对什么 |
|---|---|
| 固定双根、协议/基线、task/attempt、Agent绑定 | 原始可读位置与摘要、真实原会话；不从当前安装版重建 |
| 最后合法转换、当前CONTROL/RESOURCE | 有效链、停止/撤权、当前写权；摘要的phase或旧批准不优先 |
| 当前目标、必需约束和适用规则指针 | 仍在上下文中的必要正文或重新读取；“曾经读过”不是免读证明 |
| 当前产物、suite/run和证据 | 版本是否适用、unknown/stale及尚未完成的覆盖 |
| 在途operation、待确认request/decision | 原ID及真实外部状态；未知先对账，不重发副作用 |
| 下一获权动作、停止条件及未决问题 | 根据上述事实重新决定；摘要中的行动建议不是授权 |

缺任一当前动作所必需事实，先只读取证或报告具体阻断。无可访问原文时不能靠润色摘要补齐；压缩丢了一个安全约束也不能以“其他信息完整”继续。恢复定位完整后，仍按CONTROL/RESOURCE与合法阶段链接续，不因形成此导航就声称已恢复运行。

<a id="recovery-native-binding"></a>
## 原生继续：先比对期望绑定，再允许后续动作

恢复请求固定原 task/attempt、agent/conversation 和当前阶段/基线/控制/资源指针，保存原生继续调用及返回。不从名字、目录或模型自述推断恢复；以原生身份映射与实际可恢复状态共同核对。允许宿主更换 OS 进程或压缩本任务历史，但不得因此丢失必要状态、导入其他任务历史或重解释旧确认。

- 返回原身份且状态/控制可核验：按原合法链继续；不重复业务操作或重新请求已合法消费的确认。
- 返回新身份或声明新建：拒绝作为恢复，原 dispatch 保持原字节绑定；新产生实例不获正式写权，按 CONTROL/RESOURCE 停止、隔离并核查实际副作用。
- 返回原 ID 但状态不足、未返回或结果未知：保持阻断，查询原会话；未知不能记已终止或安全释放。确认不可恢复后才安全终止，并按新 attempt 准入接续。

恢复期间有停止/撤权，以当前控制为准；迟到响应不恢复写权。主 Agent 不补 Plan/Do/Check/Act。若实现不支持安全的原会话继续，必须报告 full_pdca 缺项，而不是通过每阶段 fresh spawn 凑齐流程。
