# bcachefs 压缩加密专题学习报告（代码级精讲扩充版）

> 事实源：`fs/data/compress.c`（835 行）、`fs/data/checksum.c`（681 行）、
> `c_src/crypto.c`（202 行），辅以 `fs/data/checksum.h`（251 行）、
> `fs/data/compress.h`（84 行）、`fs/data/read.c`、`fs/data/write.c` 作调用链核实。
> 行号函数名均经 Grep/Read 核实。八节结构保留，每节逐函数精讲：
> 签名 / 参数 / 返回 / 调用链 / ≤10 行代码片段 / 权衡。

---

## 一、全景：压缩加密校验三明治

写路径固定顺序：压缩 → 校验 → 加密；读路径逆序：校验 → 解密 → 解压。
顺序是安全不变量，不是调优点：先校验密文再解密（`read.c:974`），
解密后才能解压（`read.c:1007-1009`，`write.c:1710-1719`）。

核心函数地图（详见后各节）：

- 压缩入口：`bch2_bio_compress`（`compress.c:592`）→ `bch2_compress`（`:475`）→ `attempt_compress`（`:372`）。
- 解压入口：`bch2_bio_uncompress`（`compress.c:346`）→ `bch2_buf_uncompress`（`:244`）→ `bch2_decompress_err`（`:338`）。
- 校验入口：`bch2_checksum`（`checksum.c:132`）/`bch2_checksum_bio`（`:246`）→ `__bch2_checksum_bio`（`:184`）。
- 加解密：`bch2_encrypt`（`checksum.c:170`）/`__bch2_encrypt_bio`（`:254`），读侧经 `bch2_rbio_decrypt`（`read.c:946`）复用 ChaCha 自反性解密。
- 重算：`bch2_rechecksum_bio`（`checksum.c:313`），读窄化（`read.c:921`）与写改型（`write.c:1662/2022`）共用。
- 密钥：`bch2_request_key`（`checksum.c:494`）→ `bch2_decrypt_sb_key`（`:539`）→ `bch2_fs_encryption_init`（`:671`）；用户态 KDF 在 `c_src/crypto.c:58`。

**可学**：分层顺序即错误归因顺序；任何“先解压后校验”的调优都会把损坏密文洗成解压错。

---

## 二、压缩选型：启发加分池

### 2.1 `bch2_opt_compression_parse`（`compress.c:766`）

- 签名：`int bch2_opt_compression_parse(struct bch_fs *c, const char *_val, u64 *res, struct printbuf *err)`
- 参数：`_val` 如 `zstd:3`；`res` 输出打包的 `union bch_compression_opt`（`compress.h:13`，`type:4,level:4`）；`err` 解释错误。
- 返回：0 成功，`<0` 为 `-ENOMEM`/`-EINVAL`/`match_string` 负值。
- 调用链：mount/opts 解析 → `bch2_compression_opt_valid`（`compress.h:24`）复核 → `bch2_fs_compress_init` 按需建池。
- 片段（`compress.c:776-785`，8 行）：
```c
type_str = strsep(&p, ":");
level_str = p;
int ret = match_string(bch2_compression_opts, -1, type_str);
if (ret < 0 && err)
    prt_printf(err, "invalid compression type\n");
if (ret < 0)
    return ret;
opt.type = ret;
```
- 权衡：`none` 配 level 非零直接 `-EINVAL`（`:791-792`）；level 上限硬卡 15（`:793-794`），zstd 内部再按 `(level*3)/2` 重缩放（`:445`），把用户语义与后端量程解耦。

### 2.2 `bch2_compression_type_to_opt`（`compress.c:54`）

- 签名：`static inline enum bch_compression_opts bch2_compression_type_to_opt(enum bch_compression_type type)`
- 参数/返回：压缩类型枚举 → 选项枚举；`default: BUG()`。
- 调用链：仅 `bch2_buf_uncompress`（`:248`）用它选解压 workspace 池。
- 片段（`:56-62`，7 行）：
```c
switch (type) {
case BCH_COMPRESSION_TYPE_none:
case BCH_COMPRESSION_TYPE_incompressible:
    return BCH_COMPRESSION_OPT_none;
case BCH_COMPRESSION_TYPE_lz4_old:
case BCH_COMPRESSION_TYPE_lz4:
```
- 权衡：`lz4_old` 兼容解码但永不新写；类型→池的映射保证老数据可读、新池按需建。

### 2.3 `bch2_fs_compress_init` / `__bch2_fs_compress_init`（`compress.c:756/690`）

- 签名：`int bch2_fs_compress_init(struct bch_fs *c)`；`static int __bch2_fs_compress_init(struct bch_fs *c, u64 features)`
- 参数：`c->opts.compression/background_compression` 经 `compression_opt_to_feature`（`:749`）并入 `features`；后者再与超块 `features` 取并。
- 返回：0 或 `ENOMEM_compression_*`。
- 调用链：mount → `bch2_fs_compress_init` → `__bch2_fs_compress_init`；写时缺池经 `bch2_check_set_has_compressed_data`（`:666`）→ `__bch2_check_set_has_compressed_data`（`:649`）懒补建并写超块。
- 片段（`:718-729`，10 行内取关键 8 行）：
```c
if (!have_compressed)
    return 0;
if (!mempool_initialized(&c->compress.bounce[READ]) &&
    mempool_init_kvmalloc_pool(&c->compress.bounce[READ],
                   1, c->opts.encoded_extent_max))
    return bch_err_throw(c, ENOMEM_compression_bounce_read_init);
```
- 权衡：无压缩需求零分配；读写 bounce 池各 1 个 `encoded_extent_max` 上限元素（`:722-729`），读写分池防死锁；workspace 按算法取 max（lz4 `:702-703`、gzip `:704-706`、zstd `:707-709`），内存换免分配热路径。

### 2.4 `bch2_bounce_alloc` / `bch2_bio_bounce` / `__bch2_bio_map_or_bounce` / `bch2_bio_map_or_bounce`（`compress.c:91/138/165/232`）

