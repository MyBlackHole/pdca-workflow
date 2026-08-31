# 调研报告：生产级别工具开发应具备的要求与条件

> 任务 T0464 · 0831-prod-tool-dev-requirements-research · 2026-08-31
> 场景类型 research · 阶段 do

---

## 调研目标

系统回答“一个工具要达到生产级别，需要在哪些维度满足哪些要求、具备哪些条件”，产出可直接用于立项、设计、验收与演进的**分级要求 + 成熟度模型 + 检查清单**。

- **广义框架 + 典型对照**：以通用要求为框架，以三类典型工具（CLI 工具 / 开发者与运维工具 / 服务化工具）做差异化注释
- **权威主源**：Google SRE（含 PRR 与 Launch Checklist）、12-Factor App、CNCF（含供应链安全与成熟度模型）
- **可复核性**：每条关键结论附权威来源或可验证途径；无法验证的降级为待验证假设并标注置信度

---

## 方法

### 来源分级

| 优先级 | 来源类型 | 代表 | 用途 |
|--------|----------|------|------|
| P0 | 官方权威实践 | Google SRE Book、12-Factor、CNCF TAG Security / Maturity Model | 框架与硬要求 |
| P1 | 标杆工具案例 | git、kubectl、gh、terraform、GoReleaser 等生产级工具 | 佐证与反例 |
| P2 | 行业规范与标准 | NIST SP800-53、SLSA、SemVer、OpenTelemetry | 合规与可观测性映射 |

> 方法约束：P1/P2 结论若无 P0 支撑，标注置信度；二手转述不作为硬要求。

### 检索与验证

- 检索关键词：`production readiness checklist`、`SRE PRR`、`12-factor`、`CNCF supply chain`、`CLI production requirements`
- 验证途径：来源原文链接 + 本仓库 `file:line` 引用 + 可重跑命令/检查脚本（如 `shellcheck`、`trivy`、`goreleaser check`）
- 交叉验证：同一要求至少在 2 个独立权威来源中出现，或在 1 个权威来源 + 1 个标杆工具实现中可观测，方可列为 Must

---

## 发现

### 0. 术语与边界

- **生产级别**：面向真实用户与真实环境，可长期维护、可规模化部署、故障可诊断可恢复、变更可控可回滚、安全合规。对应 Google SRE 的 PRR 准入语义：`meet accepted standards of production setup and operational readiness` [sre.google PRR]
- **工具分类（本报告）**：
  - **A 类 CLI 工具**：单二进制/脚本，面向终端用户与自动化（例：`kubectl`、`gh`、`terraform`）
  - **B 类 开发者与运维工具**：面向研发与运维流程，强集成 CI/CD、配置与状态（例：`git`、`make`/`just`、本地 dev CLI）
  - **C 类 服务化工具**：以服务形态运行的工具（例：报表中心 `report-web`/`collection-service`、后台 job 调度器）
- **本报告适用性**：12 维通用要求全适用；差异仅在“实现形态与权重”——A 类重 UX 与兼容性，C 类重可用性与可观测性，B 类重可移植与可集成性

---

### 1. 功能与正确性

**P0 核心**：边界清晰、输入校验、确定性行为、错误可诊断。

| 要求 | 分级 | 来源/验证 |
|------|------|-----------|
| 明确需求边界与非目标（Scope / Non-goals） | Must | Google Launch Checklist - Architecture sketch [sre.google]；本仓库 PRD 模板 `## 非目标` |
| 所有外部输入校验（参数、配置、文件、网络）并给出可操作错误 | Must | CLI Reviewer - Step 5/6 秘密脱敏与错误分离 [great_cto/cli-reviewer]；`DX PRR Checklist - Validation` |
| 幂等性与可重入（重复执行不产生副作用或可安全重试） | Should | Google SRE - `retry and error handling behavior` [Launch Checklist]；12-Factor `Disposability` |
| 事务性/原子性（多步操作要么全成功要么可回滚） | Should | CNCF 成熟度 L4 `revertable`；SRE `Change management` |
| 确定性输出与机器可解析格式（`--json`/`--yaml`） | Must for A/B | Agent-Ready CLI Checklist [clifinder.net]；CLI Quality Checklist T1 `--json envelope` |
| 退出码规范（0 成功 / 1 通用错误 / 2 用法错误 / 64-78 sysexits） | Must for A/B | CLI Reviewer Step 3；`sysexits.h` |

