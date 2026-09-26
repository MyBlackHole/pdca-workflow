---
name: pdca-assist
description: 仅在用户显式调用 pdca-assist，为当前已绑定项目选择下一步工作建议时使用。普通请求不自动启用。
metadata:
  version: 5.0.0-rc.2
---

# PDCA Assist：只读候选建议

用户显式调用才进入。本入口只读取和展示候选，不创建记录、task/Agent/phase/resource，
不写 TARGET_ROOT，不执行测试/构建/安装，也不修改 Git。用户选择候选本身仍不是后续动作的授权。

## 最小读取

先按[项目绑定契约](../../ontology/contracts/project-workspace.md)只读定位一个明确的
project/workspace、PDCA_ROOT 与 TARGET_ROOT；绑定缺失、多个匹配、路径冲突或权限不足时停止，
让用户回 `pdca` 处理，不自动改绑。

只读取形成当前候选所需的项目导航、相关 records，以及获准读域内的源码/文档/只读 Git 状态。
不扫描其他项目，不默认遍历整个 ontology、source tree 或历史事件。
候选涉及某个已有 task 的阶段、待回应请求或恢复连续性时，才按
[entry-recovery](../../ontology/contracts/entry-recovery.md)读取该 task 的必要状态。

## 产生候选

从下面四个视角中**只输出有事实依据的视角**；每个视角最多一个候选，总数最多四个。
没有依据的视角直接省略，不为了凑满栏目扩大读取范围。

| 视角 | 候选关注点 |
|---|---|
| 任务地图 | 当前 task、最后实际 phase、明确依赖或待用户事项 |
| 项目上下文 | 绑定、源码、文档或固定 records 中与当前目标直接相关的缺口 |
| 证据审阅 | 已有 evidence 与固定 AC/oracle 之间的具体缺口 |
| 协作交接 | 原 Agent、待回应请求或已固定 deliverable/interface 的交接缺口 |

每个候选写明：**事实依据、建议动作、影响对象、继续所需授权**。
如果候选会新增正式职责，说明应回 modeling/DECOMP 形成 seed；不要由 Assist 自己创建任务结构。

提出候选前只做与该候选有关的反重复检查：

- 在当前绑定且获准读域中已有等价实现/记录/决定时，优先指向既有对象；
- 当前项目记录里有同一候选的明确拒绝/wontfix 时，说明已知原因；除非用户主动重提或事实发生变化，本次不重复推动。

这不是要求每次 Assist 全项目语义搜索。无法在当前最小读集判断是否重复时标 unknown，而不是扩大扫描来“证明没有”。

## 停止

展示候选后停止。正式创建 task、写记录/业务对象、发送交接、运行验证或启动任何 phase，
都由用户随后明确操作并进入对应入口；Assist 不把建议、选择或“看起来合理”转换成授权。
