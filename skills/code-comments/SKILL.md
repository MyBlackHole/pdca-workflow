---
name: code-comments
description: Use when adding Chinese annotation comments to code, when asked to translate/add supplementary comments in Chinese to existing code, or when needing to embed business-understanding diagrams (ASCII / Mermaid) alongside source code for clearer business logic visualization, or when documenting technical principles / architecture decisions / algorithm mechanisms / system architecture understanding inline for deeper code comprehension
---

# Adding Chinese Code Comments (代码备注)

## Overview

Adding Chinese comments **directly into the original source files** as **supplementary** annotations — editing the file in-place, not creating a separate annotation file or copy. The original English comments are the authoritative documentation — Chinese comments are auxiliary translations/explanations that must **never** replace them.

**思考语言要求**: 处理中文代码注释相关任务时，AI 的内部推理、分析和决策过程须使用简体中文。判断哪些代码段需要中文注释、考虑注释措辞、验证英文注释是否被保留等思考环节，均应以中文进行。

## Core Rules

1. **Add comment blocks BEFORE important functions/classes/types** — a Chinese summary block above the declaration
2. **Add comment lines BEFORE key code segments** — a Chinese explanation line before the code block it describes
3. **PRESERVE all original English comments** — do NOT remove, modify, or overwrite them. They stay exactly as-is.
4. **Chinese comments are SUPPLEMENTARY only** — added alongside, never replacing, the original English
5. **EDIT THE ORIGINAL FILE IN-PLACE** — do not create a separate annotation file, a copy, or a new file. Modify the original source file directly.
6. **Do NOT change any code** — comments-only edits
7. **Use `// 备注:` as unified Chinese prefix** — keeps format consistent and searchable across the codebase
8. **Add business-understanding diagrams for complex business logic** — when a function/class/module contains non-trivial business flow (multi-step process, state transitions, cross-module interactions), embed an ASCII or Mermaid diagram before the code block to visualize the business intent. Diagrams are **supplementary visual explanations**, not a replacement for comments.
9. **Add technical principle annotations for non-obvious mechanisms** — when code involves subtle algorithms, concurrency models, performance-critical decisions, or design trade-offs, add a structured explanation of WHY this approach was chosen, HOW it works internally, and WHAT invariants must hold. Principle annotations target developers reading the code who need to understand the rationale, not just the behavior.
10. **Add system-level annotations for cross-cutting concerns** — when code involves concurrency models, error propagation strategies, data lifecycles, or security boundaries, add annotations that describe how the code interacts with the broader system. These target developers who need to understand the orchestration, data flow, and failure modes, not just a single module.

## Comment Formats

**Prefix convention**: All Chinese annotations use `// 备注:` as a unified prefix.
Exception: File headers use `// =====` separator style.

### File header
For complex files, add at the very top of the file:

```
// ============================================
// 文件说明：用户认证相关中间件
// 包含：JWT 验证、角色权限检查、登录状态维护
// ============================================
// original English header comment — DO NOT TOUCH
```

### Function-level comment block
Place BEFORE the function declaration:

```
// 备注：处理用户数据，验证并规范化邮箱，计算活跃度得分
// 备注：@param user - 用户对象，需包含 email 字段
// 备注：@returns 标准化用户数据对象
// original English comment — DO NOT TOUCH
function existingFunction(param) {
```

### Class / Interface / Type comment block
Place BEFORE the class/interface/type declaration:

```
// 备注：用户数据仓储层
// 备注：负责用户数据的 CRUD 操作及缓存管理
// 备注：依赖 RedisService, DatabaseService
// original English comment — DO NOT TOUCH
class UserRepository {
```

### Code segment comment line
Place BEFORE the code line/key segment — Chinese on its own line, adjacent to the original English:

```
  // 备注：验证用户输入，确保 user 对象及其 email 属性存在
  // original English comment — DO NOT TOUCH
  const result = someOperation();
```

**Key rule**: Chinese and English must be on separate lines. The order of adjacent lines (Chinese above English or English above Chinese) is flexible — both are acceptable.

## When NOT to Add Chinese Comments

Avoid adding `// 备注:` in these cases — the English is already sufficient:

| Situation | Example | Why Skip |
|-----------|---------|----------|
| Self-explanatory one-liners | `count++`, `flag = !flag` | Code already reads itself |
| Simple getter/setter | `get name() { return this._name; }` | Obvious from signature |
| Trivial type conversion | `String(value)`, `Number(str)` | Type name says it all |
| Existing English already clear | `// Check if user is admin` | English explains it sufficiently |
| Boilerplate / framework hooks | `useEffect`, `componentDidMount` | Framework conventions are standard |

**Rule of thumb**: If you have to think about whether it needs a Chinese note — it probably does. If it's immediately obvious — skip it.

## 业务理解图 (Business Understanding Diagrams)

For complex business logic, supplement Chinese comments with **inline diagrams** that visualize the business flow, state transitions, or component interactions. Diagrams make business intent immediately graspable — a picture is worth a thousand words.

### When to Add Diagrams

| Scenario | Example | Recommend |
|----------|---------|-----------|
| Multi-step business process (3+ steps) | Order fulfillment pipeline | ✅ ASCII flow chart |
| State transitions of a business object | Order status: pending→paid→shipped→done | ✅ State diagram |
| Cross-module interaction flow | Auth service calls User service → Redis → DB | ✅ Sequence diagram |
| Conditional branching business logic | Discount rules: if VIP→20%, if new user→10% | ✅ Decision flow |
| Complex data transformation pipeline | Raw data → clean → enrich → aggregate → output | ✅ Pipeline diagram |
| Single-step / trivial operation | Simple getter delegating to repository | ❌ Skip — comment is enough |

