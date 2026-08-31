# 优化 rdb-cfg gen 显示参数可选值与值范围

## 背景

`xmake run rdb-cfg gen` 当前按 `libs/rdb-config.c:g_cfg_keys[]` 生成 `rdb.cfg` 模板，仅显示 `desc`、回退关系与 `def`/`required`，未展示参数的取值约束。运维需查源码才能得知 `bool` 仅 `0/1`、`int` 的 `[min,max]`、`tls_algorithm` 的算法枚举、`cert_dir` 的长度限制等，导致可用性差。

`g_cfg_keys` 已携带完整约束（`type`/`restrict_range`/`min`/`max`/`maxlen`/`invalid_policy`），`hs_algorithm_from_name` 定义 `tls_algorithm` 的合法集（`common.h:15-16`：`TLS_SM4_GCM_SM3` / `TLS_AES_256_GCM_SHA384`）。`gen` 应就地展示这些约束，使模板自解释。

## 目标

增强 `rdb-cfg/cli.c:cmd_gen`（`rdb-cfg gen`），对每个 `[section]key` 在注释中展示其可选值/值范围，且不破坏现有模板的机器可读性（`key=value` 行保持不变）。

## 验收标准

- [ ] AC-1：`BOOL` 类型在 `gen` 注释中显示 `可选值: 0=关闭, 1=开启`（通用，`allowed_values` 含值含义；与 `sec_get_bool` 的 fail-closed 语义一致）
- [ ] AC-2：`INT` 类型在 `gen` 注释中显示 `值范围: [min, max]`（`restrict_range=1` 时；否则不额外显示）；`min/max` 取自 `g_cfg_keys[].min/max`（如 `fsdeamon keepalive [0, LONG_MAX]`、`fsclient read_timeout [1, LONG_MAX]` 等，当前共 19 个 INT 项）
- [ ] AC-3：`tls_algorithm` 等枚举 `STR` 在 `gen` 注释中显示 `可选值: TLS_SM4_GCM_SM3=国密SM4-GCM-SM3(TLS1.3), TLS_AES_256_GCM_SHA384=AES256-GCM-SHA384(国际/TLS1.3)`（通用 `allowed_values` 含值含义，来源 `g_cfg_keys[].allowed_values`，与 `hs_algorithm.c` 精确匹配集一致；新增枚举仅需在 `g_cfg_keys` 填该字段，无需改 `cli.c`）
- [ ] AC-4：`STR` 类型中 `cert_dir` 等含 `maxlen>0` 的项显示 `最大长度: N`（如 `cert_dir 4095`）；其余 STR 无约束时不额外显示
- [ ] AC-5：`check`/`dump` 不回归；`gen` 生成的 `key=value` 行与既有模板行对行一致（仅注释新增），`xmake run rdb-cfg gen` 人工抽样与 `cli_test` 自动化回归通过

### 声明的测试接缝

- `libs/tests/rdb_config_test.c` 与 `rdb-cfg/cli_test.c` 可回归 `gen` 输出（字符串包含断言）
- `xmake run rdb-cfg gen` → 人工核对 `tls_enable`/`keepalive`/`tls_algorithm`/`cert_dir` 四类代表的注释
- `xmake test` 全量

## 非目标

- 不修改 `g_cfg_keys` 的约束值本身（仅为枚举项新增 `allowed_values` 含含义描述，约束值校验仍以 `hs_algorithm.c`/`sec_test_*` 为准）
- 不为 `tls_algorithm` 增加超出 `hs_algorithm_from_name` 的新枚举校验（展示与运行时校验保持单一来源 `hs_algorithm.c`）
- 不改变 `gen -o` 的文件写入路径与权限逻辑

## 关联本体节点

```
ontology:concept/pdca-task
ontology:entity/rdb-config
```

## 风险

- 注释行仅新增 `;`-前缀行，不影响 `ini_parse`；`dump`/`check` 的值校验逻辑不动，回退分支保持 `fail-closed`
