# P1模板收敛：最小本体约束+扩展区与豁免标记

## 背景

`T2045 §5` 确认模板束缚主因是 `a填空化+b门禁过严`（`task.schema.json additionalProperties:false` 全锁 + `prd` 无自由区 + `ontology-validate` 无豁免），`T2046` 只补了本体锚未动模板机制。本切片把四模板收敛为最小本体约束：尺子只量 `id/relations/testable_signal` 三件套，其余放自由区。

输入锚点：
- `file: schemas/task.schema.json:1` — 全字段锁死（待加 extensions 自由对象）
- `file: scripts/pdca_core.py:209` — acceptance 解析（自由节须豁免）
- `file: scripts/ontology-validate.py:1` — frontmatter 校验（待加注释块豁免）
- `file: ontology/concept/knowledge-artifact.md:1` — 最小约束挂接点

## 目标

新建 `ontology:concept/template-minimal` 并落地双投射：`task.json:meta.extensions` 自由对象 + `prd:## 自由扩展` 非AC节 + `validate` 注释块豁免，旧任务全过、新概念可先行。

## 范围

- 输入：`schemas/task.schema.json`、`scripts/pdca_core.py:acceptance_criteria`、`scripts/ontology-validate.py`、`ontology/concept/`
- 输出：本体新节点 + 三处投射 + 回归验证
- 不做：skill/frontmatter 扩展区（后续）；不改门禁语义，只加自由通道

## 功能需求

1. **最小模板本体**：新建 `ontology:concept/template-minimal`（三件套必填 + 扩展区规范 + testable_signal），`specializes: knowledge-artifact`，`relates_to: pdca-task`
2. **双投射**：`task.schema.json:meta` 加 `extensions` 自由对象（`additionalProperties:true`，门禁跳过内容）；`pdca_core:acceptance_criteria` 在 `## 自由扩展` 节停 parse（其后 `## `节不计 AC）；`ontology-validate` 跳过 `<!-- template-exempt -->…<!-- /template-exempt -->` 块内

## 验收标准

- [ ] AC-1 最小模板本体已产：`ontology/concept/template-minimal.md` 存在且 `ontology-validate OK`，`testable_signal` 含三件套断言可重跑
- [ ] AC-2 双投射已落地：含 `extensions` 的 task 样例过 schema，含 `## 自由扩展` 的 prd 样例 AC 解析不受影响，含豁免块的本体样例过 validate，且 `validate OK + islands:0 + doctor missing==[]` 全过

## 关联本体节点

```
ontology:concept/pdca-architecture
ontology:concept/knowledge-artifact
ontology:concept/pdca-task
```

## 拆分映射

- 最小模板本体 -> T2050 本体
- 双投射+回归 -> T2051 投射
