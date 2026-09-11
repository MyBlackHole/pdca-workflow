---
schema: pdca.work-release-manifest/v1
protocol_revision: 3.4.10
release_id: null
work_id: null
tree_revision: null
freeze_receipt_ref: null
freeze_receipt_digest: null
graph_ref: null
graph_digest: null
objects: []
node_bindings: []
known_issue_refs: []
limitations: []
---

# 工作产物发布候选清单

VERDICT-01：对象含object_id、role、ref、revision、digest、required与dependencies；节点绑定node/scene/task/attempt、delivery/独立终态、artifact、全部必需run与实际consumed_child_artifacts。清单固定后供新的审查任务读取，不包含未来审查或自身批准。

父run实际消费的每项孩子摘要必须等于此release选定版本；局部各自PASS不保证组合。缺项可发布为明确失败审查输入，不得声称成功release。目录latest或mtime不能选版本；全部对象实际解析并核对字节。
