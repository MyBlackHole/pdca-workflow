# T0324 实现审查

## 覆盖范围

- 扩展现有 `libs/rdb-config.[ch]`，集中封装 inih 和通用 INI 对象操作，不新增配置模块文件。
- 已迁移 rdb-config、rpc-config、fsclient、fsdeamon、s3file、s3mount。
- xbsa 按用户确认保持原状，未纳入改动。

## 关键检查

- INI section、key、value 读取语义保持不变，包含重复键最后值、全局 section 回退和整数默认值。
- app 配置层不再直接包含 `ini.h` 或调用 `ini_parse`；仅共享模块和明确排除的 xbsa 保留 inih 入口。
- 配置展示也已收敛到 `config_show_section`；`rpc_show_config` 和 `fsdeamon_show_config` 已移除，fsclient 的同名函数是网络请求操作而非 INI 展示，保持不变。
- 配置对象采用显式分配/释放；业务配置层在完成字段复制后释放解析对象，不保留悬空字符串指针。
- rdb/RPC 原有配置入口和 TLS/mTLS 优先级未改变；CLI、环境变量、配置 section 和默认值逻辑继续由业务层负责。

## 验证结果

- 受影响目标定向构建通过。
- `rdb_config_test`：12/12 通过。
- `xmake build`：通过。
- `xmake test -v`：36/36 通过。
- 依赖扫描结果：本轮范围内仅 `libs/rdb-config` 直接使用 inih；xbsa 保持原有独立依赖。

## 风险结论

- Blocking：0。
- 非阻塞：共享模块当前使用固定容量 256 条配置项，沿用原 rdb 配置容量；若未来配置规模超过该边界，应单独扩容并增加容量错误诊断。
