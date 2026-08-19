# 增加工具 mTLS 与算法命令参数

## 验收标准

- [ ] AC-1: 运行四个工具 `--help`，输出包含 `--mtls-enable=0|1`、`--tls-algorithm=<algorithm>`、合法算法名、默认值和优先级说明。
- [ ] AC-2: 运行四个工具命令参数解析测试，两个参数能覆盖对应环境变量及配置 section，并将结果传入握手/TLS 初始化。
- [ ] AC-3: 运行非法值测试，mTLS 非 0/1 或未知算法得到明确工具名和参数名错误，不静默降级。
- [ ] AC-4: 运行真实 rdbcomm/rdbcommd 与 aio-speed/aio-speedd 集成测试，命令参数指定明文、AES mTLS、SM4 mTLS 时行为符合配置。
- [ ] AC-5: 运行 `xmake build` 和 `xmake test`，全部测试通过；不修改协议字段、证书选择逻辑和第二阶段业务帧。

## 范围

- 纳入：四个工具的 CLI 解析、help、优先级、非法值处理和真实测试。
- 排除：新增证书路径参数、ca_cn 参数、协议字段和业务功能。

## Seam 分析

### 声明的测试接缝

- seam: `rdbcomm/rdbcomm-main.c`、`rdbcomm/rdbcommd-main.c` -> getopt 参数解析与 TLS options
- seam: `rpc/rpc-client.cpp`、`rpc/main.cpp` -> getopt 参数解析与 TLS options
- seam: `rpc/tests/tool_integration.cpp`、`rdbcomm/tests/tool_integration.c` -> 四工具 help 与 CLI 集成
- seam: `libs/tests/rpc_handshake_test.c` -> 算法合法值和错误边界
