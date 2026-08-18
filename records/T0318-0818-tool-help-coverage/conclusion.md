---
schema: pdca.asset/v1
id: T0318-0818-tool-help-coverage
phase: check
source_ids: [full-test, build, scan, implementation]
---

## 上下文

本任务补充 `aio-speedd`、`rdbcomm`、`rdbcommd`、`tls-keygen` 子命令和 `fsdeamon` 的 help 参数说明、默认值/约束与使用案例，并增加直接执行构建工具 help 的回归测试。

## 假设与结果

- AC-1：通过。工具 help 回归与扫描覆盖已有参数、值类型、默认值或约束。
- AC-2：通过。tls-keygen 全局 help 及 create、ca、sign、inspect、mtls 子命令 help 均有回归断言。
- AC-3：通过。回归测试直接执行工具 help，并对工具、参数、案例和子命令入口进行断言。
- AC-4：通过。各纳入工具均有可复制案例；测试只读取 help 输出，不执行副作用操作。
- AC-5：通过。未改变参数名称、短选项映射、业务协议；`git diff --check` 通过。`rdbcommd --keepalive` 的无参数注册与实现读取参数不一致，本次修正为必填 `SECONDS`，用户确认接受。
- AC-6：通过。`xmake build` 与完整 `xmake test -v` 成功，36/36 测试通过。

## 分析

help 文本现在覆盖参数用途、参数值形式、默认值或依赖关系，并提供安全案例。新增回归测试通过管道捕获实际工具输出，避免仅检查源代码字符串。tls-keygen 子命令 help 作为独立入口测试，覆盖了证书创建、签名、检查和 mTLS 自测的参数说明。

## 适用边界

本任务只改善已有 CLI 的说明和测试，不新增 CLI 参数，不改变业务流程或协议。`rdbcommd --keepalive` 的修正只使既有实现与声明一致；无参数调用属于无效用法，正常带数值调用不受影响。

## 下一轮建议

后续新增 CLI 参数时，应同步更新 help 和直接执行 help 回归断言。