### Diagram Types (choose by context)

**1. ASCII 流程图 (ASCII Flow Chart)**

Use `┌─┐`, `│ │`, `└─┘`, `─▶`, `▼` box-drawing characters. Best for:
- Linear business processes
- Decision branches
- Module call chains

**2. Mermaid 代码图 (Mermaid-style Diagram)**

Use Mermaid-compatible text syntax. Best for:
- Complex state machines (many states/transitions)
- Sequence diagrams with multiple participants
- Rich relationship diagrams

**3. 文本关系图 (Text Relationship Diagram)**

Use indented tree or arrow-based notation. Best for:
- Module/class dependency structures
- Hierarchical business domain models
- Layered architecture overviews

### Diagram Placement Rules

1. **File-level business flow** → Add after the file header, at the very top of the file
2. **Function-level business process** → Add BEFORE the `// 备注:` text block of the function, as the outermost layer
3. **Class-level domain model** → Add BEFORE the `// 备注:` comment block of the class
4. **Module interaction** → Add at the module boundary functions that orchestrate cross-module calls

### Prefix Convention for Diagrams

- **ASCII diagrams**: Each line starts with `// 备注：` — consistent with regular comments
- **Mermaid diagrams**: Each line starts with `// 备注：`, and the diagram is the **only** content in the comment block
- **Legend**: Always add a brief Chinese legend at the bottom of the diagram explaining the symbols

### Diagram Examples

**例 1：ASCII 流程图 — 文件级别业务流 (File-level Business Flow)**

```
// ============================================
// 文件说明：订单处理核心模块
// 包含：订单创建、支付、发货、退款全流程
// ============================================
// 备注：订单业务主流程：
// 备注：┌──────────┐     ┌──────────┐     ┌──────────┐
// 备注：│ 用户下单  │────▶│ 库存检查  │────▶│ 支付处理  │
// 备注：└──────────┘     └──────────┘     └──────────┘
// 备注：                                      │
// 备注：                                      ▼
// 备注：                  ┌──────────┐     ┌──────────┐
// 备注：                  │ 退款处理  │◀────│ 发货流程  │
// 备注：                  └──────────┘     └──────────┘
// 备注：图例：┌──┐ 表示处理节点，─▶ 表示流转方向
// original English header comment — DO NOT TOUCH
```

**例 2：ASCII 决策流 — 函数级别业务分支 (Function-level Decision Flow)**

```
// 备注：折扣计算逻辑决策流：
// 备注：          ┌──────────────────┐
// 备注：          │ 开始计算折扣       │
// 备注：          └────────┬─────────┘
// 备注：                   │
// 备注：                   ▼
// 备注：          ┌──────────────────┐
// 备注：          │ 用户是否 VIP？    │──── 否 ──▶ 普通折扣 10%
// 备注：          └────────┬─────────┘
// 备注：                   │ 是
// 备注：                   ▼
// 备注：          ┌──────────────────┐
// 备注：          │ 是否满 3 年 VIP？ │──── 否 ──▶ VIP 折扣 20%
// 备注：          └────────┬─────────┘
// 备注：                   │ 是
// 备注：                   ▼
// 备注：          ┌──────────────────┐
// 备注：          │ 老 VIP 折扣 30%  │
// 备注：          └──────────────────┘
// 备注：处理用户数据，验证并规范化邮箱，计算活跃度得分
// 备注：@param user - 用户对象，需包含 email 字段
// 备注：@returns 标准化用户数据对象
// original English comment — DO NOT TOUCH
function calculateDiscount(user) {
```

**例 3：Mermaid 状态图 — 复杂状态流转 (Complex State Transitions)**

```
// 备注：订单状态机 (Mermaid):
// 备注：
// 备注：stateDiagram-v2
// 备注：  [*] --> PENDING : 创建订单
// 备注：  PENDING --> PAID : 支付成功
// 备注：  PENDING --> CANCELLED : 用户取消
// 备注：  PAID --> SHIPPED : 发货
// 备注：  SHIPPED --> DELIVERED : 确认收货
// 备注：  DELIVERED --> [*] : 完成
// 备注：  PAID --> REFUNDING : 申请退款
// 备注：  REFUNDING --> REFUNDED : 退款成功
// 备注：  REFUNDED --> [*]
// 备注：
// 备注：图例：[*] 起始/终态，--> 状态转移，:后为触发条件
// 备注：订单状态枚举类，定义订单在其生命周期中的所有可能状态
// original English comment — DO NOT TOUCH
enum OrderStatus {
```

**例 4：Mermaid 时序图 — 跨模块调用流程 (Cross-module Sequence)**

```
// 备注：订单创建跨模块调用流程 (Mermaid):
// 备注：
// 备注：sequenceDiagram
// 备注：  participant Client as 客户端
// 备注：  participant API as 订单API
// 备注：  participant Order as 订单服务
// 备注：  participant Inv as 库存服务
// 备注：  participant Pay as 支付服务
// 备注：
// 备注：  Client->>API: POST /orders
// 备注：  API->>Order: 创建订单请求
// 备注：  Order->>Inv: 检查库存
// 备注：  Inv-->>Order: 库存充足
// 备注：  Order->>Pay: 发起支付
// 备注：  Pay-->>Order: 支付成功
// 备注：  Order-->>API: 订单创建完成
// 备注：  API-->>Client: 201 Created
// 备注：
// 备注：图例：->> 同步调用，-->> 异步返回
// 备注：创建新订单的主流程编排函数
// original English comment — DO NOT TOUCH
async function createOrder(orderData) {
```

