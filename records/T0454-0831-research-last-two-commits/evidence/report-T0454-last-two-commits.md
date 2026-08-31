# 最近两次提交调研报告（T0454）

> 任务：T0454-0831-research-last-two-commits | 仓库：aio-tools/6200/F/139 | 基线：HEAD=6195ba5d, HEAD~1=740d55f0 | 日期：2026-08-31

## 1. 摘要

- **6195ba5d（B-T0451，2026-08-31）**：2 文件 33 行，修复 `libs/tls_keygen.c` 签发链路 UAF 与序列号硬编码，`tls_keygen 1.0.0.1->1.0.0.2`。
- **740d55f0（F-139，2026-08-28）**：4180 文件 +1319731/-3074，squash 合并 `0bf741f8..fef11220` 区间 10+ 子提交，TLS/mTLS 全栈、配置收口、fail-closed、oss 集成等一次交付。
- **关联**：引入-修复链，重叠仅 `libs/tls_keygen.c` 与 `xmake.lua`；无并行特性冲突。
- **证据链**：T0451 已归档（conclusion confirmed），回归通过。
- **本体**：新增 `ontology/pitfall/tls-keygen-sign-uaf-serial.md`，`ontology-validate` 通过。

## 2. 6195ba5d 还原（AC-1）

### 2.1 变更清单

```
libs/tls_keygen.c | 35 ++++++++++++
xmake.lua         | 2 +-
 2 files changed, 33 insertions(+), 4 deletions(-)
```

- `libs/tls_keygen.c:16-18`：`#include <openssl/rand.h>`, `<time.h>`
- `libs/tls_keygen.c:553-600`：`tls_keygen_sign_with_algo` 签发链路重构
- `xmake.lua:20`：`tls_keygen_version 1.0.0.1 -> 1.0.0.2`

### 2.2 根因

**R1 UAF（P0，必现）** `libs/tls_keygen.c:537-575`：

```c
EVP_PKEY *req_pkey = X509_REQ_get_pubkey(req);
X509_REQ_verify(req, req_pkey);
EVP_PKEY_free(req_pkey);          // 554 释放
X509 *cert = X509_new();
ASN1_INTEGER_set(...,2);
X509_set_pubkey(cert, req_pkey);  // 575 up_ref 野指针
```

`X509_set_pubkey` 内部 `EVP_PKEY_up_ref`，堆 UAF 导致 `pubkey 与 CSR 不一致`、`error 7 signature failure`。单次偶过，连续 4 次签发（sm2/ed25519×server/client）或 ASAN 必现。

**R2 序列号硬编码 2（P1）** `564`：

```c
ASN1_INTEGER_set(X509_get_serialNumber(cert), 2);
```

同 CA 下 4 张 host 证书序列号均为 2，违背 PKI 唯一性。

**R3 文件前缀隔离**：`sm2_host.*` vs `ed25519_host.*` 已隔离，非覆盖；问题在签发逻辑非路径。

### 2.3 修复

- **UAF**：`free` 延后至 `X509_set_pubkey` 之后，失败分支补 free，`cert==NULL` 分支亦补 free。
- **序列号**：`RAND_bytes(8)` 拼 63 位正整数，`&0x7fffffffffffffff`，为 0 时回退 `time^pid^random`，`ASN1_INTEGER_set_int64`。

```c
if (X509_set_pubkey(cert, req_pkey)!=1) { EVP_PKEY_free(req_pkey); ... }
EVP_PKEY_free(req_pkey);
```

### 2.4 验证

- 按用户原序列 10 条命令重放：bundled openssl verify SM2 OK×2，system verify ed25519 OK×2，pubkey 一致 4/4，serial 唯一 4/4。
- `libs/tests/tls_keygen_test` 10 passed，`test/tls_test.sh` 4/4 passed，`xmake build` ok。
- 风险低，仅 sign 链路；随机序列号无存量断言依赖（已排查）。

### 2.5 版本

- `tls_keygen_version 1.0.0.1 -> 1.0.0.2`（patch +1，符合“仅 +1”归一要求）

## 3. 740d55f0 还原（AC-2）

### 3.1 规模与性质

- `4180 files changed, 1319731 insertions(+), 3074 deletions(-)`，含 `third_party/openssl4` 全量导入（约 130 万行）。
- squash 合并 `0bf741f8..fef11220`，等价于 F-139 需求单次交付，非日常迭代。

