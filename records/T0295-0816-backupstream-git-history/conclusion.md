---
schema: pdca.asset/v1
id: T0295-0816-backupstream-git-history
phase: check
source_ids: [git-history-learning-v3, convergence-map-v3]
---

## 上下文

T0295（research 场景）目标是学习 `/home/black/Downloads/backupstream` 仓库 main 分支 v65→v101 共 36 个提交的修改内容、修改作用与架构变更，以 git diff 为主、ROUND*_REVIEW 文档为辅。产出放 PDCA 记录目录，全部 36 个提交逐一分析。

分析方法：按提交哈希分组，先 `git show <hash> --stat` 抓文件级变更，再对核心模块 `git show <hash> -- <file>` 读函数级 diff，结合 docs/ROUND*_REVIEW.md 文档交叉验证。v91 无独立 git 提交（其设计并入 v92），已显式说明。

## 假设与结果

| 假设 | 结果 | 结论 |
|------|------|------|
| 36 个提交均可独立分析 | 36 个提交逐一覆盖，v91 设计并入 v92 已说明 | 满足 AC-1/AC-5 |
| 每提交可归纳「修改内容/修改作用/架构变更」三要素 | 36 节均含三要素 | 满足 AC-2 |
| 存在可归纳的演进主线 | 提炼出 4 条主线（client 目录队列/dirty journal；Agent 传输 Reactor/FSM 化；Observability 与离线诊断；贯穿的批量/正确性优化） | 满足 AC-3 |
| 存在架构分水岭版本 | 标注 v70/v74/v76/v77/v80/v83/v84/v85/v87/v88/v89/v90/v95/v98/v101 等分水岭并附演进全景时间线 | 满足 AC-4 |
| ROUND 文档对变更的描述与 git 一致 | **不一致**：文档声称"删除"的模块（agent_tree_legacy/agent_plain_control/agent_session_pool）在 git 中无删除记录，物理文件仍保留为死代码，仅移除编译接线 | 已修正并补充「文档-代码漂移观察」 |

## 分析

四条演进主线：

1. **客户端目录队列 / dirty journal（v65-v74）**：从全量目录队列演进到 inotify 驱动的 leaf-sparse dirty journal，成本从 O(目录条目数) 降到 O(变更叶子)。
2. **Agent 传输 Reactor/FSM 化（v75-v88）**：plain transport 从阻塞多线程全面演进到 Reactor/event domain 持 socket + 有界 Work Pool 做工作 + 小型 launch pool 只做进程 setup；每类操作一套 transport-neutral FSM。
3. **Observability 与离线诊断（v89-v101）**：server-local trace → JSONL/Prometheus 双平面导出 → backup-observe 离线消费与 diagnose → Reactor 相位/回调守恒测量。
4. **贯穿的批量/正确性优化**：固定批量上限、schema 递增不迁移、可重放正确性不变量。

关键分水岭：v70（backup-dirtyd inotify journal）、v76/v77（事件泵/共享事件域）、v80（非阻塞 plain ingress）、v88（无 general session pool）、v90（观测双平面导出）、v101（512 相位历史 + 守恒分解）。

修正发现（grill 用户判定"需修正"后完成）：核对 git diff 发现 ROUND 文档与 git 物理状态存在漂移——v86/v87/v88 声称删除的模块实际未在 git 删除，仅从编译/接线移除成为死代码。已修正 v86/v87/v88 三节、新增「演进全景图」「文档-代码漂移观察」章节、补充 v70/v86/v87/v88/v101 函数级源码证据、学习结论新增第 7 条 dead-code 化原则，报告重登记为 v3（48363 字节）。

## 适用边界

- 结论限于 v65-v101 当前版本状态；未来版本需重新核验。
- ROUND 文档对"删除"的表述是逻辑删除（从编译/运行接线移除），与 git 物理文件存在性不一致，阅读历史需以编译产物为准。
- 个别模块级行数（如 backup_agent.cpp -865）基于 diff 统计，精确值以 git 为准。
- v91 无独立提交，其内容并入了 v92 提交。

## AC 判定

- **AC-1** ✓：36 个提交全部逐一覆盖（git-history-learning-v3 36 节版本标题）。
- **AC-2** ✓：36 节均含「修改内容/修改作用/架构变更」三要素。
- **AC-3** ✓：4 条演进主线 + 演进全景 ASCII 时间线。
- **AC-4** ✓：架构分水岭标注 + 学习结论 + 文档-代码漂移观察。
- **AC-5** ✓：v91 无独立提交（设计并入 v92）已显式说明。
- **AC-6** ✓：以 git diff（git show hash --stat / -- <file>）为事实来源，ROUND 文档交叉验证并发现漂移。

## 下一轮建议

- 若需深入 v87/v88/v101 实现细节，可对 backup_agent.cpp 演进与 Reactor 相位会计做专题分析。
- 可将「transport-neutral FSM」「共享事件域 shard」「观测驱动架构演进」提炼为跨项目架构模式沉淀到 knowledge/。
- 后续版本学习可复用本报告的提交-哈希映射与分析方法。

## 结论

verdict = **confirmed**