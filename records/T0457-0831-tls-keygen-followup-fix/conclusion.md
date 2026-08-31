# T0457 结论

## 逐项核验

- AC-1 重复include去重 — 通过
  - 证据 ev-diff: tls_keygen_followup.diff 去除第二处 `sys/stat.h`，新增 `stdint.h`/`inttypes.h`

- AC-2 回退熵去random改clock_gettime+uint64 — 通过
  - 证据 ev-diff: `random()` 移除，改 `clock_gettime(CLOCK_REALTIME)` 纳秒熵 + `&serial` 栈地址 + `getpid`，无裸 `random` 依赖

- AC-3 有符号左移UB消除 — 通过
  - 证据 ev-diff: `long long serial`→`int64_t serial`+`uint64_t u` 累积，`u&=0x7fffffffffffffffULL` 后转 `int64_t`

- AC-4 X509_set_pubkey失败诊断可观测 — 通过
  - 证据 ev-diff: 失败分支新增 `dump_openssl_errors("X509_set_pubkey")` 与回退分支 `dump_openssl_errors("RAND_bytes fallback")`

- AC-5 版本+1且回归通过 — 通过
  - 证据 ev-test: test.log `xmake test 51/51 passed`，`xmake build tls-keygen` ok；`xmake.lua:20` `1.0.0.2→1.0.0.3`
  - 本体：`ontology/pitfall/tls-keygen-sign-uaf-serial.md` 已同步更新（T0457 加固说明），`ontology-validate` OK, `islands 0`

## 判定

- verdict: confirmed
