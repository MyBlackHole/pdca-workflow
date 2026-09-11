---
schema: pdca.fixture-definition/v1
fixture_only: true
library_id: FIX-LIB
definition_id: FIX/Range
revision: r2
semantic_identity: range-validation
applicability:
  units: bytes
  interface: strict_three_integer_parameters
constraints:
- constraint_id: C_RANGE
  required: true
  statement: 域合法时仅offset<=N且length<=N-offset返回OK
- constraint_id: C_PURE
  required: true
  statement: 不修改状态或进行外部I/O
claim_status: fixture_not_factual_certification
---

# FIX/Range r2

教学编辑性候选：补充说明“等于末尾合法，但非空区间起点不能等于N”；没有改变C_RANGE或C_PURE。需要独立语义审查，版本名称本身不是兼容证明。未运行生产发布。
