---
schema: pdca.asset/v2
id: ontology:concept/resource-ownership
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.2.0
summary: 资源预约、旧执行者隔离与业务操作身份
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/capability-protocol
  - ontology:concept/work-tree-scheduling
  - ontology:concept/task-control
  - ontology:concept/pdca-transition
resource_spec:
  schema: pdca.resource-reservation/v1
  conflict_scope: canonical_actual_resources_across_all_tasks
  guarantee_profiles:
  - isolated_private
  - cooperative_serial
  - enforced_exclusive
  multi_acquire: atomic_set_or_ordered_try_release
  lease_timeout_implies_release: false
  operation_identity: task_id_and_operation_id
  release_requires:
  - owner_match
  - revocation_evidence
  - inflight_settled_or_scope_isolated
---

# 实际资源所有权与副作用准入

## RESOURCE-01：不同任务也可能争用同一个对象

槽键(work/tree/node/scene)只管理任务身份；资源键必须标识实际对象，跨work、tree_revision、node和场景检查冲突。不能以不同Git分支、不同task_id或不同目录字符串证明数据库/设备隔离。

资源记录包含backend/namespace、canonical_object_id、scope（对象/子树/键范围等）、access、规范化证据和授权范围。文件需处理真实路径、目录包含、软硬链接别名、挂载对象、大小写规则及检查后替换；远端使用租户/端点/库表/对象或设备身份。不能证明两个别名不同则保守视为可能冲突，阻断重叠写。host必须核验实际访问目标，不能只比字符串前缀。fixture的规范化对象不是生产能力证明。

## 能力与保证等级

- isolated_private：独立私有记录/业务工作区，无共享外部副作用；可并行。共享发布仍只有一名真实写入者。
- cooperative_serial：在契约允许single_writer_best_effort时，由可信单调度者串行获取资源；无超时自动接管，必须确认旧执行者及在途动作结束。不能声称可阻止恶意/失控进程。
- enforced_exclusive：宿主或资源入口实施排他与旧代数拒绝（fencing），或能证实所有旧执行/访问资格都已撤销。适用于要求硬保证的共享或不可逆副作用；缺能力不自动降级。

这些是支持前提而不是已安装后端。ownership_epoch只在真实后端支持时填写；写一个整数不产生fencing。租约到期/心跳消失不自动取消客户端和已提交远端动作。资源端拒绝旧epoch还要核对之前已接纳的在途动作，不能仅查后续写入被拒。

## 预约生命周期与责任

宿主资源所有者是唯一预约账本写入者。`requested → held → revoking → released/retained`记录事实而不代替实际机制。每次预约固定reservation_id、owner_task_id/attempt、授权、规范化resource_set、取得依据、epoch及能力版本。

1. TASK-01派发前，取得任务私有记录区、控制区、槽的实际写权；禁止两个主体都初始化同一task。
2. Plan固定业务写域；任何Plan探测副作用也先取得相应授权与预约。Plan→Do前为完整业务集合取得/复核held及实际后端回执。
3. 多资源使用统一规范排序并try-acquire，或后端一次原子取得完整集合；失败时释放本次已取得部分，再等待/重试。禁止一边无限持有A一边等待B。解除部分预约也必须有真实释放依据。
4. 每次副作用准入、恢复、环境/权限变动时校验所有权与实际目标仍匹配；生产保证等级不足时阻断。阶段门禁通过不是整段Do永久免检。
5. 结束/取消先阻止新动作、撤权并核对在途operation，再逐资源释放；未决影响进入retained并指向终止/隔离证据。过期owner只能写自己的异常材料，不能释放新owner预约或改新交付。
6. 同资源后继必须证明旧访问失效且影响已结清，或新作用域与可靠隔离区不相交。仅有termination字符串、completed状态或锁文件被删均不足。任务槽可终止而资源继续保留；两类账本不得混用。

依赖就绪不代表资源可用。不要在等待孩子交付期间持有孩子必须使用的共享资源；派发按SCHED-01前置通过后再预约。运行时发现新的多资源需求须释放可释放集合并重新申请，不能偷偷扩大冻结写域。

## 业务操作与重试

每次可能有副作用的调用先登记operation_id、目标/resource_ref、参数摘要、幂等策略、预约/epoch、调用前状态和允许范围；真实调用后登记backend_request_ref、结果及核验位置。崩溃在登记与调用间时状态unknown，不能从“没有结果”推断“未执行”。

仅在目标支持并验证同一个幂等键，或结果查询证明前次未产生作用时允许安全重试。阶段sequence不作为业务幂等键；复制task记录不能撤销外部写入。本协议不宣称exactly-once。

## 不具备能力时

可在仍满足目标契约的前提下选私有工作区/串行，仍每节点新Agent完整PDCA。缺真正上下文隔离、独立交互、可信取消或目标所要求排他时fail-closed；不是退回父Agent模拟。能力恢复按CONTROL-01重新取证，不能靠Agent自行写held解锁。

模板：[预约](../../templates/resource-reservation.md)、[操作](../../templates/operation.md)、[能力检查](../../templates/capability-check.md)。回归含不同工作共享对象、路径别名、旧epoch恢复、部分预约失败与在途远端写。
