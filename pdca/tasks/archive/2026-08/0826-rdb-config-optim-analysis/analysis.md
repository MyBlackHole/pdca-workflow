# T0386 分析报告：rdb config 是否需要优化

> 对象：C 侧 rdb config 体系本身（参数注册表 `libs/rdb-config.c` + 解析层 + 初始化 + 安全）。
> 方法：静态通读注册表实现、跨消费点 fail-closed 核对、覆盖度/性能评估、F9 安全遗留评估。
> 范围（用户确认）：聚焦 C 侧本身；Go(oss)/跨模块仅作背景。

## 1. 执行摘要（AC-1 结论）

**当前 rdb config（C 侧本身）无需紧急优化；但存在 1 个高优先级安全遗留项与若干中/低增量优化项，建议作为后续 development 子任务立项，而非紧急重构。**

判定依据：
- 正确性/一致性层已完成充分优化：生产代码已从 `sec_resolve_*` 散点全面迁移到 `sec_get_*` 注册表（生产 `sec_resolve_*` 调用 0 处；`config_get_string/int` 的 29 处调用全在测试），14 个安全参数的 4 层解析链集中、严格解析 fail-closed、常量/env 名单一来源。
- 基础安全 fail-closed 正确：鉴权/审计等关键开关的调用方均正确处理非法 `-1`（维持开启）。
- 仍存在的优化点聚焦在：**安全纵深（F9 证书路径校验）**、**fail-closed 处理一致性**、**配置源/覆盖度统一**，均为增量改进，非阻断性缺陷。

## 2. 现状评估（已查证事实）

| 维度 | 现状 | 评价 |
|------|------|------|
| 架构 | 参数注册表 `g_param_table` + 枚举 ID + `sec_get_int/bool/str`，14 个安全参数 4 层链 env>layer2>layer3>def | 优 |
| 迁移度 | 生产 `sec_resolve_*` 调用 0（仅 1 注释残留）；`config_get_*` 29 处全在测试 | 优 |
| 严格解析 | BOOL 非法⇒-1 fail-closed(T0361)；INT `parse_strict_int` 脏值回退 default 并告警(T3981/F5)；上限不再静默截断(T0369 F2) | 优 |
| 常量集中 | 路径 `libs/cfg_path.h`(F3)、env 名 `rdb-config.h`(T3978) | 优 |
| 初始化 | `__attribute__((constructor)) rdb_auto_init` 自动加载 | 取舍点（见 §6 低优项） |
| 跨语言(背景) | Go `chooseStr=cli>env>file>def` 与 C 4 层模型一致 | 已对齐 |

## 3. 覆盖度评估（AC-2）

注册表当前覆盖 14 个参数，**全部为安全/TLS/审计/鉴权类（BOOL 或 STR 型），无 INT 型参数**。

- **设计评价**：精准覆盖高敏感的安全策略开关与证书/算法，符合"安全参数优先集中"的合理策略；`config_get_int` 底层仍支持 INT，但注册表未定义 INT 参数，意味着端口/超时/并发等整数类配置由各模块自读（不在注册表）。
- **扩展可行性**：`config_param_desc_t` 已支持 `CFG_TYPE_INT`，扩展仅需新增枚举项 + 表条目 + `sec_get_int` 已就绪，成本低。
- **建议**：不强制全量纳入；建议后续按模块增量将"结构性/高频"参数纳入注册表并复用严格解析（避免在各模块重演 T0369 的 atoi/截断类问题）。**本任务不实施**。

## 4. fail-closed 健壮性核对（AC-3）

逐一审视全部生产 `sec_get_*` 消费点的非法 `-1` 处理：

| 消费点 | 参数 | -1 处理 | 结论 |
|--------|------|---------|------|
| `timed_key.c:229` | AUTH_KEYCHECK | `!= 0` ⇒ -1 维持开启 | ✅ 正确 |
| `logger.c:121` | AUDIT | `!(-1)=false` ⇒ 维持审计开启 | ✅ 正确 |
| `rdbcommd-main.c:271/279` | AUDIT/AUTH | `if(<0) return EXIT_FAILURE` 启动期硬失败 | ✅ 最严 |
| `rdbcommd-main.c:263` | RDBCOMMD_MTLS | 直接赋值 `.mtls_enabled`，无 `<0` 校验 | ⚠️ 不一致 |
| `rdbcomm-main.c:569` | RDBCOMM_MTLS | 直接赋值，无 `<0` 校验 | ⚠️ 不一致 |
| `dmsbtex/network.c:106` | SBT_MTLS | 直接赋值 `cfg->mtls_enabled`，无 `<0` 校验 | ⚠️ 不一致 |
| `libobk/.../libobk.c:71` | SBT_MTLS | 直接赋值，无 `<0` 校验 | ⚠️ 不一致 |

**要点**：
- 鉴权/审计两类开关 fail-closed 正确且最严（硬失败）。
- 全部 `mtls_enabled` 赋值点为"直接赋值无 `<0` 校验"：因 C 中 `-1` 作真值 ⇒ 当作"开启"，**对 mTLS 安全（fail-closed 开启）**，但与被硬失败处理的 audit/auth 行为**不一致**，且依赖"-1 当真"的隐式巧合而非显式设计；若未来某消费点改为 `== 1` 精确比较会出错。
- `sec_get_str` 的 `cert_dir` 等（rdbcommd:365、rdbcomm:618、dmsbtex:130、libobk:89/61）直接消费未校验字符串，详见 §5。

## 5. 安全遗留评估：F9（AC-4）

