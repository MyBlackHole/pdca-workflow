# PRD — T0390：修复 libobk_protocol_test release 构建阻断

> 父任务：T0389（confirmed，已归档）。来源：T0389 收尾后的"重新审查"——原候选 #1（tls_cert.c `-Werror=stringop-truncation`）经实证已过时（代码已改 `safe_strcpy`，提交 `57fca54` 已修 xmake test 的 `-Werror` 阻断），故转向真实现存阻断 #3。

## 背景与问题

`libobk_protocol_test`（`libobk/test/protocol_test.c`，target 链接 `sbt` 库）在 **release 构建（`-DNDEBUG`）** 下编译失败：

```
libobk/test/protocol_test.c:17:24: error: 未使用的变量'head'   [-Werror=unused-variable]
libobk/test/protocol_test.c:18:14: error: 未使用的变量'body'   [-Werror=unused-variable]
libobk/test/protocol_test.c:20:13: error: 未使用的变量'expect' [-Werror=unused-variable]
libobk/test/protocol_test.c:22:9:  error: 'fds'未经初始化被使用   [-Werror=uninitialized]
```

## 根因

`protocol_test.c` 的 `main()` 用 `assert()` 完成两件事：
1. `assert(socketpair(...) == 0)` —— 初始化 `fds`；
2. `assert(_baseSend(...) == ...)` / `assert(_baseRecv(...) == ...)` —— 校验收发结果。

release 构建 `-DNDEBUG` 使所有 `assert` 展开为空：
- `socketpair` 调用被移除 → `fds` 从未初始化即被 `obk_hs_session_init_plain(&client, fds[0])` 使用 → `-Werror=uninitialized`；
- `_baseSend`/`_baseRecv` 的返回值仅被 `assert` 消费，断言移除后其返回值被丢弃，调用可能被死代码消除 → `head`/`body`/`expect` 被判定未使用 → `-Werror=unused-variable`。

被测逻辑（`_baseSend`/`_baseRecv`/`obk_hs_session_init_plain`）本身正确且已由 `sbt` 库提供，问题仅在测试自身的错误检查方式对 release 不健壮。

## 方案

将测试内所有 `assert(...)` 改为真实的错误检查：

```c
if (socketpair(AF_UNIX, SOCK_STREAM, 0, fds) != 0) {
    fprintf(stderr, "protocol_test: socketpair failed\n");
    return 1;
}
...
if (_baseSend(&client, &head, body, sizeof(body)) !=
    (int)(sizeof(activeioHeader) + sizeof(body))) {
    fprintf(stderr, "protocol_test: _baseSend mismatch\n");
    return 1;
}
if (_baseRecv(&server, packet, &expect, NULL) !=
    (int)(sizeof(activeioHeader) + sizeof(body))) {
    fprintf(stderr, "protocol_test: _baseRecv mismatch\n");
    return 1;
}
if (memcmp(packet + sizeof(activeioHeader), body, sizeof(body)) != 0) {
    fprintf(stderr, "protocol_test: payload mismatch\n");
    return 1;
}
```

效果：`fds` 在 release 下仍被无条件初始化；`_baseSend`/`_baseRecv` 返回值被显式比较，变量被真实使用；debug/release 行为一致。

## 验收标准

- [ ] AC-1: `libobk_protocol_test` 在 release 构建下编译链接通过（无 `-Werror=unused-variable` / `-Werror=uninitialized`）。
- [ ] AC-2: 测试仍正确校验协议收发（功能不变）；debug 构建同样通过（`xmake build libobk_protocol_test` 与常规 debug 构建均 exit 0）。
- [ ] AC-3: 不改动被测逻辑（`_baseSend`/`_baseRecv`/`protocol.c`），仅修正测试自身的错误检查方式。

## 声明的测试接缝

- seam: libobk/test/protocol_test.c -> libobk/lib/logic/oracleCmdTbl.c（`_baseSend`/`_baseRecv`）、libobk/lib/protocol.c（`obk_hs_session_init_plain`）

## 范围外

- 不动 `tls_cert.c`（#1 已确认过时，无需处理）。
- 不动 `libobk_session_test`（`session_test.c` 已正确使用 `if` 检查，无此问题，仅 `protocol_test.c` 受影响）。

## 备注

- bugfix 场景，含测试接缝。
