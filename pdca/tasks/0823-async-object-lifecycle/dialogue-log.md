# Dialogue Log — 0823-async-object-lifecycle (T0381)

## Plan 阶段摘要（2026-08-23）

### 讨论要点
1. Triage：enhancement/development；痛点为"多个管理逻辑，太复杂"（用户原话，见 clarifications round 1）；范围含核心原语 + 全部业务 runtime。
2. 方向：C 风格统一所有权契约 + 守卫原语（否决 refcount 句柄与智能指针化）；销毁后语义取强保证（销毁后回调绝不派发）。
3. API 策略：一次性替换删旧，不留兼容层；执行按 wide-refactor 保绿序列 expand→分批迁移→contract。
4. 组织：父子任务树 T0381–T0385；DAG 三批次 [T0381,T0382,T0383]→[T0384]→[T0385] 校验通过。
5. 验收：新增生命周期不变量压力测试 + sanitizer(thread/address/leak) 全开集成 + benchmark 基线不回退。

### 被否决的备选
- refcount 句柄基建——用户选纯契约路线，且热路径原子开销违背近零开销约束（ADR-0029）。
- 全面智能指针化——改动面与开销最大。
- 渐进迁移保留旧 API 薄封装——延续"多套管理逻辑"现状。
- 仅核心原语范围（推荐被否）——用户明确要全部业务 runtime。
- 协作式句柄校验/分层混合销毁语义（推荐混合被否）——用户选强保证。

### 用户关键反应
- "当前有多个管理逻辑，太复杂"（动机，captured:true）
- Q7 选"全部业务 runtime"超出推荐范围 A
- P6 终审："批准，进入 Do"（final_confirmation confirmed）

### 未解决即跳过的疑点
- 无。四轮 Grill 后 frontier 清空，决策树闭合。

## Do 阶段摘要（2026-08-23）

### 讨论要点
1. TDD 切片 1：统一入口 reactor_post_submit + spec 结构；两 impl 合并为 enqueue_impl（flags 区分阻塞路径）；旧 8 变体改薄封装保留。
2. 切片 2：lifecycle 守卫原语（单原子字 active<<1|destroying，CAS 进入/release 退出/置位销毁/退避排空）。
3. 切片 3：work_pool 完成回发与 reactor_group_post 迁移至 submit。
4. 性能对照：Debug -O0 口径曾现 -40% 假回退，按项目实际 -O3 口径复测为 +37%（消除双层转发）；work_pool completion 配对中位比 0.998 持平——基准口径必须跟随项目真实构建配置。
5. 双轴审查：标准轴 4 处超 80 列（修复）；规范轴补 expand 契约测试 test_legacy_variants_remain；TSan 揭示 WAIT 测试竞态并按终态不变量重写（e8bbf11）。

### 被否决的备选
- refcount 句柄（ADR-0029 已否决，守卫原语为显式控制面窗口原语，非热路径引用计数）。

### 用户关键反应
- 本阶段无新增用户决策点（P6 已批准完整方案，Do 按 PRD 执行）。

### 未解决即跳过的疑点
- guard 原语产品代码接入在子任务 T0382-T0385 完成；本任务仅交付原语+测试。

## Check 阶段摘要（2026-08-23）

### 讨论要点
1. 逐条 AC 判定：AC-1~AC-4 ✅（证据 ac1-unified-post-contract / ac1-dual-axis-review / ac2-sanitizer-final / ac3-regression-final / ac4-baseline-comparison）；AC-5 任务树就绪、收口依赖 T0385。
2. 过程发现并修复：TSan 揭示 WAIT 测试调度竞态（终态不变量重写）；VERSION bump 漏 protocol.hpp 联动；4 处超 80 列。
3. 基准口径教训：-O0 Debug 曾现 -40% 假回退，必须用项目真实 -O3 口径配对比较。

### 被否决的备选
- 无新增（沿用 ADR-0029 决策链）。

### 用户关键反应
- Verdict "confirmed"（check_confirmation 已落盘）。

### 未解决即跳过的疑点
- guard 原语产品接入与旧 API 删除归 T0382-T0385。
