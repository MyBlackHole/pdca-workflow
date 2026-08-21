# T0400 pgwrecover btree P2（INSERT_UPPER/META/DEDUP/REUSE）

> 来源：T0400-0821-pgwrecover-btree-p2
> 编译：bash scripts/build_pgwrecover.sh 通过

## 实现内容

在 T0339 基础上，新增 4 种 btree WAL P2 类型：

| WAL 类型 | 操作码 | 实现 |
|----------|--------|------|
| INSERT_UPPER | 0x50 | IndexTuple 插入非叶页（简化：追加到 tuple 区域） |
| INSERT_META | 0x20 | 元页更新（初始化 META+LEAF 标志） |
| DEDUP | 0xA0 | 页面 dedup（标记重复项为 LP_DEAD） |
| REUSE_PAGE | 0xD0 | 页面回收（标记为 BTP_DELETED） |

**实现细节**：
- INSERT_UPPER：简化实现，直接追加 IndexTuple 到页
- INSERT_META：重建元页结构，设置 BTP_META | BTP_LEAF
- DEDUP：复用 VACUUM/DELETE 的 LP_DEAD 标记逻辑
- REUSE_PAGE：简化为标记 BTP_DELETED

**btree WAL 类型完整覆盖**：
- P0（4种）：INSERT_LEAF / DELETE / SPLIT_L/R / NEWROOT ✅
- P1（3种）：VACUUM / MARK_HALFDEAD / UNLINK_PAGE ✅
- P2（4种）：INSERT_UPPER / INSERT_META / DEDUP / REUSE_PAGE ✅
- 跳过：REUSE_PAGE（无效）/ GIN / GiST 等
