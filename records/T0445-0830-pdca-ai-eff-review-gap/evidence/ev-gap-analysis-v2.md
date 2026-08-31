# 差距识别与优先级评估：本地 PDCA 本体 vs mattpocock/skills v1.2.3

## 差距清单

### P0 — 安全/门禁类（影响会话内决策质量）

#### G1: Phase Boundary 五选项决策树
- **差距**：本地 `advance-phase.py` 只有阶段转换逻辑，缺少 session 内阶段切换的五选项决策树（Continue/Clear/Handoff/Subagent/Compact）
- **影响**：mid-phase 切换无显式决策树，易导致阶段内误决策
- **成本**：中 — 需在 flow-do 收尾阶段嵌入决策树逻辑
- **风险**：低 — 不改变现有阶段转换，仅增加 session 内决策辅助
- **验证方式**：在 flow-do 收尾时，session 处于 mid-phase 时应能触发五选项树；用例覆盖 Continue/Clear/Handoff/Subagent/Compact 五分支
- **关联本体节点**：`ontology/domain/ai-efficiency.md`（Phase Boundary 子节点）

#### G2: Grounding 依赖图写作法
- **差距**：长文档/课程分段生成无机械约束，缺少每 beat 声明 requires/grounds 的规范
- **影响**：长内容生成时上下文漂移，缺乏可达性约束
- **成本**：中 — 需在 writing-for-agents 体系中增加 grounding 声明规则
- **风险**：低 — 仅增加写作规范，不影响现有技能
- **验证方式**：writing-for-agents 技能中应包含 grounding 声明模板；长文档生成时可检查每节是否声明 requires/grounds
- **关联本体节点**：`ontology/domain/ai-efficiency.md`（Grounding 子节点）

### P1 — 能力补齐类（提升提示词鲁棒性）

#### G3: Wait-what 重述机制
- **差距**：提示词未命中时无标准化 re-pitch 流程，缺少 wait-wait 技能和 ASD-STE100 Simplified Technical English 要求
- **影响**：用户提示词偏离预期时，缺乏结构化重述机制
- **成本**：中 — 需新建 wait-wait 技能或在 writing-for-agents 中增加 re-pitch 规范
- **风险**：中 — 新技能需与 grilling 技能协调
- **验证方式**：存在专用 wait-wait 技能文件；re-pitch 流程符合 ASD-STE100 简化技术英语规范
- **关联本体节点**：`ontology/domain/ai-efficiency.md`（Wait-what 子节点）

#### G4: SKILL-MECHANICS 前言规范
- **差距**：SKILL.md frontmatter 缺少 `policy.allow_implicit_invocation` 字段，缺显式调用选择逻辑
- **影响**：技能调用方式不明确，可能导致 model-invoked 技能被错误触发
- **成本**：低 — 补充 frontmatter 字段和调用选择逻辑文档
- **风险**：低 — 仅增加元数据字段，不影响现有技能行为
- **验证方式**：所有 SKILL.md 包含 `policy.allow_implicit_invocation` 字段；存在 user-invoked/model-invoked 显式选择规则
- **关联本体节点**：`ontology/domain/ai-efficiency.md`（SKILL-MECHANICS 子节点）

### P2 — 细节完善类（锦上添花）

#### G5: Docs Page 四节模式
- **差距**：缺少标准化 docs page 四节模板（What it does / When to reach for it / Common questions / It's working if），缺少 writing-docs.md 模板
- **影响**：文档格式不统一，用户查找信息效率低
- **成本**：低 — 新增 writing-docs.md 模板和 docs page 规范
- **风险**：低 — 仅影响新文档格式，不影响现有文档
- **验证方式**：存在 writing-docs.md 模板；新技能文档遵循四节模式
- **关联本体节点**：`ontology/domain/ai-efficiency.md`（Docs Page 子节点）

#### G6: Repo 配置技能
- **差距**：缺少 setup-matt-pocock-skills 等效的 repo 配置技能（issue tracker/triage labels/domain docs 初始化）
- **影响**：新项目初始化时缺少标准化配置流程
- **成本**：中 — 需新建配置技能（pdca 非 Claude 插件，需适配）
- **风险**：中 — 涉及项目初始化流程变更
- **验证方式**：存在 repo 配置技能；新项目可通过该技能完成初始化
- **关联本体节点**：`ontology/domain/ai-efficiency.md`（Setup 子节点）

## 优先级排序依据

1. **安全/门禁类优先**：P0 差距直接影响 session 内决策质量和内容生成的结构化约束，属于核心机制缺失
2. **能力补齐类次之**：P1 差距提升提示词鲁棒性和技能调用明确性，属于重要但非阻塞的增强
3. **细节完善类最后**：P2 差距属于格式规范和初始化流程，不影响核心功能

## 覆盖度

- 已识别差距：6 项（≥3 项，满足 AC-2）
- P0：2 项
- P1：2 项
- P2：2 项
- 每个差距均标注影响、成本、风险、验证方式
