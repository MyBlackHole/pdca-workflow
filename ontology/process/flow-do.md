---
schema: pdca.asset/v1
id: ontology:process/flow-do
type: process
layer: Knowledge
status: active
summary: Do 阶段流程实体：按 scenario_type 路由执行、ontology-ready 关卡、证据登记与执行器边界
relations:
  specializes:
  - ontology:concept/process
  part_of:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca-phase
  - ontology:entity/phase-do
  - ontology:concept/pdca-ontology-ready
  - ontology:concept/pdca-gate-do
  - ontology:concept/executor-adapter
  - ontology:concept/external-evidence-collection
  - ontology:concept/destructive-cleanup-safety
  - ontology:concept/real-project-mechanism-validation
  - ontology:concept/pdca-home
---

# PDCA Do 流程（flow-do）

Do 阶段按 `meta.scenario_type` 路由到相应 agent skill 执行，是 PDCA 周期中唯一产生实现产物的阶段。

## 阶段步骤（权威描述）

1. **路由**：`flow-do` 依据 `task.json.meta.scenario_type` 选择 6 条 Do 路径之一（development/bugfix/research/design/review/documentation）。
2. **ontology-ready 关卡**：`meta.ontology_fragment` 指向的领域片段须存在且结构合法（自举任务经 `meta.ontology_exempt` 豁免）。
3. **执行**：调用对应 skill；外部产物先复制 `workspace/external-artifacts/` 再登记 Evidence。
4. **证据登记**：`register-evidence` 把产物锚定到 `pdca-evidence` 子类型。
5. **Phase Boundary 决策树**：收尾阶段必须输出 Phase Boundary 决策树，按序询问五个选项（①能继续吗→Continue；②上下文与后续无关→/clear；③需要跨 harness/目录/同事/支线分叉→/handoff；④任务可 AFK→Subagent；⑤否则 /compact），第一个 yes 获胜，mid-phase 永不决策。
6. **门禁**：`pdca-gate-do` 校验后才能收尾进入 Check。

## 关键决策（已迁移自外部知识）

- **执行器边界**（详 `ontology:concept/executor-adapter`）：Scenario 的 Executor ID=业务角色；开放 Executor type=执行协议/平台类别；Registry adapter=可替换平台插件。核心 Planner 只判定 ready，Registry preflight 解析类型/能力/信任策略；Adapter 统一承担输入映射、会话、权限、超时/取消、流式事件、结果归一化。Codex/OpenCode/Claude Code/API Agent/MCP 差异留在 Adapter，核心无平台分支。仅 automatic 且能力满足可直接调用；命令型/Agent 型默认需审批。tmux 驱动 OpenCode 须固定工作目录+变更白名单+超时重试+可观测，阶段推进交 agent、安全边界/最终判定由执行器负责。
- **外部项目注入**：workflow root 与 agent 工作目录分离时，启动器须为目标项目执行平台 setup 并显式传入 workflow root，仅当目标缺 `AGENTS.md` 才写入（保护用户已有说明），setup 失败则拒绝启动。
- **外部证据收集**（详 `ontology:concept/external-evidence-collection`）：中央 manifest 只接受 workflow root 内安全相对路径，拒绝绝对路径/符号链接；外部产物复制副本到 `workspace/external-artifacts/` 后登记。
- **销毁清理安全**（详 `ontology:concept/destructive-cleanup-safety`）：可恢复清理须 dry-run 生成精确清单并固定恢复源为删除前不可变 commit（不引用会漂移的 HEAD）；apply 前重新验证每个目标仍处允许删除状态，任一漂移/越界/不可恢复则整批失败关闭。
- **全局仓库配置**（详 `ontology:concept/pdca-home`）：`$PDCA_HOME` 为第一优先级；仅含 `ontology/process/flow-plan.md` 的目录为有效 workflow 仓库；外部项目经 `scripts/init-external.sh` 初始化。

## 路径 A：development（软件功能开发）

确认预先约定的 Seam
先写失败的行为测试
再写最小实现
完成每个垂直切片后运行定向测试或 typecheck
所有切片完成后运行项目支持的全量验证
进入双轴代码审查

## 路径 B：bugfix（Bug 修复）

确认回归 Seam
先复现并写出失败的回归测试
确认修复方案
再做最小修复
完成每个修复切片后运行定向回归测试或 typecheck
所有修复切片完成后运行项目支持的全量验证
进入双轴代码审查

## 路径 C：research（需求调研/技术调研）

## 路径 D：documentation（需求转技术文档）

## 路径 E：design（架构设计）

## 路径 F：review（代码审查）

## 来源

- `（原知识层）executor-adapter-boundary.md`
- `（原知识层）opencode-tmux-executor-adapter.md`
- `（原知识层）external-project-workflow-injection.md`
- `（原知识层）external-evidence-collection.md`
- `（原知识层）destructive-cleanup-safety.md`
- `（原知识层）global-repo-config.md`
- `（原知识层）real-project-mechanism-validation.md`