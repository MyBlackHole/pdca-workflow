# tls-keygen: 创建 CA 失败错误码信息不明确，需补充可读原因 — 规格文档

## 问题陈述

- **现状**: `tls-keygen ca/create/sign` 子命令在底层失败（写文件权限不足、签名失败、CSR 损坏等）时，handler 仅打印 `Error: failed to create CA (code: -3)` 这类"错误码数字"，用户无法判断失败发生在哪个环节（写密钥？写证书？签名？）、目标路径是什么、系统原因是什么（目录不存在 / 权限拒绝 / 磁盘满）。
- **目标**: 所有失败返回点携带人类可读原因，至少包含：失败环节短语、目标路径、系统错误原因（strerror）；handler 不只用裸数字。**关键约束：错误码枚举值（如 `-3`）对使用者无意义，汇总行必须把该码的含义用自然语言写清楚，让使用者无需查源码即可理解。**
- **差距**: 叶函数 `fopen` 失败直接 `return TLS_KEYGEN_ERR_WRITE`，无路径/errno 上下文；handler `fprintf("... (code: %d)", ret)` 把可读责任推给用户，且 `-3` 这类内部枚举使用者根本无法理解其含义。
- **差距**: 叶函数 `fopen` 失败直接 `return TLS_KEYGEN_ERR_WRITE`，无路径/errno 上下文；handler `fprintf("... (code: %d)", ret)` 把可读责任推给用户。

## 解决方案

从用户视角：运行任何 tls-keygen 子命令失败， stderr 给出可直接定位的英文/中文可读信息，例如：

- 写密钥失败：`Error: cannot open <path> for writing: Permission denied`
- 写证书失败：`Error: cannot open <path> for writing: <strerror>`
- handler 汇总：`Error: failed to create CA: write error (code: -3)`（短语随返回码映射）

即：在底层写/读失败点补充 `路径 + strerror(errno)`，在 handler 层把返回码映射为可读短语（write/param/ca-create/sign/key-mismatch 等），两者并存。

## Seam 分析

### 测试接缝
- 黑盒接缝：以非 root 身份运行 `tls-keygen` 二进制，构造可复现的写失败，断言 stderr 含可读原因而非纯数字。
- 白盒接缝（可选）：对新增 `errcode -> 短语` 映射函数补充单测。

### 声明的测试接缝
- seam: test/tls_test.sh -> libs/tls_keygen.c （tls-keygen CLI 错误输出可读化）

### 验收可测性
- 非 root 下 `--key /root/x.key` 触发 EACCES，stderr 必须出现 `/root/x.key` 与 `Permission denied` 文本，且不得仅出现 `code: -3`。
- 退出码仍为非 0（行为不变）。
- 成功路径的 stdout 文本不受影响。

## 用户故事

1. 作为运维，执行 `tls-keygen ca` 失败时能立刻从报错看到"哪个文件/为什么"，而不必查源码错误码表。
2. 作为开发者，新增失败返回点时能复用统一的可读化输出，避免再次出现裸数字。

## 实现决策

- **新增可读化辅助**：集中一处把 `TLS_KEYGEN_ERR_*` 枚举映射为"含义短语"（如 `-3` → `failed to write output file`），handler 汇总行形如 `Error: failed to create CA: failed to write output file (code: -3)`——**短语本身解释该码含义**，使用者无需查表。
- **叶函数失败点补充上下文**：所有 `fopen` 失败返回前，打印 `cannot open <path> for <mode>: <strerror(errno)>`；需引入 `<errno.h>` 与 `strerror`。
- **不改动**：证书/密钥算法与 ASN.1 扩展逻辑、成功路径业务输出、CLI 参数解析。
- 改动集中在 `libs/tls_keygen.c`；`common.h`/单测无需动（除非新增映射函数单测）。

## 测试决策

- 黑盒优先：复用 `test/tls_test.sh`，新增在删除/不可写场景下 grep 可读报错。
- 不测实现细节（具体 fprintf 格式串），只测"stderr 含路径与原因、不含裸数字码"。
- 既有 `libs/tests/tls_keygen_test.c` 不受影响（测的是 cn/san 校验）。

## 验收标准

- [ ] AC-1: 非 root 运行 `tls-keygen ca -n X -a sm2 --key /root/x.key`，stderr 含字符串 `/root/x.key` 且含 `Permission denied`（或对应 strerror），且汇总行把 `-3` 的含义写成自然语言（如 `failed to write output file`），使用者无需查源码即可理解，**不得仅出现孤立 `code: -3` 数字**。
- [ ] AC-2: 同一命令退出码为非 0（失败语义不变）。
- [ ] AC-3: 成功路径（默认目录可写）stdout 仍打印 `Creating CA (sm2)... done` 等原样文本，无回归。
- [ ] AC-4: `create`/`sign` 子命令在写失败场景同样输出可读路径+原因（统一可读化覆盖三个写点）。

## 范围外

- 不新增子命令或参数。
- 不改变错误码枚举值（仅改展示）。
- 不引入国际化/多语言框架。

## 备注

- 关联前置修复 B-3988（默认目录缺失导致 code:-3）；本次是该失败路径的"可读化"收尾，使即便仍失败也能自解释。
- 版本号随修复 bump（1.0.0.5 -> 1.0.0.6）。
