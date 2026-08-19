# Triage Brief — 0819-unified-ini-config-module

- **category**: enhancement
- **scenario_type**: development
- **summary**: 将项目内所有 app 的 INI 文件解析和通用键值访问收敛到一个共享模块，各 app 配置层只调用统一 API。
- **current behavior**: `libs/rdb-config`、`rpc`、`fs-backup/fsclient`、`fs-backup/fsdeamon`、`s3tools/s3file` 和 `s3tools/s3mount` 存在直接依赖 inih 或独立解析入口，通用逻辑分散；`xbsa` 明确不在本轮范围。
- **desired behavior**: 共享模块独立负责 INI 读取、键值存储、section 查询、类型转换、修改和展示；所有 app 配置层只负责默认值、业务字段映射和校验。
- **key interfaces**: 共享 INI 配置对象、加载/释放、字符串与整数读取、键值写入、section 枚举、配置展示；app 配置初始化与 TLS 安全配置解析。
- **acceptance criteria**: 运行共享配置单元测试得到重复键、全局键回退、整数默认值、环境变量覆盖和 section 查询全部通过；运行全量构建得到成功；运行全量测试得到全部通过；扫描本轮范围内 app 配置实现得到不再直接调用 inih，xbsa 保持不变。
- **out of scope**: 不改变配置键名、优先级、TLS/mTLS 协议、证书选择、业务帧和工具 CLI 参数语义；不在本轮统一所有业务字段模型。
- **information gaps**: 需要确认共享模块 API 是否采用不透明配置对象，以及是否保留当前全局兼容 API 作为过渡。
- **dedup results**: 已检查活跃/归档任务与 knowledge，未发现正在执行的同一 INI 模块实现任务；已有 TLS 配置知识仅规定优先级，不提供通用 INI 模块。
- **recommended next steps**: 扩展现有 `libs/rdb-config.[ch]` 为共享 C 模块，迁移 rdb-config、rpc-config、fs-backup 两个 app 和 s3tools 两个 app，最后补充跨模块回归测试。
