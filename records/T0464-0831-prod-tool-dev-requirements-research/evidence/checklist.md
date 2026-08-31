# 生产级工具就绪检查清单（Checklist）

> 来源：T0464 调研报告 `research-report.md` 附录 B 抽取 · 可直接用于立项评审与发布门禁
> 使用：逐条勾选；Must 未通过即不具备生产准入；按工具类型裁剪权重见末节

---

## B1 基础门禁（L1 可用）— 全部 Must

- [ ] 需求边界与非目标明确（PRD `## 非目标` 已写）
- [ ] 所有外部输入校验，错误信息含 what / why / how-to-fix
- [ ] 退出码符合 0 成功 / 1 通用错误 / 2 用法错误 / 64-78 sysexits.h
- [ ] `--help` / `--version` 完整，示例可复制运行
- [ ] 安装与快速开始文档，新成员 5min 可跑通 `tool --help` + 1 READ + 1 WRITE
- [ ] 核心路径单元测试通过，无硬编码凭据（`grep -r "password" --include="*.py"` 无命中）

## B2 可靠门禁（L2 生产准入线）— 全部 Must

- [ ] SLO / SLI 已定义并可度量（C 类必须，A/B 类 Should）
- [ ] 超时、重试（指数退避+抖动）、优雅启停已实现（`kill -TERM` 优雅退出）
- [ ] 结构化日志（JSON，含 trace_id）+ 指标 + 告警（阈值可行动，无疲劳）
- [ ] 日志/错误中无秘密泄露（`grep -r "token\|password" logs/` 无命中；`chmod 600`）
- [ ] `trivy fs --severity HIGH,CRITICAL .` 零高危（或有处置记录）
- [ ] 配置与代码分离（env 驱动；litmus test：代码库可开源不泄露凭据）
- [ ] 依赖显式声明与隔离（`go.mod` / `pyproject.toml` / `Gemfile` + 隔离工具）

## B3 可运维门禁（L3）

- [ ] 仪表盘覆盖核心操作，告警可行动
- [ ] CI/CD 全自动化（lint / test / build / release）
- [ ] 可重复构建（同一 commit 产物一致，可验证）
- [ ] 灰度/金丝雀与一键回滚可演练（`rollout undo` / `tool rollback`）
- [ ] 多平台（amd64/arm64）或多环境（dev/staging/prod）一致性验证
- [ ] E2E 冒烟：至少 1 READ + 1 WRITE 真实链路通过
- [ ] 变更管理（review + approval + audit 留痕）

## B4 可规模化门禁（L4）

- [ ] 分布式追踪（OpenTelemetry）与审计日志（谁/何时/做了什么/结果）
- [ ] 压测报告（QPS/延迟/资源）与限流/熔断/背压
- [ ] SBOM + 制品签名（`syft` + `cosign verify` 通过）
- [ ] SLSA Build L1（L2 为 Excellent）
- [ ] 混沌/故障注入演练记录（至少单机/单依赖失效）
- [ ] 许可证（LICENSE）+ 依赖许可证合规 + 弃用/迁移策略

## B5 类型裁剪

- **A 类 CLI** 额外：`--json` 机器输出、stdout/stderr 分离、`NO_COLOR` 尊重、多平台二进制、路径跨平台（`pathlib`/`filepath.Join`）
- **B 类 开发者/运维工具** 额外：可移植（不依赖隐式系统工具）、可无 TTY 运行、版本 pinning
- **C 类 服务化工具** 额外：健康检查（liveness/readiness）、N+2 冗余、备份恢复演练、RBAC、容量规划

---

## 成熟度判定

| 级别 | 名称 | 晋升条件 |
|------|------|----------|
| L1 | 可用 Available | B1 全部通过 |
| L2 | 可靠 Reliable | L1 + B2 全部通过 |
| L3 | 可运维 Operable | L2 + B3 全部通过 |
| L4 | 可规模化 Scalable | L3 + B4 全部通过 |

> 门禁建议：L1 方可发布；L2 为生产准入线；L3 为团队可持续运维线；L4 为组织级规模化线。
