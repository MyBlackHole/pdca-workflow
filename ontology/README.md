# 当前本体与流程入口

[PDCA](concept/pdca.md) 定义 4.x 总原则；[INDEX](INDEX.md) 是当前规则 authority 的索引；
[LOAD-MAP](LOAD-MAP.md) 定义 AI 在不同事件下的最小读取方法；
[三场景](process/work-scenarios.md) 定义真实交付对象。

阶段方法位于 `process/flow-*.md`，场景义务统一位于 [SCENE-01](process/work-scenarios.md)；scene Skill 只是发现/路由入口。每次只按当前 phase、scene 和真实事件读取需要的部分。版本域见 [PDCA：Version domains](concept/pdca.md#version-domains)；record schema major 与 protocol revision 的关系见 [record-shape 索引](contracts/record-shapes/index.md#schema-major-and-protocol-revision)。

## 物理知识库不等于当前任务上下文

`ontology/` 同时保存：

1. **当前规则**：INDEX 中的规则、phase/scene 方法和当前契约；
2. **参考知识**：领域研究、实体、模式、陷阱、历史方法等；
3. **项目模型**：`ontology/projects/<project>/works/<work>/<revision>` 下绑定具体工作的模型。

这些内容物理上可以共存，但 AI 不应递归加载整个目录。

**目录名不是 project ontology 类型系统。** 当前 `domain/entity/pattern/fact/principle` 主要是可检索 reference library；真正绑定某个 project/work 的 ontology revision 应进入 `ontology/projects/<project>/works/<work>/<revision>`（或显式采用的外部固定模型），并满足 ONTOLOGY-01 的 semantic construction contract：每个 revision 有唯一 model root，可解析 requirement coverage、definitions/work instances、relations、constraints、provenance 与 unknown。

当前仓库已加入第一份 **candidate** project ontology：[`bounded-counter candidate-0.1.0`](projects/pdca-host-smoke/works/bounded-counter/candidate-0.1.0/model.md)。它用于验证 rc.5 的建模语义，但明确 `fixed_by_modeling_act: false`，因此不是 host-smoke PASS 或 fixed revision；维护审查见 [bounded-counter project ontology 审查](../docs/reviews/2026-09-27-bounded-counter-project-ontology.md)。构建协议背景审查见 [本体构建审查](../docs/reviews/2026-09-27-ontology-construction.md)。

参考资产进入任务必须经过 [REUSE-01](concept/ontology-reuse.md) 与
[ADOPT-01](concept/ontology-adoption.md)：先检索候选，再固定 id/revision/内容、来源、适用目标和限制。
搜索命中、链接存在、同名概念、`authority` 字段或“内容更详细”都不能自动把 reference 变成当前规则。

旧案例、retired 指针和未采用 reference 不能授予权限、恢复原用户授权、覆盖当前规则或复制 PASS。

## Ontology lifecycle

当前建模链按职责分开：

```text
ONTOLOGY-01   model root + semantic construction / closure
REUSE-01      找 semantic-unit candidate
ADOPT-01      固定选中的 definition/claim/constraint
EVOLVE-01     固定 M1 -> M2 candidate delta
TREE-01       explicit composition relation -> tree candidate
NODE-01       work instance responsibility -> node qualification
Modeling Act  固定 ontology/tree/node revisions
DECOMP-01     fixed qualified node -> task seed candidate
```

candidate、adopted input、proposed revision、fixed node、task seed 是不同事实，不能因为后一步“将来可能需要”就提前合并。
正式 task creation 仍由 TASK/CONFIRM/agent-dispatch 处理；DECOMP seed 本身不创建 Agent。

reference 的 active / archived / retired 候选资格、去重与恢复只在
[REUSE-01](concept/ontology-reuse.md#reference-lifecycle) 定义；来源缺口见[来源说明](provenance/README.md)。

## 规则只维护一份

PDCA 语义由 AI 直接读取当前 authority、Skill、Plan 和证据进行审查。
**禁止建立项目专用 Python/Shell validator，把同一语义重新编码成 assert、数字阈值或第二份 manifest。**

通用工具可以用于采集 observation，例如 Git、文本搜索、格式解析器、编译器、shell syntax check
以及 TARGET_ROOT 自己已有的测试。CASE-01 在执行前固定 oracle，TEST-01 只保存实际 observation，
EVIDENCE-01 将 decisive claim 绑定到 observation/counterevidence，最终 Check 只按 VERDICT-01 聚合。

## Rework / schedule / learning

Check 后的 continuation 分三类，不能互相替代：

```text
same attempt fix
  -> REWORK-01
  -> new Do phase_start

terminal disposition
  -> Act
  -> archived

future work
  -> fixed seed/dependency facts
  -> SCHED-01 candidate
  -> user create

optional learning
  -> explicit Act scope
  -> LEARN-01 candidate/persist/publish
  -> REUSE candidate only
```

Act 是当前 attempt 的终态处置；同-attempt rework 必须发生在 Act 之前。
LEARN 不自动写共享知识、不改 verdict，也不让其他 task 自动采用。

## Check

Check 使用 [flow-check](process/flow-check.md) 的四遍方法：

1. Scope Review；
2. Consistency Review；
3. Adversarial Review；
4. Evidence Review。

需要第二视角时按 REVIEW-01 使用一次性只读独立 AI；findings 仍只是待核验 claim，必须回到 EVIDENCE-01。
正式独立 verification 是用户显式创建的 pdca-verify scene/task，不由一次性 review 自动升级。

## 文档质量

| 维度 | 要求 |
|---|---|
| 单一语义来源 | 一条 PDCA 规则不在 validator/manifest 中重复实现 |
| 最小读取 | 链接是导航，不是递归加载指令 |
| 证据优先 | PASS/fail/unknown 必须可追溯到对象、authority/AC 与事实 |
| 主动反证 | Check 主动寻找能够推翻当前结论的证据 |
| 参考显式采用 | reference 必须经 REUSE/ADOPT 固定版本和适用性 |
| 不造阈值 | 没有领域依据时，不把 LOC、工时、置信度等经验值固化为规则 |
