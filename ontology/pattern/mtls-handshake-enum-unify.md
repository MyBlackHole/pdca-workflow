---
schema: pdca.asset/v1
id: ontology:pattern/mtls-handshake-enum-unify
type: pattern
layer: Knowledge
status: active
docType: Pattern
tags: [mtls, enum]
summary: 四模块握手算法枚举与名称映射收敛重构
source_task: T0359
relations:
  specializes: [ontology:pattern]
  guides: [ontology:entity/mtls-handshake]
attributes:
  - name: applicability
    desc: 多模块各自定义同一组算法枚举与映射的工程
    constraint: ""
    testable_signal: 枚举/映射单头定义，模块别名宏复用，include guard 不冲突，全量构建通过
---

# 四模块握手算法枚举与名称映射收敛重构
# 四模块握手算法枚举与名称映射收敛重构

## 适用场景
多个模块（C/C++ 混合工程）各自定义同一组算法枚举与「名称 ↔ 枚举」映射函数，存在重复定义、取值易漂移、难以统一校验白名单的问题。典型如 rdbcomm / libobk / dmsbtex / rpc 各自维护 `RDB_HS_ALG_*` / `OBK_HS_ALG_*` / `DM_HS_ALG_*` / `HS_ALG_*`。

## 收敛方案（单一来源）
- **真实定义唯一**放在共享头 `libs/common.h`：
  - `HS_ALG_DEFAULT = 0` / `HS_ALG_TLS_SM4_GCM_SM3 = 1` / `HS_ALG_TLS_AES_256_GCM_SHA384 = 2`
  - 每模块兼容别名宏：`RDB_HS_ALG_*` / `OBK_HS_ALG_*` / `DM_HS_ALG_*`；rpc 历史无前缀别名 `HS_ALG_SM4_GCM_SM3` / `HS_ALG_AES_256_GCM_SHA384`
- **统一实现**放在 `libs/hs_algorithm.c`：`hs_algorithm_name` / `hs_algorithm_from_name`，未知值默认返回 `NULL`（与其他模块一致）。
- 各模块本地枚举与映射函数**删除**，引用处经宏别名零改动复用：`#define rdb_hs_algorithm_name hs_algorithm_name` 等。

## 关键陷阱（来自 T0359 实战）
1. **include guard 同名遮蔽**：某模块本地 `common.h` 若用了与 `libs/common.h` 相同的 `__COMMON_H__`，会整体跳过统一头内容，导致别名宏「明明定义了却未生效」。修复：本地 guard 改名（如 `__DMSBTEX_COMMON_H__`）并在本地 `common.h` 顶部 `#include "../libs/common.h"`。
2. **链接依赖遗漏**：统一实现所在的静态库（`tls_cert`）必须被所有「调用方主目标」显式 `add_deps`；仅测试目标能链不够——该模块独立二进制（CLI / 共享库）链接期会报 `undefined reference`。重构后务必全量 `xmake` 构建（含主目标）验证。
3. **枚举命名历史差异**：rpc 旧用无前缀 `HS_ALG_SM4_GCM_SM3`，统一后真实名带 `TLS_` 前缀。用无前缀别名宏兼容，避免改动 rpc 全部调用点（保持非破坏性）。
4. **死代码确认**：删除前用 `grep` 确认零调用（如 `dm_hs_encode/decode/decide` 仅定义无引用），再删定义 + 声明。

## 验收
- `grep` 确认枚举/映射定义仅 `libs/common.h` 一处（别名宏不计第二定义）。
- 全量回归测试通过（含算法不匹配拒绝、跨模块互通集成测试）。
- 双轴代码审查（标准轴 / 规范轴）Blocking = 0。

## 复用建议
跨模块共享枚举/映射时，优先「单头真实定义 + 模块别名宏兼容」而非全局 rename，可在不破坏各模块调用点的前提下收敛单一来源；同时检查本地 common.h 的 include guard 与链接收敛。
