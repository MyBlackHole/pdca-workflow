---
schema: pdca.asset/v1
id: T0291-0815-v81-control-frame
phase: act
---

# Disposition — T0291 v81 后续控制帧非阻塞化

## Verdict

- outcome: **partial**
- AC-1/2/3/4/6: **Passed**；AC-5: **Failed**（线程判据口径与共享 work 池不适配）
- 核心实现有效：认证后控制帧非阻塞化 + 共享 control work 池 + 业务帧移交有序性修复。

## 处置

- **知识沉淀**：`knowledge/control-plane-nonblocking-ingress/v81-control-frame-nonblocking.md`（共享 work 池非阻塞化、parked 移交秩序陷阱、AC-5 判据教训）。
- **跟进任务**：`T0292` `0815-v81-ac5-criterion`（修正 AC-5 线程判据口径，或固定可比运营线程基线后重测对称负载）。
- **代码**：`src/agent_plain_ingress.cpp` 修复（ingress_control_advance 增加 control_jobs.empty() 门控），已还原并全量回归通过。

## 归档

记录 evidence 6 项 + convergence-map 已登记；conclusion.md 已写；verdict 已记入 task.json meta。按 partial 分支归档。
