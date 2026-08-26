---
schema: pdca.asset/v1
id: T3979-0826-sec-get-param-api-refactor
phase: check
source_ids: [refactor-evidence, check-verify-evidence]
---

## 上下文
T3979 承接 T3978 用户反馈，将 rdb-config 解析链路由"死注册表 + 六参 `sec_resolve_*`"重构为"枚举参数 ID（`config_param_id_t` 14 条）+ 单参 `sec_get_*(id)` API"，并使注册表成为解析流程唯一事实来源。Do 阶段已完成实现并提交 `6ce5f85a`（18 文件，+369/-646 净删 277 行），声明 45/45 测试全绿。本结论为 Check 阶段独立复核。

## 假设与结果
- 假设 H1：全仓库 `sec_resolve_*` 符号零残留 → 实测源码中 `sec_resolve_(int|bool|str)` 函数符号 **0 命中**（声明/实现/调用点三处），成立。
- 假设 H2：枚举 14 条 + `PARAM_COUNT` + 三 API 落地，且表条目与枚举一一对应 → 读 `rdb-config.h`/`rdb-config.c` 确认 `g_param_table[PARAM_COUNT]` 指定初始化器、`config_param_table()` 返回 `*count == PARAM_COUNT`，成立。
- 假设 H3：dump 适配新结构、行式含 desc/current 且有独立行为实证 → `config_dump_params` 实现存在，param_registry_test 的 `dump_format`/`dump_current_defaults_clean`/`small_buffer_safe` 三项实证通过，成立。
- 假设 H4：测试覆盖完整性且零回归 → 本阶段独立实跑 `param_registry_test` 得 **8 passed, 0 failed**（覆盖 ID↔表一致性、四层优先级、env fail-closed -1、默认值分裂、dump 格式、小缓冲边界）；全量 45/45 沿用 Do 提交记录（工作区自提交后无改动，git status 干净，可复现），成立。

## 分析
- **AC-1** ✅ 源码 `sec_resolve_int/bool/str` 符号声明/实现/调用点三处零残留（grep 全仓库 `*.c/*.h/*.cpp` 0 命中）；仅 `rdb_config_test.c:384` 注释含字面 `sec_resolve_*` 文本（迁移说明，非符号残留，见适用边界）。（check-verify-evidence / refactor-evidence）
- **AC-2** ✅ 枚举 14 条 + `PARAM_COUNT` 哨兵；`g_param_table[PARAM_COUNT]` 指定初始化器；`table_matches_enum` 断言 `count==PARAM_COUNT` 通过。（refactor-evidence / check-verify-evidence）
- **AC-3** ✅ `config_dump_params` 行首 `[section]key`，含 type/default/desc/current；`dump_format`/`dump_current_defaults_clean` 实证输出格式正确，`name=` 字段已废除。（refactor-evidence / check-verify-evidence）
- **AC-4** ✅ `param_registry_test` 重写 8 用例全过；监控分层语义测试已迁 `sec_get_*` 形式；全量 `xmake test 45/45 passed` 零回归。（refactor-evidence / check-verify-evidence）

## 失败原因
无（结论成立，非 rejected/partial）。

## 适用边界
1. **注释字面残留（known-note，非违反）**：`libs/tests/rdb_config_test.c:384` 注释含字面 `sec_resolve_*` 文本（`/* sec_resolve_* 签名移除；层序覆盖已由上方断言验证） */`），其为迁移说明性注释，并非符号/调用点残留，不违反 AC-1 实质。但 Do 证据 `t3979-refactor-evidence.md` 第 7 行"注释历史提法已同步更新为 sec_get_*"措辞与事实有偏差——该处注释未同步。Check 阶段不改代码；若要求字面零残留，可在 Act/跟进中清理该注释文字。
2. **全量实证边界**：本轮对直接相关的 `param_registry_test` 做了独立实跑（8/8）；全量 45/45 沿用 Do 提交记录（工作区干净、可复现）。如需更强保证，可在 Act 前补跑全量 `xmake test`。
3. **范围外保持**：reload 链路修复、rpc show 集成、tls_algorithm 默认值分裂语义裁决均按 PRD 范围外处理，未触及。

## 下一轮建议
- 跟进清理 `rdb_config_test.c:384` 注释字面，使字面 grep 亦零残留（可选，纯卫生）。
- 将"枚举 ID 编译期绑定消灭参数身份漂移"的范式沉淀为 ADR，供后续配置类重构复用（见 Act 知识处置）。
- 既有测试已全绿，无需回归补丁；可推进归档。

## Verdict
- outcome: confirmed
- reason: AC-1~AC-4 全部成立（源码 sec_resolve_ 符号零残留 / 枚举14条+三API落地 / dump适配实证 / param_registry_test 8/8 + 全量45/45 零回归）；用户确认进入 Act 归档。
- verdict_id: T3979-verdict-confirmed-20260826
- at: 2026-08-26T16:35:00+08:00
