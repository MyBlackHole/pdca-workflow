# 验证分层

<!-- pdca:current-validation:start -->
当前维护版本 **3.4.11**；本轮覆盖与未覆盖项见 [v3.4.11 验证说明](../migration/v3.4.11-VALIDATION.md)。
<!-- pdca:current-validation:end -->

[behavior-cases](behavior-cases.md)中的68个宿主行为正反例继续保留，需在目标宿主执行。本轮没有运行它们。结构检查、检查器合成控制、真实运行和效果 A/B 不能互相冒充。

## 当前维护入口

[入口与发布一致性](entry-maintenance/suite.md)覆盖本轮新增维护检查；代码、原输入、独立 policy 和逐项结果在配套验证包。它只验证有限静态关系，不判定 Agent 是否遵守自然语言。

[通用建模 suite](modeling-entry/suite.md)用于当前 Plan 本地绑定；[原材料回归](records-regression/README.md)、[记录修复](records-repair/suite.md)、[记录完整性](records-integrity/suite.md)保留各自范围。之前版本的独立执行器未包含在原上传中，本轮不声称恢复或复跑了它们。

[完整任务与前沿并发](agent-dispatch/suite.md)仍需区分离线事件重放、OS 进程试验和真实 Agent 执行。原 formal-records 按原协议快照解释，不用当前字节覆盖旧确认。

## 历史验证

[原迁移验证](../migration/VALIDATION.md) · [3.4.1](../migration/v3.4.1-VALIDATION.md) · [3.4.6](../migration/v3.4.6-VALIDATION.md) · [3.4.7](../migration/v3.4.7-VALIDATION.md)。历史通过数不继承为当前通过数。

## Agent行为与上下文效果

[行为对照入口](agent-behavior-eval/suite.md)定义独立请求、私有判据、真实trace和新旧版比较。配套导出/检查工具不调用模型，不冒充宿主或adapter；本轮只执行工具控制，真实Agent对照保持not_run。

## 3.4.10 派发／恢复加固

[有限回放与六组现场验收](agent-dispatch/recovery.md)区分synthetic工具控制和真实宿主执行。原59例不改写；新工具配在本版本独立验证附件，不能用回放pass填补NH01–NH06的NOT_RUN。

## 专业工作方法

[专业方法试点](professional-work/suite.md)独立比较问题定义、风险路径、证据与建议边界；12个公开请求与判据在外置验证包分离，真实行为NOT_RUN。不替代已有18个行为试点或真实宿主验收。
