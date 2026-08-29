# SSOT 修订草案（实体本体模型）【已取代】

> **状态：SUPERSEDED** — 本草案已被 `ssot-ontology-v3-final.md` 取代；v3 已落地为活跃 `ontology/README.md`。本文件仅保留为设计演进历史。
> 原状态：草案。供审阅，未改动活跃 `ontology/README.md` 与校验器。
> 目的：将 SSOT 从"知识形态分类（taxonomy）"修正为真正的"实体本体（ontology）"——以领域实体为核心单元。

## 核心转变
原 SSOT 把 `pattern/principle/pitfall/fact` 当作顶层 `type` 与目录分类，本质是 **taxonomy（按知识形态归档）**。
本体论应以**实体（entity）**为核心：节点描述实体"是什么样子"（`attributes` 可派测试验证实现），关系表达实体层次与组合，知识形态作为节点的**维度**与**关系挂接**。

## 1. 本体核心单元 = 实体
- 每个节点是一个领域实体或概念实体，具有 `attributes`（特征/属性，可派生测试用例验证"实现的实体是否正确"）。
- 多个实体可 `composed_of` 组合表达复杂知识（满足"实体可由多个实体表达方便表达知识"）。

## 2. 目录约定（目录即真理：type == 父目录名）
```
ontology/
  README.md
  domain/<slug>.md     # 领域聚合根实体（type=domain），如 tls、x509
  entity/<slug>.md     # 具体实体（type=entity），如 tls-session、mtls-handshake
  concept/<slug>.md    # 跨实体抽象概念
  process/<slug>.md    # 有步骤的流程实体
  role/<slug>.md       # 参与角色实体（client/server/CA）
```
> 知识形态（pattern/principle/pitfall/fact/decision）**不再作为顶层目录**，降为节点的附加维度（见 §4）。

## 3. 实体类别受控词汇（type，起点，可扩展）
`domain` / `entity` / `concept` / `process` / `role`
- 新增实体类别须在此登记并说明理由（开放但不失控）。
- 每个节点可带 `also_type`（辅助类别）表达跨类归属。

## 4. 知识形态作为节点维度（非目录）
- 每个节点可用 `knowledge_form` 字段标记其承载的知识形态：`pattern` / `principle` / `pitfall` / `fact` / `decision` / `concept` / `process`。
- 实体与其知识形态通过关系连接：
  - `relates_to`（通用弱相关）
  - `guided_by`（实体受其 principle/pattern 指导，指向 `knowledge_form` 节点）
  - `exemplifies`（知识形态节点归属其实体，反向 of `guided_by`）

## 5. 关系词汇表（扩展）
| 关系 | 语义 | 约束 |
|------|------|------|
| `specializes` | A is-a B（特化） | 构成层次树，无环 |
| `instance_of` | A 是 B 的实例 | — |
| `composed_of` / `part_of` | 实体组合表达 | 子实体 attributes 聚合到父 |
| `relates_to` | 弱相关 | — |
| `guided_by` | 实体受知识形态指导 | 指向 `knowledge_form` 节点 |
| `exemplifies` | 知识形态归属实体 | 反向 of guided_by |

## 6. attributes 结构（属性即测试点）
同原 SSOT：每个 attribute 含 `name` / `desc` / `constraint` / `testable_signal`，`testable_signal` 是派生测试的源头。

## 7. 组合规则
同原 SSOT：`composed_of` 多个子实体时，父实体有效属性 = 子实体 `attributes` 聚合（去重）；归纳（自底向上）从实例创建抽象，关系无环。

## 8. 示例（tls 域实体树）
```
domain/tls.md
  attributes: [角色, 阶段, 算法协商, 凭据路径]
  composed_of: [ontology:entity/mtls-handshake, ontology:entity/x509-certificate]
entity/mtls-handshake.md
  attributes: [枚举名称映射, 网络序, 兼容别名]
  guided_by: [ontology:pattern/mtls-handshake-enum-unify, ontology:pitfall/mtls-handshake-netorder]
pattern/mtls-handshake-enum-unify.md     # type=entity（或 concept）, knowledge_form=pattern
  attributes: [...]
  exemplifies: ontology:entity/mtls-handshake
```

## 9. 对校验器 / 门禁的影响
- `scripts/ontology-validate.py` 的 `type` 受控词汇从知识形态改为实体类别（§3）。
- AC-1（type==目录名）不变；新增校验 `knowledge_form`（若存在）∈ 受控集合，且 `guided_by`/`exemplifies` 引用非空悬。
- `ontology-check` skill 同步更新。

## 10. 与四层模型 / ADR-0030（不变）
`layer` 字段与物理归并边界维持原 SSOT §7/§8 约定。
