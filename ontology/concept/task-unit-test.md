---
schema: pdca.asset/v2
id: ontology:concept/task-unit-test
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.7
summary: 任务单元测试：正例、反例、覆盖与证据
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-13'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/task-test-case
  - ontology:concept/task-rework
  - ontology:concept/pdca-evidence
  - ontology:concept/work-node-contract
  - ontology:process/independent-work-review
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-evolution
  - ontology:concept/ontology-adoption
test_spec:
  case_results:
  - pass
  - fail
  - error
  - blocked
  - not_run
  mutation_results:
  - killed
  - survived
  - invalid
  - equivalent
  required_coverage:
  - positive
  - negative
  final_required_cases: all_on_same_artifact_revision
  flaky_can_pass: false
  test_error_is_kill: false
---

# 任务单元测试：正例、反例、覆盖与证据

## TEST-01：测试单元是一个节点的一次场景任务

每个 `(work_id, tree_revision, node_id, scene, attempt)` 都有 suite。实体约束定义期望，正反例定义可复现输入及 oracle，真实观测支持任务 Check。**示例不是装饰；每个必须案例都是可运行或可按明确步骤核验的验收契约。** 模板填写完整也不等于已经执行。

测试套件由节点规范提供语义，在任务 Plan 绑定宿主实际执行方式；测试函数/构建脚本可生成到目标项目的授权位置，不进入本协议运行依赖。删除本协议 Python 不禁止被实施项目的 Python/Rust/C 测试。

## 三场景各有自己的单元测试

| 场景 | 被测单元 | 正例 | 反例/错误样本 |
|---|---|---|---|
| 建模 | 当前节点定义及直接子 seed | 覆盖父需求、接口自洽、完整组合义务的定义 | 漏一条父要求、两个子节点重复拥有共享实体、未定义错误传播、不可判定约束 |
| 执行 | 当前实体实现；父节点还包括真实组合 | 合法输入/状态与所需结果 | 非法输入处理、边界越界、部分失败残留、违反约束的实现变体 |
| 审查 | 以定义和实现形成的对应判定 | 已知符合的固定实现被正确采纳 | 已知违例实现被识别；缺失/过期证据不被当作通过；无辜实现不能误报 |

审查单元测试能验证审查方法，但不能用几个夹具替代对实际工作产物的审查。审查报告中的 subject_conformance 与审查任务完成质量分别判定。

## Plan：先固定期望，后观察实现

1. 读取当前节点和适用约束，建立 `constraint_id → case_id → oracle → evidence` 覆盖矩阵。每个必须约束至少有正向行为和能够击穿违例的反向案例；边界/组合/故障等按适用性扩展。不能只测返回值而漏状态与副作用。
2. 采用 CASE-01 固定案例的前置、输入、动作、期望、禁止结果、oracle、清理与失败定位。工具绑定可暂选，但进入 Do 前必须可执行；缺能力不能写 PASS。
3. 固定 suite_id/revision、案例清单、fixture/ref/hash、参考模型来源、测试工具版本、随机策略、并发调度/故障注入控制、必需性和回归策略。oracle 必须源自已确认约束，不能来自被测实现自己的输出。
4. 明确有限的 Do 内修复预算：最大修复次数、同症状最大重复次数、工具调用/资源预算与停止条件；值由任务 Plan 确认，不设无限“直到通过”。保留必要的全部回归成本。
5. 生成冻结基线。不得先运行后把 expected 改成 actual，再宣称“预测正确”。案例尚未定义或没有 oracle 的必须约束阻断 Plan→Do。

## 覆盖分类：数量不是唯一指标

