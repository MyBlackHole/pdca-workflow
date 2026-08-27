# Dialogue Log — 清理 rdb-config.c 多余代码

## 2026-08-26 Plan
- 审计发现：owner 死字段（param_registry_test.c:71 读取）、config_get_int_env 死函数（0 调用）、空 T3978 banner、sec_resolve 过时注释。
- 待用户决断：config_get_int_env（公开 API）是否一并删除。

## 2026-08-26 架构评审（并入 E/F/G）
- 用户质疑 rdb-config 复杂度，逐层核查后三项结论并入 cleanup：
  - E（config_set_string 死写 API）：全仓库生产 0 调用，仅 rdb_config_test.c:219/226 作夹具。用户决断：并入（加项 E）。
  - F（_kv_stores[2] 双缓冲过度设计）：rdb-config 的 parse_config 仅由 rdb_auto_init 构造器于启动时执行一次，无运行时重载路径（daemon reload_config 重载的是 fsdeamon/rpc 各自配置）。用户决断：并入（加项 F）。
  - G（config_get_string 死全局回退分支）：config_set_global_fallback 全仓库仅测试调用，生产死逻辑；回退/优先级应统一为 g_param_table 驱动的单层链。用户决断：并入（首个"冗余/复杂度收敛"议题，加项 G）。
- 注：双缓冲模式在 rpc/fs-backup/fsdeamon/s3tools 因有运行时 reload 而保留；仅 rdb-config 属照搬。
- 用户明确设计原则：**解析/取值完全由 g_param_table 单一驱动**。已据此固化：
  F 把 _kv_stores[2] 收敛为单 store（原始数据），G 把 config_get_string 收敛为表驱动
  walker 内部的纯 (section,key) 访问器（无全局回退）；终态唯一路径为
  sec_get_*(id) → g_param_table[id] 层链（env>layer2>layer3>def）在单 store 求值。
  该原则写入 prd.md「设计原则（终态）」与 task.json 项 G。
