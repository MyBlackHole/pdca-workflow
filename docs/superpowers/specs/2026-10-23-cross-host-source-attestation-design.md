# Codex 与 OpenCode 跨宿主授权来源收据设计

> 状态：待用户审阅。本文定义候选设计，不改变当前授权规则或 CAP-01 能力结论。

## 1. 背景

Codex 中的用户回应可以由操作员经 tmux 转送给 OpenCode Mini。OpenCode 会记录其本机收件事件及操作员身份，却不能读取或核验 Codex 的原始用户 transcript。thread/turn ID 可以定位来源，不能单独证明来源内容、actor 或该回应针对的批准对象。

当前 CONFIRM-01 对此保持未授权；CAP-01 的跨宿主 `communicate` 能力也不能据此标为可用。真实测试观察见 [Codex→OpenCode 来源互操作记录](../../../tests/.pdca-h11-live-20261022-01/control/observation-codex-opencode-confirm-source-gap.md)。

## 2. 目标与边界

设计一个可选的跨宿主来源证明通道，使目标宿主能确认：原始输入确由用户在可信来源宿主产生、针对一个已固定的 request，并被路由到指定的目标宿主和会话。

以下不变量继续成立：

- 父 Agent 的转述、普通 prompt 中的来源声明、thread/turn 字符串和 `actor=user` 标签本身不产生授权。
- `CONFIRM-01` 继续负责解释用户回应是否明确授权固定对象；收据只证明来源、上下文绑定和路由事实。
- request、subject 或目标会话不匹配，来源不可读、签名无效、过期或重复时，结果保持 unknown/blocked。
- 没有真实宿主签发与接收端验签能力的宿主组合，CAP-01 `communicate=unavailable`。
- 收据不能预批其它 task、attempt、phase、run、subject 或写域。

非目标：用共享密码或 prompt secret 模拟来源；降低原生用户输入验证标准；实现通用多租户消息总线；修改当前 RPC task 的固定 subject 或 request。

## 3. 备选方案

### A. 保持 unavailable，要求目标宿主原生确认

当前规则不变。用户需在 OpenCode Mini 的原生入口完成批准。实施范围最小，安全边界清楚，但不能支持 Codex→OpenCode 的全自动审批转送。

### B. 宿主签发的来源收据（推荐）

来源宿主只依据自身原生用户事件签发收据；目标宿主的可信接收组件在消息进入 Mini 对话前验签并验证路由。PDCA 消费经验证的来源事实，仍单独执行 CONFIRM-01。此方案支持自动转送，并要求两个宿主都提供真实的签发/验证接口。

### C. 独立授权服务

Codex 与 OpenCode 都向独立服务提交并核验批准事件。它便于未来接入更多宿主，但增加服务运行、凭据轮换、可用性与审计范围；当前只有一对宿主，不建议先部署。

## 4. 推荐设计

采用 B，并分开验证本体协议与宿主能力。签名格式、密钥算法和轮换由实现阶段根据两个宿主实际提供的可信接口确定；任何私钥不得进入 prompt、Agent 环境变量或普通项目记录。

### 4.1 来源宿主签发

来源宿主的原生适配器应直接取得可恢复的用户输入事件和其 actor/conversation 上下文，并确认该回应关联到一个由来源宿主展示的固定批准对象。适配器产生版本化、可验签的 attestation，至少覆盖：

- 收据 ID、版本、签发方 key ID、签发时间、到期时间和一次性 nonce；
- 来源宿主、用户 actor、唯一来源 message/transcript ref、conversation/turn；
- 原始回应文本摘要；
- 固定的 request ID、request digest、subject digest、scope/action/phase/run；
- 目标宿主、目标 OpenCode session，以及允许的路由范围。

签发器必须从来源宿主原生事件取值，不接受 Agent 自行提交的 `source_ref`、actor 或“用户已批准”声明作为签发依据。若来源宿主不能确认原始用户事件及它所回应的固定批准对象，就不签发。

### 4.2 目标宿主接收与验签

目标宿主的可信接收组件使用受信 issuer/key 配置验签，并在把内容交给 Mini 前核对：

