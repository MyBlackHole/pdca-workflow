# report-web 登录鉴权与备份域管理服务 — 规格文档

## 问题陈述

报表中心 Web/API 服务缺失：需实现验证码登录、Token 鉴权、备份域管理（创建/启停/删除/连通性测试）、保存报告，以及经 `CollectionSchedulerRPCClient` 的受限 Job 控制与经既有 rpc 工具通道的 `verify-credentials` 连通性测试。

## 解决方案

实现 `report-web`（FastAPI）：验证码（Redis 摘要，TTL 5 分钟）→ 登录（Redis 限流 20 分钟 5 次锁定）→ `ReportAuthenticationService`（Argon2id）→ `password_change_token`（5 分钟一次性）或 RSA RS256 访问 Token（Redis 记录 + 主动撤销）；备份域 CRUD 与 `collection_enabled` 启停经 RPC 注册/删除三 Job；RPC 连通性测试固定 `cdm-data-cli verify-credentials`；已保存报告按 Token `sub` 隔离。

## Seam 分析

- 测试接缝：认证（改密一次性、Token 撤销、限流锁定）、域 CRUD 唯一性校验、连通性测试四类失败分类、保存报告隔离/模糊搜索。
- Mock/Stub：Redis 用 fakeredis 或测试实例；RPyC Job 用测试配置起的真实 Scheduler；CDM 通道连通性测试用 mock rpc 工具。

## 用户故事

1. 作为管理员，我想要首次登录强制改密与 Token 可撤销，以便控制会话安全。
2. 作为管理员，我想要域创建/启停/删除与连通性测试，以便纳管 CDM 备份域。

## 实现决策

- 落地仓库：**report-center 新仓库**。
- 依赖：T0215（Web API 子方案）、T0216（UserRepository/PreferenceRepository/ReadRepository）。
- 关键规则：采集账号不得登录页面（§3.1.2）；`rpt_backup_domain.password` AES 加密（`pycryptodome` AES-ECB+PKCS7）写入，日志/响应不回显（§3.1.1）；Token 私钥 `root:rdb-report` `0640`，启动校验密钥对匹配（§3.1.4）；备份域删除先停用→删 Job→同事务逻辑删除→删周期文件（§3.1.6）。
- 连通性测试四分类：`RPC_CONNECT_FAILED`/`RPC_TIMEOUT`/`RPC_CLI_AUTH_FAILED`/`RPC_EXEC_FAILED`（§3.1.7）。

## 测试决策

- 认证/Token/改密契约测试、限流滑动窗口、域名称唯一与模糊搜索、连通性测试成功与四类失败及无副作用、删除域历史数据保留、保存报告隔离。

## 验收标准

- [ ] AC-1: 验证码摘要存 Redis（TTL 5 分钟，5 秒刷新限制）；登录限流 20 分钟 5 次锁定；成功登录清除计数（§3.1.2）。
- [ ] AC-2: 首次安装 `admin` 幂等创建且 `must_change_password=true`；改密后一次性 Token 立即失效；复杂度 8~32 三类字符（§3.1.2、§3.1.3）。
- [ ] AC-3: 访问 Token RS256 签发，`sub`/管理员标记/iat/exp 服务端写入；每次请求校验签名 + Redis Token 存在；`POST /auth/logout` 删除实现主动撤销；TTL 修改仅影响新会话（§3.1.4）。
- [ ] AC-4: 域创建/启停/删除；名称 2~30 字符与全局唯一（含已删除）；创建域后 `ensure_domain_schedule_config`，启停经 `add_job`/`remove_job`，失败补偿回滚（§3.1、§4.2）。
- [ ] AC-5: 删除域先停用→删三 Job→同控制事务 `is_deleted=true`→删周期文件；周期文件删除失败不阻断（§3.1.6）。
- [ ] AC-6: 连通性测试固定 `verify-credentials`，10 秒超时，四类失败分类，无副作用（不建 Job/不改采集/不入库）（§3.1.7）。
- [ ] AC-7: 保存报告按 Token `sub` 隔离；名称全局唯一 2~30 字符；打开按保存快照重建 QuerySpec 查最新数据（§3.1.5）。
- [ ] AC-8: 密码/AES 密钥/Token 不回显于页面、响应、日志、审计；`--password` 日志脱敏（§3.1.1、§3.1.4）。

## 范围外

- 不做普通用户 CRUD/角色/用户同步。
- 不做采集任务明细页面展示。

## 备注

- 依赖：T0215、T0216、T0218（RPC Client 调用方）；下游：T0220、T0221、T0222。
