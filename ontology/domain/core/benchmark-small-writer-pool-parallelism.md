---
schema: pdca.asset/v1
id: ontology:domain/benchmark-small-writer-pool-parallelism
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/benchmark-small-writer-pool-parallelism/1.0.0
summary: Small Writer Pool Parallelism
domain:
- ontology:domain/benchmark
relations:
  specializes:
  - ontology:domain/benchmark
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件基准测试场景含至少 1 个可重跑验证命令，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# Small Writer Pool Parallelism

When a client receives packed small files, tune local writer concurrency with paired GET measurements rather than assuming more workers is faster.

## Reusable pattern

- Keep the default synchronous path unchanged unless the measurements justify a behavior change.
- Bound the producer queue and expose enqueue, completion, peak queue, peak active, backpressure, and failure counters through an existing progress channel.
- Latch the first worker error, clear pending work, stop accepting frames, and drain only at ordering barriers before hardlinks, directory metadata, or TREE_END.
- Compare workers `0/1/2/4/8` in paired samples, then repeat the selected candidate under checksum and strict durability.

## Round 60 result

On the tested host with 10000 small files and four pairs, worker 1 regressed against worker 0, worker 4 had the best average throughput in the baseline matrix, and worker 8 did not improve over worker 4. The safe disposition was to keep default worker 0 and use worker 4 only as an explicit deployment candidate.

This result is workload- and storage-dependent; repeat the paired matrix on the target host before changing defaults.


## C4 组件 — benchmark-small-writer-pool-parallelism（P1补图）

```mermaid
graph TD
    A[benchmark-small-writer-pool-parallelism<br/>domain] --> B[core能力<br/>PDCA]
    B --> C[实现<br/>scripts/]
    %% Source: ontology/domain/benchmark-small-writer-pool-parallelism.md:1 + ontology/concept/ontology-fidelity-criterion.md:1
```

Source: `ontology/domain/benchmark-small-writer-pool-parallelism.md:1` + `ontology/concept/ontology-fidelity-criterion.md:1`

## 正例

```bash
# 正例：benchmark-small-writer-pool-parallelism 可通过本体复现
grep -q 'benchmark-small-writer-pool-parallelism' ontology/domain/benchmark-small-writer-pool-parallelism.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'
```

## 反例

```bash
# 反例：缺图导致不可视化
# 无 mermaid 时，AI无法从本体还原组件关系，需补图
```

## 门禁

- **图门禁**：`grep -c 'mermaid' ontology/domain/benchmark-small-writer-pool-parallelism.md` ≥1
- **溯源门禁**：含 `Source:` 行号
- **校验**：`python3 scripts/ontology-validate.py` 0 issues

