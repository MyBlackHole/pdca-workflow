# 改进：真实用户交互捕获机制 — PRD

## 来源

T0374 审查后用户指出"沟通过程的交互才是核心提升资料"。验证实锤三问题：
1. 真实用户输入（question 工具回答、会话元反馈）未持久化，会话结束即流失
2. AI 代填的 Q&A 污染 clarifications.jsonl 数据源（657 条中真实性不可区分）
3. 违反 HITL 红线：grilling agent 自问自答

## 方案（development 场景）

### D1. provenance 字段约定（数据层）
clarifications.jsonl 条目新增可选字段 `captured`：
- `"captured": true` — 用户原文实时落盘（question 工具回答/用户原话引用）
- `"captured": false` 或缺省 — AI 代填（hypothesis 语义）
schema 层面：该字段为 additional 可选字符串/布尔——需检查 task.schema.json 是否约束 clarifications（预期无，JSONL 非 schema 管控对象则纯约定）

### D2. 元反馈类型（语义层）
新增 source 枚举值 `user_meta_feedback`：记录用户对产出质量的元反馈（如"还可以更详细吗"），字段含 feedback 原文 + 触发场景 + 处置结果。

### D3. 技能与流程接线（执行层）
- skills/grilling/SKILL.md 三处强化：
  a) 规则 6 区分 captured 双态；AI 代填仅限 hypothesis 且禁止标记为用户实证；HITL 红线写入
  b) 新增防重问规则：每轮计算 frontier 前先读既往 `captured:true` 条目（借鉴 mattpocock/skills triage notes 复用模式，triage/SKILL.md:70）
  c) captured 条目作为下轮 frontier 计算输入（借鉴 teach learning-records 驱动 ZPD 的思想）
- flows/flow-check/SKILL.md Ch5 与 flow-plan P6：verdict 确认时若用户给出自由文本反馈（如"还可以更详细吗"类听者状态信号，语义对齐 wait-what），须以 user_meta_feedback 落盘
- scripts/append-confirmation.py 不改动脚本（范围控制），自由文本反馈以独立 JSONL 行追加

### D4. 本会话三次元反馈补录（即时价值）
将「还可以更详细吗」「还有细化空间吗」「沟通过程的交互才是核心提升资料吧」补录为 user_meta_feedback 首批样本到 T0370/T0375 的 clarifications。

## 测试接缝声明

### 声明的测试接缝
- seam: tests/test_interaction_capture.py -> scripts/pdca_core.py（clarifications 校验函数，如存在）
- 说明：若校验逻辑内嵌于 transition-phase.py 无独立函数，则以脚本级冒烟测试替代（运行 transition 拒绝路径断言 provenance 不被剥离）

## 验收标准

- [ ] AC-1: grilling SKILL 含 captured 双态规则与 HITL 红线条款
- [ ] AC-2: flow-plan P6 / flow-check Ch5 含用户自由文本反馈须落盘 user_meta_feedback 的要求
- [ ] AC-3: 冒烟测试证明带 captured 字段的 clarifications 条目通过全部现有门禁（transition 不拒绝新字段）
- [ ] AC-4: 本会话三次元反馈已按新格式补录且可在 JSONL 中检索
- [ ] AC-5: baseline 更新（若触发）且 audit 零 budget issue；evidence 登记齐备 convergence valid

## 范围外

- 不改造 question 工具本身（平台层）；捕获靠流程纪律+SKILL 规则
- 不回溯清洗历史 232 个任务的存量代填数据（量大且无法可靠判定真伪，标注机制仅对新条目生效）

## 与 mattpocock/skills 的关联（用户问询后补充）

- 借鉴：wayfinder resolution comment 落盘+索引（SKILL.md:125）、triage notes 防重问（:70,112）、loop-me NOTES.md、teach learning-records 驱动 ZPD、wait-what 元反馈触发词
- 超越点：grilling 原版不落盘 Q&A（grep 零命中）；两项目均无 provenance 数据层标记——captured 双态为本项目首创

## 备注

用户原始反馈三条是本任务的一手需求来源，实施时原文引用不得改写。
