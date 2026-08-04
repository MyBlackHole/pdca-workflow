# PDCA 共享术语表

由 `domain-modeling` 技能维护。在此记录项目中使用的关键术语、缩写和约定。

## 核心术语

| 术语 | 定义 |
|------|------|
| **PDCA** | Plan-Do-Check-Act 四阶段循环，AI 代理执行协议的核心周期 |
| **Seam** | 测试接缝，测试的公共边界接口 |
| **YAGNI** | You Ain't Gonna Need It，只构建当前需要的功能 |
| **PRD** | 产品需求文档，Plan 阶段的输出产物 |
| **task.json** | 任务元数据文件，跟踪阶段、状态和标记 |
| **skill** | 可复用的 AI 指令模块，对应 skills/ 下的 SKILL.md |
| **ADR** | 架构决策记录，存于 docs/adr/ |
| **grill** | 追问门禁，用户发起，委托 grilling 执行 |
| **triage** | 任务分诊，将模糊输入转换为结构化任务 |
| **严格任务 schema** | T0135 起采用的任务数据合约；新数据必须完整满足 schema，不为旧任务格式增加兼容分支 |
| **能力协议** | flow/skill 只声明所需抽象能力、是否必需及降级策略；具体 Agent 平台工具名由适配层解析 |
| **内容成本指标** | 默认使用 UTF-8 bytes 进行跨环境比较；模型真实 token 只由 Agent runner 实测 |
| **内容预算** | 每个 flow/skill 资产的版本化 UTF-8 bytes baseline；默认拒绝增长，只有记录必要性并通过非退化验证的显式豁免才可更新 |
| **确定性夹具** | 输入、预期输出和 pass/fail 信号均固定，可在不调用 Agent 模型的情况下重复执行的测试场景 |
| **路由合约** | AI 友好评测使用的严格、机器可读 scenario→路径映射，是测试的唯一事实源；用于验证导航与评测 oracle，不等同于真实模型能力或语义成功率 |
| **生命周期夹具** | 使用真实 gate/transition 逻辑构造的 PDCA 完整成功路径与按转换分组的关键失败路径；不以手工常量返回替代门禁行为 |
| **convergence map** | Do 收尾时生成并登记的结构化证据映射；逐条把 Plan 中的 `meta.convergence` 回链到 PRD 验收条件和已登记 evidence ID，本身不作为验收通过证据 |
| **Flow Issue Occurrence** | 一次具体发生、可追溯且写入后不可修改的 PDCA 机制问题事实；不等同于聚合问题或改进授权 |
| **Flow Issue** | 由一个或多个 occurrence 按版本化 fingerprint 确定性聚合出的 PDCA 机制问题视图；可重建，不是事实源 |
| **Flow Issue Decision** | 对 Flow Issue 作出的带确认者、理由和时间的不可变治理回执，如 impact、false-positive、accepted-risk、关闭或候选晋级 |
| **Improvement Candidate** | 基于 Flow Issue 生成、尚未获得修改权威流程授权的改进提案；包含依据、预期指标、风险和验证计划 |
| **Improvement Task** | Improvement Candidate 经用户确认后创建的正式 PDCA 任务；只有该任务能在既有门禁下实施流程改动 |
| **Effectiveness Verdict** | Improvement Task 部署后的跨周期效果判定；基于预先声明的 baseline、指标、规则版本和观察窗口，结果为 improved、neutral 或 regressed |
| **逻辑导出** | 通过数据库 SQL、COPY、dump、JDBC、客户端查询或官方导出工具按逻辑行/列读取数据并输出到中间格式或目标格式；区别于直接复制数据库物理数据文件或 WAL/binlog 原始日志。 |
| **报表中心 (Report Center)** | CDM 报表中心，需求 140；由 `report-web` 与 `collection-service` 两个应用 + Report DB 组成，中心化采集备份域数据并查询 |
| **report-web** | 报表中心 Web/API 服务：验证码登录、Token 鉴权、备份域管理、RPC 连通性测试、固定报表查询/同步导出 |
| **collection-service** | 报表中心采集调度服务：APScheduler 周期调度、50 线程池、固定 Topic Worker、JSONL 校验入库；唯一实例 |
| **cdm-data-cli** | CDM 侧受控 CLI，固定 Topic 子命令输出 JSONL，经既有 rpc 工具通道被调用 |
| **既有 rpc 工具（agent）** | 各 CDM 主机已部署的 RPC 通道，执行固定命令并缓冲返回退出码/stdout/stderr；报表中心只复用该通道 |
| **Report DB** | 报表中心独立数据库，一期唯一实现 PostgreSQL 17；维度/事实/聚合/控制表统一经 Repository/Adapter 访问 |
| **JSONL 采集** | CLI stdout 逐行 JSON 输出 → Collection Service 本地临时文件 → 校验 → 批量事务 Upsert |
| **Topic** | 固定采集主题：`resource`（资源快照）/`task`（任务增量）/`capacity`（容量样本） |

## 约定

- 技能命名：<作用>-<领域>（如 `register-evidence`、`write-conclusion`）
- 任务 ID 格式：T + 序列号（如 T0100）
- 阶段推进：通过 advance-phase 技能统一管理
- 证据登记：通过 register-evidence 技能统一管理
- 内容量比较：默认报告 UTF-8 bytes；不保留不能改变审查决策的冗余指标
- 历史任务：严格 schema 冻结后以 dry-run 清单清理不合规任务，不增加旧格式兼容逻辑

---
*由 domain-modeling 技能自动维护。更新请直接编辑此文件。*
