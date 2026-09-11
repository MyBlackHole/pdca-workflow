---
schema: pdca.asset/v2
id: ontology:concept/capability-protocol
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.10
summary: 宿主能力：隔离、独立交互和真实测试
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-14'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-task
  - ontology:concept/work-tree-scheduling
  - ontology:concept/task-unit-test
  - ontology:concept/runtime-transition-coordinator
  - ontology:concept/task-control
  - ontology:concept/resource-ownership
  - ontology:concept/work-dependency-graph
capability_spec:
  checkpoints:
  - pre_dispatch
  - plan_probe
  - plan_to_do
  - before_effect
  - before_transition_commit
  - recovery
  - environment_change
  changed_capability_default: deny_affected_actions_and_revalidate
  simulation_fallback: false
---

# 宿主能力与动态核验

## CAP-01：名称是能力契约，不是假定API

必须记录实际tool/backend、status=available/missing/unknown、授权scope、真实evidence_ref、checked_at及计时来源、环境/版本和limitations。工具存在不代表当前调用获授权；不猜API、不增加adapter或Registry，不把fixture当生产能力。

| 核验时机 | 必须成立的能力/范围 | 缺失处理 |
|---|---|---|
| 派发前 | fs定位/私有记录写入、spawn_fresh隔离、autonomous/resume身份、task.interaction/user.confirm、host事件排序、integrity.digest；已授权wait-policy；槽与记录区取得 | 未执行保持blocked_unexecuted；spawn结果未知先查，不盲建 |
| Plan中每个有副作用的探测前 | 当前探测明确授权，RESOURCE-01覆盖实际资源；业务实现仍不得提前执行 | 只允许安全规划/记录，禁止被阻断探测 |
| Plan→Do | 实际业务工具和tests.execute/observe可用；契约要求的写入隔离/排他等级；固定依赖图与准入证据 | 必需执行能力缺失不能开Do；不能把not_run作为Plan准入豁免 |
| 每次受控动作及阶段提交前 | owner/epoch/授权/控制视图仍有效，检查scope未漂移；实际副作用目标与预约一致 | 停新动作；必要时stopping，对账在途操作 |
| 恢复、宿主/模型/权限/工具/存储变化 | 更新capability-check证据，核对原绑定、原基线与未决操作 | 同契约同Agent可按CONTROL解除blocked；终止或语义变更用新attempt |

真实整树运行需要host.schedule/host.events提供节点前沿、真实固定交付通知、工作索引单写者；这是事件与身份服务，不是父Agent阶段批准。真实用户确认必须独立定位来源，不能凭Agent自填authority:user。

## 保证等级

RESOURCE-01定义isolated_private、cooperative_serial、enforced_exclusive。默认的single_writer_best_effort仅在用户任务允许合作式单写者、宿主实际能遵守且没有未隔离共享副作用时使用；强一致、可靠取消、不可逆共享写或跨文件原子性要求未获证明时必须停止，不静默降级。

没有排他后端可选私有工作区+串行发布，或可验证的单调度者串行且无超时自动接管；仍然每节点新Agent完整PDCA。缺隔离/独立交互不能改由父Agent模拟。无法证明旧执行者不再写时，不抢占资源。

## blocked解除协议

能力恢复必须来自新的实际证据，由可信准入机制记录限制解除，Agent核验后继续原phase；不能直接把missing改成available。原授权不能覆盖新增资源或不同目标语义。测试能力在Do丢失但记录/确认仍安全可用时，可记录真实失败并进入Check，不重新开展被阻断测试，也不支持成功交付。

期限需要可信时钟/事件排序；无此能力则只能采用已授权explicit_wait，而非伪造超时。宿主身份或时钟域变化先阻断消费并核对。能力探测本身不可执行未授权的破坏性动作。

模板：[能力证据](../../templates/capability-check.md)。源级机制参考和适用限制见[技术来源](../../tests/protocol-regression/sources.md)。

## 派发前分开核实三种能力