- 签名：`struct bbuf bch2_bounce_alloc(struct bch_fs *c, unsigned size, int rw)`；`struct bbuf bch2_bio_bounce(struct bch_fs *c, struct bio *bio, struct bvec_iter start, int rw)`；`struct bbuf bch2_bio_map_or_bounce(struct bch_fs *c, struct bio *bio, int rw)`。
- 参数：`size` 受 `BUG_ON(size > encoded_extent_max)`（`:95`）硬拦截；`rw` 区分 READ/WRITE 池。
- 返回：`struct bbuf`（`compress.h:42`，`BB_none/BB_vmap/BB_kmalloc/BB_mempool` 四态）配 `__cleanup(bch2_bbuf_exit)`（`:74`）自动释放。
- 调用链：`bch2_bio_compress`（`:610-613`）、`bch2_bio_uncompress`（`:359-362`）、`bch2_write_op_decode`（`write.c:1701-1713`）均为调用方。
- 片段（`compress.c:127-133`，7 行）：
```c
b = kmalloc(size, GFP_NOIO|__GFP_NOWARN|__GFP_SKIP_ZERO);
if (b)
    return (struct bbuf) { .c = c, .b = b, .type = BB_kmalloc, .rw = rw };
b = mempool_alloc(&c->compress.bounce[rw], GFP_NOIO);
```
- 权衡：kmalloc 优先、mempool 兜底、最终 `BUG()`（`:135`）——宁可崩也不静默降级；`__GFP_SKIP_ZERO`（`:98-126` 大段注释）对热 bounce 跳过发行版默认清零，理由是三类输出要么全覆盖、要么错即弃、要么按压缩长裁剪；`__bch2_bio_map_or_bounce` 先物理连续直映射（`:171-180`）、再 vmap（`:216-226`）、最后才拷贝，保证零拷贝优先。

**可学**：小 IO 跳过（见 3.2）、池按需建、上限硬拦截是三条硬规则，不是启发。

---

## 三、失败处理：重试验证传播

### 3.1 `attempt_compress`（`compress.c:372`，static）

- 签名：`static int attempt_compress(struct bch_fs *c, void *workspace, void *dst, size_t dst_len, void *src, size_t src_len, union bch_compression_opt compression)`
- 参数：`workspace` 为对应算法池内存；`dst/src+len` 均为 512 对齐（`:387-388` 双 `BUG_ON`）；`compression` 含 type/level。
- 返回：`>0` 压缩后字节；`=0` 本轮失败可重试；`<0`（仅 lz4 路）为“能装下多少”的提示值（`:398-399` 返回 `-len`）。
- 调用链：`bch2_compress` 循环内唯一压缩原语；三后端分岔 lz4（`:391-413`）/gzip（`:414-439`）/zstd（`:440-469`）。
- 片段（`:460-468`，9 行）：
```c
size_t len = zstd_compress_cctx(ctx,
        dst + 4,    dst_len - 4 - 7,
        src,        src_len,
        &params);
if (zstd_is_error(len))
    return 0;
*((__le32 *) dst) = cpu_to_le32(len);
return len + 4;
```
- 权衡：zstd 头 4 字节存真实长（解压要求精确长，四舍五入到扇区不行，`:449-454` 注释），尾部再扣 7 字节防后端越界写（`:456-458`）；lz4HC 尾部同样预留 7 字节防 `LZ4_wildCopy` 越界（`:378-383`）；gzip 任何 zlib 非终态直接回 0（`:432-436`），不区分原因、交上层统一折半。

### 3.2 `bch2_compress`（`compress.c:475`，static）

- 签名：`static unsigned bch2_compress(struct bch_fs *c, void *dst, size_t *dst_len, void *src, size_t *src_len, unsigned compression_opt, struct bpos write_pos)`
- 参数：`*dst_len/*src_len` 既是输入上限又是输出实长；`compression_opt` 为打包值；`write_pos` 仅用于校验失败打点。
- 返回：`enum bch_compression_type`，成功为具体类型，失败为 `BCH_COMPRESSION_TYPE_incompressible` 单向标记。
- 调用链：`bch2_bio_compress`（`:615-620`）→ 本函数 → `attempt_compress`；缺池时经 `compression_opt_not_marked_in_sb` fsck 钩子懒建池（`:496-506`）。
- 片段（`:484-490` + `:514-546` 取 10 行核心循环）：
```c
/* If it's only one block, don't bother trying to compress: */
if (*src_len <= c->opts.block_size)
    return BCH_COMPRESSION_TYPE_incompressible;
```
```c
ret = attempt_compress(c, workspace, dst, *dst_len, src, *src_len, compression);
if (ret > 0) { *dst_len = ret; ret = 0; break; }
if (*src_len <= *dst_len) { ret = -1; break; }
if (ret < 0) *src_len = -ret;
else         *src_len -= (*src_len - *dst_len) / 2;
*src_len = round_down(*src_len, block_bytes(c));
```
- 权衡：单块直返不可压缩（硬规则）；折半收敛必终止（`src<=block` 或 `src<=dst` 双出口 `:515-534`）；成功还须“严格更小”——`round_up(dst) >= src` 仍判不可压缩（`:554-555`），防元数据膨胀；尾部补零到块对齐（`:557-560`）。

### 3.3 写时验证 `bch2_verify_compress` 开关 + 内联 verify 块（`compress.c:50-52/562-585`）

- 签名：模块参数 `bool bch2_verify_compress = IS_ENABLED(CONFIG_BCACHEFS_DEBUG)`。
- 参数/返回：开关量；验证块内 `bch2_buf_uncompress` + `memcmp`，失配记 `compression_error` fsck 并回退 `incompressible`。
- 调用链：`bch2_compress` 尾部（`:562`）→ `bch2_bounce_alloc` 取 verify 缓冲 → `bch2_buf_uncompress`。
- 片段（`:569-572`，4 行）：
```c
struct bbuf verify __cleanup(bch2_bbuf_exit) = bch2_bounce_alloc(c, *src_len, WRITE);
ret = bch2_buf_uncompress(c, verify.b, dst, crc);
BUG_ON(ret);
```
- 权衡：默认仅 DEBUG 开启，生产免付往返解压；一旦开启即 `BUG_ON(ret)` + `memcmp` 双保险，把压缩器 bug 转为可记账 fsck 而非静默坏数据。

### 3.4 `bch2_buf_uncompress`（`compress.c:244`）

