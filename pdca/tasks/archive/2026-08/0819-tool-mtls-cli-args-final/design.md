# CLI 参数设计

参数：`--mtls-enable=0|1`、`--tls-algorithm=TLS_SM4_GCM_SM3|TLS_AES_256_GCM_SHA384`。

优先级：命令参数 > 工具环境变量 > 工具 section > `[security]` > 默认值。

非法值明确报错并退出；未指定 CLI 参数时保持现有配置行为；不增加证书路径或 ca_cn 参数。
