# AGENT-BRIEF 真实效果审计（T0268）

按 `knowledge/pdca-flow/real-usage-effectiveness-audit.md` 协议执行。审计对象：
T0265 在 triage-work 落地的 AGENT-BRIEF 结构化模板（产出 triager-brief.md）。
审计数据截至 2026-08-15。

## 三层证据分离

| 层 | 证据 | 状态 |
|---|---|---|
| 实现正确性 | T0265 `tests/test_skills_increments.py` 含 AGENT-BRIEF 契约测试（grep 命中 2 处）；T0268 `tests/test_triage_brief.py` 6 测试全绿（契约解析/退出码/回溯基线） | **成立** |
| 运行数据可用性 | 历史全量回溯 93 个 triager-brief 可提取字段：核心三字段（category/evidence/dedup）全含 58.1%（54/93）；category 76.3%、evidence 80.6%、dedup 76.3%、scenario 79.6%、priority 55.9%、actionable 66.7%。T0265 落地后的 round62/66/67 核心字段 100% 全含 | **成立**（字段不变量可重建） |
| 效果闭环 | brief 驱动实施转化有证据：round67 brief 的推荐方向（batch ledger/block 方案）进入 design.md（grep 命中）；round62 brief 主题（checkpoint/resume）进入 do-evidence。但**无系统性 decision→candidate→Improvement Task→effectiveness verdict** 反馈链 | **不成立**（缺失） |

三层任一不成立即不能判定 supported。效果闭环缺失 → **partial**（同 T0260 对 flow-issues 的判定口径）。

## 四轴评分

### 1. 覆盖（是否捕获独立真实 issue；同时报告漏报）

**良好**。round62 brief 捕获"LMDB-default 二进制在标准集成套件中失败（`file is not a database`）"及"TREE 中断后无持久逐批 checkpoint 契约"两个独立问题，均引用代码证据（`src/metadata_store.cpp`）与单样本基准。round66 捕获"`TreeCheckpoint::confirmed` 为 unordered_map 随 namespace 线性内存增长"问题，引用 `src/backupctl.cpp` 具体行。
**漏报**：无独立参照集可系统确认漏报（协议要求"不能用 occurrence 自己证明 occurrence"）；如实标注覆盖评分仅基于既有 brief 的捕获质量，不外推全量召回率。

### 2. 信噪（区分原子失败/重复 burst/系统问题）

**良好**。round62 brief 明确将"20,000 条单样本 benchmark（0.0667s LMDB vs 0.0741s SQLite）"标注为**非生产证据**，不当作结论；round66 brief 区分"T0251 覆盖日志/事件/100k 语义"与"不证明 checkpoint 内存边界"——查重段精确划定边界，避免重复归因。

### 3. 可行动性（能否定位任务/原因/影响/可验证指标）

**良好**。round67 brief 给出推荐方向（单文件 `.partial`+原子 rename；海量目录改 batch ledger）+ 信息缺口（tmpfs/SSD/旋转盘分别测量、重复发送窗口、三类故障注入）——可验证指标明确。round62 brief 有具体基准与测试命令。

### 4. 转化及时性（事实是否进入投影/治理/candidate/实施）

**中等**。brief→design→evidence 转化真实存在（round67 brief 推荐方向进入 design.md；round62 主题进入 do-evidence），说明事实及时进入实施。但 brief 驱动的**效果验证反馈缺失**：任务完成后无"brief 预测是否正确/是否避免问题"的回读机制，effectiveness verdict 从未产出。

## Effectiveness Verdict

### verdict: **partial**

- **supported 部分**：实现正确（契约测试 + 6 测试全绿）；运行数据可用（93 brief 可重建，T0265 后核心字段 100%）；真实采用且转化及时（round62/66/67 brief→design→evidence 有据）。**AGENT-BRIEF 有真实提升作用（结构化 triage 被采用并驱动任务实施）——确认成立**。
- **不成立部分**：效果闭环缺失——无 decision→candidate→Improvement Task→effectiveness verdict 反馈链，无法确证"brief 是否持续提升任务成功率/减少返工"。
- **判定依据**：T0260 三层口径（三层全满足才 supported）。运行数据可用与效果闭环同时一真一假是协议明确允许的形态。

## 提升作用结论（回应"前提确定有提升作用"）

**AGENT-BRIEF 的采用与转化有真实证据，其提升作用在"结构化采用"维度成立（supported）；在"效果验证"维度未闭环（partial）。** 四轮增量（T0265-T0267）均属"实现正确 + 运行可用"层，缺第三层——这正是本审计与前一轮采用率=0 误判的修正：机制有采用（AGENT-BRIEF 真实被用），缺的是效果回读。

## 行动建议（闭环路径）

1. 为 round62-67 建 brief→实施→效果回读（brief 预测 vs 实际结论对比），逐步填充闭环。
2. T0263 观察窗（08-29 或 20 个新任务）期满后，复用本审计口径对 identity 机制出 verdict。
3. 采用度基线（93 brief / 58.1% 核心字段）已固化到 `tests/test_triage_brief.py`，后续轮次可对比演进。

## 适用边界

- 审计基于历史记录（93 brief），不包含实时运行遥测（缺失时写 unknown，未伪造）。
- 覆盖评分不外推全量召回率（无独立参照集）。
- 本审计产出判定而非机制改动；AGENT-BRIEF 文档未变更。
