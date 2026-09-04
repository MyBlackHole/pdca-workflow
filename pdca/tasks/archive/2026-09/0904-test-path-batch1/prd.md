# B1测试清偿首批：陈旧skill路径簇修复（T2059子切片）

## 背景

`T2056` 立案 104 预存红，其中最大一簇约 30 个为 `FileNotFoundError` 陈旧 skill 路径：测试夹具仍引用 `T2036` 迁移前的 `ontology/domain/skill-*.md`（实文件已在 `ontology/domain/pdca/`）、`ontology/process/flow-*/SKILL.md` 与 `skills/*/SKILL.md`（flows/skills 旧布局已不存在）。`T2046` 已修 `AGENTS.md` 同类漂移，本批修测试侧同构问题，被测代码不动。

输入锚点：
- `file: /tmp/pytest-dur.log:1` — 路径簇失败清单（约30个FileNotFoundError）
- `file: ontology/domain/pdca/skill-grilling.md:1` — 迁移后实路径
- `file: AGENTS.md:27` — T2046 路由修复先例

## 目标

路径簇全绿，全量无新增红，`T2059` 减负约三成。

## 范围

- 输入：引用陈旧 skill 路径的测试夹具（约30个失败）
- 输出：夹具路径改写 + 双检验证
- 不做：同文件非路径红（留后批）；被测代码零改动；本体零改动

## 功能需求

1. **skills布局簇**：`ontology/domain/skill-*` → `ontology/domain/pdca/skill-*`，`skills/*/SKILL.md` 按现状处置（文件不存在则改夹具指向实节点或删过期断言）
2. **flows布局簇**：`ontology/process/flow-*/SKILL.md` 改写为实路径（`ontology/process/flow-*.md` 或 `ontology/domain/pdca/` 对应 skill）

## 验收标准

- [ ] AC-1 skills布局簇全绿：目标测试重跑通过，`FileNotFoundError: skill` 清零
- [ ] AC-2 flows布局簇全绿且无新增红：目标测试重跑通过，全量 `pytest` 失败数只减不增（对照 `104` 基数）

## 关联本体节点

```
ontology:concept/pdca-architecture
ontology:concept/pdca-task
```

## 拆分映射

- skills布局簇 -> T2061 路径
- flows布局簇 -> T2062 路径
