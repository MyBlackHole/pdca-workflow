# T0160 设计：AI 友好评测的可执行 oracle

## 组件边界

| 组件 | 职责 | 公开 seam |
| --- | --- | --- |
| Route Contract | 声明 scenario、route ID、文档锚点和步骤的唯一映射 | schema + JSON 合约 |
| Route Resolver | 读取合约并以稳定 JSON 返回路由或错误 | CLI `--scenario` |
| Flow Documentation Check | 验证人类文档锚点与合约一致，不参与路由决定 | 审计 CLI / fixture |
| Lifecycle Fixture | 构造最小有效严格仓库并调用公共 phase 转换 | fixture JSON |
| Content Budget | 对当前审计资产和版本化 baseline 执行差分检查 | 内容审计 `--check-budget` |

## 路由模型

每条 route 由 `{scenario, route_id, anchor, steps}` 组成。合约严格限制 scenario 为任务 schema 的六个枚举。resolver 的输出由合约规范化排序，包含输入 scenario、route ID、anchor 和步骤；错误统一以稳定 code 和 path 说明原因。

`flow-do` 的路径标题是文档锚点，而不是决策逻辑。测试分三层：resolver 正确映射、锚点一致性、保留标题但篡改合约的 mutation 反例。

## 生命周期模型

临时根目录包含最小 flows、schemas、scripts、records 和一个严格 task。成功路径只使用 `transition-phase.py`：

`plan --confirmed--> do --PRD/evidence/convergence--> check --conclusion/verdict/check confirmation--> act --disposition--> archive`

失败矩阵在相邻转换前仅移除一个关键输入，以观察实际 gate 的稳定错误。fixture 不修改 task 的 phase 绕过转换；必要的 evidence 通过现有登记协议构造。

## 内容预算模型

baseline 记录审计范围、metric 与每个资产的最大允许 bytes。预算检查先验证 baseline 的严格 schema 和资产集合，再计算当前 bytes 与 delta：

- 当前资产未登记或 baseline 资产消失：fail-closed。
- 当前 bytes 大于 baseline：`CONTENT_BUDGET_EXCEEDED`。
- 等于或低于 baseline：通过。
- 对增长的恢复通过必须来自版本控制中的显式 baseline 更新，且 entry 含非空理由；测试同时运行引用和相关 fixture 非退化检查。

baseline 不记录或推断真实 token。它不自动修订自身，避免优化工具循环自证。

## 失败与安全边界

- 所有配置/fixture 路径通过受控相对路径解析，拒绝绝对路径和 `..` 逃逸。
- 所有 CLI 输出规范化 JSON；失败包含可枚举 code 与最小定位信息。
- 临时仓库在测试后清理；并发运行不共享真实 `records/` 或活跃任务。
- 不调用网络或模型；真实 Agent 性能继续由未来 runner + 保留任务任务评测。
