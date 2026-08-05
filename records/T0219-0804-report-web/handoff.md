## 当前状态

T0219（report-web 登录鉴权与备份域管理服务）已完整走完 Plan→Do→Check→Act。verdict=confirmed，disposition=task_only。全量 pytest 237 passed。

## 未完成事项

- **AC-7 打开重建端到端验证**：当前保存报告/隔离/唯一已验证；"打开按快照重建 QuerySpec 查最新数据"依赖 T0220 真实模板，留待 T0220 闭环（TemplateRegistry 协议注入点已就位）。

## 已知约束

- report-center venv（Python 3.14.6），pip 清华镜像。
- RPC 契约：T0218 返回 `{"ok":True,"data":...}/{"ok":False,"error":{...}}`；客户端须在 rpyc `with` 块内 `rpc_obtain` 解包；CollectionError 用 `error_code`。
- 测试用 fakeredis + podman PG 容器（t0216-pg）；conftest `_ensure_schema` 现确保全部迁移应用。
- V002 迁移（per-owner 唯一）已应用；test_migrations 回滚恢复会重放全部版本。
- 登录限流 key 归一化（lower）；TTL 经 ttl_provider 注入仅影响新会话。

## 推荐的下一步

- T0220 落地后复验 AC-7 打开重建，闭环 partial 边界。
- T0221/T0222 接入 /auth /domains /saved-reports 契约时复验错误码映射。

## 关键上下文文件列表

- `prd.md`、`conclusion.md`（records/T0219-0804-report-web/）
- `evidence/`（e1~e5 + convergence-map）、`clarifications.jsonl`
- 代码：`report_center_db/security/*`、`report_center_db/services/{auth_service,domain_repository,domain_service,rpc_clients,saved_report_service}.py`、`report_web/app.py`
- 迁移：`migrations/postgresql/V002__report_saved_report_owner_unique.up.sql`
- 知识：`knowledge/report-center/auth-rpc-compensation-patterns.md`

## suggested skills

- `feature-commit-format`（提交）
- `code-comments`（如需补充中文注释）