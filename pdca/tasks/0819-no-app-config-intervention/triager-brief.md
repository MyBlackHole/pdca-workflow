# Triage Brief — 0819-no-app-config-intervention

- **category**: enhancement
- **scenario_type**: development
- **summary**: 移除 app 配置模块对 INI 生命周期和状态的介入。
- **current behavior**: app 仍通过 config.cpp/h 接收配置文件、维护配置生命周期并映射配置结构。
- **desired behavior**: `libs/rdb-config.c/h` 独立完成加载、默认值、校验、重载和配置状态管理；app 只读取统一结果。
- **acceptance criteria**: 源码扫描无 app INI 生命周期接口；全量构建和测试通过；真实工具行为不变。
- **out of scope**: xbsa、INI 格式、业务协议、CLI 语义和非配置业务结构。
- **recommended next steps**: 统一配置状态访问接口，删除 app 配置生命周期，再回归所有工具。
