# 八维度 AI 适应性评分

## 评分总表

| # | 维度 | 评分 | 评级 |
|---|------|------|------|
| 1 | 入口引导 | 4.0/5 | 🟢 良好 |
| 2 | 流程可导航 | 4.0/5 | 🟢 良好 |
| 3 | 门禁自检 | 4.5/5 | 🟢 优秀 |
| 4 | 工具对齐 | 4.0/5 | 🟢 良好 |
| 5 | 上下文效率 | 4.0/5 | 🟢 良好 |
| 6 | 容错与恢复 | 3.5/5 | 🟡 中等 |
| 7 | 人机分工清晰度 | 4.0/5 | 🟢 良好 |
| 8 | AI 适用度 | 3.5/5 | 🟡 中等 |
| | **综合** | **3.9/5** | 🟢 总体良好 |

## 各维度详情

### 1. 入口引导 — 4.0/5
**优势**：
- 所有 flow 和 skill 均有 YAML frontmatter 含 name + description
- flow-do 有路径索引表，一眼可定位目标路径
- SKILLS-INDEX.md 提供全局索引

**问题**：
- 部分 skill description 行数过多，降低扫描效率（如 context-retrieval 有 16 行 frontmatter）
- code-review 的 description 为空（只有子标题"双轴代码审查"，未描述触发场景）

### 2. 流程可导航 — 4.0/5
**优势**：
- 所有 flow 使用统一步骤编号（P0-P7/Ch1-Ch6/Ac0-Ac8/A-F+Z1-Z3）
- 步骤总览表位于每个 flow 文件顶部
- flow-do 通用收尾 Z1-Z3 消除了 12 次重复引用

**问题**：
- flow-do 仍然有 13 次 skill 引用，每引用一次需额外上下文加载
- 跨文件导航依赖 AI 的文件读取能力

### 3. 门禁自检 — 4.5/5
**优势**：
- advance-phase 明确定义了 4 个转换门禁及校验条件
- validate-gate.sh 提供可编程校验
- rollback-phase.sh 支持阶段回滚
- 条件均为可检查的（文件存在/JSON字段/内容匹配）

**问题**：
- advance-phase 行数从 25→58 行（超出 SKILLS-INDEX 声明），但功能上合理

### 4. 工具对齐 — 4.0/5
**优势**：
- 大部分步骤映射到 AI 可用工具（read/write/bash/git）
- skill() 加载通过 `$PDCA_HOME` 路径引用
- subagent 派发使用标准的 task() 工具调用

**问题**：
- "并行子代理"假设 AI 可同时运行多个 task()，平台可能有限制
- context-retrieval 依赖 `pdca context` CLI 命令——该命令可能不存在

### 5. 上下文效率 — 4.0/5
**优势**：
- 总内容量 501 + 1,402 = 1,903 行，典型场景仅需加载 1 flow + 2-4 skills
- T0130 压缩效果保持良好，4 个压缩文件无回弹
- 最小 skill（grill）仅 6 行 262 字节

**问题**：
- **SKILLS-INDEX.md 行数信息过期** — 多个技能行数与实际不符
- advance-phase(2,435B) 和 writing-great-skills(2,409B) 字节量较高
- 37 个 skill 中 11 个超过 2,000 字节，整体仍有精简空间

### 6. 容错与恢复 — 3.5/5
**优势**：
- flow-do 有子代理容错机制（Blocking/Non-blocking）
- advance-phase 有 task.json.bak 备份机制
- rollback-phase.sh 可用
- flow-act 有 rejected/partial 分支处理

**问题**：
- to-tickets 的 Dispatch 子代理派发无错误处理，与 flow-do 容错机制脱节
- flow-plan 的 subagent 派发未引用 flow-do 的通用容错
- 无上下文窗口溢出恢复机制

### 7. 人机分工清晰度 — 4.0/5
**优势**：
- `invocation: manual` 明确标记 user-invoked 技能
- flow-plan P6 标记为"唯一门禁"
- "子代理对齐说明"明确人类决策留在主 session

**问题**：
- 部分 skill 缺乏显式的自动触发条件（`Use when...` 不完整）
- triage（user-invoked）却包含 AI 执行步骤描述，边界模糊

### 8. AI 适用度 — 3.5/5
**适用度评估**：

| 等级 | 数量 | 代表技能 |
|------|------|---------|
| 🟢 高适用 | 18 | advance-phase, register-evidence, write-conclusion, commit-format, code-comments, research, web-research, grill 等 |
| 🟡 中适用 | 14 | code-review, tdd, diagnosing-bugs, domain-modeling, triage, to-tickets, prototype 等 |
| 🔴 低适用 | 5 | context-retrieval（依赖CLI）, wayfinder（抽象度过高）, resolving-merge-conflicts（复杂冲突）等 |

**关键问题**：
- context-retrieval 依赖 `pdca context` CLI，无回退方案
- to-tickets 的 task() 派发无超时/重试逻辑
- improve-codebase-architecture 的分析输出好但修复建议需要人工验证
