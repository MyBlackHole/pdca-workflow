# 统一 INI 配置管理模块

## 问题

当前 `rdb-config` 与 `rpc-config` 各自直接使用 inih。通用 INI 解析、键值存储和查询逻辑分散，后续新增工具容易出现不同的默认值、重复键处理、错误行为和配置优先级实现。

## 目标

建立一个位于 `libs` 的共享 INI 管理模块。模块封装第三方 inih，并提供可复用的配置对象 API；项目内所有当前直接使用 INI 的 app 配置层迁移为调用该 API，保留现有外部行为。

## 方案

- 使用不透明 `config_store_t` 配置对象，调用方负责显式 load/free，避免依赖共享全局状态。
- 共享模块负责：INI 解析、键值保存、重复键的最后值读取、全局 section 回退、字符串/整数读取、键值设置、section 枚举和配置展示。
- app 配置层负责：默认值初始化、业务字段映射、字段合法性检查、工具专属 section 和环境变量优先级。迁移范围包括 `rdb-config`、`rpc-config`、`fs-backup/fsclient`、`fs-backup/fsdeamon`、`s3tools/s3file` 和 `s3tools/s3mount`；`xbsa` 保持现状，不在本轮范围。
- inih 依赖只保留在共享模块的实现/构建边界内。
- 不保留旧的 `config_kv_store` 等兼容 API；迁移完成后由所有调用方直接使用共享模块 API。

## 验收标准

- [ ] AC-1: 运行共享 INI 模块单元测试，字符串读取、全局 section 回退、整数默认值、重复键最后值、键值设置、section 枚举和展示均通过。
- [ ] AC-2: 运行所有 app 配置回归测试，rdb、RPC、fs-backup、s3tools 和 xbsa 的默认值、section、环境变量覆盖及字段校验保持一致。
- [ ] AC-3: 运行源码依赖扫描，本轮范围内 app 配置实现不再直接包含或调用 inih API，第三方解析依赖仅集中在共享模块；xbsa 仍保留原有 inih 依赖。
- [ ] AC-4: 运行 `xmake build`，共享模块及项目内所有受影响 app 全部构建成功。
- [ ] AC-5: 运行 `xmake test -v`，全量测试通过，且真实 RPC/rdbcomm、fs-backup 和 s3tools 测试无回归；xbsa 构建保持通过。
- [ ] AC-6: 运行配置回归测试，确认所有 app 的 INI section、key、默认值、优先级、协议帧和 CLI 参数语义未发生变化。
- [ ] AC-7: 运行源码接口扫描，配置展示统一调用共享 `config_show_section`，不再存在 `rpc_show_config`、`fsdeamon_show_config` 等 app 专属 INI 展示实现；fsclient 的网络 show-config 请求保持不变。
- [ ] AC-8: 运行源码接口扫描，范围内不再存在 `*_check_config` app 配置校验 API，整数、布尔和字符串校验统一由 `rdb-config.c/h` 提供。

## 测试接缝分析

### 声明的测试接缝

- seam: 共享 INI 单元测试 -> `libs/rdb-config` API
- seam: rdb 配置测试 -> `libs/rdb-config` 迁移适配
- seam: RPC 配置测试 -> `rpc/rpc-config` 迁移适配
- seam: fs-backup 配置测试 -> `fs-backup/fsclient` 与 `fs-backup/fsdeamon` 配置适配
- seam: s3tools 配置测试 -> `s3tools/s3file` 与 `s3tools/s3mount` 配置适配
- seam: 工具集成测试 -> 所有受影响 app 的启动配置与既有业务路径

## 范围外

不改变配置文件格式、已有配置键名、TLS/mTLS 握手协议、证书选择、业务数据帧和命令行参数定义；不在本轮将所有业务配置字段抽象成统一 schema。

## 需要确认的设计决策

1. 共享模块采用不透明配置对象和显式生命周期。
2. 不保留 `rdb-config` 的兼容 API，所有调用方直接迁移。
3. 将 inih 依赖从 `rpc/xmake.lua` 移除并集中到 `libs/xmake.lua`，避免依赖边界继续分散。
