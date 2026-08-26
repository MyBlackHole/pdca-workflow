# Triage Brief — analyze-rpc-reload-chain

- **category**: enhancement
- **scenario_type**: research
- **summary**: 分析 rpc 配置重载链路三层断裂（store 单次加载/TLS 字段缺席重解析/发布顺序竞态）并产出修正设计
- **current behavior**: RELOAD_CONFIG_CMD 仅调 rpc_parse_config；libs 的 _kv_stores 由 constructor rdb_auto_init 启动加载一次后再无刷新路径；mtls_enabled/tls_algorithm/cert_dir 只在 rpc_init_config 解析；g_rpc_config 先发布后回写安全开关字段
- **desired behavior**: 厘清配置数据流全景与每层刷新时机，量化 reload 后各安全消费点的实际行为，产出保持 fail-closed 的修正设计
- **key interfaces**: RELOAD_CONFIG_CMD、rpc_init_config/rpc_parse_config 双缓冲发布、rdb-config parse_config/_kv_stores 双缓冲、sec_resolve_int/bool 四层解析、握手期 mtls_enabled/tls_algorithm/cert_dir 消费点
- **acceptance criteria**:
  - 运行 `ls records/<record>/analysis-report.md` 得到报告存在
  - 报告含配置数据流全景图（文字版层级图即可）且标注每层刷新时机
  - 报告含安全消费点 × reload 后行为的影响矩阵（逐点判定 生效/不生效/竞态）
  - 报告含至少两个修正方案的权衡（含 fail-closed 论证）与推荐方案
  - 每条关键结论附可复核验证途径（file:line 或可重跑命令）
- **out of scope**: 不修改代码（修复另行任务）；不重审 T3975 其他发现
- **information gaps**: 无——三层断裂点均已初步实证（rdb-config.c:380 constructor、rpc-config.cpp:104-113、main.cpp:308-330）
- **dedup results**: 无同类任务；T3968 为引入"重载重解析"裁定的历史任务（其裁定意图与本缺陷直接相关，需纳入分析）
- **recommended next steps**: Plan 终审后执行深度分析
