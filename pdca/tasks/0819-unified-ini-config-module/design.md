# T0324 统一 INI 配置模块设计

## 模块边界

现有 `rdb-config` 模块同时承载通用 INI 文档管理，不知道 rdbcomm、RPC 或 TLS 业务。它维护一个拥有所有键值的配置对象，并提供只读查询、修改和展示接口。

应用配置层负责把配置对象映射为自己的 typed config，负责默认值、字段校验和环境变量/CLI 优先级。迁移对象包括 rdb/RPC、fs-backup 和 s3tools 的所有直接 INI 使用者；xbsa 保持独立实现。INI 的 section、key、value 文本不做改名或重写。

## 生命周期

每次加载返回独立配置对象；调用方显式释放。禁止共享解析器全局对象，便于测试和未来多个工具在同一进程使用不同配置。

## 兼容策略

不保留旧 `config_kv_store`、`rpc_config` 解析兼容入口。所有当前调用方在本轮完成迁移；对外工具配置文件格式保持兼容。

## 依赖边界

第三方 inih 由 `libs/rdb-config.c` 和 `libs/xmake.lua` 统一承载本轮范围内的配置解析；xbsa 保留自己的 inih 依赖和 `ini.h` 使用，不纳入迁移。

## 风险控制

- 先为共享模块建立单元测试，再迁移 rdb 和 RPC。
- 迁移前后对同一组配置文件比较 typed config 结果。
- 保留真实 RPC/rdbcomm 集成测试，覆盖明文、mTLS、时间获取和算法配置。