- 签名：`int bch2_buf_uncompress(struct bch_fs *c, void *dst, void *src, struct bch_extent_crc_unpacked crc)`
- 参数：`crc.compressed_size/uncompressed_size` 以扇区计，内转字节（`:259-260` `<<9`）；`crc.compression_type` 经 2.2 选池。
- 返回：0 或 `decompress_lz4[_old]/gzip[_size_mismatch]/zstd_*`。
- 调用链：`bch2_bio_uncompress`（`:364`）、`bch2_compress` 验证块（`:570`）、`bch2_write_op_decode`（`write.c:1719`）共用。
- 片段（`:294-306`，取 9 行 zstd 头校验）：
```c
ZSTD_DCtx *ctx;
size_t real_src_len = le32_to_cpup(src);
if (real_src_len > src_len - 4)
    return bch_err_throw(c, decompress_zstd_src_len_bad);
void *workspace = mempool_alloc(workspace_pool, GFP_NOIO);
ctx = zstd_init_dctx(workspace, zstd_dctx_workspace_bound());
size_t ret = zstd_decompress_dctx(ctx, dst, dst_len, src + 4, real_src_len);
```
- 权衡：lz4 用 `LZ4_decompress_safe_partial` 且要求 `ret == dst_len`（`:265-270`），防截断谎报；gzip 双检 `Z_STREAM_END` + `avail_out==0`（`:288-291`）；zstd 先验头长再解、错码经 `zstd_err_to_bch_err` 透出（`:310-317`），三后端“长度全等”语义统一。

### 3.5 `bch2_bio_uncompress`（`compress.c:346`）+ `bch2_decompress_err`（`:338`）

- 签名：`int bch2_bio_uncompress(struct bch_fs *c, struct bio *src, struct bio *dst, struct bvec_iter dst_iter, struct bch_extent_crc_unpacked crc)`；`int bch2_decompress_err(struct bch_fs *c, int ret)`。
- 参数：`dst_iter` 支持子区解压（`crc.offset<<9` 偏置 `:368`）；双 `BUG_ON` 校验 `dst_iter+offset` 与 `src->bi_size==compressed<<9`（`:352-353`）；`encoded_extent_max` 双向硬拦截（`:355-357`）。
- 返回：0 或透传解压错；`bch2_decompress_err` 在非 `no_data_io` 下记 `bch2_sb_error_count`（`:340-342`）。
- 调用链：读 `__bch2_read_endio_work`（`read.c:1009/1042`）→ 本函数；写搬运 `bch2_write_op_decode`（`write.c:1719`）→ `bch2_buf_uncompress` → `bch2_decompress_err`。
- 片段（`compress.c:359-364`，6 行）：
```c
struct bbuf dst_buf __cleanup(bch2_bbuf_exit) = dst_len == dst_iter.bi_size
    ? __bch2_bio_map_or_bounce(c, dst, dst_iter, WRITE)
    : bch2_bounce_alloc(c, dst_len, WRITE);
struct bbuf src_buf __cleanup(bch2_bbuf_exit) = bch2_bio_map_or_bounce(c, src, READ);
try(bch2_decompress_err(c, bch2_buf_uncompress(c, dst_buf.b, src_buf.b, crc)));
```
- 权衡：整 extent 解压才给直映射，否则整分配再 `memcpy_to_bio` 偏置子区（`:366-368`），用内存换校验覆盖粒度；每次解压失败都计数（注释 `:327-337`），move 路“满盘不可移动压缩盘”先看此计数定责。

### 3.6 `bch2_bio_compress`（`compress.c:592`，写路径总入口）

- 签名：`unsigned bch2_bio_compress(struct bch_fs *c, struct bio *dst, size_t *dst_len, struct bio *src, size_t *src_len, unsigned compression_opt, struct bpos write_pos, bool bounce_source)`
- 参数：`consume_src=min(bi_size, encoded_extent_max)`（`:600`）截断输入；`consume_dst=min(bi_size, consume_src)`（`:602`）保证输出不大于输入；`bounce_source` 决定源是否强制拷贝。
- 返回：压缩类型；`none/incompressible` 时不回拷（`:622-623`）。
- 调用链：`bch2_write_extent`（`write.c:1972`）→ 本函数 → `bch2_compress`。
- 片段（`:604-613`，9 行）：
```c
swap(dst->bi_iter.bi_size, consume_dst);
swap(src->bi_iter.bi_size, consume_src);
*src_len = src->bi_iter.bi_size;
*dst_len = dst->bi_iter.bi_size;
struct bbuf dst_data __cleanup(bch2_bbuf_exit) = bch2_bio_map_or_bounce(c, dst, WRITE);
struct bbuf src_data __cleanup(bch2_bbuf_exit) = bounce_source
```
- 权衡：`swap(bi_size)` 临时收窄 bio 视窗、退出复原（`:632-633`），不改 bio 结构即限界；双 `BUG_ON(!*len || >bi_size)`（`:628-629`）保证压缩前后长度契约。

**可学**：重试必收敛（折半+双出口）、输出必验证（DEBUG 回环）、否定标记单向（`incompressible` 一旦判即不再试）。

---

## 四、校验协商：强度分级

### 4.1 `bch2_csum_opt_to_type`（`checksum.h:115`）

- 签名：`static inline enum bch_csum_type bch2_csum_opt_to_type(enum bch_csum_opt type, bool data)`
- 参数：用户选项 `none/crc32c/crc64/xxhash`；`data` 区分数据/元数据。
- 返回：元数据恒强——`crc32c→crc32c_nonzero`、 `crc64→crc64_nonzero`（`:122-124`）。
- 调用链：`bch2_data_checksum_type`（`:132`）、`bch2_meta_checksum_type`（`:157`）及 `sb/io.c:1186` 超块初始化共用。
- 片段（`:118-124`，7 行）：
```c
switch (type) {
case BCH_CSUM_OPT_none:   return BCH_CSUM_none;
case BCH_CSUM_OPT_crc32c: return data ? BCH_CSUM_crc32c : BCH_CSUM_crc32c_nonzero;
case BCH_CSUM_OPT_crc64:  return data ? BCH_CSUM_crc64 : BCH_CSUM_crc64_nonzero;
```
- 权衡：`nonzero` 变体种子为全 1（`checksum.c:43-47`），专防“全零页 crc==0 与无校验混淆”。

