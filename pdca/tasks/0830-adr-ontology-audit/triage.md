# T0419 Triage Brief：docs/adr/ 本体迁移可行性审计

## 分类
- scenario_type: documentation（审计 + 可选迁移）
- 来源：T0418 收尾时发现 `docs/adr/` 中 ADR-0032~0036 已可迁移进本体并删除；用户进一步质疑整个 `docs/adr/` 是否冗余。审计结论：仅 PDCA 元工作流相关 ADR 可能已被本体表示，子系统 ADR 无本体归属。

## docs/adr/ 清单（31 个，含两个 ADR-0013）
### A. PDCA 元工作流相关（可能可迁移）
| ADR | 主题 | 可能对应本体节点 | 是否已存在 |
|---|---|---|---|
| 0001 | PDCA 工作流架构决策记录机制 | pdca-architecture / 决策记录机制 | 部分 |
| 0002 | 严格任务合约与能力适配边界 | pdca-task（合约不变量） | 部分 |
| 0003 | Convergence 证据映射与 Do→Check 硬门禁 | pdca-evidence / pdca-verdict | 已有 |
| 0004 | Flow Issue 使用独立不可变事件文件 | （流程事件） | 待定 |
| 0017 | to-tickets DAG 与 ready-set | to-tickets 相关 | 待定 |
| 0024 | 统一 task/record identity 原子事务 | task-record-identity（T0418 已建） | 已有 |
| 0030 | 知识资产全部物理归并至 ontology/ | knowledge-ontology / ontology-creation-gate | 已有 |
| 0031 | 本体存储选型 md 优先 + 图升级路径 | ontology-creation-gate / pdca-ontology-ready | 已有 |

### B. 外部子系统相关（无本体归属，被技能引用）
rpc 协议/线程模型（0010-0014,0027,0028）、report（0015）、small-file（0019,0020）、LMDB（0021-0023）、backup（0808 任务）、handshake（0820/0823/0827 任务）等。这些决策属于其它项目，本仓库仅是归档位。

## 引用审计（已确认）
- `README.md`、`AGENTS.md`、`pdca/CONTEXT.md`、`flows/flow-plan/SKILL.md`、`skills/grilling`、`skills/domain-modeling-work/SKILL.md`（"扫描 docs/adr/ 找最大编号建 ADR"）、`skills/tdd`、`templates/to-spec/SPEC.md`、多个任务 PRD 都把 `docs/adr/` 当作 ADR 权威写入/查阅位置。
- 因此 `docs/adr/` 作为"决策记录机制"仍被流程依赖；子系统 ADR 删除会丢失无归属决策并破坏 ADR 写入流程。

## 查重
- 无重复任务（T0418 仅处理 0032~0036）。

## Claim 验证
- 事实：ADR-0032~0036 删除后 `ontology-validate` 仍通过、`docs/adr/` 引用仍存在 → 整体删除不可行，仅"被本体表示的 ADR"可迁移。

## 建议范围（待 Grill 确认）
- 仅审计并（可选）迁移 A 组 PDCA 元工作流 ADR；B 组子系统 ADR 保留并单独给出归属建议。