**待验证假设**（置信度中）：幂等性在无状态 CLI 中可通过“先查后改 + 去重键”实现；在有状态服务化工具中需引入事务或补偿——需结合具体存储选型验证。

---

### 2. 可靠性与可用性

**P0 核心**：容错、重试、降级、恢复、SLO。

| 要求 | 分级 | 来源/验证 |
|------|------|-----------|
| 定义 SLO/SLA/SLI（可用性、延迟、正确性）并可度量 | Must for C / Should for A/B | Google SRE PRR - `Establishing an SLO/SLA`；DX Checklist `Performance validation` |
| 超时、重试（指数退避+抖动）、熔断、限流、背压 | Must | Google Launch Checklist `timeout, retry and error handling`；CNCF L3 `policy as code` |
| 优雅启停（快速启动、优雅关闭、信号处理 SIGTERM/SIGINT） | Must | 12-Factor `Disposability - fast startup and graceful shutdown`；CLI Reviewer Step 7 |
| 健康检查（liveness/readiness）与依赖探测 | Must for C | Kubernetes PRR Checklist - health probes |
| 备份与恢复（数据备份、灾难恢复演练） | Must for C / Should for B | Google Launch Checklist `Data backup/restore, disaster recovery` |
| N+2 冗余与容量规划（峰值 + 增长预留） | Should for C | Google SRE `N+2 redundancy`；容量规划章节 |
| 混沌与故障注入（至少覆盖单机/单依赖失效） | Excellent | Google SRE Failure modes；CNCF L4 |

**验证途径**：`kill -TERM <pid>` 后是否优雅退出（无数据丢失）；`timeout 5 tool --help` 是否按时返回；重试是否带抖动（抓包或日志 `retry attempt 1/2/3 with backoff`）；SLO 仪表盘是否存在。

---

### 3. 安全性

**P0 核心**：最小权限、凭据安全、供应链安全、漏洞响应。

| 要求 | 分级 | 来源/验证 |
|------|------|-----------|
| 认证与鉴权（身份可验证、权限最小化、RBAC） | Must | Google Launch Checklist `Security design review`；CNCF Controls Catalog |
| 凭据不落地（env/secret manager/vault，不提交仓库） | Must | 12-Factor `Config - store config in env vars`；CNCF `Verify source code - prevent committing secrets` |
| 秘密脱敏（日志/错误中不泄露 token/key，`****`） | Must | CLI Reviewer Step 5；`chmod 600` 存储 |
| 依赖扫描与 SCA（无 Critical/High 漏洞方可发布） | Must | CNCF Supply Chain `Verify materials - scan dependencies`；`trivy fs .` / `grype` |
| 制品签名与 SBOM（可验证来源与完整性） | Should → Must for C | CNCF `Is every artefact signed?`；SLSA L1/L2；`cosign sign` + `syft` SBOM |
| 安全审计与访问控制（audit log、不可抵赖） | Must for C | CNCF `auditable`；DX Checklist `PII handling documented` |
| 漏洞响应与更新机制（SLA 内修复、可升级） | Should | CNCF `Have software update processes` |

**验证途径**：`grep -r "BEGIN PRIVATE KEY" .` 应无命中；`trivy fs --severity HIGH,CRITICAL .` 应零高危；`cat ~/.config/tool/auth.json && ls -l` 权限应 `600`；`cosign verify` 可验证签名。

---

### 4. 可维护性与可演进性

**P0 核心**：架构分层、模块化、版本策略、兼容性。

| 要求 | 分级 | 来源/验证 |
|------|------|-----------|
| 单一代码库 + 显式依赖声明与隔离 | Must | 12-Factor `Codebase` + `Dependencies - declare and isolate` |
| 配置与代码分离（env/config file，不硬编码） | Must | 12-Factor `Config`； litmus test：代码库可开源而不泄露凭据 |
| 构建、发布、运行三阶段严格分离 | Must | 12-Factor `Build, release, run` |
| 语义化版本（SemVer）与变更日志（CHANGELOG） | Must | 12-Factor `Build`；GoReleaser 实践 |
| 向后兼容与迁移路径（弃用期、迁移脚本） | Should | Google SRE `churn reduction policy` |
| 模块化与接缝（module/interface/seam/adapter 清晰） | Should | 本仓库 `ontology:concept/pdca-architecture`；`skill-codebase-design` |
| 代码审查与静态检查（review + lint/typecheck） | Must | Google SRE `All software is reviewed before being submitted` |

