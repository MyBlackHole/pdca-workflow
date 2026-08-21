# 实施计划 — tls_cert 初始化 API 完善（T0342）

## 0. 执行边界

- 本计划仅描述 Do 应做之事，不在此阶段写代码/改文件。
- Do 以 `development` A 路径执行：A2 测优 → A3 全量 → A4 双轴审查 → Z1-4 收尾。
- 变更集冻结为 7 文件 + 1 测试文件（`common.h` 统一常量、`tls_cert.h/c` 精简与兼容、`tls_keygen.c` 复用、`rpc/*` 调用点），工作区其余脏文件（`dmsbtex/network.c` 等 7 个）禁止随本次提交。

## 1. 变更清单（冻结）

| # | 文件 | 行号锚点 | 改动 | 对应 AC |
|---|------|----------|------|---------|
| 0 | `libs/common.h:19` | 统一常量 | 新增 `CERT_FILE_ED25519_CA="ed25519_ca.crt"`、`CERT_FILE_ED25519_HOST="ed25519_host.crt"`、`CERT_FILE_ED25519_HOST_KEY="ed25519_host.key"` 等（与旧无前缀并存，注释“新优先旧回退”） | AC-8 |
| 1 | `libs/tls_cert.h:46` | `tls_cert_client/server_options_t` 精简 | 删除 `profiles[2]/profile_count`，`client` 仅 `{mtls_enabled,cert_dir,algorithm,ca_cn}`，`server` 仅 `{mtls_enabled,cert_dir}`；`tls_cert_profile_t` 仅作内部 `build_server_profiles` 产出 | AC-1..AC-5 |
| 2 | `libs/tls_cert.c:118` | `slot_create` 与 `init_*` 重构 | 拆 `LOAD_CERT/LOAD_KEY`，`ca_cn` 遍历非空 CN，`init_*` 删除 `profiles` 分支仅 `cert_dir` 必填（空→`INVALID_PARAM`），`build_client_profile:212` 加 `ca_cn` 必填与非法字符校验，双格式回退（`ed25519_*`→`host.*`/`ca.crt`） | AC-3,AC-4,AC-5,AC-7 |
| 3 | `libs/tls_keygen.c:751` | 路径统一 | `handle_create/ca/sign` 中 `snprintf("%s_host.key", algo)` 改为复用 `common.h` 常量（`CERT_FILE_*` 分支），生成仍优先新前缀，读取兼容双格式 | AC-8 |
| 4 | `libs/tests/tls_cert_test.c:884` | `main` 前新增 6 用例 | 新增 `build_server_profiles / build_client_profile / init_server_from_cert_dir / init_client_from_cert_dir / ed25519_compat_has_prefix / ed25519_compat_no_prefix`，覆盖 AC-1/2/3/4/7；不再含 `explicit_single_profile` | AC-1,AC-2,AC-3,AC-4,AC-6,AC-7 |
| 5 | `rpc/rpc-config.cpp:181` | `rpc_init_config` 尾 | 补 `cert_dir` 的 `sec_resolve_str(...,RPC_TLS_CERT_DIR_ENV,DEFAULT_CERT_DIR)` | AC-3,AC-5 |
| 6 | `rpc/rpc-io.cpp:133` | `rpc_handshake_client_negotiate` | 删除显式 `client_cert/client_key` 分支与栈局部拷贝，仅 `cert_dir+algorithm+ca_cn` 单路径，统一 `init/handshake/cleanup` | AC-4,AC-5 |
| 7 | `rpc/main.cpp:417` / `rdbcomm/rdbcommd-main.c:352` / `rpc/rpc-config.h:31` | 服务端调用点精简 | `rpc/main.cpp` 删除 `hs_algorithm_name/tool_algorithm` 单算法甄别与 `ca_cert/server_cert/server_key` 手填，改为 `server_opts{mtls_enabled=1, cert_dir}`；`rdbcommd-main.c` 同步；`rpc-config.h` 删除 `ca_cert/server_cert/server_key` 存量字段（按需） | AC-5 |

> `libs/tls_cert.h` 不改接口，仅在 1/2 落地后视需补 `ca_cn` 校验注释；`tls_cert_init_*_from_cert_dir` 保持保留。

## 2. 分步实施（A2 测优循环）

### 切片 1 — AC-1 `build_server_profiles`
- **先写测试**：`TEST(tls_cert_build_server_profiles)` 断言 `count==2`，`profiles[0].algorithm==TLS_SM4_GCM_SM3` 且 `ca0` 后缀 `sm2_ca.crt`，`profiles[1].algorithm==TLS_AES_256_GCM_SHA384` 且 `ca1` 后缀 `ca.crt`（或 `ed25519_ca.crt` 新前缀），`cert0/key0` 与 `cert1/key1` 分别为对应 `sm2_host.*` / `host.*`，非法 `NULL/""` 返回 `INVALID_PARAM`。
- **再实现**：`common.h` 统一常量后 `tls_cert.c:191` 改复用常量；仅跑测试显绿。
- **验证**：`xmake build tls_cert_test && CERT_DIR=/home/black/Public/aio/aio-tools/6200/F/139/libs/tests/certs ./build/linux/x86_64/debug/tls_cert_test 2>&1 | grep -E "RUN_TEST.*build_server|PASSED|Failed"`

