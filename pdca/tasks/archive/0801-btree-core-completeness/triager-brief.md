# Triage Brief — T0168

- **分类**: enhancement / review（对 subvol 现有 btree 核心做完整性审计，非新功能）
- **需求**: 走 PDCA 流程，分析 subvol 的 btree 核心功能是否完整（对照 bcachefs 语义）
- **查重**: 检索 `$PDCA_HOME/pdca/tasks/**`（含归档）与 `knowledge/`，无 subvol/btree 相关任务；唯一 subvol 相关记录为 knowledge/pdca-flow/external-evidence-collection.md（方法论文档，非 btree 分析）。无重复。
- **事实核查**（2026-08-01）:
  - subvol 为独立 Rust 存储引擎核心，crates/subvol/src/btree/ 共 12 模块、约 23K 行：bkey/bset/bset_build/bset_search/bset_update/cache/interior/io/iter/node_iter/types/update
  - 另有 journal.rs（3.1K 行）、engine.rs 对外 API：Transaction/ReadTransaction/StorageEngine（put/delete/get/scan/verify/checkpoint/sync/reclaim/recover/inject_fault）
  - `cargo build` 通过（dev profile，425 warnings，多为 C 风格对齐警告）
  - **关键发现**：`cargo test --lib` 存在堆崩溃 — `engine::tests::checkpoint_pages_are_cow_and_corrupt_page_falls_back_to_prior_root` 单独运行即 SIGABRT（`free(): invalid next size (normal)`）。测试套件不完整通过，btree/checkpoint 路径存在内存安全疑点。
  - 代码以本地 `/home/black/Documents/bcachefs-tools` 为唯一对照基准（AGENTS.md 14 条约束）
- **关键未知（需 P1/P2 决策）**:
  - 完整性分析的覆盖深度（仅 btree 模块 vs btree+journal+engine 全链）
  - 完整性判定基准（bcachefs 功能矩阵的哪些项属于"核心"，哪些豁免——AGENTS.md 已豁免 fs 层 id 方案）
  - 发现缺陷（如堆崩溃）时的处置范围：仅报告 vs 报告+修复
  - 分析产出形态（结论文档、缺陷清单、功能矩阵、建议任务拆解）
- **推荐下一步**: 进入 P1/P2 澄清与 Grill，逐项确认覆盖深度、判定基准、缺陷处置与产出形态