**例 5：文本关系图 — 模块依赖结构 (Module Dependency)**

```
// 备注：模块依赖关系：
// 备注：
// 备注：  OrderService (订单服务)
// 备注：    ├──> InventoryClient (库存客户端)
// 备注：    │     └──> Database (库存表)
// 备注：    ├──> PaymentGateway (支付网关)
// 备注：    │     └──> PaymentProvider (第三方支付)
// 备注：    ├──> NotificationService (通知服务)
// 备注：    │     └──> SmsProvider + EmailProvider
// 备注：    └──> OrderRepository (订单仓储)
// 备注：          └──> Database (订单表)
// 备注：
// 备注：图例：──> 表示直接依赖
// original English comment — DO NOT TOUCH
class OrderService {
```

### Diagram Design Principles

| Principle | Explanation |
|-----------|-------------|
| **Keep it small** | Max 15-20 lines per diagram. If bigger, split into sub-diagrams at each sub-function |
| **One intent per diagram** | Each diagram should answer ONE business question: flow, state, or structure, not all three |
| **Chinese labels** | All node labels, edge descriptions, and legends MUST be in Chinese |
| **Add legend** | Every diagram must end with `// 备注：图例：...` explaining the symbols used |
| **ASCII first** | Prefer ASCII box-drawing for simple flows (works everywhere). Use Mermaid only when state/sequence complexity demands it |
| **No code in diagrams** | Diagrams describe **business concepts**, not code mechanics. Use domain language, not variable names |

## 原理性注释 (Technical Principle Comments)

For code involving non-trivial technical mechanisms, supplement Chinese comments with **principle annotations** that explain WHY an approach was chosen, HOW it works internally, and WHAT invariants must hold. These target **developers** who need to understand the rationale and mechanics — not business stakeholders.

The fundamental principle: **explain WHY, not WHAT**. The code itself already says WHAT it does. The annotation explains WHY it does it that way, and what alternatives were considered.

### When to Add Principle Annotations

| Scenario | Example | Recommend |
|----------|---------|-----------|
| Non-obvious design choice | Why Channel not Mutex | ✅ Architecture Decision |
| Complex algorithm | Token bucket, LRU cache, Raft consensus | ✅ Algorithm Walkthrough |
| Critical invariants | DB constraints, data structure invariants | ✅ Invariants & Contracts |
| State machine with guards | Order status with transition rules | ✅ State Machine Mechanics |
| Repeated CR questions | "Why not use stdlib?" "Why this pattern?" | ✅ FAQ Annotation |
| Low-level wire/on-wire format | Protocol buffers, packet layout, encoding | ✅ Wire Format Diagram |
| Obvious/simple code | `if (x > 0) return x` | ❌ Skip — code is self-evident |

### Annotation Types

**1. 架构决策注释 (Architecture Decision Record)**

Covers: trade-offs, alternatives considered, quantified rationale. Place **before** the implementation block.

Format:
```
// 备注：决策：标题，概括决策内容
// 备注：
// 备注：背景：触发决策的上下文
// 备注：
// 备注：方案 A: 方案名称及简述
// 备注：  优点：...
// 备注：  缺点：...
// 备注：
// 备注：方案 B: 方案名称及简述
// 备注：  优点：...
// 备注：  缺点：...
// 备注：
// 备注：结论：选 B 及核心原因
// 备注：参考：链接或文献
```

**2. 算法机理注释 (Algorithm Walkthrough)**

Covers: step-by-step execution, time/space complexity, critical implementation details. Place **before** the algorithm implementation.

Format:
```
// 备注：算法：名称及一句话概括
// 备注：
// 备注：时间线示例（输入 = ...）:
// 备注：  T=0  state → action
// 备注：  T=1  state → action
// 备注：  ...
// 备注：
// 备注：关键实现细节：
// 备注：  - 细节 1
// 备注：  - 细节 2
// 备注：复杂度：O(n), 空间 O(1)
// 备注：参考：链接
```

**3. 不变量与契约注释 (Invariants & Contracts)**

Covers: must-always-be-true conditions, pre/post-conditions, violation consequences. Place **before** the data structure / function it constrains.

Format:
```
// 备注：不变量（任何时候必须保持）：
// 备注：  1. 规则 1 — 业务/技术描述
// 备注：  2. 规则 2 — 业务/技术描述
// 备注：
// 备注：违反后果：...
```

**4. 状态机机理注释 (State Machine Mechanics)**

Covers: legal/illegal transitions, guard conditions, concurrency handling. Place **before** the state machine implementation.

Format:
```
// 备注：状态机：名称
// 备注：
// 备注：合法转移：
// 备注：  STATE_A → STATE_B   转移触发条件
// 备注：  STATE_B → STATE_C   转移触发条件
// 备注：
// 备注：非法转移（被显式阻止的）：
// 备注：  STATE_A → STATE_C   阻止原因
// 备注：
// 备注：转移守卫条件：
// 备注：  STATE_A→STATE_B:  requires condition
// 备注：
// 备注：并发处理：锁/乐观锁/事务策略
```

**5. 原理性 FAQ 注释 (Mechanism FAQ)**

Covers: questions that repeatedly come up in code review, organized as Q&A. Place **before** the relevant code block.

