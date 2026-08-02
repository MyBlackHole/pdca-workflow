# T0187 当前实现设计：freespace index 接缝

本地 `foreground.c` 的 candidate 选择不是直接扫描 alloc，而是优先读取
`BTREE_ID_freespace`，并以 `alloc_freespace_pos()` 编码 device、bucket 和可用空间；
`background.c:bch2_bucket_do_freespace_index()` 在 alloc 状态转移时同步删除/插入索引。

因此下一切片必须先补齐 freespace index 的本地 key/value 编码与 btree id 映射，再把当前
`allocate_bucket()` 的 alloc 全表扫描改为 freespace candidate。不能把 alloc 扫描继续扩展成
自有的近似 allocator，否则无法满足本地 bcachefs 的控制流和边界语义。

当前已实现的 alloc state transition 仅作为该切片的前置：free→btree、empty→need_discard→free、
generation bump 和反向引用为空检查；在 freespace index 接入前不宣称完整 allocator 链路。
