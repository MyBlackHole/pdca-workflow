# AI 深本体 B：zfs/bcachefs 域 LLM 两阶段（MOMo 20 模块复用）

## 背景

`T2036` 全量 `8 桶` 已冻，`T2034 P0-a` 的 `50 核心` 与 `T2038 P0-b` 的 `426` 已验证 `AI 10→20 CQ + 5 域 disjoint + 人定 4→12 问` 闭环，现以冻结版为 `core`，对 `zfs 11` + `bcachefs 10` 域启动第二批 `MOMo` 两阶段（`先定模块再产规则体`，`GeoLink` 高精召回范式）。

输入锚点：
- `file: ontology/domain/zfs/*.md:11` + `ontology/domain/core/bcachefs.md:1` — zfs/bcachefs 域
- `file: pdca/tasks/archive/2026-09/0904-ai-ontology-p0a-pdca50/cq-delta-draft.md:10 CQ` — 模板
- 网络：`MOMo LLM4KGOE 2024` 的 `20 模块两阶段` + `RIGOR` 逐表 `delta`

## 目标

对 `zfs/bcachefs` 域跑 `LLM` 两阶段：**先定 `5 模块`（`zfs-dmu/dsl/spa/zio/arc` 等）再产 `规则体`**，产 `20 CQ`（`zfs/bcachefs` 各 10）+ `disjoint` 扩增 + `4 问` 人审。

## 范围

- 输入：`zfs 11` + `bcachefs 10`（`domain/zfs + domain/core/bcachefs*`）
- 输出：`20 CQ` + `zfs/bcachefs` 的 `disjoint` + `4` 人审 `Grill`
- 不做：不改 `pdca 50` 核心，仅深 `zfs/bcachefs`

## 功能需求

1. **先定模块**：`LLM` 第一阶段按 `MOMo` 定 `zfs` 的 `5 模块`（`dmu/dsl/spa/zio/arc`）与 `bcachefs` 的 `3 模块`
2. **再产规则体**：第二阶段为每 `CQ` 产 `规则体`（`antecedent → consequent`），`o1` 拟 `85%` 覆盖
3. **人定**：`20 CQ` 中 `4` 复杂 `Reification` 人审 `captured:true`

## 验收标准

- [ ] AC-1 `5 模块` 已定：`zfs` 的 `5 模块` 名单可检（`grep -q "zfs-dmu" ontology/domain/zfs/*.md`）
- [ ] AC-2 `20 CQ` 规则体已产：`20 CQ` 各含 `规则体`，`5 Reification` 可检
- [ ] AC-3 人定已产：`4/20` 复杂 `CQ` 人审 `captured:true`，`HITL` 可度量

## 关联本体节点

```
ontology:domain/zfs-crypto
ontology:domain/bcachefs
```

## 拆分映射

- 先定模块 -> T2040 本体
- 再产规则体+人定 -> T2040 本体
