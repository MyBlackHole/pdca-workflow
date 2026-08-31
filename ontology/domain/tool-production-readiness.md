---
schema: pdca.asset/v1
id: ontology:domain/tool-production-readiness
type: domain
layer: Knowledge
status: active
summary: 生产级工具就绪度领域知识：12维分级要求、L1-L4成熟度模型与B1-B4检查清单
relations:
  specializes:
    - ontology:concept/pdca
  relates_to:
    - ontology:concept/pdca-task
    - ontology:domain/skill-research
    - ontology:concept/pdca-ontology-ready
  guides:
    - ontology:concept/pdca-task
attributes:
  - name: twelve_dimensions
    desc: 12个生产就绪维度及其Must/Should/Excellent分级
    constraint: 覆盖功能正确性、可靠性与可用性、安全性、可维护性与可演进性、可观测性、性能与资源、兼容性与可移植性、测试与质量保障、文档与用户体验、发布与运维、合规与治理、组织与流程条件；每维至少1条Must
    testable_signal: 对照 records/T0464-0831-prod-tool-dev-requirements-research/evidence/research-report-v2.md 的"发现"章节，校验12个维度标题均存在且每维含"Must/Should/Excellent"分级，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空
  - name: maturity_model
    desc: L1可用→L2可靠→L3可运维→L4可规模化四级成熟度模型
    constraint: 每级有明确判定条件与典型门禁，L1全部Must通过方可发布，L2为生产准入线
    testable_signal: 检查本文件"成熟度模型"章节含L1/L2/L3/L4四级定义，且每级含判定条件与门禁清单，与 records/T0464-0831-prod-tool-dev-requirements-research/evidence/research-report-v2.md 附录A一致
  - name: checklist
    desc: B1-B4四级就绪检查清单与类型裁剪
    constraint: 清单条目为可判定项（是/否/度量值），按A类CLI/B类开发者与运维/C类服务化裁剪权重
    testable_signal: 校验本文件"检查清单"章节含B1/B2/B3/B4四级清单，且每条含勾选框与可重跑验证命令（如 trivy fs、syft、cosign verify、tool --json | jq），与 records/T0464-0831-prod-tool-dev-requirements-research/evidence/checklist.md 条目一致
  - name: authoritative_sources
    desc: 每条关键结论附权威来源与可验证途径
    constraint: 关键结论关联R1-R16权威来源或可重跑命令，无法验证的标注待验证假设与置信度
    testable_signal: 抽样检查本文件任一Must要求可追溯至"参考资料"中至少一条来源（sre.google/12factor.net/cncf.io）或一条可重跑命令
---

# 生产级工具就绪度（tool-production-readiness）

> 来源：T0464 调研报告 `records/T0464-0831-prod-tool-dev-requirements-research/evidence/research-report-v2.md:1` 与 `checklist.md:1`
> 权威主源：Google SRE PRR/Launch Checklist、12-Factor App、CNCF 供应链与成熟度模型

生产级别工具指面向真实用户与真实环境，可长期维护、可规模化部署、故障可诊断可恢复、变更可控可回滚、安全合规的工具。本领域沉淀其**12维分级要求、L1-L4成熟度模型与B1-B4检查清单**，作为工具类任务立项、设计、验收与演进的本体依据。

## 12维分级要求

| 维度 | 核心要求（Must 示例） | 来源 |
|------|----------------------|------|
| 1. 功能与正确性 | 输入校验、确定性行为、退出码规范、机器可解析输出 | SRE Launch Checklist, 12-Factor |
| 2. 可靠性与可用性 | SLO/SLI、超时重试（指数退避+抖动）、优雅启停、健康检查、备份恢复 | SRE PRR, 12-Factor Disposability |
| 3. 安全性 | 最小权限、凭据不落地、秘密脱敏、依赖扫描零High/Critical、制品签名与SBOM | CNCF Supply Chain |
| 4. 可维护性与可演进性 | 单一代码库+显式依赖、配置与代码分离、三阶段分离、SemVer、兼容与迁移 | 12-Factor |
| 5. 可观测性 | 结构化日志、指标与仪表盘、追踪、告警、审计、人机输出分离 | SRE Borgmon, OpenTelemetry |
| 6. 性能与资源 | 性能基线与压测、资源请求与限制、限流熔断 | SRE Capacity Planning |
| 7. 兼容性与可移植性 | 多平台/多环境一致性、可移植依赖、跨平台路径处理 | 12-Factor Dev/prod parity |
| 8. 测试与质量保障 | 单元/集成/E2E分层、回归、覆盖率门禁、契约测试 | SRE Continuous Testing |
| 9. 文档与用户体验 | 安装快速开始、--help/--version、错误可用性、NO_COLOR | CLI Reviewer |
| 10. 发布与运维 | CI/CD全自动化、可重复构建、灰度与回滚、变更管理 | SRE Push-on-green |
| 11. 合规与治理 | 许可证、数据合规、审计留痕、SLSA | CNCF Controls Catalog |
| 12. 组织与流程条件 | on-call、PRR/Postmortem、依赖SLA、持续改进 | SRE Engagement Model |