Format:
```
// 备注：常见原理问题：
// 备注：
// 备注：Q: 为什么不用 X？
// 备注：A: 原因（最好有量化依据）。
// 备注：
// 备注：Q: 为什么单独传 ctx 而非用 struct 字段？
// 备注：A: 原因。
```

**6. 内部机制注释 (Internal Mechanics / Wire Format)**

Covers: binary/on-wire layouts, encoding schemes, bit-level protocol details. Place **before** the serialization/deserialization code.

Format:
```
// 备注：帧格式 (Wire Format)：
// 备注：  ┌─────┬──────┬────────┬──────────┐
// 备注：  │字段 A│字段 B │ 字段 C  │ 字段 D   │
// 备注：  │ nB  │ mB   │  kB    │  变长     │
// 备注：  ├─────┼──────┼────────┼──────────┤
// 备注：  │示例值│示例值│ 示例值  │ 示例值    │
// 备注：  └─────┴──────┴────────┴──────────┘
// 备注：
// 备注：字段 A: bit7=X, bit6=Y, bit0=Z
// 备注：字段 B: 单调递增，用于去重
```

### Principle Annotation Examples

**例 1：架构决策 — 为什么用 Channel 而非 Mutex**

```
// 备注：决策：为什么用 Channel 而非 Mutex 保护 WebSocket 连接池？
// 备注：
// 备注：背景：连接池在 20 个 goroutine 中并发读写，峰值 10K+ 连接
// 备注：
// 备注：方案 A: sync.RWMutex
// 备注：  优点：实现简单，熟悉的人多
// 备注：  缺点：高并发下读锁争用严重，pprof 显示 15% 时间花在锁等待
// 备注：
// 备注：方案 B: Go Channel 串行化
// 备注：  优点：无锁竞争，吞吐量稳定，天然的背压机制
// 备注：  缺点：需要理解 CSP 模型，调试难度略高
// 备注：
// 备注：结论：选 B。压测显示同场景下 P99 延迟从 120ms 降到 35ms
// 备注：参考：https://github.com/golang/go/wiki/LearnConcurrency
// original English comment — DO NOT TOUCH
type WSConPool struct {
```

**例 2：算法机理 — Token Bucket 限流**

```
// 备注：算法：Token Bucket 限流（每秒填充 r 个令牌，桶容量 b）
// 备注：
// 备注：时间线示例（r=5, b=10）:
// 备注：  T=0ms   桶=[TTTTTTTTTT] 10/10  满
// 备注：  T=0ms   请求到达，消耗 1 → [TTTTTTTTT·] 9/10
// 备注：  T=200ms 填充 1.0 → [TTTTTTTTTT] 10/10
// 备注：  T=200ms 突发 8 请求 → [TT········] 2/10
// 备注：  T=300ms 第 9 请求到达 → 拒绝（桶空）
// 备注：
// 备注：关键实现细节：
// 备注：  - 使用浮点数累积 lastRefillTime 差值，避免定时器开销
// 备注：  - tokens 上限 max(b)，不会累积超过桶容量
// 备注：  - 允许短时突发（最多 b 个），但长期平均速率被限制在 r/s
// 备注：复杂度：O(1) 每次请求
// 备注：参考：https://en.wikipedia.org/wiki/Token_bucket
// original English comment — DO NOT TOUCH
func (tb *TokenBucket) Allow() bool {
```

**例 3：不变量 — 订单聚合根约束**

```
// 备注：不变量（任何时候必须保持）：
// 备注：  1. order.items.length > 0 — 订单至少包含一个商品
// 备注：  2. order.total === Σ item.price — 总价=明细加和，不允许手动改
// 备注：  3. order.status === 'REFUNDED' ⇒ order.refundAmount > 0
// 备注：  4. user.vipLevel ∈ [0, 5] — 0=普通, 1=银卡, 2=金卡, 3=白金, 4=钻石, 5=黑卡
// 备注：
// 备注：违反后果：下单页面金额显示不一致（违反 2），财报对不上（违反 3）
// original English comment — DO NOT TOUCH
class Order {
```

**例 4：状态机 — 订单状态转移**

```
// 备注：状态机：OrderStateMachine
// 备注：
// 备注：合法转移：
// 备注：  PENDING → PAID        支付回调成功
// 备注：  PENDING → CANCELLED   用户手动取消（必须在 30min 内）
// 备注：  PAID → REFUNDING      用户申请退款（必须在发货前）
// 备注：  PAID → SHIPPED        仓库发货（必须有物流单号）
// 备注：  SHIPPED → DELIVERED   用户确认/系统自动（发货后 15 天）
// 备注：
// 备注：非法转移（被显式阻止的）：
// 备注：  PENDING → SHIPPED     未支付不能发货
// 备注：  REFUNDING → PAID      退款流程不可逆
// 备注：
// 备注：转移守卫条件：
// 备注：  PENDING→CANCELLED:  requires order.createAt + 30min > now
// 备注：  PAID→REFUNDING:     requires no shipment record
// 备注：  DELIVERED→REFUNDING: requires now - deliveredAt < 7days
// 备注：
// 备注：并发处理：UPDATE ... WHERE status = :old 乐观锁
//     if (result.affectedRows === 0) throw ConflictError
// original English comment — DO NOT TOUCH
func (m *OrderStateMachine) Transition(ctx context.Context, to Status) error {
```

**例 5：FAQ — 反复被问的设计问题**

