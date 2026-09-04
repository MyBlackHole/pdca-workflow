---
schema: pdca.asset/v1
id: ontology:entity/zfs-zio
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/zfs-zio/1.0.0
summary: ZFS ZIO 实体 — I/O Pipeline 位图调度与 VDEV 子流水线及 transform 栈
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:domain/zfs-crypto
    - ontology:pattern/research-diagram-methodology
attributes:
  - name: pipeline_bitmap
    desc: ZIO pipeline 位图组合可测
    constraint: 覆盖 enum zio_stage 1<<n 与 ZIO_READ/WRITE/FREE/CLAIM 等宏及 __zio_execute 循环按位推进，支持 GANG/DDT/BRT/NOPWRITE/ENCRYPT 按需插入
    testable_signal: "运行 grep -q 'ZIO_WRITE_PIPELINE' records/T0516-0903-research-zfs-zio/research-zio.md 且 grep -q 'ZIO_STAGE_WRITE_COMPRESS' include/sys/zio_impl.h 命中"
  - name: vdev_dispatch
    desc: VDEV 子流水线与 taskq 分发可测
    constraint: 覆盖 zio_create→zio_execute→__zio_execute→zio_vdev_io_start→vdev_queue_io→leaf vdev 完整链，含 spa_taskq_dispatch 与 ZIO_STAGE_VDEV_IO_START/DONE/ASSESS
    testable_signal: "运行 grep -q '__zio_execute' records/T0516-0903-research-zfs-zio/research-zio.md 且 grep -q 'vdev_queue_io' module/zfs/vdev_queue.c 命中"
  - name: transform_stack
    desc: transform 栈压缩/加密/校验可逆变换与 compress/checksum 分支可测，对应时序图 transform 压栈-弹栈与状态机 ZIO_STAGE_WRITE_COMPRESS/ENCRYPT/CHECKSUM_* 往返，细化压缩与校验分支
    constraint: 覆盖 zio_push_transform / zio_pop_transforms 栈（zt_orig_abd/zt_orig_size/zt_bufsize/zt_transform 链）与 lsize→psize 可逆变换；COMPRESS 的栈压弹（ZIO_STAGE_WRITE_COMPRESS 压 zio_decompress、读侧 zio_read_bp_init 压 decompress，pio/pwrite 的 lsize→psize 与弹栈 psize→lsize）与 CHECKSUM 的非栈生成/校验；细化 compress 选型（zio_compress_table[ZIO_COMPRESS_FUNCTIONS] 的 ci_compress/ci_decompress/ci_decompress_level/ci_level、zio_compress_info_t、enum zio_compress 的 lz4/zstd/gzip1-9/zle/lzjb/empty/off/on/inherit、ZIO_COMPRESS_HASLEVEL/zstd level 1-19/fast、compress_empty 短路（abd_cmp_zero→psize 0 hole / EMPTY→psize=lsize）、zio_compress_data/zio_decompress_data 的 d_len 与 c_len>d_len→s_len 回退、embedded 短路 BPE_PAYLOAD_SIZE 与 psize roundup 的 abd_zero_off）与 checksum 选型（zio_checksum_table[ZIO_CHECKSUM_FUNCTIONS] 的 ci_func[2]/ZCHECKSUM_FLAG_DEDUP/METADATA/NOPWRITE/SALTED/EMBEDDED/ci_tmpl_init 与 fletcher2/4/sha256/sha512/skein/edonr/blake3 的 on/dedup/feature-gate 选型）、zio_checksum_info_t 表驱动与 abd_checksum 边界（abd_iterate_func + fletcher_4_abd_ops.acf_iter、ZEC_MAGIC 嵌入式 gang/label/zilog 分支、salted tmpl 复用、加密半截截断）及 ABD 边界（ZFS_COMPRESS_WRAP_DECL 的 abd_borrow_buf 双缓冲、zle n=64 literal/run、lz4 BE_32 bufsiz 头、gzip qat 硬件短路、zstd early-abort 与 header c_len/level），及 zio_transform_stack_depth 边界，经 C4 L3 与状态机可一图建模
    testable_signal: "运行 grep -q 'zio_compress' records/T0523-0903-research-zfs-compress/research-compress.md 且 grep -q 'zio_compress_info_t' records/T0523-0903-research-zfs-compress/research-compress.md 且 grep -q 'compress_empty' records/T0523-0903-research-zfs-compress/research-compress.md 且 grep -q 'zio_checksum' ontology/entity/zfs-zio.md 命中"
---

# ZFS ZIO（I/O Pipeline）

I/O 流水线：`zio_t` 以 `enum zio_stage`（每 stage `1<<n`）位图定义 pipeline，`ZIO_READ/WRITE/FREE/CLAIM` 等宏按位组合，`__zio_execute` 以 `while (io_stage < ZIO_STAGE_DONE)` 按位推进；支持按需插入 `GANG/DDT/BRT/NOPWRITE/ENCRYPT`；`zio_push_transform` 栈实现压缩/加密的栈变换（`ZIO_STAGE_WRITE_COMPRESS` 压 `zio_decompress`、 `io_lsize→psize`），`ZIO_STAGE_CHECKSUM_GENERATE/VERIFY` 实现校验的非栈生成/校验；`VDEV` 子流水线 `VDEV_IO_START/DONE/ASSESS` 经 `spa_taskq_dispatch` 落至 `vdev_queue`。压缩分支以 `zio_compress_table[ZIO_COMPRESS_FUNCTIONS]` 的 `ci_compress/ci_decompress/ci_decompress_level/ci_level` 表驱动，覆盖 `lz4/zstd/gzip1-9/zle/lzjb/empty` 的 `HASLEVEL/zstd level` 选型、`compress_empty` 双短路（`abd_cmp_zero→psize 0 hole` / `EMPTY→psize=lsize`）与 `lsize→psize` 五分支（`zero/EMPTY/ge_lsize/embedded/roundup→push`），`ABD` 边界经 `ZFS_COMPRESS_WRAP_DECL` 的 `abd_borrow_buf` 双缓冲统一（`zle n=64 literal/run`、`lz4 BE_32 头`、`gzip qat`、`zstd header c_len+level/early-abort`）。校验分支以 `zio_checksum_table[ZIO_CHECKSUM_FUNCTIONS]` 的 `ci_func[2]/ZCHECKSUM_FLAG_*/ci_tmpl_init` 表驱动，覆盖 `fletcher2/4/sha256/sha512/skein/edonr/blake3` 的 `DEDUP/NOPWRITE/SALTED/EMBEDDED` 选型，`ABD` 边界经 `abd_iterate_func + fletcher_4_abd_ops.acf_iter` 统一，嵌入式 `ZEC_MAGIC`（`label/gang/zilog`）与加密半截截断经 `zio_checksum_compute/error_impl` 分线。

