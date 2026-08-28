# Triage Brief — aio-oss-tls-startup-silent

- **category**: bug
- **scenario_type**: bugfix
- **summary**: `aio-oss server --tls` 启动期致命错误（证书缺失 fail-closed、:80 绑定被拒等）只写入日志文件，CLI 控制台无任何输出；证书缺失时静默退出码 1，绑定失败时 goroutine 内报错后主流程永久阻塞，运维看到"启动异常"却无任何诊断。
- **current behavior**:
  - TLS 配置失败：`log.Printf("TLS 配置失败（fail-closed），服务不起: %v", err)` 仅进日志文件，`serverMain` 返回 error，但 urfave/cli v3 不向 stderr 透传，控制台空输出、退出码 1。
  - 监听失败（`serveHTTPS`/`serveHTTP` 内 `log.Println(err)`）：错误只在 goroutine 内记录，主流程 `select{}` 等待信号永不退出，进程挂起，控制台无输出。
- **desired behavior**: 任何启动期致命错误都同时输出到控制台（stderr）并给出可操作提示（证书路径、如何用 `tls-keygen` 生成、或改用 `--port` 避开特权端口）；监听失败应快速非零退出而非静默挂起。
- **key interfaces**: aio-oss `server` 子命令入口 `serverMain`、TLS 装配 `buildServingTLS`/`buildTLSConfig`、监听 `serveHTTPS`/`serveHTTP`。
- **acceptance criteria**:
  - 运行 `aio-oss server --tls`（默认 cert 目录无 `ed25519_host.crt`）时，stderr 出现清晰错误，含证书路径与 `tls-keygen` 生成提示，且进程非零退出（不再静默退出码 1 无信息）。
  - 监听失败（如非 root 绑定 :80）时，stderr 出现"监听失败"信息且进程非零退出，不再永久挂起。
  - 正常启动（证书齐备 + 可绑定端口）不受影响。
- **out of scope**: 不自动生成证书、不改变 fail-closed 策略、不新增 `--tls` 之外的启动参数语义。
- **information gaps**: 控制台文案语言（与 oss 现有中文日志保持一致）。
- **dedup results**: 无 out-of-scope 命中；关联 T0259(aio-oss https 支持)、T3989(tls-keygen 错误码可读化) 但不重复。
- **recommended next steps**: 抽取"致命错误同时写日志+stderr"的辅助函数；TLS 错误信息补充证书路径与 tls-keygen 生成提示；监听失败改为明确非零退出。
