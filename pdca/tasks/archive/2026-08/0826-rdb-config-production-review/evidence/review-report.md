# T3980 审查报告：rdb-config 生产使用级别就绪度

- 任务：T3980 / 0826-rdb-config-production-review
- 场景：review（纯评估，不改代码）
- 审查对象：
  - 核心库 `libs/rdb-config.{c,h}`（C 侧四层解析 `sec_get_int/bool/str`）
  - 消费者：`rpc/rpc-config.cpp`、`rdbcomm/rdbcommd-main.c`、`dmsbtex/network.c`、`libobk/lib/logic/oracleCmdTbl.c`、`libobk/lib/sbt/libobk.c`、`rdbcomm/rdbcomm-main.c`
  - Go 侧：`oss/cmd/tls.go`、`oss/cmd/base.go`、`oss/cmd/oss_https_test.go`
  - 回归基线：`knowledge/rdb-config/audit-findings.md`（T0369 F1–F9）
- 方法：静态逐行审查 + 跨语言一致性比对 + T0369 F1–F8 回归矩阵 + 安全框架（CERT C / OWASP / CWE Top 25）对照
- 审查结论（verdict）：**不满足生产使用级别**（CRITICAL/HIGH = 1）

---

## 一、总体判定

| 维度 | 结论 |
|------|------|
| 正确性 | 大部分正确；存在 1 个确定性安全控制 defect（HIGH） |
| 健壮性 | 脏值/截断有告警，但 INT 安全开关 env 层未严格解析 |
| 安全性 | INT 型安全开关（审计/鉴权）在 env 脏值时 **fail-open** |
| 并发 | 读取双缓冲加锁，但 `config_set_string` 写路径无锁 |
| 可观测性 | 重载后超限静默（`g_truncated_warned` 不重置）、缺文件静默空配置启动 |
| 跨语言一致性 | F1 优先级对齐 ✅；但 BOOL 严格度 C/Go 分歧 |

**HIGH 数量 = 1 → 不满足「CRITICAL/HIGH=0」硬门槛。**

---

## 二、发现清单（按严重度）

### 🔴 HIGH-1：`sec_walk_int` env 层用 `atoi`，INT 型安全开关脏值静默 fail-open
- 位置：`libs/rdb-config.c:381-385`（env 层）、`:400`（def 层亦 `atoi`）
- 现象：
  - `sec_walk_int` 在 env 层 `if (v && v[0]) return atoi(v);`——`atoi("abc")==0`，无任何告警。
  - layer2/layer3 已通过 `config_get_int(...,-1)` + `parse_strict_int` 做到脏值回退（T0369 F5），**唯独 env 层遗留 `atoi`**。
  - 受影响参数：`PARAM_AUDIT_ENABLED`（`AUDIT_ENABLE_ENV`）、`PARAM_AUTH_KEYCHECK_ENABLED`（`AUTH_ENABLE_ENV`）——均为 CFG_TYPE_INT，**即审计开关与鉴权开关**。
- 消费者未做 -1 校验：
  - `rpc/rpc-config.cpp:188` `g_rpc_config->audit_enabled = sec_get_int(PARAM_AUDIT_ENABLED);`（无 `<0` 检查）
  - `rpc/rpc-config.cpp:190` `auth_enabled = sec_get_int(PARAM_AUTH_KEYCHECK_ENABLED);`
  - `rdbcomm/rdbcommd-main.c:271,273` 同模式
- 后果：运维误设 `AUDIT_ENABLE=garbage` → `atoi→0` → **审计被静默关闭**，无告警、无报错。与同文件 BOOL 开关（`rpc-config.cpp:180`、`rdbcommd-main.c:332` 均 `<0` fail-closed 报错）形成**内部不一致**——安全开关的 fail-closed 保护被遗漏。
- 威胁模型：env 通常运维可控，但容器/12-factor/CI 环境下 env 可被间接注入；审计/鉴权属安全关键控制，应按 CERT "fail-closed" 原则处理。
- 整改建议（任一）：
  1. 将 `AUDIT_ENABLED`/`AUTH_KEYCHECK_ENABLED` 改为 `CFG_TYPE_BOOL`，走 `sec_get_bool`（已 fail-closed 且校验 -1）；或
  2. `sec_walk_int` env 层改用 `parse_strict_int`，失败返回 -1，并要求消费者对 -1 显式处理（fail-closed）。
