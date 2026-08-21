# T0339 pgwrecover btree P1（VACUUM/MARK_HALFDEAD/UNLINK_PAGE）

> 来源：T0339-0821-pgwrecover-btree-p1
> 编译：bash scripts/build_pgwrecover.sh 通过

## 实现内容

在 T0338 基础上，新增 3 种 btree WAL P1 类型：

| WAL 类型 | 操作码 | 实现 |
|----------|--------|------|
| VACUUM | 0xC0 | 同 DELETE（标记 LP_DEAD，无冲突处理） |
| MARK_PAGE_HALFDEAD | 0xB0 | 父页删除下链接 + 叶页重建为 half-dead |
| UNLINK_PAGE | 0x80 | 页面从 btree 链摘除（更新左右兄弟指针） |
| UNLINK_PAGE_META | 0x90 | 同 UNLINK_PAGE + 元页更新（元页部分跳过） |

**实现细节**：
- VACUUM：复用 DELETE 的 LP_DEAD 标记逻辑
- MARK_HALFDEAD：重建叶页为 BTP_HALF_DEAD | BTP_LEAF，更新父页 LSN
- UNLINK_PAGE：重建目标页为 BTP_DELETED，修复左右兄弟的 btpo_prev/btpo_next

**简化/跳过**：
- MARK_HALFDEAD 的 dummy high key 未完整添加
- UNLINK_PAGE_META 的元页恢复未实现
- 叶页链修复（leafleftsib/leafrightsib）未实现