> 差异化权重：A类CLI重UX与兼容，C类服务化重SLO与可观测，B类开发者工具重可移植与可集成（见报告§13权重表）

## 成熟度模型

| 级别 | 名称 | 判定条件 | 典型门禁 |
|------|------|----------|----------|
| L1 | 可用 Available | 功能闭环、输入校验、退出码规范、安装文档、单平台可运行 | `tool --help` + 1 READ + 1 WRITE 可跑 |
| L2 | 可靠 Reliable | L1 + SLO、超时/重试/优雅停机、结构化日志与告警、SCA零高危、配置与代码分离 | `kill -TERM` 优雅退出；`trivy`零高危 |
| L3 | 可运维 Operable | L2 + 指标/仪表盘、CI/CD、可重复构建、灰度/回滚、多平台一致、E2E冒烟 | CI全绿；`rollout undo`可回滚 |
| L4 | 可规模化 Scalable | L3 + 追踪/审计、压测与限流、SBOM/签名、SLSA、混沌演练 | `syft` SBOM + `cosign verify` 通过 |

> 门禁建议：L1方可发布；L2为生产准入线；L3为团队可持续运维线；L4为组织级规模化线。

## 检查清单

### B1 基础门禁（L1）

- [ ] 需求边界与非目标明确
- [ ] 外部输入校验，错误含 what/why/how-to-fix
- [ ] 退出码 0/1/2/64-78 规范
- [ ] --help/--version 完整，示例可复制
- [ ] 安装与快速开始文档，5min可跑通
- [ ] 核心路径单元测试通过，无硬编码凭据

### B2 可靠门禁（L2 生产准入线）

- [ ] SLO/SLI 已定义并可度量
- [ ] 超时、重试（指数退避+抖动）、优雅启停
- [ ] 结构化日志（JSON）+ 指标 + 告警
- [ ] 日志/错误中无秘密泄露
- [ ] `trivy fs --severity HIGH,CRITICAL` 零高危
- [ ] 配置与代码分离（env驱动）
- [ ] 依赖显式声明与隔离

### B3 可运维门禁（L3）

- [ ] 仪表盘与告警可行动
- [ ] CI/CD全自动化
- [ ] 可重复构建
- [ ] 灰度/金丝雀与一键回滚可演练
- [ ] 多平台或多环境一致性验证
- [ ] E2E冒烟 1 READ + 1 WRITE 通过
- [ ] 变更管理（review+approval+audit）

### B4 可规模化门禁（L4）

- [ ] 分布式追踪与审计日志
- [ ] 压测报告与限流/熔断
- [ ] SBOM + 制品签名
- [ ] SLSA Build L1
- [ ] 混沌/故障注入演练记录
- [ ] 许可证与依赖合规

## 参考资料

- R1 Google SRE PRR https://sre.google/sre-book/evolving-sre-engagement-model/
- R2 Launch Checklist https://sre.google/sre-book/launch-checklist/
- R6 12-Factor https://12factor.net/
- R8 CNCF Supply Chain https://www.cncf.io/blog/2024/05/03/is-your-supply-chain-secure-double-check-with-our-framework/
- 完整R1-R16见 `records/T0464-0831-prod-tool-dev-requirements-research/evidence/research-report-v2.md:1` 参考资料表

## 与PDCA流程的衔接

- 立项时用本清单作PRD验收标准前置
- 设计时按三类工具权重裁剪优先级
- 发布前跑PRR轻量版（L2门禁）
- 缺陷修复按bugfix路径补回归用例

## 溯源

- 调研任务：T0464 `pdca/tasks/archive/2026-08/0831-prod-tool-dev-requirements-research/task.json:1`
- 证据：`records/T0464-0831-prod-tool-dev-requirements-research/evidence/research-report-v2.md:1`、`checklist.md:1`
- 结论：`records/T0464-0831-prod-tool-dev-requirements-research/conclusion.md:1` verdict confirmed
