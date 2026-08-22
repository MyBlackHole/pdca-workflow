---
schema: pdca.asset/v1
id: T0342-0822-tls-cert-init-api
phase: check
source_ids: ["test-suite-v2", "static-scan", "build", "review"]
---

## 上下文

任务 T0342 目标为 `tls_cert` 初始化 API 的强制 `cert_dir` 单路径化与证书路径统一：服务端 `cert_dir` 双算法（SM4+AES）同时持有，客户端 `cert_dir+algorithm+ca_cn` 三元组，前者经 `common.h` 统一常量，后者经 `ED25519` 有前缀优先回退无前缀的双格式兼容。原 API 的 `profiles[2]` 显式手填与 `server/client` 前缀文件已移除，不兼容旧写法。

## 假设与结果

- **AC-1 `build_server_profiles`**：假设 `cert_dir` 构建产出 `count==2` 且 `sm2_ca.crt`/`ed25519_ca.crt` 区分。结果 `PASS` — `test-suite-v2` 中 `tls_cert_build_server_profiles` 断言 `profiles[0].algorithm==SM4` 且 `ca0` 含 `sm2_ca.crt`，`profiles[1]` 为 `AES` 且 `ca1` 含 `ed25519_ca.crt` 回退 `ca.crt`，非法参数返回 `INVALID_PARAM`。
- **AC-2 `build_client_profile`**：假设 `algorithm` 区分 `ca` 且 `ca_cn` 必填白名单。结果 `PASS` — `test-suite-v2` 中 `SM4+my-ca` 得 `sm2_ca.crt + my-ca/host.*`，`AES+my-ca` 得 `ed25519_ca.crt` 回退，`ca_cn` 空或含 `/`/`..` 返回 `INVALID_PARAM`。
- **AC-3 `init_server`**：假设 `cert_dir` 必填且双 `SSL_CTX` 非空互异，缺失 `LOAD_*` 不降级。结果 `PASS` — `tls_cert_init_server_from_cert_dir` 在 `libs/tests/certs`（`host.crt`/`ed25519_*`/`sm2_*` 均 ED25519/SM2 新生成）下 `TLS_CERT_OK` 且 `aes_ctx != sm_ctx`，`cert_dir` 空直接 `INVALID_PARAM`。
- **AC-4 `init_client`**：假设三元组必填且旧 `profiles` 已移除。结果 `PASS` — `tls_cert_init_client` 在 `cert_dir/algorithm/ca_cn` 透传下 `get_ssl_ctx != NULL`，空/非法返回 `INVALID_PARAM`，编译期 `grep profiles` 仅内部辅助。
- **AC-5 静态**：假设调用点仅 `cert_dir` 单路径且无 `getenv`/`lock`/`hardcode`。结果 `PASS` — `static-scan` 显示 `profiles` 仅内部 `out_profiles`，`grep "%s_host.key"` 0，`getenv/rwlock` 0，`rpc/main`/`rdbcommd-main` 无 `hs_algorithm_name` 单选，`rpc-io` 仅单 `init_client`。
- **AC-6 回归**：假设 `tls_cert_test` 8 用例全绿。结果 `PASS` — `test-suite-v2` 全绿，`rpc_handshake_test` 同步为 `cert_dir` 后通过，`build` 全量成功。
- **AC-7 双格式**：假设 `ED25519` 新旧目录双测均成功。结果 `PASS` — `tls_ed25519_dual_format` 在仅旧 `ca.crt/host.crt` 与仅新 `ed25519_*` 的临时目录双测均 `TLS_CERT_OK`。
- **AC-8 统一**：假设 `common.h` 唯一源且 `tls_keygen` 复用。结果 `PASS` — `static-scan` 显示 `CERT_FILE_ED25519_*` 5 常量存在，`tls_keygen.c` 硬编码 0，`grep CERT_FILE` 均指向 `common.h`。

## 分析

- 证据链闭环：`common.h` 5 常量新增 → `tls_cert.c` 的 `pick_ed25519_*` 回退与 `ca_cn` 校验 → `tls_keygen.c` 的 5 个 `keygen_*_file()` 复用 → 调用点 7 处收敛 → `test-suite-v2` 8 用例覆盖 `AC-1/2/3/4/7`，`static-scan` 覆盖 `AC-5/8`，`build` 覆盖 `AC-5/6`，`review` 全量映射。
- 关键决策有效：强制 `cert_dir` 消除双分支歧义，`ed25519` 双格式回退使滚动升级不中断（`host.crt` 新旧共存期均 `PASS`），`ca_cn` 白名单防路径遍历。
- 无未覆盖 AC：8 条均有证据或显式失败判定，符合 `convergence` 4 证据映射。

## 适用边界

- 仅 `cert_dir` 驱动，不支持显式 `profiles` 旧写法（`!` 不兼容）。
- `ED25519` 双格式回退仅 `ed25519_* → host.*`，`SM2` 单格式 `sm2_*`，不含 `server/client` 前缀（已从 `libs/tests/certs` 删除）。
- 证书轮转/热重载不在本轮，需另起 PDCA。

## 下一轮建议

- 清理残留 `sm2_client.crt` 的 `client` 前缀（若需彻底无 `client` 字面）或文档化其保留原因。
- 考虑抽 `tls_paths.h` 独立于 `common.h`，进一步收敛路径职责。
- 补充 `rdbcomm` 集成测试对 `host.crt` 新生成的回归（当前仅单元）。