### 4.2 `bch2_data_checksum_type` / `bch2_meta_checksum_type`（`checksum.h:132/157`）

- 签名：`static inline enum bch_csum_type bch2_data_checksum_type(struct bch_fs *c, struct bch_inode_opts opts)`；`static inline enum bch_csum_type bch2_meta_checksum_type(struct bch_fs *c)`。
- 参数/返回：数据侧 `nocow→0`（无校验，`:135-136`）；加密覆盖一切——数据按 `wide_macs` 选 `poly1305_128/80`（`:138-141`），元数据恒 `poly1305_128`（`:159-160`）。
- 调用链：写分配 checksum 类型协商；`bch2_checksum_type_valid`（`:165`）再卡“加密类型无 key 即非法”（`:171-172`）。
- 片段（`:135-142`，8 行）：
```c
if (opts.nocow)
    return 0;
if (c->sb.encryption_type)
    return c->opts.wide_macs
        ? BCH_CSUM_chacha20_poly1305_128
        : BCH_CSUM_chacha20_poly1305_80;
return bch2_csum_opt_to_type(opts.data_checksum, true);
```
- 权衡：性能（nocow 裸写）与安全（加密即宽 MAC）分层取舍写死，不给用户配出“加密+弱校验”组合。

### 4.3 `csum_vstruct`（`checksum.h:41`）+ `bch2_checksum_mergeable`（`:12`）/ `bch2_checksum_merge`（`checksum.c:289`）

- 签名：宏 `csum_vstruct(_c,_type,_nonce,_i)` → `bch2_checksum(_c,_type,_nonce,start,vstruct_end-start)`；`struct bch_csum bch2_checksum_merge(unsigned type, struct bch_csum a, struct bch_csum b, size_t b_len)`。
- 参数：`_i` 为 sb/bset/jset 等“首字段即 csum”的变长结构；`_start` 跳过自身 csum（`:43`）。
- 返回：校验和；`merge` 仅 `none/crc32c/crc64` 可合并（`:15-19`），否则 `BUG_ON`（`:298`）。
- 调用链：sb（`sb/io.c:866/1187`）、bset（`btree/write.c:484`）、jset（`journal/write.c:801`）写时算；`bch2_rechecksum_bio` 可合并路径逐 split 重算再 `merge`（`checksum.c:354-357`）。
- 片段（`:41-46`，6 行）：
```c
#define csum_vstruct(_c, _type, _nonce, _i)                \
({                                    \
    const void *_start = ((const void *) (_i)) + sizeof((_i)->csum);\
    bch2_checksum(_c, _type, _nonce, _start, vstruct_end(_i) - _start);\
})
```
- 权衡：自描述跳自身是“校验不自指”铁律；合并用零页补 `b_len` 再异或（`:300-310`），线性校验和可分段、加密 MAC 不可——`rechecksum` 遇到加密类型强制整算（`:334-335`）。

### 4.4 `bch2_checksum_init/update/final`（`checksum.c:35/75/57`）+ `bch2_checksum`（`:132`）

- 签名：`static void bch2_checksum_init(struct bch2_checksum_state *state)`；`static void bch2_checksum_update(... const void *data, size_t len)`；`static u64 bch2_checksum_final(...)`；`struct bch_csum bch2_checksum(struct bch_fs *c, unsigned type, struct nonce nonce, const void *data, size_t len)`。
- 参数：`state={seed|h64state}+type`（`:27-33`）；`bch2_checksum` 对加密类型走 poly 路（`:152-164`），`nonce` 仅该路有效。
- 返回：`{ .lo = cpu_to_le64(final) }`（`:149`）；poly 按 `bch_crc_bytes[type]` 截断拷贝（`:162`，80/128 位两档）。
- 片段（`:35-44`，取 7 行）：
```c
switch (state->type) {
case BCH_CSUM_none:
case BCH_CSUM_crc32c:
case BCH_CSUM_crc64:
    state->seed = 0;
    break;
case BCH_CSUM_crc32c_nonzero:
```
- 权衡：crc 系种子可合流（供 4.3 合并），xxhash 用流式 `h64state`（`:50/:89`）；`none` 在 update 直接 return（`:78-79`），零成本短路。

### 4.5 `__bch2_checksum_bio` / `bch2_checksum_bio`（`checksum.c:184/246`）

- 签名：`static struct bch_csum __bch2_checksum_bio(struct bch_fs *c, unsigned type, struct nonce nonce, struct bio *bio, struct bvec_iter *iter)`；`struct bch_csum bch2_checksum_bio(struct bch_fs *c, unsigned type, struct nonce nonce, struct bio *bio)`。
- 参数：`iter` 允许子区迭代；HIGHMEM 用 `bvec_kmap_local`（`:204-209`），否则 `bvec_virt`（`:211-212`）；poly 路同样逐段 `poly1305_update`（`:225-235`）。
- 返回：`struct bch_csum`。
- 调用链：读验（`read.c:974`）、写验（`write.c:1791-1812`）、`bch2_rechecksum_bio` 内逐 split（`:347`）与整算（`:359`）均为调用方。
- 片段（`:246-252`，7 行）：
```c
struct bch_csum bch2_checksum_bio(struct bch_fs *c, unsigned type,
                  struct nonce nonce, struct bio *bio)
{
    struct bvec_iter iter = bio->bi_iter;
    return __bch2_checksum_bio(c, type, nonce, bio, &iter);
}
```
- 权衡：`none` 直接回零（`:191-192`）；调用方传 `iter` 指针实现“算一段、前进一步”（`rechecksum.c:345-350`），零拷贝分段校验。

### 4.6 `bch2_rechecksum_bio`（`checksum.c:313`）

