---
name: pdca
description: 用户显式选择 PDCA、绑定项目、查询状态或恢复已有任务时使用。定位集中 Git 工作副本与原会话，不自动创建任务或执行四阶段。
metadata:
  version: 4.0.0-rc.2
---

# PDCA：集中定位与用户操作分流

## 先定位，不以加载当授权

核对本文件经符号链接解析后的真实路径，定位集中 Git 工作副本 **PDCA_ROOT**（安装默认 `~/.agents/pdca`）。既有任务绑定优先于 cwd 或环境变量；与入口所在根冲突时停止，不自动换根。**TARGET_ROOT** 是当前业务项目的规范化真实路径；不在目标项目创建 `.pdca/` 或另一份 records。

先按[项目绑定契约](../../ontology/contracts/project-workspace.md)只读定位一个项目/工作区，再读[共同恢复入口](../../ontology/contracts/entry-recovery.md)、该项目 context、自己的 task/原 Agent 绑定、最后完整事件和当前请求。不依据 basename、Git remote 或最新任务猜测身份；缺失绑定、多个匹配、目录移动或权限不足时说明事实并等待用户明确。定位已有绑定不写记录，也不要求新的写入授权。

## 显式绑定与 Git 追溯

1. 新增或修改绑定前，展示稳定的 `project_id`、`workspace_id`、真实 `target_root`、`pdca_root`、`records_root=PDCA_ROOT/records` 及具体待写路径 `records/projects/<project_id>/workspaces/<workspace_id>/project-context.md`。核对用户的**记录写入授权**，明确批准后才写；已给出的有效授权无需重复索取。绑定只登记元数据，不创建任务、不启动阶段、不修改目标项目指令或 ignore。
2. 在 PDCA_ROOT 内只读执行 `git rev-parse HEAD` 与 `git status --porcelain`；可用 `GIT_OPTIONAL_LOCKS=0` 避免状态查询刷新索引。每次获准写入绑定、任务或事件前重新采集，将当时 HEAD 写入 `rules_git_head`，将工作树状态原样写入 `rules_git_status`（干净时为空字符串），按[上下文格式](../../ontology/contracts/record-shapes/project-task-context.md)保存。命令失败、无有效 HEAD 或根不是预期 Git 工作副本时停止，不编造值。
3. Git HEAD 与工作树状态只作追溯，不是不可变规则快照；不复制规则、不自动 checkout 历史提交。遇到未提交改动只报告风险，给出审阅、提交、暂存或继续的选项；用户尚未明确如何处理时不改动 Git。已有任务不自动改绑或升级规则；原依据不可用或与当前规则冲突时说明缺口并停止。
4. **Git 提交授权**与记录写入授权分开。只有用户另行明确要求提交具体范围后，才能执行相应 `git add`/`git commit`；已有写记录批准不算提交批准，提交范围不明时先确认。AI 不自动提交、拉取、切换分支、暂存、还原或覆盖集中工作树；Git 跟踪不扩大任何项目的读写授权。

## 操作

1. 状态查询只读当前项目/工作区的导航，输出任务、场景、最后实际阶段、待用户事项和未决资源；不扫描其他项目完整记录。
2. 新工作先说明目标与三场景关系；完成获准绑定后，仅在用户明确创建具名任务时按[派发入口](../../ontology/contracts/agent-dispatch.md)创建真实可交互 Agent。新 Agent 先与你确认 Plan 目标，不能直接建模。
3. 继续任务时定位原会话，把用户原始操作送回原任务。创建未知只对账原请求，恢复失败不新建替代。
4. 明确阶段操作分别选择 `pdca-plan`、`pdca-do`、`pdca-check`、`pdca-act`；选择场景使用[场景索引](../README.md)。一个场景内部仍是完整四阶段，不自动串联各入口。用户显式调用 `pdca-assist` 时使用[只读辅助入口](../pdca-assist/SKILL.md)。
5. 普通请求不自动启用 PDCA；阶段完成或资源就绪只提出下一步建议。取消/撤权优先安全停止，不因等待业务授权延误止损。

## 报告与停止

报告当前事实、推荐入口、等待对象或阻断原因即可。不替任务批准、生成四阶段结果或轮询监工。安装、状态检查与项目登记都不等于正式任务已执行。
