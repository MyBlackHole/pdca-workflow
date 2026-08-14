# PRD — inih 静态库隐藏 API 符号，移除 inih_static 别名

## 背景

inih 作为第三方静态库被 7 个 target 链接。其中共享库（libxbsa64.so）静态链接 inih 后，将 inih 的 C API（ini_parse 等）导出到动态符号表，造成 API 符号泄漏，可能与其他动态库中的同名符号冲突。

## 目标

1. 通过 `add_requires` 配置 `configs = {shared=false, cxflags="-fvisibility=hidden"}` 隐藏 inih 的 API 符号，使其不再出现在共享库动态符号表。
2. 移除 `inih_static` 别名，全部 7 处统一为 `inih` 引用 + static 连接。

## 方案

每处将：

```lua
-- 改前
add_requires("inih 60", { system = false, configs = { shared = false }, debug = is_mode("debug"), alias = "inih_static" })
...
add_packages("inih_static")

-- 改后
add_requires("inih 60", { system = false, configs = { shared = false, cxflags = "-fvisibility=hidden" }, debug = is_mode("debug") })
...
add_packages("inih")
```

涉及文件（7 处 add_requires + 对应 add_packages）：

| # | 文件 | add_packages 位置 |
|---|------|------------------|
| 1 | fs-backup/fsclient/xmake.lua | L18 |
| 2 | fs-backup/fsdeamon/xmake.lua | L21 |
| 3 | libs/xmake.lua | L132 |
| 4 | rpc/xmake.lua | L34, L61, L112 |
| 5 | s3tools/s3file/xmake.lua | L14 |
| 6 | s3tools/s3mount/xmake.lua | L18 |
| 7 | xbsa/src/xbsa/xmake.lua | L10 |

## 验收标准

- [ ] AC-1: 全仓无 `inih_static` 残留（grep 计数 = 0）
- [ ] AC-2: `xmake build` 全量构建成功
- [ ] AC-3: `libxbsa64.so` 动态符号表不再含 `ini_parse*`（`nm -D` 验证）
- [ ] AC-4: `xmake install -D -o install` 成功，且安装产物二进制 `--version`/基本功能正常（回归）

## 非目标

- 不改动 inih 包源码（xmake-repo 内 inih/xmake.lua 保持不变，通过 configs 注入）。
- 不改变其他第三方库（openssl3/libuuid/tbox）的符号可见性。
- 不改动 target 层 set_symbols 逻辑（timed_net_key 先例保留）。
