# T0197 AC-1 上游锚点记录

## 上游 open bucket 守卫语义

- open bucket 由分配路径保证非 free：foreground.c 的 free-bucket
  candidate 规则只分配 free 桶为 btree-owned，open bucket 在已分配
  桶上建立（engine-local `allocate_bucket` engine.rs:802 对应）。
- fsck 校验 open bucket 状态与 alloc 一致性：check_allocations.c
  （fsck pass 校验 alloc 桶状态，open bucket 引用与 alloc data_type
  必须匹配）；engine-local `verify_guard_invariants`（T0193）裁决
  open∧free 与 not_rw∧free 非法。

## 上游 not_rw 语义

- `background.c:1650-1667` `bch2_dev_allocator_set_rw`：rw_devs 位图
  控制设备可写性；非 rw 设备拒绝分配与 free 转换。
- `discard.c:357-365` `bch2_dev_get_ioref(WRITE)` 失败：not_rw 设备
  discard 拒绝。
- engine-local `set_device_rw`（engine.rs:924，rw_devs 位图 + 锁序
  open_buckets→rw_devs）。

## 现有模型结构（engine.rs:3511 open_bucket_discard_model_protects_open_from_reuse）

```
op 0: queue_discard_bucket        — queued 影子状态，EEXIST(-17) 期望
op 1: run_discard_worker          — deferred 判定，EAGAIN(-11)/Ok 期望
op 2: reclaim_bucket              — open 影子状态，EBUSY(-16)/Ok 期望
op 3: allocate_bucket             — free_count 判定，-1/Ok 期望
op 4: flush + drop + open_persistent — alloc 树投影重建模型状态
op 5: open_bucket（预判 state!=0）   ← 手写守卫复刻，本次注入
op 6: close_open_bucket（预判 open） ← 手写守卫复刻，本次注入
每 op 后: verify_all is_ok + verify_guard_invariants is_ok + alloc 核对
```

## 注入方案对应锚点

- 无条件 open/close：open_bucket（engine.rs:901）无预校验 insert——
  守卫裁决在 verify_all/verify_guard_invariants（T0193 聚合断言），
  模型由"预判"改为"探索+裁决"。
- 错误名契约：OpenBucketFree（engine.rs:249 变体）、NotRwBucketFree
  （engine.rs:249），Display 输出变体名。

## 结论

守卫裁决是实现职责（verify_guard_invariants），模型手写 `state != 0`
预判是重复实现；注入后模型状态由实现结果驱动，语义上游可证
（alloc 保证 open 非 free；fsck 校验 open 状态）。
