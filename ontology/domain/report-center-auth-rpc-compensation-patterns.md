---
schema: pdca.asset/v1
id: ontology:domain/report-center-auth-rpc-compensation-patterns
type: domain
layer: Knowledge
status: active
summary: report-center 认证服务与 RPC 补偿模式
domain:
- ontology:domain/report-center
relations:
  specializes:
  - ontology:domain/report-center
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 由领域实践与测试验证
---

# report-center 认证服务与 RPC 补偿模式

## 来源
- 记录：`records/T0219-0804-report-web/conclusion.md`
- 前置知识：`db-adapter-pg-practices.md`（Repository/Adapter 分层）

## 适用范围
T0221/T0222（下游页面接入）、report-center 后续任何含认证或 RPC 编排的服务层、其他含外部服务调用的 FastAPI 后端。

## 1. 认证服务模式（AuthService）

### 组件职责
| 组件 | 职责 | 关键点 |
|------|------|--------|
| `CaptchaService` | 验证码摘要存 Redis | TTL 5 分钟、5 秒刷新限制 |
| `RedisTokenStore` | Token 签发/校验/撤销 | 校验 = 验签 + Redis 中存在；撤销 = 删 Redis key |
| `AuthService` | 登录/改密/登出编排 | 登录失败计数、must_change_password 流程 |

### 登录限流要点
- **限流 key 必须归一化**（`username.lower()`），否则大写变体可绕过 5 次锁定。
- 成功登录清除失败计数；锁定窗口 20 分钟 5 次。
- 登录校验顺序：验证码 → 用户锁定 → 密码 → must_change_password。

### 改密流程
- must_change_password=true 时登录返回一次性 `password_change_token`。
- 改密后：`clear_must_change_password` + **立即 revoke 所有该用户 Token**（AC-2）。
- 改密 Token 与访问 Token 用同一 RS256 但 `type` claim 区分（`TokenType`）。

### Token TTL 动态化
- 不要硬编码 TTL。用 `ttl_provider: Callable[[], int]` 注入（app 层从系统设置读取）。
- **修改 TTL 仅影响新会话**：签发时读当前值写入 exp；已签发 Token 不受影响。

### 首装 admin 引导
- `create_app(bootstrap_admin=True)` 时幂等执行 `ensure_bootstrap_admin`。
- 初始 `must_change_password=true`，强制首次登录改密。
- 幂等：username 唯一索引 + 已存在则跳过（勿用无条件 INSERT）。

## 2. RPC 补偿回滚模式（DomainService + RPC Client）

### 调用契约
- T0218 服务端返回 `{"ok": True, "data": ...}` 或 `{"ok": False, "error": {"code", ...}}`。
- **客户端必须在 `with rpc_client() as c:` 块内解包 netref**（`rpc_obtain`），块外访问返回 netref EOFError。
- rpyc 暴露方法名去掉 `exposed_` 前缀（`conn.root.ensure_domain_schedule_config`）。
- CollectionError 用 `error_code` 属性（非 `code`）。

### 通道异常分类
超时类异常（`TimeoutError`/socket.timeout/`RPC_WAIT_TIMEOUT`）→ `RPC_TIMEOUT`；其余（连接拒绝等）→ `RPC_CONNECT_FAILED`。统一经 `_classify_channel_error(exc, timeout)`。

### 编排补偿
- 创建域：DB 插入 → `ensure_domain_schedule_config`；RPC 失败则 DB 回滚。
- 启停：`add_job`/`remove_job`；失败补偿回滚 + 状态回写。
- **删除顺序（AC-5）**：逻辑删除先生效（`is_deleted=true`，同控制事务）→ 删 3 个 Job → 删周期文件。Job/周期文件删除失败**不阻断**（尽力而为），避免 RPC 故障导致删除中断。
- 连通性测试固定 `verify-credentials`，10 秒超时，四类失败分类，**无副作用**（不建 Job/不入库）。

### 唯一约束精确捕获
- 创建时 `except psycopg.errors.UniqueViolation` 转业务错误（勿捕获全部 Exception 误报）。

## 3. 保存报告 per-owner 隔离
- 唯一约束必须是 `(owner_subject_id, LOWER(report_name))`（V002 迁移），不能全局唯一——否则用户 B 无法保存与 A 同名报告。
- 查询按 `owner_subject_id` 过滤 + per-owner 索引（`idx_saved_report_owner_created`）。
- 跨用户访问返回 404（不泄露存在性）。

## 4. 测试基建经验
- **conftest 迁移初始化应确保所有版本应用**（`for spec in discover_migrations: adapter.migrate(spec)`），不能只在表不存在时执行 V001——否则新增迁移（V002+）在共享测试库不生效。
- 迁移回滚测试（V001 down 全表 DROP）恢复时必须**重放全部版本**并清空 UP/SUCCESS 审计，否则 V002 索引随表删除但审计记录仍在导致跳过重放。
- 生产 Redis 用 fakeredis 测试；PG 契约测试用 podman 容器（t0216-pg）。
- `ON CONFLICT` 需匹配唯一索引表达式（`LOWER(username)`），测试 seed 优先 DELETE+INSERT。

## 局限
- 认证/限流未做高并发压测；RPC 失败补偿依赖 T0218 服务端稳定。
- AC-7 打开重建 QuerySpec 端到端验证留待 T0220（TemplateRegistry 协议注入点已就位）。
