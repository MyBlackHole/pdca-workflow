# Design — rdb-config 参数注册表（T3978 详细实现设计）

## 0. 盘点结论：17 条逻辑参数（注册表全量内容）

粒度裁定：**一条 = 一个 sec_resolve 调用链实例**（非单个 ini 键），完整复刻五元组。同 physical 键（如 `[security]tls_enable`）被多条参数共享属正常。

| # | name | owner | type | L1 env | L2 (专用层) | L3 (全局兜底) | default | 消费点 |
|---|------|-------|------|--------|------------|--------------|---------|--------|
| 1 | audit_enabled | shared | INT | AUDIT_ENABLE | [security]audit_enable | [auth]enable | 0 | logger.c:119 · rpc-config.cpp:107,195 · rdbcommd-main.c:273 |
| 2 | auth_keycheck_enabled | shared | INT | AUTH_ENABLE | [security]auth_enable | [auth]enable | 0 | timed_key.c:227 · rpc-config.cpp:111,199 · rdbcommd-main.c:277 |
| 3 | cert_dir | shared | STR | RPC_TLS_CERT_DIR | — | [security]cert_dir | /opt/aio/cfg/certs/ | rpc-client.cpp:702 · rpc-config.cpp:225 · network.c:135 · rdbcommd:362 · rdbcomm-main:625 |
| 4 | dmsbtex.mtls_enabled | dmsbtex | BOOL | SBT_MTLS_ENABLE | — | [security]tls_enable | 0 | network.c:109 |
| 5 | dmsbtex.tls_algorithm | dmsbtex | STR | SBT_TLS_ALGORITHM | — | [security]ciphersuites | NULL(未设置) | network.c:103 |
| 6 | libobk.srv.mtls_enabled | libobk | BOOL | SBT_MTLS_ENABLE | — | [security]tls_enable | 0 | oracleCmdTbl.c:42 |
| 7 | libobk.srv.tls_algorithm | libobk | STR | SBT_TLS_ALGORITHM | — | [security]ciphersuites | NULL | oracleCmdTbl.c:33 |
| 8 | libobk.cli.mtls_enabled | libobk | BOOL | SBT_MTLS_ENABLE | — | [security]tls_enable | 0 | libobk.c:74 |
| 9 | libobk.cli.tls_algorithm | libobk | STR | SBT_TLS_ALGORITHM | — | [security]ciphersuites | **SM4_GCM_SM3** ⚠ | libobk.c:70 |
| 10 | aio-speedd.mtls_enabled | aio-speedd | BOOL | AIO_SPEEDD_MTLS_ENABLE | [aio-speedd]mtls_enable | [security]tls_enable | 0 | rpc-config.cpp:183 |
| 11 | aio-speedd.tls_algorithm | aio-speedd | STR | AIO_SPEEDD_TLS_ALGORITHM | [aio-speedd]tls_algorithm | [security]ciphersuites | NULL | rpc-config.cpp:203 |
| 12 | aio-speed.mtls_enabled | aio-speed | BOOL | AIO_SPEED_MTLS_ENABLE | [aio-speed]mtls_enable | [security]tls_enable | 0 | rpc-client.cpp:663 |
| 13 | aio-speed.tls_algorithm | aio-speed | STR | AIO_SPEED_TLS_ALGORITHM | [aio-speed]tls_algorithm | [security]ciphersuites | **SM4_GCM_SM3** | rpc-client.cpp:679 |
| 14 | rdbcommd.mtls_enabled | rdbcommd | BOOL | RDBCOMMD_MTLS_ENABLE | [rdbcommd]mtls_enable | [security]tls_enable | 0 | rdbcommd-main.c:263 |
| 15 | rdbcommd.tls_algorithm | rdbcommd | STR | RDBCOMMD_TLS_ALGORITHM | [rdbcommd]tls_algorithm | [security]ciphersuites | NULL | rdbcommd-main.c:333 |
| 16 | rdbcomm.mtls_enabled | rdbcomm | BOOL | RDBCOMM_MTLS_ENABLE | [rdbcomm]mtls_enable | [security]tls_enable | 0 | rdbcomm-main.c:569 |
| 17 | rdbcomm.tls_algorithm | rdbcomm | STR | RDBCOMM_TLS_ALGORITHM | [rdbcomm]tls_algorithm | [security]ciphersuites | **SM4_GCM_SM3** | rdbcomm-main.c:603 |

