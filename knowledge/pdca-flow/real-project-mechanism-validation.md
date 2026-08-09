---
schema: pdca.asset/v1
id: knowledge.pdca-flow.real-project-mechanism-validation
summary: T0234 真实工程实测：ready-set/seam/词汇契约三机制在真实开发任务全部有效；词汇契约适用范围边界；集成测试捕获真实 bug；外部项目模式可行
tags: [pdca-flow, mechanism-validation, seam, ready-set, vocab, external-project]
scenarios: [plan, do, check]
phases: [plan, do, check, act]
source_ids: [T0234-0809-fastapi-app-verify]
---

# 真实工程机制验证（T0234 实测）

用 FastAPI + SQLAlchemy + SQLite TODO 应用（外部项目）完整走 PDCA，
实测 T0232/T0233 三机制在真实开发的效果。

## 实测结论

| 机制 | 真实工程效果 |
|------|-------------|
| **ready-set 调度** | 3 子任务 DAG valid，分批 [[T0235],[T0236],[T0237]]；storage 完成后 T0236 自动 ready，调度与预期一致 |
| **seam 契约** | 3 个 PRD seam 逐一校验通过（测试文件存在 + 模块一致），门禁对"声明 vs 实际"守护有效 |
| **词汇契约** | 拒绝 component/API/boundary、接受 module/interface/seam，机制工作正常 |

## 关键教训

1. **词汇契约适用范围边界**：check-design-vocab 禁用词表针对接口设计文档，
   对普通 PRD/需求文本误报（T0234 PRD 含 component/service/API 词被误判）。
   → 契约必须限定适用文档类型（仅 design 文档），不得误用于需求文档。

2. **集成测试捕获真实 bug**：TestClient 测试发现 create 后 GET/PUT 404，
   根因 get_db 缺 commit（跨请求事务未落盘）。集成测试（真实请求链路）
   价值实证。

3. **门禁严格要求**：P6 转换需精确 `## 验收标准` 标题 + schema 严格校验
   （meta.note 非法、status 枚举限制）。真实任务首次运行需修正格式，
   门禁真实阻止不合规任务进入 Do。

4. **时间戳格式一致性**：手写 states 时间戳带微秒 vs transition 生成的无微秒
   会触发门禁误判（STATE_TIME_ORDER）。时间戳应统一格式。

## 外部项目模式（验证可行）

- 应用代码放外部目录（如 /tmp/opencode/todo-fastapi/），任务/记录/证据
  留在 PDCA 中心仓库。
- init-external.sh 在外部项目创建 AGENTS.md（PDCA_HOME 引用）。
- register-evidence 可将外部文件**复制快照**登记进 evidence。
- 关键：web 应用是测试 PDCA 的工具，**不应放入 PDCA 仓库**（用户明确）。

## 复用场景

- 后续新机制的验证载体（外部项目可复用）。
- 修正 check-design-vocab 适用场景时的依据。
- CI 集成 seam_contract 门禁的依据。
