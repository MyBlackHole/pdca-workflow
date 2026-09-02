---
schema: pdca.asset/v1
id: ontology:domain/build-config
type: domain
layer: Knowledge
status: active
summary: build-config 领域知识根节点（由 ontology/domain/build-config/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "检查本文件构建相关章节的完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# build-config（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `go-module-in-xmake` → `ontology:domain/build-config-go-module-in-xmake`
- `hide-static-lib-symbols` → `ontology:domain/build-config-hide-static-lib-symbols`


## C4 组件 — build-config（P1补图）

```mermaid
graph TD
    A[build-config<br/>domain] --> B[core能力<br/>PDCA]
    B --> C[实现<br/>scripts/]
    %% Source: ontology/domain/build-config.md:1 + ontology/concept/ontology-fidelity-criterion.md:1
```

Source: `ontology/domain/build-config.md:1` + `ontology/concept/ontology-fidelity-criterion.md:1`

## 正例

```bash
# 正例：build-config 可通过本体复现
grep -q 'build-config' ontology/domain/build-config.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'
```

## 反例

```bash
# 反例：缺图导致不可视化
# 无 mermaid 时，AI无法从本体还原组件关系，需补图
```

## 门禁

- **图门禁**：`grep -c 'mermaid' ontology/domain/build-config.md` ≥1
- **溯源门禁**：含 `Source:` 行号
- **校验**：`python3 scripts/ontology-validate.py` 0 issues