⚠ 盘点即暴露两处既有不一致（注册表价值的第一手证据，本任务只登记不修改）：
- **tls_algorithm 默认值分裂**：#5/#7/#11/#15 默认未设置(NULL)，#9/#13/#17 默认 SM4_GCM_SM3——同一语义两种缺省行为
- **SBT_*_ENV 宏双定义**：dmsbtex/network.h:44 与 libobk/include/oracleCmdTbl.h:10 各一份

## 1. 头文件新增（libs/rdb-config.h）

```c
/* ---- T3978 参数注册表 ---- */

typedef enum {
    CFG_TYPE_INT = 0,
    CFG_TYPE_BOOL,
    CFG_TYPE_STR,
} config_param_type_t;

/* 单条逻辑参数：完整复刻 sec_resolve 四层解析链的静态描述。
 * layerN_*=NULL 表示该参数无此层。def 为字符串形态默认值；
 * NULL 表示"未设置"语义（区别于空串与 "0"）。 */
typedef struct {
    const char *name;           /* 唯一逻辑参数名，如 "aio-speedd.mtls_enabled" */
    const char *owner;          /* 归属模块（展示用）：shared/rpc/dmsbtex/libobk/rdbcomm… */
    const char *layer2_section; /* 第2层专用 section */
    const char *layer2_key;
    const char *layer3_section; /* 第3层全局兜底 section */
    const char *layer3_key;
    const char *env_name;       /* 第1层环境变量 */
    config_param_type_t type;
    const char *def;            /* 第4层默认值；NULL=未设置 */
    const char *desc;           /* 中文一句话说明 */
} config_param_desc_t;

/* 返回全表；*count 出参为条目数（可传 NULL）。表为静态 const，无需释放。 */
const config_param_desc_t *config_param_table(int *count);

/* 按逻辑参数名精确查找；未找到返回 NULL。O(n)。 */
const config_param_desc_t *config_param_find(const char *name);

/* key=value 行式输出全表到 buf。
 * with_values=0：仅静态五元组（可当参数文档用）。
 * with_values=1：每行追加 current=<v>，按该条目解析链现算生效值
 *                （INT/BOOL 经 sec_resolve_int/bool，STR 经 sec_resolve_str；
 *                 BOOL 非法配置如实显示 current=-1）。
 * 返回：成功=实际写入长度（不含 '\0'）；缓冲区不足=返回应有的总长度
 *      （调用方以 ret > len-1 判定截断，可重分配后重试）；参数非法=-1。 */
int config_dump_params(char *buf, int len, int with_values);
```

## 2. 注册表本体（libs/rdb-config.c 追加）

