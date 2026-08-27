# PRD — 清理 rdb-config.c 多余代码

## 背景
T3979 将解析链路重构为 `sec_get_*(id)` + 枚举注册表后，`libs/rdb-config.{c,h}`
与 `libs/tests/param_registry_test.c` 中仍存在重构前的遗留噪声，叠加 2026-08-26
架构评审发现的设计冗余：
1. `config_param_desc_t.owner` 字段——定义存在、14 条表数据已填（如 `"shared"`），
   但 `sec_walk_*` 与 `config_dump_params` 从不读取，仅 `param_registry_test.c:71`
   做非空断言，属纯死字段。
2. `rdb-config.c:259` `/* ---- T3978 参数注册表本体 ---- */` banner 下方无任何代码，
   为空遗留注释。
3. `rdb-config.h:105` 注释称"完整复刻 sec_resolve 四层解析链"，已失实。
4. `config_get_int_env`（声明 header:83-94，定义 c:122-137）全仓库 0 调用（含测试），为死函数。
5. `config_set_string` 写 API 生产 0 调用，仅测试夹具用（rdb_config_test.c:219/226），与 4 同类死 API。
6. `_kv_stores[2]` 双缓冲在 rdb-config 中仅启动时翻转一次：rdb-config 无运行时重载路径
   （daemon 的 `reload_config` 重载的是 fsdeamon/rpc 各自配置），双缓冲原子热重载能力从未被使用，属过度设计。
7. `config_get_string` 内含全局 section 回退分支（T0369 F4），由 `config_set_global_fallback`
   开启，而全仓库仅测试调用该开启函数 → 生产死逻辑；回退/优先级概念被拆成两套机制
   （全局回退 + `sec_walk_*` 层链），应统一为 `g_param_table` 驱动的单一层链。

## 清理范围（项 A–G）
- A：删除 `config_param_desc_t.owner` 死字段（struct 定义、14 处表条目首字符串字面量、param_registry_test.c:71 断言）。
- B：删除 `rdb-config.c:259` 空 T3978 banner 注释。
- C：更新 `rdb-config.h:105` 过时注释为实际 env>layer2>layer3>def 四层模型描述。
- D：`config_get_int_env` 死函数处置（全仓库 0 调用，含测试）——公开 API，建议删除（0 生产调用，安全）。
- E：`config_set_string` 死写 API 处置（生产 0 调用，仅测试夹具）——删除声明/定义及测试夹具调用，测试改用构造含目标键的 ini + parse_config。
- F：`_kv_stores[2]` 双缓冲简化为单一 `config_kv_store`：删 `config_index` / `tmp_index` 翻转逻辑，`get_config_store()` 返回单例。
- G：解析/取值完全由 `g_param_table` 驱动：删除 `config_get_string` 中的全局 section 回退分支（`config_set_global_fallback` 声明/定义、`g_allow_global_fallback`），使每个逻辑参数唯一走 `g_param_table` 条目的 env>layer2>layer3>def 层链；`config_get_string` 仅保留为表驱动 walker 内部的纯 `(section,key)` 访问器。`config_get_string_global_fallback` 测试相应删除。

## 设计原则（终态）
**解析/取值完全由 `g_param_table` 单一驱动。**
- F 把 `_kv_stores[2]` 收敛为单一原始数据存储（仅承载 ini 解析后的 (section,key,value)）。
- G 把 `config_get_string` 收敛为表驱动 walker 内部的纯 `(section,key)` 访问器（无全局回退）。
- 最终唯一的值解析路径为 `sec_get_*(id)` → 按 `g_param_table[id]` 的层链
  （env>layer2>layer3>def）在单 store 上求值；不再存在任何绕过 `g_param_table` 的 generic 全局回退机制。

## 验收标准
- [ ] AC-1: owner 字段全仓库零引用（grep config_param_desc_t 上下文无 .owner/->owner 读取）
- [ ] AC-2: xmake build + xmake test 全绿，param_registry_test 层序/一致性断言保持
- [ ] AC-3: config_get_int_env 已删除或保留（按处置决断），全仓库 0 调用
- [ ] AC-4: 空 banner 与过时 sec_resolve 注释清除，无残留误导
- [ ] AC-5: config_set_string 已删除（声明+定义+测试夹具同步移除）且 0 生产调用
- [ ] AC-6: _kv_stores 简化为单 store 后 xmake 全量测试零回归；get_config_store() 返回稳定单例，sec_walk_* 取值路径不变
- [ ] AC-7: config_get_string 无 g_allow_global_fallback / config_set_global_fallback 引用，单测相应移除，优先级机制唯一

## 影响与风险
低。A/B/C/G 删死字段/死分支不改变任何运行时行为；D/E 死函数/死 API 全仓库 0 生产调用，
删除安全（若作为对外库接口则需 CHANGELOG 标注）。F 仅简化内部存储结构，
`get_config_store()` 返回单例、`sec_walk_*` 取值路径签名不变，无行为变化。
风险点在于 `config_get_int_env` / `config_set_string` 若被本仓库外消费者依赖——已确认本仓库内零引用。

## 测试策略
依赖既有 `param_registry_test` 与全量 `xmake test` 作为回归护栏。
E 移除 `config_set_string` 后，`rdb_config_test` 相关用例改用构造含目标键的 ini + `parse_config`；
G 移除全局回退分支后，`config_get_string_global_fallback` 测试相应删除。整体清理不改变运行时行为。