## C4 L3 Component — ZIO pipeline 位图调度

`zio_t` 含 `io_stage`（当前 stage 位）、`io_pipeline`（位图，`ZIO_*_PIPELINE` 宏预组合）、`io_transform_stack`（`zio_transform_t` 栈顶指针）、`io_vdev`/`io_bp`（目标 VDEV 与 blkptr）。`enum zio_stage` 每个枚举值为 `1<<n`（如 `ZIO_STAGE_OPEN=1<<0`、`WRITE_COMPRESS=1<<3`、`VDEV_IO_START=1<<8`），`ZIO_WRITE_PIPELINE = WRITE_COMMON + WRITE_BP_INIT + COMPRESS + ENCRYPT + CHECKSUM_GENERATE + DVA_THROTTLE + DVA_ALLOCATE + READY + VDEV_IO_START` 以位或拼装；`ZIO_READ_PIPELINE = READ_COMMON + READ_BP_INIT + VDEV_IO_START + CHECKSUM_VERIFY + DECRYPT + DECOMPRESS`。`__zio_execute` 核心循环 `while (io_stage < ZIO_STAGE_DONE) { stage = 1 << highbit(io_pipeline & ~executed); switch(stage) ... }` 按位推进，`zio_reexecute` 可在子 ZIO 完成回调中按需置位 `GANG/DDT/BRT` stage。C4 L3 图以 `zio_t → pipeline bitmap → stage executor → transform stack → vdev_queue` 五组件呈现该调度。

Source: `openzfs/zfs/include/sys/zio_impl.h:60-260`（`enum zio_stage` 与 `ZIO_*_PIPELINE` 宏定义）+ `openzfs/zfs/module/zfs/zio.c:934`（`zio_create` 签名与 `io_pipeline` 赋值）+ `openzfs/zfs/module/zfs/zio.c:2428`（`__zio_execute` while 循环按位推进）

## 时序 — zio_create → zio_execute → __zio_execute → vdev_queue_io → leaf vdev

写主路径：1) `zio_write(pio, spa, txg, bp, abd, lsize, psize)` → `zio_create(pio, ..., ZIO_TYPE_WRITE, ZIO_WRITE_PIPELINE, ...)` 分配 `zio_t` 并设 `io_pipeline`；2) `zio_execute(zio)` 入 `__zio_execute` 循环；3) 依次命中 `ZIO_STAGE_WRITE_BP_INIT → WRITE_COMPRESS（zio_push_transform 压压缩）→ ZIO_STAGE_ENCRYPT（zio_push_transform 压加密）→ ZIO_STAGE_CHECKSUM_GENERATE → ZIO_STAGE_DVA_ALLOCATE（metaslab_alloc 选 DVA）→ ZIO_STAGE_READY`；4) `ZIO_STAGE_VDEV_IO_START` 中 `zio_vdev_child_io` 为每个 DVA 创建 `io_vsd` 子 ZIO 并 `zio_execute` 子 pipeline；5) 子 ZIO 经 `spa_taskq_dispatch` 按 `zio_taskqs[ZIO_TASKQ_ISSUE]` 分发至 `vdev_queue_io`，leaf `vdev_disk_io_start` 落盘；6) `VDEV_IO_DONE → VDEV_IO_ASSESS → CHECKSUM_VERIFY` 回调主 ZIO，再 `zio_pop_transforms` 弹栈。读路径共用 `VDEV_IO_START/DONE/ASSESS` 子流水线，`READ_BP_INIT` 处理 `GANG` 拼装与 `DDT` 查表。时序图以 `DMU/TXG → zio_create → __zio_execute loop → VDEV queue → leaf → ASSESS → transform pop` 全链呈现该分发衔接。

Source: `openzfs/zfs/module/zfs/zio.c:934`（`zio_create` pipeline 赋值）+ `openzfs/zfs/module/zfs/zio.c:2186`（`spa_taskq_dispatch` 与 `zio_taskqs` 定义）+ `openzfs/zfs/module/zfs/zio.c:2428`（`__zio_execute` 调度循环）+ `openzfs/zfs/module/zfs/vdev_queue.c:80-180`（`vdev_queue_io` 入队与 `vdev_queue_issue` 调度）

## 状态机 — transform 栈的压栈-弹栈可逆变换

`zio_transform_t` 栈节点含 `zt_orig_abd / zt_orig_size / zt_transform`（变换函数指针），`zio_t.io_transform_stack` 为单向链表栈顶。状态五态：`ZT_NONE`（空栈）→ `ZT_COMPRESSED`（`WRITE_COMPRESS` 压入 `compress_func`，`lsize→psize`）→ `ZT_ENCRYPTED`（`ENCRYPT` 压入 `encrypt_func`，`abd` 替换为加密后 abd）→ `ZT_CHECKSUMMED`（`CHECKSUM_GENERATE` 压入 `checksum_func`）→ `ZT_READY`（`READY` 固化 `bp`），读方向逆向 `ZT_READY → ZT_CHECKSUM_VERIFIED（CHECKSUM_VERIFY）→ ZT_DECRYPTED（DECRYPT 弹加密）→ ZT_DECOMPRESSED（DECOMPRESS 弹压缩）→ ZT_NONE（zio_pop_transforms 逐项还原 `abd` 与 `size`）`。`zio_push_transform` 在 `zt_stack_depth < ZIO_TRANSFORM_STACK_DEPTH`（默认 8）时 `kmem_alloc` 新节点入栈，`zio_pop_transforms(is_write)` 按 `io_pipeline` 中是否含对应 stage 决定是否回放。状态机图覆盖写压栈三阶与读弹栈三阶及 `depth` 溢出分支。

Source: `openzfs/zfs/module/zfs/zio.c:320-420`（`zio_push_transform` / `zio_pop_transforms` 栈实现与 `ZIO_TRANSFORM_STACK_DEPTH`）+ `openzfs/zfs/include/sys/zio_impl.h:260-320`（`zio_transform_t` 定义与 `ZIO_STAGE_ENCRYPT/COMPRESS/CHECKSUM_*`）+ `openzfs/zfs/module/zfs/zio.c:2428`（`__zio_execute` 中 transform stage 调度）

