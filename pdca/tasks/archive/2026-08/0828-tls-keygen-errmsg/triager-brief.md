# Triage Brief — tls-keygen-errmsg

- **category**: bug
- **scenario_type**: bugfix
- **summary**: tls-keygen 各子命令失败时仅打印 `code: -N` 数字错误码，用户无法判断失败环节与原因（目录缺失/权限/参数等），需补充可读原因与失败路径上下文。
- **current behavior**: 调用 `tls_keygen_*` 系列函数失败时，handler 直接 `fprintf(stderr, "Error: ... (code: %d)\n", ret)`，叶函数在 `fopen`/签名等失败点仅返回错误码，不输出具体路径与系统错误原因；用户看到 `code: -3` 无从下手。
- **desired behavior**: 每个失败返回点都携带人类可读原因（如 "failed to open <path> for write: <strerror>"），handler 把错误码映射为可读短语（WRITE/CA_CREATE/SIGN/...），并尽量附 errno 上下文。
- **key interfaces**: tls-keygen 子命令入口（ca/create/sign/inspect/mtls）、统一错误码枚举、底层 OpenSSL/EVP 调用失败点。
- **acceptance criteria**:
  - 运行 `tls-keygen ca -n X -a sm2` 在默认目录不存在场景，错误信息包含目标路径与失败原因（含 strerror 文本），而非仅 `code: -3`。
  - 运行后从 stderr 可 grep 到可读错误短语（非纯数字），每条失败原因唯一可区分。
  - 既有成功路径输出不受影响，退出码语义保持不变（非 0 仍失败）。
- **out of scope**: 不新增子命令、不改证书/密钥算法逻辑、不改版本号语义（仅随修复 bump）。
- **information gaps**: 是否需要为全部返回码建立统一的 `errcode -> string` 映射表（影响面评估）。
- **dedup results**: 无 out-of-scope 命中；关联 T0255(tls-keygen-sm2)、T0321(tool-mtls-cli-args) 但不重复。
- **recommended next steps**: 先在叶函数 fopen 失败点补充路径+strerror，再在 handler 层做错误码可读化映射；补充回归脚本验证错误信息可 grep。
