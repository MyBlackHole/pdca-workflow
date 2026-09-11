---
schema: pdca.asset/v2
id: ontology:domain/tdd-mocking
name: tdd-mocking
summary: mocking 辅助文档
description: 'TDD 技能辅助文档。

  '
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/tdd-mocking/3.1.0
relations:
  relates_to:
  - ontology:concept/domain-modeling
  - ontology:concept/pdca-task
  instance_of:
  - ontology:concept/knowledge-artifact
revision: 3.1.0
authority: reference
validation:
  structural_checks:
  - 递归解析本节点身份及关系列表；目标 ID 必须可定位。引用数量不作为行为验证。
  claim_status: unverified
  adoption: claim_review_required
semantic_kind: individual
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# 何时 Mock

仅在**系统边界**处 mock：

- 外部 API（支付、邮件等）
- 数据库（有时 —— 优先使用测试数据库）
- 时间/随机数
- 文件系统（有时）

不要 mock：
- 你自己的模块/类
- 内部协作者
- 你能控制的任何东西

## 可 Mock 性设计

在系统边界处，设计易于 mock 的接口：

**1. 依赖注入**

外部依赖通过参数传入，而非内部创建：

```typescript
// 易 mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// 难 mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. SDK 风格接口优于通用 fetcher**

为每个外部操作创建独立函数，而非一个带条件逻辑的通用函数：

```typescript
// 好：每个函数独立可 mock
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// 坏：mock 需要在内部加条件逻辑
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

SDK 风格的优点：
- 每个 mock 返回一种特定形状
- 测试设置中无需条件逻辑
- 更容易看到测试覆盖了哪些端点
- 每个端点有类型安全
