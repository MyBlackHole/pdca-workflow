# 验证本体→代码：rpc 1544 细化 + rdbcomm SHACL（v1.0.0 首个 bugfix 垂直切片）

## 背景

`v1.0.0` 已冻（`8 桶 FAIR` + `MOMo 5 域` + `FAIR 426`），`T2028` 的 `P0` 建议（`rpc.cpp:1544` 固定文案）与 `T2036` 的 `rdbcomm 32/5MB` 本体（`ontology:entity/aio-tools-6200-release`）待 **本体→代码** 垂直验证。

输入锚点：
- `file: /home/black/Public/aio/aio-tools/6200/release/rpc/rpc.cpp:1544` — `connect to failure` 固定文案（`T2028` 结论 `P0`）
- `file: ontology/entity/aio-tools-6200-release.md: rdbcomm_plugin_contract` — `32 槽/5MB` 约束（`T2028` 本体）
- `file: ontology/versions/2026-09-04/START-HERE.owl:1.0.0` — `v1.0.0` 冻结版

## 目标

产 **可回归验证** 的 `bugfix` 切片：`rpc 1544` 细化与 `rdbcomm` `SHACL`，证明 **本体指导代码** 的价值（`ontology` 的 `testable_signal` 直驱 `回归测试`）。

## 范围

- 输入：`aio-tools 6200/release` 的 `rpc/rdbcomm`（`v1.0.0` 本体为 `core`）
- 输出：`rpc.cpp:1544` 细化 `diff` + `rdbcomm` `SHACL` 形状 + 回归测试
- 不做：不改 `FSDAEMON/rpc` 全链，仅 `1544` 与 `32/5MB` 两点

## 功能需求

1. **rpc 1544 细化**：`rpc.cpp:1544` 的 `snprintf` 区分 `connect/socket/handshake/EBADF/File exists`（`T2028` 的 `ioctl_buff` 透出），`grep -q` 可检
2. **rdbcomm SHACL**：为 `32 槽/5MB` 补 `SHACL` 形状（`5MB` 超限分片、`32` 满 `SHACL` 阻断），`shacl` 可检

## 验收标准

- [ ] AC-1 `rpc.cpp:1544` 已细化：`grep -q "connect.*socket.*handshake" rpc/rpc.cpp` 命中且 `T0457` 的 `8811` 回归可检
- [ ] AC-2 `rdbcomm` `SHACL` 已补：`shacl.ttl` 对 `5MB` 超限与 `32` 满可 `shacl` 检

## 关联本体节点

```
ontology:entity/aio-tools-6200-release
ontology:concept/pdca-task
```

## 拆分映射

- rpc 1544 细化 -> T2042 本体
- rdbcomm SHACL -> T2042 本体
