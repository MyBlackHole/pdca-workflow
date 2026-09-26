# 当前本体与流程入口

[PDCA](concept/pdca.md) 定义 4.x 总原则；[INDEX](INDEX.md) 是当前规则 authority 的索引；
[LOAD-MAP](LOAD-MAP.md) 定义 AI 在不同事件下的最小读取方法；
[三场景](process/work-scenarios.md) 定义真实交付对象。

阶段方法位于 `process/flow-*.md`，每次只按当前 phase、scene 和真实事件读取需要的部分。

## 物理知识库不等于当前任务上下文

`ontology/` 同时保存：

1. **当前规则**：INDEX 中的规则、phase/scene 方法和当前契约；
2. **参考知识**：领域研究、实体、模式、陷阱、历史方法等；
3. **项目模型**：`ontology/projects/<project>/works/<work>/<revision>` 下绑定具体工作的模型。

这些内容物理上可以共存，但 AI 不应递归加载整个目录。

参考资产进入任务必须经过 [REUSE-01](concept/ontology-reuse.md) 与
[ADOPT-01](concept/ontology-adoption.md)：先检索候选，再固定 id/revision/内容、来源、适用目标和限制。
搜索命中、链接存在、同名概念、`authority` 字段或“内容更详细”都不能自动把 reference 变成当前规则。

旧案例、retired 指针和未采用 reference 不能授予权限、恢复原用户授权、覆盖当前规则或复制 PASS。

参考资产的 active-reference / archived / retired 区别、去重与恢复只在
[REUSE-01](concept/ontology-reuse.md#参考资产的生命周期) 定义；来源缺口见[来源说明](provenance/README.md)。

## 规则只维护一份

PDCA 语义由 AI 直接读取当前 authority、Skill、Plan 和证据进行审查。
**禁止建立项目专用 Python/Shell validator，把同一语义重新编码成 assert、数字阈值或第二份 manifest。**

通用工具可以用于采集事实，例如 Git、文本搜索、格式解析器、编译器、shell syntax check
以及 TARGET_ROOT 自己已有的测试；工具输出只是 evidence，最终符合性判断仍由 AI 的 Check 完成。

## Check

Check 使用 [flow-check](process/flow-check.md) 的四遍方法：

1. Scope Review；
2. Consistency Review；
3. Adversarial Review；
4. Evidence Review。

需要第二视角时可以使用一次性只读独立 AI，但它的 findings 仍是待核验 claim，不替代当前 Check，
也不自动建立新的 PDCA 生命周期。

## 文档质量

| 维度 | 要求 |
|---|---|
| 单一语义来源 | 一条 PDCA 规则不在 validator/manifest 中重复实现 |
| 最小读取 | 链接是导航，不是递归加载指令 |
| 证据优先 | PASS/fail/unknown 必须可追溯到对象、authority/AC 与事实 |
| 主动反证 | Check 主动寻找能够推翻当前结论的证据 |
| 参考显式采用 | reference 必须经 REUSE/ADOPT 固定版本和适用性 |
| 不造阈值 | 没有领域依据时，不把 LOC、工时、置信度等经验值固化为规则 |
