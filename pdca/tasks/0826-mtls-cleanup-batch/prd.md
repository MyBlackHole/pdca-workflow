# mTLS 改进批量实施（T3965 分析落地）

## 问题

T3965 mTLS 整体分析确认的改进项 + 用户补充的 sec_resolve 重复解析问题：

1. **P1**：客户端 ctx 缓存（ccache）64 槽耗尽后返回 `TLS_CERT_ERR_SSL_CREATE`（语义误导），且无淘汰——第 65 种 (cert_dir,algorithm,ca_cn) 组合起永久失败。
2. **S1/C3**：四模块 config init 的算法解析块完全同构（sec_resolve NULL 默认 + CLI 覆盖 + 白名单校验 + from_name，各约 20 行）；sec_resolve 6 参数签名冗长。
3. **C1**：跨层 key 名不一致——mtls 工具层="mtls_enable"/全局层="tls_enable"；算法工具层="tls_algorithm"/全局层="ciphersuites"。
4. **C2**：SBT_MTLS_ENABLE_ENV/SBT_TLS_ALGORITHM_ENV 在 dmsbtex/network.h 与 libobk/oracleCmdTbl.h 双定义。
5. **用户补充**：`sec_resolve_int(SEC_GLOBAL_SECTION, SEC_GLOBAL_AUDIT_KEY, SEC_MASTER_SECTION, SEC_MASTER_ENABLE_KEY, AUDIT_ENABLE_ENV, 0)` 每次调用重复执行 getenv+锁+线性查找。已核实配置 store 有内存缓存（T0369 双缓冲）非重读文件，属重复解析模式问题。

## 方案

### A. P1 — ccache LRU 淘汰 + 专用错误码

- tls_cert.h 新增 `TLS_CERT_ERR_CCACHE_FULL -8`
- ccache entry 增加 `last_used`（CLOCK_MONOTONIC）；acquire 命中/新建刷新
- 满 64 时淘汰 refcount==0 中 last_used 最旧者；全部 refcount>0 才返回 CCACHE_FULL

### B. S1+C3 — 算法解析归一 libs

libs/hs_algorithm.c 新增单一实现：

```c
/* 返回 >0=显式配置的算法ID(服务端应锁定)；0=未设置不锁；-1=非法 fail-closed */
int hs_algorithm_config_resolve(const char *cli_algorithm,
                                const sec_spec_t *spec);
```

四模块 config init 迁移调用，删除各自同构块（含白名单校验，内部完成）。

### C. C3 — spec 化签名

rdb-config.h 新增：

```c
typedef struct {
	const char *tool_section; const char *tool_key;
	const char *global_section; const char *global_key;
	const char *env_name;
} sec_spec_t;
int sec_resolve_bool_spec(const sec_spec_t *spec, int default_val);
const char *sec_resolve_str_spec(const sec_spec_t *spec, const char *default_val);
```

旧 6 参接口保留（兼容既有调用点）；四模块 mtls/algorithm 解析点迁移至 spec 变体。

### D. C1 — 全局层 key 别名映射

rdb-config.c 新增集中别名表（global 层查找 miss 时双向回退）：
- `tls_enable` ↔ `mtls_enable`
- `ciphersuites` ↔ `tls_algorithm`

新代码统一使用规范名 mtls_enable/tls_algorithm；旧配置文件无需修改。

### E. C2 — SBT_* 宏归一

SBT_MTLS_ENABLE_ENV/SBT_TLS_ALGORITHM_ENV 定义迁至 libs/common.h（HS_ERR/HS_ALG 同址）；dmsbtex/network.h 与 libobk/oracleCmdTbl.h 删除本地定义。

### F. 重复解析 — spec 缓存变体 + 策略开关一次性解析

- 新增 `sec_resolve_bool_spec_cached()`：首次解析后缓存于静态 slot，`parse_config()` 成功与 `sec_cache_invalidate()` 时自动失效——策略类开关（audit/auth 等）生命周期不变场景零重复解析
- logger.c init_audit_logger、timed_key.c auth 检查迁移至 cached 变体

## 用户故事

1. 作为维护者，我希望新增服务端工具时算法/mTLS 配置解析只需一行调用而非复制 20 行同构代码。
2. 作为库使用者，ccache 耗尽时得到准确错误码且低引用组合自动淘汰。
3. 作为运维，旧 ini 配置（tls_enable/ciphersuites key）在新版本继续生效。

## Seam 分析

### 声明的测试接缝

- seam: libs/tests/rdb_config_test.c -> ../rdb-config.c
- seam: libs/tests/hs_err_test.c -> ../hs_algorithm.c
- seam: libs/tests/tls_cert_test.c -> ../tls_cert.c
- seam: rpc/tests/mixed_mtls_integration.cpp -> ../rpc-server.cpp
- seam: libobk/test/session_test.c / dmsbtex/test/session_test.c -> 各模块实现

## 测试决策

- rdb_config_test 新增：key 别名双读、spec 接口、cached 失效行为。
- hs_err_test 扩展：hs_algorithm_config_resolve 的 CLI/env/ini/未设置/-1 五分支。
- tls_cert_test 新增：ccache 填满淘汰与 CCACHE_FULL 行为。
- 回归：mixed_mtls_integration AC1-9、三模块 session_test、e2e 19 场景全过（锁定/别名兼容证明）。

## 验收标准

- [ ] AC-1: ccache 用满后 acquire 第 65 种组合在存在零引用条目时成功（LRU 淘汰），全部占用时返回 TLS_CERT_ERR_CCACHE_FULL；tls_cert_test 用例通过。
- [ ] AC-2: 四模块 config init 不再包含同构算法解析块，均调用 hs_algorithm_config_resolve；mixed_mtls_integration 与三 session_test 锁定用例回归通过。
- [ ] AC-3: 旧 key 配置（[security] tls_enable / ciphersuites）与新 key（mtls_enable / tls_algorithm）等效生效，rdb_config_test 别名用例通过。
- [ ] AC-4: SBT_* 宏仅在 libs/common.h 定义，dmsbtex/libobk 为引用；全量构建通过。
- [ ] AC-5: cached 变体：二次调用不再触发 getenv/store 查找（以失效计数或插桩验证），parse_config 后缓存失效重新解析；logger/timed_key 迁移后回归通过。
- [ ] AC-6: e2e 场景矩阵 19/19 全过。

## 范围外

- server_serve 决策树抽纯函数（S2，需单独评审）
- hs_session 三套抽象归一（收益低于成本）
- ini 文件格式变更