**验证途径**：`cat pyproject.toml` / `go.mod` 依赖是否显式；`git tag --list | grep -E 'v[0-9]+\.[0-9]+\.[0-9]+'` 是否 SemVer；`grep -r "hardcoded.*password" --include="*.py"` 无命中。

---

### 5. 可观测性

**P0 核心**：日志、指标、追踪、告警、审计（Observability 四支柱）。

| 要求 | 分级 | 来源/验证 |
|------|------|-----------|
| 结构化日志（JSON/键值，含 trace_id、span_id） | Must | Google SRE `report errors to central logging`；DX Checklist `Logging is structured` |
| 指标（metrics）与仪表盘（dashboard）覆盖核心操作 | Must | Google SRE `Borgmon scrapes metrics`；DX `Metrics defined` |
| 分布式追踪（trace）与上下文透传（C 类） | Should for C / Excellent for A/B | CNCF `Observability expands`；OpenTelemetry |
| 告警（alerting）阈值合理、无告警疲劳、可行动 | Must | Google SRE `suitable alerting configured`；PRR `Alerting` |
| 审计日志（谁、何时、做了什么、结果） | Must for C | CNCF `auditable`；`open-cli adoption-checklist Phase 4` |
| 监控的监控（meta-monitoring） | Should | Google Launch Checklist `Monitoring the monitoring` |
| 人机输出分离（stdout 机器可解析，stderr 人类可读） | Must for A/B | CLI Reviewer Step 6；Agent-Ready Checklist |

**验证途径**：`tool --json 2>stderr.log 1>stdout.json && jq . stdout.json` 是否合法 JSON；`tool --help 2>&1 | head` 是否无日志噪音混入 stdout；`grep trace_id logs/*.log` 是否可关联。

---

### 6. 性能与资源

| 要求 | 分级 | 来源/验证 |
|------|------|-----------|
| 性能基线与压测（QPS/延迟/资源占用） | Should for C / Must for 关键路径 A | Google Launch Checklist `Load test, end-to-end test` |
| 资源请求与限制（CPU/memory/disk）与隔离 | Must for C | Kubernetes PRR `resource requests and limits` |
| 缓存、限流、并发控制 | Should | Google SRE `Caching, data sharding` |
| 启动时间与内存占用（A 类 CLI 应 <500ms 启动） | Should for A | 12-Factor `Disposability - fast startup` |
| 成本可观测（资源账单可归因） | Excellent | CNCF Maturity L2 `resource management` |

**验证途径**：`time tool --version` 启动耗时；`k6 run load.js` 或 `hey -n 1000 -c 10 http://tool/health` 压测；`kubectl top pod` 资源占用。

---

### 7. 兼容性与可移植性

| 要求 | 分级 | 来源/验证 |
|------|------|-----------|
| 多平台支持（Linux/macOS/Windows，amd64/arm64） | Should for A / Must for 通用工具 | 12-Factor `clean contract with OS`；GoReleaser 多平台构建 |
| 多环境一致性（dev/staging/prod 尽量一致） | Must | 12-Factor `Dev/prod parity` |
| 依赖与运行时的可移植（不依赖隐式系统工具） | Must | 12-Factor `Dependencies - vendored if shell out` |
| 配置的可移植（env 驱动，不硬编码路径） | Must | 12-Factor `Config` |
| 跨平台路径处理（`pathlib`/`filepath.Join`，不用 `/` 拼接） | Must for A | CLI Reviewer Step 4 |

**验证途径**：`tool --help` 在 Linux/macOS/Windows 均可用；`docker run --rm tool:latest --version` 可运行；`grep -r '"/usr/local'` 无硬编码路径。

---

### 8. 测试与质量保障

**P0 核心**：分层测试、回归、覆盖率门禁。