## Checksum 分支 — zio_checksum_table 与 abd_checksum 边界

校验分支以 `zio_checksum_table[ZIO_CHECKSUM_FUNCTIONS]`（`module/zfs/zio_checksum.c:160`）表驱动，每项 `zio_checksum_info_t`（`include/sys/zio_checksum.h:69`）含 `ci_func[2]`（NATIVE/BYTESWAP 双路径）、`ci_tmpl_init/ci_tmpl_free`（`skein/edonr/blake3` 的 `spa_cksum_tmpls` 盐模板）、`ci_flags`（`ZCHECKSUM_FLAG_METADATA=1<<1 / EMBEDDED=1<<2 / DEDUP=1<<3 / SALTED=1<<4 / NOPWRITE=1<<5`，`include/sys/zio_checksum.h:40`）与 `ci_name`。`enum zio_checksum`（`include/sys/zio.h:85`）15 项：`INHERIT/ON/OFF/LABEL/GANG_HEADER/ZILOG/FLETCHER_2/FLETCHER_4/SHA256/ZILOG2/NOPARITY/SHA512/SKEIN/EDONR/BLAKE3`，`ON_VALUE=FLETCHER_4`（`zio.h:109`），`SHA256` 为 dedup 默认（`ZCHECKSUM_FLAG_DEDUP|NOPWRITE` 同时置位）。`fletcher2` 已废弃仅 `EMBEDDED`，`fletcher4` 仅 `METADATA` 不可 `DEDUP/NOPWRITE`；`sha512` 需 `SPA_FEATURE_SHA512`，`skein/edonr/blake3` 需 `SPA_FEATURE_SKEIN/EDONR/BLAKE3` 且 `SALTED` 需 `DMU_POOL_CHECKSUM_SALT` 参与 `tmpl_init`。生成侧 `zio_checksum_generate`（`zio.c:5229`）按 `bp==NULL→LABEL/OFF / BP_IS_GANG→GANG_HEADER / 否则 BP_GET_CHECKSUM` 选型后调 `zio_checksum_compute`（`zio_checksum.c:337`），后者按 `ci_flags & EMBEDDED` 分线：嵌入式读尾部 `zio_eck_t`（`ZEC_MAGIC=0x210da7ab10c7a11`，`zio.h:35`）并 `saved=bp->blk_cksum` 替换 verifier，非嵌入式直取 `bp->blk_cksum`，再 `ci_func[0](abd,size,tmpl,&cksum)`；`ABD` 边界统一经 `abd_fletcher_4_impl`（`zio_checksum.c:114`）的 `acf_init → abd_iterate_func(abd,0,size,acf_iter) → acf_fini`，`sha256/sha512` 为 `abd_checksum_sha*` 直调。校验侧 `zio_checksum_verify`（`zio.c:5260`）经 `zio_checksum_error_impl`（`zio_checksum.c:412`）按 `BSWAP_64(ZEC_MAGIC)` 或 `BP_SHOULD_BYTESWAP` 选 `ci_func[byteswap]`，加密块 `zc_word[2/3]=0` 截断比对，失败则 `vs_checksum_errors++` 并 `zfs_ereport_start_checksum`，叶侧校验经 `zio_vdev_child_io`（`zio.c:1623`）的 `pio &= ~VERIFY / pipeline |= VERIFY` 下推。状态机图覆盖 `GENERATE 非栈写 bp` 与 `VERIFY byteswap 双路径` 及 `salted tmpl` 分支。

Source: `openzfs/zfs/include/sys/zio.h:85-100`（`enum zio_checksum` 15 项）+ `openzfs/zfs/include/sys/zio.h:109`（`ON_VALUE`）+ `openzfs/zfs/include/sys/zio_checksum.h:40-50`（`ZCHECKSUM_FLAG_*`）+ `openzfs/zfs/include/sys/zio_checksum.h:69-85`（`zio_checksum_info_t`）+ `openzfs/zfs/module/zfs/zio_checksum.c:160-198`（`zio_checksum_table`）+ `openzfs/zfs/module/zfs/zio_checksum.c:114-118`（`abd_fletcher_4_impl` 的 `abd_iterate_func`）+ `openzfs/zfs/module/zfs/zio.c:5229`（`zio_checksum_generate`）+ `openzfs/zfs/module/zfs/zio.c:5260`（`zio_checksum_verify`）+ `openzfs/zfs/module/zfs/zio_checksum.c:337`（`zio_checksum_compute`）+ `openzfs/zfs/module/zfs/zio_checksum.c:412`（`zio_checksum_error_impl`）+ `openzfs/zfs/module/zfs/zio.c:5984`（派发表）

## Compress 分支 — zio_compress_info_t 与 lz4/zstd/gzip/zle 及 lsize→psize