| 类别 | 必须考虑的内容 | 不能接受的替代 |
|---|---|---|
| 正例 | 典型合法值、最小合法、最大合法、代表性组合 | 一条 happy-path 覆盖全部约束 |
| 非法输入反例 | 缺字段、错误类型、空值、越界、矛盾状态、未授权范围 | 只看进程退出，不看错误类别和副作用 |
| 边界 | 等号两侧、0/1、空/满、极值、大小端/单位适用处 | 只用中间值；整数溢出被语言默认行为掩盖 |
| 状态与故障 | 每个已定义状态转移，失败注入点，超时/中断后结果未知 | 把测试程序出错当系统正确拒绝 |
| 并发/幂等 | 合同要求的交错、重复操作、写入竞争、恢复 | 串行通过就声称并发安全 |
| 组合 | 真实孩子接口/版本、错误传播、整体不变量、组合失败 | 汇总孩子 PASS，或只用 stub 最终验收 |
| 错误实现检测 | 对关键约束构造独立有意违例变体/错误审查样本 | 编译失败或运行环境坏了就说成功击杀 |
| 回归 | 本节点历史缺陷、相关约束、全部必需案例和本节点负责的组合；祖先回归交由祖先任务 | 只重跑曾失败一例；删案例换高通过率 |

不适用分类需记录理由、适用性依据与确认来源；不适用是测试设计裁定，不能把一个已经失败的必需案例改为 N/A。对于文档/研究任务，使用同样具体的固定文本/事实样本、评分条目、反证与独立来源；只有主观自述的 oracle 不足以支持必须事实通过。

## 执行顺序与隔离

先验证测试环境/夹具/已知正确样本，排除“测试器自身总是通过/总是失败”；再运行固定 suite。每案例独立清理，不能意外继承上一例状态；确需状态序列则把整个序列写成单个具名案例。真实业务凭据和破坏性外部对象不得用于故障注入，使用授权隔离环境。

完整保存 actual，不覆盖 expected。随机测试保存生成器版本、seed、生成数量、失败样本和最小化步骤；不能只记录“随机一千次通过”。并发测试记录调度种子/屏障/事件次序和失败窗口；非确定问题至少保留复现条件，不能筛掉失败运行。

大套件按索引分批运行，原始结果在上下文外固定；Agent读取覆盖摘要和相关失败，不必将几千条案例全量载入。分批不能漏跑必需案例。

## 结果分类与聚合

单案例 `result` 为 `pass / fail / error / blocked / not_run`：
- pass：动作实际执行，全部预期与禁止副作用断言均满足，oracle/证据有效。
- fail：动作已执行，观测违反至少一项断言；保存 expected/actual 差异。
- error：测试器、夹具、解析器或执行环境出错，无法判断被测行为；不能算正确拒绝。
- blocked：已识别的前置/权限/依赖不满足，尚不能运行。
- not_run：未实际运行，写明原因；计划执行不等于执行。

`flaky` 是跨运行不稳定标志而非 pass；任何与已确认确定性要求不符的运行阻止完整通过。不得用最后一次成功覆盖先前失败。AC 聚合映射：pass→pass，fail→fail，error/blocked→unknown，not_run→not_run；关键案例缺失/过期也记 unknown。

node_local_pass只聚合当前node_id/scene的固定套件：所有必需约束覆盖完整；所有必需案例对同一交付产物版本实际pass；没有未解释flaky、测试器错误或未清理副作用；要求的错误实现检测有效；本节点历史缺陷及本节点负责的组合回归完成。其他节点、祖先和工作级复审不得放入本套件的通过前置。它们各有完整PDCA任务，由REWORK-01跟踪其结果。非必需案例失败仍须披露。

Do→Check 只要求足以诚实判断：失败、error、not_run 的完整记录可以进入 Check；它不代表 suite 通过。任务confirmed需要本地通过且相应场景产物满足契约；delivery_usable还需VERDICT-01的终态和交付条件。孩子可先交付，工作issue可以继续open/regression_pending；这是作用域分离，不是跳过祖先回归。

## 错误实现检测（mutation）

每个关键/安全/数据完整性约束至少构造一个可执行的错误变体，或有同等区分力的已知缺陷样本。记录 mutant_id、被破坏约束、唯一改动、预期击杀 case_id；在隔离副本执行，不改生产实现。

