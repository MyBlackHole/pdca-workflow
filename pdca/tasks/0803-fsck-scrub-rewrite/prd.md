# T0206 PRD：fsck/scrub 自动触发 btree 节点重写（need_rewrite 消费路径）

## 需求

实现 bcachefs 的 fsck/scrub 自动触发节点重写能力：在 fsck 修复
模式（FixErrors::Yes）中遍历 btree 节点做 scrub 校验，校验失败
的节点自动经 `rewrite_node_key` 重写（对齐 `btree_node_scrub_work`
read.c:1233-1252 + read.c:1243 的 rewrite_key 触发语义），重写后
重新校验通过。

背景：T0205 已交付节点重写能力（rewrite_node / rewrite_node_key）
与 `BTREE_NODE_need_rewrite` 标志，但无自动触发消费路径（T0205
范围外显式列出）；T0195-T0200 已建 fsck 修复调度框架
（fsck_image + FixErrors + verify_all + 故障注入），修复动作目前
仅覆盖派生索引键，无节点级修复。

范围裁决（用户，P2/D3）：**含读路径自动触发**——读路径
（bch2_btree_node_read 校验失败/坏键截断）按上游语义设置
need_rewrite 标志（对齐 read.c:567/844/871），读完成后检查
need_rewrite → 自动调度重写（对齐 read.c:968 +
async_btree_node_rewrite_work interior.c:3406），与 fsck 修复
模式触发一并实现。

## 验收标准

- [ ] AC-1: 修改前逐段对照 bcachefs scrub→rewrite 触发管线
      （`btree_node_scrub_work` read.c:1233-1252 / `bch2_btree_node_scrub`
      read.c:1264-1328 / `btree_node_scrub_check` read.c:1169-1204 /
      `async_btree_node_rewrite_work` interior.c:3395-3415 /
      read.c:968 async 触发条件 / read.c:567/844/871 need_rewrite
      设置点），记录锚点与 subvol 域内差异判定。
- [ ] AC-2: 读路径 need_rewrite 设置：`bch2_btree_node_read` 校验
      失败/坏键截断时按上游语义设置 need_rewrite 标志（对齐
      read.c:567/844/871 的 set_btree_node_need_rewrite + 错误子
      标志），而非一律返回错误码；可修复错误与硬错误的分类
      对齐上游 btree_err FSCK_CAN_FIX 门控。
- [ ] AC-3: 读完成自动触发：读路径完成且 need_rewrite 时自动调度
      节点重写（对齐 read.c:968 条件 + async_btree_node_rewrite_work
      interior.c:3406 的 rewrite_key 调用，域内为同步 API）；
      重写失败传播（对齐 upstream ret 传播，不部分修复后假装成功）。
- [ ] AC-4: fsck 修复模式触发：FixErrors::Yes 时对 btree 节点做
      scrub 校验（对齐 btree_node_scrub_check 的 magic/csum/written
      边界检查），校验失败 → rewrite_node_key（对齐 read.c:1243
      语义，level 传目标节点层）；FixErrors::No 只检查不重写
      （对齐上游 fix_errors 门控语义）。
- [ ] AC-5: 修复后验证：节点重写后重新校验必须通过；重写提交后
      verify_all 通过；崩溃注入后重跑 fsck 收敛（对齐 T0200
      故障注入模式）。
- [ ] AC-6: workspace 全量测试、fmt、diff gate 通过，单项不超过
      一分钟。

## 实现决策（草案）

- 读路径：`bch2_btree_node_read`（io.rs:435）增加 need_rewrite
  设置语义——可修复错误（对齐上游 FSCK_CAN_FIX 分类）设置
  need_rewrite + 对应子标志后继续，硬错误维持返回错误码。
- 读完成触发：读路径返回后检查 need_rewrite → 自动调用
  rewrite_node_key（对齐 read.c:968 + interior.c:3406，域内同步）。
- fsck 触发：`fsck_image_with_fault`（engine.rs:2670）在
  FixErrors::Yes 时，于派生索引修复之外新增节点级 scrub 校验
  → 失败节点重写（对齐 read.c:1243 scrub_work 的 rewrite_key 触发）。
- 校验：遍历 btree 各节点读盘校验（对齐 btree_node_scrub_check
  的 magic/csum/written 检查语义）。
- 重写：复用 T0205 的 rewrite_node_key（rewrite_key 语义，
  level=目标节点层）。
- 测试：构造损坏节点（校验和破坏/键损坏）→ 读路径自动重写 +
  FixErrors::Yes 修复 → 节点校验通过 + verify_all 通过 +
  FixErrors::No 不改动断言；故障注入（重写提交前/后崩溃）→
  重跑收敛。

## 范围外

GC 触发重写、async rewrite worker 队列、读路径 IO 失败重试
（read.c 的 have_retry/多副本路径，域内单设备）、
need_rewrite_error 的 fsck 上报聚合（域内错误处理对齐）。

## 备注

前置：T0205（rewrite_node / rewrite_node_key 入口）、
T0195-T0200（fsck_image + FixErrors + verify_all + 故障注入）。
差异判定（草案，AC-1 细化）：
- D1: async_btree_op work 队列 → 同步 API（域内无异步调度）。
- D2: move.c 数据移动层 scrub 触发 → fsck_image 修复模式触发。
- D3: 读路径容错语义：上游"截断坏键 + set need_rewrite + 读完成
  自动重写"（read.c:567/844/871/968）→ 域内 bch2_btree_node_read
  增加 need_rewrite 设置，读完成检查并同步触发重写（用户裁决
  含读路径）。
- D4: scrub level 语义（read.c:1243 用 level-1，scrub level=
  指针键所在层）→ 域内以目标节点层调 rewrite_node_key。