压缩分支以 `zio_compress_table[ZIO_COMPRESS_FUNCTIONS]`（`module/zfs/zio_compress.c:33`）表驱动，每项 `zio_compress_info_t`（`include/sys/zio_compress.h:129`）含 `ci_name`、`ci_level`（`gzip1-9=1..9 / zle=64 / zstd=3 / lz4/lzjb=0`）、`ci_compress/ci_decompress/ci_decompress_level`（`zstd` 具 `ci_decompress_level` 回传 `zp_complevel`，其余 `NULL`）与 `ZIO_COMPRESS_HASLEVEL`（`zstd 或 gzip1-9`）。`enum zio_compress`（`zio_compress.h:31`）18 项：`INHERIT/ON/OFF/LZJB/EMPTY/GZIP_1-9/ZLE/LZ4/ZSTD`，`ON` 经 `zio_compress_select`（`zio_compress.c:83`）按 `SPA_FEATURE_LZ4_COMPRESS active→LZ4_ON_VALUE` 否则 `LZJB`，`EMPTY` 的 `ci_compress NULL` 仅作 `compress_empty` 占位（`abd_cmp_zero→psize 0 hole` 与 `EMPTY→psize=lsize` 双短路，不入 `ci_compress`）。`ZIO_STAGE_WRITE_COMPRESS=1<<5`（`zio_impl.h:125`）在 `ZIO_WRITE_PIPELINE`（`zio_impl.h:214`）中位列 `WRITE_BP_INIT` 之后、`ENCRYPT` 之前；写侧 `zio_write_compress`（`zio.c:1907`）以 `lsize=io_lsize / psize=io_size` 为锚，经 `pass>=dont_compress(8)→OFF`、`RAW_COMPRESS` 分线后三路并列：`abd_cmp_zero==0→psize 0 hole`、`compress==EMPTY→psize=lsize`、`else zio_compress_data(c, abd, &cabd, lsize, d_len=get_max_size, complevel)`（`zio_compress.c:107` 中 `complevel=ci_level`（`zstd` 时 `level==INHERIT→return s_len` / `DEFAULT→3`）再 `c_len=ci_compress(s,l,d,complevel)`，`c_len>d_len→return s_len` 不可压），后四路分发：`psize==0→OFF hole / psize>=lsize→OFF+free(cabd) / psize<=BPE_PAYLOAD_SIZE(512)且非加密且level0且无填充且embedded feature→encode_embedded_bp_compressed 不压栈 / else psize<lsize→rounded=zio_roundup_alloc_size(spa,psize)（`zio.c:1777` 的 `s_len - s_len>>3` 12.5% 与 `gcd_alloc` 对齐），`rounded>=lsize→OFF 回退`，否则 `abd_zero_off(cabd,psize,rounded-psize)` 后 `zio_push_transform(zio,cabd,psize,lsize,NULL)`（`zio.c:492` 的 `zt_orig_abd/zt_orig_size=lsize` 链），完成 `lsize→psize` 可逆记录，再 `BP_SET_LSIZE/PSIZE/COMPRESS` 固化（`zio.c:2103`）。读侧 `zio_read_bp_init`（`zio.c:1803`）在 `BP_GET_COMPRESS!=OFF && !RAW_COMPRESS` 时 `zio_push_transform(zio, abd_alloc_sametype(abd,psize), psize, psize, zio_decompress)` 压 `zio_decompress`（`zio.c:545` 的 `zio_decompress_data(BP_GET_COMPRESS(bp), psize→lsize, &zp_complevel)`，`zstd` 时 `ci_decompress_level` 否则 `ci_decompress(...,ci_level)`），经 `zio_pop_transforms`（`zio.c:510`）的 `zt_transform` 逆序还原 `lsize`。`ABD` 边界统一经 `ZFS_COMPRESS_WRAP_DECL`（`zio_compress.h:174`）的 `abd_borrow_buf_copy(src)/abd_borrow_buf(dst)→_buf→abd_return_buf` 双缓冲：`zle`（`zle.c:29`）按 `n=64` 分 `b<n→literal b+1 else zero 256-b+1` 且 `src==s_end?dst_len:s_len` 判定不可压；`lz4`（`lz4_zfs.c:57`）以 `BE_32(bufsiz)` 存精确压缩长于头部，解压时 `BE_IN32` 校验 `bufsiz+4<=s_len`；`gzip`（`gzip.c:42`）先 `qat_compress` 硬件短路再 `zlib compress2(n)` 且 `d_len!=s_len→memcpy 回退`；`zstd`（`zfs_zstd.c:555`）先 `zstd_enum_to_level` 再 `early-abort`（`lz4 pass→zstd-1 pass` 两级探测）后 `zfs_zstd_compress_impl` 以 `header {BE_32 c_len, raw_version_level}` 包裹 `level`，解压时 `ZSTD_f_zstd1_magicless`。状态机图覆盖 `compress_empty 双短路`、`ge_lsize 回退`、`embedded 不压栈` 与 `roundup→push` 的 `lsize→psize` 往返及 `DECOMPRESS psize→lsize` 逆向。

Source: `openzfs/zfs/include/sys/zio_compress.h:31-49`（`enum zio_compress` 18 项）+ `openzfs/zfs/include/sys/zio_compress.h:129-135`（`zio_compress_info_t`）+ `openzfs/zfs/module/zfs/zio_compress.c:33-64`（`zio_compress_table`）+ `openzfs/zfs/module/zfs/zio_compress.c:107-142`（`zio_compress_data`）+ `openzfs/zfs/module/zfs/zio_compress.c:144-159`（`zio_decompress_data`）+ `openzfs/zfs/include/sys/zio_compress.h:36`（`ZIO_COMPRESS_EMPTY`）+ `openzfs/zfs/module/zfs/zio.c:1907`（`zio_write_compress` 的 `lsize→psize` 五分支）+ `openzfs/zfs/module/zfs/zio.c:1777`（`zio_get_compression_max_size`）+ `openzfs/zfs/module/zfs/zio.c:1803`（`zio_read_bp_init` 压 `zio_decompress`）+ `openzfs/zfs/module/zfs/zio.c:545`（`zio_decompress`）+ `openzfs/zfs/module/zfs/zio.c:492`（`zio_push_transform` 的 `lsize/psize` 链）+ `openzfs/zfs/include/sys/zio_impl.h:125`（`ZIO_STAGE_WRITE_COMPRESS`）+ `openzfs/zfs/include/sys/zio_impl.h:214`（`ZIO_WRITE_PIPELINE`）+ `openzfs/zfs/module/zfs/zle.c:29`（`zle n=64`）+ `openzfs/zfs/module/zfs/lz4_zfs.c:57`（`lz4 BE_32`）+ `openzfs/zfs/module/zfs/gzip.c:42`（`gzip qat/zlib`）+ `openzfs/zfs/module/zstd/zfs_zstd.c:555`（`zstd early-abort/header`）

## 决策树

```mermaid
flowchart TD
    START([ZIO 到达 __zio_execute]) --> Q1{io_type?}
    Q1 -- WRITE --> Q2{压缩开启? compress!=OFF 且非 RAW}
    Q2 -- 否 OFF/RAW --> A2[跳过 WRITE_COMPRESS<br/>psize=lsize 不压栈]
    Q2 -- 是 --> Q2A{abd 全零? abd_cmp_zero}
    Q2A -- 是 --> HOLE[compress_empty 短路<br/>psize=0 hole_birth<br/>pipeline=INTERLOCK 不压栈]
    Q2A -- 否 --> Q2B{compress==EMPTY?}
    Q2B -- 是 --> EMPTY[EMPTY 短路<br/>psize=lsize 不调 ci_compress<br/>视为不可压]
    Q2B -- 否 --> COMP_CALL[zio_compress_data<br/>ci=&table[compress]<br/>c_len=ci_compress s_len/d_len/complevel]
    COMP_CALL --> Q2C{psize 判定}
    Q2C -- psize==0 --> HOLE
    Q2C -- psize>=lsize --> GE[不可压<br/>OFF+free cabd<br/>psize=lsize 不压栈]
    Q2C -- psize<lsize --> Q2D{psize<=BPE_PAYLOAD_SIZE<br/>且非加密且 level0<br/>且 embedded feature?}
    Q2D -- 是 --> EMBED[嵌入式短路<br/>encode_embedded_bp_compressed<br/>不压栈 不经 VDEV]
    Q2D -- 否 --> ROUND[roundup<br/>rounded=roundup_alloc_size ps<br/>rounded>=lsize→OFF 回退<br/>else abd_zero_off→psize=rounded]
    ROUND --> Q2E{rounded>=lsize?}
    Q2E -- 是 --> GE
    Q2E -- 否 --> A1[WRITE_COMPRESS<br/>zio_push_transform cabd psize/lsize<br/>lsize→psize 压栈]
    HOLE --> Q3{加密数据集?}
    EMPTY --> Q3
    GE --> Q3
    EMBED --> END_EMB([INTERLOCK 结束])
    A1 --> Q3
    A2 --> Q3
    Q3 -- 是 dataset加密 --> A3[ENCRYPT<br/>zio_push_transform encrypt<br/>abd 替换]
    Q3 -- 否 --> A4[跳过 ENCRYPT]
    A3 --> Q3C{checksum 选型?}
    A4 --> Q3C
    Q3C -- OFF --> CS_OFF[跳过 CHECKSUM_GENERATE<br/>直接 READY]
    Q3C -- fletcher4/sha256/sha512<br/>edonr/skein/blake3 --> CS_GEN[CHECKSUM_GENERATE<br/>zio_checksum_generate<br/>ci_func[0] 选型]
    CS_GEN --> Q4{嵌入式?}
    Q4 -- label/gang/zilog<br/>EMBEDDED --> CS_EMB[尾部 zio_eck_t<br/>ZEC_MAGIC 校验]
    Q4 -- 普通块 --> CS_NORM[非嵌入式<br/>bp->blk_cksum 直写]
    CS_EMB --> Q4C{加密?}
    CS_NORM --> Q4C
    Q4C -- BP_USES_CRYPT 且非 OBJSET --> CS_CRYPT[handle_crypt 截断<br/>zc_word[2/3] 处理]
    Q4C -- 否 --> CS_READY[生成完成]
    CS_CRYPT --> CS_READY
    CS_OFF --> Q4
    CS_READY --> Q5N{需要分配?}
    Q4 --> Q5N
    Q5N -- 需 metaslab --> A5[DVA_ALLOCATE<br/>metaslab_alloc 选 DVA]
    Q5N -- 已有 DVA --> A6[直接 READY]
    A5 --> Q5{VDEV 类型?}
    A6 --> Q5
    Q5 -- mirror/raidz --> A7[zio_vdev_child_io<br/>子 pipeline VDEV_IO_START<br/>VERIFY 下推至叶]
    Q5 -- leaf disk --> A8[vdev_queue_io<br/>spa_taskq_dispatch ZIO_TASKQ_ISSUE]
    A7 --> Q6{读 or 写?}
    A8 --> Q6
    Q6 -- 写 --> END1([VDEV_IO_DONE→ASSESS<br/>仅校验不弹栈])
    Q6 -- 读 --> Q7{VERIFY 结果?}
    Q7 -- ECKSUM --> RETRY[镜像重试<br/>vdev_mirror 择另 DVA]
    Q7 -- OK --> DECRYPT[CHECKSUM_VERIFY→DECRYPT→DECOMPRESS<br/>zio_pop_transforms 逆序还原 abd<br/>psize→lsize 解压]
    RETRY --> Q7
    DECRYPT --> END2([Done])