- 严重度：**HIGH**（安全控制确定性 fail-open，与兄弟 BOOL 处理不一致）

### 🟠 MEDIUM-1：F9 遗留——`sec_walk_str` 直接返回 `getenv` 指针，证书路径无校验
- 位置：`libs/rdb-config.c:441-445`（`sec_walk_str` env 层 `return v;` 直接返回 `getenv` 指针）
- 现象：`PARAM_CERT_DIR`（`RPC_TLS_CERT_DIR_ENV`，CFG_TYPE_STR）env 层直接返回 `getenv` 指针，**未做路径合法性/穿越校验**。
- 缓解：消费者均 `snprintf(dest, ..., sec_get_str(...))` 立即拷贝（如 `rpc-config.cpp:211`），未长期持有指针，故指针生命周期风险实践中可控。
- 残留风险：若 env 不可信，证书目录可被指向攻击者可写路径，造成证书/私钥加载被劫持（F9 原评级 MEDIUM，本次维持）。
- 整改建议：对 `RPC_TLS_CERT_DIR` 等路径类参数增加绝对路径/前缀白名单校验。
- 严重度：**MEDIUM**（继承自 T0369 F9，未被 T3978/T3979 覆盖）

### 🟠 MEDIUM-2：`config_set_string` 写路径无锁，与双缓冲读加锁模型不一致
- 位置：`libs/rdb-config.c:139-163`（无 `g_cfg_lock`）
- 现象：读取路径（`get_config_store`/`parse_config`）加 `g_cfg_lock`，但 `config_set_string` 直接写 `_kv_stores[config_index].entries` 无锁。若运行期并发 `config_set_string` 与读取，可能读到半写入条目。
- 实际风险：当前调用点多在初始化期，运行期并发写入概率低 → 降级为 **MEDIUM/LOW**。
- 整改建议：写路径加 `g_cfg_lock`，或与 `parse_config` 共用同一保护。

### 🟠 MEDIUM-3：`g_truncated_warned` 跨 reload 不重置 → 重载后超限静默截断
- 位置：`libs/rdb-config.c:23,36-42`
- 现象：`g_truncated_warned` 为一次性全局标志，`parse_config` 重置 `count` 但不重置该标志。首次超限告警后，后续 reload 再超限**不再告警**。
- 后果：运维 reload 配置后若条目超限，截断静默发生，可观测性缺口。
- 整改建议：reload 开始时重置 `g_truncated_warned=0`，或改为按 store 实例的截断计数。
- 严重度：**MEDIUM**（可观测性）

### 🟡 LOW-1：`init_config` 遇 `ENOENT` 静默返回 0（空配置启动）
- 位置：`libs/rdb-config.c:249-254`
- 现象：配置文件缺失时返回成功，使用空配置（安全开关取默认，多为关闭）。缺少显式"配置未加载"信号。
- 后果：路径配错/部署遗漏时服务"正常"启动但安全策略全关，难排查。
- 整改建议：缺失时至少记一条告警日志（非致命）。
- 严重度：**LOW**

### 🟡 LOW-2：`rdb_auto_init` constructor 静默吞错
- 位置：`libs/rdb-config.c:569-573`
- 现象：`__attribute__((constructor))` 在库加载时自动 `init_config`，constructor 无法返回错误；非 `ENOENT` 的加载失败被丢弃，库以空配置运行。
- 整改建议：constructor 失败记告警；或由显式初始化入口替代自动初始化以可控时机。
- 严重度：**LOW**

### 🟡 LOW-3：Go / C 布尔解析严格度分歧
- 现象：C `sec_get_bool` 非法值返回 -1、调用方 fail-closed 报错（如 `rdbcommd-main.c:332`）；Go `resolveEnableValue`（oss/cmd/tls.go:187）对可疑假值**告警后按关闭处理**（不报错）。
- 影响：同一份脏值配置，C 工具启动失败、Go 服务降级为明文 HTTP——行为不统一，运维预期易错乱。
- 整改建议：跨语言统一"非法值 fail-closed"策略（推荐均报错或均明确告警+关闭，但需文档化）。
- 严重度：**LOW**

