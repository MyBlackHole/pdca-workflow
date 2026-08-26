# rdb-config 解析链路重构：枚举参数 ID + sec_get_* 单参 API

## 问题陈述（承 T3978 用户反馈）

1. `config_param_desc_t.name` 冗余——身份应由解析链自身表达
2. `g_config_param_table` 未接入解析流程——注册表是与 sec_resolve 脱节的死数据，漂移只能靠测试事后发现

用户裁定：方案丙·一次到位——枚举参数 ID + `sec_get_*(id)` 单参 API + 全部调用点迁移 + 旧 API 移除。

## 方案

### 新接口（libs/rdb-config.h）

```c
typedef enum {
    PARAM_AUDIT_ENABLED,          /* AUDIT_ENABLE > [security]audit_enable > [auth]enable > 0 */
    PARAM_AUTH_KEYCHECK_ENABLED,  /* AUTH_ENABLE > [security]auth_enable > [auth]enable > 0 */
    PARAM_CERT_DIR,               /* RPC_TLS_CERT_DIR > [security]cert_dir > DEFAULT_CERT_DIR */
    PARAM_SBT_MTLS_ENABLED,       /* SBT_MTLS_ENABLE > [security]tls_enable > 0（dmsbtex/libobk 共用）*/
    PARAM_SBT_TLS_ALGORITHM,      /* SBT_TLS_ALGORITHM > [security]ciphersuites > NULL（dmsbtex/libobk.srv 共用）*/
    PARAM_LIBOBK_CLI_TLS_ALGORITHM, /* 同上但 default=SM4_GCM_SM3（既有分裂如实登记）*/
    PARAM_AIO_SPEEDD_MTLS_ENABLED,
    PARAM_AIO_SPEEDD_TLS_ALGORITHM,
    PARAM_AIO_SPEED_MTLS_ENABLED,
    PARAM_AIO_SPEED_TLS_ALGORITHM,
    PARAM_RDBCOMMD_MTLS_ENABLED,
    PARAM_RDBCOMMD_TLS_ALGORITHM,
    PARAM_RDBCOMM_MTLS_ENABLED,
    PARAM_RDBCOMM_TLS_ALGORITHM,
    PARAM_COUNT
} config_param_id_t;

int         sec_get_int(config_param_id_t id);
int         sec_get_bool(config_param_id_t id);
const char *sec_get_str(config_param_id_t id);
```

### 条目粒度裁定

**解析链完全一致即合并**：dmsbtex/libobk.srv/libobk.cli 的 mtls 链相同 → 合并 `PARAM_SBT_MTLS_ENABLED`；dmsbtex/libobk.srv 的 algorithm 链相同 → 合并；libobk.cli 因 default 不同独立。最终 **14 条**（原 17 条去重）。表按枚举索引 O(1) 定位，条目含完整链信息（env/layer2/layer3/fallback/type/def/desc）。

### 迁移清单（30 处调用点 → 6 模块）

- libs: logger.c:119 · timed_key.c:227
- rpc: rpc-client.cpp×3 · rpc-config.cpp×7
- dmsbtex: network.c×3
- libobk: oracleCmdTbl.c×3 · libobk.c×3
- rdbcomm: rdbcommd-main.c×5 · rdbcomm-main.c×3

### 删除项

`sec_resolve_int/bool/str` 声明与实现全删；`config_param_find(name)/config_dump_params 旧签名`适配新结构（find 改双参 section+key 或删除视测试需要）。

## Seam 分析

development 场景 TDD。

### 声明的测试接缝

- seam: libs/tests/param_registry_test.c -> libs/rdb-config.c

## 范围外

reload 链路修复；rpc show 集成；tls_algorithm 默认值分裂的语义裁决（重构仅如实保留各条目现状 def）。

## 验收标准

- [ ] AC-1: 全仓库 `sec_resolve_` 符号零残留（grep 验证声明/实现/调用点三处）
- [ ] AC-2: 枚举 + 表 + 三 API 落地；表条目 14 条且与枚举一一对应（静态断言或测试断言 PARAM_COUNT 一致）
- [ ] AC-3: dump 接口适配新结构并保持 key=value 行式含 desc/current；行为经独立编译实证
- [ ] AC-4: param_registry_test 重写覆盖完整性（ID↔表一致性、层序、fail-closed -1 可视化、边界），xmake test 全量通过且既有测试零回归
