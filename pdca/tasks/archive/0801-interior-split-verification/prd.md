# T0177 验证 interior split 多级分裂语义对齐与异步 btree_update 框架不适用性

## 问题

T0168 review-report P1 行（0801-btree-core-completeness/evidence/
review-report.md:114）：「补 interior split_interior/异步 update_start
语义（部分模块）——多级分裂当前靠重试，未对齐 interior.c 完整语义」。
矩阵三亦列「interior.rs 缺异步 btree_update 框架/split_interior/merge」。

对照本地 bcachefs 源码（约束 1/2，interior.c 全文 3853 行已读）后，
该描述需要细分验证：

1. **多级分裂语义已存在**：subvol `bch2_btree_split_leaf`
   （interior.rs:380）为同步 loop 模型——leaf 分裂后若 parent 放不下
   则继续分裂 parent（parent_keys + pivot 扫描 + formats，interior.rs:
   990-1030 区域），直至新建 root（interior.rs:780 区域）——与
   bcachefs `btree_split`（interior.c:1962）+ `bch2_btree_insert_node`
   递归 parent_keys（interior.c:2191）+ `__btree_root_alloc`
   （interior.c:2095）控制流逐段对应；-8（parent 中 key 缺失）/-10
   （锁升级失败）/-12（BTREE_MAX_DEPTH）错误分支亦一一对应。但
   **无测试覆盖多级（>2 层）级联分裂**，仅有单级 root 增深测试
   （interior.rs:1277）与 D1 回归（engine.rs:1742）。
2. **异步框架为架构差异，不适用**：bcachefs `bch2_btree_update_start`
   （interior.c:1404）的 mempool/closure/gc.lock/interior_updates
   list/write_blocked/异步节点写盘管线，根因是 bcachefs 节点写盘
   异步后台化；subvol 为 journal 先行持久化（事务 commit 时 journal
   一次落盘即原子持久化，engine.rs:731 注释），无独立写盘管线——
   与 T0176 seq_blacklist 结论同类：机制因架构差异不适用（约束 12）。
3. **merge 缺失属实但非正确性必需**：`bch2_foreground_maybe_merge`
   （interior.c:2327 附近）为分裂后相邻节点合并的性能优化，非
   btree 操作正确性/持久性语义；T0168 未将其列为交付门槛。

## 目标

验证型任务：
1. 补多级分裂测试：构造深度 ≥2 的树，连续插入触发 leaf→parent→root
   级联分裂，verify 全树通过（锁定 btree_split 递归语义）
2. 失败路径对照验证：-8/-10/-12 与 interior.c 对应分支语义一致
   （可达分支补测试覆盖）
3. 结论文档化：异步 btree_update 框架不适用（含源码锚点）、merge
   范围外声明、review-report P1 描述修正

## 用户故事

作为存储引擎开发者，我希望验证现有同步 split 模型与 bcachefs
btree_split 的多级分裂语义完全对齐、并确认异步 update_start 框架
因 journal 先行架构不适用，以便：确认无需移植 ~1000 行异步框架、
用测试锁定多级级联分裂边界防止回归、修正 review-report 的「未对齐」
表述。

## 方案

1. **多级分裂测试**（engine.rs 或 interior.rs tests）：
   - 构造深度 2 树（root+leaf，512B 小节点），向同一 leaf 连续 put
     直至：leaf 分裂（写入 root）→ root 满 → root 分裂 → 新建深度 3
     root（对应 interior.c btree_split 的 parent 递归路径 + n3 增深）
   - `engine.verify()` 断言全树拓扑/排序正确，scan 断言键完备
2. **失败路径验证**：
   - -8（parent 中 old key 缺失 → interior.c btree_split 的
     bch2_btree_iter_peek 未命中路径）：验证代码对照一致
   - -10（bch2_btree_node_lock_write 失败 → interior.c 锁升级失败
     返回）：与 interior.c bch2_btree_node_lock_write 错误传播一致
   - -12（BTREE_MAX_DEPTH）：与 interior.c BTREE_MAX_DEPTH 检查一致；
     可达性评估后决定测试构造（或不构造，代码对照即可）
3. **conclusion.md**：异步框架不适用论证 + 锚点 + merge 范围外 +
   review-report 修正

## 实现决策

| 决策 | 选择 | 依据 |
|------|------|------|
| 多级分裂 | 保持现有同步 loop，补测试锁定 | 控制流与 interior.c btree_split/btree_insert_node 递归逐段对应（interior.rs:780/990 vs interior.c:1962/2191） |
| 异步框架 | 不移植，conclusion 文档化不适用 | journal 先行持久化无异步写盘管线（engine.rs:731）；与 T0176 seq_blacklist 结论同类；约束 12 |
| merge | 范围外声明，不实现 | 性能优化非正确性/持久性语义（interior.c:2327）；非 T0168 交付门槛 |
| 约束 10 | 修改前已对照 bcachefs 源码 | interior.c 全文（3853 行）已读，关键函数逐段比对 |

## 验收标准

- [ ] AC-1: 多级分裂测试通过（深度 ≥2 树 leaf→parent→root 级联分裂，verify 全树通过、scan 键完备）
- [ ] AC-2: 失败路径 -8/-10/-12 与 interior.c 对应分支语义一致（对照记录）；可达分支有测试覆盖
- [ ] AC-3: conclusion 记录异步框架不适用结论 + 锚点（interior.c:1404/1962/2095/2191/2327）+ merge 范围外声明 + review-report P1 修正
- [ ] AC-4: 全量回归绿（lib + 集成）+ fmt 干净
- [ ] AC-5: 与 bcachefs 语义对齐（多级分裂=btree_split 递归，非重试爬升；restart 仅用于锁/ENOMEM 重启）

## 范围外

- 移植异步 btree_update 框架（mempool/closure/gc.lock/write_blocked/
  异步写盘管线——journal 先行架构下无适用场景）
- 实现 merge（bch2_foreground_maybe_merge——性能优化，非交付门槛）
- byte_order grow 路径改造（T0174 已验证的既有行为）
- 其他 P 项（P2 属性测试已在 T0174 部分落地、P3 测试覆盖等）

## 备注

- 提交：feature-commit-format（【F-T0177】…，0.1.0 -> 0.1.0）
- parent: T0168（P1 interior 语义）
- 纯测试 + 文档任务，无引擎行为修改（若验证发现行为与对齐不符则
  升级为 bugfix 任务）