- 签名：`int bch2_rechecksum_bio(struct bch_fs *c, struct bio *bio, struct bversion version, struct bch_extent_crc_unpacked crc_old, struct bch_extent_crc_unpacked *crc_a, *crc_b, unsigned len_a, len_b, unsigned new_csum_type)`
- 参数：`bio` 整 extent；`len_a/len_b` 为要切出的两段，余下为第三 split（`:329-333` 三槽数组）；`crc_old` 必须非压缩（`:340` `BUG_ON`）、加解密属性必须同侧（`:341-342`）。
- 返回：0 或 `recompute_checksum`；失配打 `WARN_RATELIMIT` 并打印新旧类型（`:362-377`）。
- 调用链：读窄化（`read.c:921`）、写 `bch2_write_rechecksum`（`write.c:1662` 整切/`:2022` 子集）→ 本函数；加密类型 nonce 按 `crc_nonce += len` 步进（`:392-393`）。
- 片段（`:344-352`，9 行）：
```c
for (i = splits; i < splits + ARRAY_SIZE(splits); i++) {
    iter.bi_size = i->len << 9;
    if (mergeable || i->crc)
        i->csum = __bch2_checksum_bio(c, i->csum_type, nonce, bio, &iter);
    else
        bio_advance_iter(bio, &iter, i->len << 9);
    nonce = nonce_add(nonce, i->len << 9);
}
```
- 权衡：可合并则分段算再合（省一次全量）、不可合并（xxhash/加密）则只算所需段、第三段 `crc==NULL` 时可合并仍要算（为整体 `merge` 提供输入 `:346` 条件）；“先整验旧、再签新”（`:354-360`），损坏内存不被新校验洗白。

**可学**：元数据恒强不可协商；自描述跳自身；合并白名单制；窄化三分裂。

---

## 五、先验后解：错误优先级

### 5.1 `bch2_checksum_bio` 先验（`read.c:974-975` 经 `__bch2_read_endio_work:955`）

- 签名：`static int __bch2_read_endio_work(struct bch_read_bio *rbio)`（`read.c:955`）。
- 参数：`rbio->{bio,pick.crc,version,bounce,flags}`；`nonce=extent_nonce(version,crc)`（`:964`）。
- 返回：0 或 `data_read_retry_csum_err[_maybe_userspace]/data_read_decrypt_err`/解压错。
- 调用链：`bch2_read_endio`（`:1097`）→ `bch2_read_endio_work`（`:1079`）→ 本函数 → `bch2_checksum_bio` → `bch2_rbio_decrypt` → `bch2_bio_uncompress`。
- 片段（`:974-985`，取 8 行核心）：
```c
csum = bch2_checksum_bio(c, crc.csum_type, nonce, src);
bool csum_good = !bch2_crc_cmp(csum, rbio->pick.crc.csum) || c->opts.no_data_io;
if (!csum_good && !rbio->bounce && (rbio->flags & BCH_READ_user_mapped)) {
    rbio->flags |= BCH_READ_must_bounce;
    return bch_err_throw(c, data_read_retry_csum_err_maybe_userspace);
}
```
- 权衡：直写用户页时先疑“用户串改”而非盘坏，强制 bounce 重试一次，把用户内存竞争与介质错误分离归因。

### 5.2 `bch2_rbio_decrypt`（`read.c:946`）+ `bch2_encrypt`（`checksum.c:170`）/ `bch2_encrypt_bio`（`checksum.h:94`）/ `__bch2_encrypt_bio`（`checksum.c:254`）

- 签名：`static int bch2_rbio_decrypt(struct bch_fs *c, struct bch_read_bio *rbio, struct bch_extent_crc_unpacked crc, struct nonce nonce)` → `return bch2_encrypt_bio(...) ? data_read_decrypt_err : 0`（`:949-951`）；`int bch2_encrypt(struct bch_fs *c, unsigned type, struct nonce nonce, void *data, size_t len)`；`int __bch2_encrypt_bio(struct bch_fs *c, unsigned type, struct nonce nonce, struct bio *bio)`。
- 参数：非加密类型 `bch2_encrypt` 直接回 0（`:173-174`）；无 key 即 `no_encryption_key` 不一致错（`:176-178`）；bio 路要求每段 `CHACHA_BLOCK_SIZE` 对齐、末段除外（`:275-279`）。
- 调用链：读压缩/非压缩双路（`read.c:1007/1020`）、data_update 验后重加密（`:1047`）、promote 回填（`:1068`）；写侧 `write.c:1716/1871/2050`。
- 片段（`checksum.c:170-181`，9 行取关键 8 行）：
```c
int bch2_encrypt(struct bch_fs *c, unsigned type,
          struct nonce nonce, void *data, size_t len)
{
    if (!bch2_csum_type_is_encryption(type))
        return 0;
    if (bch2_fs_inconsistent_on(!c->chacha20_key_set,
                    c, "attempting to encrypt without encryption key"))
        return bch_err_throw(c, no_encryption_key);
```
- 权衡：ChaCha 加解密自反，同一函数双向复用；bio 路全程 `chacha_state` 常驻、尾 `chacha_zeroize_state`（`:266/:285`），密钥不出栈；未对齐 bio 直接 `-EIO`（`:276-278`）不静默处理。

### 5.3 压缩/非压缩双路 + 错误不掩盖（`read.c:999-1061`）

- 签名：同 5.1 函数体内两分支。
- 参数：压缩路先整 bio 解密再 `bch2_bio_uncompress`（`:1007-1009`）；非压缩路 `nonce_add(offset<<9)` 跳步 + `bio_advance`（`:1014-1015`）只解所需子区。
- 返回：解压错在非 `no_data_io` 下直接 `return ret`（`:1010-1011`），但最终 `!csum_good` 仍以校验错覆盖返回（`:1060-1061`）。
- 片段（`:1004-1011`，8 行）：
```c
if (crc_is_compressed(crc)) {
    BUG_ON(!rbio->bounce);
    try(bch2_rbio_decrypt(c, rbio, crc, nonce));
    ret = bch2_bio_uncompress(c, src, dst, dst_iter, crc);
    if (ret && !c->opts.no_data_io)
        return ret;
```
- 权衡：压缩 extent 强制 bounce（`:1005`）——解压输出与源不可同页；校验错优先级高于解压错（`:1060` 后置检查），损坏密文不被“解压失败”洗成另一类错，重试链不断。

### 5.4 写侧“先解后验” `bch2_write_op_decode`（`write.c:1683`）

