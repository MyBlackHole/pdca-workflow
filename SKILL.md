---
name: pdca
description: 用户明确选择 PDCA、已加载全局规则选用 PDCA，或继续/恢复已有 PDCA 任务时使用。普通开发、讨论 PDCA 概念或维护本规则库，不因本技能可见而自动启动正式流程；明确本次不用 PDCA 时不启用。
compatibility: 正式执行需真实隔离 Agent、原会话继续、确认路由及获权文件工具；不依赖特定产品、adapter 或捆绑运行器。
metadata:
  version: "3.4.10"
---

# PDCA：按当前事实进入，不从头重复启动

本文件只负责发现与交接，不授予权限。维护规则、填模板和脚本自测不等于正式 PDCA 完成。

| 当前事实 | 下一步 |
|---|---|
| 本次明确不用 PDCA | 不启动、不创建任务目录；已有任务停止仍按原控制授权处理 |
| 已有父派发、task 或恢复消息 | 沿用固定双根、project-context、原协议快照及真实绑定；进入原任务，不按 cwd、新版本或重复消息另建 attempt |
| 新工作已选择 PDCA | 按 [USE-PDCA](USE-PDCA.md)观察真实 cwd 与单变量 PDCA_ROOT，固定双根；缺有效入口时报告具体路径，不安装、初始化或换根 |

定位后读取固定 PDCA_ROOT 的[入口交接](bootstrap/entry-check.md)，完成其必需读集，再按[角色与事件](bootstrap/entry-check.md#role-actions)执行当前获权动作。已绑定节点不再次派发自己；普通检索问题不递归启动完整框架。

同一摘要且仍可用的上下文不重复加载；压缩或恢复后按 [RECOVERY](ontology/concept/pdca-recovery.md#recovery-capsule)重新核验当前必要事实，不能把“读过”当作“仍掌握”。CONTROL/RESOURCE 停止与撤权始终有效。

输出当前动作的真实观察、产物或具体阻断。缺原生能力为 dispatch_blocked，等待真实批准为 awaiting_confirmation；不代签、不降为 Do-only、不补造阶段。方法不产生新的授权。

## 分发

标准技能目录名为 `pdca`，保留本文件及相对引用目录，不只复制入口。宿主实际加载不证明派发能力；跨项目根定位仍按 USE-PDCA，不自动改全局配置。维护评测在独立验证包执行，不进入业务必读集。
