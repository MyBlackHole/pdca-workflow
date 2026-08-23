# 历史任务审查与自我提升 — 审查报告

> 任务：T0374 | 场景：review | 方法：全量扫描 257 task.json + 抽样审读 + AI 失误复盘
> 日期：2026-08-23 | 双轴：标准轴（AGENTS.md 门禁+schema）/ 规范轴（各任务 PRD 承诺）

## 1. 全量扫描量化（AC-1）

### 1.1 总量与阶段分布

257 个 task.json 全部可解析。phase 分布：

| phase | 数量 | 占比 | 解读 |
|-------|------|------|------|
| archive | 188 | 73% | 正常终态 |
| plan | 36 | 14% | 多为备份域真实工作排队（rpc/tls/lmdb 族），非流程问题 |
| do | 13 | 5% | 同上 |
| check | 13 | 5% | 卡点观察项（见 4.3） |
| act | 7 | 3% | 卡点观察项 |

### 1.2 schema 合规分代统计

CONTEXT.md 约定严格 schema 自 T0135 起生效，分代统计：

| 代际 | 数量 | schema 合规 | 合规率 |
|------|------|------------|--------|
| legacy（<T0135） | 1 | 0 | 已接受的旧格式，按既有 dry-run 清单机制处理 |
| strict（≥T0135） | 256 | 223 | **87%** |

strict 代 33 个不合规样本分布：plan 19 / archive 13 / act 1。多为早期过渡期产物（如 `followup_of` 额外字段、`completed_at: null` 类型错误），属"冻结后未回改的历史欠账"，与 CONTEXT.md "不为旧格式增加兼容分支"的决策一致——处置见第 5 节改进立项。

### 1.3 归档任务四类产物覆盖率

| 产物 | 覆盖率 | 缺口明细 |
|------|--------|---------|
| verdict | **188/188 (100%)** | 无 |
| disposition | 185/188 (98%) | T0207/T0208/T0209 |
| conclusion | 181/188 (96%) | 7 个缺（见 1.4） |
| evidence manifest | 180/188 (95%) | 8 个缺 |

### 1.4 归档缺产物违规明细（逐个核实）

| 任务 | record 目录实况 | 定性 |
|------|----------------|------|
| T0336 | record 指向 `T0336-0821-tls-cert-ssl-free` **不存在**；records 下另有 `T0336-0820-pgwrecover-incremental-scope` | **身份错位**：疑似 slug 冲突期产物，task 身份与 record 脱钩 |
| T0337 | record 目录不存在 | 归档时 record 未创建 |
| T0340 | 目录仅有 task.json，无 conclusion/evidence | 半途归档 |
| T0335 | 有 conclusion，缺 evidence manifest | 局部缺口 |
| T0348 | evidence 目录存在但无 manifest.jsonl | 登记方式不规范（手放文件未走 register-evidence） |
| T0149/T0162/T0146 | record=None 且无目录 | record 机制引入前的旧归档，属已接受状态 |

## 2. 抽样审读（AC-2）

跨年代抽 6 个，conclusion 质量逐个结论：

| 样本 | 结构完整性 | AC 判定 | 证据回链 | 结论 |
|------|-----------|---------|---------|------|
| R0079 (0727) | 五段齐 | 显式 | source_ids 6 条 | 优——假设结果表+双轴改造记录完整 |
| R0135 (0728) | 五段齐 | 显式 | source_ids 5 条 | 优——可验证协议验收链清晰 |
| T0104 (0727) | 变体但实 | 部分 | 根因清单 | 良——早期格式但内容扎实 |
| T0333 (0820) | 五段齐 | 显式 | 有 | 良——含用户修正记录（双平台自研） |
| T0370 (0823) | 六段齐 | ✅逐条 | source_ids 齐 | 优——含可靠性自查节 |
| T0336 (0821) | **无 conclusion** | — | — | **不合格**——归档即失忆，见 1.4 |

