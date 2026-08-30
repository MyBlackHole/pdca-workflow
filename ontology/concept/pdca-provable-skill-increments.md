---
schema: pdca.asset/v1
id: ontology:concept/pdca-provable-skill-increments
type: concept
layer: Knowledge
status: active
summary: 可证明 Skill 增量方法谱系（T0265→T0272 八轮演进：从文档结构契约到体系健康度元验证）
relations:
  specializes:
  - ontology:concept/pdca-continuous-improvement
  relates_to:
  - ontology:concept/pdca-continuous-improvement
  - ontology:concept/self-optimization-loop
---

# 可证明 Skill 增量方法谱系（pdca-provable-skill-increments）

来源：T0265–T0272 系列。本知识沉淀从 mattpocock/skills 借鉴并本地化的可证明增量机制，供后续任务复用。

## 通用原则

- **可证明优先**：每个机制落地时必须配硬指标与测试断言（结构契约 + 行为状态机），指标优先于直觉。
- **文档增量 + 测试接缝**：skill 增量为 markdown 文档，测试用 grep/正则断言结构契约；行为机制用子进程状态机测试。
- **失败驱动实现**：先写失败测试（红），再实现（绿）。
- **推翻旧决策需记录**：推翻历史结论须在 PRD 与 conclusion 记录理由（如 0809 不落地 expand-contract 在 T0265 重新决策落地）。

## 机制谱系（要点）

1. **AGENT-BRIEF 结构化模板**（triage-work）：字段含 category/scenario_type/summary/current-desired behavior/key interfaces/AC 等；AC 可测、durability over precision（写概念级接口不写 `:line`/具体路径）；质量约束接入自动门禁。
2. **Wide-Refactor 保绿序列化**（to-tickets）：expand→分批迁移→contract→(integrate-and-verify)，每批 `blocked by` 上一批，逐批保持 CI 绿。
3. **Ticket Claim 并发防冲突**（wayfinding-work）：`check-ticket-claims.py` 状态机，仅 `open+unblocked+unclaimed` 票可选，重复 claim→`ALREADY_CLAIMED`、非认领者 resolve→`NOT_CLAIMANT`。
4. **out-of-scope 概念聚合知识库**：`knowledge/out-of-scope/<concept>.md` 一个概念一个文件，同概念追加 `## Prior requests`，`--implemented` 拒绝污染。
5. **merge-conflicts intent-based 解析**：找 primary source 理解双方意图、保留双方真实意图、绝不 `--abort`、`git diff --check` 无残留。
6. **DEEPENING 深化测试策略**：依赖分类（in-process/local-substitutable/remote-owned/true-external）→ 测试策略映射；seam 纪律 one adapter=假设接缝、two adapters=真实接缝；deletion test 判定模块是否挣存在。
7. **skill 结构契约检查器**（`check-skill-structure.py`）+ **Gotchas 段机制**：全量 39 skills 机器可判定契约 + 核心 9 skill gotchas 从历史失败点提取含记录级来源引用。
8. **采用度结构化**（`check-triage-brief.py`）：历史全量回溯 + 基线固化，把"是否被用"变可量化。
9. **决策兑现回读**（`recall-brief-decisions.py`）：决策→产出命中矩阵 + 兑现率，闭环"被采用"到"被兑现"。
10. **门禁合规扫描**（`audit-gate-compliance.py`）：全量扫描 receipts/verdict/convergence/final_confirmation 覆盖率 + 异常分类（legacy_no_gate/gate_incomplete/id_collision…）。
11. **transition 拒绝留痕**（rejected receipt）：4 拒绝点统一写 `transition-receipts/rejected-<ns>-<to>.json`，纳秒时间戳防覆盖。
12. **门禁合规存量修复**（`remediate-gate-compliance.py`）：`--dry-run` 预览、`--apply` 幂等；补 verdict 从 conclusion 提取有据、豁免如实不伪造；修复即再审计。
13. **体系健康度聚合诊断**（`self-audit.py`）：聚合 doctor/identity/seam/门禁四类信号 + 三级严重度 + 根因分类，输出可复现报告与修复候选排序。

## 方法论演进（强度递进）

| 轮次 | 证明对象 | 方法 | 结论形态 |
|------|---------|------|---------|
| T0265–T0267 | 机制存在/采用/兑现 | 测试/回读 | supported / partial-progressed |
| T0268–T0269 | 效果闭环 | 三层证据/回读矩阵 | partial → partial-progressed |
| T0270 | 门禁执行与拦截可审计 | 全量扫描+拒绝留痕+分类 | 门禁有效性确立 |
| T0271 | 存量缺陷清零且不伪造 | 有据回填+如实豁免+再审计 | 合规态修复 |
| T0272 | 体系整体健康度可量化 | 四类信号聚合+分级+根因 | 健康度总览+修复候选排序 |

## 审计方法论教训

- 前置误判：初版"采用率=0"是 grep 关键词误判（产出文件名 ≠ 机制名）；审计须按产出物实际形态判定。
- 三层证据不可互相替代：fixture 全绿与真实采用可同时一真一假；运行可用与效果闭环也可同时一真一假。
- 门禁有效性需双向证明：覆盖率（被执行）+ 拒收留痕（拦截被记录）缺一不可。
- 聚合优于分散：单次聚合报告比多个独立工具更能暴露体系性模式（legacy 占比 81% 一眼可见）。

## 来源

- `（原知识层）provable-skill-increments.md`
