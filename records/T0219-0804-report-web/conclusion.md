---
schema: pdca.asset/v1
id: T0219-0804-report-web
phase: check
source_ids:
  - e1-pytest-full
  - e2-s1-slices
  - e3-s2-slices
  - e4-s3-slices
  - e5-s4-web-api
---

## 上下文

T0214 备份与恢复可视化平台（report-center）的子任务 T0219：report-web 登录鉴权（验证码登录 / Token 鉴权 / 改密）与备份域管理服务（域 CRUD / 启停 / RPC 连通性测试 / 保存报告按 sub 隔离）。

依赖 T0215/T0216/T0218（RPC 调用方），下游 T0220/T0221/T0222。技术栈：FastAPI + uvicorn + redis-py（生产）/ fakeredis（测试）+ argon2-cffi + pycryptodome + cryptography + PyJWT。开发路径（development）。

## 假设与结果

- 假设：AC-1~AC-8 全部可通过 report-center venv 内测试验证。
- 结果：全量 pytest 237 passed（基线 + T0219 新增 93 项）。AC-1~AC-6、AC-8 **confirmed**；AC-7 **partial**（已知边界）。

### 结论

**整体 confirmed（AC-7 partial 作为已知边界）。** T0219 功能实现完成并通过 A4 双轴审查（发现 8 个 Blocking 全部修复并回归）。用户 verdict=confirmed，AC-7 边界由 T0220 闭环。

| AC | 结论 | 证据 |
|----|------|------|
| AC-1 验证码 Redis TTL/限流 + 登录锁定 | confirmed | e1, e2, e5 |
| AC-2 admin 幂等引导 + 改密 token 撤销 | confirmed | e1, e2, e5 |
| AC-3 Token RS256 + 校验 + 撤销 + TTL 新会话 | confirmed | e1, e2, e5 |
| AC-4 域 CRUD/启停 + 调度 Job + 补偿回滚 | confirmed | e1, e3, e5 |
| AC-5 删除顺序 + 周期文件尽力 | confirmed | e1, e3, e5 |
| AC-6 verify-credentials 固定 + 四类分类 + 无副作用 | confirmed | e1, e3, e5 |
| AC-7 保存报告 sub 隔离 + 快照重建 | **partial** | e1, e4, e5 |
| AC-8 敏感信息不回显日志 | confirmed | e1, e5 |

## 分析

- **A4 双轴审查收敛**：标准轴 5 Blocking + 规范轴 4 Blocking，去重 8 项。全部已修复：
  限流 key 归一化（防大小写绕过）、TTL 生效（ttl_provider）、域创建唯一冲突精确捕获、域删除顺序、保存报告 per-owner 唯一（V002）、首装 admin 引导、GET/PATCH saved-reports 端点、RPC 通道异常分类。
- **V002 迁移**：保存报告唯一约束从全局改为 per-owner（`uq_rpt_saved_report_owner_name`），消除"用户 B 无法保存与用户 A 同名报告"的子隔离冲突。test_migrations 的 V001 down 会删全部表，恢复时重放全部版本补 V002。
- **测试基建修复**：conftest `_ensure_schema` 改为确保所有迁移应用（而非仅 V001），使 V002 在共享测试库可靠生效。

## 失败原因（仅 rejected/partial）

AC-7 部分验证：prd 写明"打开按保存快照重建 QuerySpec 查最新数据"经 TemplateRegistry 协议注入，但**真实端到端**依赖 T0220 采集报表模板。T0219 完成：保存报告 CRUD、按 sub 隔离、per-owner 唯一、快照保存与 TemplateRegistry 协议接口。打开-重建-查最新数据的真实验证留待 T0220，属计划阶段已确认的 T0219/T0220 边界决策。

## 适用边界

- 本结论适用于 report-center 后端的登录鉴权与备份域管理服务层。
- AC-7 打开重建的端到端验证未被 T0219 覆盖，T0220 前不应宣称"打开报告查询最新数据"完全验收。
- 非功能项：限流/TTL 走 Redis，未做高并发压测；RPC 失败补偿依赖 T0218 服务端稳定。
- 测试用 fakeredis（模拟 Redis）与 podman PG 容器（t0216-pg）。

## 下一轮建议

- **T0220** 落地后按真实模板对 AC-7"打开重建 QuerySpec 查最新数据"做端到端验证，闭环 partial。
- T0221/T0222（下游页面）接入 /auth /domains /saved-reports 契约时复验 T0219 返回错误码映射一致性。
- 长期：登录限流与 Token 撤销的生产规模压测；V002 迁移在真实既有数据上验证回滚路径。