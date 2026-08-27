# T3984 Do 阶段验证证据

任务：0826-cleanup-rdb-config-deadcode（rdb-config.c 多余代码清理 A–G）
阶段：do（实现 + 验证）
验证时间：2026-08-26

## 改动摘要（libs/rdb-config.c / rdb-config.h / tests）
- A：删除 `config_param_desc_t.owner` 死字段（struct 定义 + 14 条表条目首字面量 + param_registry_test.c:71 断言）。
- B：删除 `rdb-config.c` 空 T3978 banner 注释。
- C：更新 `rdb-config.h` 两处过时/重复注释（sec_resolve 四层描述 → 实际 env>layer2>layer3>def 模型）。
- D：删除死函数 `config_get_int_env`（全仓库 0 调用，含测试）。
- E：删除死写 API `config_set_string`（生产 0 调用，仅测试夹具）+ 其测试。
- F：`_kv_stores[2]` 双缓冲简化为单 `_kv_store`；移除 `config_index`/`g_cfg_lock` 及原子切换逻辑，`get_config_store()` 返回单例，`parse_config` 直写单 store。
- G：删除 `config_get_string` 的全局 section 回退分支（`config_set_global_fallback`/`g_allow_global_fallback`）→ 纯 (section,key) 原语；解析/取值完全由 `g_param_table` 驱动。

## 验证结果
### rdb_config_test（手动 gcc 编译 rdb-config.c + 测试）
15 passed, 0 failed
覆盖：parse/get_int/get_string、section count/entry、parse 两次、文件不存在、
init_config_from_env、trailing spaces、tool tls 隔离与优先级、bool 层语义、
audit/auth 四层、默认无全局回退、脏值回退 default。

### param_registry_test（手动 gcc）
9 passed, 0 failed
覆盖：表与枚举一致、层序、bool fail-closed、audit/auth env fail-closed、
str 默认、shared 链一致、dump 格式/默认值、小缓冲安全。

### xmake run rpc_config_test（整体项目构建回归）
4 passed, 0 failed
（xmake 全量 generate + build 无编译错误，证明 rdb-config.c 在大型项目中链接正常，
且无生产代码引用已移除的符号）

## 全仓符号核查
- 已移除符号（config_set_string / config_set_global_fallback / config_get_int_env /
  _kv_stores / config_index(in rdb-config) / g_cfg_lock / g_allow_global_fallback / owner）
  在 libs/rdb-config 与 tests 外无任何引用。
- `.owner` 残留命中均为其他模块的无关字段；`config_index` 残留为 rpc/fs-backup/s3tools
  各自的双缓冲（按设计保留，因其有运行时 reload）。
