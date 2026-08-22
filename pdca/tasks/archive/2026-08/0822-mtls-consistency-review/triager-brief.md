# Triage Brief — mtls-consistency-review

- **category**: enhancement
- **scenario_type**: review
- **summary**: 审查 rdbcomm、sbt、dmsbtex 三个模块的 mTLS 模式实现逻辑是否与 rpc 基准实现一致。
- **current behavior**: 四模块各自维护独立的 mTLS 握手协商与配置解析实现；结果码数值同构但配置来源链、强制模式失败路径、降级语义等细节可能存在偏差。
- **desired behavior**: 产出逐维度一致性审查报告：协议常量/协商状态机/无降级策略/配置优先级/TLS 构建时机/资源清理等维度的一致与偏差清单，附风险评级。
- **key interfaces**: mTLS 握手协商层（握手帧 flags、结果码 OK_MTLS/ERR_MTLS_REQUIRED/ERR_MTLS_UNAVAILABLE）、mTLS 使能开关（CLI/ini/环境变量三级配置链）、TLS 会话升级（按需握手 vs 启动时构建）。
- **acceptance criteria**:
  - 运行 conclusion.md 查看报告，得到覆盖 rdbcomm/sbt/dmsbtex 三模块 × 全部审查维度的比对矩阵。
  - 运行 grep 检查报告中每个"不一致"结论，得到可定位到源码符号/行为的证据引用。
  - 运行 conclusion.md 查看 verdict 段，得到每项偏差的 pass/fail 判定与风险等级（高/中/低）。
- **out of scope**: 不修改任何代码；不审查 TLS 证书生成/管理本身（已有独立任务线）；不审查非 mTLS 的加密通道（如 sbt-transfer-encryption）。
- **information gaps**: "rp" 的确切指向需用户确认（推荐解释为 rpc 模块/aio-speed 工具链基准实现）；审查维度范围需确认（仅协商逻辑 vs 含配置链与生命周期）。
- **dedup results**: 无重复任务；最接近的 0820-tls-session-integration-test 是集成测试任务而非一致性审查；out-of-scope 知识库无 mtls 相关拒绝记录。
- **recommended next steps**: P2 批量澄清"rp"指向、维度范围、产出形态后合成完整 PRD 并终审。
