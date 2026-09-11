---
schema: pdca.scenario-coverage/v3
work_id: null
tree_revision: null
scene: null
release_ref: null
writer_ref: null
rows: []
protocol_revision: 3.4.10
---

# 场景覆盖清单草稿

由宿主单写者根据固定节点交付更新；不能并发让每Agent覆写整表。rows或正文每项绑定node_id、attempt、task_id、agent_ref、delivery_ref/digest、phase_completion、delivery_usable/subject_conformance、issue/stale。

## 必需节点覆盖

| node_id | attempt/task_id | 真实新Agent | 固定输入/交付 | 完整PDCA或中断 | 当前结果 | 未决/失效 |
|---|---|---|---|---|---|---|

不得以根任务替代孩子或删除失败attempt。最终发布选择明确版本，不按最新时间戳猜。
