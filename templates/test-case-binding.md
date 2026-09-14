---
schema: pdca.test-case-binding/v1
protocol_revision: 3.4.11
binding_id: null
source_suite_ref: null
source_suite_revision: null
source_suite_digest: null
source_case_id: null
source_case_revision: null
source_case_digest: null
node_id: null
scene: null
local_suite_ref: null
local_case_id: null
input_contract: null
input_transform: null
constraint_mapping: []
oracle_applicability: null
local_delta: null
required: true
effective_case_ref: null
effective_case_digest: null
source_case_ref: null
source_defaults_ref: null
source_defaults_digest: null
---

# 来源案例的本地适用绑定

CASE-01：输入转换与local_delta不得改变被采用的允许行为或事后改expected。无转换明确identity；映射说明约束语义不是只写同名。有效展开包括源case与固定defaults以及本地增量，进入Do前固定完整字节；未来场景工具在各自Plan绑定，语义不能留空。

来源若仅检验布尔facts，必须标structural_predicate；对原文的提取/判定另有raw_material_review案例，不能静默改输入类型。


source_case_ref明确来源字节位置；local_suite_ref允许具名suite身份，由外层绑定解析，不能生成摘要自环。展开按 CASE-01#case-deterministic-expansion。

## 映射两端

constraint_mapping每项的source存在于固定来源case，local存在于当前有效case的约束集合；完整覆盖来源及本地必需约束。不得使用不存在的local ID或仅比较source集合。
