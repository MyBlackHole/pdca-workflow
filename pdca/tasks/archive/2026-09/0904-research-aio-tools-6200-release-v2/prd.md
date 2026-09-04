# 重调 aio-tools 6200/release 全景（按推荐：全景+build事实+records-only，主链路+rdbcomm 增补）

## 背景

复用 `T2027 0904-research-aio-tools-6200-release` 的快照事实（`6.2.0.0-release fe9d4364`，`xmake.lua 11 变量`，`build/version.log 17 产物`，`build/linux/x86_64/release 60+ 产物`），按 `Round 1` 4 问的推荐确认重调，补 `rdbcomm` 插件契约一节，余结构沿用 T2027。

## 目标

产出 `research-report.md`（含 ≥3 mermaid + ≥3 Source + 可重跑清单），覆盖全景/版本/构建/CI/主链路+rdbcomm，沉于 `records-only`。

## 范围

- 输入：`/home/black/Public/aio/aio-tools/6200/release`（复用 T2027 度量：488 源码文件/18.9万 LOC）
- 含 `build/install` 事实，略 `third_party` 展开
- 不做：不改代码、不跨分支、不压测

## 功能需求

1. 复用 T2027 的 C4 L2/依赖拓扑/版本状态机三图，增补 `rdbcomm` 插件契约图/表
2. 模块矩阵沿用 14 模块+libs+third_party 三列，与 `build/version.log` 一致
3. 版本/构建/CI 可重跑清单复用 T2027
4. 主链路时序复用 T2027，增 `rdbcomm` 插件生命周期补充

## 验收标准

- [ ] AC-1 `research-report.md` 含 7 段且 `mermaid≥3` `Source:≥3`
- [ ] AC-2 C4 L2/依赖/状态机/时序图各≥1 且每图 Source
- [ ] AC-3 模块矩阵 14 模块三列与 `build/version.log` 一致可重跑
- [ ] AC-4 版本/构建/CI 可重跑验证清单
- [ ] AC-5 主链路+rdbcomm 时序/状态可回溯 file:line
- [ ] AC-6 已 register-evidence 且 conclusion 含 `records-only` 决策过 settlement

## 关联本体节点

```
ontology:concept/pdca-task
ontology:pattern/scientific-research-methodology
```

## 拆分映射

- 全景/版本/构建/CI -> report#发现.全景
- rdbcomm 增补 -> report#发现.rdbcomm
