# T0238 Triage Brief — 机制修正

## 来源
T0234（FastAPI 应用验证 PDCA 流程）实测发现的两个机制问题，用户选定"机制修正"方向。

## 问题 1：词汇契约适用范围边界
- **现象**：check-design-vocab 对 T0234 的 PRD（需求文本）误报违规
  （component/service/API/boundary），但 PRD 是需求文档不是接口设计文档。
- **根因**：check-design-vocab 是 design-it-twice 词汇契约校验器（docstring 明确
  "接口设计文档"），但对任意 stdin 文本都检查，无文档类型限定。
- **修复方向**：场景限定——仅校验接口设计文档（design.md），需求/PRD/其他
  文档不检查；或提供显式场景参数。

## 问题 2：states 时间戳手工写入与 transition 冲突
- **现象**：T0234 手工写的 states.plan（带微秒 `13:04:44.126299`）晚于
  transition 自动写的 states.do（无微秒 `13:04:44`），触发 STATE_TIME_ORDER
  （timestamps must be nondecreasing）。
- **根因**：datetime.fromisoformat 比较时 `13:04:44 < 13:04:44.126299`，
  do 早于 plan → 顺序颠倒。本质是**手工写时间戳与 transition 自动写冲突**，
  违反 flow-plan "禁止手写时间戳" 约定。
- **修复方向**：自动化 states 时间戳写入（transition 阶段统一生成），或
  校验层识别此冲突给出明确 guidance；补充 STATE_TIME_ORDER 测试覆盖。

## 修复目标
1. check-design-vocab 场景限定（仅 design 文档检查）
2. states 时间戳写入自动化 + 明确 guidance
3. 新增 STATE_TIME_ORDER 与场景限定测试

## 后续
P1 澄清 → P2 Grill → P3 PRD → P3.5 seam → P4 → P5 → P6 → Do
