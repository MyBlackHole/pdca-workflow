# 从目录定位交接到正式流程

本页是跨项目加载导航，不是第29项权威、额外批准门禁或新的执行器。原 TASK/CAP/RESOURCE/CONFIRM 保持不变。首次工作使用已捕获的双根；恢复使用原固定上下文，不重新从环境推导。

## 确定的读取顺序

下表数据是维护工具与入口共同使用的导航读集。所有 path **相对固定 PDCA_ROOT**，不要相对当前开发 cwd 打开。已实际读过同一版本的文件可以复用读入事实，不递归回读 USE/AGENTS，也不一次加载全库。

```json
{
  "schema": "pdca.entry-read-plan/v1",
  "revision": "cross-project.2-hotfix.3",
  "reference_base": "pdca_root",
  "required_reads": [
    {
      "id": "usage",
      "path": "USE-PDCA.md",
      "purpose": "entry_directory_contract"
    },
    {
      "id": "workspace",
      "path": "ontology/contracts/project-workspace.md",
      "purpose": "root_and_storage_contract"
    },
    {
      "id": "release",
      "path": "protocol-release.md",
      "purpose": "pin_protocol_snapshot"
    },
    {
      "id": "ontology_entry",
      "path": "ontology/README.md",
      "purpose": "workflow_handoff"
    },
    {
      "id": "authority",
      "path": "ontology/concept/pdca.md",
      "purpose": "authoritative_workflow"
    },
    {
      "id": "phase_entry",
      "path": "ontology/process/pdca-flow-model.md",
      "purpose": "new_work_or_resume_routing"
    },
    {
      "id": "load_map",
      "path": "ontology/LOAD-MAP.md",
      "purpose": "current_event_rule_navigation"
    }
  ],
  "dispatch_reads": [
    {
      "id": "task",
      "path": "ontology/concept/pdca-task.md"
    },
    {
      "id": "capability",
      "path": "ontology/concept/capability-protocol.md"
    },
    {
      "id": "scheduling",
      "path": "ontology/concept/work-tree-scheduling.md"
    },
    {
      "id": "control",
      "path": "ontology/concept/task-control.md"
    },
    {
      "id": "resource",
      "path": "ontology/concept/resource-ownership.md"
    },
    {
      "id": "confirmation",
      "path": "ontology/concept/pdca-ai-friendly-confirmation.md"
    },
    {
      "id": "dispatch_guide",
      "path": "bootstrap/dispatch-guide.md"
    },
    {
      "id": "dispatch_contract",
      "path": "ontology/contracts/agent-dispatch.md"
    }
  ],
  "required_entry_observation": [
    "target_root",
    "pdca_root",
    "records_root",
    "protocol_revision",
    "read_refs",
    "entry_status",
    "blockers"
  ],
  "entry_statuses": [
    "not_loaded",
    "entry_blocked",
    "rules_loaded",
    "dispatch_blocked",
    "awaiting_confirmation",
    "ready_for_current_action"
  ],
  "not_proven": [
    "host_global_instructions_loaded",
    "fresh_agent_isolation",
    "filesystem_tool_permissions",
    "phase_confirmation",
    "formal_pdca_completion"
  ]
}
```

按 required_reads 顺序读取并固定本次版本；release 自身的摘要由外层保存，不能要求清单含自身摘要。按 LOAD-MAP 与阶段入口读取当前适用规则；dispatch_reads 是派发前的必要入口，不代表其它阶段规则可以省略。不要从示例中复制 PASS、身份或批准。

## 四类路径不可混为 cwd

| 输入形式 | 定位基准 |
|---|---|
| 本页 path、协议布局 ontology/...、templates/...、tests/... | PDCA_ROOT |
| 正文要求新建 records/<task>/... | PDCA_ROOT/records，而非 TARGET_ROOT/records |
| Markdown 链接如 ontology/README 中的 concept/pdca.md | 链接所在文件的父目录 |
| 源码 src/...、产品测试及开发命令 | 固定 TARGET_ROOT 或其批准子目录 |
| 已固定记录的 ref | 该记录既有显式 ref_base 或所属文件；不重新解释历史引用 |

开发工具 workdir 保持目标目录；读取 PDCA 采用绝对文件名。为工具切换 cwd 时必须显式传递，不能令一次 cd 改写上下文。路径声明不是 OS 沙箱，仍按 RESOURCE 检查真实路径及授权。

## 必须输出实际状态，不能把说明当作启动成功

给用户一段短的真实观察，包含 required_entry_observation：开发根、PDCA 根、资料根、版本、已读文件、状态及具体阻断原因。这可以是会话消息，获权后才保存到 PDCA 记录区；它不是 task、批准或终态。

