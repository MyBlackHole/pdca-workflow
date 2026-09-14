---
schema: pdca.asset/v2
id: ontology:concept/resource-ownership
type: concept
semantic_kind: class
layer: Knowledge
authority: normative
status: active
revision: 4.0.0-rc.2
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-14'
summary: RESOURCE-01：集中资源预约，独立任务不互相越权
resource_spec:
  record_root: PDCA_ROOT/records/resources
  conflict_scope: canonical_actual_resources_across_all_projects_and_tasks
  states: [requested, held, revoking, released, retained]
  guarantee_profiles: [isolated_private, cooperative_serial, enforced_exclusive]
  multi_acquire: atomic_set_or_ordered_try_release
  lease_timeout_implies_release: false
  ledger_is_backend_lock: false
---

# RESOURCE-01：集中资源预约，独立任务不互相越权

## 资源中心与真实对象

所有project/workspace/work/node/scene/attempt在同一个PDCA_ROOT登记资源；不能按项目建立互不相见的预约库。实际对象才是资源键：backend、namespace、canonical_object_id、scope、access与规范化证据。不同task、分支、目录字符串不能证明隔离。

文件核对realpath、祖先/子树重叠、硬链接或挂载别名及检查后替换；远端核对租户、端点、库表、设备或对象身份。无法证明不同就视为可能冲突。对跨任务冲突只读必要资源元数据，不能借集中登记读取其他任务完整历史。

规则与快照只读；模型草稿、公共知识发布、任务私有记录和业务TARGET_ROOT是不同写域。用户授权阶段不表示任意写集中根，也不代替真实资源权限。

## 预约与取得

[预约记录契约](../contracts/record-shapes/resource-reservation.md)位于集中records/resources；由宿主提供的资源管理能力或用户指定的单一账本写者持有元数据写权。它是资源服务职责，不是父Agent的阶段监督职责。任务Agent提出请求、提供操作回执并独立执行；不得并发手改同一预约。

requested → held → revoking → released/retained。held必须引用实际取得回执与规范化资源集合；requested或纯Markdown中自填held不提供排他。恢复旧预约不得更换owner_task_id/attempt；新拥有者另有取得依据，旧拥有者不能释放新预约。

- isolated_private：实际私有记录/业务工作区且无重叠外部副作用，仍检查共享发布。
- cooperative_serial：只在用户接受且目标允许的保证范围，由单一资源入口串行执行冲突访问；不声称能阻挡失控进程。
- enforced_exclusive：真实后端排他、fencing或可证明旧访问已失效；整数epoch仅在后端真实支持时使用。需要此保证但缺后端时阻断，不自动降级。

多个资源原子取得完整集合，或用统一规范顺序try-acquire；失败后有据释放已取得部分再等待，不能持A无限等B。非冲突的已授权任务继续，不需要父Agent轮询。等待用户或子交付时只保留确有必要的占用，不阻塞对方必须写入的资源；不能安全释放的保留并说明。

## 操作、未知与结清

每个有副作用的调用按[operation](../contracts/record-shapes/operation.md)保存task/attempt/run、operation_id、资源/预约、参数摘要、幂等依据与原生请求结果。先登记再调用；崩溃或超时没有返回仍为unknown，不推断未执行。仅在同一后端幂等键已核验，或查询证明未产生副作用时重试，不宣称exactly-once。

每次副作用、恢复、资源路径或权限变化重新核对拥有者和实际目标。取消先停止新增动作，撤销访问并核对已接纳的在途操作；停止会话、租期过期、心跳消失、删除锁文件或task completed均不自动released。

released需要owner匹配、撤权依据及在途结清；未决影响进入retained并记录实际隔离范围与解除条件。只有后继不相交或旧影响已结清时才能重用。同一任务完成Act可如实记录保留隔离，但不得宣称所有资源释放。

安装器不实现这些业务锁、后端仲裁或fencing；本包恢复的是集中语义、记录与验收方法。真实能力不满足就阻断对应动作，绝不让父Agent监工冒充安全保证。
