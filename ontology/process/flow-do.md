---
schema: pdca.asset/v2
id: ontology:process/flow-do
type: process
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.11
summary: Do：实现节点、运行测试与有限修复
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-14'
relations:
  specializes:
  - ontology:concept/process
  relates_to:
  - ontology:concept/pdca-gate
  - ontology:concept/pdca-transition
  - ontology:concept/pdca-task
  - ontology:concept/task-unit-test
  - ontology:concept/task-rework
  - ontology:process/work-scenarios
  - ontology:concept/task-control
  - ontology:concept/resource-ownership
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-evolution
  - ontology:concept/task-decomposition
---

# Do：实现节点、运行测试与有限修复

## 适用、输入与动作


当前phase=do且有合法Plan→Do回执；继续使用同一Agent。读取CONTRACT-01、TEST-01、CASE-01、REWORK-01与EVIDENCE-01。

1. 每个副作用调用先按RESOURCE-01核验当前控制/owner和operation_id；按scene实际生成节点定义/实现实体/独立审查；组合实现必须使用固定真实孩子版本，不代孩子做其任务。
2. 先检查测试器与夹具，再运行当前节点全部必需suite，保留正反例的actual、断言、原始证据、环境和实现摘要。非法输入正确拒绝也应为pass；环境error不能冒充正确拒绝。
3. 发现失败先固定run与复现，按 [TEST 定位与复验](../concept/task-unit-test.md#test-professional-paths)用可推翻的假设定位，不连续猜改。合同不变且Do修复预算剩余时按REWORK-01同任务修复，生成新实现版本、新run，最终全必需回归；预算耗尽或需改目标时停止实现尝试，记录失败/新任务建议。
4. 建立AC→case→run→artifact映射，附真实输入版本、原始输出及局限；按 [EVIDENCE 消费入口](../concept/pdca-evidence.md#evidence-consumption)使后续能核验actual，不只交付“已通过”。区分失败、unknown/not_run和旧版本stale，不用映射自证正确。
5. 固定当前结果包，自行核对完整性与GATE-01。无父Agent放行要求；完整失败记录同样可进入Check。
6. 用TRANSITION-01记录Do→Check。冻结后不再改该产物版本。

输出真实产物、套件结果、缺陷、修复迭代与固定结果包。非幂等副作用未知先RECOVERY-01；缺能力如实停止。只能在Do内部执行已授权有限修复，不偷偷改变验收。

收到取消先停止新增动作，CONTROL-01管理在途结清与stopping；能力丢失按CAP重新核验，不用旧Plan批准无限继续。

## 复用也是实际建模工作

modeling的Do根据已确认决定生成当前NODE/映射/局部delta和三场景suite；有共享修订则另产EVOLVE-01候选，不直接覆盖ontology投影。最终产物以父seed、原Plan和独立资料为判据，不能先产出再照抄为oracle。引用旧case不等于本次运行；当前测试以当前对象重新验证。

## 实体、实例与递归子本体

modeling产出定义或固定采用结果，以及当前 work instance；按 DECOMP-01评估全部三个场景职责，结果 leaf/composite/blocked。composite仅固定自己的直接 seed/角色接口/组合测试，交宿主后续派发，每个孩子自行再评估，不用父 Agent逐步控制。

定义真正的新业务实体时形成独立payload和案例；实例参数、任务actual留在records。按REUSE-01记录入库义务，不能只写create但没有定义对象。三场景suite的语义在本节点交付前定义，未来运行保持not_run，不写not_defined并宣称完成。

测试方法须接收固定错误样本；“当前候选没有错误”只说明本次负向断言，不证明判定器会拒绝错误。实际构造positive/negative及always-pass/always-fail控制，结果记录到run，不写回case的expected。

按CASE-01先核对subject不含本例答案、变体差异实际命中计划缺陷；按TEST-01分开材料判定、检查器案例与错误检查器结果。归档原始样本/方法/观测后再清理；每次失败和修复各有不可变run，不保留一个最终全PASS覆盖历史。