结果为 killed（有效执行且预期断言失败）、survived（错误变体仍通过）、invalid（未能执行/编译/夹具错误）、equivalent（有理由证明不改变允许行为）。invalid不算killed；equivalent需独立依据且不能消灭该约束的检测义务。survived说明测试有盲区，不说明实现正确；先修补案例/判定，再重跑正确样本与错误变体。关键约束不得留未经解释的survivor。

## 证据与版本

每次 run_id 固定 task/attempt、suite与case版本、实现及孩子摘要、工具/环境、实际动作、原始输出、断言差异、退出状态和清理结果；格式见 `templates/test-run.md`。样例中的 expected 不可复制到 actual；哈希不得臆造。

实现改变后旧 PASS 仍是旧版本证据，但不能证明新版本。新版本必须重跑所有必需固定案例（成本不可承受先拆节点或调整尚未确认的计划，不事后静默抽样）；影响到其他节点时按 REWORK-01 传播。用于诊断的新案例不反向修改冻结 oracle，正式加强规范须发新suite版本并明确授权；若改变允许行为、期望、必须性或接口，按TREE-01新树版本。纯诊断反例不追溯修改已冻结套件。

详细示例见 [任务单元测试示例](../../examples/range-task/README.md)。


## 验收边界的最小反例

B1本地全通过而B/R未开始：B1可正常完成自己的Check/Act，宿主确认归档后允许B采纳；缺陷不得关闭。B1本地任一必需失败：B不就绪。B1通过但B组合失败：B1旧本地证据仍真实，B的交付不可用，R阻断，工作不可发布。禁止把上述三个判据压成一个PASS。

## 复用与演进的单元测试

建模suite必须验证采用是否适用：已有定义完全覆盖且不新增知识的正例；同名不同语义、遗漏base必需约束、局部放宽、安全公告未处理、旧case与新期望混用的反例。共享修订测试还要验证旧base拒绝、语义合并、授权对象及不可变store；参考模型只能证明其测试谓词，不能证明任意文字兼容。

复用旧案例时固定case/source/oracle版本、适用域和当前工具绑定；actual必须来自当前task/实现/环境，不能复制别树PASS。本地delta增加要求需新的正例、非法行为反例与错误定义控制；缩窄对外输入不凭“更严格”宣称可替换。

知识发布不触发全部旧任务自动失效；真实采用新输入或已确认缺陷才按ADOPT-01影响。回归范围分本地/组合/跨工作，不令孩子等待全局迁移。详细[U01—U20](../../tests/reuse-regression/README.md)逐例保留失败与重做路径。

## 定义测试、检查器测试与未来执行分离

当前候选满足“未声称孩子已实现”是一个候选断言；它不证明检查器能识别真的肯定违例。反例检测义务要求固定错误样本实际进入相同检查方法，保存输入、actual判定、错误位置与oracle。正确样本被接受和错误样本被拒绝分别运行；再用always-pass、always-fail或关键词-only等错误检查器核对误报/漏报。含“不得声称已实现”的正确句不能被关键词匹配误判为已经实现。

案例引用使用(node_id,suite_id,suite_revision,case_id,case_revision)及固定位置；局部同名合法，但不能用另一suite的M-P1补缺失引用。not_defined（没有规范）与not_run（有规范未执行）不相同。modeling本地验收要求当前节点所有scene有固定case/expected/oracle及必需性；未来场景的工具绑定/真实actual留待各自Plan/Do，不能因暂无实现就免定义。

新增用例参见 [K01—K20](../../tests/modeling-regression/README.md) 和 [可复用审查契约](../../tests/audit-contracts/README.md)。它们是固定夹具与规范，不是完成了真实AI审查的证明。

## 三种测试与结果不可混算