```
// 备注：常见原理问题：
// 备注：
// 备注：Q: 为什么不用标准库的 sort.Slice？
// 备注：A: 线上 pprof 显示 sort.Slice 反射开销占排序总时间的 40%。
// 备注：   手写 sort.Interface 实现后，单次排序时间从 2.3ms 降到 1.1ms。
// 备注：
// 备注：Q: 为什么单独传 ctx 而非用结构体字段？
// 备注：A: 请求级上下文，每次调用都不同。如果放在 struct 里，
// 备注：   并发场景下会出现 ctx 覆盖，导致 trace 串联错误。
// 备注：
// 备注：Q: 这个 for 循环为什么不用 range？
// 备注：A: range 在迭代时会复制每个元素，这个结构体 512 字节。
// 备注：   用 index 访问避免复制，benchmark 显示减少 60% 内存分配。
// original English comment — DO NOT TOUCH
func processItems(items []HeavyStruct) {
```

**例 6：Wire Format — 消息帧结构**

```
// 备注：消息帧格式 (Wire Format)：
// 备注：  ┌─────┬──────┬────────┬──────────┬─────────┐
// 备注：  │标志位│ 序列号│ 消息类型 │ 负载长度  │ 负载    │
// 备注：  │ 1B  │  4B  │   1B   │   4B     │ 变长    │
// 备注：  ├─────┼──────┼────────┼──────────┼─────────┤
// 备注：  │ 0x01 │ 0001 │  0x0A  │ 0x000010 │ 16 bytes│
// 备注：  └─────┴──────┴────────┴──────────┴─────────┘
// 备注：
// 备注：标志位: bit7=压缩, bit6=加密, bit0=需要ACK
// 备注：序列号: 单调递增，用于去重和乱序重排
// 备注：消息类型: 0x0A=心跳, 0x0B=业务数据, 0x0C=控制指令
// original English comment — DO NOT TOUCH
func (f *Frame) Decode(raw []byte) error {
```

### Principle Annotation Design Principles

| Principle | Explanation |
|-----------|-------------|
| **Explain WHY, not WHAT** | The code says WHAT it does. Comments explain WHY it does it that way |
| **Give alternatives** | Don't just say "used Channel" — say why not Mutex. Shows due diligence |
| **Quantify the rationale** | "Performs better" is weak. "P99 from 120ms to 35ms" is convincing |
| **Write for your future self** | Assume you'll forget the context in 3 months. Be explicit |
| **Cite references** | Link to Wikipedia, RFC, paper, or internal doc for deeper reading |
| **Time-series examples** | For algorithms, show time step evolution. More intuitive than pseudocode |
| **One concern per block** | Decision block = one decision. FAQ block = related Q&As. Don't mix |

## 系统层面理解 (System-Level Understanding)

For cross-cutting concerns that span multiple modules or layers, supplement Chinese comments with **system-level annotations** that describe how the code interacts with the broader system — the concurrency model, how errors propagate, the lifecycle of key data objects, and where security boundaries lie. These target **developers who need to understand the orchestration**, not just a single function.

Principle annotations explain "why this code works this way." System-level annotations explain "how this code fits into the whole system."

### When to Add System-Level Annotations

| Scenario | Example | Recommend |
|----------|---------|-----------|
| Concurrent execution model | Fan-out workers, channel-based sync, shared memory | ✅ Concurrency Model |
| Error handling strategy | Where errors are caught, wrapped, retried, or surfaced | ✅ Error Propagation |
| Data flow across layers | DTO → Domain → Entity serialization pipeline | ✅ Data Lifecycle |
| Security trust boundaries | Where input is validated, where authentication happens | ✅ Security Boundary |
| Trivial sync (single-threaded) | Sequential code with no concurrency concerns | ❌ Skip — no need |
| Happy-path-only errors | Simple script where all errors panic/exit | ❌ Skip — not a strategy |

### System-Level Annotation Types

**1. 并发模型注释 (Concurrency Model)**

Covers: goroutine/thread topology, shared vs private data, synchronization strategy, deadlock risk analysis. Place **before** the concurrency-critical code (e.g., the function that spawns goroutines).

Format:
```
// 备注：并发模型：
// 备注：
// 备注：  主 goroutine（HTTP handler）
// 备注：    │
// 备注：    ├── 扇出 N 个 worker goroutine 并行处理
// 备注：    │   每个 worker 持有独立连接，无需同步
// 备注：    │
// 备注：    ├── 聚合结果写入 channel（容量 N，阻塞式）
// 备注：    │
// 备注：    └── 主 goroutine 从 channel 读取，串行化处理
// 备注：
// 备注：共享数据：无（worker 之间不共享，通过 channel 通信）
// 备注：同步方式：channel（无锁设计）
// 备注：并发度：max(1, min(cpu*2, N))，由 semaphore channel 控制
// 备注：
// 备注：竞态风险：无（all data is either local or communicated via channel）
// 备注：死锁风险：channel 容量 = worker 数，不会写满阻塞
```

**2. 错误传播策略注释 (Error Propagation)**

Covers: layer-by-layer error handling strategy, error type classification, retry vs fail vs circuit-break decisions. Place **at the module entry point** or in the error-handling middleware.

Format:
```
// 备注：错误处理策略：
// 备注：
// 备注：  Repository 层：原始错误 + 包装上下文
// 备注：    └─→ err = fmt.Errorf("db: find order %d: %w", id, ErrNotFound)
// 备注：
// 备注：  Service 层：根据错误类型做不同处理
// 备注：    ├── ErrNotFound     → 返回 nil, nil（空结果不等于异常）
// 备注：    ├── ErrConflict     → 重试（最多 3 次，指数退避）
// 备注：    ├── ErrTimeout      → 返回 circuit breaker error
// 备注：    └── 其他            → 返回 500，异步打告警
// 备注：
// 备注：  Handler 层：统一写 errorHandler middleware
// 备注：    └── 根据 error type → HTTP status code 映射
// 备注：
// 备注：不向上透传的：DB deadlock（自动重试）、临时网络错误（重试）
// 备注：必须向上透传的：校验错误、权限错误、资源不存在
```

