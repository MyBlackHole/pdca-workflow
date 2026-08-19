# T0323 实现审查

## 需求覆盖

- `rdbcomm`、`rdbcommd`、`aio-speed`、`aio-speedd` 均支持既有参数体系中的长参数：`--mtls-enable=0|1` 与 `--tls-algorithm=TLS_SM4_GCM_SM3|TLS_AES_256_GCM_SHA384`。
- 命令行参数优先级为 CLI > 工具环境变量 > 工具配置段 > `[security]` > 默认值。
- 参数值统一使用共享宏，工具名、配置段名、环境变量名和算法名不再散落硬编码。
- 无效参数由具体工具明确报错并以失败状态退出，不会静默回退。
- 握手协议、证书选择和第二阶段业务帧逻辑未改变；参数只进入既有 TLS/mTLS 配置解析路径。

## 风险审查

- Blocking：0
- 非阻塞：CLI 覆盖状态是进程级配置，适合当前每个工具进程单次启动配置；测试重置路径会清理该状态。
- 未发现协议兼容性、明文路径、mTLS 算法选择或错误处理方面的回归。

## 验证结果

- `xmake build`：通过。
- `xmake test -v`：36/36 通过。
- `rpc_tool_integration`：四个工具 help 与非法 CLI 参数测试通过。
- `rpc_time_integration`、`rdbcomm_tool_integration`：明文、AES mTLS、SM4 mTLS 及证书缺失/不匹配场景通过。
