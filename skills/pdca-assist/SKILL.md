---
name: pdca-assist
description: 仅在用户显式调用 pdca-assist，为当前已绑定项目选择下一步工作建议时使用。普通请求不自动启用。
metadata:
  version: 5.0.0-rc.2
---

# PDCA Assist：只读候选建议

用户显式调用才进入。只读取和展示候选；不创建 record/task/Agent/phase/resource，
不写 TARGET_ROOT、不运行测试/构建/安装、不修改 Git。候选被用户选中也不是后续动作授权。

## 最小读取

按[项目绑定契约](../../ontology/contracts/project-workspace.md)只读定位唯一 project/workspace、
PDCA_ROOT 与 TARGET_ROOT，并按其中的只读 Git 快照规则采集需要的状态。绑定缺失、冲突或权限不足时停止，
让用户回 `pdca` 处理，不自动改绑。

只读取当前候选真正需要的项目导航、相关 records 与获准业务材料；不扫描其他项目，
不默认遍历整个 ontology/source tree/history。候选依赖已有 task 的阶段、待回应请求或恢复连续性时，
才按 [entry-recovery](../../ontology/contracts/entry-recovery.md)读取该 task 的必要状态。

## 候选

从以下视角中只输出**有事实依据**的项，每个最多一个、总数最多四个：

- **任务地图**：实际 task/phase、明确依赖或待用户事项；
- **项目上下文**：与当前目标直接相关的绑定、源码、文档或 records 缺口；
- **证据审阅**：现有 evidence 与固定 AC/oracle 的具体缺口；
- **协作交接**：原 Agent、待回应请求或固定 deliverable/interface 的交接缺口。

每个候选只写：事实依据、建议动作、影响对象、继续所需授权。发现新的 ontology responsibility 时，只说明应回 modeling 形成 EVOLVE/TREE/NODE candidate；经 Modeling Check/Act 固定为 formal node 后，才可由 DECOMP 形成 task seed。Assist 本身不创建任何结构。

只对当前候选做反重复检查：获准读域已有等价实现/决定时优先复用；同一候选已有明确拒绝/wontfix 时说明原因，
除非用户重提或事实变化不再推动。无法从最小读集判断时标 unknown，不扩大扫描来“证明没有”。

## 停止

展示候选后停止。创建 task、写记录/业务对象、发送交接、运行验证或启动 phase 都需后续明确用户操作；
Assist 不把建议、选择或“看起来合理”转换成授权。
