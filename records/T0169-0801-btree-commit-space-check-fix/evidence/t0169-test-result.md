# T0169 Do 证据 — 测试验证结果

## 环境

- `cargo test --lib`（stable，debug）：**173 passed; 0 failed**（含新增回归测试），耗时 ~2.2s（约束 9：单测 < 1 分钟 ✅）。
- ASAN：`RUSTFLAGS="-Zsanitizer=address" cargo +nightly test --lib engine::tests::single_transaction_many_keys_into_one_leaf_splits_without_overflowing` → ok，无 ASAN 报告。

## 覆盖说明（PRD 验证标准）

| 验证项 | 结果 |
|--------|------|
| `cargo test --lib` 全绿 | ✅ 173 passed |
| ASAN 运行回归测试无报告 | ✅ 1 passed（`-Zsanitizer=address`） |
| 新增回归测试覆盖多 update 同 leaf 累计场景 | ✅ `single_transaction_many_keys_into_one_leaf_splits_without_overflowing` |
| 单测总时长 < 1 分钟 | ✅ 2.2s |

## 备注

- PRD 现象中的原崩溃测试 `checkpoint_pages_are_cow_and_corrupt_page_falls_back_to_prior_root` 随 checkpoint 体系迁移（`30534a3`）移除；其崩溃根因（同 leaf 多 update 空间未累加）由新回归测试直接覆盖同一写路径（单事务 32 键超容量序列）。
- 全量 173 测试含：崩溃恢复（journal/checkpoint/tail 三阶段进程级）、持久化往返、并发 RCU 读写、reclaim 水位、btree split/merge 单测。
