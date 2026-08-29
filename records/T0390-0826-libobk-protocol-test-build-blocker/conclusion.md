# 结论 — T0390：修复 libobk_protocol_test release 构建阻断

## 背景（来自重新审查）

T0389 收尾后做"重新审查"，原候选 #1（`tls_cert.c` `-Werror=stringop-truncation`）经实证已**过时**：代码早已改为 `safe_strcpy`，且提交 `57fca54` 已修复 xmake test 的 `-Werror` 阻断，重编 `tls_cert.c` 仅余无关弃用告警并正常归档。真正现存的构建阻断是 #3：`libobk_protocol_test`。

## 根因

`libobk/test/protocol_test.c` 的 `main()` 用 `assert()` 完成 `socketpair` 初始化与 `_baseSend`/`_baseRecv` 结果校验。release 构建 `-DNDEBUG` 使 `assert` 展开为空：
- `socketpair` 调用被移除 → `fds` 未初始化即被使用 → `-Werror=uninitialized`；
- `_baseSend`/`_baseRecv` 返回值仅被 `assert` 消费，断言移除后调用被死代码消除 → `head`/`body`/`expect` 判定未使用 → `-Werror=unused-variable`。

被测逻辑（`_baseSend`/`_baseRecv`/`obk_hs_session_init_plain`，由 `sbt` 库提供）正确无误，问题仅在测试自身的错误检查方式对 release 不健壮。

## 修复

将全部 `assert(...)` 改为真实错误检查（`if (...) { fprintf(stderr,...); return 1; }`），使 `fds` 在 release 下仍被无条件初始化、`_baseSend`/`_baseRecv` 返回值被显式比较。仅补 `#include <stdio.h>`，**未改动任何被测逻辑**。

## 验收判定

- **AC-1** ✅ `libobk_protocol_test` 在 release（NDEBUG）构建下编译链接通过，无 `-Werror=unused-variable` / `-Werror=uninitialized`——证据：`protocol_test_release`
- **AC-2** ✅ 测试仍正确校验协议收发；debug 与 release 构建均 `build ok` 且运行 `exit 0`——证据：`protocol_test_release`、`protocol_test_debug`
- **AC-3** ✅ 未改动 `_baseSend`/`_baseRecv`/`protocol.c`，仅修正测试自身的错误检查方式（diff 仅触及 `protocol_test.c`）——证据：`impl-diff`

## 收敛

见 `evidence/t0390-convergence-map.json`：单一收敛点（release/debug 均通过且被测逻辑不变）由 `impl-diff` + `protocol_test_release` + `protocol_test_debug` 支撑。

## 结论

修复达成：`libobk_protocol_test` 在 release（NDEBUG）构建下的 `-Werror` 阻断消除，debug/release 行为一致，协议收发校验功能不变。建议 verdict=**confirmed**。
