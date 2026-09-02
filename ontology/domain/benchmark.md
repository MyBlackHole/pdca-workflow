---
schema: pdca.asset/v1
id: ontology:domain/benchmark
type: domain
layer: Knowledge
status: active
summary: benchmark 领域知识根节点（由 ontology/domain/benchmark/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "检查本文件基准测试相关章节的完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# benchmark（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `build-profile-baseline-matching` → `ontology:domain/benchmark-build-profile-baseline-matching`
- `paired-comparison-noise` → `ontology:domain/benchmark-paired-comparison-noise`
- `small-pack-streaming-decode` → `ontology:domain/benchmark-small-pack-streaming-decode`
- `small-writer-pool-parallelism` → `ontology:domain/benchmark-small-writer-pool-parallelism`


## C4 组件 — benchmark（P1补图）

```mermaid
graph TD
    A[benchmark<br/>domain] --> B[core能力<br/>PDCA]
    B --> C[实现<br/>scripts/]
    %% Source: ontology/domain/benchmark.md:1 + ontology/concept/ontology-fidelity-criterion.md:1
```

Source: `ontology/domain/benchmark.md:1` + `ontology/concept/ontology-fidelity-criterion.md:1`

## 正例

```bash
# 正例：benchmark 可通过本体复现
grep -q 'benchmark' ontology/domain/benchmark.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'
```

## 反例

```bash
# 反例：缺图导致不可视化
# 无 mermaid 时，AI无法从本体还原组件关系，需补图
```

## 门禁

- **图门禁**：`grep -c 'mermaid' ontology/domain/benchmark.md` ≥1
- **溯源门禁**：含 `Source:` 行号
- **校验**：`python3 scripts/ontology-validate.py` 0 issues

