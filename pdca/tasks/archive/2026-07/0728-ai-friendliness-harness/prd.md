# 建立六场景确定性 AI 友好度评测

## 问题陈述

旧 AI 友好度审查依赖单模型自评，没有固定输入、可执行 pass/fail、独立重复运行或失败分类，无法作为优化前后的科学基线。

## 解决方案

- 为 development、bugfix、research、documentation、design、review 建立正常路径和故障路径夹具。
- 记录 fixture ID、输入 digest、预期、实际、错误码和运行环境。
- 只保留当前可执行的确定性 harness；没有独立 runner 的实验协议不纳入实现。

## 验收标准

- [ ] 六类 scenario 均至少有一个正常夹具和一个故障夹具。
- [ ] 相同版本重复运行结果字节一致或有明确排除字段。
- [ ] 故障覆盖拒绝确认、缺 PRD、断链、非法场景、未来状态和归档矛盾。
- [ ] 输出可作为 skill 精简前后的同一配对基线。

## 范围外

- 宣称有限夹具覆盖所有真实任务。
- 没有当前执行路径的 Agent runner、trial schema 或跨模型排行榜。