### 3.2 子提交拆解（0bf741f8..fef11220）

| 顺序 | hash | 主题 |
|------|------|------|
| 1 | 63c8aae2 | KEY_LEN 缺失 |
| 2 | acbf4953 | 配置加载统一收口至 init_config 并修复 reload 边界 |
| 3 | f24cffd3 | dmsbtex/libobk .so 入口补齐 rdb-config store 加载（pthread_once 幂等） |
| 4 | be2aa914 | 全局算法兜底 key 由 ciphersuites 统一为 tls_algorithm |
| 5 | f7adb820 | logger 重复注册 fork 回调 |
| 6 | 4cb4a1cb | mTLS 证书缺失 fail-closed |
| 7 | 75e9ddbc | mTLS 指定算法证书异常 fail-closed |
| 8 | d7261231 | tls-keygen 默认目录不存在 CA 失败(code:-3) |
| 9 | 8f8943c8 | tls-keygen 创建失败错误码可读短语 |
| 10 | fef11220 | aio-oss server 致命错误显式化 |
| ... | 4ef9c5c1 等 | TLS/mTLS 全栈实现与演进整合 |

### 3.3 核心分类

1. **TLS/mTLS 全栈**：`libs/tls_cert.c/h`（1320 行变更）、`libs/tls_keygen.c`（1210 行）、`libs/hs_algorithm.c` 新增、`libs/rpc-net.c/h`、`libobk/lib/sbt/libobk.c` 等；sm2/ed25519 双算法、OpenSSL4 国密、SAN 修复。
2. **rpc 安全开关进程上下文**：`libobk/include/protocol.h`、`dmsbtex/network.c` 等，`sec_resolve` 收敛为进程上下文字段。
3. **oss HTTPS 开关化**：`oss/` 新目录 30+ 文件，Go `oss/cmd/tls.go`、`server.go` 等，默认 HTTP，参配开启 HTTPS。
4. **配置收口**：`libs/rdb-config.c/h`（1078 行）、`fs-backup/*/config.cpp` 等，统一收口 `init_config`，修复 reload 边界，store 加载补齐。
5. **fail-closed**：mTLS 启用且证书缺失/算法异常时启动失败（4cb4a1cb、75e9ddbc），`aio-oss server` 致命错误显式化。
6. **xmake 单测接入**：`libs/tests/xmake.lua`、`dmsbtex/test/session_test.c` 等，`tls_keygen_test` 等接入 `xmake test`。
7. **其他**：`logger.c` fork 回调、`common.c/h`、`cfg_path.h` 等。

### 3.4 版本矩阵（相对 fe9d4364 均仅 +1，符合归一）

| 组件 | 前 | 后 | 说明 |
|------|----|----|------|
| libobk | 1.0.0.0 | 1.0.0.1 | 修正误跳 1.0.1.7 |
| rpc | 3.6.4.19 | 3.6.4.20 | |
| dmsbtex | 1.1.0.1 | 1.1.0.2 | |
| rdbcomm | 1.0.1.8 | 1.0.1.9 | |
| tls_keygen | 1.0.0.0 | 1.0.0.1 | 首版集成后续被 6195ba5d 升至 1.0.0.2 |
| oss | - | 1.0.0.1 | 新增 |
| rdbcomm/rpc 等 | | | 均 +1，未跳版 |

## 4. 关联分析（AC-3）

### 4.1 重叠文件

```
git diff --name-only 740d55f0~1 740d55f0 | grep -x ...
git diff --name-only 6195ba5d~1 6195ba5d
# 交集仅：
libs/tls_keygen.c
xmake.lua
```

其余 4178 文件无交集。

### 4.2 引入-修复链判定

- **引入**：740d55f0 对 `libs/tls_keygen.c` 的 1210 行重构引入 UAF 与硬编码序列号（见 `git show 740d55f0:libs/tls_keygen.c | sed -n '551,575p'` 与 `HEAD~1` 对比）。
- **修复**：6195ba5d 在同一函数 `tls_keygen_sign_with_algo` 以 35 行修复。
- **证据**：`740d55f0` 含 SAN 修复等 tls-keygen 改进，但签发链路缺陷未被该次测试覆盖；`6195ba5d` 的 T0451 以双算法连续签发为复现手段命中。

### 4.3 提交性质差异

