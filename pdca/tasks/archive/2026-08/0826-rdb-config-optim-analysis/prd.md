# T0386 分析 rdb config 是否需要优化

## 问题陈述
T0369 完成 `rdb.cfg` 配置使用问题审计并修复 F1~F8 后，代码又经一轮「注册表化」重构（T3978/T3979 集中 schema + T0361/T3981 严格解析 fail-closed），生产代码已从 `sec_resolve_*` 散点调用全面迁移到 `sec_get_*` 注册表 API。现需评估：**以 C 侧 rdb config 体系本身（参数注册表 + 解析层 + 初始化 + 安全）为对象，是否仍需要优化？** 若是，优化点何在、优先级与实施方案如何。

## 初步事实（Triage 已查证，基于当前代码）
- **架构**：C 侧已建立参数注册表（`libs/rdb-config.c` 的 `g_param_table` + 枚举 `config_param_id_t` + `sec_get_int/bool/str`），集中描述 14 个安全参数的 4 层解析链（env > layer2 > layer3 > def）。
- **迁移完成度**：生产代码 `sec_resolve_*` 实际调用已从 56 处降为 0（仅 1 处注释残留）；`config_get_string/int` 的 29 处调用全部位于 `libs/tests/rdb_config_test.c`（测试），无生产散点调用。生产读取 100% 经注册表。
- **严格解析**：BOOL 任一层非法值返回 -1（fail-closed，T0361）；INT 经 `parse_strict_int` 严格校验、脏值/空串回退 default 并告警（T3981/T0369 F5）；达上限不再静默截断（T0369 F2）。
- **fail-closed 调用方正确性（部分）**：鉴权开关 `timed_key.c:229`（`!= 0` ⇒ -1 维持开启）、审计开关 `logger.c:121`（`!(-1)=false` ⇒ 维持开启）均正确；`rdbcommd-main.c` 中 `audit_enabled`/`auth_enabled` 对 -1 做**启动期硬失败**（`if (<0) return EXIT_FAILURE`），但 `.mtls_enabled`（263 行）**直接赋值无 `<0` 校验**——fail-closed 语义（开启）对 mTLS 安全，但与其它开关处理不一致（AC-3 标注）。
- **常量单一来源**：路径常量 `libs/cfg_path.h`（T0369 F3）、env 名契约 `rdb-config.h`（T3978）已集中。
- **初始化**：存在 `__attribute__((constructor)) rdb_auto_init` 自动加载（无显式禁用/指定路径/错误处理）；各模块（s3file/s3mount/rpc）另有各自 `init_config` 变体。
- **已知遗留（来自 T0369 知识库）**：F9 `sec_walk_str` 直接返回 `getenv` 指针、CERT_DIR 未做路径校验（证书路径注入风险，留安全专项）；F7 配置源分散（dmsbtex 仍读 `sbt-config.conf`）未合并。
- **Go 侧（背景，本次不展开）**：`oss/cmd/tls.go` 的 `chooseStr=cli>env>file>def` 与 C 注册表 4 层模型语义一致（F1 已修复且对齐）。

## 方案方向
- **分析方法**：静态通读注册表实现与解析层；逐一审视 `sec_get_bool/int` 全部消费点的 -1 处理（含 rdbcommd `.mtls_enabled` 不一致）；评估注册表覆盖度与扩展可行性；评估 `sec_get_*` 每次 `getenv`+O(n) 扫描在热路径的必要性（性能，含调用频率证据或「无证据不优化」结论）。
- **产出**：① 明确「rdb config 当前（以 C 侧本身为对象）是否需要优化」结论；② 优化点优先级清单（高/中/低，每项含 问题/影响/建议）；③ 针对确认需优化的项给出**实施方案设计**（可落地但不写代码）；④ 如需实施，作为后续 development 子任务立项（P4 拆解）。
- **范围（按用户确认）**：聚焦 C 侧 rdb config 本身（注册表/解析层/初始化/安全）；Go 侧与跨模块仅作背景，不展开全量。

## 验收标准
- [ ] AC-1: 分析报告给出明确结论「rdb config 当前（以 C 侧本身为对象）是否需要优化」，并区分「无需紧急优化」与「建议增量优化项」。
- [ ] AC-2: 覆盖度评估——说明注册表当前覆盖的 14 个参数类别；评估是否应将更多参数（如各模块自读的非安全参数）纳入注册表或复用严格解析 helper，给出建议。
- [ ] AC-3: fail-closed 健壮性核对——逐一审视全部 `sec_get_bool/int` 消费点（尤其 `rdbcommd-main.c` 直接赋值 `.mtls_enabled` 的 -1 语义）是否正确处理非法 -1 值；标注存疑/不一致点。
- [ ] AC-4: 安全遗留评估——评估 F9（`sec_walk_str` 直接返回 getenv 指针、CERT_DIR 未做路径校验）的实际风险与优化建议。
- [ ] AC-5: 性能评估——评估 `sec_get_*` 每次 `getenv`+O(n) 扫描是否构成热路径瓶颈，给出是否需要缓存的判定（含调用频率证据或「无证据不优化」结论）。
- [ ] AC-6: 输出优化点优先级清单（高/中/低），每条含 问题、影响、建议、是否建议本任务外单独立项。
- [ ] AC-7: 针对确认需优化的项，给出实施方案设计（含改动点、兼容性、回归策略），但不实施代码。
- [ ] AC-8: 如需实施，列出后续 development 子任务候选（P4 拆解骨架），本任务仅分析。

## 范围外
- 不实施优化代码（仅分析与方案设计）；实施由后续 development 子任务承担。
- 不重写配置系统整体架构。
- Go(oss) 侧与 dmsbtex/s3file/s3mount/rpc 跨模块配置仅作背景，不展开全量审计（可列为后续专项）。

## 备注
- 关联任务：T0369（rdb.cfg 配置审计，已归档，沉淀 `knowledge/rdb-config/audit-findings.md`）；T3978/T3979/T0361/T3981（注册表化重构，据代码注释）。
- research 场景无测试产物，跳过测试接缝声明（P3.5）。
