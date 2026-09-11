---
schema: pdca.asset/v2
id: ontology:concept/pdca-verdict
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.7
summary: 任务判定、被审对象与发布结果
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-13'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-ai-friendly-confirmation
  - ontology:concept/task-unit-test
  - ontology:process/independent-work-review
  - ontology:concept/task-rework
acceptance_spec:
  node_local_scope: node_scene_artifact
  delivery_profile:
  - full
  delivery_requires_terminal_receipt: true
  ancestor_regression_blocks_local_delivery: false
  work_issue_scope: affected_nodes_and_reviews
  release_scope: whole_tree_current_release
---

# 任务判定、被审对象与发布结果

## VERDICT-01

Check对原基线判定task verdict：confirmed=所有必须AC与TEST-01套件有真实当前版本证据并通过；partial=有成果但存在失败/unknown/not_run；rejected=核心目标或关键约束不成立。不能多数表决或用测试比例掩盖一项必需失败。

必须给聚合理由、成立/不成立范围和未解决缺陷。错误实现变体的预期断言失败属于mutation killed，不混入正确实现的失败统计；测试器error不属于pass。

用户check_confirmation只表示认可判定，不能改写outcome。归档/completed只表示正常生命周期结束；delivery_usable按下表评价当前场景交付能否被下一任务采用。3.1只支持full交付，不再保留未实现的降级例外；partial/rejected实现不能成为父组合的可用输入。

审查场景另有subject_conformance=pass/fail/unknown，评价被审实现。审查正确发现实现失败时审查任务可confirmed而subject_conformance=fail。整树发布只看当前release各必需节点符合性和组合/根目标，不把审查任务confirmed当实现通过。

知识处置由LEARN-01决定；反例和失败也可有复用价值。Check不能修改AC、伪造证据或回退阶段，返工见REWORK-01。


## 验收作用域：四种结果不互相替代

| 判据 | 唯一范围与成立条件 | 不能等待/替代什么 |
|---|---|---|
| node_local_pass | TEST-01当前节点、当前场景、当前产物的全部必需案例和错误检测通过，观测完整；包括本节点负责的真实组合 | 不等待祖先未来任务或工作缺陷关闭 |
| delivery_usable | node_local_pass=true、task verdict=confirmed、当前任务完整四阶段正常结束、固定交付有效且无本节点未决副作用；由宿主核对终态回执后采纳 | 不等于全局issue关闭或最终发布；integration_ready仅是projection交付被父合同接纳后的推导值，不另存镜像字段 |
| work_issue_closed | REWORK-01中该缺陷涉及的本地、依赖者、祖先组合及必要独立审查都对固定版本完成，关闭证据齐全 | 不作为孩子局部通过或交付可用的前置 |
| release_approved | REVIEW-01整树必需对象符合、组合/根目标通过、相关阻断缺陷已关闭且无unknown/stale | 不作为节点任务正常归档的前置 |

`delivery_usable`在Act交付草案中只是声明；后续任务需同时核验该任务的独立终态回执。交付包不引用尚未生成的归档回执，宿主索引组合引用两者，避免摘要循环。未完成四阶段、失败或中断时不能成为可用交付。

建模交付可用指当前定义及直接seed完成，不要求未生成后代已完成；因此生成方向仍为根到叶。审查交付可用指审查报告可信且审查任务通过，`subject_conformance=fail`报告仍可供父审查汇聚，不可供实现任务假冒成功输入。

本版本`delivery_profile`只能为full。领域本身允许的降级行为可以作为另一个明确目标契约建模、确认并完整测试，但不得把旧full失败改名为降级成功。未来多模式支持需要单独规范变更。

## 知识目标与本地成功

`knowledge_goal_satisfied` 是REUSE-01工作索引基于不可变义务与追加履行证据计算的工作级结论，不是新增phase或Agent写出的发布许可。没有必需新发布的纯reuse工作可以满足；shared_required未发布、已隔离或必需事实仍未知则不能满足。shared_deferred只有在确有范围授权与接续责任时才属于已披露非本轮发布义务。

要求建设本体库的工作，其release_approved还需该知识目标满足；node_local_pass/delivery_usable保持本地范围，后代和全局迁移不得进入其等待条件。共享文件出现不等于发布，candidate_only不取消已确认义务。

## 工作发布绑定精确版本组合

使用[work-release-manifest](../../templates/work-release-manifest.md)固定树冻结回执、图、每节点选定的task/attempt、delivery/独立终态、artifact和真实消费的孩子版本。审查任务固定它作为输入，自己的报告与批准放在清单外；[work-release-receipt](../../templates/work-release-receipt.md)再绑定该清单、必需审查、阻断issue关闭和适用知识义务履行。

父测试A@1+B@1，不可因为A@2单独PASS就发布A@2+B@1+旧父。逐条比较父实际消费输入与release选定对象摘要，而非选各节点“最新PASS”。新输入需受影响祖先自己的完整回归/审查；相关清单变更新发布ID，不覆盖旧批准。失败包可进入诚实审查，但缺项时release_approved不得为true。


## 结论缺证据时的采用边界

报告数字、schema标签、任务目录、手填completed都不是状态来源。缺当前必需观察/确认/终态时，不接受其成功或发布资格；保留具体缺口，不断言历史事件绝对未发生。维护integrity-event只记录当前检查和建议，不代表宿主已撤权、取消、隔离或批准；实际控制仍需具权宿主执行。

审计工具可在有限结构/关系profile上通过且准确拒绝错误subject；其`production_eligible`仍为false，未测层保留unknown/not_run/not_implemented。对审查对象的fail与审计方法的pass分别输出，不把“检出了问题”计成业务测试通过。


## 正确否定与错误汇总的区分

已核验原始观察指出确定违例时，不允许独立摘要把subject改写为pass。审查证据一致性、被审对象符合性、审查任务verdict、交付可用性与发布各保留自己的作用域；正确报告对象fail可以是合格审查，不需要等待修复完成才能交付审查报告。

缺字段或缺导出证据不能把真实运行标记为不存在；unknown是某项事实的可判定性，不是整次运行的真实性。对已确定的误判追加精确纠正，其余成果分别核验。维护结果中evidence_integrity_result=pass或subject_conformance=fail均不自动产生真实任务confirmed或宿主批准。
