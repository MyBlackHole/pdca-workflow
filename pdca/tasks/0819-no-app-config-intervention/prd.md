# 移除 app 配置管理介入

## 问题陈述

当前 fsdeamon、fsclient、RPC/aio-speed/aio-speedd、rdbcomm/rdbcommd、s3file 和 s3mount 仍保留 `*_init_config`、`*_parse_config` 及配置结构映射代码，虽然底层读取已集中，但配置管理职责仍由 app 参与。

## 解决方案

由 `libs/rdb-config.c/h` 独立维护统一配置状态和快照。app 删除配置加载、解析、校验、默认值和重载入口，只通过共享 API 读取配置结果；业务结构如确有必要，只作为业务运行时数据，不再拥有配置生命周期。

## Seam 分析

### 声明的测试接缝

- seam: `libs/tests/rdb_config_test.c` -> `libs/rdb-config.c`
- seam: RPC 工具集成测试 -> 统一配置状态
- seam: rdbcomm 工具集成测试 -> 统一配置状态
- seam: fs-backup 配置启动路径 -> 统一配置状态
- seam: s3tools 配置启动路径 -> 统一配置状态

## 验收标准

- [ ] AC-1: `libs/rdb-config.c/h` 独立完成范围内配置加载、默认值、校验、重载和状态持有。
- [ ] AC-2: fsdeamon、fsclient、RPC/aio-speed/aio-speedd、rdbcomm/rdbcommd、s3file 和 s3mount 不再包含配置解析、校验、默认值或重载实现及对应接口。
- [ ] AC-3: app 只通过共享配置 API 获取配置结果，不拥有 INI 配置状态。
- [ ] AC-4: 配置文件格式、section/key、默认值、优先级、CLI 和协议行为保持不变。
- [ ] AC-5: xbsa 无任何源码或构建配置变化。
- [ ] AC-6: `xmake build` 全部受影响目标通过。
- [ ] AC-7: `xmake test -v` 和真实 RPC/rdbcomm/fs-backup/s3tools 测试全部通过。

## 范围外

不修改 xbsa、INI 文件格式、业务协议、TLS/mTLS 握手和业务运行时结构本身。