---

## 三、T0369 F1–F8 回归矩阵

| 项 | 状态 | 证据 |
|----|------|------|
| F1 跨语言优先级一致 | ✅ 已满足 | C `sec_walk` env>layer2>layer3>def；Go `chooseStr` CLI>env>file>def，env 在 file 之前（oss/cmd/tls.go:95-106,111） |
| F2 CONFIG_KV_MAX 不截断 | ✅ 已满足 | rdb-config.c:35-44 `return 1` 继续解析 + 单次告警 |
| F3 常量单一来源 | ✅ 已满足 | `grep` 确认 `RDB_CONFIG`/`DEFAULT_RDB_CONFIG_PATH` 仅定义于 `libs/cfg_path.h:13-14` |
| F4 隐式回退关闭 | ✅ 已满足 | `g_allow_global_fallback=0`（rdb-config.c:19），`config_get_string` 默认不回退（:89-98） |
| F5 脏值严格解析 | ⚠️ **部分回归** | `config_get_int` 已严格（:113）；但 `sec_walk_int` **env 层仍 `atoi`**（:384）→ 见 HIGH-1 |
| F6 并发锁 | ⚠️ **部分** | `get_config_store`/`parse_config` 加锁（:170-172,:190-192）；但 `config_set_string` 无锁 → MEDIUM-2 |
| F7 配置源分散 | ✅ 已知未修复（非阻塞） | dmsbtex 仍读 `sbt-config.conf`，基线已记录为后续优化 |
| F8 命名混淆 | ✅ 已满足 | 代码统一 `rdb.conf`，注释无 `rdb.cfg` 残留 |

> F9（env 直接返回指针/证书路径注入）：见 MEDIUM-1，维持 MEDIUM，未被 T3978/T3979 覆盖。

---

## 四、AC 验收逐条

- **AC-1 审查报告交付**：✅ 本报告
- **AC-2 核心库生产就绪判定**：❌ 不满足（HIGH-1）
- **AC-3 消费者迁移正确**：⚠️ 功能迁移正确（param ID 解析链路完整），但 INT 安全开关消费点缺 -1 校验（与 HIGH-1 同源）
- **AC-4 Go 侧一致性**：✅ 优先级对齐（F1）；⚠️ BOOL 严格度分歧（LOW-3）
- **AC-5 T0369 F1–F8 回归**：⚠️ F5/F6 部分（见上）
- **AC-6 F9 注入评估**：⚠️ 确认存在（MEDIUM-1）
- **AC-7 CRITICAL/HIGH=0 门槛**：❌ 违反（HIGH=1）
- **AC-8 清理类归并**：✅ 见下

---

## 五、清理类发现归并（→ 0826-cleanup-rdb-config-deadcode）

以下非阻塞、可后续清理，归入活跃任务 `0826-cleanup-rdb-config-deadcode`：
- MEDIUM-2 `config_set_string` 加锁
- MEDIUM-3 `g_truncated_warned` reload 重置
- LOW-1 `init_config` ENOENT 告警
- LOW-2 `rdb_auto_init` 错误可见化
- LOW-3 Go/C 布尔严格度统一（需跨语言协调）

---

## 六、整改优先级建议

1. **必须（满足生产级别前）**：HIGH-1 —— INT 安全开关 env 层改为严格解析 / 改 CFG_TYPE_BOOL，并使消费者 fail-closed。
2. **建议**：MEDIUM-1 证书路径校验；MEDIUM-2 写锁；MEDIUM-3 告警重置。
3. **可选**：LOW-1/2/3 可观测性与跨语言一致性打磨。

> 一句话结论：**rdb-config 架构范式正确、跨语言优先级已对齐，但 INT 型安全开关（审计/鉴权）在 env 脏值时 fail-open，构成 1 个 HIGH 级确定性缺陷，须整改后方可判定满足生产使用级别。**
