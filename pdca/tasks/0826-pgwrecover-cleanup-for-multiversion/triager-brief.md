# Triage Brief — 0826-pgwrecover-cleanup-for-multiversion

- **category**: enhancement
- **scenario_type**: development
- **summary**: 清理 pgwrecover 中多余/未使用的 PG 代码，建立清晰的版本边界，使后续可插拔 PG16/PG17 等多版本支持。
- **current behavior**: src/pg/ 混入了版本无关编排代码、PG18 官方 xlog 拷贝、以及死代码（.bak 备份、未实现的 legacy PG9 clog 读取器）。重放逻辑全部硬编码 PG18（拷贝自 REL_18_STABLE），无版本分发边界，导致新增 PG 版本需侵入式改动。
- **desired behavior**: 仅保留当前 PG18 支持所需的代码；删除死代码；建立版本分发边界（如版本特性表/分发点），使新增 PG 版本 = 注册一份该版本的 xlog 模块，而非改动核心编排。
- **key interfaces**: WAL redo 分派（pg_replay.c）、各 rmgr redo 模块、pg_versions.h（版本事实矩阵）、构建脚本（scripts/build_pgwrecover.sh）。
- **acceptance criteria**:
  - 删除确认无用的文件（含 src/pg/main_pg_t0163.cpp.bak、src/pg/pg_clog_legacy_pg9.c/.h 等实测未调用项）后，构建仍成功且全量 pytest 仍 PASS。
  - 建立版本分发边界（最小可用：版本特性集中在 pg_versions.h 或独立 dispatch 模块，含 PG18 条目），使后续 PG16/17 可注册而不改核心分派。
  - 删除/重构后无新增 -Wall -Wextra 警告。
  - 单索引与多索引端到端测试仍全量 PASS（行为不变，纯清理）。
- **out of scope**: 不实现 PG16/PG17 的实际重放（那是下一个任务）；不改动重放算法本身；不引入构建系统切换。
- **information gaps**:
  - stub_pg.c 与 pg_wal_stub.c 是否功能重叠（均为 PG 函数前端桩）——需 Do 阶段确认是否可合并或其一为死桩。
  - 各 redo 模块内部是否存在未被调用的静态函数——需 Do 阶段用编译/链接未用符号扫描确认。
- **dedup results**: 活跃/归档无同概念重复（0818-pg-version-convert-test 为 PG→parquet 转换，非 WAL 重放，不相关）；out-of-scope 概念检查无命中。
- **recommended next steps**: Do 阶段先删死代码(.bak + legacy pg9 clog)并确认构建/测试仍绿；再建立版本分发边界(将 PG18 版本事实集中、定义版本注册点)；最后扫描并移除模块内未用函数。
