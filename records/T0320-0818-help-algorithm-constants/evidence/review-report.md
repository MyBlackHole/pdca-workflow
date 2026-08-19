# T0320 Do 阶段双轴审查

## 标准轴

- Blocking：0。`git diff --check` 通过；工具标识和算法值集中在共享头文件，help、配置和测试引用统一宏。
- Warning：0。help 文案仍保留各工具现有输出结构，未引入无必要的参数解析重构。

## 规范轴

- Blocking：0。四个工具 help 均明确列出 section、对应环境变量、算法取值、默认值、优先级和无副作用示例；`AIO_SPEEDD_MTLS_ENABLE`、`aio-speedd`、`AIO_SPEEDD_TLS_ALGORITHM` 等标识均纳入宏化治理。
- Warning：0。未新增 CLI 参数，未修改握手字段或第二阶段业务帧。

结论：标准轴 0 个 Blocking，规范轴 0 个 Blocking，审查通过。