```

Source: `openzfs/zfs/include/sys/zio_impl.h:60-260`（`enum zio_stage` 位图与 `ZIO_*_PIPELINE`）+ `openzfs/zfs/module/zfs/zio.c:1907`（`zio_write_compress` 的 `zero/EMPTY/ge_lsize/embedded/roundup→push` 与 `lsize→psize`）+ `openzfs/zfs/module/zfs/zio.c:1777`（`zio_get_compression_max_size`）+ `openzfs/zfs/module/zfs/zio_compress.c:107`（`zio_compress_data` 的 `ci_compress`）+ `openzfs/zfs/module/zfs/zio.c:5229`（`zio_checksum_generate` 选型）+ `openzfs/zfs/module/zfs/zio.c:5260`（`zio_checksum_verify` 分支）+ `openzfs/zfs/module/zfs/zio_checksum.c:160-198`（`zio_checksum_table` 的 `ci_flags`）+ `openzfs/zfs/module/zfs/zio.c:492`（`zio_push_transform` 的 `lsize→psize`）+ `openzfs/zfs/module/zfs/vdev_queue.c:80-180`（`vdev_queue_io` 分发）+ `openzfs/zfs/module/zfs/zio_checksum.c:337`（`zio_checksum_compute` 嵌入式分线）+ `openzfs/zfs/module/zfs/zio_checksum.c:412`（`zio_checksum_error_impl` byteswap）


## 补充 状态机 — pipeline 位图推进（补图至 3 mermaid）

```mermaid
stateDiagram-v2
    [*] --> OPEN: zio_create
    OPEN --> COMPRESS: ZIO_STAGE_WRITE_COMPRESS
    COMPRESS --> ENCRYPT: ENCRYPT
    ENCRYPT --> CHECKSUM: CHECKSUM_GENERATE
    CHECKSUM --> VDEV: VDEV_IO_START
    VDEV --> DONE: ASSESS
    %% Source: openzfs/zfs/include/sys/zio_impl.h:60-260
```

Source: `openzfs/zfs/include/sys/zio_impl.h:60-260` + `openzfs/zfs/module/zfs/zio.c:2428`


## 正例

```c
// 正例1：写 pipeline 正确按位图创建与执行，transform 栈配对压弹 + checksum 非栈生成
zio_t *pio = NULL; // parent zio
zio_t *zio = zio_create(pio, spa, txg, bp, abd, lsize, psize, zio_write_done, NULL,
    ZIO_TYPE_WRITE, ZIO_PRIORITY_SYNC_WRITE, 0, NULL, 0, ZIO_STAGE_OPEN,
    ZIO_WRITE_PIPELINE); // 位图含 COMPRESS+ENCRYPT+CHECKSUM_GENERATE+DVA_ALLOCATE+READY+VDEV_IO_START
