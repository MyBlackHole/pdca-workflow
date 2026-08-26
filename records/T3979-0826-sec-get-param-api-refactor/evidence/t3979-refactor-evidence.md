# T3979 重构实施证据

## 提交
6ce5f85a（18 files: +369/-646 净删 277 行）

## AC 断言（Check 独立复核口径）
- AC-1 ✅ grep sec_resolve_ 全仓库（libs/rpc/dmsbtex/libobk/rdbcomm/fs-backup）零代码符号残留；注释历史提法已同步更新为 sec_get_*
- AC-2 ✅ 枚举 14 条目 + PARAM_COUNT 哨兵；g_param_table[PARAM_COUNT] 指定初始化器；table_matches_enum 断言 count==PARAM_COUNT
- AC-3 ✅ dump 行首 [section]key（独立 gcc+inih 静态库链接实证输出：static_len=1720/values_len=1938，[security]audit_enable 等行格式正确）
- AC-4 ✅ param_registry_test 重写 8 用例（层序四级/env fail-closed/默认值/一致性/dump/小缓冲）；rdb_config_test 三处分层语义测试迁移 sec_get_* 形式；全量 45/45 passed

## TDD/实施轨迹
红灯①枚举未定义 → 头文件 → 红灯②链接失败 → 实现 → 实施缺陷修复三连：
sec_parse_strict_bool 误删恢复、got maybe-uninitialized 初始化、双逗号（正则替换边界）
dmsbtex/main.c 与 libobk/main.c 补 rdb-config.h 包含（宏单一来源后传递依赖显式化）