**3. 数据生命周期注释 (Data Lifecycle)**

Covers: data object transformation across layers, serialization boundaries, caching strategy, lifecycle stages. Place **at the aggregate root or main data flow entry point**.

Format:
```
// 备注：数据生命周期：<数据对象名>
// 备注：
// 备注：  Input         → Layer: 描述（格式）
// 备注：    ↓
// 备注：  Stage 2       → Layer: 描述（格式）
// 备注：    ↓
// 备注：  Stage 3       → Layer: 描述（格式）
// 备注：
// 备注：注意事项：
// 备注：  - XXXX 层只出现什么，不出现什么
// 备注：  - XXXX 对象只存在于什么层
```

**4. 安全边界注释 (Security Boundary)**

Covers: trust boundaries, validation checkpoints, authentication/authorization decisions, data sanitization. Place **at the request entry point** or where external data first enters the system.

Format:
```
// 备注：安全边界：
// 备注：
// 备注：  ┌─ 信任边界 ─────────────────────────┐
// 备注：  │ [用户输入] → 校验器 → [已校验数据] → 业务逻辑│
// 备注：  │   ↑              ↑                  │
// 备注：  │ 未信任         已信任                │
// 备注：  └──────────────────────────────────────┘
// 备注：
// 备注：校验点：
// 备注：  1. [x] 输入 JSON schema 验证
// 备注：  2. [x] 用户身份认证 (JWT verify)
// 备注：  3. [x] 权限校验 (RBAC)
// 备注：  4. [x] SQL 注入防护（参数化查询）
// 备注：  5. [ ] 频率限制（TODO: 接入 rate limiter）
// 备注：
// 备注：信任假设：所有外部输入在到达业务逻辑前必须经过校验
```

### System-Level Examples

**例 1：并发模型 — 扇出/聚合模式**

```
// 备注：并发模型：
// 备注：
// 备注：  主 goroutine（HTTP handler）
// 备注：    │
// 备注：    ├── 扇出 10 个 worker goroutine 并行查库存
// 备注：    │   每个 worker 持有独立连接，无需同步
// 备注：    │
// 备注：    ├── 聚合结果写入 channel（容量 10，阻塞式）
// 备注：    │
// 备注：    └── 主 goroutine 从 channel 读取，串行化处理
// 备注：
// 备注：共享数据：无（worker 之间不共享，通过 channel 通信）
// 备注：同步方式：channel（无锁设计）
// 备注：并发度：max(1, min(cpu*2, 10))，由 semaphore channel 控制
// 备注：
// 备注：竞态风险：无（all data is either local or communicated via channel）
// 备注：死锁风险：channel 容量 = worker 数，不会写满阻塞
// original English comment — DO NOT TOUCH
func batchCheckInventory(ctx context.Context, skus []string) ([]Stock, error) {
```

**例 2：错误传播 — 三层错误策略**

```
// 备注：错误处理策略：
// 备注：
// 备注：  Repository 层：原始错误 + 包装上下文
// 备注：    └─→ err = fmt.Errorf("db: find order %d: %w", id, ErrNotFound)
// 备注：
// 备注：  Service 层：根据错误类型做不同处理
// 备注：    ├── ErrNotFound     → 返回 nil, nil（空结果不等于异常）
// 备注：    ├── ErrConflict     → 重试（最多 3 次，指数退避）
// 备注：    ├── ErrTimeout      → 返回 circuit breaker error
// 备注：    └── 其他            → 返回 500，异步打告警
// 备注：
// 备注：  Handler 层：统一写 errorHandler middleware
// 备注：    └── 根据 error type → HTTP status code 映射
// 备注：
// 备注：不向上透传的：DB deadlock（自动重试）、临时网络错误（重试）
// 备注：必须向上透传的：校验错误、权限错误、资源不存在
// original English comment — DO NOT TOUCH
type OrderService struct {
```

**例 3：数据生命周期 — 订单数据**

```
// 备注：数据生命周期：订单
// 备注：
// 备注：  HTTP body          → Controller: 解析 JSON → OrderDTO
// 备注：    ↓
// 备注：  OrderDTO           → Service: DTO → Order domain object
// 备注：    ↓
// 备注：  Order (domain)     → Service: 业务校验 + 计算
// 备注：    ↓
// 备注：  OrderEntity        → Repository: domain → entity → DB
// 备注：    ↓
// 备注：  DB row             → DB
// 备注：    ↓
// 备注：  OrderEntity        → Repository: DB → entity → domain + events
// 备注：    ↓
// 备注：  Order (domain)     → Service: 触发领域事件
// 备注：    ↓
// 备注：  OrderResponse      → Controller: domain → response JSON
// 备注：
// 备注：注意事项：
// 备注：  - DTO 只存在于 Controller 层，不在 Service 层使用
// 备注：  - Entity 有 DB 字段注解，不暴露到 API
// 备注：  - Domain 对象不含 DB/API 注解，纯业务
// original English comment — DO NOT TOUCH
func CreateOrder(ctx context.Context, dto OrderDTO) (*OrderResponse, error) {
```

**例 4：安全边界 — 请求处理管道**

