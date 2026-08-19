# 增加工具 mTLS 与算法命令参数

## 验收标准

- [ ] AC-1: 四个工具 `--help` 包含 `--mtls-enable=0|1`、`--tls-algorithm=<algorithm>`、合法值、默认值和优先级。
- [ ] AC-2: 四个工具 CLI 测试证明两个参数覆盖环境变量和配置 section，并传入握手/TLS 初始化。
- [ ] AC-3: 非法 mTLS/算法值明确报告工具名和参数名，不静默降级。
- [ ] AC-4: 真实四工具集成测试证明 CLI 指定明文、AES mTLS、SM4 mTLS 行为正确。
- [ ] AC-5: `xmake build` 与 `xmake test` 全部通过，协议字段和第二阶段业务帧不变。

## 范围

纳入四工具 CLI 解析、help、优先级、非法值和真实测试；排除证书路径、ca_cn、协议字段和业务功能。

## Seam 分析

### 声明的测试接缝

- seam: `rdbcomm/rdbcomm-main.c`、`rdbcomm/rdbcommd-main.c` -> getopt 与 TLS options
- seam: `rpc/rpc-client.cpp`、`rpc/main.cpp` -> getopt 与 TLS options
- seam: `rpc/tests/tool_integration.cpp`、`rdbcomm/tests/tool_integration.c` -> help 与 CLI 集成
- seam: `libs/tests/rpc_handshake_test.c` -> 算法合法值和错误边界
