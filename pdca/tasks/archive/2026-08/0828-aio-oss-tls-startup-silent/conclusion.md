# T3990 结论 — aio-oss server --tls 启动致命错误静默吞掉

## 验证方式
- 重编译 `aio-oss`（release），运行黑盒 `test/tls_test.sh`（含 T3/T4 oss 场景）；另跑 Go 白盒 `TestDescribeTLSErrorActionable`。
- 复跑原命令 `aio-oss server --store /opt/aio/logs/tools/oss-emulator/store --tls` 及其变体，捕获 stdout/stderr。

## 实测结果
- 场景1（无证书 + `--tls`，用空 `--cert-dir` 触发 fail-closed）：stderr 输出
  `Error: failed to start TLS server: cannot load certificate/key pair (...): open ... no such file or directory; generate the host certificate via 'tls-keygen ca/create/sign' (default algorithm ed25519, or --tls-algorithm sm2) -- looked for <cert> / <key>`，退出码 1，不再静默。
- 场景2（非 root 绑定 :80）：stderr 输出 `Error: failed to listen on :80: listen tcp :80: bind: permission denied`，进程非零退出（不再永久挂起）。
- 场景3（正常启动路径，证书齐备 + 可绑定端口）：无回归。
- `--help` 全部文案已无中文（与英文控制台风格一致）。
- Go 单测 `TestDescribeTLSErrorActionable` PASS：错误文案含证书路径、`tls-keygen` 生成提示、默认算法 `ed25519`。

## 验收判定
- AC-1（无证书 --tls：stderr 含证书名+tls-keygen 提示+非0退出）：✅ PASS
- AC-2（非 root 绑 :80：stderr 含监听失败提示+非0退出不挂起）：✅ PASS
- AC-3（正常启动无回归）：✅ PASS
- AC-4（白盒单测覆盖错误文案含路径+提示）：✅ PASS

## 结论
启动期致命错误（TLS 配置失败、监听绑定失败）现在同时写入日志与控制台 stderr，并给出可操作提示（证书路径 / tls-keygen 生成方式 / 端口权限），不再静默退出或挂起。fail-closed 与算法策略未改。

## Verdict
PASS — 建议进入 Act（提交并归档）。
