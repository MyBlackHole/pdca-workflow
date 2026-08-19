# T0310 设计：统一 RPC session transport

## 目标

将连接 fd、可选 SSL、读写函数和关闭责任收敛到同一个 transport session。RPC 业务函数只接收连接/session 对象，不再自行从 fd 创建 plain I/O。

## 关键接口决策

可维护性优先：不为迁就旧调用方式保留宏替换、隐式 fd/session 双轨或“看似兼容”的适配层。接口调整应一次性完成并让类型/参数直接表达真实 transport 所有权。

- 连接建立函数返回/初始化完整 session，而不是只返回裸 fd。
- 应用收发统一调用 session 的 read/write；明文和 TLS 只在 transport 实现层分派。
- session 负责 SSL cleanup；fd 的关闭责任由连接生命周期统一处理，避免重复关闭。
- `connect_server`、`connect_server2` 及其 fd-only 收发包装不再作为业务数据面入口；同仓调用点全部迁移。
- 首阶段仍使用现有 `rpc_hs_session_t`，mTLS 握手成功后原地切换到 TLS read/write 指针。
- 不新增客户端参数；算法仍从既有 `RPC_TLS_CIPHERSUITES`/配置读取，并在握手结果中严格校验。

## 状态流

`TCP connected → plain first-stage → TIME close | NEGOTIATE reject | NEGOTIATE plain | NEGOTIATE mTLS → TLS handshake → session app frames → session cleanup → fd close`

## 错误与超时

- 首阶段 operation/version/result 必须组合校验。
- 握手和时间请求使用连接已有超时配置，并将 SSL WANT_READ/WANT_WRITE 映射为可诊断错误。
- 任意失败路径经过同一个 cleanup 出口。

## 测试设计

- 单元：握手字段、错误 operation/version/frame、超时和决策矩阵。
- 集成：RPC/rdbcomm 真实服务进程分别验证 plain/classic mTLS/SM2 mTLS/算法不匹配/证书缺失/强制 mTLS/时间/未知帧。
- 回归：现有 RPC 应用测试迁移到 session transport 后继续通过。
- 工具层：新增可编译的 RPC/rdbcomm 集成测试目标，使用 `fork/exec` 或等价进程控制直接启动 `aio-speedd`/`rdbcommd`，再执行 `aio-speed`/`rdbcomm`；测试目标通过 `add_tests("default")` 纳入 `xmake test`。通过既有配置/环境开关切换明文、常规 mTLS 和 SM2 mTLS，验证工具退出码、业务结果、时间功能及失败原因。
