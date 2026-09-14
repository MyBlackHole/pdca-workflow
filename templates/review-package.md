---
schema: pdca.review-package/v3
task_id: null
review_id: null
phase: null
baseline_digest: null
objects: []
protocol_revision: 3.4.11
---

# 不可变审查包清单草稿

按EVIDENCE-01从真实产物生成固定副本或不可变版本。objects每项记录role、固定ref、实际digest；包含当前门禁需要的AC映射、证据和结论。对象缺失不能以空清单通过。

先写固定对象，再写本清单；清单自身摘要由外部请求的subject_digest引用。不在此填入自身摘要、尚未产生的确认或转换回执。请求发出后禁止覆写；修改须新review_id。

工作版conclusion.md追加Act处置不会改变此包；原始包损坏或实际交付产物漂移仍需阻断。模板不是已生成的包。


## 共享知识发布（仅合同明确包含时）

明确action=publish_definition、library_id/definition_id、精确release_manifest_ref/digest、base_revision/digest、独立review_refs和允许发布范围；由当前Check冻结对象经CONFIRM-01真实确认。普通任务判定认可不授予共享发布权；无此动作时明确not_applicable，不新增默认发布。授权在结论包外保存，避免自引用。EVOLVE-01仍须在提交边界复核对象/资源/当前base。


## 结果消费核对

按 [EVIDENCE 消费顺序](../ontology/concept/pdca-evidence.md#evidence-consumption)核对最终字节、所用观察及对结论的影响，消费行放入既有AC映射。请求前与交付前各核对一次，不因Act增加章节继承旧Check；历史原件与本次纠错观察分别保留。