- 签名：`static int bch2_write_op_decode(struct bch_write_op *op, struct bio *bio)`。
- 参数：`crc=op->crc`；要求 `bi_size==compressed<<9`（`:1692`）、输出上限 `encoded_extent_max`（`:1694`）。
- 返回：0 或 `decompress_exceeded_max_encoded_extent/data_write_csum`；解压类错调用方转“原样直写”（`:1824-1844` 注释+分支）。
- 调用链：`bch2_write_prep_encoded_data`（`:1744` 内 `:1823`）→ 本函数 → `bch2_encrypt`（`:1716` 私有拷贝上解密）→ `bch2_buf_uncompress`（`:1719`）。
- 片段（`write.c:1710-1717`，8 行）：
```c
bool encrypted = bch2_csum_type_is_encryption(crc->csum_type);
struct bbuf src_buf __cleanup(bch2_bbuf_exit) = encrypted
    ? bch2_bio_bounce(c, bio, bio->bi_iter, READ)
    : bch2_bio_map_or_bounce(c, bio, READ);
if (encrypted)
    try(bch2_encrypt(c, crc->csum_type, extent_nonce(op->version, *crc),
             src_buf.b, crc->compressed_size << 9));
```
- 权衡：加密数据先私有拷贝再解密（注释 `:1703-1709`），`@bio` 在确认有明文可回填前零触碰；解不开的 extent 永不失败写、原密文直写保数据（`:1828-1832`），“写保住”优先于“写优化”。

**可学**：读先验后解、压缩错不盖校验错、用户映射先疑内存后疑盘。

---

## 六、nonce 步进与域分离

### 6.1 `nonce_add`（`checksum.h:188`）

- 签名：`static inline struct nonce nonce_add(struct nonce nonce, unsigned offset)`
- 参数：`offset` 字节数，必须 `CHACHA_BLOCK_SIZE` 对齐（`:190` `EBUG_ON`）；内部 `le32_add_cpu(&nonce.d[0], offset/64)`（`:192`，ChaCha 块 64B）。
- 返回：步进后 nonce（值语义）。
- 调用链：`extent_nonce` 尾（`:219`）、`rechecksum` 逐 split（`checksum.c:351`）、读子区（`read.c:1014`）、btree 跳段（`btree/read.h:86`）。
- 片段（`:187-194`，8 行）：
```c
static inline struct nonce nonce_add(struct nonce nonce, unsigned offset)
{
    EBUG_ON(offset & (CHACHA_BLOCK_SIZE - 1));
    le32_add_cpu(&nonce.d[0], offset / CHACHA_BLOCK_SIZE);
    return nonce;
}
```
- 权衡：计数器只加 `d[0]`、高位域不动，步进永不串域；调用方一律 `<<9` 扇区转字节（`checksum.c:351`），单位统一在调用点。

### 6.2 `extent_nonce`（`checksum.h:204`）

- 签名：`static inline struct nonce extent_nonce(struct bversion version, struct bch_extent_crc_unpacked crc)`
- 参数：`version.{lo,hi}`；`crc.{nonce,compression_type,uncompressed_size}`。
- 返回：`d[0]=size<<22, d[1..2]=version.lo, d[3]=version.hi|type<<24 ^ BCH_NONCE_EXTENT`（`:211-217`），再 `nonce_add(nonce, crc.nonce<<9)`（`:219`）。
- 调用链：所有数据加解密/校验 nonce 源头（`checksum.c:322/360`、`read.c:964`、`write.c:1716/1789/1811/1866/2051`）。
- 片段（`:210-219`，10 行）：
```c
struct nonce nonce = (struct nonce) {{
    [0] = cpu_to_le32(size << 22),
    [1] = cpu_to_le32(version.lo),
    [2] = cpu_to_le32(version.lo >> 32),
    [3] = cpu_to_le32(version.hi|
              (compression_type << 24))^BCH_NONCE_EXTENT,
}};
return nonce_add(nonce, crc.nonce << 9);
```
- 权衡：版本号+压缩类型+尺寸三维绑定，覆写/重压缩必换 nonce；是否压缩改变 `size` 取值（`:210` 压缩才带尺寸），密文与明文长度域分离。

### 6.3 `bch2_poly1305_init`（`checksum.c:121`）+ `BCH_NONCE_POLY`（`checksum.h:32`）

- 签名：`static void bch2_poly1305_init(struct poly1305_desc_ctx *desc, struct bch_fs *c, struct nonce nonce)`
- 参数：`nonce.d[3] ^= BCH_NONCE_POLY`（`checksum.c:126`，`1<<31`）；再 `bch2_chacha20(key, nonce, zero_key)` 派生一次性 poly key（`:128`）。
- 调用链：`bch2_checksum` poly 分支（`:158`）、`__bch2_checksum_bio` poly 分支（`:223`）唯一入口。
- 片段（`:121-130`，10 行）：
```c
static void bch2_poly1305_init(struct poly1305_desc_ctx *desc,
                   struct bch_fs *c, struct nonce nonce)
{
    u8 key[POLY1305_KEY_SIZE] = { 0 };
    nonce.d[3] ^= BCH_NONCE_POLY;
    bch2_chacha20(&c->chacha20_key, nonce, key, sizeof(key));
    poly1305_init(desc, key);
}
```
- 权衡：加密流与 MAC 密钥域分离一位异或，同一 key+nonce 永不复用 Chaos 块 0；poly key 不存储、每次现派，泄 MAC 不泄流密钥。

### 6.4 `bch2_chacha20_init` / `bch2_chacha20`（`checksum.c:96/111`）

- 签名：`static void bch2_chacha20_init(struct chacha_state *state, const struct bch_key *key, struct nonce nonce)`；`void bch2_chacha20(const struct bch_key *key, struct nonce nonce, void *data, size_t len)`。
- 参数：`key_words` 栈拷贝 + `le32_to_cpu_array`（`:102-103`），用后 `memzero_explicit`（`:108`）；`BUILD_BUG_ON` 双检 `key==32B`、`nonce==IV`（`:101/105`）。
- 调用链：数据加解密（`:180`）、poly 派生（`:128`）、sb key 解封（`:558`）、用户态 `bch2_passphrase_check`（`c_src/crypto.c:107`）共用。
- 片段（`:111-119`，9 行）：
```c
void bch2_chacha20(const struct bch_key *key, struct nonce nonce,
           void *data, size_t len)
{
    struct chacha_state state;
    bch2_chacha20_init(&state, key, nonce);
    chacha20_crypt(&state, data, data, len);
    chacha_zeroize_state(&state);
}
```
- 权衡：en/decrypt 同函数（流密码自反）；state 与 key_words 双清零，栈残留即漏洞按漏洞治。

