# T0120 审查报告：入口和流程导航的 AI 友好度

## 审查范围

- AGENTS.md（46 行）
- flows/flow-plan/SKILL.md（132 行）
- flows/flow-do/SKILL.md（180 行）
- flows/flow-check/SKILL.md（70 行）
- flows/flow-act/SKILL.md（80 行）

## 审查方法

以 AI Agent 首次进入仓库执行一个 PDCA 任务的全过程为线索，逐文件模拟执行，评估每个环节的阻力点。

## 逐项评分（1-5）

### 1. 入口引导 — 总分：4/5

| 文件 | 评分 | 分析 |
|------|------|------|
| AGENTS.md | 4 | 第一句明确定义仓库用途，五阶段门禁列表清晰。**缺点**：缺少"首次进入的 AI 代理第一步做什么"的快速启动指南；`$PDCA_HOME` 变量未设环境变量时无 fallback 说明 |

### 2. 流程可导航 — 总分：4.25/5

| 文件 | 评分 | 分析 |
|------|------|------|
| flow-plan/SKILL.md | 4 | 步骤编号 0-7 清晰；三明治对齐机制（2b+6）设计精良。**缺点**：步骤 0 末尾"跳到步骤 1"没有返回路径；步骤 2a 中 `disable-model-invocation: true` 是特殊标记，不同 AI 理解可能不一致 |
| flow-do/SKILL.md | 4 | 六路径分类清晰，统一出口。**缺点**：路径编号重复（每个路径都从 1 开始），阅读时易混淆；路径 A 步骤 4 双轴审查描述过细 |
| flow-check/SKILL.md | 5 | 最简洁的流程文件，六步闭环，场景感知追问设计精巧 |
| flow-act/SKILL.md | 4 | 八步结构清晰，知识沉淀逻辑完整。**缺点**：步骤 1 Grill 在没有可复用知识时是否跳过不明确；步骤 7 git 操作在外部项目模式下不适用 |

### 3. 上下文效率 — 总分：3.5/5

| 文件 | 评分 | 分析 |
|------|------|------|
| AGENTS.md | 3 | 与 flow-plan 有部分功能重叠描述；未聚合关键路径引用 |
| flow-plan/SKILL.md | 4 | 132 行合理；引用路径明确。`disable-model-invocation` 标记增加理解成本 |
| flow-do/SKILL.md | 3 | 180 行六路径有大量重复模板（登记证据/进入 Check 重复 6 次）；可提取公共步骤减少重复 |
| flow-check/SKILL.md | 4 | 70 行精简，与 grilling/verify-convergence/write-conclusion 解耦良好 |
| flow-act/SKILL.md | 4 | 80 行精简 |

## 不友好之处的定位与严重程度

| # | 位置 | 问题 | 影响 | 严重度 |
|---|------|------|------|--------|
| F01 | AGENTS.md:7 | `$PDCA_HOME` 无环境变量 fallback 说明 | AI 可能不知道用当前仓库路径 | 中 |
| F02 | AGENTS.md:1-46 | 缺少"AI 首次进入快速启动"段落 | 新 AI 代理需自行摸索入口 | 低 |
| F03 | flow-plan/SKILL.md:17 | `disable-model-invocation: true` 非标准语法 | 不同 AI 模型理解不一致 | 中 |
| F04 | flow-plan/SKILL.md:25 | "跳到步骤 1"无返回路径 | 步骤 0 需明确链接到步骤 1 | 低 |
| F05 | flow-do/SKILL.md:23-175 | 六路径步编号重复 | 跨路径引用混淆 | 中 |
| F06 | flow-do/SKILL.md:150-175 | Path F 缺少审查非代码产物的说明 | review 场景路径不完整 | 中 |
| F07 | flow-check/SKILL.md:61 | rejected/partial 必须进入 Act 但无 Act 处理分支说明 | Check 失败后路径不明确 | 高 |
| F08 | flow-check/SKILL.md:62 | "若有异议→回到步骤 1"跳过 Grill | 异议可能来自 Grill 不足却跳过 Grill | 低 |
| F09 | flow-act/SKILL.md:17 | 步骤 1 Grill 无跳过条件 | 无知识沉淀需求时仍需走 Grill | 低 |
| F10 | flow-act/SKILL.md:63 | git 命令对外部项目模式不适用 | 外部项目中执行失败 | 中 |

## 改进建议

### 高优先级
1. **F07**：在 flow-check 中增加 rejected/partial 进入 Act 后的处理分支说明，或在 flow-check → flow-act 之间增加明确的"降级处理"子流程

### 中优先级
2. **F01**：在 AGENTS.md 开头增加 `$PDCA_HOME` 的 fallback 逻辑说明
3. **F05**：flow-do 六路径改用 A/B/C/D/E/F 前缀编号避免混淆
4. **F06**：Path F 增加对非代码审查场景（如流程审查、配置审查）的适配说明
5. **F10**：flow-act 步骤 7 增加对外部项目的条件判断

### 低优先级
6. **F02**：AGENTS.md 末尾增加"快速启动"段落
7. **F03**：将 `disable-model-invocation` 替换为明确的"手动加载"说明
8. **F04**：步骤 0 末尾改为链接到步骤 1
9. **F08/F09**：增加跳过条件