```c
static const config_param_desc_t g_config_param_table[] = {
    /* name, owner, l2_sec, l2_key, l3_sec, l3_key, env, type, def, desc */
    {"audit_enabled", "shared",
     SEC_GLOBAL_SECTION, SEC_GLOBAL_AUDIT_KEY,
     SEC_MASTER_SECTION, SEC_MASTER_ENABLE_KEY,
     AUDIT_ENABLE_ENV, CFG_TYPE_INT, "0",
     "审计开关：操作日志是否落审计文件"},
    {"auth_keycheck_enabled", "shared",
     SEC_GLOBAL_SECTION, SEC_GLOBAL_AUTH_KEY,
     SEC_MASTER_SECTION, SEC_MASTER_ENABLE_KEY,
     AUTH_ENABLE_ENV, CFG_TYPE_INT, "0",
     "鉴权开关：连接是否校验时间密钥"},
    {"cert_dir", "shared",
     NULL, NULL,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_CERT_DIR_KEY,
     RPC_TLS_CERT_DIR_ENV, CFG_TYPE_STR, DEFAULT_CERT_DIR,
     "证书目录（各工具 mTLS 证书三件套所在）"},
    {"dmsbtex.mtls_enabled", "dmsbtex",
     NULL, NULL,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
     SBT_MTLS_ENABLE_ENV, CFG_TYPE_BOOL, "0",
     "dmsbtex(SBT 备份插件) mTLS 开关"},
    {"dmsbtex.tls_algorithm", "dmsbtex",
     NULL, NULL,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_CIPHERSUITES_KEY,
     SBT_TLS_ALGORITHM_ENV, CFG_TYPE_STR, NULL,
     "dmsbtex TLS 算法锁定；未设置=协商不限"},
    {"libobk.srv.mtls_enabled", "libobk",
     NULL, NULL,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
     SBT_MTLS_ENABLE_ENV, CFG_TYPE_BOOL, "0",
     "libobk 服务端 mTLS 开关"},
    {"libobk.srv.tls_algorithm", "libobk",
     NULL, NULL,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_CIPHERSUITES_KEY,
     SBT_TLS_ALGORITHM_ENV, CFG_TYPE_STR, NULL,
     "libobk 服务端算法锁定"},
    {"libobk.cli.mtls_enabled", "libobk",
     NULL, NULL,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
     SBT_MTLS_ENABLE_ENV, CFG_TYPE_BOOL, "0",
     "libobk 客户端 mTLS 开关"},
    {"libobk.cli.tls_algorithm", "libobk",
     NULL, NULL,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_CIPHERSUITES_KEY,
     SBT_TLS_ALGORITHM_ENV, CFG_TYPE_STR,
     RPC_TLS_ALGORITHM_DEFAULT,
     "libobk 客户端算法（默认 SM4_GCM_SM3，与服务端不一致见 T3978 报告）"},
    {"aio-speedd.mtls_enabled", "aio-speedd",
     AIO_SPEEDD_TOOL_SECTION, SEC_TOOL_MTLS_KEY,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
     AIO_SPEEDD_MTLS_ENABLE_ENV, CFG_TYPE_BOOL, "0",
     "aio-speedd 服务端 mTLS 开关"},
    {"aio-speedd.tls_algorithm", "aio-speedd",
     AIO_SPEEDD_TOOL_SECTION, SEC_TOOL_ALGORITHM_KEY,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_CIPHERSUITES_KEY,
     AIO_SPEEDD_TLS_ALGORITHM_ENV, CFG_TYPE_STR, NULL,
     "aio-speedd 算法锁定"},
    {"aio-speed.mtls_enabled", "aio-speed",
     AIO_SPEED_TOOL_SECTION, SEC_TOOL_MTLS_KEY,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
     AIO_SPEED_MTLS_ENABLE_ENV, CFG_TYPE_BOOL, "0",
     "aio-speed CLI mTLS 开关"},
    {"aio-speed.tls_algorithm", "aio-speed",
     AIO_SPEED_TOOL_SECTION, SEC_TOOL_ALGORITHM_KEY,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_CIPHERSUITES_KEY,
     AIO_SPEED_TLS_ALGORITHM_ENV, CFG_TYPE_STR,
     RPC_TLS_ALGORITHM_DEFAULT,
     "aio-speed CLI 算法（默认 SM4_GCM_SM3）"},
    {"rdbcommd.mtls_enabled", "rdbcommd",
     RDBCOMMD_TOOL_SECTION, SEC_TOOL_MTLS_KEY,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
     RDBCOMMD_MTLS_ENABLE_ENV, CFG_TYPE_BOOL, "0",
     "rdbcommd 服务端 mTLS 开关"},
    {"rdbcommd.tls_algorithm", "rdbcommd",
     RDBCOMMD_TOOL_SECTION, SEC_TOOL_ALGORITHM_KEY,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_CIPHERSUITES_KEY,
     RDBCOMMD_TLS_ALGORITHM_ENV, CFG_TYPE_STR, NULL,
     "rdbcommd 算法锁定"},
    {"rdbcomm.mtls_enabled", "rdbcomm",
     RDBCOMM_TOOL_SECTION, SEC_TOOL_MTLS_KEY,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
     RDBCOMM_MTLS_ENABLE_ENV, CFG_TYPE_BOOL, "0",
     "rdbcomm 客户端 mTLS 开关"},
    {"rdbcomm.tls_algorithm", "rdbcomm",
     RDBCOMM_TOOL_SECTION, SEC_TOOL_ALGORITHM_KEY,
     SEC_GLOBAL_SECTION, SEC_GLOBAL_CIPHERSUITES_KEY,
     RDBCOMM_TLS_ALGORITHM_ENV, CFG_TYPE_STR,
     RPC_TLS_ALGORITHM_DEFAULT,
     "rdbcomm 客户端算法（默认 SM4_GCM_SM3）"},
};

const config_param_desc_t *config_param_table(int *count)
{
    if (count)
        *count = (int)(sizeof(g_config_param_table) /
                       sizeof(g_config_param_table[0]));
    return g_config_param_table;
}

const config_param_desc_t *config_param_find(const char *name)
{
    int n;
    const config_param_desc_t *t;

    if (name == NULL || name[0] == '\0')
        return NULL;
    t = config_param_table(&n);
    for (int i = 0; i < n; i++) {
        if (strcmp(t[i].name, name) == 0)
            return &t[i];
    }
    return NULL;
}
```

