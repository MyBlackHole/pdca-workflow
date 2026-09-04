---
schema: pdca.asset/v1
id: ontology:domain/mysql-schema-nullable-contract
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/mysql-schema-nullable-contract/1.0.0
summary: MySQL --schema 必须如实标注 nullable（InnoDB 长度数组契约）
domain:
- ontology:domain/mysql
relations:
  specializes:
  - ontology:domain/mysql
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "运行 grep -q 'MySQL --schema 必须如实标注 nullable（InnoDB 长度数组契约）' ontology/domain/core/mysql-schema-nullable-contract.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


# MySQL --schema 必须如实标注 nullable（InnoDB 长度数组契约）

> 来源：T0325 可见性 POC 补缺（records/T0325-0819-pg-poc-consistency-visibility/conclusion.md）

## 背景
mysqlbin 对 5.6/5.7（无 SDI）用 `--schema=` 文本构建物理布局。8.0+ 走 SDI 自动。
T0325 在 5.6/5.7 复验删除场景时发现 TEXT 字段读出**空串**：schema 未标 `:null`，
但真实表列默认可空 → 记录布局推断错误。

## 根因
InnoDB 列**默认可空**（`CREATE TABLE (id BIGINT PRIMARY KEY, val INT, note TEXT)` 的
val/note 均可空）。记录布局：
```
[header][null bitmap: CEIL(n_nullable/8) 字节][变长长度数组][列数据]
```
`rec_offsets` 用 `lens = org-6 - (n_nullable+7)/8` 定位变长长度数组。若 schema 把
可空列标成 NOT NULL（少算 null 位图字节），长度数组起点**偏高 1 字节**，读到
null 位图/info 字节（0x00）→ 变长字段长度误判为 0 → 空串。

8.0/8.4 SDI 自带真实 nullable 标记，不受影响（故原矩阵只在 8.0 测时未暴露）。

## 契约
- **`--schema` 必须与真实表定义一致**：可空列加 `:null`，不可空列不加（默认 NOT NULL）。
  主键列（`:pk`）隐含 NOT NULL。
- 典型示例（poc_scen.schema）：
  ```
  id:bigint:pk
  val:int:null
  note:text:null
  ```
- 定长字段（INT/DATETIME/DECIMAL）不受此影响（无长度前缀），但为语义完整仍应标对。

## 自查
- 已知表定义含 `NOT NULL` 时 schema 可不标；**不确认时一律标 `:null`**（记录含 null
  位图是更常见情况）。
- 现象信号：变长字段（varchar/text）全部输出空串或错位、定长字段正常。
