---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.1
authority: reference
status: active
---

# 原生派发契约 v4

TASK/CAP/CONFIRM/SCHED是本版依据；按bootstrap/dispatch-guide.md新建、继续、处理未知和恢复失败。父Agent不监控生命周期、不指挥阶段、不代答，宿主原生机制维持消息和资源。

任务开始前真实新Agent、独立输入、用户双向交互和原会话继续均可用，才具备正式资格。每阶段启动仍由用户决定。引用原生回执，不认证自述或同名角色。

独立验证包只检查有限记录关系，不创建Agent、不认证宿主、不证明隔离。现场验收状态NOT_RUN；不要把离线合成控制通过称运行验收通过。