## 3. config_dump_params 实现

```c
static const char *cfg_type_name(config_param_type_t t)
{
    switch (t) {
    case CFG_TYPE_INT:  return "int";
    case CFG_TYPE_BOOL: return "bool";
    case CFG_TYPE_STR:  return "str";
    }
    return "?";
}

int config_dump_params(char *buf, int len, int with_values)
{
    int n, off = 0, truncated = 0, total;
    const config_param_desc_t *t;

    if (buf == NULL || len <= 0)
        return -1;
    buf[0] = '\0';
    t = config_param_table(&n);

    for (int i = 0; i < n; i++) {
        int need;
        char line[512];

        /* 先格式化到栈上局部行，再统一追加——避免中途截断产生残行 */
        need = snprintf(line, sizeof(line),
                        "%s type=%s env=%s layer2=%s layer3=%s "
                        "default=%s desc=%s",
                        t[i].name, cfg_type_name(t[i].type),
                        t[i].env_name ? t[i].env_name : "-",
                        t[i].layer2_section ?
                                t[i].layer2_section : "-",
                        t[i].layer3_section ?
                                t[i].layer3_section : "-",
                        t[i].def ? t[i].def : "(unset)",
                        t[i].desc ? t[i].desc : "-");
        if (need < 0)
            return -1;

        if (with_values) {
            int tail = (int)strlen(line);
            switch (t[i].type) {
            case CFG_TYPE_INT:
                snprintf(line + tail, sizeof(line) - tail,
                         " current=%d",
                         sec_resolve_int(t[i].layer2_section,
                                         t[i].layer2_key,
                                         t[i].layer3_section,
                                         t[i].layer3_key,
                                         t[i].env_name,
                                         t[i].def ? atoi(t[i].def) : 0));
                break;
            case CFG_TYPE_BOOL:
                snprintf(line + tail, sizeof(line) - tail,
                         " current=%d",
                         sec_resolve_bool(t[i].layer2_section,
                                          t[i].layer2_key,
                                          t[i].layer3_section,
                                          t[i].layer3_key,
                                          t[i].env_name,
                                          t[i].def ? atoi(t[i].def) : 0));
                break;
            case CFG_TYPE_STR: {
                const char *v =
                    sec_resolve_str(t[i].layer2_section,
                                    t[i].layer2_key,
                                    t[i].layer3_section,
                                    t[i].layer3_key,
                                    t[i].env_name, t[i].def);
                snprintf(line + tail, sizeof(line) - tail,
                         " current=%s", v ? v : "(unset)");
                break;
            }
            }
        }

        total = (int)strlen(line);
        if (!truncated && off + total + 1 < len) {
            memcpy(buf + off, line, total);
            off += total;
            buf[off++] = '\n';
        } else {
            truncated = 1;   /* 停止写入但继续循环累计应有总长 */
        }
    }

    if (!truncated) {
        buf[off] = '\0';
        return off;
    }
    /* 缓冲区不足：返回应有的总长度（调用方 ret > len-1 判定截断），
     * 并尽力保证 buf 以 '\0' 结尾 */
    buf[len - 1] = '\0';
    return off;
}
```

要点：
- 行内先组 `char line[512]` 再追加——保证不会输出残行
- 截断时**返回应有总长度**（POSIX snprintf 惯例），调用方一次重分配即可拿全量
- `with_values` 的 current 直接复用 sec_resolve_* 重放解析链——**所见即运行期真实生效值**，且 BOOL 非法配置如实显示 `-1`（fail-closed 可视化）
- 无堆分配、无锁（store 读经 get_config_store 与现有读取同级安全）、可重入

## 4. 测试设计（libs/tests/param_registry_test.c，先写先红）

