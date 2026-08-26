# T3978 实施证据

## 提交
e7878e78【F-139】rdb-config: 参数注册表落地（6 文件：rdb-config.h/.c 追加、network.h 与 oracleCmdTbl.h 删双定义、tests/xmake.lua 接入、param_registry_test.c 新增）

## TDD 轨迹
红灯① gcc -fsyntax-only: config_param_desc_t 未定义 → 红灯② 编译过链接失败 → 实现 → 实施中修复两缺陷（格式串占位符不匹配 -Werror 捕获；small_buffer 用例暴露 truncated 分支未累计长度）→ 全绿

## AC 断言
- AC-1 ✅ config_param_desc_t 九字段 + 17 条目落盘（git show e7878e78 -- libs/rdb-config.h libs/rdb-config.c）
- AC-2 ✅ dump 双模式测试通过（dump_static_format/dump_current_* 五用例）
- AC-3 ✅ registry_matches_macros 按 name 定位断言宏一致（含全 mtls 层共享键遍历）
- AC-4 ✅ xmake test 全量 45/45 passed（原 44 零回归），param_registry_test/default 单独可跑

## 附带收益
SBT_MTLS_ENABLE_ENV/SBT_TLS_ALGORITHM_ENV 宏双定义收敛至 rdb-config.h 单一来源（T3975 登记项闭环）
