# T0451 结论

## 逐项核验

- AC-1 UAF 修复后连续双算法签发证书均可通过 openssl verify 与 mtls 自测 — 通过
  - 证据 AC1: libs/tls_keygen.c diff（UAF 延后 free，X509_set_pubkey 前 req_pkey 有效）
  - 验证：按用户原序列生成 4 host 证书，bundled openssl verify SM2 OK×2，system verify ed25519 OK×2，pubkey 与 CSR 一致 4/4
  - 根因：libs/tls_keygen.c:556 EVP_PKEY_free(req_pkey) 在 X509_set_pubkey 前释放，导致野指针；并发/多次签发放大堆扰动

- AC-2 序列号唯一性修复 — 通过
  - 证据 AC2
  - 验证：4 host 证书 serial 均不同（随机 63 位，之前硬编码 2）

- AC-3 回归测试通过 — 通过
  - 证据 AC3
  - 验证：libs/tests/tls_keygen_test 10 passed，test/tls_test.sh 4/4 passed，xmake build ok

## 遗留说明

- SM2 在系统 openssl（3.6）下 verify 失败属 bundled 4.0.1 vs 系统库跨库差异，bundled 内自洽（OK）；非并发文件覆盖或 UAF 所致，已在结论中说明，不影响并发修复的判定。

## 判定

- verdict: confirmed
