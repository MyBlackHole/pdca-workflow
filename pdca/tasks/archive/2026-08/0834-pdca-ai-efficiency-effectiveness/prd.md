# 验证 PDCA 本体改进是否真实提升 AI 使用效率

## 目标

按 GQM 评测框架验证 T0435-T0437 的本体改进是否真实提升了 AI 使用效率。

## GQM 评测框架

### Goal
改善 AI 工作流的确定性、导航准确性和上下文效率。

### Question
1. Q1：新增概念节点是否被流程正确消费？
2. Q2：导航成功率是否提升？
3. Q3：上下文成本是否降低？
4. Q4：故障恢复是否改善？

### Metric
- Q1：ontology_fragment 消费率 = 消费了 ontology_fragment 的任务数 / 总任务数
- Q2：路由成功率 = 正确路由的任务数 / 总路由任务数
- Q3：context load = AGENTS.md + skill descriptions 的 UTF-8 bytes 总量
- Q4：门禁失败率 = 门禁拒绝数 / 总尝试数

### 验证方法
- 机器 pass/fail：确定性夹具
- 前后配对：T0435-T0437 前后的指标对比
- 失败路径使用固定夹具，失败必须得到预期错误码

## 实施计划

### AC-1：GQM 评测框架
- 在 `ontology/concept/pdca-ai-friendliness-review-methodology.md` 中补充 GQM 评测章节
- 定义 Goal → Question → Metric → Method

### AC-2：机器 pass/fail 验证夹具
- 新建 `ontology:concept/deterministic-fixture` 概念节点
- 定义确定性夹具的三要素：输入、预期输出、pass/fail 信号
- 更新 `ontology/concept/pdca-ai-friendliness-review-methodology.md`

### AC-3：前后配对指标收集
- 收集 T0435-T0437 前后的指标数据
- 记录 baseline 和观察窗口
- 输出 improvement/neutral/regressed 判定

### AC-4：effectiveness verdict
- 判定每个 Question 的效果：improved / neutral / regressed
- 仅 improved 可形成 verified decision
- 非 improved 需提出改进建议

### AC-5：登记证据
- 收敛映射 valid:true