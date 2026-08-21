# T0336 端到端验证记录（3 场景容器实证）

> 来源：T0336-0820-pgwrecover-incremental-scope
> 样本：/tmp/opencode/t0336-*（PG18 容器，DB report_test OID=16384）
> 结论：重放输出 heap 与运行库最终状态**字节级一致**（仅差可见性 hint bit），
> 较 T0334 的 parquet 行数级验证更严格（heap 层面直接比对）。

## 场景构造

每个样本 = 备份目录（backup/）+ 运行库对照（live_heap.bin）+ relnode.txt：

| 样本 | 表 | relfilenode | 增量 WAL | UPDATE flags |
|------|-----|------------|---------|-------------|
| t0336-scope | t_scope | 1946604 | MULTI_INSERT(COPY 10) + 4×UPDATE | 0x00（无压缩） |
| t0336-prefix | t_prefix | 1946630 | 1×HOT_UPDATE | 0x20（PREFIX） |
| t0336-psuf | t_suf | 1946650 | 1×HOT_UPDATE | 0x60（PREFIX\|SUFFIX） |

构造法：容器内 INSERT → CHECKPOINT → tar 打包备份 → UPDATE 触发增量 →
**重拷 UPDATE 后的 WAL 段 8E 进备份**（备份快照的 8E 不含 UPDATE 记录）→
拷贝提交后 clog 到 cur_clog。脚本 gen_t0336_prefix.sh / gen_t0336_psuf.sh。

## 结果

### 1. MULTI_INSERT + 普通 UPDATE（t0336-scope）

- 重放 blk2 新页（MULTI_INSERT 10 行 + 4 条 UPDATE 新版本 = 6 items）与运行库
  逐字节一致（屏蔽 hint bit 与 XMAX_INVALID 时的 xmax 残留后）。
- blk0/blk1 不比对：运行库后续 VACUUM prune 标记 DEAD item，不在增量 WAL 内。

### 2. UPDATE prefix 压缩（t0336-prefix，flags 0x20）

- 重放 item1（len=79）与运行库完全一致：prefix 取旧 tuple 定长 id 4 字节，
  中间为 WAL 新增数据。TOAST 外联文本不参与前后缀比较。

### 3. UPDATE prefix+suffix 压缩（t0336-psuf，flags 0x60）

- 内联文本触发 PREFIX|SUFFIX。重放 item1（len=1532）与运行库完全一致。

### 4. 同页分支修复验证

同页 UPDATE（oldblk==newblk，HOT）原实现修改 opage 却写回 npage，旧版本
元数据丢失（item0 保持备份原样 xmax=22、ctid=(0,1)）。修复后重放 item0 与
运行库一致：xmin=29341、cmin=29342、xmax=0、ctid=(0,2)。

### 5. 全量回归

`tests/pgwrecover/` 9 项单测全 PASS（含本次新增 test_redo_scope.py 4 项与
T0334 既有 5 项），无回归破坏。

## hint bit 说明（重放 vs 运行库唯一差异）

运行库读取 tuple 时按 clog 动态标记 HEAP_XMIN_COMMITTED(0x100)/
HEAP_XMAX_COMMITTED(0x400) 并写回；备份/重放不设置（可见性由 clog 判断）。
另 HEAP_XMAX_INVALID(0x800) 时运行库 xmax 字段残留值 1。两者均不影响可见性。