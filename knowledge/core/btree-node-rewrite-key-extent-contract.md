# btree 节点重写 key 构造的 extent 保留契约

来源：T0206 部分完成 PDCA（AC-5 验证测试失败暴露）。

## 事实

T0205 引入的 `bch2_btree_node_rewrite` root 分支（interior.rs）用
`child_ptr(n)` 构造自身指针键：**仅 mem_ptr 寻址、无 extent ptr**
（journal-first 域内模式，节点 key 以内存指针标识）。重写成功后
`bch2_btree_set_root_for_read` 将 slot.key 更新为该键。

## 缺陷

重写后 slot.key 丢失磁盘位置（extent ptr 为空）→ io 层（真实磁盘
读盘模式）下重开恢复时，`bch2_btree_root_read` 重新读盘在
`bch2_bkey_ptrs_c` 处返回 -2（无 ptr），节点无法再读回。上游语义：
`bch2_btree_set_root` 后 root 记录**保留原 extent**（重写覆盖写原
位置）。

## 契约

- **mem_ptr 寻址与 extent 寻址双模式**：engine journal-first 路径
  用 mem_ptr（不读盘，无影响）；io 层读盘路径需要 extent ptr。
- **节点指针键构造必须保留磁盘位置**：任何重写/指针更新生成的新
  键，若旧键含 extent ptr（磁盘定位），新键必须继承（对齐上游
  set_root 覆盖写语义）；仅当域内确定永不读盘（journal-first）时
  才允许纯 mem_ptr 键。
- **验证方式**：重写后从 slot 取 key → mem_ptr 清零 → 重新
  root_read 必须成功（`rewritten_node_revalidates_on_reopen` 测试）。

## 修复方向

root 分支 bkey_copy 前合并旧 extent ptr（从 b.key 拷贝 extent 到
child_ptr(n) 生成的键）。
