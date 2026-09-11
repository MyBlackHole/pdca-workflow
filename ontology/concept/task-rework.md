---
schema: pdca.asset/v2
id: ontology:concept/task-rework
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.7
summary: 失败、返工与回归：任务级闭环
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-13'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/task-unit-test
  - ontology:concept/task-test-case
  - ontology:concept/work-ontology-tree
  - ontology:concept/work-tree-scheduling
  - ontology:concept/pdca-recovery
  - ontology:concept/task-control
  - ontology:concept/resource-ownership
  - ontology:concept/ontology-evolution
  - ontology:concept/ontology-adoption
rework_spec:
  in_do_same_task: true
  after_check_new_task: true
  new_attempt_fresh_agent: true
  preserve_failed_runs: true
  rerun_all_required: true
  propagate_stale_to_ancestors: true
  infinite_retries: false
---

# 失败、返工与回归：任务级闭环

## REWORK-01：失败是证据，不是应清除的噪声

失败保存在当前 task_id/attempt/run_id 的不可变记录；创建 issue_id，把 node/scene/定义/实现/suite版本、case_id、expected/actual、最小复现及证据关联起来。没有可复现输入时如实写未复现，不凭模型解释关闭缺陷。

## 两条路径，不混用阶段与运行次数

| 发现时刻/类型 | 处理 | 身份与验证 |
|---|---|---|
| Do内，目标/期望不变，有限修复预算尚有余量 | 同Agent、同任务留在Do修实现，每次产生新artifact_revision和run_id | 保留全部旧失败；最终版本跑全必需suite和回归；不得为一次命令创建PDCA |
| 已进入Check，或Do预算耗尽、需改变范围/权限、审查场景发现实现缺陷 | 原任务按原基线诚实判定与Act处置，创建该节点相应场景的新attempt | 新task_id、新Agent，完整PDCA；禁止Check→Do/Archive→Plan偷跑 |
| oracle/本体定义错误或前置契约冲突 | 建模场景新attempt形成新tree_revision/suite_revision，真实确认后重新覆盖 | 不用改expected把原实现变成成功；旧失败仍按旧定义保留 |
| 测试环境/夹具坏了 | 记录error，修复测试环境并验证已知正确与错误样本 | 不当作被测系统正确拒绝；若改变语义/超预算则新attempt |
| 外部副作用未知/真实Agent丢失 | 按RECOVERY-01先确定事实和写入权 | 不盲重试、不冒充原Agent；无法结清则blocked或interrupted |

`run_id` 是一次测试执行；`repair_iteration` 是同Do内一次修复；`attempt` 是完整PDCA任务尝试。三者不能混为“同一个任务反复清零”。同场景同节点同时至多一个有效写入者。

## 诊断与修复的详细步骤

1. **冻结失败现场**：保存原输入/fixture、被测实现摘要、suite/case版本、工具及环境、退出状态、前后状态、原始输出和失败断言。故障注入信息必须标注测试用途。
2. **检查测试器**：执行无歧义的已知正确样本和已知违例样本；确认不是测试器总通过、总拒绝、比较反了或读取了旧构建。错误归类为实现、组合、定义、oracle、环境、证据、非确定性；允许根因unknown。
3. **最小复现**：在隔离环境复现同症状；逐步减小输入/步骤而不改变失败谓词，保留原样本与缩减链。随机seed、竞态时序、特定版本缺一不可时保留。只复述错误日志不是复现。
4. **影响分析**：列出坏约束、直接修改节点、运行输入依赖者、组合祖先、可能失效的test/review/release；检查共享文件和接口是否越权。不要只修报错行而忽略同模式错误。
5. **提出可证伪修复假设**：说明哪个机制导致差异、最小改动是什么、预期哪些案例由fail变pass、哪些既有行为必须不变。低置信根因不能隐藏。
6. **先固定缺陷回归案例**：原失败已有案例则保留；新增最小复现作为诊断/回归增补，链接issue。先在旧实现证明该例确实失败，再在新实现验证；旧版本无法运行时写明证据缺口，不声称已证明“先红后绿”。
7. **实施有限修复**：在授权写域改变实现，不偷偷放宽本体、删除反例、把必需改为可选、增加过大容差、catch所有异常或替换真实组件为stub。每次修复生成新版本与差异。
8. **分层回归并移交**：当前任务完成原失败/最小复现、相邻边界及本节点全部必需suite（包含自己负责的组合）。本地完成即可按VERDICT-01正常Check/Act交付；随后由宿主启动受影响的依赖者/祖先各自完整任务，最后独立审查。祖先回归是工作issue关闭条件，不是孩子交付条件。最终每个节点交付都必须有自己的同版本全必需结果，不拼接旧PASS。
9. **重新审查并关闭**：执行任务可提交“修复候选”；缺陷关闭需要原失败被解决、无新必需失败、证据固定、影响范围回归和必要独立审查通过。关闭记录引用旧失败/新run/新artifact/新review，旧记录不改成pass。
10. **无法修复时停止**：超过已确认预算、同症状反复、原因不明、发现安全/权限问题时停止尝试，提交实际结果与未完成项，等待授权或新任务，不继续无限循环。