- `entry_blocked`：环境/cwd不可取得、路径不存在、入口或固定引用损坏。说明缺的变量/文件/摘要，不换根。
- `rules_loaded`：读到了本次必需规则；不代表可派发。
- `dispatch_blocked`：规则已读，但 CAP/RESOURCE 所需真实能力尚未取得。逐项标明缺失/未知及现有观测，不能仅因存在跨目录就假定无权限，也不能把真实不支持当作已支持。
- `awaiting_confirmation`：对象已固定，等待原机制要求的真实批准，不代签。
- `ready_for_current_action`：仅对当前获权动作成立，不代表整项工作/所有未来阶段已获批。

没加载全局入口是 `not_loaded`，外部只读工具不能替宿主认证它。用户只说“无法使用”而无日志时，不能把任一可能层级宣称为已确认根因。

## 诊断与限制

独立附件 `pdca_entry_doctor.py` 在本进程 cwd 下观察入口、读集与发布摘要；默认不创建文件，显式 `--probe-record-write` 才在已存在的 PDCA records 内创建并删除一个唯一探测文件，不写目标。报告只对该进程的权限成立，不证明 Agent 其它文件工具、确认消费或独立上下文。

工具输出不是 Agent 已按流程读取文件的证据，更不是正式 PDCA 运行。详细操作见[跨项目故障定位](../examples/cross-project/troubleshooting.md)。

<a id="role-actions"></a>
## 规则加载后：按角色与事件只选一个入口

先复核当前 CONTROL/RESOURCE 停止、撤权和在途事实。下表只导航，不替代 required_reads、dispatch_reads 或 LOAD-MAP 的适用规则；同一摘要已读可复用，变化必须重新核验。

| 可观察条件 | 现在做什么 | 必须看到的结果／停止边界 |
|---|---|---|
| 已有 task，收到继续／恢复／重复消息 | 先读取 [RECOVERY](../ontology/concept/pdca-recovery.md)及[原生绑定核对](../ontology/concept/pdca-recovery.md#recovery-native-binding)，按[恢复导航](../ontology/concept/pdca-recovery.md#recovery-capsule)重读必要事实、控制与写权；再选择真实阶段 | 缺绑定或状态有冲突先报告具体缺项；不换根、不另 spawn、不从目录或摘要猜阶段 |
| 当前是宿主，尚未提交或有新就绪任务 | 读 dispatch_reads 与[派发动作](dispatch-guide.md)，核验真实原生能力和容量后提交完整任务 | 分别报告 pending、accepted（真实句柄）、unknown、未派发原因；unknown 查同一 request，不盲目重建 |
| 已有真实节点绑定，phase=plan | 读 [Plan](../ontology/process/flow-plan.md)，固定目标／seed、验收／oracle、写域和预算；拆分用[拒收见证](../ontology/concept/task-decomposition.md#decomp-rejection-witness)，提出当前 Plan 确认 | 当前请求合法消费且门禁成立才进入 Do；派发许可不代替阶段确认 |
| 同一绑定，phase=do 且有合法 Plan→Do 回执 | 读 [Do](../ontology/process/flow-do.md)，在原授权内实施并运行测试；失败保留原 run，再按预算修复，最终全必需回归 | 记录真实产物摘要、命令／观测、退出状态与 AC→case→run；完整失败也可进入 Check，不修改 oracle |
| phase=check 且有合法 Do→Check 回执 | 读 [Check](../ontology/process/flow-check.md)，按[消费顺序](../ontology/concept/pdca-evidence.md#evidence-consumption)核对最终产物与实际结果；必要时查反证，再请求当前 Check 确认 | 旧 PASS 不能证明新产物；任务成功与被审对象不符合可以同时成立；不回 Do 偷改实现 |
| phase=act 且有合法 Check→Act 回执 | 读 [Act](../ontology/process/flow-act.md)，固定交付、限制、知识处置与后继建议，核对第四边并交回写权 | 交付可用、任务完成、整树就绪与发布资格分别判断；不倒填归档、不自动批准后继 |
| 已归档，或收到真实停止／撤权事件 | 归档只读；停止按 [CONTROL](../ontology/concept/task-control.md)和 [RESOURCE](../ontology/concept/resource-ownership.md)结清在途 | 不为凑四阶段继续副作用；新 attempt 必须另有真实身份与授权 |

已有有效派发绑定的节点 Agent 只执行自己的当前任务，不再次派发自己。没有真正 fresh Agent、原会话继续或确认路由能力时保持 dispatch_blocked，不能改成“草稿完整PDCA／草稿归档”。一项等待确认不等于暂停其他已就绪任务，宿主按原 SCHED 继续处理。

## 减少重复上下文而不减少核验

发布清单的逐成员摘要可由已获权文件工具在上下文外核对，保留完整清单与结果；模型读取协议身份、当前动作的权威映射和相关差异，不必反复载入整张assets表。此方式不豁免实际适用规则正文，也不将工具读过文件等同Agent理解规则。缓存只复用同一摘要；任一字节变化重新核验。真实token节省和漏约束率需宿主A/B测量，本仓库不宣称已测得收益。
