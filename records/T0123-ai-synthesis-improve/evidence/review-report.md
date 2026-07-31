# T0123 综合审查报告：PDCA 流程 AI 友好度全貌

## 综合评分

| 维度 | T0120 分 | T0121 分 | T0122 分 | **综合** |
|------|---------|---------|---------|---------|
| 入口引导 | 4/5 | — | — | **4.0** |
| 流程可导航 | 4.25/5 | — | — | **4.25** |
| 门禁自检 | — | 3.6/5 | — | **3.6** |
| 工具对齐 | — | 3.5/5 | 3.6/5 | **3.55** |
| 上下文效率 | 3.5/5 | — | — | **3.5** |
| 容错与恢复 | — | 2.5/5 | — | **2.5** |
| 人机分工清晰度 | — | — | 3.3/5 | **3.3** |
| 引用链完整性 | — | — | 3.5/5 | **3.5** |
| **总分（35 满分）** | | | | **28.2 → 80.6%** |

## 核心发现

### 做得好的（AI 友好）
1. **AGENTS.md 路由设计** — 入口清晰，路径引用统一使用 `$PDCA_HOME` 变量
2. **flow-check 精简度** — 70 行闭环，与 grilling/verify-convergence/write-conclusion 解耦良好
3. **register-evidence 工具对齐** — 18 行的 bash 命令式技能，AI 零摩擦执行
4. **四阶段分离** — flows 各自独立成文件，按需加载减少 token 浪费
5. **三明治对齐机制** — flow-plan 2b 方向确认 + 6 方案终审的设计精巧

### 亟待改进的（AI 不友好）
1. **容错与恢复（2.5/5）** — 流程无回滚、无部分推进、subagent 失败无恢复路径
2. **disable-model-invocation（严重）** — 4 个技能文件使用非标准 frontmatter，不同 AI 模型行为不一致
3. **门禁为自然语言描述** — advance-phase 门禁条件无可执行校验脚本
4. **flow-do 路径编号重复** — 六路径各自从 1 开始编号，阅读混淆
5. **rejected/partial 缺少处理分支** — flow-check 要求进入 Act 但 Act 无对应处理逻辑
6. **README/AGENTS.md 功能重叠** — AI 首次进入可能混淆入口

## 优先改进方案

| 优先级 | 改进项 | 涉及文件 | 类型 | 预估工作量 |
|--------|--------|---------|------|-----------|
| **P0** | 统一 `disable-model-invocation` 为标准化标记 | triage, domain-modeling, wayfinder, handoff | 全局替换 | 小 |
| **P1** | 创建门禁校验脚本 | advance-phase，（新增）scripts/validate-gate.sh | 新增脚本 | 中 |
| **P1** | 补充 rejected/partial 处理分支 | flow-check + flow-act | 流程修改 | 中 |
| **P2** | AGENTS.md 增加 `$PDCA_HOME` fallback 说明和快速启动 | AGENTS.md | 入口补充 | 小 |
| **P2** | flow-do 路径改为 A-F 前缀编号 | flow-do/SKILL.md | 编号修改 | 小 |
| **P2** | 明确 AGENTS.md 和 README.md 的职责边界 | AGENTS.md + README.md | 职责梳理 | 小 |
| **P3** | SKILLS-INDEX.md 补全描述 | SKILLS-INDEX.md | 索引维护 | 小 |

## 改进执行

以下为实际文件修改。
