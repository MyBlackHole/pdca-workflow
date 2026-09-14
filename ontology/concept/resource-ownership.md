---
schema: pdca.asset/v2
id: ontology:concept/resource-ownership
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: RESOURCE-01：独立上下文与写权分开
---

# RESOURCE-01：独立上下文与写权分开

业务动作需当前任务身份、用户批准的阶段写域和真实可用权限。路径用规范化realpath核对，防止符号链接和共享资源越界；目录名不是沙箱。记录写域与业务写域分离，不允许子任务覆盖父／兄弟记录或已固定证据。

并行任务只写获准不冲突区域；真实后端无法提供排他时明确合作式限制，并串行冲突部分或使用实际隔离。父Agent不靠心跳抢占；停止或租期到不等于旧写者已消失。

非幂等操作保留operation_id、提交状态及原始返回。结果未知先对账，不能靠重试猜成功。取消／恢复误建的新实例不得获得原业务写权，先停止并结清实际副作用。

本轮Act完成前结清在途操作与必要资源；任务archive文字不自动释放资源。归还或保留隔离区有实际依据，无法证明就明确unknown并阻断冲突后继。
