---
schema: pdca.asset/v1
id: ontology:concept/pdca-phase-status
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/pdca-phase-status/1.0.0
summary: 阶段→状态/活跃度映射（plan→Pending/true，do→InProgress/true，check/act→Completed/true，archive→Completed/false）
relations:
  specializes:
  - ontology:concept/pdca-phase
  relates_to:
  - ontology:concept/pdca-task
attributes:
- name: mapping
  desc: plan→(Pending,true)；do→(InProgress,true)；check→(Completed,true)；act→(Completed,true)；archive→(Completed,false)
  constraint: 五阶段全覆盖，状态∈{Pending,InProgress,Completed}，archive 唯一 active=false
  testable_signal: python3 -c "from scripts.pdca_core import PHASE_STATUS; assert PHASE_STATUS=={'plan':('Pending',True),'do':('InProgress',True),'check':('Completed',True),'act':('Completed',True),'archive':('Completed',False)}" && grep -q "ontology:concept/pdca-phase-status" scripts/pdca_core.py
---

# pdca-phase-status

阶段→状态/活跃度映射（本体是源，`scripts/pdca_core.py:PHASE_STATUS` 是投射）。

| phase | status | active |
|-------|--------|--------|
| plan | Pending | true |
| do | InProgress | true |
| check | Completed | true |
| act | Completed | true |
| archive | Completed | false |

## 决策背景

`task.json` 的 `status/meta.active` 不得与 `meta.phase` 脱钩（见 `pdca_core:STATUS_PHASE_MISMATCH/ACTIVE_PHASE_MISMATCH`）。映射更改必须先改本节点再改代码（本体到代码单向）。