### 切片 2 — AC-2 `build_client_profile` + AC-8 路径统一预检
- **先写测试**：`TEST(tls_cert_build_client_profile)`：`SM4+ca_cn`→`sm2_ca.crt + my-ca/host.*`，`AES+ca_cn`→`ed25519_ca.crt` 优先回退 `ca.crt` + `my-ca/host.*`；`ca_cn` 为空或含 `a/b`/`..`→`INVALID_PARAM`；非法 `NULL/"" cert_dir` 与非法 `algorithm` 亦 `INVALID_PARAM`。另预检 `grep -rn CERT_FILE libs/common.h | grep ed25519` 非空且 `grep -rn "%s_host.key" libs/tls_keygen.c` 为 0。
- **再实现**：在 `build_client_profile:212` 前置 `ca_cn` 必填与字符集校验；`tls_keygen.c` 改复用 `common.h`。
- **验证**：同切片 1，`grep tls_cert_build_client_profile`。

### 切片 3 — AC-3/AC-4 `init_*` 强制 `cert_dir` + AC-7 双格式兼容
- **先写测试**：`TEST(tls_cert_init_server_from_cert_dir)` 非法 `NULL/""`→`INVALID_PARAM`，真实 `CERT_DIR` 下 `TLS_CERT_OK` 且双 `SSL_CTX` 非空互异；`TEST(tls_cert_init_client_from_cert_dir)` 非法 `NULL/"" cert_dir` 与空 `ca_cn/algorithm`→`INVALID_PARAM`；`TEST(ed25519_compat)` 分别在仅无前缀与仅有前缀的临时 `cert_dir`（`mktemp -d` + 拷贝）下 `init_server` 均 `TLS_CERT_OK`。
- **再实现**：`tls_cert.h/c` 精简 options 删 `profiles`，`rpc-config.cpp` 补 `cert_dir`，`tls_cert.c` 拆 `LOAD_KEY`、 `cert_dir` 必填校验并加双格式回退（`stat` 或二次 `load` 尝试）。
- **验证**：`grep -rn "profiles\[" libs/tls_cert.h | test $? -ne 0`；`CERT_DIR=... ./build/.../tls_cert_test` 23 用例全绿。

### 切片 4 — AC-5 调用点收敛与静态检查
- **实现**：`rpc-io.cpp` 单路径化（见 1-#4）；`rpc/main.cpp:417` 确认 `cert_dir` 分支注释。
- **验证**：
  ```bash
  grep -n "getenv" libs/tls_cert.c; test $? -ne 0 # 预期 0 命中
  grep -rn "rwlock\|pthread_rwlock" libs/tls_cert.c; test $? -ne 0
  grep -c "tls_cert_init_client" rpc/rpc-io.cpp | grep -q "^1$"
  xmake build 2>&1 | tail -5 | grep -q "build ok"
  ```

### 切片 5 — AC-6 回归
- **验证**：
  ```bash
  CERT_DIR=/home/black/Public/aio/aio-tools/6200/F/139/libs/tests/certs ./build/linux/x86_64/debug/tls_cert_test
  CERT_DIR=/home/black/Public/aio/aio-tools/6200/F/139/libs/tests/certs ./build/linux/x86_64/debug/rpc_handshake_test 2>&1 | tail -20
  ```

## 3. 全量与审查（A3-A4）

- A3：无独立 `make test` 时以 `tls_cert_test + rpc_handshake_test` 为最宽覆盖，报告中注明“受限于证书目录前置”；`tls_keygen` 路径统一后以 `grep -rn CERT_FILE` 校验无硬编码。
- A4 双轴：标准轴（`secure-coding` + `testing-strategy`）查 `LOAD_KEY` 区分、`ca_cn` 注入、双格式回退、单路径可审计；规范轴对照 `prd.md` 8 条 AC 逐条映射。

## 4. 收尾（Z1-Z4）

- Z1 登记 evidence：`test-suite-result`（`tls_cert_test` 全绿 + 双格式兼容日志）、`static-scan`（`grep getenv/lock` 空 + `grep "%s_host.key" tls_keygen.c` 空 + `CERT_FILE` 统一）、`build-result`（`xmake build ok`）、`review-report`（双轴报告）。
- Z2 `convergence.json` 已有 `task identity is unique and immutable`，Z2 时追加 `convergence-map` 使 `AC-1..8`→`evidence ID` 映射完整，再 `python3 $PDCA_HOME/scripts/seam_contract.py prd.md --base-dir /home/black/Public/aio/aio-tools/6200/F/139` 二次校验。
- Z3 仅提交 7+1 文件，`git add libs/common.h libs/tls_cert.h libs/tls_cert.c libs/tls_keygen.c libs/tests/tls_cert_test.c rpc/rpc-config.cpp rpc/rpc-io.cpp rpc/main.cpp rdbcomm/rdbcommd-main.c rpc/rpc-config.h`，`feat(tls)!: T0342 force cert_dir, ed25519 dual-format, unify paths`（`!` 标记不兼容）。
- Z4 `transition-phase.py --to check`。

## 5. 风险与回退

- 证书目录缺失致 AC-3 假红：前置 `ls libs/tests/certs/sm2_ca.crt libs/tests/certs/ca.crt` 检查。
- `ca_cn` 校验若入本任务则为小范围行为变更，回归需补 `ca_cn="../../etc"` 用例；若排期紧则标 `T0343` 后续，不阻塞本次。
- 回退：`bash $PDCA_HOME/scripts/rollback-phase.sh pdca/tasks/0822-tls-cert-init-api` + `git restore` 四文件。

## 6. 不做之事（重申范围外）

- 不改握手帧、不改 `sec_*` 签名、不做证书轮转/热重载、不新增 lock。