| 能力 | 核验方式与边界 |
|---|---|
| 内容完整性 | 在授权临时对象上实际计算摘要、重读并变更字节验证不一致；记录算法/工具/输出。无签名、无事务后端不是省略哈希的理由。 |
| 消息来源与确认消费 | 核实当前宿主能路由具名task/attempt/object，提供真实消息来源与单一消费决策；不能用自建fixture证明用户已批准。 |
| 控制排序与写入保证 | 按当前实际后端/合作式范围核实资格、停止、交回与竞争边界；哈希不提供身份、CAS或原子事务。 |

能力检查先于正式派发；共享一个交互界面合法，不要求每个Agent有独立窗口。批量确认只能覆盖当时已列明的对象与摘要。原生工具提供所需事实即可，不要求新服务、adapter、签名系统或工作流执行器。无法证明的能力记missing/unknown，禁止乐观降级。

<a id="cap-full-agent-and-parallel"></a>
## 全流程 Agent 与并发能力分开核验

先通过宿主实际可用的工具发现/原生描述核验能力，再在授权的隔离探测范围观察；不能未经查找就断言“不支持子 Agent”，也不能用工具名字猜测功能。记录以下不同能力的 actual_tool、scope、status、限制与原始证据，沿用 capability-check.checks，不另加服务：

| capability | 必须核实的事实 |
|---|---|
| spawn_fresh | 新上下文、真实唯一 Agent/会话身份及允许导入的固定输入；无整段主/兄弟活动对话继承。 |
| task.full_pdca | 同一绑定能负责 Plan/Do/Check/Act、保存自己的实际产物、跨等待继续；不是只返回摘要的 Do-only。 |
| task.interaction / user.confirm | 每个 task/attempt 可独立收发并消费当前对象的真实确认；统一界面不由父代答。 |
| host.dispatch_async | 创建被接受后返回可跟踪的在途句柄，可在前一任务结束前提交下一任务；未知结果可查询。 |
| host.capacity | 活跃会话、在途创建和可运行执行位的真实上限/计量；unknown 不能填成计划并发数。 |
| host.events / host.schedule | 原生事件可排序、工作索引单写者、局部唤醒、结束补位及重复事件去重。 |
| fs.task_scope | 每个子任务继承固定双根、可访问目标获权区、只写其私有资料区；宿主不共写任务正文。 |

full_pdca 能力不足阻断正式任务；parallel 能力不足与之不同：按授权允许的容量运行并诚实报告限制，不能把未并行说成通过并行验收。并发探测采用有界屏障及明确测试信号，不伪造真实用户确认、不创建未经授权的业务任务。进程/线程并发只能测试调度模型，不证明新 Agent 隔离或完整 PDCA。

能力证据在受影响环境变化后失效并复核；根和孩子同样适用。详见[直接派发入口](../../bootstrap/dispatch-guide.md)和[记录关联](../contracts/agent-dispatch.md)。

<a id="cap-environment-and-call"></a>
## 环境核验可以复用，每次调用事实不能省略

沿用 capability-check 的 environment_revision、checks、evidence_ref/digest、limitations 和 supersedes_ref；不增加隔离证书或平行 schema。

**环境级：**首次采用或相关变化后，在已授权的隔离范围核验原生新建/继续、历史继承、公共规则/记忆、确认路由和写域。记录宿主/工具版本、模型、权限、配置、存储与身份域及适用范围。已核验环境未变时可引用同一依据；相关变化使受影响能力失效，须补新证据。文档/源码只说明候选机制，不是本机已验收。

**调用级：**每次新建核对实际参数、输入清单和原生结果，关联本次 task/request；每次继续核对期望与实际 agent/conversation、状态连续性、控制与写权。原始日志需在获权位置可定位；回执缺身份或输入事实时记 unknown，不能让 Agent 自述补齐。环境 PASS 不能替代本次调用成功，亦不授权新增动作。

历史继承开关、前后台等待、会话持久化、文件写入隔离分别核验；某一项成立不推出其他项成立。容量为1可以依法串行不同独立任务，不等于并发验收通过。缺能力不内联降级为主 Agent 正式执行。当前相关分支见[四路径](../../bootstrap/dispatch-guide.md#dispatch-four-paths)。