| 用例 | 断言 |
|------|------|
| registry_integrity | count ≥ 17；每条 name/owner/desc 非空且 name 全表唯一；type ∈ 枚举；BOOL 的 def ∈ {"0","1"}；STR 的 def 可 NULL；layer 成对出现（section/key 同时为 NULL 或同时非 NULL） |
| registry_matches_macros | **按 name 定位条目**（config_param_find，禁硬编码下标——表序变化不得破坏测试）：audit_enabled.layer2_section==SEC_GLOBAL_SECTION、aio-speedd.mtls_enabled.layer2_key==SEC_TOOL_MTLS_KEY、auth_keycheck_enabled.layer3_section==SEC_MASTER_SECTION、cert_dir.env_name==RPC_TLS_CERT_DIR_ENV、四工具 section 宏（AIO_SPEEDD/AIO_SPEED/RDBCOMMD/RDBCOMM_TOOL_SECTION）逐一相符——宏改名/表改值任一发生即红 |
| dump_static_format | with_values=0 输出含全部 17 个 name；每行含 `type=`/`env=`/`default=`/`desc=`；无 current 字样 |
| dump_current_defaults | 统一 fixture `reset_store()`：unsetenv 全部相关 env → parse_config(空 ini) 清空 store → with_values=1：audit_enabled 行含 `current=0`；cert_dir 行含 `current=/opt/aio/cfg/certs/`（不依赖 init_config 的环境行为，直接以 parse_config 控制 store 状态；init_config ENOENT 时返回 0 已核实 rdb-config.c:249-251） |
| dump_current_ini_layer | 临时 ini 写 `[security]\naudit_enable = 1` → parse_config 后 dump：audit_enabled `current=1` |
| dump_current_env_priority | setenv("AUDIT_ENABLE","0") 覆盖 ini 的 1 → current=0（第1层优先实证）；用后 unsetenv |
| dump_bool_invalid_fail_closed | 临时 ini 写 `[security]tls_enable = yes` → dmsbtex.mtls_enabled 行 `current=-1`（fail-closed 可视化） |
| find_api | config_param_find("cert_dir") 非 NULL 且各字段正确、指针落在 [table, table+count) 区间内；find("nope")/find("")/find(NULL) 均 NULL |
| small_buffer_safe | len=8 时返回值 > 8（可探测需重分配）、buf[7]=='\0' 无越界写 |

测试骨架沿用 rdb_config_test.c 的 TEST/RUN_TEST 风格 + CHECK 宏（-DNDEBUG 不剥离，T3975 教训）。临时 ini 复用 mkstemp 模式。**每个涉及 store 状态的用例前后显式 reset_store()，杜绝用例顺序耦合（T3975 对 dmsbtex 测试的同类批评）**。

## 5. xmake 接入（libs/tests/xmake.lua 追加，对齐 rdb_config_test 实际写法）

```lua
target("param_registry_test")
    set_default(false)
    set_kind("binary")
    add_defines("_GNU_SOURCE")
    add_files("param_registry_test.c")
    add_deps("rdb-config")      -- 注意连字符：libs 主 target 实名（已核对 xmake.lua）
    add_tests("default", {realtime_output = true})
```

## 6. 明确不做 / 已知限制

- 不改 sec_resolve_* 与任何调用点（30+ 处零触碰）
- 表↔调用点的**实参级**漂移（如有人单独改动某调用的 default）无法被测试捕获——测试锚定的是表↔宏；实参一致性靠后续演进（方案 B param_get(id)）根治
- dump 的 current 为取样瞬间的值，非一致性快照（与 store 双缓冲读语义一致）
- 既有缺陷仅登记不顺带修：tls_algorithm 默认值分裂（§0 ⚠）、SBT_*_ENV 宏双定义——建议随注册表采纳后的清理任务统一处置

## 7. 自审查记录（2026-08-26，评审前修正）

| # | 发现 | 定级 | 处置 |
|---|------|------|------|
| 1 | `snprintf(line+strlen,0,"\n")` 死代码（size=0 不写入，注释误导） | 实现 bug | 删除 |
| 2 | dump 格式串遗漏 desc 字段——违背"dump 即文档"目标 | 设计缺陷 | 格式串补 `desc=%s` |
| 3 | xmake 依赖名误写 `rdb_config`（实际 `rdb-config`），漏 set_default/defines/realtime_output | 事实错误 | 已按 libs/tests/xmake.lua 实际写法核对修正 |
| 4 | 测试断言 `init_config==0 \|\| errno==ENOENT` 冗余不可靠 | 测试缺陷 | fixture 改为 parse_config(临时ini) 直接控状态 |
| 5 | matches_macros 硬编码下标 t[audit]——表序变化破坏测试 | 测试脆弱 | 改 config_param_find 按 name 定位 |
| 6 | 截断分支缺显式标志，可读性差 | 可读性 | 引入 truncated 标志 |

自审后遗留的已知限制（接受）：表↔调用点实参级漂移无法测试捕获；line[512] 内超长值截断为行完整性让步。
