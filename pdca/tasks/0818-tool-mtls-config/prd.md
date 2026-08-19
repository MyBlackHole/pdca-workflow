# 为 rdbcomm 与 aio-speed 增加独立 mTLS 算法配置

## 问题与目标

`rdbcomm`、`rdbcommd`、`aio-speed` 和 `aio-speedd` 缺少面向工具的 mTLS 开关与算法配置入口，当前高层连接逻辑依赖共享安全配置，无法让四个工具在同一运行环境中独立选择策略。目标是补齐工具级配置对象，并将其明确传入已有客户端/服务端握手配置。

## 用户故事

- 作为工具使用者，我希望分别配置 rdbcomm、rdbcommd、aio-speed、aio-speedd 是否启用 mTLS 和使用的具体算法。
- 作为运维人员，我希望算法名称直接对应 TLS 套件，而不是 `CLASSIC` 等抽象名称。
- 作为运维人员，我希望看到明确的配置优先级、默认值和错误信息。

## 验收标准

- [ ] AC-1: 运行 rdbcomm 与 rdbcommd 独立配置测试，分别配置 `mtls_enable` 和 `tls_algorithm=TLS_SM4_GCM_SM3`，得到对应客户端/服务端国密握手行为；未配置时得到 mTLS 关闭、国密算法默认值。
- [ ] AC-2: 运行 aio-speed 与 aio-speedd 独立配置测试，分别配置 `mtls_enable` 和具体算法名，得到对应客户端/服务端握手行为；未配置时得到 mTLS 关闭、国密算法默认值。
- [ ] AC-3: 运行配置隔离测试，同时设置四个工具不同策略，得到四者互不污染；工具专属参数优先于共享参数，且只接受定义的 mTLS/算法参数。
- [ ] AC-4: 运行证书链缺失、算法不匹配和 mTLS 必需但客户端未请求场景，得到明确错误且不静默降级；有效 mTLS 第二阶段继续使用 TLS session。
- [ ] AC-5: 运行真实 rdbcomm 与 aio-speed 工具集成测试，明文、`TLS_AES_256_GCM_SHA384` mTLS、`TLS_SM4_GCM_SM3` mTLS 场景按配置通过或按预期失败。
- [ ] AC-6: 运行 `xmake build`、`xmake test` 和配置回归测试，构建成功、全部测试通过；不修改协议字段和第二阶段业务帧。

## 配置决策（待确认）

- 配置载体：同一配置文件独立 section，还是每个工具独立配置文件。
- section/键名：`[rdbcomm]`、`[rdbcommd]`、`[aio-speed]`、`[aio-speedd]`，键名为 `mtls_enable`、`tls_algorithm`；证书路径和 `ca_cn` 沿用现有 TLS 配置。
- 优先级：工具专属环境变量 > 工具专属 section > 共享 `[security]` 配置 > 默认值；具体环境变量命名需 Plan 终审确认。
- 默认值：mTLS 关闭，算法 `TLS_SM4_GCM_SM3`；服务端强制 mTLS 时仍由服务端策略拒绝不符合条件的客户端。
- 算法取值：`TLS_SM4_GCM_SM3` 与 `TLS_AES_256_GCM_SHA384`；移除 `RPC_HS_ALG_CLASSIC` 抽象命名，替换为具体算法名，协议字段宽度和值的兼容语义需单独验证。

## Seam 分析

### 声明的测试接缝
- seam: `rdbcomm/tests/tool_integration.c` -> rdbcomm 独立配置加载与客户端握手
- seam: `rpc/tests/tool_integration.cpp` -> aio-speed 独立配置加载与客户端握手
- seam: `libs/tests/rdb_config_test.c` -> 配置 section、键名、优先级和默认值
- seam: `libs/tests/rpc_handshake_test.c` -> 客户端显式握手配置与错误边界
- seam: `xmake.lua` test graph -> 配置回归、真实工具集成、全量构建测试

## 范围外

- 不修改握手协议字段、TIME 协议和第二阶段业务帧。
- 不改变服务端按 `ca_cn` 选择证书的逻辑。
- 不新增与 mTLS/算法配置无关的 CLI 参数或业务功能。
