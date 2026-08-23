# Triage Brief — async-object-lifecycle

- **category**: enhancement
- **scenario_type**: development
- **summary**: 优化异步基础设施中异步对象的所有权与生命周期处理，降低手动管理带来的悬垂/泄漏风险。
- **current behavior**: Reactor 源/定时器/post 回调均为裸指针加 `void* user`；所有权转移依赖注释约定与 discard 回调；slot 复用靠 generation 计数防 ABA；业务 runtime 散布布尔所有权标志与 force_destroy 手工拆卸；无智能指针参与。
- **desired behavior**: 异步对象存续期由统一且可验证的机制保证：回调派发窗口内对象必然存活，销毁路径无泄漏、无二次释放、无 use-after-free；优化后性能基线不回退。
- **key interfaces**: Reactor 事件源与定时器注册、回调 post 所有权协议（含 owned/discard 变体）、work_pool 任务提交、业务子 Reactor 的创建与拆卸、连接对象所有权。
- **acceptance criteria**: 待 P1/P2 澄清范围后补充，每条形如"运行 X 得到 Y"。
- **out of scope**: 待澄清；初步排除 plain 路径整体 Reactor 化（归 0815-plain-reactor-converge 蓝图的独立实施任务）。
- **information gaps**: 优化动机（故障驱动 vs 预防性重构）、覆盖范围（核心原语 vs 全部业务 runtime）、方向偏好（句柄基建 vs 统一契约）、性能开销约束。
- **dedup results**: 活跃/归档任务无同概念任务；out-of-scope 概念库 `async-object-lifecycle` 未命中。相邻任务 plain-reactor-converge 与 sbt-rpc-session 目标不同，非重复。
- **recommended next steps**: 进入 P1/P2 逐轮 Grill 澄清四个缺口后合成 PRD；复杂度达 3+ 模块，预计需 design.md 与 implement.md。