## 返工单必填信息

`templates/rework.md` 中 issue_id、origin_task/run/case、owner_node、scene、predecessor、目标版本、失败证据、根因分类及置信度、复现、修复方案、不能改变的约束、regression_case_ids、影响集合、预算、停止理由、后继任务及close_evidence 均需按事实填写。unknown可用于诊断，不能作为关闭依据。

## 影响传播与版本规则

修改节点先标记自己的旧交付/测试/审查相对于新产物为stale，再沿**实际产物依赖 + 组成祖先**传播。祖先即使代码没改，因孩子输入版本变更，其旧组合证据也不能自动适用。未受影响兄弟可保留原固定包，但必须写影响判定依据。

父组合必须等待新孩子完整PDCA结束且delivery_usable=true（并有终态回执）再启动自己的完整任务；孩子不得反过来等待父组合才交付。审查使用新的release与新审查任务，不能只让旧审查Agent追加“现在通过”。多个并发修复合并成一个固定输入集合，避免父任务测试一半新一半旧却声明同一release。

接口或目标改变按TREE-01新树版本重新覆盖；只修改实现且合同不变，同树版本新attempt。每次最终release明确选用哪一个attempt的交付，不能按文件修改时间猜“最新”。

## 缺陷与任务结果不是同一个状态

issue状态：open→reproduced（或reproduction_unknown）→fix_proposed→regression_pending→review_pending→closed；可为blocked/wont_fix，但wont_fix不意味着约束被满足。若缺陷发生在执行尚未独立审查阶段，可以先regression_pending→review_pending，不能自审关闭需要独立审查的缺陷。

任务可以以rejected/partial结束而issue保持open。修复任务自身confirmed仅代表其本地合同完成，正常归档后的固定包可供父组合使用；工作最终成功还需新产物的独立审查与整树条件。中断/取消任务未完成四阶段应标明interrupted，不伪造正常archive；新attempt不得同时占用旧写权。

## 必须识别的返工反例

改expected追随actual；删除失败案例；重试到偶然pass；只修示例输入；重用旧build；用mock代替最终组件；只跑单例不跑整套；同Agent承接另一轮独立任务；父审查PASS未失效；声称“问题已修复”却无新证据。任一发生都不能关闭缺陷或发布完整成功。

完整逐步示例见 [返工演练](../../examples/range-task/rework-walkthrough.md)，示例记录不是实际生产运行。


## 缺陷关闭主体与发布顺序

本任务只提交本地修复候选和open_issues。工作级issue由宿主工作索引唯一写入者按固定任务/审查包更新；`closed`要求所有affected_nodes回归及审查证据匹配，不靠执行Agent自述。审查任务先交付报告、后由工作索引关闭缺陷、最后计算release_approved；审查任务不得等待自己报告导致的issue关闭才能完成，避免第二个循环。

新增反例若只揭示原约束已禁止的行为，可作为具名诊断增补先复现；确认其判定后生成新suite版本用于后续attempt，不覆盖历史suite。改变语义/允许结果/接口则新树版本，不以测试补漏掩饰需求变化。


## Check以后返工的正常与异常路径

提出issue/新attempt建议不等于启动新任务。正常路径是原任务真实Check确认→Act→Archive→真实写权/资源结清，再开始新attempt。若真实用户取消/明确替代，或派发前已授权的期限生效，可按CONTROL-01先stopping再interrupted；原phase与失败证据保留，不能补齐四条边。

新attempt必须有新的派发依据、新task_id、新Agent和自己的Plan确认；取消不自动批准后续修改。旧记录写者已退出不等于远端operation结束，RESOURCE-01仍需排除冲突；保留资源未释放时不得接管。未变规则按当前固定版本，新规则采用通过迁移新任务处理。

