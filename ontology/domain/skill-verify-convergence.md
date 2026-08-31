---
schema: pdca.asset/v1
id: ontology:domain/skill-verify-convergence
name: verify-convergence
summary: Verify that PDCA cycles have converged on acceptable solutions.
description: 生成并验证 convergence → PRD AC → registered evidence 的确定性支撑链，作为 Do→Check 硬门禁。
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/pdca-task
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


---
name: verify-convergence
description: 生成并验证 convergence → PRD AC → registered evidence 的确定性支撑链，作为 Do→Check 硬门禁。
---

1. 按 `prd.md` 中精确标题 `## 验收标准` 下的 Markdown checkbox 顺序编号为
   `AC-1`、`AC-2`……。
2. 先通过 `register-evidence` 登记所有实质证据。
3. 在任务工作区生成 `convergence.json`：

```json
{
  "schema": "pdca.convergence/v1",
  "items": [
    {
      "index": 1,
      "text": "与 task.meta.convergence[0] 完全一致",
      "criteria": ["AC-1"],
      "evidence_ids": ["unit-result"]
    }
  ]
}
```

4. 为 task 中每条 convergence 写且只写一个 item：
   - `index` 从 1 开始；
   - `text` 原样复制 Plan 值；
   - `criteria` 指向已定义 AC；
   - `evidence_ids` 指向实际支持这些 AC 的非 map 证据。
5. 最后登记 map，固定使用：

```bash
python3 "$PDCA_HOME/scripts/register-evidence.py" \
  --record <record-id> \
  --source <task-dir>/convergence.json \
  --id convergence-map \
  --kind convergence-map \
  --criterion AC-1
```

有多个 AC 时重复 `--criterion`。这些 criteria 仅表示 map 涉及范围；验证器明确
排除 convergence map，不允许它给 AC 或自身作证。

6. 执行：

```bash
python3 "$PDCA_HOME/scripts/validate-convergence.py" --task-dir <task-dir>
```

任何 issue 都必须修复后再进入 Check。程序验证引用结构，Check 阶段仍负责判断
证据内容是否足以支持结论。

完成条件：命令返回 `valid: true`，且 Do→Check 阶段转换通过同一核心门禁。

## 已知坑

- convergence 文本必须与 task.json `meta.convergence` 逐字一致（CONVERGENCE_TEXT_MISMATCH）；convergence-map 不能作为自身证据。
