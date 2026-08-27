# 统一 rdb-config parse_config 入口，消除启动期与运行期重复解析

## 问题陈述

- **现状**: F-139 提交安全审查发现 `parse_config` 被 `init_config` / `set_rpc_init_config` /
  `fsdeamon_init_config` / `fsclient_init_config` 各自调用，运行期 `fs_source.cpp` /
  `backup_helper.cpp` / `unix_server.cpp` 还会再次调用，导致同一全局单例 `_kv_store`
  被反复覆盖解析。各模块 init 还都接收 `config_file` 参数用于自行解析。
- **目标**: 收敛 `parse_config` 为 `init_config` 独占；各模块 init 去掉 `config_file` 参数、
  改为无参并从已加载的全局 store 读取；运行期重载统一走 `init_config`。
- **差距**: 当前每次 init/reload 都重复文件 IO 与 inih 解析覆盖全局 store，存在重复开销、
  潜在 TOCTOU 不一致、调用关系不清晰。

## 解决方案

从调用方视角：启动与重载均先经 `init_config(config_file, &pr)` 完成"加载全局 store"，
随后各模块 init 仅从 store 读取参数填充自身结构，不再参与文件解析。

## Seam 分析

### 测试接缝
- 在哪个接口/边界层编写测试？rdb-config 解析入口（init_config）、各模块 init 入口、reload 路径。
- 哪些已有测试覆盖：libs/tests/rdb_config_test.c、rpc/tests/rpc_config_test.cpp、
  fs-backup/fsdeamon/tests/config_test.cpp。需新增"多次 init 去重"行为测试。
- Mock/Stub：用临时文件（mkstemp 风格路径）构造 rdb.conf，无需网络/DB 隔离。

### 声明的测试接缝
- seam: libs/tests/rdb_config_test.c -> libs/rdb-config.c
- seam: rpc/tests/rpc_config_test.cpp -> rpc/rpc-config.cpp
- seam: fs-backup/fsdeamon/tests/config_test.cpp -> fs-backup/fsdeamon/config.cpp

### 验收可测性
- 每个验收项均有可构造的输入与可 grep/断言的 pass/fail 信号（见验收标准）。
- 行为测试为主，不引入内部计数器探针。

## 用户故事

1. 作为维护者，我希望配置只被解析一次，以便消除重复 IO 与潜在不一致。
2. 作为维护者，我希望各模块 init 不各自持有配置路径，以便加载入口单一、可审计。
3. 作为运维，我希望重载行为与应用启动一致，以便配置生效可预测。

## 实现决策

- **收敛 parse 调用**：`parse_config` 仅由 `init_config` 调用；外部模块（rpc/fs-backup）不得再直接调用 `parse_config`。
- **唯一加载入口**：`init_config(config_file, &pr)` 按 `config_file` → `getenv(RDB_CONFIG)` → `DEFAULT_RDB_CONFIG_PATH` 解析并填充全局单例 `_kv_store`；保持"未显式指定且默认路径不存在 → 空配置 ok"语义。
- **各模块 init 去参**：`set_rpc_init_config` / `fsdeamon_init_config` / `fsclient_init_config` 去掉 `config_file` 参数（错误返回通道 `err_msg` 保留），改为"默认值初始化 + 从已加载 store 经 `sec_get_*` 读取覆盖"，内部不再调用 `parse_config`。
- **调用方调整**：各 `main` 先 `init_config(config_file, &pr)` 加载 store，再无参调用各模块 init。
- **运行期 reload 统一**：`fs_source` / `backup_helper` / `unix_server` 的 reload 点改为 `init_config(config_path, &pr)` 重新加载 store，随后重新调用对应模块 init 刷新模块结构；rpc 侧 `rpc_parse_config(config_file!=NULL)` 改为经 `init_config` 重载 store，`NULL` 时复用已加载 store（不 parse）。
- **接口收敛但保兼容**：错误返回通道（`err_msg`/`int` 返回码）保持，降低调用方回归面。

## 测试决策

- 行为测试为主（用户选定）：构造临时 rdb.conf → 先 `init_config` 加载 → 多次各模块 init →
  断言全局 store / 模块参数与单次加载一致；修改文件后 `init_config` 重载断言参数刷新；
  文件缺失断言默认值保留。
- 既有单测（rpc_config_test / config_test）需更改为新签名并补充无参 init 行为断言。
- 不引入计数器/内部探针。

## 验收标准

- [ ] AC-1: `init_config` 调用后，依次调用 `set_rpc_init_config` / `fsdeamon_init_config` / `fsclient_init_config`（无参），全局 `_kv_store` 内容与仅调用一次 `init_config` 后一致（重复 init 不产生附加解析副作用）。
- [ ] AC-2: `set_rpc_init_config` / `fsdeamon_init_config` / `fsclient_init_config` 的函数签名不再包含 `config_file` 参数，且实现内部不再调用 `parse_config`（静态/编译可见）。
- [ ] AC-3: 运行期 reload（fs_source / backup_helper / unix_server 触发）经 `init_config` 重新加载 store 后，模块参数反映最新文件内容。
- [ ] AC-4: 配置文件缺失（ENOENT）时，各模块 init 仍保留注册表默认值且进程可正常启动，行为与重构前一致。
- [ ] AC-5: 既有 TLS 开关、证书路径等参数经 store 读取，在 rpc/fs-backup/dmsbtex 集成与单测中取值正确，无回归（安全语义不变：fail-closed、强制 mTLS 行为保持）。

## 范围外

- 全局 `_kv_store` 在 reload 与并发读取间的无锁竞态（0823 审计已记录，独立问题）。
- 配置项语义/默认值本身的变更（仅重构加载入口，不改参数含义）。
- `parse_config` 底层解析逻辑（ini 解析、截断处理）的改动。

## 备注

- 与 0826-cleanup-rdb-config-deadcode(T3984) 互补：其已将双缓冲简化为单例 store，本任务在此基础上收敛 parse 调用。
- 本任务源自 F-139 提交安全审查发现 #4（审查报告条目 4：parse_config 被多次分散调用）。
- 设计约束（注入知识资产）：遵循 `security-bool-failclosed.md` 与 `int-security-switch-failopen.md`——本重构仅收敛 parse 调用入口，**不得改变任何安全开关（mtls_enabled / audit_enabled / auth_enabled）的 fail-closed 解析语义**；ENOENT 保留默认时默认值必须安全（不得因去重而让安全开关 fail-open）。遵循 `process-context-held-switches.md` 范式：各模块 init 从已加载 store 读并填充自身上下文结构，reload 经 init_config 重新解析刷新结构体。