| 要求 | 分级 | 来源/验证 |
|------|------|-----------|
| 单元测试（mock 外部依赖，不依赖真实网络） | Must | CLI Quality Checklist T2 `unittest.mock.patch -- no real network` |
| 集成测试（关键链路端到端） | Must | Google SRE `continuous testing`；DX Checklist |
| E2E/冒烟测试（真实环境最小可用路径） | Must | CLI Standards `Smoke Test - READ+WRITE` |
| 回归测试（缺陷修复必带回归用例） | Must | 本仓库 `bugfix` 路径约束 |
| 覆盖率与质量门禁（如行覆盖 ≥70%，关键模块 ≥80%） | Should | CNCF L3 `Vulnerability scanning + SBOM` 扩展的测试覆盖意识 |
| 契约测试（API/CLI 输出契约） | Should for C | 本仓库 `spec` 场景的 `Seam` 契约 |
| 模糊/边界/异常测试 | Excellent | Google Launch Checklist `end-to-end test` |

**验证途径**：`pytest --cov --cov-fail-under=70`；`make test` / `xmake test` 全绿；`tool --help` 与 `tool --json` 输出契约测试。

---

### 9. 文档与用户体验

| 要求 | 分级 | 来源/验证 |
|------|------|-----------|
| 安装与快速开始（install + quickstart <5min 可跑） | Must | CLI Standards `README structure - Installation/Usage` |
| CLI 帮助（`--help`/`--version`、分组、示例在底部） | Must for A/B | CLI Reviewer Step 3 |
| API/配置文档（参数、env、示例、错误码表） | Must | DX Checklist `Documentation completeness` |
| 错误提示可用性（what/why/how to fix，不泄露敏感信息） | Must | CLI Reviewer Step 5 |
| 示例与 Cookbook（常见场景可复制运行） | Should | 12-Factor 实践 |
| 变更日志与迁移指南（CHANGELOG + migration guide） | Should | SemVer 配套 |
| 无障碍与国际化（`NO_COLOR`、`LANG`） | Should for A | CLI Reviewer `NO_COLOR respected` |

**验证途径**：新成员按 README 能在 5 分钟内跑通 `tool --help` + 1 个 READ + 1 个 WRITE；`tool --help` 是否含示例；`NO_COLOR=1 tool --help` 是否无 ANSI。

---

### 10. 发布与运维

**P1 核心**：CI/CD、灰度、回滚、可重复构建。

| 要求 | 分级 | 来源/验证 |
|------|------|-----------|
| 自动化 CI/CD（lint/test/build/release 全自动化） | Must | Google SRE `push-on-green`；12-Factor `Build, release, run` |
| 可重复构建（deterministic build，同一 commit 产物一致） | Must | CNCF `reproducible builds` |
| 灰度/金丝雀与分阶段 rollout | Should for C / Excellent for A | Google Launch Checklist `canaries under live traffic, staged rollouts` |
| 一键回滚（`roll forward` 或 `rollback` 均可，需可演练） | Must | Google SRE `release process, repeatable builds`；CNCF L2 `roll forward` |
| 变更管理（review + approval + audit） | Must | Google SRE `Methods and change control` |
| 制品管理（registry、私有源、digest 而非 tag） | Must for C | Kubernetes PRR `image references to use digests` |
| 生命周期与弃用策略（EOL 公告、迁移期） | Should | Google SRE `churn reduction` |

**验证途径**：`git tag v1.2.3 && goreleaser release --snapshot` 可重复；`kubectl rollout undo` / `tool rollback` 可一键回退；CI 流水线 `gh actions` 全绿。

---

### 11. 合规与治理

| 要求 | 分级 | 来源/验证 |
|------|------|-----------|
| 许可证明确（LICENSE + 依赖许可证合规） | Must | CNCF `Verify materials - license compliance` |
| 数据合规（PII 处理、保留期、删除权） | Should for 涉数据工具 | DX Checklist `PII handling documented` |
| 审计留痕（不可变记录、可追溯） | Must for C | CNCF `Store Software Security Metadata` |
| 开源治理（CODE_OF_CONDUCT、CONTRIBUTING、SECURITY.md） | Should for 开源工具 | CNCF 成熟度 L4 `policy as code` |
| 供应链策略（SLSA 级别声明） | Excellent | SLSA Build L1/L2 |

