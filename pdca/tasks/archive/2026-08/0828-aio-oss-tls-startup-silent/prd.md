# aio-oss server --tls 启动致命错误静默吞掉 — 规格文档

## 问题陈述

- **现状**: `aio-oss server --tls` 启动期致命错误（证书缺失 fail-closed、特权端口绑定被拒等）仅写入日志文件；控制台（stderr）无任何输出。证书缺失时进程以退出码 1 静默退出，绑定失败时因监听错误只发生在 goroutine 内、主流程阻塞于信号等待而**永久挂起**。运维执行命令看到"启动异常"，却得不到任何诊断信息。
- **目标**: 所有启动期致命错误都同时输出到控制台并给出可操作提示；监听失败快速非零退出而非静默挂起。
- **差距**: 错误只进了 `log`（已被重定向到文件）；`serverMain` 返回 error 但 urfave/cli v3 不透传；监听错误在 goroutine 内 `log.Println` 后 goroutine 结束、主流程无感知。

## 解决方案

从运维视角：执行 `aio-oss server --tls` 失败，控制台立刻看到原因与下一步动作。

1. 抽取辅助函数 `fatalToStderr(msg)`：先 `log.Print(msg)` 再 `fmt.Fprintln(os.Stderr, msg)`，集中"日志+控制台"双写。
2. TLS 配置失败路径（`buildServingTLS` 返回 err）：用 `fatalToStderr` 输出，并在信息中**包含证书路径与 `tls-keygen` 生成提示**（如默认前缀 ed25519，可用 `--tls-algorithm sm2` 指定）。**控制台文案使用英文**（与 tls-keygen 工具报错风格一致），示例：`Error: failed to start TLS server: cannot load certificate <path>: <err>; generate host cert via 'tls-keygen ca/create/sign' (default algorithm ed25519, or --tls-algorithm sm2)`。
3. 监听失败路径（`serveHTTPS`/`serveHTTP`）：监听 error 时 `fatalToStderr("failed to listen on :<port>: <err>")`，随后以**非零码退出**（不再静默挂起）；非 root 绑定特权端口的权限错误也能在控制台看到。

## Seam 分析

### 测试接缝
- 白盒：Go 单测验证 TLS 启动错误文案含证书路径与生成提示、监听失败文案可被识别。
- 黑盒：直接运行 `aio-oss server --tls`（无证书）与绑定特权端口场景，断言 stderr 非空且含关键提示、进程非零退出。

### 声明的测试接缝
- seam: oss/cmd/oss_https_test.go -> oss/cmd/tls.go （TLS 启动错误可读化与文案）
- seam: test/tls_test.sh -> aio-oss 二进制 （启动失败控制台可诊断、非零退出）

### 验收可测性
- 黑盒：无证书时 stderr 含 `ed25519_host.crt` 与 `tls-keygen` 提示，退出码非 0。
- 黑盒：绑定 :80 失败时 stderr 含 `监听失败`/权限提示，退出码非 0（不挂起）。
- 白盒：单测断言错误文案包含证书路径与生成提示字符串。

## 用户故事

1. 作为运维，运行 `aio-oss server --tls` 失败时能立刻在终端看到"缺哪个证书、怎么生成"，而非空退出或卡死。
2. 作为开发者，新增启动期致命错误时复用 `fatalToStderr`，避免再次静默吞错。

## 实现决策

- **辅助函数** `fatalToStderr`：双写日志与 stderr，统一出口。
- **TLS 错误文案**：在 `buildServingTLS` 调用处格式化，保留证书路径，追加 `tls-keygen ca/create/sign` 生成指引；不改 `buildTLSConfig` 的密码套件/算法策略。
- **监听失败退出**：`serveHTTPS`/`serveHTTP` 内 `err != nil` 时 `fatalToStderr` 后 `os.Exit(1)`（致命启动失败，立即非零退出）。
- 改动集中在 `oss/cmd/oss.go`（及可能的 `oss/cmd/tls.go` 文案）；不改证书/算法逻辑、不改 fail-closed 语义、不改 `tls-keygen` 工具。

## 测试决策

- 白盒优先覆盖错误文案（可断言字符串），黑盒覆盖"控制台可见 + 非零退出 + 不挂起"行为。
- 既有 `oss/cmd/oss_https_test.go` 的 TLS 开关/解析测试不受影响（仅新增错误文案用例）。

## 验收标准

- [ ] AC-1: 无证书运行 `aio-oss server --tls`，stderr 含字符串 `ed25519_host.crt`（或实际前缀证书名）与 `tls-keygen` 生成提示，进程以非 0 退出。
- [ ] AC-2: 在非 root 下绑定特权端口（默认 :80）启动，stderr 含 `监听失败` 或权限相关提示，进程以非 0 退出且在超时内结束（不永久挂起）。
- [ ] AC-3: 证书齐备且端口可绑定时，正常启动路径 stdout/日志无回归、退出码 0（Ctrl-C 前持续运行）。
- [ ] AC-4: 白盒单测覆盖 TLS 启动错误文案，断言含证书路径与生成提示，且监听失败文案可被识别。

## 范围外

- 不自动生成/补全证书；不改变 fail-closed 整体策略；不新增启动参数。

## 备注

- 延续 B-3988 / T3989 的"报错信息不明确"主线：把 oss 启动失败的隐式错误显式化。
- 版本号：若 oss 模块需 bump，随修复升至 1.0.0.1（当前 1.0.0.0）。
