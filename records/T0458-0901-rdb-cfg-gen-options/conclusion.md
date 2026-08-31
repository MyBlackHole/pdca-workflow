# T0458 结论

## 逐项核验

- AC-1 BOOL 可选值 0=关闭,1=开启（含含义） — 通过
  - 证据 ev-gen: gen_output.conf 含 `; 可选值: 0=关闭, 1=开启`（如 `[security]audit_enable`、`tls_enable` 等 20+ BOOL 项均展示）
  - 证据 ev-diff: cli.c 通用分支 `type==CFG_TYPE_BOOL` 回退 `0=关闭,1=开启`，`rdb-config.h` 注释说明通用语义
  - 通用性：不再针对特定 key 硬编码，新增 BOOL 无需改 cli.c

- AC-2 INT 值范围 [min,max] — 通过
  - 证据 ev-gen: 如 `keepalive ; 值范围: [0, 9223372036854775807]`、`read_timeout ; 值范围: [1, ...]` 等 19 个 INT 项均展示
  - 证据 ev-diff: cli.c 基于 `restrict_range/min/max` 通用展示

- AC-3 tls_algorithm 枚举含含义（通用 allowed_values） — 通过
  - 证据 ev-gen: 8 个 `tls_algorithm` 均显示 `; 可选值: TLS_SM4_GCM_SM3=国密SM4-GCM-SM3(TLS1.3), TLS_AES_256_GCM_SHA384=AES256-GCM-SHA384(国际/TLS1.3)`（值+含义）
  - 证据 ev-diff: `rdb-config.h` 新增 `allowed_values` 通用字段（含含义描述），`g_cfg_keys` 8 处 `tls_algorithm` 均填充该字段，`cli.c` 仅 `if (allowed_values) print` 无业务 key 硬编码，新增枚举只需改 `g_cfg_keys`，与 `hs_algorithm.c` 校验集一致

- AC-4 STR maxlen 最大长度 — 通过
  - 证据 ev-gen: `cert_dir ; 最大长度: 4095` 等含 `maxlen>0` 的 STR 项展示

- AC-5 gen 兼容且回归通过 — 通过
  - 证据 ev-test: test.log `xmake test 51/51 passed`
  - 验证：`gen -o /tmp/rdb_gen2.conf` 后 `check`/`dump` 正常解析（注释 `;` 被 `ini_parse` 忽略），`key=value` 行保持不变

## 判定

- verdict: confirmed
