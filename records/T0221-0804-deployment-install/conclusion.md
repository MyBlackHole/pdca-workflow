---
schema: pdca.asset/v1
id: T0221-0804-deployment-install
phase: check
source_ids: [test-deploy-check, install-drill, dual-platform-design]
---

## 上下文

T0221 实现报表中心两阶段安装部署与配置校验（AC-1~AC-7）。Do 阶段产出：
- 预安装 `1.pre_install`/`2.install`（AC-1/AC-2）
- 正式安装 `install.sh` 编排（AC-3/AC-5）
- `--check-config` 配置校验（AC-6）
- `--install-db` 真实 DB 迁移 + admin 幂等创建（AC-4）
- `deploy_health.py` 探针框架、systemd 单元、manifest、version
- 版本 0.4.0 → 0.5.0，提交 e9e9b24

## 假设与结果

| 假设 | 结果 |
|------|------|
| AC-1 预安装失败非零不标记 | 成立：依赖缺失→MISSING=1→exit 1，不写标记（演练） |
| AC-2 预安装不建 Schema/账号/服务 | 成立：脚本无任何 CREATE/账号/Web 入口操作（grep 验证） |
| AC-3 正式包校验失败即退出 | 成立：完整性/manifest/平台/预装标识逐项校验（演练） |
| AC-4 admin 幂等+升级不重置 | 成立：真实 PG 首装"创建"→升级"复用已有"；ensure_bootstrap_admin 单测（幂等返回 False） |
| AC-5 健康检查门禁 | 成立：端口缺失→拒绝不标记；--force→写标记；探针框架 5 单测 |
| AC-6 --check-config 非法拒绝 | 成立：超时顺序/周期目录校验，CLI 6 单测 + 安装预检演练 |
| AC-7 双平台验收 | 设计留档：脚本含 x86_64/aarch64 支持；实机验收延后 T0222 |

## 分析

- 测试：新增 17 用例全绿；全量 313 passed，6 errors 均为既有 `REPORT_TOKEN_PRIVATE_KEY` 环境问题，与本次变更无关。
- 收敛映射 valid: true，7 条 AC 均有证据映射。
- 双轴代码审查：标准轴无 Blocking；规范轴发现 AC-4 DB 迁移占位缺口 → 补 `deploy_install.py` + `--install-db` 真实装配，审查后无 Blocking。
- 关键设计取舍：健康检查的 report_db/jobstore/login 探针为"由装配入口校验"占位（真实 DB 可达性由 `--install-db` 强保证）；端口成功路径依赖沙箱外验证（沙箱禁 bind）。

## 失败原因（仅 rejected/partial）

无。

## 适用边界

- 沙箱禁 bind TCP 端口 → 健康检查"通过路径"由单测保证，未做端到端端口成功演练（环境限制，非代码缺陷）。
- AC-7 双平台实机安装/卸载/升级/回退验收未在本任务执行，延后 T0222 目标环境。
- 健康检查的 process/jobstore/login 探针为框架占位，真实服务装配校验在 T0218/T0219 服务侧已具备。

## 下一轮建议

- T0222 在目标环境执行 AC-7 双平台验收，回填验收记录。
- T0224 异步导出任务（由 T0220 拆解，plan 阶段）。
- 若安装链路在真实主机暴露问题，回退方案为 `git revert` + 重装 + migration down.sql。