```
// 备注：安全边界：
// 备注：
// 备注：  ┌─ 信任边界 ──────────────────────────────┐
// 备注：  │                                           │
// 备注：  │  [用户输入] → 校验器 → [已校验数据] → 业务逻辑 │
// 备注：  │    ↑              ↑                       │
// 备注：  │  未信任         已信任                     │
// 备注：  └───────────────────────────────────────────┘
// 备注：
// 备注：校验点：
// 备注：  1. [x] 输入 JSON schema 验证（长度、类型、枚举值）
// 备注：  2. [x] 用户身份认证 (JWT verify)
// 备注：  3. [x] 权限校验 (RBAC)
// 备注：  4. [x] SQL 注入防护（参数化查询）
// 备注：  5. [ ] 频率限制（TODO: 接入 rate limiter）
// 备注：
// 备注：信任假设：所有外部输入在到达业务逻辑前必须经过校验
// original English comment — DO NOT TOUCH
func (m *Middleware) Chain(next http.Handler) http.Handler {
```

### System-Level Design Principles

| Principle | Explanation |
|-----------|-------------|
| **Architecture, not implementation** | Describe how pieces fit together, not how each piece works internally |
| **Trace the complete path** | Error propagation must show ALL layers (handler→service→repo), not just one |
| **Mark secure/incomplete items** | Use `[x]` for done, `[ ]` for known gaps, `TODO` for planned work |
| **Include failure modes** | Concurrency model MUST state deadlock/free risk; error strategy MUST state what is NOT retried |
| **Use layer terminology** | Names like "Controller → Service → Repository" are universal — prefer them over custom names |

## Common Mistakes

| Mistake | Why It's Wrong | Correct |
|---------|---------------|---------|
| Deleting `// Validate input` and replacing with `// 验证输入` | Original English comment lost | Keep `// Validate input`, add `// 验证输入` as a separate line |
| Merging `// Process user data` into a larger Chinese block | Original wording lost | Keep the original comment line, add Chinese block separately |
| Claiming "retained original comments" but they're gone | Self-deception — verify with explicit check | After editing, re-read the file and confirm every original comment still exists |
| Adding Chinese comment replacing an English one on the same line | Original comment overwritten | Keep original on its own line, add Chinese on a separate adjacent line |
| Creating a separate annotation file instead of editing the original | Comments detached from source code | Edit the original file directly — use Edit tool to insert Chinese comments inline |
| Over-annotating trivial code (`i++` → `// 备注：自增i`) | Noise that hurts readability | Skip obvious one-liners — English is sufficient |
| Using inconsistent Chinese prefix (mix of `// 备注:`, `// 说明:`, `// 中文:`) | Hard to search/filter later | Always use `// 备注:` — consistent and searchable |
| 用英文思考再决定加什么中文注释 | 思考语言与产出语言不一致，导致注释措辞生硬不自然 | 从思考阶段就使用中文，直接产生贴切的中文注释 |
| 图表画得太大（30+行） | 占据过多视觉空间，反而降低可读性 | 控制在 15-20 行内，复杂流程拆到子函数中去 |
| 图表中使用代码变量名而非业务概念 | 不具备业务知识的人看不懂，违背"业务理解"初衷 | 节点标签使用中文业务术语，如"待支付"而非"status === 'PENDING'" |
| 遗漏图例说明 | 读者可能不熟悉 ASCII 框图约定或不理解符号含义 | 每张图最后一行给出 `// 备注：图例：...` |
| 同一张图混合流程+状态+结构 | 图意混乱，难以快速理解 | 一张图只回答一个业务问题：flow / state / structure 选其一 |
| 为简单逻辑硬加图表 | `if (isAdmin) grantAccess()` 不需要流程图 | 只有 3+ 步骤或分支的业务逻辑才需要配图 |
| Mermaid 格式错误（缩进/语法不对） | 无法被 Mermaid 渲染器解析 | 严格遵循 Mermaid 语法，必要时先验证再嵌入 |
| ASCII 框图不对齐 | 视觉混乱，难以理解箭头指向 | 使用等宽字体环境预览对齐，确保箭头正确指向目标节点 |
| 原理注释只写 WHAT 不写 WHY | 代码已经表达了 WHAT，注释重复等于没写 | 聚焦 WHY：为什么选这个方案、不选别的 |
| 决策注释缺少对比方案 | 只说"用了 Channel"但没说"为什么不用 Mutex" | 列出至少 2 个备选方案及优缺点，再给结论 |
| 原理注释只有定性没有定量 | "性能更好"这种表述没有说服力，也无法验证 | 给出具体数据："P99 从 120ms 降到 35ms" |
| 在简单代码上加原理注释 | `if (a > b) return a` 不需要解释决策背景 | 只有包含非显而易见的实现选择时才加 |
| 状态机注释只列状态不列守卫条件 | 知道有哪些状态，但不知道什么条件下能转移 | 每个转移标注 guard condition |
| 系统注释专注于单层而非全链路 | 只看 controller 层不知道 error 最终怎么处理 | 错误传播必须画完整链路：handler→service→repo→外部 |
| 并发模型漏掉死锁/竞态分析 | 读者只知道"用了 goroutine"但不知道是否安全 | 必须显式声明：竞态风险、死锁风险、并发度控制 |
| 安全边界不标注已覆盖/未覆盖项 | 安全审计时无法区分"做了但没写"和"真的没做" | 用 `[x]` 标记已实现的校验点，`[ ]` 标记已知缺口 |
| 数据生命周期只列正向不列异常路径 | 读者不知道数据校验失败时、DB 错误时数据去哪了 | 标注异常分支：校验失败→返回 4xx，DB 错误→500+告警 |

