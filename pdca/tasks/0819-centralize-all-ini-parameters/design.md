# T0326 全部 INI 参数集中管理设计

## 目标架构

`rdb-config.c/h` 同时承担 INI 文档层和参数目录层。文档层负责解析键值；参数目录层负责把每个受支持参数描述为 section、key、类型、默认值、环境变量覆盖和校验规则；加载入口输出统一配置快照。调用方只接收快照或通过统一参数 ID 读取，不再自行解释 INI。

## 初始参数盘点

当前代码已确认的生产参数分组如下，Do 阶段继续以配置样例、help 和历史行为补齐清单：

- `security`：TLS/mTLS 总开关、ciphersuites、TLS CA CN 及安全相关覆盖项。
- `auth`：enable。
- RPC/`rdbcomm`/`aio-speed` 工具 section：debug、retry、check_data、keepalive、parallel、read_timeout、fsbackup_dev_path、mtls_enable、tls_algorithm。
- `fsclient`：check_data、retry、keepalive、read_timeout、parallel。
- `fsdaemon`：check_data、debug、keepalive、retry。
- `s3file`：cache_path、gmssl、parallel。
- `s3mount`：verify_ssl、cache_path、cache_capacity、log_path、fuse_mount_point。

测试样例中的临时 section/key 仅用于验证通用解析能力，不进入生产参数目录。

## 生命周期

1. 共享入口加载 INI 文档。
2. 共享模块按参数目录写入默认值。
3. 共享模块按统一优先级应用配置文件和环境变量覆盖。
4. 共享模块完成类型转换和校验，错误包含 section/key 和原因。
5. 共享模块发布快照；工具启动和重载均显式传递该快照。

## 兼容约束

section/key、默认值、优先级、错误返回、CLI 参数和业务协议均以迁移前行为为基线。任何发现的历史差异必须在参数清单和回归测试中显式记录，不通过隐式兼容 API 掩盖。

## 主要风险

- 隐藏在 help、启动脚本或测试工具中的参数遗漏。
- 默认值存在于运行时结构初始化而不在 INI 解析函数中。
- 环境变量覆盖可能同时存在通用安全项和工具专属项。
- 运行时结构字段与共享快照字段不一一对应。

## 风险控制

先生成基线清单和快照测试，再迁移 app；迁移后以源码扫描、配置回归、真实工具集成测试和 xbsa 无差异检查作为门禁。