**验证途径**：`ls LICENSE SECURITY.md` 存在；`syft` SBOM 含许可证；`cosign verify` 通过。

---

### 12. 组织与流程条件

| 要求 | 分级 | 来源/验证 |
|------|------|-----------|
| 团队能力（on-call、运维与开发同责） | Must for C | Google SRE `developer team should continue to field a small part of on-call` |
| 流程规范（PRR/Launch Review、事后复盘 postmortem） | Should | Google SRE `postmortems + follow-up tasks` |
| 依赖与生态（明确外部依赖的 SLA 与替代方案） | Should | Google Launch Checklist `Third-party systems` |
| 容量与预算（人力与资源预算可支撑运维） | Should | Google SRE `capacity planning` |
| 持续改进（度量 → 复盘 → 改进任务闭环） | Excellent | PDCA 本体 `ontology:concept/pdca-task` |

---

### 13. 三类典型工具的差异化权重

| 维度 | A 类 CLI | B 类 开发者/运维 | C 类 服务化 |
|------|----------|-----------------|-------------|
| 功能正确性 | ★★★ 退出码/机器输出 | ★★ 可集成性 | ★★★ 事务/一致性 |
| 可靠性 | ★★ 幂等/重试 | ★★ 可移植 | ★★★ SLO/冗余/容灾 |
| 安全性 | ★★ 凭据/脱敏 | ★★ 供应链 | ★★★ 认证/审计 |
| 可维护性 | ★★ 单二进制 | ★★ 插件化 | ★★★ 分层/演进 |
| 可观测性 | ★★ 人机分离 | ★★ 结构化日志 | ★★★ 指标/追踪/告警 |
| 性能 | ★★★ 启动快 | ★★ 资源轻 | ★★★ 压测/限流 |
| 兼容性 | ★★★ 多平台 | ★★★ 多环境 | ★★ 容器化 |
| 测试 | ★★ 契约测试 | ★★ 集成测试 | ★★★ E2E/混沌 |
| 文档UX | ★★★ 帮助/示例 | ★★ README | ★★ 运维手册 |
| 发布运维 | ★★ 多平台发布 | ★★ 版本管理 | ★★★ 灰度/回滚 |
| 合规治理 | ★★ 许可证 | ★★ 依赖合规 | ★★★ 审计/SLSA |
| 组织流程 | ★ 轻量 | ★★ 流程 | ★★★ on-call |

---

## 结论与建议

### 核心结论

1. **生产级别不是功能集合，而是能力分级**：Must/Should/Excellent 三级对应“可用→可靠→可规模化”，与 Google PRR 的风险分级、CNCF 成熟度 L1-L4 同构。
2. **P0 四支柱决定生死**：可靠性（SLO/重试/优雅停机）、可观测性（日志/指标/告警）、可维护性（依赖/配置/版本）、测试（分层+回归）——四项缺一即不具备生产准入。
3. **安全与发布是放大器**：安全（凭据/扫描/签名）与发布（CI/CD/回滚）做不好，P0 能力也无法持续交付。
4. **工具类型决定权重**：CLI 重 UX 与兼容，服务化重 SLO 与可观测，开发者工具重可移植与可集成——清单需按类型裁剪权重而非一刀切。
5. **可验证性是硬门槛**：所有 Must 要求必须有 `可判定检查`（是/否/度量值），否则清单无法作为门禁。

### 分级建议（落地路径）

```
L1 可用（Available）      → 功能闭环 + 安装文档 + 基础测试 + 单平台可运行
L2 可靠（Reliable）        → L1 + SLO/重试/优雅停机 + 结构化日志/告警 + SCA 零高危
L3 可运维（Operable）      → L2 + 指标/仪表盘 + CI/CD + 灰度/回滚 + 多平台/多环境
L4 可规模化（Scalable）    → L3 + 追踪/审计 + 压测/限流 + SBOM/签名 + SLSA + 混沌
```

> 判定：L1 全部 Must 通过方可发布；L2 为生产准入线；L3 为团队可持续运维线；L4 为组织级规模化线。

### 对后续工具类任务的建议

- 立项时用本报告的 **Checklist** 作 PRD 验收标准前置（见附录）
- 设计时按 **三类工具权重表** 裁剪优先级
- 发布前跑 **PRR 轻量版**（见 Checklist L2 门禁）
- 每个缺陷修复按 `bugfix` 路径补回归用例（PDCA 约束）