返工验证新增：Plan取消无Do产物；Check替代不伪归档；迟到确认不能批准新对象；旧Agent恢复无法覆盖新写者；资源未知仍阻断；全部测试因环境丢失blocked可诚实失败收尾但不能交付实现。详细[R01—R20](../../tests/protocol-regression/README.md)分别有正例、反例、错误控制与恢复证据。

## 知识演进返工

内容被更早发布修改而导致base冲突时，保留失败proposal和旧摘要；以当前head重新三方比对，重新固定payload/manifest/测试/独立审查/授权。资源已串行不免除版本比较。Do内同合同有限修复可重新形成候选；进入Check后或改变允许行为/验收则新attempt、新Agent，不能覆盖原候选骗过批准。

ADOPT-01按真实采用闭包找受影响树并明确coverage范围；新head不自动改旧基线。旧版已知错误另发可信advisory，停止危险继续使用并在各工作中重建/回归；共享定义修好不等于全部工作问题closed。用户未授权的树不可改写，记录通知/未覆盖而非全库已修复。

## 发现者合格不消除被发现的缺陷

发现别人节点的必需约束/反例/oracle/版本绑定缺失时，必须形成issue，含发现者、受影响node/scene/revision/constraint、复现、责任人、`blocks`与消费对象。工作索引据此追加采用限制并重算readiness；不改原已封存产物。发现者可如实交付，但受影响对象不能因其报告PASS继续冻结。

冻结前必需定义或测试缺失，不得移交冻结后projection才修；未来运行not_run合法，规范not_defined不合法。已归档父节点由新modeling attempt修复，并按实际影响重验孩子seed；不得唤醒旧根Agent或要求尚未生成后代先完成才让父本地结束。

测试器/夹具修复必须保留原run、原checker/fixture、失败/invalid观测及修复差异，使用新run并复验正负控制。Check中只能修不改变已冻结业务产物、oracle语义或授权的测试环境/夹具；实际判定代码缺陷或新增业务实现按本节两条路径处理，不能以“修测试”为由改本体。最终一次PASS不删除首次error。

## 工作累计预算与安全接续

[work-budget](../../templates/work-budget.md)按work及(node,scene,issue)累计attempt、修复、重复症状和实际资源消耗；新task/Agent或递归层级不清零。Plan保留全必需回归费用，超上限需真实范围/预算授权；未知消耗不能按0处理。宿主维护计量事实，不替业务节点判断。

后继有predecessor时必须有rework issue或完整性事件、旧写者停止/交回、槽和资源结清、新派发依据。`held`、心跳丢失或自填archive不证明已释放。版本文件采用独立路径或可重新取得的内容对象，`file.md#rev1`不能代替rev1字节；新attempt不得覆盖旧证据。


<a id="rework-budget-quantities"></a>
## REWORK-01 · 预算数值边界

普通 consumed/reserved 为同单位有限非负数；布尔、NaN、无穷和负数不能充当消费。退款或计量纠正使用有来源且可审计的独立修正事件，不能靠负 consumed 抵消其他 attempt 的实际消耗。未知计量保持 unknown，不当0；允许 consumed=0，但依据必须真实。


## 内容演进不能偷换验收对象

模型深化、改标题或增章节也可能删掉旧义务。每项原约束给出保留、等效迁移、增强或经授权删除的对应和依据；未知关系不当作覆盖。case同ID但语义/必需性/expected改变必须新版本；旧版本的PASS只适用于旧输入。

Check后在Act发现需改变产物、接口或定义时，保留原判定并按既有REWORK/TREE开启适用新attempt/树版本；不在Act重做实现后沿用旧Check。诊断补充不改变交付字节时可作为追加证据，但不倒填先前实际。修复关闭按精确diff、新版本全必需回归及受影响作用域取证，不能仅凭“问题已解决”文字。


## 历史误判的修复回归

把已发生误判的原始输入、当时规则、实际输出与发现位置固定为回归来源；不要修改原件使其通过。明确分别修复判定方法、实际使用路径、业务对象及报告四个环节。关闭工具缺陷需要原反例和合法控制；关闭实际工作流缺陷还需对应采用路径的回归，不能把两者合并。

最终产物变化、case语义变化或旧义务移除后，用旧Check声明的新版本通过必须被检出。未受影响的结果仅在固定输入与影响依据仍成立时复用；全文增量更长不是约束保留证明。旧执行事实未知时先补取原证据；不能把所有缺口变成“重新执行整个工作”的无条件要求。