1. 签名、issuer、版本、有效期及 nonce；
2. 原始回应摘要与实际收件文本一致；
3. request ID/digest、subject digest、scope、phase/run 与当前唯一未消费对象一致；
4. target host/session 与原生收件事件一致；
5. nonce 未消费，且该来源 event 未被用于另一个 decision。

验证结果应由宿主 verifier 原生出具，不能由 Agent 写一段“已验签”文本替代。OpenCode 的收件 actor 仍记录真实 relay/operator；收据中的 origin actor 单独记录为来源用户。两种身份不得合并。

### 4.3 PDCA 记录投影

新增独立的 `pdca.source-attestation/v1` 记录形状，保存签发声明和宿主验证回执的不可变引用。扩展 `pdca.response/v4` 增加 `source_attestation_ref`；现有 `source_ref`、`actor_ref`、`conversation_ref` 指向原始来源，`host_received_event_ref` 指向目标宿主收件事实。新增字段不改变 request/response/decision 的职责边界。

CONFIRM-01 仅在可信 verifier 结果覆盖上述绑定且响应语义明确时，才可把来源计为可核实用户回应并消费 request。decision 仍是审计投影，不是签发器。重复输入幂等；过期或对象变化后不得重用旧收据。

### 4.4 CAP-01 能力判定

`communicate` 对来源/目标宿主对单独记录适用范围和证据。以下条件全满足后才可标为 PASS：

- 来源宿主提供基于原生用户事件的签发能力；
- 目标宿主在信任边界内验证签名及目标路由；
- 两侧能导出可核查的签发、投递、验签回执；
- 负向用例拒绝伪造、篡改、过期、重放和目标不符的收据。

任何一项未实现或未实测，保持 NOT_RUN/unknown/unavailable；静态 schema、角色提示和 Agent adapter 不能代替宿主能力验收。

## 5. 数据流

```text
来源宿主原生 user event
        │ 关联固定 request / subject
        ▼
来源宿主签发 source-attestation
        │ 绑定 target host/session 与一次性 nonce
        ▼
目标宿主 native inbox event ──> 可信接收组件验签、验路由、记 nonce
                                      │
                                      ▼
                         Mini 收到分离的 origin / relay 身份
                                      │
                                      ▼
                  CONFIRM-01 匹配回应语义并消费唯一 request
```

任一箭头缺少宿主原生证据，当前路径即 blocked，不以人工补写记录继续。

## 6. 验收

### 协议验证

- 有效签发、有效路由、正确 request/subject：收据可验证，CONFIRM-01 按回应语义处理。
- 伪造 issuer、无效签名、改写回应文本：接收端拒绝。
- request/subject/phase/run/session 任一不符：拒绝消费，不创建 run。
- 过期、重放、重复投递：拒绝或幂等回到已有消费结果，不产生第二个 decision/run。
- 缺少 verifier 原生回执：保持 unknown/blocked。

### 真实宿主验证

在隔离 TARGET_ROOT 使用一条新固定 request。来源必须是来源宿主实际原生接收的用户批准；中继操作员可以运输消息，但不能成为来源证明。逐项保存来源签发回执、目标 native delivery event、验签回执、CONFIRM decision 与同一 request/run 的关联。反向用例不得启动 phase。宿主版本、配置或接入路径改变后重新核验 CAP-01。

当前 OpenCode Mini 测试的 RPC Plan 请求继续保持未消费和未启动；本设计不会借用该 request 做协议正向测试。

## 7. 分阶段落地

1. **协议与模型**：评审本设计，固定记录 shape、字段语义、信任根和重放规则；只增加无签发能力声明的静态模型不能使 CAP-01 通过。
2. **宿主可行性**：只读核实 Codex 原生来源签发点、OpenCode 原生接收/验证点和受信密钥管理。任一宿主缺少必要扩展点时，保持 unavailable，并将宿主集成作为单独工作拆分。
3. **实现与验证**：先针对收据解析/验签和拒绝路径做测试，再通过真实 source→relay→verify→CONFIRM 场景验收。

每一阶段各自固定对象、写域和验收证据。当前阶段仅产出设计供审阅，不修改 ontology、Skills、代码或现有任务记录。
