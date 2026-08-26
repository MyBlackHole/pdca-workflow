# T3979 Check 阶段独立复核实证

复核时间：2026-08-26T16:20+08:00（Do 提交 6ce5f85a 之后，工作区 git status 干净）

## 方法
- 源码符号残留核查：`grep -r '\bsec_resolve_(int|bool|str)\b'` 于全仓库 `*.c/*.h/*.cpp`（排除 build/ 二进制产物）
- 解析链 API 落地核查：直接读取 `libs/rdb-config.h` 与 `libs/rdb-config.c`
- 行为实证：实跑 `xmake run param_registry_test`（非仅沿用 Do 记录）

## 结果
- **AC-1 符号残留（实质）**：`sec_resolve_int/bool/str` 函数符号在全部源码中 **0 命中**（声明/实现/调用点三处均零残留）。✅
- **AC-2 枚举与表**：`config_param_id_t` 枚举 14 条 + `PARAM_COUNT` 哨兵；`g_param_table[PARAM_COUNT]` 指定初始化器；`sec_get_int/bool/str(id)` 三 API 声明与实现到位。✅
- **AC-3 dump**：`config_dump_params` 实现存在，行首 `[section]key`，含 type/default/desc/current（由 param_registry_test 实证）。✅
- **AC-4 测试**：`xmake run param_registry_test` 实测 **8 passed, 0 failed**：
  `table_matches_enum / sec_get_layer_order / sec_get_bool_fail_closed /
  sec_get_str_defaults / shared_chain_consistency / dump_format /
  dump_current_defaults_clean / small_buffer_safe`。覆盖 ID↔表一致性、四层优先级、env fail-closed -1、默认值分裂、dump 格式、小缓冲边界。✅

## 偏差修正（对 Do 证据措辞的校正）
Do 证据 `t3979-refactor-evidence.md` 第 7 行称"注释历史提法已同步更新为 sec_get_*"，
但实测 `libs/tests/rdb_config_test.c:384` 注释仍含字面 `sec_resolve_*` 文本：
`/* sec_resolve_* 签名移除；层序覆盖已由上方断言验证） */`
该文本为**迁移说明性注释**（说明此测试块取代旧 sec_resolve 测试），并非符号/调用点残留，
不违反 AC-1 实质。但 Do 证据"注释已全同步"的措辞与事实有偏差——此处注释未同步为 sec_get_* 字面。

处置建议（Check 不改动代码，留待 Act/跟进）：在结论 known-note 标注；若要求字面零残留，
可在后续清理该注释文字。

## 全量 45/45 零回归
沿用 Do 提交（6ce5f85a）记录之全量 `xmake test 45/45 passed`（工作区自提交后无改动，git status 干净，结果可复现可信）。本轮额外对直接相关测试 param_registry_test 做了独立实跑实证。
