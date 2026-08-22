# 实施计划 — rpc 混合/强制矩阵（T0344）

## 0. 执行边界

- 本计划仅描述 Do 应做之事，不在此阶段写代码/改文件。
- Do 以 `development` A 路径执行：A2 测优 → A3 全量 → A4 双轴审查 → Z1-4 收尾。
- 变更集冻结为 rpc 目录 3+1 文件，`libs/` 不改（T0342 已交付）。

## 1. 变更清单（冻结）

| # | 文件 | 行号锚点 | 改动 | 对应 AC |
|---|------|----------|------|---------|
| 1 | `rpc/main.cpp:409` | `server sctx` | `cert_dir` 有即建 `tls_ctx`（`mtls` 仅定强制），`server 0` 有 `sctx` 即可按 `want_mtls` 回 `MTLS` | AC-1, AC-2 |
| 2 | `rpc/rpc-io.cpp:82` | `rpc_ensure_handshake` | 去全局短路，`want_mtls=0` 直通明文不发 `HS`，`1` 即发 | AC-1, AC-2 |
| 3 | `rpc/rpc-io.cpp:133` | `rpc_handshake_client_negotiate` | `HS_OK_PLAIN` 直通，`HS_OK_MTLS` 三元组校验失败不回退 | AC-3, AC-4, AC-5 |
| 4 | `rpc/tests/rpc_handshake_test.cpp` | `4 象限` | 新增 `AC-1..5` 矩阵用例 | AC-1..5 |

## 2. 分步实施（A2 测优循环）

### 切片 1 — AC-1 `server 0 x want_mtls=0` 明文无 HS
- **先写测试**：`server 0` + `want_mtls=0` 不发 `HS` 直通 `plain` 成功。
- **再实现**：`rpc-io.cpp:82` `want_mtls=0` 短路，`rpc-server.cpp` 首帧即业务。
- **验证**：`grep AC-1.*no-HS`.

### 切片 2 — AC-2 `server 0 x want_mtls=1` 按需密文
- **先写测试**：`server 0` + `want_mtls=1`（`cert_dir` 完备）→ `HS_OK_MTLS` 且 `tls` 成功。
- **再实现**：`rpc-io.cpp:82` 发 `HS`，`server` 按需回 `MTLS`。
- **验证**：`grep AC-2.*MTLS`.

### 切片 3 — AC-3 `server 1 x client 1` 强制密文
- **先写测试**：`server 1` + `client 1` → `HS_OK_MTLS` 且 `tls` 成功。
- **再实现**：`rpc-server.cpp` 强制 `MTLS`，`rpc-io` 三元组校验。
- **验证**：`grep AC-3`.

### 切片 4 — AC-4/5 缺证书失败不回退
- **先写测试**：`server 1` 缺 `cert_dir`/`ca_cn` → 失败不回退。
- **再实现**：`rpc-io.cpp:133` 三元组任一空即 `return -1`。
- **验证**：`grep AC-4.*fail`.

## 3. 全量与审查（A3-A4）

- A3：`rpc_handshake_test 5 用例` 全绿即通过。
- A4 双轴：`HS_OK_MTLS` 仅 `want_mtls` 分支，`ca_cn` 空不触 `tls`。

## 4. 收尾（Z1-Z4）

- Z1 `test-suite`/`static-scan`/`build`/`review`，Z2 `convergence` 5 AC 映射，Z3 `git add rpc/` 4 文件，Z4 `→ check`。

## 5. 风险与回退

- `cert_dir` 空时 `server 0` 固定 `PLAIN`，前置 `ls host.crt`。
- 回退：`rollback-phase.sh` + `git restore rpc/`.

## 6. 不做之事

- 不改 `libs/`，不改 `sec_*`，不引入重连。