zio_execute(zio); // 内部 __zio_execute while(io_stage < DONE) 按位推进
// ZIO_STAGE_WRITE_COMPRESS: 若可压缩则 zio_push_transform(zio, abd, psize, compress_func)
// ZIO_STAGE_ENCRYPT: 若加密数据集则 zio_push_transform(zio, enc_abd, enc_size, decrypt_func)
// ZIO_STAGE_CHECKSUM_GENERATE: zio_checksum_generate 按 BP_GET_CHECKSUM(bp) 选 ci_func[0] 直写 bp->blk_cksum（非栈）
// 读完成回调中自动 zio_pop_transforms(zio) 逆序还原 abd 与 size（仅 compress/encrypt 栈）

// 正例2：VDEV 子流水线正确经 taskq 分发至 leaf，且 VERIFY 下推
zio_t *child = zio_vdev_child_io(zio, bp_child, vdev, offset, abd, psize, ZIO_TYPE_WRITE, ZIO_PRIORITY_SYNC_WRITE, 0, zio_vdev_io_done, NULL);
// child->io_pipeline = ZIO_VDEV_CHILD_PIPELINE (VDEV_IO_START|VDEV_IO_DONE|VDEV_IO_ASSESS)
// 若 type==READ 且 bp!=NULL 则 pipeline|=CHECKSUM_VERIFY 且 pio&=~CHECKSUM_VERIFY（叶侧校验）
zio_execute(child); // __zio_execute 命中 VDEV_IO_START -> spa_taskq_dispatch -> vdev_queue_io -> leaf vdev_disk_io_start

// 正例3：checksum 选型正确 — fletcher4 非 dedup、sha256 可 dedup、edonr 需 salted verify
enum zio_checksum c1 = ZIO_CHECKSUM_FLETCHER_4; // ci_flags=METADATA 仅元数据，!DEDUP
enum zio_checksum c2 = ZIO_CHECKSUM_SHA256; // ci_flags=METADATA|DEDUP|NOPWRITE 可作 dedup
enum zio_checksum c3 = ZIO_CHECKSUM_EDONR; // ci_flags=METADATA|SALTED|NOPWRITE 需 spa_cksum_tmpls 盐，verify 强制
// zp_checksum=ZIO_CHECKSUM_ON → ZIO_CHECKSUM_ON_VALUE=FLETCHER_4；dedup 时 spa_dedup_checksum→SHA256
zio_checksum_compute(zio, c2, abd, size); // 内部 abd_fletcher_4_impl: acf_init→abd_iterate_func→acf_fini
// 嵌入式：label/gang_header 的 zio_eck_t 尾部 ZEC_MAGIC 校验后 ci_func[byteswap] 计算

// 正例4：压缩选型与 lsize→psize 正确 — lz4/zstd/gzip/zle 与 compress_empty 短路
enum zio_compress co_lz4 = ZIO_COMPRESS_LZ4; // ci_level 0, ON 默认经 zio_compress_select→LZ4
enum zio_compress co_zstd = ZIO_COMPRESS_ZSTD; // ci_level 3 default, ci_decompress_level 非空, HASLEVEL 需 complevel
enum zio_compress co_gzip = ZIO_COMPRESS_GZIP_6; // ci_level 6, gzip-1..9 各等级独立表项
enum zio_compress co_zle = ZIO_COMPRESS_ZLE; // ci_level 64, n=64 literal/run 分线, zfs_zle_compress_buf
// zp_compress=ZIO_COMPRESS_ON → SPA_FEATURE_LZ4_COMPRESS active? LZ4 : LZJB
zio_prop_t zp_com; zp_com.zp_compress = ZIO_COMPRESS_LZ4; zp_com.zp_complevel = 0;
uint64_t lsize5 = 131072, psize5 = lsize5;
abd_t *abd5 = abd_alloc_linear(lsize5, B_TRUE); // 明文
// zio_write_compress 内：abd_cmp_zero!=0 → compress!=EMPTY → zio_compress_data(lz4, s_len=lsize, d_len=max_size)→psize=8000 (<lsize)
// psize> BPE_PAYLOAD_SIZE → roundup→zio_push_transform(zio, cabd, psize, lsize, NULL) // lsize→psize
// BP_SET_LSIZE(bp,lsize); BP_SET_PSIZE(bp,psize); BP_SET_COMPRESS(bp, ZIO_COMPRESS_LZ4)
// 读侧：zio_read_bp_init 中 BP_GET_COMPRESS!=OFF → zio_push_transform(psize, zio_decompress) 压 decompress，pop 时 psize→lsize 还原
// zstd 示例：zp_complevel=ZIO_ZSTD_LEVEL_3 → header {BE_32 c_len, raw_version_level} 编码 level，解压时 ci_decompress_level 回传

// 正例5：compress_empty 与不可压回退正确
abd_t *zero_abd = abd_alloc_linear(8192, B_TRUE); abd_zero(zero_abd); // 全零
// zio_write_compress：abd_cmp_zero==0 → psize=0 → compress=OFF → hole_birth 不压栈，pipeline=INTERLOCK
abd_t *incomp = abd_alloc_linear(131072, B_TRUE); // 随机不可压
// zio_compress_data → psize>=lsize → free(cabd) compress=OFF psize=lsize 不压栈，直接 BP_SET_COMPRESS OFF

