---
schema: pdca.asset/v1
id: T0168-0801-btree-core-completeness
phase: check
source_ids: [review-report, checkpoint-cow-heap-rootcause, convergence-map, convergence-validation]
---

## 交接给 Check 阶段

**Do 阶段产物（均登记于 records/T0168-0801-btree-core-completeness/evidence/）**：

| 证据 id | 文件 | 覆盖 |
|---------|------|------|
| review-report | review-report.md | AC-1..AC-8（功能/资源/一致性矩阵、不重合项、缺陷清单、任务拆解、路径抽查） |
| checkpoint-cow-heap-rootcause | e5-checkpoint-cow-heap-corruption-rootcause.md | AC-5（根因级，ASAN 证据） |
| convergence-map | convergence-map.json | AC-1..AC-8 |
| convergence-validation | convergence-validation-result.json | AC-1..AC-8（valid: true） |

**Check 阶段关注点**：

1. **D1 CRITICAL 缺陷（不修复，仅报告）**：commit 空间检查未累加同 leaf 多 update → 堆越界写。修复方向已给出（对齐 commit.c:1083-1097 累加 + commit.c:189-195 EBUG_ON + 回归测试），建议作为独立 bugfix 任务（P0）。
2. **验收标准核对**：8 项 AC 是否都被单一证据覆盖（review-report 聚合）；矩阵行号与 bcachefs 对照路径抽查是否足够（12 文件 + 5 符号）。
3. **复现路径**：`cargo test --lib engine::tests::checkpoint_pages_are_cow_and_corrupt_page_falls_back_to_prior_root`（崩溃）；ASAN 需 `RUSTFLAGS="-Zsanitizer=address" cargo +nightly test --lib engine::tests::checkpoint_pages_are_cow`。
4. **已知边界**：子代理部分小节（trigger 链详细对照、事务 allocator 行号、snapshot 写路径）为综合推断，如有疑问可回源 subvol 源码核对；但所有结论均有行号锚点，抽查即可。
