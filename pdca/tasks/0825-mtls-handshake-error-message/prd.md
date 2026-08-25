# 握手错误码报错信息可读化（rpc/libobk/rdbcomm/dmsbtex 全模块）

## 问题

服务端开启 mTLS 强制模式后，未启用 TLS 的客户端连接被拒，但客户端报错只有十六进制码甚至静默失败：

```
[Error] rpc/rpc-client.cpp:973 execute_shell_script| server rejected: handshake error result=0x8004
error: execv(...) failed(252)
```

用户无法得知"服务端要求 mTLS、客户端需启用 TLS"。

## 方案

复刻 T0359 归一模式（libs/common.h 唯一定义 + 模块别名宏 + libs 单一实现）：

### 1. 错误码归一（libs/common.h）

定义唯一码集（运行时值严格不变，取四模块并集），四模块兼容别名：

| 统一名 | 值 | 含义 |
|--------|-----|------|
| HS_ERR_BAD_MAGIC | 0x8001 | magic 错 |
| HS_ERR_BAD_VERSION | 0x8002 | 版本错 |
| HS_ERR_BAD_OPERATION | 0x8003 | 操作类型错 |
| HS_ERR_MTLS_REQUIRED | 0x8004 | 服务端要求 mTLS |
| HS_ERR_ALGORITHM | 0x8005 | 算法协商失败 |
| HS_ERR_CA_CN | 0x8006 | CA/CN 不可用 |
| HS_ERR_FRAME | 0x8007 | 帧格式错 |
| HS_ERR_MTLS_UNAVAILABLE | 0x8008 | 服务端无 mTLS 能力 |

rpc/rpc-protocol.h 的 `#define HS_ERR_*`、rdbcomm/io.h 与 dmsbtex/protocol.h 与 libobk/include/protocol.h 的 enum 改为引用统一定义的别名宏，保持既有符号名全部可用。

### 2. 文案函数（libs/hs_algorithm.c 新增 hs_err_str）

```c
const char *hs_err_str(uint16_t result);  /* 英文描述，未知码返回 unknown 提示 */
```

别名 `rdb_hs_err_str` / `obk_hs_err_str` / `dm_hs_err_str`。示例文案：
- 0x8004 → `server requires mTLS but client TLS is disabled; enable tls and cert_dir in client config`
- 0x8008 → `server has no mTLS capability but client requested TLS`

### 3. 客户端接入（6 处）

| 模块 | 位置 | 改动 |
|------|------|------|
| rpc | rpc-client.cpp 两处 execute_shell_script 防御分支 | 文案改用 hs_err_str；退出码语义化 |
| rpc | rpc-io.cpp 主动握手拒绝分支 | 文案统一走 hs_err_str |
| libobk | libobk/lib/sbt/libobk.c 客户端协商拒绝分支 | 文案改用 obk_hs_err_str |
| rdbcomm | rdbcomm/client.c 握手 fail 路径 | 补 ErrorLog 输出拒绝原因（消除静默失败） |
| dmsbtex | dmsbtex/network.c sbt_session_client_init result!=OK 分支 | 补 ErrorLog 输出拒绝原因（消除静默失败） |

### 4. 退出码语义化

rpc 两处 `error_no = -(int)hs.result`（-32772 被 shell 截断为无意义 252）改为固定码 `-2`（shell 呈现 254）；原始错误码保留在 stderr 日志中供诊断。libobk/rdbcomm/dmsbtex 库返回 -1 的约定维持不变。

## 用户故事

1. 作为运维，服务端强制 mTLS 而客户端未启用时，我希望看到明确的修复指引（enable tls/cert_dir），而不是十六进制码。
2. 作为维护者，四个模块的握手拒绝报错行为一致：均有可读日志、退出码稳定可文档化。

## Seam 分析

### 声明的测试接缝

- seam: rpc/tests/mixed_mtls_integration.cpp -> ../rpc-client.cpp
- seam: libs/tests/hs_err_test.c -> ../hs_algorithm.c

## 实现决策

- 不改协议帧格式与线上字节流；仅消费侧文案与日志增强。
- 已废弃的 libs/tests/rpc_handshake_test.c（引用已删除的 rpc-handshake.h，不参与构建）不在本任务处理范围。
- 测试证书沿用项目内 libs/tests/certs（T0342/T0350 约束）。

## 测试决策

- 扩展 mixed_mtls_integration：server 强制 mTLS + client 明文场景断言 client stderr 含可读文案（非裸十六进制）、进程退出码为 254。
- 新增 hs_err_test：覆盖 0x8001~0x8008 及未知码的文案输出非空且含关键短语。
- 回归：plain/mixed/forced 正常象限用例全部通过。

## 验收标准

- [ ] AC-1: 运行"server 强制 mTLS + aio-speed 未启用 TLS + `-c true`"，client stderr 含 "mTLS required" 可读文案且不再出现裸 `result=0x` 十六进制打印，进程退出码为 254。
- [ ] AC-2: 运行 hs_err_test，0x8001~0x8008 每个码值返回非空英文描述且含对应关键短语，未知码返回含 "unknown" 的提示，全部通过。
- [ ] AC-3: 运行 rdbcomm 与 dmsbtex 客户端握手被拒场景用例，日志均含可读拒绝原因（rdbcomm/dmsbtex 不再静默返回）。
- [ ] AC-4: 运行 plain/mixed/forced 正常象限回归用例，全部通过无回归。
- [ ] AC-5: grep 四模块客户端源码，不存在绕过 hs_err_str 直接以 `%x` 格式打印握手结果码的路径。

## 范围外

- 握手协议帧格式变更；自动重试；服务端侧报错改造。
- 错误码定义之外的协议字段归一（如后续 follow-up）。
- 已废弃死测试文件 rpc_handshake_test.c 的清理。
