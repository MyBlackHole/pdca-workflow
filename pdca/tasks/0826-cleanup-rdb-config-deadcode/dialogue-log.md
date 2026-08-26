# Dialogue Log — 清理 rdb-config.c 多余代码

## 2026-08-26 Plan
- 审计发现：owner 死字段（param_registry_test.c:71 读取）、config_get_int_env 死函数（0 调用）、空 T3978 banner、sec_resolve 过时注释。
- 待用户决断：config_get_int_env（公开 API）是否一并删除。
