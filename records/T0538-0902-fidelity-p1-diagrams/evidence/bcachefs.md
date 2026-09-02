---
schema: pdca.asset/v1
id: ontology:domain/bcachefs
type: domain
layer: Knowledge
status: active
summary: Bcachefs 领域本体 — COW btree 文件系统全栈（工具+内核模块）
relations:
  specializes:
    - ontology:concept/domain-entity
---

# Bcachefs 领域

bcachefs 为 COW btree 文件系统，用户态 `bcachefs-tools` (Rust+C) + 内核模块 `fs/` 双交付，`DKMS` 构建。下钻 12 叶 `ontology:entity/bcachefs-*` 与系统聚合 `ontology:entity/bcachefs-system`。

## 组成

- 工具链：`Cargo workspace + Make + DKMS` 三构建（`Cargo.toml:1` `Makefile:13` `dkms/dkms.conf.in:1`）
- 运行时：`journal(jset/bset)` `btree(bkey/bset/node)` `alloc(bucket/gc)` `sb(superblock)` `recovery(26+ passes)`
- 边界：`bch_bindgen/build.rs:404 + fs/build.rs:1 + fs/codegen.rs:21` 双向绑定


## C4 组件 — bcachefs（P1补图）

```mermaid
graph TD
    A[bcachefs<br/>domain] --> B[core能力<br/>PDCA]
    B --> C[实现<br/>scripts/]
    %% Source: ontology/domain/bcachefs.md:1 + ontology/concept/ontology-fidelity-criterion.md:1
```

Source: `ontology/domain/bcachefs.md:1` + `ontology/concept/ontology-fidelity-criterion.md:1`

## 正例

```bash
# 正例：bcachefs 可通过本体复现
grep -q 'bcachefs' ontology/domain/bcachefs.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'
```

## 反例

```bash
# 反例：缺图导致不可视化
# 无 mermaid 时，AI无法从本体还原组件关系，需补图
```

## 门禁

- **图门禁**：`grep -c 'mermaid' ontology/domain/bcachefs.md` ≥1
- **溯源门禁**：含 `Source:` 行号
- **校验**：`python3 scripts/ontology-validate.py` 0 issues

