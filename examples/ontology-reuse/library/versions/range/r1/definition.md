---
schema: pdca.fixture-definition/v1
fixture_only: true
library_id: FIX-LIB
definition_id: FIX/Range
revision: r1
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

# FIX/Range r1

本体复用演练的教学输入，不是生产已发布本体。完整参数域、类型及错误优先级以原范围示例为准；此处只演示复用、版本和范围映射，不能将三例演练当完整验收。
