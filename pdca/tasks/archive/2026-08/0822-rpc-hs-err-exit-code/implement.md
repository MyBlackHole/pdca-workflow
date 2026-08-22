# 实施计划 — client HS_ERR 帧校验 + 项目内证书约束（T0346）

## 0. 执行边界

- 本计划仅描述 Do 应做之事，不在此阶段写代码/改文件。
- Do 以 `development` A 路径执行：A2 测优 → A3 全量 → A4 双轴审查 → Z1-4 收尾。
- 变更集冻结为 7 项：rpc-client.cpp、rpc-io.cpp、tls_cert.c（仅诊断分支）、mixed_mtls.cpp、mixed_mtls_integration.cpp、xmake.lua、certs 清理。工作区其余脏文件禁止随本次提交。

## 1. Stash 恢复策略（关键）

`stash@{0}` 混杂有效改动与违规内容，**禁止盲目 pop**：
- **选择性恢复**（checkout）：`rpc/rpc-client.cpp`、`rpc/tests/mixed_mtls.cpp`、`rpc/tests/mixed_mtls_integration.cpp`、`rpc/tests/xmake.lua`
- **丢弃**：`libs/tests/certs/client-001/002` 与 `sm2_client.*` 的删除记录——在新约束下重新执行 `git rm`

## 2. 变更清单（冻结）

| # | 文件 | 改动 | 对应 AC |
|---|------|------|---------|
| 1 | `rpc/rpc-client.cpp:966` | recv 后校验 `uiMT == MT_HANDSHAKE_RESP` → ErrorLog "server rejected" + `error_no = -(int)hs.result` + break | AC-1, AC-2 |
| 2 | `rpc/tests/mixed_mtls.cpp` | 加 `#include "../rpc-io.h"`（seam 契约） | 全部 |
| 3 | `rpc/tests/mixed_mtls_integration.cpp` | 删除 keygen 死代码与 `/tmp` 证书生成；证书固定 `libs/tests/certs`；AC-5 断言 client exit != 0 且 stderr 含 rejected | AC-1..AC-4 |
| 4 | `libs/tests/certs` 清理 | `git rm sm2_client.{crt,csr,key}`；删 `client-001/002/` 旧 RSA 目录 | AC-4 |
| 5 | `rpc/rpc-io.cpp:146` | client init 失败补日志：cert_dir/algorithm/ca_cn 实际值 | 可观察性 |
| 6 | `libs/tls_cert.c:614` handshake 失败分支（client 角色） | 补 `SSL_get_verify_result` 错误字符串 + 对端证书 subject/issuer 输出 | AC-5 |
| — | （已有）`rpc/rpc-server.cpp:340` 拒绝明文业务 ErrorLog | 已交付，本任务断言其存在 | AC-5 |

> 握手帧、协议版本不动。#6 触及 libs/tls_cert.c 仅限失败诊断分支，不改变行为。
> AC 编号对齐 PRD：AC-4=证书资产约束，AC-5=证书异常可观察性。

## 3. 分步实施（A2 测优循环）

### 切片 1 — Stash 选择性恢复 + certs 清理
- 恢复 4 代码文件；`git rm sm2_client.*`；删 `client-001/002` 目录
- 验证：`ls libs/tests/certs | grep -i client` 为 0

### 切片 2 — mixed_mtls_integration 项目内证书化
- 删 keygen/work 残留；certs 固定 `getenv("CERT_DIR") ?: "libs/tests/certs"`
- 编译通过

### 切片 3 — AC-1/AC-2 client 帧校验生效
- 真实进程：server1+client0+`-c true` → exit != 0 且 stderr 含 "server rejected"
- 回归：server0/client0 plain 通、server0/client1 MTLS 通、server1/client1 forced 通

### 切片 4 — 可观察性验证（AC-5）
- 构造 server 证书校验失败场景（client CA 不匹配），断言 client 日志含 verify_result 错误与 peer subject
- 构造 init 失败场景，断言 client 日志含 cert_dir/algorithm/ca_cn 实际值

### 切片 5 — 全量回归
- `mixed_mtls_test`（单测）+ `mixed_mtls_integration`（工具级）+ `tls_cert_test` 全绿

## 4. 收尾（Z1-Z4）

- Z1 evidence：`unit-quad` / `tool-integration` / `obs-log`（可观察性日志样本）/ `build` / `static-scan`
- Z2 convergence 4 AC 映射 + validate-convergence
- Z3 提交 5 文件，`fix(rpc): T0346 client HS_ERR 帧校验 + 测试项目内证书化`
- Z4 `transition --to check`

## 5. 风险与回退

- stash pop 冲突：改用 `checkout stash@{0} -- <file>` 逐文件恢复，失败则按本计划重写
- server 侧 ca_cn 返回依赖 `ED25519 Test CA/` 目录存在（已确认含 host.crt+host.key+ca.crt）
- 回退：`rollback-phase.sh` + `git restore` + 丢弃 stash

## 6. 不做之事

- 不改 libs 握手行为与协议帧（tls_cert.c 仅失败诊断分支）；不自动重试；不引入新配置项