- 740d55f0：需求整合型（F-139），含第三方大库导入，评审需穿透 squash 区间。
- 6195ba5d：缺陷修复型（B-T0451），聚焦单函数，commit message 含完整问题/根因/方案/影响/复现/验证/回滚。

## 5. PDCA 证据链与复现命令（AC-4）

### 5.1 PDCA 链

- T0451-0831-tls-keygen-uaf-fix：`Completed/archived`，prd.md 含 R1/R2/R3 根因图，conclusion.md 三 AC 均通过，verdict confirmed。
- T0454-0831-research-last-two-commits：本次调研，prd.md 6 AC，新增本体 pitfall。

### 5.2 可复现命令

```bash
# 1. 看最近两次提交
git log --oneline -5
# 6195ba5d B-T0451 ...
# 740d55f0 F-139 ...

# 2. 看 6195ba5d 变更
git show --stat HEAD
git diff HEAD~1 HEAD -- libs/tls_keygen.c
git show HEAD:libs/tls_keygen.c | sed -n '553,610p'

# 3. 看 740d55f0 规模与子提交
git show --stat HEAD~1 | head -n 80
git log --oneline 0bf741f8..fef11220
git diff --name-only 740d55f0~1 740d55f0 | wc -l  # 4180

# 4. 验证重叠
comm -12 <(git diff --name-only 740d55f0~1 740d55f0 | sort) <(git diff --name-only HEAD~1 HEAD | sort)

# 5. 验证 UAF 修复前后对比
git show HEAD~1:libs/tls_keygen.c | sed -n '551,580p'
git show HEAD:libs/tls_keygen.c   | sed -n '551,610p'

# 6. 复现 UAF（需在修复前 commit 检出）
rm -rf /opt/aio/cfg/certs/
xmake run tls-keygen ca -n MySM2RootCA -a sm2
xmake run tls-keygen ca -n MySM2RootCA -a ed25519
xmake run tls-keygen create -a sm2 && xmake run tls-keygen sign -a sm2
xmake run tls-keygen create -a ed25519 && xmake run tls-keygen sign -a ed25519
xmake run tls-keygen create -n MySM2RootCA -a sm2 && xmake run tls-keygen sign -n MySM2RootCA -a sm2
xmake run tls-keygen create -n MySM2RootCA -a ed25519 && xmake run tls-keygen sign -n MySM2RootCA -a ed25519
openssl verify -CAfile /opt/aio/cfg/certs/sm2_ca.crt /opt/aio/cfg/certs/sm2_host.crt
```

## 6. 风险评估与建议（AC-5）

### 6.1 6195ba5d 风险

- **低**：仅 sign 链路，失败分支已补释放，无并发新增；随机序列号不影响存量固定断言。
- **遗留**：`random()` 回退低熵，仅兜底，主路径 `RAND_bytes` 足够；建议后续 `srandom` 或直接 `BN_rand`。
- **环境差异**：SM2 在系统 openssl 3.6 vs bundled 4.0.1 跨库 verify 失败属已知环境限制，bundled 内自洽，不影响结论。

### 6.2 740d55f0 风险

- **高**：squash 一次合 4180 文件，评审盲区大；虽版本均 +1 归一，但第三方 openssl4 导入使 diff 统计失真，真实业务变更约数千行而非百万行。
- **建议**：后续 F 类需求避免单次 squash 全量交付，按子提交分批合入；或在 squash message 中显式列区间 hash 供穿透审查（本次已列 0bf741f8..fef11220，可复用）。

### 6.3 流程建议

- **调研收敛性**：纯 research 不沉淀本体将导致重复调研。本次已以 `pitfall/tls-keygen-sign-uaf-serial.md` 沉淀，后续同类签发链路变更可直接关联该 pitfall，避免再调研。
- **Plan Grill 补位**：建议在 `skill-grilling` 的 Plan→Do 视角追加“调研是否需沉淀本体”前沿问题，或在 `research` 的 PRD 模板中默认提示 `ontology_fragment` 候选。

## 7. 结论

两次提交构成“F-139 全栈交付 → B-T0451 缺陷修复”闭环，修复精准且验证充分；F-139 的 squash 形态需穿透审查。本次调研以 6 AC 闭环并沉淀 pitfall 本体，满足收敛要求。

---
*证据：git log/show/diff 均可复现；PDCA：T0451 archived, T0454 do；本体：ontology/pitfall/tls-keygen-sign-uaf-serial.md validate OK*
