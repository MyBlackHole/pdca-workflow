---
schema: pdca.asset/v2
id: ontology:concept/task-test-case
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.6
summary: 单元测试案例：输入、oracle 与失败诊断
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-13'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/task-unit-test
  - ontology:concept/task-rework
  - ontology:concept/pdca-evidence
case_spec:
  schema: pdca.test-case/v3
  required_fields:
  - case_id
  - revision
  - node_id
  - scene
  - suite_ref
  - constraint_ids
  - category
  - required
  - preconditions
  - inputs
  - action
  - expected
  - forbidden
  - oracle
  - observation
  - failure_signature
  - cleanup
---

# 单元测试案例：输入、oracle 与失败诊断

## CASE-01：一个案例是一份可复现契约

使用 `pdca.test-case/v3` Markdown。公共环境、夹具、动作入口可在 suite defaults 定义，案例以 defaults_ref 固定继承；执行前解析完整有效案例并记录内容摘要。不能靠上一轮对话中的隐含设置运行。

| 字段 | 具体要求 |
|---|---|
| case_id / revision | 套件内唯一稳定身份；期望改变升版本，旧案例不覆盖 |
| node_id / scene / suite_ref | 明确测试对象及所属场景；不跨节点冒用 |
| constraint_ids / ac_ids | 指向实际义务；至少一条必须约束或已标记诊断目的 |
| category / required | 正例、非法输入、边界、故障、组合、回归等；Plan前确定必需性 |
| purpose / rationale | 为什么这个输入能验证这条约束；避免同义案例充数 |
| preconditions / fixtures | 完整初始状态、输入对象、固定数据/版本、依赖/替身、权限 |
| action / inputs | 可执行的工具/调用绑定与精确参数；顺序/时序/并发控制适用时必填 |
| expected | 返回/错误类别、输出结构和内容、状态变化、允许副作用 |
| forbidden | 绝不能发生的行为/残留/外部调用；拒绝请求是否保持状态不变 |
| oracle | 比较方法、标准来源、容差/时限及理由；独立于被测实现 |
| observation | 必须收集的返回、状态快照、事件/日志和实际退出状态 |
| failure_signature | 哪个断言失败意味着什么；区分行为错误与测试环境错误 |
| cleanup | 成败/超时都要执行的隔离恢复；未知副作用如何处理 |
| reproducibility | 随机seed、版本、时序、环境限制；不能复现时不可假报复现 |
| kills / regression_issue | 预期识别的错误变体、回归缺陷编号；无关联可显式空 |

最终 suite 中 expected/forbidden/oracle/必要输入不得留待填写。模板可为空，但有空占位不得进入Do。正文和frontmatter矛盾则案例无效。

## 正例、非法输入反例、错误实现反例的不同期望

正例：合法输入→预期合法结果；案例 pass。
非法输入反例：非法输入→规定的错误且无禁止副作用；案例仍应 pass。仅“抛出任意异常”不算正确拒绝，除非契约就是这样定义。
错误实现反例：替换为有意违反约束的变体，用原案例检验→至少一项关键断言 fail；mutation 记录 killed。这个 fail 不能混入正确实现 suite 的通过率；在单独变体运行中登记。

## 断言顺序与错误优先级

多个输入同时无效时，必须规定错误优先级或允许的错误集合；不能看到输出以后临时解释为可接受。需要检验拒绝不改变状态时同时比较前后状态/外部事件，不能只比返回码。

浮点/性能阈值需固定容差、计量方法、样本策略和环境适用范围；时间不可信则不能填写伪造耗时。文本任务需精确列举必须事实与禁止结论，不以“看起来专业”当oracle。

## 失败记录

执行 observation 与规范 case 分开保存。失败至少包含输入版本、expected/actual、失败断言、原始证据、候选根因与不确定性、最小复现、影响节点。根因是推断时明确标识，不把猜测写成既成事实。后续处理依 REWORK-01。

## 错误样本与判定器的双层结果

负向行为断言与负样本运行分开：absence_on_current_candidate 不等于 negative_sample_rejected。以固定正确/违例文本或结构作为subject，记录subject_verdict与checker_case_result；subject违反约束时应fail，而检查器准确报告fail时检查器案例可pass。不得只写“若出现则失败，本次没出现，所以已拒绝”充当运行。

每项case带完整suite身份与版本；复用案例规范保留出处和适用性，当前actual必须新记录。文本语义案例允许人工或AI按精确规则检查，但模型化结构检查不能自称完成任意自然语言理解或真实宿主验收。

## 原始材料、判定标准与实际观测分离

文本/文档检查必须分开固定`subject_ref`（被检查材料）、`oracle_ref`（已确认判据与本例expected）、`observation_ref`（实际判断）。checker可读取通用规则，但检测能力测试不得把本例答案、标签、缺陷位置提示作为subject输入；执行前固定实际可见上下文清单。已看过答案的同一上下文不能再证明盲测识别能力。透明的人工核验可披露这一限制，不能伪称独立盲测。

每个注入案例固定`fault_model`、原样本摘要、唯一预期改动、须保持的不变量和变体差异；先确认实际变体触发计划中的缺陷。承诺“旧PASS用于新artifact”必须保留所有必需字段并真实构造版本错配，不能替换成删除约束行。注入未命中或引入无关解析错误记fixture invalid/error，不计killed；另立case测试缺字段仍有价值。

案例复用用[test-case-binding](../../templates/test-case-binding.md)固定来源suite/case版本、摘要、当前node/scene、输入契约与转换、约束映射、oracle适用性和local_delta。来源有同名案例不等于本节点已绑定。defaults只复用公共环境/动作/清理；独特输入、违例机制和期望不能省略。执行前保留完整有效案例摘要。


<a id="case-deterministic-expansion"></a>
## CASE-01 · 确定性展开，不使用最后写入覆盖

展开顺序为固定 defaults → source case → 显式 local binding。defaults 只填 source 未提供的执行设置；已写出的 null 不隐式删除来源义务。required、expected、forbidden、constraint_ids、oracle 的规范语义受原冻结契约保护，local_delta 不得覆盖或减弱；适用工具参数在 input_contract 明列后绑定。观察、诊断信息允许追加但不得覆盖原证据。字段冲突、未知绑定键或输入类型不兼容明确报错，不静默合并。

先保留来源 suite/case/defaults 的版本及字节摘要，再固定有效展开案例；同名 case 不代替 source_case_digest。local_suite_ref 使用具名 suite 身份时以外层 suite 清单解析，避免 case→suite→case 的摘要自环。仅 structural_predicate 的来源不能通过 identity 转换变成 raw_material_review。未确定的任意正文语义由独立语义审查处理，不能把机械检查无报错提升为语义通过。


## 断言与方法适用性

需要逐断言核算时在case中填写assertions，每项具有稳定assertion_id、constraint_ids、expected、forbidden、oracle和所需observation；run的assertion_results引用对应固定case，不复制期望充当观测。多个断言属于同一case合法，重复ID或找不到所属case不合法。

一致性比较先声明exact_declaration、abstract_contract、layout或behavior等方法范围。前者可忽略注释/空白，但不能忽略成员类型、顺序、数组长度；抽象合同必须预先明确允许省略的内容。布局需固定编译器、目标ABI、宏/对齐配置和实际数值输出。符号数组维度只能比较声明标记，不能据相同标记断言宏展开值相同。声明匹配不能提升为布局或行为通过；不支持的语法/环境返回unknown/error而非自动相等。