**证据**：`sec_walk_str`（`libs/rdb-config.c`）第 1 层 `if (v && v[0]) return v;` 直接返回 `getenv(p->env_name)` 指针。`PARAM_CERT_DIR` 的 env 名为 `RPC_TLS_CERT_DIR_ENV`，证书目录经此返回后由 `rdbcommd-main.c:365` 等直接用于 `tls.LoadX509KeyPair`/路径拼接。

**风险**：在 env 不可信的威胁模型下（容器/进程环境被注入、误设），`RPC_TLS_CERT_DIR` 可被指向任意路径（含 `..`、绝对恶意路径），导致 mTLS 加载攻击者控制的证书/私钥，构成**证书路径注入**。当前依赖"env 可信"假设，T0369 将其留安全专项。

**建议**：在注册表 STR 解析层对"路径类"参数（`PARAM_CERT_DIR`）增加校验——绝对路径、无 `..` 段、位于白名单前缀（如 `DEFAULT_CERT_DIR` 父目录）。非路径类 STR（算法名）做字符白名单即可。

## 6. 性能评估（AC-5）

`sec_get_*` 每次调用执行 `getenv` + `_kv_store` 线性扫描（O(n)，`CONFIG_KV_MAX=1024`，实际远小于）。

**判定：无需优化（无证据）**。关键证据：`rdbcomm/server.h:16`、`rpc/rpc-config.h:23` 注释明确"安全策略开关初始化时一次解析保存于进程上下文，连接处理路径只读字段"——热路径（每连接）读的是已解析的 `server_opts` 字段，**不重复调用 `sec_get_*`**。启动期少量调用的 O(n) 扫描开销可忽略。

## 7. 优化点优先级清单（AC-6）

| 优先级 | 项 | 问题 | 影响 | 建议 | 是否本任务外立项 |
|--------|----|------|------|------|------------------|
| **高** | F9 证书路径校验 | `sec_walk_str` 直接返回未校验 env 路径 | 证书路径注入（env 不可信时） | 注册表 STR 层加路径/字符白名单校验 | 是（安全专项 D1） |
| **中** | fail-closed 一致性 | `mtls_enabled` 直接赋值无 `<0` 校验，与 audit/auth 硬失败不一致 | 行为不一致、隐式依赖 -1 当真 | 统一所有消费点：显式 fail-closed 或启动期硬失败 | 是（D2） |
| **中** | F7 配置源统一 | dmsbtex 仍读 `sbt-config.conf`，与 `rdb.conf` 并存 | 部署/排障负担、双解析实现漂移 | 合并到 `rdb.conf` 统一源 | 是（跨模块专项 D3） |
| **低** | 注册表覆盖度扩展 | 无 INT 型注册参数，结构/整数类参数各模块自读 | 重演 atoi/截断类隐患风险 | 按模块增量纳入复用严格解析 | 是（可选 D4） |
| **低** | 显式初始化入口 | `rdb_auto_init` constructor 无法禁用/指定路径/错误处理 | 测试/嵌入式场景取舍 | 提供显式 `init_config` 覆盖入口并文档化 | 是（可选 D5） |
| **否决** | 性能缓存 | `sec_get_*` 每次 getenv+O(n) | 热路径已缓存于 server_opts，无瓶颈 | 不优化 | 否 |

## 8. 实施方案设计（AC-7，针对高/中项，不写代码）

### D1 — F9 证书路径校验（高）
- **改动点**：`libs/rdb-config.c` 的 `sec_walk_str`：在返回 env/file 值前，增加 `is_safe_path()` 校验（绝对路径、无 `..`、前缀白名单）；非法值降级到下一层或返回 NULL（fail-closed 由调用方维持默认 cert 目录）。算法名类 STR 增加字符白名单（`[A-Za-z0-9_-]`）。
- **兼容性**：仅收紧非法路径，合法部署（cert 在 `/opt/aio/...`）不受影响。
- **回归**：新增 `param_registry_test.c` 用例——`RPC_TLS_CERT_DIR=/etc/shadow` 或含 `..` 时被拒绝/回退默认；`sec_get_str(PARAM_CERT_DIR)` 行为断言。

### D2 — fail-closed 一致性（中）
- **改动点**：统一 `mtls_enabled` 赋值点（`rdbcommd-main.c:263`、`rdbcomm-main.c:569`、`dmsbtex/network.c:106`、`libobk/...:71`）为 `int v = sec_get_bool(...); if (v < 0) v = 1; /* fail-closed 默认开启 */`；或采用与 audit/auth 一致的"启动期硬失败"。推荐后者（统一最严），但需评估 dmsbtex/libobk 作为库的失败传播方式。
- **兼容性**：行为变化仅影响"非法值"输入，合法 `0/1` 不变。
- **回归**：新增用例——各工具读非法 mTLS 开关时行为一致（全部开启或全部启动失败）。

### D3 — F7 配置源统一（中，跨模块专项）
- **改动点**：dmsbtex 由读 `sbt-config.conf` 改为读统一 `rdb.conf` 的对应 section；移除 `sbt-config.conf` 解析分支。
- **兼容性**：需保留旧部署过渡（兼容读取旧文件名一次或文档化迁移）。
- **回归**：dmsbtex mTLS 集成测试以 `rdb.conf` 为源通过。

## 9. 后续 development 子任务候选（AC-8，P4 拆解骨架）

- **D1** `0826-rdb-config-f9-path-validation`（高，安全专项）：F9 证书/算法路径校验。
- **D2** `0826-rdb-config-failclosed-unify`（中）：fail-closed 消费点一致性。
- **D3** `0826-rdb-config-source-unify`（中，跨模块）：F7 配置源合并。
- **D4**（可选）`0826-rdb-config-registry-extend`：注册表覆盖度扩展。
- **D5**（可选）`0826-rdb-config-explicit-init`：显式初始化入口。

本任务仅完成分析与方案设计，上述由后续 development 子任务实施。
