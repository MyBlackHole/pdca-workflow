# Triage Brief — 0820-pgwrecover-incremental-scope

- **category**: enhancement
- **scenario_type**: development
- **summary**: 扩展 pgwrecover 增量重放覆盖：补齐 XLOG_HEAP2_MULTI_INSERT、
  UPDATE prefix/suffix 压缩，btree 增量实现或论证跳过安全
- **current behavior**: 增量重放仅覆盖 HEAP_INSERT/DELETE/UPDATE/HOT_UPDATE/LOCK；
  RM_HEAP2(MULTI_INSERT) 走 default 跳过，UPDATE 遇 prefix/suffix flag 构造错 tuple，
  btree 无增量
- **desired behavior**: 批量多行 INSERT 恢复产物行完整；UPDATE 前后缀重组正确；
  btree 一致性有明确结论（实现或论证）
- **key interfaces**: 增量重放分发器(pg_redo_heap_record)、UPDATE 重放、btree
  重放、WAL 记录读取、测试接缝
- **acceptance criteria**: 每条独立可验证，见 prd.md 的 AC-1~AC-6（构造 WAL 样本
  重放后逐字节比对；e2e 复用 T0334 容器样本回归）
- **out of scope**: 其他 rmgr、PITR、wal_level=minimal、MySQL 引擎
- **information gaps**: btree 增量实现成本 vs 跳过论证的取舍待用户决策（S3a/S3b）
- **dedup results**: 无重复任务（仅 T0334 归档提及缺口）；out-of-scope 无命中
- **recommended next steps**: P2 Grill 展示 btree 取舍 → P6 终审 → 进入 Do