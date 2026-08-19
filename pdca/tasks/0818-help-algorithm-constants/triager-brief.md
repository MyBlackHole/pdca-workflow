# Triage Brief — 0818-help-algorithm-constants

- **category**: enhancement
- **scenario_type**: development
- **summary**: 补齐 rdbcomm、rdbcommd、aio-speed、aio-speedd 的 mTLS/算法 help 说明和使用案例，并集中固定算法值。
- **current behavior**: 工具已经接受工具级 mTLS 与具体算法配置，但用户无法从 help 了解配置项、默认值、取值约束和示例；算法字符串与默认值仍存在散落定义风险。
- **desired behavior**: 四个工具的 help 明确说明独立 section、工具名和对应环境变量（包括 `AIO_SPEEDD_MTLS_ENABLE`、`aio-speedd`、`AIO_SPEEDD_TLS_ALGORITHM`），这些标识与算法值均由统一宏或常量提供，避免多处散落。
- **key interfaces**: 工具 help 渲染、共享 TLS/RPC 算法定义、配置读取接口、xmake 工具集成测试。
- **acceptance criteria**: 运行四个工具 help 得到 mTLS/算法说明和案例；运行常量/映射测试得到固定算法名一致；运行 xmake build/test 得到成功。
- **out of scope**: 不新增 CLI 参数、不改变现有配置键名、不修改握手帧和第二阶段业务逻辑。
- **information gaps**: 无；已有 CLI help 回归规范和四工具真实集成测试可复用。
- **dedup results**: T0318 已覆盖通用 help 完整性；本任务仅补充 T0319 新增配置的 help 和常量治理，不重复替代原任务。
- **recommended next steps**: Plan 阶段冻结 help 文案、算法常量归属和测试接缝，用户确认后实现。