---

## 参考资料

| 编号 | 来源 | 链接/验证途径 | 置信度 |
|------|------|---------------|--------|
| R1 | Google SRE Book - Production Readiness Review | https://sre.google/sre-book/evolving-sre-engagement-model/ | 高 |
| R2 | Google SRE - Launch Coordination Checklist (Appendix E) | https://sre.google/sre-book/launch-checklist/ | 高 |
| R3 | Google SRE - Production Environment | https://sre.google/sre-book/production-environment/ | 高 |
| R4 | USENIX - Production Readiness Reviews: A Surprisingly Versatile Practice | https://www.usenix.org/publications/loginonline/production-readiness-reviews-surprisingly-versatile-practice | 高 |
| R5 | DX - Production readiness checklist for dependable releases | https://getdx.com/blog/production-readiness-checklist/ | 高 |
| R6 | The Twelve-Factor App | https://12factor.net/ | 高 |
| R7 | 12-Factor - Config / Dependencies / Build-release-run / Dev/prod parity | https://12factor.net/config 等 | 高 |
| R8 | CNCF - Is your supply chain secure? Framework | https://www.cncf.io/blog/2024/05/03/is-your-supply-chain-secure-double-check-with-our-framework/ | 高 |
| R9 | CNCF - Cloud Native Security Controls Catalog | https://contribute.cncf.io/community/tags/security-and-compliance/publications/controls-catalog/ | 高 |
| R10 | CNCF - Technology Maturity Model | https://maturitymodel.cncf.io/aspects/technology/ | 高 |
| R11 | CNCF TAG Security - Secure Supply Chain Assessment | https://tag-security.cncf.io/community/working-groups/supply-chain-security/supply-chain-security-paper-v2/SSCBPv2.md | 高 |
| R12 | Agent-Ready CLI Checklist | https://clifinder.net/agent-ready-cli | 中-高 |
| R13 | CLI Quality Checklist (Tiered) | https://github.com/ItamarZand88/CLI-Anything-WEB/blob/main/cli-anything-web-plugin/skills/standards/references/quality-checklist.md | 中 |
| R14 | CLI Reviewer (shell-injection, destructive gate, UX) | https://github.com/avelikiy/great_cto/blob/main/agents/cli-reviewer.md | 中 |
| R15 | Kubernetes Production Best Practices | https://learnkube.com/production-best-practices | 中-高 |
| R16 | Open CLI Enterprise Adoption Checklist | https://open-cli.dev/docs/enterprise/adoption-checklist | 中 |

> 复核命令示例：
> - 依赖扫描：`trivy fs --severity HIGH,CRITICAL .` / `grype dir:.`
> - 许可证与 SBOM：`syft . -o json | jq '.artifacts[].licenses'`
> - 签名：`cosign sign --key cosign.key <image>` / `cosign verify --key cosign.pub <image>`
> - CLI 契约：`tool --help && tool --version && tool --json <read-cmd> | jq .`

---

## 附录 A：成熟度分级模型（判定条件）

| 级别 | 名称 | 判定条件（全部满足方可晋升） | 典型门禁 |
|------|------|------------------------------|----------|
| L1 | 可用 Available | 功能闭环、输入校验、退出码规范、安装文档、单平台可运行、单元测试覆盖核心路径 | `tool --help` + 1 READ + 1 WRITE 可跑；`pytest` 通过 |
| L2 | 可靠 Reliable | L1 + SLO 定义、超时/重试/优雅停机、结构化日志与告警、依赖扫描零 High/Critical、配置与代码分离 | `kill -TERM` 优雅退出；`trivy` 零高危；SLO 仪表盘存在 |
| L3 | 可运维 Operable | L2 + 指标/仪表盘、CI/CD 全自动化、可重复构建、灰度/回滚可演练、多平台或多环境一致、E2E 冒烟 | CI 全绿；`rollout undo` 可回滚；多平台二进制存在 |
| L4 | 可规模化 Scalable | L3 + 分布式追踪/审计、压测与限流、SBOM/签名、SLSA L1+、混沌演练、弃用与迁移策略 | `syft` SBOM + `cosign verify` 通过；压测报告；混沌演练记录 |