| test_layer | 被测对象与实际输入 | 有效结果 |
|---|---|---|
| structural_predicate | 已显式给定的合成facts/状态 | 仅证明字段判定与所列控制，不证明从原文提取事实 |
| raw_material_review | 固定原文/文件集合/报告/版本引用 | 保存实际提取事实、证据位置和逐约束判定；不能直接喂入答案 |
| checker_mutation | 有意有错的检查器处理同一固定样本 | 单独记录错误检查器版本与killed/survived/invalid/equivalent |

正常检查器拒绝错误subject时`subject_verdict=fail`、`checker_case_result=pass`，不是自动mutation kill；`mutation_run=false`时`checker_mutation_result`必须为空。只有改了检查器且有效运行才可填写该列。先验证已知正负样本，再运行实际候选；合成模型结果、材料检查结果与真实宿主结果分别报告。

每次run固定suite/case、subject/fixture、oracle、checker、artifact及孩子版本。原始输入、变体差异、命令/方法、stdout/stderr或人工逐项观测、清理和首次失败必须归档到固定位置后再删除临时目录。仅剩已删除的`/tmp`路径不支持可复核PASS。敏感内容可脱敏并固定转换方式，无法再复现时写明证据范围。

## 冻结合同与回归增补

保留`frozen_contract_suite_ref`，后续增补使用[regression-extension](../../templates/regression-extension.md)，列issue、原有禁止约束、旧/新样本、判定依据与授权。后继Plan固定基准suite加增补解析出的完整有效案例清单；test-run记录全部`effective_case_refs`和增补摘要。基准必需案例是有效集合的子集且语义/required/expected逐字节不变，不修改冻结节点指向旧suite的记录。

只增加检测原有禁止行为的案例可在同树新attempt采用新有效suite；不能借增补删除原例、降级必需性、改变允许结果或接口。允许行为改变按TREE/REWORK用新树版本。纯诊断未获采用时不冒充已经固定的必需合同。


## 可核算的覆盖与证据

案例与断言分开计数。宣称断言全通过时，先从固定要求与有效case展开具名assertion清单，再逐条绑定case完整身份、expected/oracle、实际observation和结果；总数由集合计算，不能接受手填45/45或100%。登记外的诊断案例披露但不计入冻结必需集合；新增正式义务按回归增补/新基线采用，不能倒写Plan。

suite与case仅保存规范，实际结果保存在新run。actual与expected同文不是蓄意造假的证明，也不是运行证据；准确返回固定字符串的案例可以合法同文，但仍须固定实际动作、输入和原始观测。缺观测、不同case版本、不同产物或保留材料损坏时结果unknown/error，不由“全部pass”消除。

原要求→当前约束→案例/断言→实现/材料→实际观察双向闭合；清单从已固定要求独立得到，不能根据报告已经列出的部分构造分母。移除旧不变量、同ID改义、复用Act前版本的PASS，均须被覆盖检查拒绝。新增回归见[真实记录反例](../../tests/records-repair/suite.md)。


## 检查输出必须进入实际Check判定

每个方法固定支持范围和失败语义。执行后读取本次新生成的结果及原始输出，核对输入/工具/环境和退出状态；没有本次结果、检查器崩溃、未知profile或旧结果文件均不能被解释为pass。检查器error单列，不计为正确拒绝或mutation killed。保存结果使用新的具名位置，不能覆盖首次失败。

错误输入既应触发检测，也必须使相应最终结论不再是“完全一致”。使用真实历史误判原件作回归，并增加未同文的独立变体和合法控制；检测一个固定26/45案例不代表通用语义能力。正负控制、真实材料重放、业务运行分别统计，不通过导入测试类重复执行或把assertion数当case数扩大成绩。

盲测核对被评测者实际可见的文件角色及已知本例答案/判据的交集，同字节重命名副本也须排除；不只信answers_included=false。评分器可读判据，通用规则可以是合法输入。透明审查可明确采用，但不以其结果证明盲测能力；清单级无已知交集不认证宿主真实上下文隔离。
