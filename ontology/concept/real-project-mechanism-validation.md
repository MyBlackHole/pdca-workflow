---
schema: pdca.asset/v1
id: ontology:concept/real-project-mechanism-validation
type: concept
layer: Knowledge
status: active
summary: T0234 真实工程实测：ready-set/seam/词汇契约三机制有效，集成测试捕获真实 bug，外部项目模式可行
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca-task
  - ontology:concept/pdca-acceptance-criterion
---

# 真实工程机制验证（real-project-mechanism-validation）

用 FastAPI + SQLAlchemy + SQLite TODO 应用（外部项目）完整走 PDCA，实测机制在真实开发的效果。

## 实测结论

| 机制 | 真实工程效果 |
|------|-------------|
| ready-set 调度 | 3 子任务 DAG valid，storage 完成后 T0236 自动 ready，调度与预期一致 |
| seam 契约 | 3 个 PRD seam 逐一校验通过（测试文件存在 + 模块一致），门禁对"声明 vs 实际"守护有效 |
| 词汇契约 | 拒绝 component/API/boundary、接受 module/interface/seam，机制正常 |

## 关键教训

1. **词汇契约适用范围边界**：check-design-vocab 禁用词表针对接口设计文档，对普通 PRD/需求文本误报；契约必须限定适用文档类型。
2. **集成测试捕获真实 bug**：TestClient 测试发现 create 后 GET/PUT 404，根因 get_db 缺 commit；真实请求链路价值实证。
3. **门禁严格要求**：P6 转换需精确 `## 验收标准` 标题 + schema 严格校验；真实任务首次运行需修正格式。
4. **时间戳格式一致性**：手写 states 时间戳带微秒 vs transition 生成无微秒会触发 `STATE_TIME_ORDER`；时间戳应统一格式。

## 外部项目模式（验证可行）

应用代码放外部目录，任务/记录/证据留 PDCA 中心仓库；`init-external.sh` 在外部项目创建 `AGENTS.md`（PDCA_HOME 引用）；`register-evidence` 可复制快照登记；web 应用是测试工具不应放入 PDCA 仓库。

## 来源

- `（原知识层）real-project-mechanism-validation.md`
- 关联任务：`T0234-0809-fastapi-app-verify`