// 正例6：校验失败正确自愈
// 读侧 zio_checksum_verify 失败 → vs_checksum_errors++ + zfs_ereport_start_checksum
// 镜像池择另 DVA 重试，good_copies>0 时 ZIO_FLAG_IO_REPAIR 自愈写修复
```

命中：`zio_create` 时 `ZIO_WRITE_PIPELINE` 位图与 `ZIO_TYPE_WRITE` 配对，`__zio_execute` 按位推进，`zio_push_transform` 在 `WRITE_COMPRESS`（`zio_write_compress` 的 `lsize→psize` 五分支）与 `ENCRYPT` stage 内且 `CHECKSUM_GENERATE` 非栈直写 `bp->blk_cksum`，`zio_vdev_child_io` 经 `spa_taskq_dispatch` 落 `vdev_queue_io`，`zio_compress_table` 的 `ci_compress/ci_level` 与 `enum zio_compress`（`lz4/zstd/gzip/zle/empty`）及 `ZIO_COMPRESS_HASLEVEL` 配对正确，`compress_empty`（`abd_cmp_zero→0` / `EMPTY→lsize`）短路与 `ge_lsize→OFF` 回退及 `embedded/roundup→push` 一致，`zio_checksum_table` 的 `ci_flags` 与 `enum zio_checksum` 配对正确，`byteswap` 双路径一致，读侧 `CHECKSUM_VERIFY` 后才 `DECRYPT→DECOMPRESS`（`zio_decompress` 的 `psize→lsize`）逆序 `zio_pop_transforms`。

## 反例

```c
// 反例1：pipeline 位图与 io_type 错配导致 stage 漏执行
zio_t *zio = zio_create(pio, spa, txg, bp, abd, lsize, psize, done, NULL,
    ZIO_TYPE_READ, ZIO_PRIORITY_SYNC_READ, 0, NULL, 0, ZIO_STAGE_OPEN,
    ZIO_WRITE_PIPELINE); // 错：READ 类型却配 WRITE_PIPELINE，__zio_execute 误入 WRITE_COMPRESS/ENCRYPT/CHECKSUM_GENERATE，bp 错误

// 反例2：漏配对 transform 弹栈导致 ABD 悬挂与数据错
zio_push_transform(zio, enc_abd, enc_size, decrypt_func); // 加密后替换 abd
// 漏 zio_pop_transforms：读完成未弹栈还原，abd 仍指向加密后密文，DECOMPRESS 以密文解压直接 ECKSUM
// 更隐蔽：CHECKSUM_VERIFY 失败后未重试直接上抛，漏 vs_checksum_errors 统计与 ereport

// 反例3：VDEV 子 ZIO 绕过 taskq 直接同步调用 leaf 导致调度饥饿
// 错：直接调用 vdev_disk_io_start(child) 而非 zio_execute(child)
// 结果：未进 spa_taskq_dispatch 的 ZIO_TASKQ_ISSUE 队列，绕过 vdev_queue 的 deadline 调度，破坏并发限流与 I/O 聚合
// 且叶侧 CHECKSUM_VERIFY 未下推，父 ZIO 重复校验浪费且 byteswap 分支错配

// 反例4：transform 栈深度未检查溢出
for (int i = 0; i < 16; i++)
    zio_push_transform(zio, abd, size, func); // 错：超 ZIO_TRANSFORM_STACK_DEPTH(8) 未检，直接 kmem 越界或断言

// 反例5：checksum 算法选型错 — fletcher4 作 dedup
zio_prop_t zp; zp.zp_checksum = ZIO_CHECKSUM_FLETCHER_4; zp.zp_dedup = B_TRUE;
// 错：fletcher4 的 ci_flags 仅 METADATA 无 DEDUP，zio_checksum_table[FLETCHER_4] 断言失败或静默碰撞
// 正：dedup 必须选 SHA256/SHA512/BLAKE3（具 DEDUP 标志）或经 spa_dedup_checksum 转 sha256

// 反例6：误将 CHECKSUM_GENERATE 当栈变换 push
zio_push_transform(zio, abd, size, checksum_func); // 错：CHECKSUM_GENERATE 非栈，后续 zio_pop_transforms 多弹一次导致 abd 错
// 正：GENERATE 仅 zio_checksum_compute 写 bp->blk_cksum，不 push；VERIFY 亦不 push，仅校验

// 反例7：byteswap 分支遗漏导致跨平台校验误判
// 错：始终 ci_func[0] 而不按 BSWAP_64(ZEC_MAGIC) / BP_SHOULD_BYTESWAP 选 ci_func[byteswap]
// 结果：小端写入大端读取时 fletcher4/sha512 的 actual 与 expected 恒不等，误报 ECKSUM

// 反例8：edonr 未启用 salted 模板导致校验不一致
// 错：未调用 ci_tmpl_init 构造 spa_cksum_tmpls[EDONR] 即直接 abd_checksum_edonr_native
// 结果：带盐哈希未混入 DMU_POOL_CHECKSUM_SALT，dedup 时已知明文碰撞可构造

// 反例9：compress 选型错 — zstd 未传 level 导致 INHERIT 回退
zio_prop_t zp9; zp9.zp_compress = ZIO_COMPRESS_ZSTD; zp9.zp_complevel = ZIO_COMPLEVEL_INHERIT;
// 错：zstd 的 complevel 为 INHERIT 时 zio_compress_data 直接 return s_len（不可压），误以为压缩失败
// 正：zstd 必须经 zio_complevel_select 选 parent 或 DEFAULT(3)，且 ci_decompress_level 需回传 level 供解压校验

// 反例10：compress_empty 误当普通压缩调用 ci_compress
enum zio_compress c10 = ZIO_COMPRESS_EMPTY;
// 错：直接 zio_compress_data(EMPTY, ...) → ASSERT(ci_compress!=NULL) 崩溃，因 EMPTY 的 ci_compress 为 NULL 仅作占位
// 正：zio_write_compress 中 compress==EMPTY 时 psize=lsize 短路，不调 ci_compress；全零块走 abd_cmp_zero→psize 0 hole

// 反例11：lsize→psize 漏 roundup 导致分配不对齐
size_t psize11 = 9000; // 假定压后 9000
// 错：直接 BP_SET_PSIZE(bp, 9000) 而不经 zio_roundup_alloc_size → psize 未对齐 spa_gcd_alloc，落盘后 BP 与 vdev asize 不一致，EIO
// 正：必须 rounded=roundup(psize) 且 rounded<lsize 才 push，否则 OFF 回退；且 abd_zero_off 补零尾部