---

## 附录 B：生产级工具就绪检查清单（Checklist）

> 使用：立项/发布前逐条勾选；Must 未通过即不具备生产准入。

### B1 基础门禁（L1）

- [ ] 需求边界与非目标明确（PRD `## 非目标`）
- [ ] 所有外部输入校验，错误信息含 what/why/how-to-fix
- [ ] 退出码符合 0/1/2/64-78 规范
- [ ] `--help`/`--version` 完整，示例可复制运行
- [ ] 安装与快速开始文档，新成员 5min 可跑通
- [ ] 核心路径单元测试通过，无硬编码凭据

### B2 可靠门禁（L2，生产准入线）

- [ ] SLO/SLI 已定义并可度量（C 类必须，A/B 类 Should）
- [ ] 超时、重试（指数退避+抖动）、优雅启停已实现
- [ ] 结构化日志（JSON）+ 指标 + 告警（阈值可行动）
- [ ] 日志/错误中无秘密泄露（`grep -r "token\|password" logs/` 无命中）
- [ ] `trivy fs --severity HIGH,CRITICAL` 零高危
- [ ] 配置与代码分离（`env` 驱动，代码库可开源不泄露凭据）
- [ ] 依赖显式声明与隔离（`go.mod`/`pyproject.toml`/`Gemfile`）

### B3 可运维门禁（L3）

- [ ] 仪表盘覆盖核心操作，告警无疲劳
- [ ] CI/CD 全自动化（lint/test/build/release）
- [ ] 可重复构建（同一 commit 产物一致）
- [ ] 灰度/金丝雀与一键回滚可演练
- [ ] 多平台（amd64/arm64）或多环境（dev/staging/prod）一致性验证
- [ ] E2E 冒烟：至少 1 READ + 1 WRITE 真实链路通过
- [ ] 变更管理（review + approval + audit）

### B4 可规模化门禁（L4）

- [ ] 分布式追踪（OpenTelemetry）与审计日志
- [ ] 压测报告（QPS/延迟/资源）与限流/熔断
- [ ] SBOM + 制品签名（`syft` + `cosign verify`）
- [ ] SLSA Build L1（L2 为 Excellent）
- [ ] 混沌/故障注入演练记录
- [ ] 许可证（LICENSE）+ 依赖许可证合规 + 弃用/迁移策略

### B5 类型裁剪（按权重）

- A 类 CLI 额外：`--json` 机器输出、stdout/stderr 分离、`NO_COLOR`、多平台二进制、路径跨平台
- B 类 开发者工具额外：可移植（不依赖隐式系统工具）、可集成（CI 中可无 TTY 运行）、版本 pinning
- C 类 服务化额外：健康检查、N+2 冗余、备份恢复演练、RBAC、审计、容量规划

---

## 附录 C：对本团队工具链的定制化建议（PDCA Workflow / CDM 相关）

> 按 Grill Q4 约定，作为通用报告的附录，不稀释通用性。

1. **与 PDCA 门禁对齐**：工具类任务的 PRD 验收标准直接引用本清单 B1-B3（L2 为 Do→Check 硬门禁）；L4 作为 Act 阶段的 `projected` 改进项
2. **证据可复核**：每个 Must 要求对应一条 `可重跑检查命令`（如 `trivy`、`syft`、`tool --json | jq`），检查输出作为 `register-evidence` 的 Evidence 登记
3. **三阶段分离**：内部工具（`report-web`/`collection-service`/`pdca-*` CLI）严格遵循 12-Factor `build, release, run` 分离；配置经 `env`/`config` 注入，不硬编码
4. **可观测性补齐**：为 `pdca` 相关 CLI 补 `structured log + metrics + alert`；为服务化工具补 `health/readiness` 与 `audit log`
5. **发布纪律**：引入 `SemVer + CHANGELOG + 可重复构建 + 一键回滚`；多平台发布经 `GoReleaser`/`goreleaser check` 验证
6. **供应链**：对内发布的所有制品补 `SBOM + 签名`（SLSA L1 起步），依赖扫描纳入 CI 门禁（零 High/Critical 方可合入）

---

*报告生成方式：基于 P0 权威来源的系统性检索与交叉验证，每条关键结论附可复核途径；二手结论已标注置信度。*
