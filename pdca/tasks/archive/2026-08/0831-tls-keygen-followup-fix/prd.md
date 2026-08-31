# 修复 tls-keygen 回退熵、类型UB与诊断缺失等遗留

## 背景

T0454 review 指出 6195ba5d（B-T0451，`libs/tls_keygen.c:19-21,566-604`）修复方向正确但遗留 MEDIUM/LOW 缺陷；740d55f0 为流程类遗留，本次仅收口 6195ba5d 的代码遗留。需小 patch `1.0.0.2→1.0.0.3` 闭环。

## 验收标准

- [ ] AC-1：`libs/tls_keygen.c:9,21` 重复 `sys/stat.h` 已去重（仅保留一处）
- [ ] AC-2：`libs/tls_keygen.c:568-584` 回退路径不再依赖 `random()/srandom`，改 `uint64_t` 累积、`clock_gettime(CLOCK_REALTIME)` 纳秒熵、`&serial` 栈地址扰动，`RAND_bytes` 失败可观测（`dump_openssl_errors`）
- [ ] AC-3：`libs/tls_keygen.c:572` 有符号左移 UB 消除（`uint64_t u` 累积再转 `int64_t`，`&0x7fffffffffffffffULL`）
- [ ] AC-4：`libs/tls_keygen.c:596-603` `X509_set_pubkey` 失败分支补 `dump_openssl_errors`
- [ ] AC-5：`xmake.lua:20` `tls_keygen_version 1.0.0.2→1.0.0.3`，`xmake test 51/51` 通过，`ontology-validate` 通过

## 非目标

- 不改 740d55f0 的 `rdb-config` 全局回退兼容性（文档声明即可），不改签发主路径 `RAND_bytes` 成功分支语义

## 关联本体节点

```
ontology:concept/pdca-task
ontology:pitfall/tls-keygen-sign-uaf-serial
```

## 风险

- 仅 `tls_keygen.c` 约 15 行，失败回退分支几乎不触发；主路径不变，回归风险低