// 反例12：解压时错选 ci_decompress 而漏 ci_decompress_level（zstd）
// 错：zstd 块始终 ci_decompress(src,dst,psize,lsize,ci_level) 而不经 ci_decompress_level→level 回传
// 结果：压缩时 level=6 的块解压时用 ci_level=3 默认解压，header 中 level 校验失败 → EIO；正为 ci_decompress_level 回写 zp_complevel
```

## 门禁

- **多图门禁**：`grep -c '```mermaid' records/T0523-0903-research-zfs-compress/research-compress.md` ≥3 且 `grep -c '```mermaid' records/T0522-0903-research-zfs-checksum/research-checksum.md` ≥3
- **溯源门禁**：`grep -c 'Source:' records/T0523-0903-research-zfs-compress/research-compress.md` ≥3 且 `grep -c 'Source:' records/T0522-0903-research-zfs-checksum/research-checksum.md` ≥3 且每图附 `openzfs/zfs file:line`
- **压缩算法覆盖门禁**：`grep -q 'lz4' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'zstd' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'gzip' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'zle' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'ZIO_STAGE_WRITE_COMPRESS' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'zio_decompress' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'lsize' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'psize' records/T0523-0903-research-zfs-compress/research-compress.md`
- **校验算法回归门禁**：`grep -q 'fletcher4' records/T0522-0903-research-zfs-checksum/research-checksum.md && grep -q 'sha256' records/T0522-0903-research-zfs-checksum/research-checksum.md && grep -q 'sha512' records/T0522-0903-research-zfs-checksum/research-checksum.md && grep -q 'edonr' records/T0522-0903-research-zfs-checksum/research-checksum.md && grep -q 'ZIO_STAGE_CHECKSUM_GENERATE' records/T0522-0903-research-zfs-checksum/research-checksum.md && grep -q 'ZIO_STAGE_CHECKSUM_VERIFY' records/T0522-0903-research-zfs-checksum/research-checksum.md`
- **压缩分支门禁**：`grep -q 'zio_compress' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'zio_compress_info_t' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'compress_empty' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'ZIO_COMPRESS_EMPTY' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'zio_compress_data' records/T0523-0903-research-zfs-compress/research-compress.md`
- **校验分支回归门禁**：`grep -q 'zio_checksum' records/T0522-0903-research-zfs-checksum/research-checksum.md && grep -q 'zio_checksum_info_t' records/T0522-0903-research-zfs-checksum/research-checksum.md && grep -q 'abd_checksum' records/T0522-0903-research-zfs-checksum/research-checksum.md && grep -q 'ZCHECKSUM_FLAG_DEDUP' records/T0522-0903-research-zfs-checksum/research-checksum.md`
- **栈门禁**：`grep -q 'zio_push_transform' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'zio_pop_transforms' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'zio_write_compress' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'zio_decompress' records/T0523-0903-research-zfs-compress/research-compress.md && grep -q 'lsize.*psize' records/T0523-0903-research-zfs-compress/research-compress.md`
- **校验栈回归门禁**：`grep -q 'zio_push_transform' records/T0522-0903-research-zfs-checksum/research-checksum.md && grep -q 'zio_pop_transforms' records/T0522-0903-research-zfs-checksum/research-checksum.md && grep -q 'zio_checksum_generate' records/T0522-0903-research-zfs-checksum/research-checksum.md && grep -q 'zio_checksum_verify' records/T0522-0903-research-zfs-checksum/research-checksum.md`
- **正文门禁**：`wc -l ontology/entity/zfs-zio.md` ≥60 且 `grep -q '决策树' ontology/entity/zfs-zio.md && grep -q '正例' ontology/entity/zfs-zio.md && grep -q '反例' ontology/entity/zfs-zio.md && grep -q '门禁' ontology/entity/zfs-zio.md && grep -q 'Compress 分支' ontology/entity/zfs-zio.md && grep -q 'Checksum 分支' ontology/entity/zfs-zio.md`
- **属性门禁**：`attributes` 数量 ≥3 且每条 `testable_signal` 含 `grep -q` 动词+判定，且 `grep -q "zio_compress" ontology/entity/zfs-zio.md` 命中且 `grep -q "zio_checksum" ontology/entity/zfs-zio.md` 命中
- **本体校验**：`python3 scripts/ontology-validate.py --ontology-dir ontology` 0 issues 且 `python3 scripts/ontology_graph.py --format summary` `islands:0`
- **脚手架门禁**：`python3 scripts/ontology_test_scaffold.py --node ontology:entity/zfs-zio --out /tmp/test_zfs_zio_scaffold.py` 可产且 `pytest` 可收集
- **收敛门禁**：`python3 scripts/validate-convergence.py --task-dir pdca/tasks/0903-research-zfs-compress` `valid:true` 且 `python3 scripts/validate-convergence.py --task-dir pdca/tasks/0903-research-zfs-checksum` `valid:true`
- **T0516 回归门禁**：`grep -q 'ZIO_WRITE_PIPELINE' records/T0516-0903-research-zfs-zio/research-zio.md` 仍命中（不破坏已有门禁）

Source: `openzfs/zfs/include/sys/zio_impl.h:60-260`（`enum zio_stage`）+ `openzfs/zfs/module/zfs/zio.c:934`（`zio_create`）+ `openzfs/zfs/module/zfs/zio.c:2428`（`__zio_execute`）+ `openzfs/zfs/module/zfs/zio.c:492`（`zio_push_transform` 的 `lsize→psize`）+ `openzfs/zfs/module/zfs/vdev_queue.c:80-180`（`vdev_queue_io`）+ `openzfs/zfs/module/zfs/vdev.c:120`（`vdev_alloc`）+ `openzfs/zfs/include/sys/zio_compress.h:31-49`（`enum zio_compress`）+ `openzfs/zfs/include/sys/zio_compress.h:129-135`（`zio_compress_info_t`）+ `openzfs/zfs/module/zfs/zio_compress.c:33-64`（`zio_compress_table`）+ `openzfs/zfs/module/zfs/zio_compress.c:107`（`zio_compress_data`）+ `openzfs/zfs/module/zfs/zio_compress.c:144`（`zio_decompress_data`）+ `openzfs/zfs/module/zfs/zio.c:1907`（`zio_write_compress` 的 `lsize→psize`）+ `openzfs/zfs/module/zfs/zio.c:1803`（`zio_read_bp_init` 的 `decompress`）+ `openzfs/zfs/module/zfs/zio.c:545`（`zio_decompress`）+ `openzfs/zfs/include/sys/zio.h:85-100`（`enum zio_checksum`）+ `openzfs/zfs/module/zfs/zio_checksum.c:160-198`（`zio_checksum_table`）+ `openzfs/zfs/module/zfs/zio_checksum.c:337`（`zio_checksum_compute`）+ `openzfs/zfs/module/zfs/zio_checksum.c:412`（`zio_checksum_error_impl`）+ `openzfs/zfs/module/zfs/zio.c:5229`（`zio_checksum_generate`）+ `openzfs/zfs/module/zfs/zio.c:5260`（`zio_checksum_verify`）
