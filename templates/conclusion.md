---
schema: pdca.conclusion/v3
task_id: null
baseline_digest: null
verdict: null
verdict_type_ref: null
check_confirmation_ref: null
disposition: null
candidate_refs: []
follow_up_refs: []
confirmed_package_ref: null
protocol_revision: 3.4.10
---

# 结论与处置

这是可变工作视图模板，verdict不能预填成功。Check确认绑定不可变审查包清单；confirmed_package_ref保存其位置。Act追加处置不覆盖已确认包，详见EVIDENCE-01。

## 逐项验收

| AC ID | pass/fail/unknown/not_run | 预期对象／实际读入对象 | 原始证据与actual | 采用或拒用理由／局限 |
|---|---|---|---|---|

## 总体判定

按VERDICT-01说明为什么为confirmed/partial/rejected；未运行项明确说明。判定与用户是否认可分开记录。

## 知识处置

按LEARN-01选择disposition，写理由、来源、复用价值和候选/已有节点引用。没有新增知识可以明确说明，不强制制造节点。

## 失败与后续行动

记录恢复、升级或独立跟进目标；风险未明不能直接归档。既有结论不因归档被改成成功。

## 当前版本测试、交付与独立审查

逐例/约束聚合，旧PASS与新产物不混用；delivery_usable及理由、issue/新attempt计划。审查场景单列subject_conformance，不能用任务verdict替代。


## 共享知识发布（仅合同明确包含时）

明确action=publish_definition、library_id/definition_id、精确release_manifest_ref/digest、base_revision/digest、独立review_refs和允许发布范围；由当前Check冻结对象经CONFIRM-01真实确认。普通任务判定认可不授予共享发布权；无此动作时明确not_applicable，不新增默认发布。授权在结论包外保存，避免自引用。EVOLVE-01仍须在提交边界复核对象/资源/当前base。
