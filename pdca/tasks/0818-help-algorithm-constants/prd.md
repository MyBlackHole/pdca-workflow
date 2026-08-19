# 补齐工具 mTLS help 并集中算法常量

## 问题与目标

T0319 增加了四个工具的独立 mTLS 与算法配置，但用户无法从工具 help 获得完整说明，且固定算法值散落在实现中会增加后续维护成本。本任务补齐可操作文档并建立单一常量来源。

## 验收标准

- [ ] AC-1: 运行 `rdbcomm --help`、`rdbcommd --help`、`aio-speed --help`、`aio-speedd --help`，输出包含 mTLS 开关、算法配置项、默认值、合法算法名、配置优先级以及对应环境变量：`RDBCOMM_MTLS_ENABLE`/`RDBCOMM_TLS_ALGORITHM`、`RDBCOMMD_MTLS_ENABLE`/`RDBCOMMD_TLS_ALGORITHM`、`AIO_SPEED_MTLS_ENABLE`/`AIO_SPEED_TLS_ALGORITHM`、`AIO_SPEEDD_MTLS_ENABLE`/`AIO_SPEEDD_TLS_ALGORITHM`。
- [ ] AC-2: 运行四个工具 help，输出至少包含一个不启动服务、不覆盖文件的可复制配置/命令案例，并明确证书与 `ca_cn` 前置条件仍沿用共享 TLS 配置。
- [ ] AC-3: 运行常量与映射回归测试，工具 section 名、工具名、四组 mTLS/算法环境变量名，以及 `TLS_SM4_GCM_SM3`、`TLS_AES_256_GCM_SHA384` 和默认值均由统一宏/常量提供并保持一致；不再使用 `RPC_HS_ALG_CLASSIC` 等抽象名称或散落字面量。
- [ ] AC-4: 运行 help 回归测试，缺失工具、section、环境变量、参数说明、案例标题或算法约束时能够明确指出失败对象。
- [ ] AC-5: 运行 `xmake build` 和 `xmake test`，既有功能测试与新增 help/常量测试全部通过，协议字段和第二阶段业务帧不变。

## 范围

- 纳入：`rdbcomm`、`rdbcommd`、`aio-speed`、`aio-speedd`，共享 TLS/RPC 算法定义和相关测试。
- 排除：新增 CLI 参数、配置键改名、握手协议变更、证书选择逻辑变更、业务帧变更。

## Seam 分析

### 声明的测试接缝

- seam: `rpc/tests/tool_integration.cpp` -> 四个工具构建产物的 help 输出
- seam: `libs/tests/rpc_handshake_test.c` -> 算法宏、默认值与字符串映射
- seam: `libs/tests/rdb_config_test.c` -> 算法常量在配置读取路径中的一致性
- seam: `xmake.lua` test graph -> help 回归、常量回归和全量构建测试
