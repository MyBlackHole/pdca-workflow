# Triage Brief — 0826-mtls-cleanup-batch

- **category**: enhancement
- **scenario_type**: development
- **summary**: 批量实施 T3965 分析改进项（P1 ccache LRU、S1 算法解析归一、C1 key 别名、C2 SBT 宏归一、C3 spec 签名）+ sec_resolve 重复解析治理。
- **current behavior**: ccache 满即永久失败且错误码误导；四模块 ~20 行同构解析块；跨层 key 名不一致；SBT 宏双定义；sec_resolve 每次全链重查。
- **desired behavior**: CCACHE_FULL+LRU；hs_algorithm_config_resolve 单一实现；规范 key 双读兼容；宏单源；spec+cached 变体。
- **key interfaces**: tls_cert.h 错误码、libs/hs_algorithm.c、rdb-config.h spec/别名、common.h 宏。
- **acceptance criteria**: 见 PRD AC-1~AC-6（ccache 行为/归一迁移/别名兼容/宏单源/cached 失效/e2e 回归）。
- **out of scope**: S2 决策树抽函数；hs_session 归一；ini 格式变更。
- **information gaps**: 无。
- **dedup results**: T3965 分析为本任务依据；无重复任务。
- **recommended next steps**: 底层向上实施：rdb-config(别名+spec+cached) → common.h 宏 → hs_algorithm_config_resolve → 四模块迁移 → ccache → 全量回归。
