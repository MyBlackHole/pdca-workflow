# 工具 mTLS/算法 CLI 参数设计

## 参数

- `--mtls-enable=0|1`
- `--tls-algorithm=TLS_SM4_GCM_SM3|TLS_AES_256_GCM_SHA384`

四个工具均支持，参数值非法时明确报错并退出，不回退到配置值。

## 优先级

命令参数 > 工具环境变量 > 工具 section > `[security]` > 默认值。

## 实现

解析结果使用显式 override 状态传递给现有 `sec_tool_tls_*`/TLS 初始化路径；未指定 CLI 参数时保持 T0320 的配置行为。help 同步说明参数、合法值、优先级和示例。