### 6.5 `__bch2_sb_key_nonce` / `bch2_sb_key_nonce`（`checksum.h:227/239`）

- 签名：`static inline struct nonce __bch2_sb_key_nonce(struct bch_sb *sb)`；`static inline struct nonce bch2_sb_key_nonce(struct bch_fs *c)`。
- 参数：超块魔数 `__bch2_sb_magic/bch2_sb_magic` 拆两 `__le32` 放 `d[2..3]`，`d[0..1]=0`（`:231-236`）。
- 调用链：`bch2_decrypt_sb_key`（`checksum.c:558`）、用户态 `bch2_passphrase_check`/`bch_crypt_update_passphrase`（`c_src/crypto.c:107/196`）。
- 片段（`:227-237`，10 行内取 9 行）：
```c
static inline struct nonce __bch2_sb_key_nonce(struct bch_sb *sb)
{
    __le64 magic = __bch2_sb_magic(sb);
    return (struct nonce) {{
        [0] = 0,
        [1] = 0,
        [2] = ((__le32 *) &magic)[0],
        [3] = ((__le32 *) &magic)[1],
    }};
}
```
- 权衡：sb 密钥 nonce 与数据 `BCH_NONCE_EXTENT/BTREE/JOURNAL/PRIO`（`:28-31`）天然正交，魔数绑定防跨 fs 密钥复用。

**可学**：nonce 步进是生命线（每扇区必进）；域分离一位异或防跨协议；sb/数据/btree/journal 四域常量正交。

---

## 七、密钥直交与清零

### 7.1 `__bch2_request_key` 双实现（`checksum.c:439` 内核 / `:464` 用户态）+ `bch2_request_key`（`:494`）

- 签名：`static int __bch2_request_key(char *key_description, struct bch_key *key)`；`int bch2_request_key(struct bch_sb *sb, struct bch_key *key)`。
- 参数：描述串 `bcachefs:<user_uuid>`（`:499-500`）；内核走 `request_key(user)` + `datalen==32` 硬检（`:447-454`），用户态依次试 session→user→user_session 三 keyring（`:467-480`）。
- 返回：0 或 `PTR_ERR/-errno/-EINVAL`；用户态失败回落读口令 `bch2_passphrase_check`（`:505-512`）。
- 片段（`:439-445` + `:499-502`，共 9 行分两段）：
```c
struct key *keyring_key = request_key(&key_type_user, key_description, NULL);
if (IS_ERR(keyring_key))
    return PTR_ERR(keyring_key);
```
```c
prt_printf(&key_description, "bcachefs:");
pr_uuid(&key_description, sb->user_uuid.b);
ret = __bch2_request_key(key_description.buf, key);
```
- 权衡：描述串绑定 `user_uuid`，多 fs 共机不串 key；长度非 32 即 `-EINVAL` 不截断不补零。

### 7.2 `bch2_decrypt_sb_key`（`checksum.c:539`）+ `bch2_fs_encryption_init/exit`（`:671/666`）

- 签名：`int bch2_decrypt_sb_key(struct bch_fs *c, struct bch_sb_field_crypt *crypt, struct bch_key *key)`；`int bch2_fs_encryption_init(struct bch_fs *c)`；`void bch2_fs_encryption_exit(struct bch_fs *c)`。
- 参数：`crypt->key` 为被口令 key 包裹的 sb 主 key；`bch2_key_is_encrypted` 以 `magic != BCH_KEY_MAGIC` 为哨兵（`checksum.h:222`）。
- 返回：错口令即 `incorrect encryption key` + `-EINVAL`（`:561-563`）；双出口统一 `memzero_explicit(sb_key+user_key)`（`:568-569`）。
- 调用链：`bch2_fs_encryption_init`（`:677`）→ `bch2_decrypt_sb_key` → `bch2_request_key` + `bch2_chacha20(user_key, sb_nonce, sb_key)`（`:558`）；退出 `bch2_fs_encryption_exit` 清 `chacha20_key`（`:668`）。
- 片段（`:548-558`，取 8 行）：
```c
/* is key encrypted? */
if (!bch2_key_is_encrypted(&sb_key))
    goto out;
ret = bch2_request_key(c->disk_sb.sb, &user_key);
if (ret) {
    bch_err(c, "error requesting encryption key: %s", bch2_err_str(ret));
    goto err;
}
/* decrypt real key: */
bch2_chacha20(&user_key, bch2_sb_key_nonce(c), &sb_key, sizeof(sb_key));
```
- 权衡：未加密直接 `goto out` 明文装载（`:548-549`）；解封后二次验哨兵（`:560`），错口令不残留、不继续；`exit` 单行清零主 key 常驻内存最小化。

### 7.3 `derive_passphrase`（`c_src/crypto.c:58`）

- 签名：`struct bch_key derive_passphrase(struct bch_sb_field_crypt *crypt, const char *passphrase)`
- 参数：盐固定 `"bcache"`（`:61`，含 NUL 共 7B）；`N/R/P` 取 `1<<BCH_KDF_*`（`:70-72`）；未知 KDF 直接 `die`（`:77-78`）。
- 返回：32B `struct bch_key`（值返回）。
- 调用链：`bch2_passphrase_check`（`:105`）、`bch_crypt_update_passphrase`（`:194`）→ 本函数 → `crypto_pwhash_scryptsalsa208sha256_ll`。
- 片段（`:65-75`，9 行取关键 8 行）：
```c
case BCH_KDF_SCRYPT:
    ret = crypto_pwhash_scryptsalsa208sha256_ll(
        (void *) passphrase, strlen(passphrase),
        salt, sizeof(salt),
        1ULL << BCH_KDF_SCRYPT_N(crypt),
        1ULL << BCH_KDF_SCRYPT_R(crypt),
        1ULL << BCH_KDF_SCRYPT_P(crypt),
        (void *) &key, sizeof(key));
```
- 权衡：默认 `N=14/R=3/P=4`（即 16384/8/16，`:189-191`），内存 hardness 优先；类型可扩展但未知即 `die` 不降级。

### 7.4 `bch2_passphrase_check`（`c_src/crypto.c:92`）

