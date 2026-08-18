## 当前状态

T0309 已完成代码审查，Check verdict 为 `partial`。统一首阶段协议、时间功能和部分 TLS 数据面成立；RPC 全量 mTLS 不成立。

## 未完成事项

- RPC fd-only 连接/业务入口需要统一迁移到 session transport。
- RPC 服务端 SSL cleanup、握手严格校验、超时和真实 RPC/rdbcomm mTLS 业务回归需要补齐。

## 已知约束

- 不新增客户端配置参数。
- 默认明文；服务端启用 mTLS 即强制，不允许静默降级。
- mTLS 后必须使用密文 I/O；不兼容旧协议。
- 后续任务：T0310；既有补测任务：T0307。

## 推荐的下一步

进入 T0310 Plan，先 session 化 RPC 连接与业务路径，再补真实进程测试矩阵，之后重新核对 T0309 的 AC-3/AC-4/AC-5。

## 关键上下文文件列表

- `records/T0309-0818-mtls-implementation-review/conclusion.md`
- `records/T0309-0818-mtls-implementation-review/evidence/review-report.md`
- `pdca/tasks/0818-mtls-rpc-session-followup/prd.md`
- `knowledge/rpc-rdbcomm/mtls-review-fd-session-boundary.md`

## suggested skills

- `code-review`
- `secure-coding`
- `testing-strategy`
- `register-evidence`
