# T0178 源码对齐记录

## 唯一对照来源

`/home/black/Documents/bcachefs-tools/fs/journal/validate.c`。

## 对齐范围

本任务只移植不依赖 bcachefs fs 层 btree-id 语义的前三个布局分支：

1. `journal_validate_key()` 第 64–71 行：key `u64s == 0` 时，将 entry
   长度截断到该 key 之前，并以空 `jset_entry` 填充原剩余区间。
2. 第 74–81 行：key 的 `bkey_next()` 超过 entry 末尾时，使用相同截断和
   填充顺序。
3. 第 84–91 行：format 非 `KEY_FORMAT_CURRENT` 时，先减少 entry `u64s`，
   再 `memmove` 紧缩后继 key，最后由 `journal_entry_null_range()` 填充尾部。

subvol 的 `journal_entry_null_range()` 与
`journal_entry_btree_keys_validate()` 保持上述分支顺序；恢复的首轮扫描在
overlay/replay 前调用后者。

## 有意不移植

`journal_validate_key()` 第 95–112 行调用的 `bch2_bkey_validate()` 依赖
bcachefs fs 层的 btree id → type/size/snapshot 规则。subvol 默认的独立
`BtreeId(0)` 会写入 `KEY_TYPE_cookie,size=0,snapshot=0`；直接使用 bcachefs
extents(id 0) 规则将拒绝现有合法数据。此限制符合项目 AGENTS.md 第 14 条。