- 签名：`bool bch2_passphrase_check(struct bch_sb *sb, const char *passphrase, struct bch_key *passphrase_key, struct bch_encrypted_key *sb_key)`
- 参数：`sb_key` 先拷超块 wrapped key（`:100`）；无 crypt 段 / 未加密分别 `die`（`:97-103`）。
- 返回：`true` 口令错（仍加密）、`false` 口令对（已解开，由调用方 `bch2_add_key:134-136` 取反判断）。
- 片段（`:105-112`，8 行）：
```c
*passphrase_key = derive_passphrase(crypt, passphrase);
bch2_chacha20(passphrase_key, __bch2_sb_key_nonce(sb), sb_key, sizeof(*sb_key));
if (bch2_key_is_encrypted(sb_key))
    return true;
return false;
```
- 权衡：对错哨兵验（magic 比对），永不存口令哈希；口令 key 经 `bch2_chacha20` 原地解包裹，一次流密码即验即解。

### 7.5 `bch2_add_key`（`c_src/crypto.c:115`）+ `read_passphrase`（`:22`）

- 签名：`bool bch2_add_key(struct bch_sb *sb, const char *type, const char *keyring_str, const char *passphrase)`；`char *read_passphrase(const char *prompt)`。
- 参数：`keyring_str` 仅 `session/user/user_session` 三取值（`:124-131`）；`description=bcachefs:<uuid>`（`:141`）；`add_key` 失败 `die`（`:146-147`）。
- 返回：同 7.4 反直觉约定（`true`=口令错）。
- 片段（`:149-154`，6 行）：
```c
memzero_explicit(description, strlen(description));
free(description);
memzero_explicit(&passphrase_key, sizeof(passphrase_key));
memzero_explicit(&sb_key, sizeof(sb_key));
```
- 权衡：描述串、口令 key、sb_key 三清零；`read_passphrase` 关 `ECHO`（`:38`）+ `TCSAFLUSH`（`:40`）防回显与排队输入，`isatty` 否才走管道（`:46-48`）。

### 7.6 `bch_sb_crypt_init` / `bch_crypt_update_passphrase`（`c_src/crypto.c:157/170`）

- 签名：`void bch_sb_crypt_init(struct bch_sb *sb, struct bch_sb_field_crypt *crypt, const char *passphrase)`；`void bch_crypt_update_passphrase(struct bch_sb *sb, struct bch_sb_field_crypt *crypt, struct bch_key *key, const char *new_passphrase)`。
- 参数：新建随机主 key（`:162` `get_random_bytes`）+ `magic=BCH_KEY_MAGIC`（`:164`）；`new_passphrase==NULL` 即去口令明文存（`:181-184`）；已有加密参数复用 KDF（`:187-192`）。
- 返回：void；落盘前 `assert(仍加密)`（`:201`）。
- 片段（`:194-200`，7 行）：
```c
struct bch_key passphrase_key = derive_passphrase(crypt, new_passphrase);
bch2_chacha20(&passphrase_key, __bch2_sb_key_nonce(sb), &new_key, sizeof(new_key));
memzero_explicit(&passphrase_key, sizeof(passphrase_key));
crypt->key = new_key;
assert(bch2_key_is_encrypted(&crypt->key));
```
- 权衡：换口令不换主 key（只重包裹），历史数据零重写；口令 key 立清，主 key 永不明文经 keyring。

**可学**：密钥少中转（口令→keyring→sb解封三跳）；残留即漏洞（双出口/三清零/栈清零）；哨兵验口令（magic 比对）。

---

## 八、设计启示

1. 顺序固定：压缩→校验→加密写，校验→解密→解压读（`compress.c:592`、`checksum.c:170/246`、`read.c:955`、`write.c:1683`）。
2. 启发选型：单块跳过（`compress.c:485`）、折半收敛（`:541-545`）、严格更小（`:554`）。
3. 重试收敛：`attempt_compress` 三后端归一化为 `>0/=0/<0` 协议。
4. 强度分级：数据可协商、元数据恒强、加密覆盖宽 MAC（`checksum.h:132-163`）。
5. 优先级不掩盖：校验错压解压错（`read.c:1060`），损坏不洗白（`checksum.c:362`、`write.c:1783-1795`）。
6. 步进生命线：`nonce_add`（`checksum.h:188`）+ `extent_nonce`（`:204`）+ poly 异或（`checksum.c:126`）。
7. 少中转：`bch2_request_key`（`checksum.c:494`）直交 keyring，描述串绑 uuid。
8. 类型清零：`chacha_zeroize_state`、`memzero_explicit(key_words/sb_key/user_key/passphrase_key)` 分层清零。

---

## 复核途径

- `grep -n "attempt_compress\|bch2_compress\|bch2_bio_compress\|bch2_buf_uncompress\|bch2_bio_uncompress\|bch2_decompress_err" fs/data/compress.c` 看压缩重试验证（对应 `:372/:475/:592/:244/:346/:338`）。
- `grep -n "bch2_checksum_bio\|__bch2_checksum_bio\|bch2_rechecksum_bio\|bch2_checksum_merge" fs/data/checksum.c` 看校验窄化（对应 `:246/:184/:313/:289`）。
- `grep -n "nonce_add\|BCH_NONCE_POLY\|extent_nonce\|bch2_sb_key_nonce\|bch2_chacha20\|bch2_encrypt" fs/data/checksum.h fs/data/checksum.c` 看步进分离（对应 `checksum.h:188/:32/:204/:239`、`checksum.c:121/111/170/254`）。
- `grep -n "bch2_request_key\|bch2_decrypt_sb_key\|bch2_fs_encryption_init\|bch2_fs_encryption_exit" fs/data/checksum.c` 看密钥装载清零（对应 `:494/:539/:671/:666`）。
- `grep -n "derive_passphrase\|bch2_passphrase_check\|bch2_add_key\|bch_crypt_update_passphrase\|read_passphrase" c_src/crypto.c` 看 KDF 口令链（对应 `:58/:92/:115/:170/:22`）。
- `grep -n "__bch2_read_endio_work\|bch2_rbio_decrypt\|bch2_write_op_decode" fs/data/read.c fs/data/write.c` 看先验后解（对应 `read.c:955/946`、`write.c:1683`）。
