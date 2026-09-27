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
dcterms_modified: '2026-09-27'
summary: RESOURCE-01：真实共享资源的取得、持有与结清
resource_spec:
  record_root: PDCA_ROOT/records/resources
  conflict_scope: canonical_actual_resources_across_all_projects_and_tasks
  states: [requested, held, revoking, released, retained]
  guarantee_profiles: [isolated_private, cooperative_serial, enforced_exclusive]
  multi_acquire: atomic_set_or_ordered_try_release
  lease_timeout_implies_release: false
  ledger_is_backend_lock: false
---

# RESOURCE-01：真实资源 ownership

RESOURCE-01 只回答：**某个 task/attempt 对哪些真实共享对象拥有何种可证明的访问保证，以及这些占用何时真正结清。**
它不批准 phase、不决定 task state，也不解释 dependency ready。

## 资源身份与冲突

资源键来自真实对象而不是任务名/路径字符串：backend、namespace、canonical object identity、scope、access。
文件需考虑 realpath、祖先/子树重叠、硬链接/挂载别名与检查后替换；远端需核对租户、端点、库表、设备等真实身份。

无法证明两个写目标互不重叠时，按可能冲突处理。跨任务只读取判断冲突所需的资源元数据，不导入其他 task 历史。

## 预约生命周期

记录格式见 [resource-reservation](../contracts/record-shapes/resource-reservation.md)。

`requested → held → revoking → released | retained`

- requested：提出资源请求，不表示已取得；
- held：必须有真实 backend acquire/ownership 依据；
- revoking：停止新增依赖该 ownership 的业务动作，并撤销/隔离访问；
- released：owner、在途 operation 与后端访问都已有结清证据；
- retained：仍有未决影响或无法安全释放，记录隔离范围与 release conditions。

停止会话、心跳消失、租期到期、删除锁文件、phase/task completed 都不会自动得到 released。

## 保证等级

- **isolated_private**：真实私有且无重叠外部副作用；
- **cooperative_serial**：由单一入口协作串行，不能声称阻挡同权限失控进程；
- **enforced_exclusive**：后端真实排他/fencing，旧访问已可证明失效。

需要更强保证但后端不支持时保持 blocked，不自动降级。

多资源要么原子取得完整集合，要么按统一顺序 try-acquire 并有据释放失败前已取得部分；
不能持 A 无限等待 B。

## Side-effect operation 与结清

副作用调用事实只记录在 [operation](../contracts/record-shapes/operation.md)。
RESOURCE 使用这些事实判断 ownership 是否能安全释放：

- submitted/unknown operation 在未对账前阻止相关资源进入 released；
- unknown 只对账原 operation，不因超时推定未执行；
- 只有后端幂等语义已有证据，或查询证明原调用未产生副作用时，才允许安全重试；
- owner/target/resource path/permission 变化时重新核对实际对象。

CONTROL-01 的 cancel/revoke 可以触发资源进入 revoking，但真正 released/retained 只由本规则按实际结清证据决定。
RESOURCE 状态事实由 STATE/GATE 消费；资源记录本身不会自动修改 task execution_state 或生成授权。
