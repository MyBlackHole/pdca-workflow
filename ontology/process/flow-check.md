---
schema: pdca.asset/v2
id: ontology:process/flow-check
type: process
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.9
summary: Check：当前任务自检与明确失败判定
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-13'
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
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-adoption
  - ontology:concept/task-decomposition
---

# Check：当前任务自检与明确失败判定

## 适用、输入与动作


当前phase=check，有合法Do→Check回执；输入为原基线、最终产物与真实测试结果包，不要求父层审查回执。读取TEST-01、VERDICT-01、CONFIRM-01。

1. 按 [EVIDENCE 消费顺序](../concept/pdca-evidence.md#evidence-consumption)逐项读取对象、执行、actual/oracle并回链最终判定；检查每个必须AC与案例的覆盖、过期PASS、未解决flaky和假mutation kill，不能只复述Do摘要。
2. 比较Plan预测与Do实际，按pass/fail/unknown/not_run逐项解释；有可疑发现时用 [反证核验](independent-work-review.md#review-counterevidence)复核已有材料。组合节点核对真实孩子/接口/状态传播；孩子通过不代替本节点通过。
3. 生成conclusion.md和任务verdict；独立审查场景必须额外给subject_conformance，二者不混淆。
4. 新发现实现问题创建issue/返工建议，不回Do修改。需要新实验/范围时记录REWORK-01后继建议；旧槽未完成正常交回或CONTROL-01安全终止前，不得实际启动新attempt。
5. 固定结论包并请求当前任务真实用户确认；认可失败判定可进入Act。满足GATE-01后记录转换。

输出明确结论、证据回链、缺陷与真实确认。用户拒绝保持Check（真实取消/授权期限到期则走CONTROL-01异常终止）；可澄清现有证据和判定，但不能改原产物偷做修复。

正常Check确认与异常替代是两条不同路径。新attempt不能继承旧结论请求的迟到批准，不能为绕过确认由AI自行取消。

## 复用与更新审查

modeling逐项审查检索完整性声明、必须约束映射、local delta、兼容性和adoption来源；无新知识可通过而不伪造新增节点。禁止只看名称/版本号、从候选active字段推断已发布、忽略当前错误公告。共享候选通过本任务Check不替代EVOLVE-01独立发布审查和明确发布许可。

## 建模交付的交叉检查

核对原目标→业务定义→当前实例→需求责任→分解结论→三场景suite。DECOMP-01对每个子seed不预设原子叶；只读规范可共享，不能把兄弟引用当拥有权冲突。使用TEST-01具名反例的实际结果检验判定器，缺失case或只有“无此错误”不得标反例能力通过。

current_task_pass、node_definition_ready、tree_freeze_ready与knowledge_goal_satisfied分别判断。当前本地交付可用不意味着后代/共享发布已完成；必须发布事项仍未完成时明确其状态，不能通过candidate_only消失。

必需覆盖须验证案例语义，不只解析ID；未来suite复用必须有明确绑定。发现其他节点必需缺口时创建有阻断范围的issue并通知工作索引，不能记“无issue”或移交冻结后才修。当前发现者可如实通过，被影响交付仍需处置。Check修夹具依REWORK-01保留原error，不偷改业务产物或oracle。

## 同一事实的跨表达一致性

对承担关键约束的文字、状态表、流程图/时序图和案例，列出同一主体/前提/版本下的顺序与含义，验证互相一致；明确图区分数据流与提交先后时不误报。原始来源固定后再确定oracle，不能从被审图生成预期证明自身。故意颠倒关键先后、删除否定条件、遗漏测试约束的报告应被反例识别。缺目标源快照时只报告表达内部矛盾，不推断目标实现存在同样bug。

本任务是只读研究时，projection执行研究并交付解释/证据，不因此扩大为源码重构；所有建议修改另按原目标/授权处理。
