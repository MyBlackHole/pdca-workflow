# T2147 triage brief（PDCA本体落地A场景）

- **scenario_type**: development（按 `ontology:concept/pdca-scenario-boundary-rule`：含可测试代码产出 → development；任务内“不再区分 bugfix/development”列为治理议题，不直接改六值键）
- **current behavior**: `ontology:process/flow-do` 路径A（development/bugfix）只有文字流程，无对应可回归验证的执行链；`scripts/ci-ontology-gate.py` 引用缺失脚本 `check-scenario-mismatch.py` 致 GATE FAILED；`ontology-validate.py` 通过，flow-*四节点引用存活达标（plan 6/do 7/check 3/act 5）
- **expected behavior**: 基于 PDCA 流程本体实现对应的 A 路径可执行落地（具体交付物待第二轮 Grill 收敛），路径A执行链可回归验证，“不再区分”议题有治理结论（改本体走 Improvement 流程，不在任务内直接改权威流程）
- **boundary**: 允许附带修本体（结构类错字可附带，语义改动另立项）；历史 archive ID 重复与 seam 缺失不在本任务范围
- **evidence**: T2135（archive/confirmed）、ontology-validate OK、ci-ontology-gate GATE FAILED（悬空引用）、pdca-doctor valid:false（历史瑕疵）
