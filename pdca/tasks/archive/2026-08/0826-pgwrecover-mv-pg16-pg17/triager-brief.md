# Triage Brief — 0826-pgwrecover-mv-pg16-pg17

- **category**: enhancement
- **scenario_type**: development
- **summary**: 在已有 PG18 版本分发缝基础上，让 pgwrecover 支持 PG16 与 PG17 的 WAL 重放
- **current behavior**: 仅有一份 vendored PG18 源码与重放集合；无 PG16/PG17 源码；构建单版本；分发缝已就位但只注册 PG18
- **desired behavior**: 提供 PG16/PG17 重放能力，按 control_version 自动选取对应版本重放集合，且各版本端到端回归通过
- **key interfaces**: 版本分发缝（按 control_version 返回重放集合）、构建期版本选择、各版本 redo 实现、fixtures 生成与端到端验证
- **acceptance criteria**:
  - 运行构建选定 PG16 得到可编译产物，control_version=PG16 时走 PG16 重放集合（非 PG18）
  - 运行 PG16 fixtures 端到端重放得到与 PG 最终态语义一致（btree/GIN 主要 rmgr 通过）
  - 运行 PG17 同上通过
  - 运行默认（PG18）回归仍有 9 passed，行为不变，构建 0 警告
- **out of scope**: 抽取 pg_common/ 共享内核优化、PG<16 旧版本、流复制/分布式、性能调优
- **information gaps**: PG16/PG17 源码获取方式（网络可下 tarball，已确认）、是否做 pg_common/ 抽取（留 Grill）、每版本 fixtures 体积与 CI 策略
- **dedup results**: 无重复活跃/归档任务；knowledge 已有 pgwrecover-multiversion-strategy.md（策略 B：共享内核+每版本增量）与 pgwrecover-official-rewrite.md（官方源码前端化方法论）
- **recommended next steps**: P1/P2 对齐源码布局与范围；P3 写 PRD；P4 按版本拆子任务