## Red Flags

- **"I retained all original English comments"** — Did you actually verify? Re-read the file to confirm.
- **"The Chinese makes the English redundant"** — Doesn't matter. Keep ALL original comments.
- **"I merged them into a combined comment"** — Don't merge. Keep separate.
- **"The English comment is obvious, the Chinese replaces it"** — Preserve means preserve. Keep both.
- **"I'll create a separate annotation file to keep the originals clean"** — No. Edit the original file in-place. The whole point is having Chinese annotations in the same file as the code.
- **"Every line needs a Chinese note"** — No. Skip trivial one-liners, obvious getter/setters, and boilerplate.
- **"I'll use different prefixes for variety"** — No. Always `// 备注:` for consistency.
- **"I think in English and output Chinese comments"** — No. Think in Chinese from the start to produce natural, idiomatic Chinese annotations.
- **"加了图就不用写注释了"** — 图是注释的补充，不是替代。必须同时保留文字注释。
- **"这个 Mermaid 图很漂亮"** — 但如果 ASCII 图就能表达清楚，优先用 ASCII。简单 > 花哨。
- **"我把整个业务流画在一张图里"** — 超过 20 行图请拆分。读者一次只能消化一个概念。
- **"我用代码变量名当节点标题"** — 图是为了业务人员看的。节点标题用中文业务术语。
- **"等宽字体下对齐了就行"** — ASCII 图必须用等宽字体检查对齐。不对齐的图比没图更糟。
- **"这个图只有我能看懂"** — 图的目标是让**不熟悉这段代码的人**也能理解业务。找个同事验证。
- **"这行代码不直观，我加个注释解释一下"** — 先问：注释说的是 WHAT 还是 WHY？重复 WHAT 是噪音，解释 WHY 才有价值。
- **"我说明了用了什么方案，够了"** — 不够。只说"用了 Channel"没价值，要说"为什么不用 Mutex"。
- **"我说了性能更好"** — 没有数据的"更好"等于没说。量化：P99、QPS、内存、延迟。
- **"这个决策太明显了不需要写"** — 如果 3 个月后你回来看，觉得"为什么不用 X 而用 Y"是明显的吗？写下来。
- **"FAQ 占地方，去 wiki 看吧"** — 开发者读代码时不会切到 wiki。FAQ 要出现在代码里、问题发生的地方。
- **"并发模型就是起了几个 goroutine，没什么好写的"** — 如果写得出来怎么起 goroutine，就应该写出来它们之间怎么通信、怎么同步。
- **"安全边界就是 JWT 校验那一行"** — 安全边界是整个请求管道的属性，不是一行代码的事。画出信任边界和所有校验点。
- **"数据生命周期就是 DTO 转 Entity"** — 如果数据只在两层之间传递，确实不需要。但如果经过了 4+ 层且有序列化边界，就应该画出来。
- **"错误处理很简单，抛异常就行"** — 错误处理策略的复杂性不在于"抛"，而在于"谁兜底、谁重试、谁打告警"。画出分层策略。

## Verification Checklist (MANDATORY)

After adding Chinese comments and/or diagrams, ALWAYS verify:

### 通用检查 (General)
- [ ] 思考过程确认：添加注释/图时的分析、判断、措辞选择均使用中文进行
- [ ] Re-read the file and confirm every original English comment is still present word-for-word
- [ ] Chinese comments are on separate lines, not replacing English ones
- [ ] No code was modified
- [ ] Function-level blocks are before the function declaration, not inside it
- [ ] Code segment comments are immediately before the relevant code

### 图表检查 (Diagram-specific)
- [ ] Diagram is placed BEFORE `// 备注:` comment block, not after
- [ ] Every diagram has a `// 备注：图例：...` line explaining symbols
- [ ] Node labels use Chinese business terminology, not code variable names
- [ ] ASCII boxes are properly aligned (check with monospace font)
- [ ] Mermaid syntax is valid (stateDiagram-v2 / sequenceDiagram / flowchart LR as appropriate)
- [ ] Diagram is ≤20 lines — if bigger, consider splitting
- [ ] Diagram answers ONE business question (flow/state/structure — not mixed)
- [ ] Diagram is accompanied by relevant Chinese text comments — visual alone is not sufficient

### 原理注释检查 (Principle-specific)
- [ ] The annotation explains WHY, not WHAT — if it only describes what the code does, remove it
- [ ] Decision annotations list at least 2 alternatives with pros/cons before giving a conclusion
- [ ] Performance/quality claims are quantified with specific data (not "better"/"faster" without numbers)
- [ ] State machine annotations include guard conditions for each transition, not just state names
- [ ] Invariant annotations include the consequence of violation ("what breaks if this is false")
- [ ] FAQ items are real questions that have come up in code review (not hypothetical)
- [ ] Wire format diagrams include byte sizes, example values, and bit-level field semantics

### 系统层面检查 (System-level)
- [ ] Concurrency model declares shared data, sync mechanism, and deadlock/race risk explicitly
- [ ] Error propagation traces ALL layers (handler→service→repo), not just one
- [ ] Error strategy states what errors ARE retried AND what errors are NOT retried
- [ ] Data lifecycle shows both forward path and exception/error branches
- [ ] Security boundary clearly marks `[x]` (done) vs `[ ]` (known gap) for each checkpoint
- [ ] System annotations focus on cross-module orchestration, not implementation details