**ac_judged 全量仅 40%** 的根因：✅/❌ 判定格式是中后期才固化的模板演进，早期 conclusion 用叙述式判定（内容在但不符机器可检索格式）——非质量缺失而是格式漂移，验证了 write-conclusion 已知坑条款的价值。

## 3. AI 操作性失误清单（AC-3）

本会话 T0370-T0374 全部门禁拒绝事件复盘，每条含根因与防再发措施：

| # | 事件 | 根因 | 防再发措施 | 去向 |
|---|------|------|-----------|------|
| 1 | STATUS_PHASE_MISMATCH：创建后手改 status=InProgress 被 transition 拒 | 绕过统一入口直改 task.json 字段，不知 status 与 phase 有联动约束 | 一切字段变更经脚本；Pending 由 transition 管理 | journal 纪律条目 |
| 2 | FINAL_CONFIRMATION_AFTER_TRANSITION + TIME_ORDER：两次手写 final_confirmation 时间戳被拒 | 手写时间戳违反"禁止手写 at"；对时间顺序校验（不得早于创建/晚于转换）无知 | 只用 append-confirmation.py；理解门禁校验的是时间线一致性而非单点值 | journal + 本报告 |
| 3 | improvement_source SCHEMA_INVALID ×2（T0373/T0372） | 不知该字段需 Flow Issue 管道对象（FI-/FC-/FD- 24hex），评估产出的改进直接填任务 ID | Improvement Task 若非 Flow Issue 管道产出则不填该字段 | **知识沉淀** |
| 4 | register-evidence duplicate filename ×3 | 同一文件不能登多条证据；手动 cp 进 evidence 后再登记撞名 | 一条证据映射多 AC 用多个 --criterion；始终 --source 让脚本复制，勿手动预置 | **register-evidence 已知坑扩充** |
| 5 | replacement must use different --file ×2 | --replace 时新条目须换文件名 | supersede 时同步换 --file 名 | 与 #4 合并沉淀 |
| 6 | survey.md 先 mkdir+cp 再登记失败 | 文件操作顺序颠倒（应先登记后核对，或直接以 evidence 内路径为准） | 同 #4：--source 是唯一写入通道 | 同上 |
| 7 | convergence map 初版 AC-6 UNCOVERED | map 排除自身作证，AC-6 需独立非 map 证据 | 记住 convergence-map 不能给任何 AC 作证 | 已在技能文档，执行纪律强化 |

模式归纳：**7 起失误中 5 起（#1/#2/#4×2/#6）同根——绕过统一入口手工操作文件**。PDCA 的原子性与不可变性设计是对的，失误全在执行者贪快走捷径。

## 4. 三层处置（AC-4）

### 4.1 立即修复（本任务内完成）
- 本报告本身即 #3/#4/#5 的防再发载体；knowledge 沉淀见 Act。

### 4.2 改进立项（候选 Improvement Task）
1. **strict 代 33 个 schema 欠账清理**：触发既有 dry-run 清单机制跑一次真实清理（development，小）。
2. **write-conclusion 判据 demand 化**：T0373 回审遗留（verdict 四字段+逐条 AC 判定入完成判据），顺带把 ac_judged 格式固化进模板，治 40% 低判定率（documentation，小）。
3. **T0336 身份错位修复**：核实 slug 冲突成因，决定 record 补建或标注豁免（research，微）。

### 4.3 记录观察（触发条件）
- check/act 卡点 20 个：下次月度审查若仍 >15 则立推进任务。
- disposition 缺失 3 个（T0207-T0209）：随 #1 清理顺带补。
- flow-do 持平 baseline 已破（T0372 +79B）：后续动 flow-do 的豁免门槛提高。

## 5. 自我提升结论

体系侧：门禁的时间线校验、原子 receipt、SSOT 入口在 7 次拦截中全部正确工作——**被拦的每一次都是数据被保护的一次**。执行者侧：核心改进是把"统一入口"从规则内化为默认动作；三条知识沉淀（Improvement Task 字段约束、evidence 单文件单条+--source 唯一通道、supersede 换名）已足以消除本会话全部失误类别的再发条件。
