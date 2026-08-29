# 跟进 T0386：rdb config F9 证书路径校验（已取消）

> **决策（Plan 阶段）：信任外部输入（env 可信），F9 无需修改代码。本任务取消，不进入 Do。与 T0369 F9「仅建议、依赖 env 可信」结论一致。**

## 问题陈述
T0369 审查遗留 F9：`libs/rdb-config.c` 的 `sec_walk_str`（`sec_get_str` 的 4 层遍历）第 1 层直接 `return getenv(p->env_name)`，对 `PARAM_CERT_DIR`（`RPC_TLS_CERT_DIR`）等路径类参数**未做任何路径合法性校验**。在 env 不可信的威胁模型下，攻击者可将 `RPC_TLS_CERT_DIR` 指向任意路径（如 `/etc/shadow`、`/opt/aio/../etc`、`/other/service/certs`），导致 mTLS 加载攻击者控制的证书/私钥（证书路径注入，CWE-22 路径遍历范畴）。本任务在注册表 STR 解析层增加路径/字符白名单校验，使非法 env 值被拒绝并安全回退。

## 初步事实（Triage 已查证，源自 T0386 analysis.md §5/§8）
- `sec_walk_str`（`libs/rdb-config.c:370+`）第 1 层 `if (v && v[0]) return v;` 直接返回 `getenv` 指针，无校验。
- `PARAM_CERT_DIR` 默认 `DEFAULT_CERT_DIR="/opt/aio/cfg/certs/"`（`libs/common.h:14`），env 名 `RPC_TLS_CERT_DIR`（`libs/rdb-config.h:36`）。
- 证书目录经 `sec_get_str(PARAM_CERT_DIR)` 被 `rdbcommd-main.c:365`、`rdbcomm-main.c:618`、`dmsbtex/network.c:130`、`libobk/...:89/61` 直接用于 TLS 证书加载/路径拼接。
- 安全编码原则：外部输入（env）不可信、默认拒绝/白名单优先、防路径遍历。

## 方案方向（待 Grill 确认严格度）
在 `config_param_desc_t` 增加 `unsigned is_path` 标志（仅 `PARAM_CERT_DIR` 置 1，其余 STR 视为"名称/算法"类）；`sec_walk_str` 在每层取到值后调用新增 `sec_validate_str(const config_param_desc_t*, const char* value)`：
- **路径类（`is_path`）**：校验为绝对路径、规范化后无 `..` 段、且位于允许前缀白名单（默认 `/opt/aio`，可编译期扩展）。非法则**拒绝该层**（continue 到下一层）并 `fprintf(stderr, ...)` 告警一次。
- **名称/算法类**：校验字符白名单 `[A-Za-z0-9_-]`（防注入分隔符/路径字符）。非法同样拒绝该层并告警。
- **失败行为**：拒绝非法 env 层后回退到文件 section / 默认 cert 目录（fail-safe，不采用恶意值、不崩溃）。

## 验收标准
- [ ] AC-1: `RPC_TLS_CERT_DIR=/etc/shadow` 被拒绝——`sec_get_str(PARAM_CERT_DIR)` 不等于 `/etc/shadow`，回退到文件值或 `DEFAULT_CERT_DIR`（param_registry_test 断言）。
- [ ] AC-2: `RPC_TLS_CERT_DIR` 含 `..`（`/opt/aio/../etc`）被拒绝并回退默认。
- [ ] AC-3: 合法 `RPC_TLS_CERT_DIR=/opt/aio/cfg/certs/custom` 通过，`sec_get_str` 返回该值。
- [ ] AC-4: 算法名类 STR（`PARAM_SBT_TLS_ALGORITHM`/`PARAM_LIBOBK_CLI_TLS_ALGORITHM`）含非法字符（如 `/`、`;`、`$`）被拒绝并回退默认/NULL。
- [ ] AC-5: 失败行为——非法 env 值被拒后回退下一层并 stderr 告警一次，不崩溃、不采用恶意值（现有 `sec_get_str_defaults` 回归仍通过）。
- [ ] AC-6: 兼容性——合法部署（cert 在 `/opt/aio/...`）行为不变；`param_registry_test` 全过，编译无 `-Werror` 问题。
- [ ] AC-7: 文档——`rdb-config.h` 注释说明 `is_path` 标志与路径白名单约束，沉淀到 knowledge。

## 声明的测试接缝
### 声明的测试接缝
- seam: libs/tests/param_registry_test.c -> libs/rdb-config.c

## 范围外
- 不改 mTLS 加载逻辑（`buildTLSConfig`/`tls.LoadX509KeyPair`），仅收紧配置源路径。
- 不处理 Go(oss) 侧（背景，本次聚焦 C 侧本身）；F7 配置源统一属其它专项。
- 不动 `config_get_string/int` 底层（仅测试使用）。

## 备注
- 父任务：T0386（分析 rdb config 是否需要优化，confirmed）。知识：`knowledge/rdb-config/optim-roadmap.md`、`knowledge/rdb-config/audit-findings.md`。
- development 场景，含测试接缝（P3.5），Do 阶段需实现 + 回归。
