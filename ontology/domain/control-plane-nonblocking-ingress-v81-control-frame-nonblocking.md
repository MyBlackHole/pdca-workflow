---
schema: pdca.asset/v1
id: ontology:domain/control-plane-nonblocking-ingress-v81-control-frame-nonblocking
type: domain
layer: Knowledge
status: active
summary: 控制面非阻塞 ingress + 共享 work 池（v81 经验）
domain:
- ontology:domain/control-plane-nonblocking-ingress
relations:
  specializes:
  - ontology:domain/control-plane-nonblocking-ingress
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


---
schema: pdca.ontology/domain/v1
topic: control-plane-nonblocking-ingress
slug: v81-control-frame-nonblocking
source_record: records/T0291-0815-v81-control-frame/conclusion.md
---

# 控制面非阻塞 ingress + 共享 work 池（v81 经验）

## 背景

v80 仅对「业务前握手」做非阻塞隔离；认证后首个操作提交即由阻塞 worker 全程持有 fd，慢控制会话可占死 worker。v81 把非阻塞前端扩展到「认证后每帧」：ingress 在 Reactor 非阻塞解析出完整 work-ready 帧后，才分派共享 control 工作池。

## 关键洞察（可复用）

1. **分段移交模式可泛化**：v80 的 preface/handoff 移交概念（前端持有 fd → 完整操作 → 移交 worker）可平滑扩展到认证后的控制帧。前端只需解析出 work-ready 帧，不复制 TREE/FILE 状态机。
2. **共享 work 池替代"每会话阻塞 worker"**：PING/TIME/SYS 等平铺控制帧分派到固定 control-workers 池，stalled/慢会话不占业务 worker。
3. **业务帧与 in-flight 控制帧的秩序陷阱**：业务帧被 in-flight 控制任务 park（`handoff_queued=true`）时，必须等在飞控制任务全部 drain 后才移交。若在 `control_jobs` 未清空时提前 handoff，随后到达的控制帧/第二个业务帧会读到并覆盖 parked 帧，导致响应乱序。修复：`if(handoff_queued){ if(control_jobs.empty()){...handoff...} else return 0; }`。
   - 判定要点：一旦 parked，必须让读侧保持 off（return 0 不恢复 READ），否则后续控制帧被读入会破坏 parked 帧完整性。
4. **并发验证用"同连接多控制帧 burst + 立即跟业务帧"**：单会话并发 SYS_REQ + PUT 是最能暴露 parked 移交缺陷的波形；客户端按 type 分流收集乱序响应（不要假设固定完成顺序）。

## 判据教训（AC-5 失败）

- 「线程峰值下降 50%」这一判据与共享 work 池设计不适配：对称全活跃高并发（control-plane concurrency=32）恰是池无法复用降本的波形，agent_threads=7 > v80 每会话阻塞的 4。
- 收益集中在**不对称负载**（慢/闲置会话不占 worker，v81 stall 场景线程不增长）。
- 结论：评估共享池架构应改用「stalled 会话不消耗业务 worker + 池复用」等行为判据，或先固定可比运营线程基线再对比，而非照搬每会话阻塞架构的线程峰值判据。

## 适用边界

- 每会话有序性以会话为提交单位，不跨会话重排。
- EXEC 仍是既有 shard 移交，未纳入本模式。
- 数据面（Data Lane）未重构，仅验证。
