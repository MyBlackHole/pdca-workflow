# tls-keygen 错误码可读化原则

## 适用场景
tls-keygen（及其同类 CLI 工具）在子命令失败时向 stderr 报告错误。

## 结论
- 内部错误码枚举值（如 `TLS_KEYGEN_ERR_WRITE = -3`）对使用者无意义，**handler 不应只打印裸数字 `code: -N`**。
- 每个返回码必须映射为"含义短语"（如 `-3 -> failed to write output file`），汇总行形如 `Error: failed to create CA: failed to write output file (code: -3)`。
- 底层写/读失败点（`fopen` 失败）返回前应打印 `cannot open <path> for writing: <strerror(errno)>`，携带目标路径与系统原因（errno）。
- 改报错文案保持与既有风格一致（tls-keygen 现有报错为英文）。

## 限制
- 仅覆盖失败返回点的"可读化"，不改变错误码枚举值、成功路径输出、退出码语义。
- 仅在确实需要定位失败环节时补充上下文；不引入国际化框架。

## 来源
- record: `records/T3989-0828-tls-keygen-errmsg/`（T3989 错误码可读化任务）
- 关联: B-3988（默认目录缺失导致 code:-3 修复）的收尾。
