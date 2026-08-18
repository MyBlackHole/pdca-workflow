## 当前状态

T0312 已完成 Act 前处置，Check verdict 为 partial；代码提交为 `0356fb14`，全量 `xmake test` 36/36 通过。

## 未完成事项

SM2 证书初始化成功，但真实 rdbcomm 应用帧在 TLS 握手后连接失败，服务端目前只记录 `TLS handshake failed`，尚无 OpenSSL 错误细节。

## 已知约束

- TIME 必须使用独立 `time` 子命令，不使用 `-c time`。
- 不新增客户端参数；继续使用既有环境配置和 `ca_cn` 证书目录选择。
- mTLS 应用数据必须走握手结构体绑定的 TLS session。

## 推荐的下一步

进入 T0313，先补服务端/客户端 TLS 错误栈和 SM2 session 初始化对比，再完成 rdbcomm 与 RPC 的 SM2 应用帧双向往返测试。

## 关键上下文文件列表

- `/home/black/Documents/pdca-workflow/pdca/tasks/0818-rpc-rdbcomm-sm2-app-frame-followup`
- `/home/black/Documents/pdca-workflow/records/T0312-0818-rpc-rdbcomm-real-mtls-matrix-followup/conclusion.md`
- `rdbcomm/tests/tool_integration.c`
- `rpc/tests/time_integration.cpp`
- `libs/rpc-handshake.c`
- `libs/tls_cert.c`

## suggested skills

- `$PDCA_HOME/skills/tdd/SKILL.md`
- `$PDCA_HOME/skills/code-review/SKILL.md`
- `$PDCA_HOME/skills/testing-strategy/SKILL.md`
