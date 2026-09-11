---
schema: pdca.ontology-impact/v1
state: draft
protocol_revision: 3.4.10
impact_id: null
source_publication_or_advisory_ref: null
library_id: null
definition_id: null
old_version_refs: []
new_version_ref: null
affected_constraint_ids: []
adoption_index_ref: null
index_generation: null
coverage_status: null
coverage_scope: []
unknown_regions: []
affected_adoptions: []
non_affected_adoptions: []
work_actions: []
global_resolution: null
---

# 跨树影响与迁移处置

ADOPT-01。affected_adoptions包含采用身份、固定版本、匹配约束/依赖闭包、直接依赖和组成祖先、证据理由；不能从relates_to推断全库全部受影响。non_affected必须有适用性依据。

每项work_actions含work/tree/node、动作（保持旧版/显式迁移/阻断核查/取消退役）、新tree或attempt依据、套件映射、真实确认/后继任务/局部与祖先回归/独立审查，未运行写not_run。旧失败与旧字节不修改。

global_resolution区分定义已修复、已知采用者处置中、声明范围已结清；coverage不完整时不能写“所有采用者已修复”。退役只完成管理处置，不证明实现通过。当前节点可先本地交付，不等全局迁移完成。
