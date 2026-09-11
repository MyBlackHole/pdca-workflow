# 3.2运行控制回归：20个任务级验收案例

这些是每次节点场景任务的单元测试材料，不是成功运行日志。R01—R20逐例给出固定输入、正例、反例、独立预期、错误控制、观测、清理和返工；model_vectors只是可复跑参考模型投影，不能代表真实Agent行为。

| 案例 | 目标 | 权威 | 真实宿主 |
|---|---|---|---|
| [R01](R01.md) | Plan取消不伪造后续阶段 | CONTROL-01, STATE-01 | NOT_RUN |
| [R02](R02.md) | Do取消与未知远端操作 | CONTROL-01, RESOURCE-01 | NOT_RUN |
| [R03](R03.md) | 明确无限等待不自动批准 | CONTROL-01, CONFIRM-01 | NOT_RUN |
| [R04](R04.md) | 截止到期与迟到确认 | CONTROL-01, CONFIRM-01 | NOT_RUN |
| [R05](R05.md) | 确认与超时竞争只有一个请求终局 | CONTROL-01, TRANSITION-01 | NOT_RUN |
| [R06](R06.md) | 同槽接管与旧写权 | SCHED-01, RESOURCE-01 | NOT_RUN |
| [R07](R07.md) | 跨工作真实资源与别名冲突 | RESOURCE-01 | NOT_RUN |
| [R08](R08.md) | 租约失效后的旧epoch写入 | RESOURCE-01, CONTROL-01 | NOT_RUN |
| [R09](R09.md) | 能力丢失与同任务恢复 | CAP-01, CONTROL-01 | NOT_RUN |
| [R10](R10.md) | 45组phase与execution_state | STATE-01 | NOT_RUN |
| [R11](R11.md) | 回执重复与内容冲突 | TRANSITION-01 | NOT_RUN |
| [R12](R12.md) | 新尝试序号复用与旧写者 | TRANSITION-01, SCHED-01 | NOT_RUN |
| [R13](R13.md) | 部分落盘与恢复不重做业务 | RECOVERY-01, TRANSITION-01 | NOT_RUN |
| [R14](R14.md) | 无双向边的三节点长环 | DEPENDENCY-01 | NOT_RUN |
| [R15](R15.md) | 组成与额外输入联合查环 | DEPENDENCY-01 | NOT_RUN |
| [R16](R16.md) | 检查后改图与合法跨场景 | DEPENDENCY-01 | NOT_RUN |
| [R17](R17.md) | 弱关联环、显式检索与预算 | CONTEXT-01, DEPENDENCY-01 | NOT_RUN |
| [R18](R18.md) | 方法阶段与工作流终态类型 | STATE-01, ONTOLOGY-01 | NOT_RUN |
| [R19](R19.md) | 全部测试blocked仍能诚实失败收尾 | GATE-01, TEST-01 | NOT_RUN |
| [R20](R20.md) | Check正常归档与授权替代接续 | REWORK-01, CONTROL-01 | NOT_RUN |

## 两层验证分别记录

参考模型读取实际Markdown规则和固定fixture，输出独立results；它检查规则谓词、状态关系、图和拒绝路径。真实宿主必须实际提供Agent隔离、路由、停止/撤权、资源排他和后端事件证据，不能用fixture里的source_verified=true替代真实授权。

R10还需执行45组矩阵全积；R13需要实际文件部分写/修复演练；R07/R08在真实宿主验收时必须观察目标资源端，不只看最终报告。所有现场结果写入当前任务自己的suite/run，与此教学文件分离。

## 错误控制与返工

至少验证：直接取消归档、超时批准、迟到消息复活、active当锁、任务ID当资源ID、旧epoch写、全局sequence、回放已执行操作、只测双向环、分图各自通过、忽略图版本、弱关联变前置、archive当方法阶段、测试必须有PASS才允许Check、取消自动批准后继。

先正确控制通过，再逐个错误变体断言失败；测试器错误/未运行不能当作killed。失败保留原输入与实现，Do内预算允许则同任务修复，Check后新attempt新Agent；最终修复版本重跑全部受影响必需案例，旧结果不拼成新全绿。

[综合返工演练](rework-walkthrough.md) · [机制来源](sources.md) · [原68个宿主案例](../behavior-cases.md)
