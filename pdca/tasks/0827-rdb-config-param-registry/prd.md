# 跟进：rdb-config 集中式参数注册表改造

## 问题陈述（承 T3977 §5）

rdb config 参数定义散落三处（rdb-config.h 宏 / rpc MATCH 硬编码 / 调用点实参），show 仅覆盖 8/20+ 字段且 sec 层键零展示，无文档——运维与开发者无法得知"有哪些参数、什么含义、当前生效值"。根因：无单一参数注册表。

## 方案

在 `libs/rdb-config.{c,h}` 建立集中式参数注册表（TDD）：

### 数据结构

```c
typedef enum { CFG_TYPE_INT, CFG_TYPE_BOOL, CFG_TYPE_STR } config_param_type_t;

typedef struct {
    const char *display;   /* 展示名 "security.tls_enable" */
    const char *section;   /* ini section */
    const char *key;       /* ini key */
    config_param_type_t type;
    const char *env_name;  /* 第1层 env（可 NULL）*/
    const char *def;       /* 默认值字符串 */
    const char *desc;      /* 一句话说明 */
} config_param_desc_t;

const config_param_desc_t *config_param_table(int *count);
int config_dump_params(char *buf, int len, int with_values);
/* with_values=0: 五元组清单（即文档）；=1: 追加当前 sec_resolve 生效值 */
```

### 注册表条目（首版 8 键，源自 T3977 盘点）

security.tls_enable(B)、security.auth_enable(I)、security.audit_enable(I)、security.ciphersuites(S)、security.cert_dir(S)、auth.enable(I)、tool.mtls_enable(B)、tool.tls_algorithm(S)——tool section 因工具而异，条目标注该事实，解析时仍由调用方传具体 section。

### 设计边界

- **不改动 30+ 现有 sec_resolve 调用点**（风险控制）；以一致性测试防漂移：断言注册表 section/key 与 rdb-config.h 的 SEC_* 宏逐一相符。
- **不含 reload 修复**（后续任务）；rpc 业务 7 键迁移列为范围外（评估后另行任务）。
- show 全量输出供 rpc_show_config 后续集成（本任务交付库级接口 + 测试，rpc 集成接口预留）。

## Seam 分析

development 场景 TDD：先写失败测试再实现。

### 声明的测试接缝

- seam: libs/tests/param_registry_test.c -> libs/rdb-config.c

## 范围外

reload 链路修复；rpc 业务键迁移进注册表；30+ 调用点改造；文档自动生成脚本（dump 即文档）。

## 验收标准

- [ ] AC-1: 注册表落盘——`config_param_desc_t` 结构 + 8 个安全键条目（含 type/env/default/desc 五类信息）
- [ ] AC-2: `config_dump_params(buf,len,0)` 输出全部 8 键五元组清单；`(buf,len,1)` 附每键当前生效值（store/env 未配置时显示默认值）
- [ ] AC-3: 一致性防漂移测试——注册表条目与 rdb-config.h SEC_* 宏逐一断言相等，人为篡改任一处测试失败
- [ ] AC-4: `xmake test` 全绿——新增 param_registry_test/default 接入且原 44 条零回归
