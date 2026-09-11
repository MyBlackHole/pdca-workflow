---
schema: pdca.scheduling-observation/v1
extension_revision: agent-dispatch.1
protocol_revision: 3.4.10
observation_id: null
work_id: null
tree_revision: null
requirements_basis_ref: null
requirements_basis_digest: null
pinned_graph_ref: null
pinned_graph_digest: null
capability_check_ref: null
trigger_event_ref: null
trigger_event_digest: null
event_order_ref: null
frontier: []
capacity_observations: []
decisions: []
spawn_receipt_refs: []
next_wakeup_refs: []
coverage: incomplete
---

# 一次调度机会的观测，不是新批准

宿主单写者保存，也可由既有控制记录内联后外层固定。不修改节点自己的task/阶段文件。

frontier 对照原目标/合法seed和图列出全部候选，每项含 task_key、input_refs/digests、依赖实际资格、资源/授权、eligible及依据。不能只列已派发项，不能把待确认任务当已结束。

capacity_observations 区分会话/执行位/在途创建、总量/占用/未知保留，绑定原生事实。decisions 对每个候选记录 submitted/deferred/blocked/already_inflight，及request_id、理由证据和下一唤醒；不得以“等待A终态”解释还有兼容容量的B。按每次原生接受/不明/失败更新余量后再决策；取消优先。

spawn_receipt_refs 引用实际工具返回及上下文/写权事实，不是构造的名字。序号来自可核验宿主事件顺序；不能拼接不同时间域的墙钟推断重叠。coverage 只有独立依据集合和已捕获事件齐备才为complete；缺口为incomplete，不是pass。此处complete仅为轨迹覆盖，不是PDCA业务完成或生产授权。
