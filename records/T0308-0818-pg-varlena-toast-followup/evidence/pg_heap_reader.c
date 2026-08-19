/*
 * pg_heap_reader.c — T0250 重写版 PG heap 物理直读（含精确 CLOG 可见性）。
 *
 * 相对 T0163（启发式 XMAX_INVALID && !UPDATED）的核心升级：
 *   通过读取 pg_xact/CLOG 判断 t_xmin/t_xmax 的提交状态，等效 PG MVCC
 *   快照语义，覆盖正常关闭后残留的 abort 事务元组与死元组场景。
 *
 * T0301 版本适配升级：本实现自解码 heap 字段（替代 PG18 编译期
 * heap_deform_tuple，避免编译期布局错位）。
 * 版本差异（T0301 实测 pg9.6/pg11/pg18.4 三容器 pageinspect + 原始字节对拍）：
 *   - heap 元组头字节偏移各版本一致（xmin/xmax/cid@0/4/8，ctid@12，
 *     infomask2@18，infomask@20，t_hoff@22，头 24B）。早前基于"PG12 移除
 *     t_xvac 使头缩短 4B"的推论有误：t_xvac 位于 t_field3 union（与 t_cid
 *     共用 4B），不改变头布局。
 *   - varlena 编码各版本一致（packed：1B 头最低位=1 长度=头>>1；4B 头
 *     低 2 位=00/10，长度=(va_header>>2)&0x3FFFFFFF）。早前"PG13- 老格式
 *     （最高位标志）"推论无实例支撑，PG9.6/11 数据（payload 0xA3=81B、
 *     4B 头 0x330>>2=204B）均按 packed 解析。
 *   - CLOG 仅目录名随版本迁移（pg9.x 及更早 pg_clog/，PG10+ pg_xact/），
 *     SLRU 段与 2-bit xid 状态编码一致；目录由调用方传入。
 * 页面解析用 storage/bufpage.h（页格式各版本一致）；numeric 解码为 Decimal128。
 */
#include "pg_versions.h"

#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#include "postgres.h"
#include "access/htup_details.h"
#include "access/tupdesc.h"
#include "storage/bufpage.h"
#include "utils/memutils.h"

#include "pg_clog_reader_pg10.h"

/* postgres.h 经 port.h 将 qsort 宏替换为 pg_qsort（PG 私有符号），本项目
 * 未链接 src/port/qsort.c，恢复标准库 qsort。 */
#undef qsort

/* c.h 把 fprintf 替换为 pg_fprintf，这里解除 */
#ifdef fprintf
#undef fprintf
#endif

#define NBASE 10000

/* ---------------- numeric 解码（同 T0163 结构，保留） ---------------- */
typedef int16 NumericDigit;
struct NumericShort { uint16 n_header; NumericDigit n_data[]; };
struct NumericLong { uint16 n_sign_dscale; int16 n_weight; NumericDigit n_data[]; };
union NumericChoice { uint16 n_header; struct NumericLong n_long; struct NumericShort n_short; };

#define NUMERIC_SIGN_MASK 0xC000
#define NUMERIC_NEG 0x4000
#define NUMERIC_SHORT 0x8000
#define NUMERIC_SPECIAL 0xC000
#define NUMERIC_FLAGBITS(n) ((n)->n_header & NUMERIC_SIGN_MASK)
#define NUMERIC_IS_SHORT(n) (NUMERIC_FLAGBITS(n) == NUMERIC_SHORT)
#define NUMERIC_IS_SPECIAL(n) (NUMERIC_FLAGBITS(n) == NUMERIC_SPECIAL)
#define NUMERIC_HEADER_IS_SHORT(n) (((n)->n_header & 0x8000) != 0)
#define NUMERIC_SHORT_SIGN_MASK 0x2000
#define NUMERIC_SHORT_DSCALE_MASK 0x1F80
#define NUMERIC_SHORT_DSCALE_SHIFT 7
#define NUMERIC_SHORT_WEIGHT_SIGN_MASK 0x0040
#define NUMERIC_SHORT_WEIGHT_MASK 0x003F
#define NUMERIC_DSCALE_MASK 0x3FFF
#define NUMERIC_SIGN(n) \
    (NUMERIC_IS_SHORT(n) ? \
        (((n)->n_short.n_header & NUMERIC_SHORT_SIGN_MASK) ? NUMERIC_NEG : NUMERIC_POS) : \
        (NUMERIC_IS_SPECIAL(n) ? NUMERIC_FLAGBITS(n) : NUMERIC_FLAGBITS(n)))
#define NUMERIC_DSCALE(n) (NUMERIC_HEADER_IS_SHORT((n)) ? \
    ((n)->n_short.n_header & NUMERIC_SHORT_DSCALE_MASK) >> NUMERIC_SHORT_DSCALE_SHIFT \
    : ((n)->n_long.n_sign_dscale & NUMERIC_DSCALE_MASK))
#define NUMERIC_WEIGHT(n) (NUMERIC_HEADER_IS_SHORT((n)) ? \
    (((n)->n_short.n_header & NUMERIC_SHORT_WEIGHT_SIGN_MASK ? ~NUMERIC_SHORT_WEIGHT_MASK : 0) \
     | ((n)->n_short.n_header & NUMERIC_SHORT_WEIGHT_MASK)) \
    : ((n)->n_long.n_weight))

static __int128 decode_numeric(const char *data, size_t len, int target_scale)
{
    __int128 value = 0;
    int ndigits = 0, weight = 0, dscale = 0, sign = 1;
    int i;
    int exp10[128];
    int min_exp = INT_MAX;
    uint16 n_header;
    const char *digits_base = NULL;

    if (len < sizeof(uint16))
        return 0;
    memcpy(&n_header, data, sizeof(uint16));

    /* 所有字段用 memcpy 读取：short varlena 数据区可能非对齐（UBSan 对齐要求） */
    if ((n_header & NUMERIC_SIGN_MASK) == NUMERIC_SPECIAL)
        return 0; /* NaN */
    if ((n_header & NUMERIC_SIGN_MASK) == NUMERIC_SHORT)
    {
        if (n_header & NUMERIC_SHORT_SIGN_MASK)
            sign = -1;
        dscale = (n_header & NUMERIC_SHORT_DSCALE_MASK) >> NUMERIC_SHORT_DSCALE_SHIFT;
        weight = (n_header & NUMERIC_SHORT_WEIGHT_SIGN_MASK)
            ? (~NUMERIC_SHORT_WEIGHT_MASK) | (n_header & NUMERIC_SHORT_WEIGHT_MASK)
            : (n_header & NUMERIC_SHORT_WEIGHT_MASK);
        ndigits = (int) ((len - sizeof(uint16)) / sizeof(NumericDigit));
        digits_base = data + sizeof(uint16);
    }
    else /* long */
    {
        uint16 sd;
        if (len < 4)
            return 0;
        memcpy(&sd, data, sizeof(uint16));
        memcpy(&weight, data + sizeof(uint16), sizeof(uint16));
        sign = (sd & NUMERIC_SIGN_MASK) == NUMERIC_NEG ? -1 : 1;
        dscale = sd & NUMERIC_DSCALE_MASK;
        ndigits = (int) ((len - 4) / sizeof(NumericDigit));
        digits_base = data + 4;
    }
    (void) dscale;

    if (ndigits <= 0)
        return 0;

    for (i = 0; i < ndigits && i < 128; i++)
    {
        int e = 4 * (weight - i) + target_scale;
        exp10[i] = e;
        if (e < min_exp)
            min_exp = e;
    }
    for (i = 0; i < ndigits && i < 128; i++)
    {
        NumericDigit d;
        memcpy(&d, digits_base + i * (int) sizeof(NumericDigit), sizeof(NumericDigit));
        {
            __int128 v = d;
            int e = exp10[i] - min_exp;
            while (e-- > 0)
                v *= 10;
            value += v;
        }
    }
    if (min_exp < 0)
    {
        __int128 den = 1;
        int e = -min_exp;
        while (e-- > 0)
            den *= 10;
        value /= den;
    }
    else
    {
        int e = min_exp;
        while (e-- > 0)
            value *= 10;
    }
    if (sign < 0)
        value = -value;
    return value;
}

/* ---------------- heap 头布局（T0301 实测） ----------------
 * 各版本（PG9.6/11/18 实测）一致：xmin@0 xmax@4 cid@8 ctid@12 infomask2@18
 * infomask@20 t_hoff@22 头 24B；t_bits（null bitmap）紧随头部；数据区从
 * t_hoff 起（已含 bitmap 对齐）。布局常量在 pg_versions.h（PG_HEAP_*）。
 * 注：早前"PG12 移除 t_xvac 使头 28B→24B"推论有误——t_xvac 与 t_cid 同处
 * t_field3 union（4B），PG11 头仍 24B（pageinspect t_hoff=24 实测确认）。
 */

/* 字段解码类型（poc_orders 固定 7 列；对齐规则同 PG attalign） */
enum { ATTR_INT8 = 0, ATTR_INT4 = 1, ATTR_VARLENA = 2, ATTR_BOOL = 3 };
static const struct { int kind; int align; } PgColAttr[7] = {
    {ATTR_INT8, 8}, {ATTR_INT4, 4}, {ATTR_VARLENA, 4}, {ATTR_INT8, 8},
    {ATTR_VARLENA, 4}, {ATTR_VARLENA, 4}, {ATTR_BOOL, 1},
};

/* ---------------- 输出列缓冲 ---------------- */
typedef struct PgCols
{
    int64_t *ids;
    int32_t *customers;
    int64_t *created_at_us;
    int64_t *amount_lo;
    int64_t *amount_hi;
    uint8_t *actives;
    uint8_t *nulls;         /* 每行 1 字节：bit a=第 a 列 NULL */
    char *strbuf;
    size_t *status_off, *status_len;
    size_t *payload_off, *payload_len;
    size_t strbuf_cap;
    uint8_t *dscratch;      /* 解压临时缓冲（行内压缩/TOAST 外置） */
    size_t dscratch_cap;
} PgCols;

typedef struct { size_t page_idx; uint16 next_offnum; } ParseCursor;

/*
 * varlena 头解码（T0301 实测：PG9.6/11/18 编码一致，packed 格式，小端）：
 *   1B 头最低位=1（数据短格式），长度=头>>1（≤127B 含头）；
 *   4B 头低 2 位=00（未压缩）/10（压缩），长度=(va_header>>2)&0x3FFFFFFF；
 *   1B 头=0x01（external）为 TOAST 指针（poc_orders 均 <2KB 小字段不触发）。
 * 早前"PG13- 老格式（1B 头最高位=0 长度=头&0x7F；4B 头最高位=1）"推论
 * 无实例支撑：PG9.6/11 数据（1B 头 0xA3→81B、4B 头 0x00000330>>2→204B）
 * 均按 packed 解析正确。
 */
static uint32 varlena_size_any(const uint8_t *vp)
{
    uint8 h = vp[0];
    if (h & 0x01)
        return h >> 1;
    return ((*(const uint32 *) vp) >> 2) & 0x3FFFFFFF;
}

static uint32 varlena_size_exhdr(const uint8_t *vp)
{
    return varlena_size_any(vp) - ((vp[0] & 0x01) ? 1 : 4);
}

static const uint8_t *varlena_data(const uint8_t *vp)
{
    return (vp[0] & 0x01) ? vp + 1 : vp + 4;
}

static int varlena_extended(const uint8_t *vp)
{
    return VARATT_IS_EXTERNAL(vp) || VARATT_IS_COMPRESSED(vp);
}

/*
 * pglz 解压（移植自 PG18 src/common/pg_lzcompress.c；压缩流格式各版本
 * PG9.6/11/18 一致，T0308 实测）。
 *
 * 格式：控制字节每 8 位管 8 个块；位 0=字面量(复制 1B)、位 1=回引 tag
 * （T1 低 4 位=len-3，T1 高 4 位=off 高 4 位，T2=off 低 8 位；len==18 时
 * 后跟 1B 扩展长度）。off 范围 1..4095，len 范围 3..273。
 *
 * 返回解压字节数（=rawsize），失败返回 -1。
 */
static int32 pglz_decompress(const char *source, int32 slen, char *dest,
                             int32 rawsize)
{
    const unsigned char *sp = (const unsigned char *) source;
    const unsigned char *srcend = sp + slen;
    unsigned char *dp = (unsigned char *) dest;
    unsigned char *destend = dp + rawsize;

    while (sp < srcend && dp < destend)
    {
        unsigned char ctrl = *sp++;
        int ctrlc;
        for (ctrlc = 0; ctrlc < 8 && sp < srcend && dp < destend; ctrlc++)
        {
            if (ctrl & 1)
            {
                int32 len, off;
                if (sp + 2 > srcend)
                    return -1;
                len = (sp[0] & 0x0f) + 3;
                off = ((sp[0] & 0xf0) << 4) | sp[1];
                sp += 2;
                if (len == 18)
                {
                    if (sp >= srcend)
                        return -1;
                    len += *sp++;
                }
                if (off == 0 || off > (int32) (dp - (unsigned char *) dest))
                    return -1;
                len = (len < (int32) (destend - dp)) ? len : (int32) (destend - dp);
                while (off < len)
                {
                    memcpy(dp, dp - off, (size_t) off);
                    len -= off;
                    dp += off;
                    off += off;
                }
                memcpy(dp, dp - off, (size_t) len);
                dp += len;
            }
            else
                *dp++ = *sp++;
            ctrl >>= 1;
        }
    }
    if (dp != destend || sp != srcend)
        return -1;
    return (int32) (dp - (unsigned char *) dest);
}

/* ---------------- TOAST 外置值（T0308） ----------------
 * TOAST 表（pg_toast_<oid>）为普通 heap：3 列 (chunk_id int4, chunk_seq int4,
 * chunk_data bytea)。解码流程：external varlena 头解析出 chunk_id
 * (va_valueid) → 按 chunk_id 分组、chunk_seq 升序拼接 → 若 external 压缩
 * （extsize < rawsize-4）再 pglz 解压得原始值。
 *
 * external 头布局（T0308 实测 PG9.6/11/18 一致，无版本差异）：
 *   varattrib_1b_e: [0]=0x01 [1]=0x12(VARTAG_ONDISK=18)
 *   varatt_external: rawsize@2 int32, extinfo@6 uint32(低 30 位=extsize,
 *     高 2 位=压缩方法; pglz 时 bit30=1), valueid@10 uint32, toastrelid@14 uint32
 *   压缩判定: extsize < rawsize - VARHDRSZ(4)
 */
typedef struct PgToast
{
    uint32 *keys;       /* 排序去重后的 chunk_id */
    size_t *offs;       /* 该 chunk_id 的拼接数据起始（blob 内） */
    size_t *lens;       /* 该 chunk_id 的拼接数据长度 */
    uint8_t *blob;      /* 全部 chunk 数据拼接（已去 varlena 头） */
    size_t n;           /* 唯一 chunk_id 数 */
    size_t blob_len;
} PgToast;

/* TOAST 表扫描收集（chunk_data 指向 mmap 文件内，排序后复制进 blob） */
typedef struct ToastChunk
{
    uint32 id;
    uint32 seq;
    const uint8_t *d;
    uint32 len;
} ToastChunk;
typedef struct ToastChunkList
{
    ToastChunk *items;
    size_t n, cap;
} ToastChunkList;

static int toast_cmp(const void *a, const void *b)
{
    const ToastChunk *x = (const ToastChunk *) a, *y = (const ToastChunk *) b;
    if (x->id < y->id) return -1;
    if (x->id > y->id) return 1;
    if (x->seq < y->seq) return -1;
    if (x->seq > y->seq) return 1;
    return 0;
}

/*
 * TOAST external 值解码：由 external 头解析 chunk_id(va_valueid)，查 PgToast
 * 拼接结果；若 external 压缩（extsize < rawsize-4）则 pglz 解压。
 * 成功返回 0，*out=原始数据（不含 varlena 头）、*outlen=长度；失败返回 -1。
 */
static int toast_decode(const uint8_t *vp, const PgToast *toast,
                        uint8_t *scratch, size_t scratch_cap,
                        const uint8_t **out, uint32 *outlen)
{
    int32 rawsize;
    uint32 extinfo, valueid, extsize;
    const uint8_t *blob;
    size_t lo = 0, hi, n = toast ? toast->n : 0;

    if (!toast || n == 0 || vp[1] != 18) /* VARTAG_ONDISK */
        return -1;
    memcpy(&rawsize, vp + 2, 4);
    memcpy(&extinfo, vp + 6, 4);
    memcpy(&valueid, vp + 10, 4);
    extsize = extinfo & 0x3FFFFFFFu;

    /* 二分查 chunk_id */
    hi = n;
    while (lo < hi)
    {
        size_t mid = (lo + hi) / 2;
        if (toast->keys[mid] < valueid)
            lo = mid + 1;
        else
            hi = mid;
    }
    if (lo >= n || toast->keys[lo] != valueid)
        return -1;
    blob = toast->blob + toast->offs[lo];
    if (toast->lens[lo] != extsize)
        return -1;

    if (extsize < (uint32) (rawsize - 4)) /* external 压缩（pglz） */
    {
        uint32 pfx;
        if (rawsize <= 4 || (uint32) (rawsize - 4) > scratch_cap)
            return -1; /* 目标尺寸超解压缓冲：拒绝（防堆溢出） */
        if (extsize < 4)
            return -1;
        /* toast 压缩数据格式（pglz，PG9.6/11/18 实测一致）：
         *   4B 前缀 = rawsize 低 30 位（PG18 高 2 位=压缩方法，0=pglz/1=lz4；
         *   9.6/11 无方法位，恒 0）+ pglz 流。 */
        memcpy(&pfx, blob, 4);
        if ((pfx & 0x3FFFFFFFu) != (uint32) (rawsize - 4))
            return -1; /* 前缀 rawsize 与 external 头不一致 */
        if ((pfx >> 30) != 0)
            return -1; /* 仅支持 pglz（lz4 见 research-report 遗留边界） */
        {
            int32 n = pglz_decompress((const char *) (blob + 4), (int32) extsize - 4,
                                      (char *) scratch, rawsize - 4);
            if (n < 0 || (size_t) n > scratch_cap)
                return -1;
            *out = scratch;
            *outlen = (uint32) n;
        }
    }
    else
    {
        *out = blob;
        *outlen = extsize;
    }
    return 0;
}

/*
 * 自解码 heap 元组字段（T0301，替代 PG18 编译期 heap_deform_tuple）：
 *   数据区从 t_hoff 起（有无 null bitmap 均已被 t_hoff 计入，无需额外对齐）；
 *   null bitmap 仅在 infomask 置 HEAP_HASNULL 时存在（否则全列非空，bitmap
 *   为 0 字节）；null 列不占数据区空间不推进；非 null 列按 attalign 对齐后
 *   按类型读取（int8/int4/varlena/bool）。
 *
 *   varlena 文本列三态（T0308）：
 *     普通 1B/4B 头   直接读数据；
 *     4B 头压缩(行内) pglz 解压（va_tcinfo 低 30 位=原始数据大小不含头）；
 *     external(TOAST) 解析 external 头 → toast 表 chunk 拼接 → 按需解压。
 */
static void decode_tuple(const HeapTupleHeader tup, PgCols *cols,
                         size_t row, uint64_t *skipped_toast, size_t *strpos,
                         const PgToast *toast)
{
    const uint8_t *b = (const uint8_t *) tup;
    uint8 t_hoff = b[PG_HEAP_T_HOFF_OFF];
    uint16 infomask = *(const uint16 *)(b + PG_HEAP_INFOMASK_OFF);
    int hasnull;
    if (t_hoff < PG_HEAP_HEADER_SIZE || t_hoff > BLCKSZ)
        t_hoff = PG_HEAP_HEADER_SIZE; /* 头偏移越界：回退最小头防越页读 */
    hasnull = (infomask & HEAP_HASNULL) != 0;
    cols->nulls[row] = 0; /* 每行起点清零 nulls 位图 */
    const uint8_t *bits = b + PG_HEAP_HEADER_SIZE; /* 仅 hasnull 时有效 */
    const uint8_t *dp = b + t_hoff;           /* 数据区起点 */
    size_t dpos = 0;
    int a;

    for (a = 0; a < 7; a++)
    {
        int nullbit = hasnull ? ((bits[a >> 3] >> (a & 7)) & 1) : 1;
        if (!nullbit)
        {
            /* null 列（bit=0）：不占数据区空间不推进；显式置哨兵并登记
             * nulls 位图（避免下游读到未初始化值），PG 约定 bit=1=非空。 */
            cols->nulls[row] |= (uint8_t) (1u << a);
            switch (PgColAttr[a].kind)
            {
            case ATTR_INT8:
                if (a == 0)
                    cols->ids[row] = 0;
                else
                    cols->created_at_us[row] = 0;
                break;
            case ATTR_INT4:
                cols->customers[row] = 0;
                break;
            case ATTR_VARLENA:
                if (a == 2)
                {
                    cols->amount_lo[row] = 0;
                    cols->amount_hi[row] = 0;
                }
                else if (a == 4)
                    cols->status_len[row] = 0;
                else
                    cols->payload_len[row] = 0;
                break;
            case ATTR_BOOL:
                cols->actives[row] = 0;
                break;
            }
            continue;
        }
        {
            int align = PgColAttr[a].align;
            if (PgColAttr[a].kind == ATTR_VARLENA)
            {
                if (dp[dpos] == 0)
                    dpos = (dpos + align - 1) & ~(size_t) (align - 1);
            }
            else
            {
                dpos = (dpos + align - 1) & ~(size_t) (align - 1);
            }
            const uint8_t *fp = dp + dpos;
            switch (PgColAttr[a].kind)
            {
            case ATTR_INT8:
                if (a == 0)
                    cols->ids[row] = *(const int64_t *) fp;
                else
                {
                    int64 pg_us = *(const int64_t *) fp;
                    cols->created_at_us[row] = pg_us + ((int64) 946684800 * 1000000);
                }
                dpos += 8;
                break;
            case ATTR_INT4:
                cols->customers[row] = *(const int32_t *) fp;
                dpos += 4;
                break;
            case ATTR_VARLENA:
            {
                uint32 vsz;
                if (VARATT_IS_EXTERNAL(fp))
                    vsz = 2 + 16; /* varattrib_1b_e(2) + varatt_external(16) */
                else
                    vsz = varlena_size_any(fp);
                if (a == 2) /* amount numeric（数值小，不 TOAST） */
                {
                    __int128 v128 = decode_numeric(varlena_data(fp), varlena_size_exhdr(fp), 2);
                    cols->amount_lo[row] = (int64_t) ((uint64) v128);
                    cols->amount_hi[row] = (int64_t) ((__int128) v128 >> 64);
                }
                else /* status(4) / payload(5) text */
                {
                    size_t *offp = (a == 4) ? &cols->status_off[row] : &cols->payload_off[row];
                    size_t *lenp = (a == 4) ? &cols->status_len[row] : &cols->payload_len[row];
                    const uint8_t *data;
                    uint32 vlen = 0;
                    int ok = 1;
                    if (VARATT_IS_EXTERNAL(fp))
                    {
                        if (toast_decode(fp, toast, cols->dscratch, cols->dscratch_cap,
                                         &data, &vlen) != 0)
                            ok = 0;
                    }
                    else if (VARATT_IS_COMPRESSED(fp)) /* 4B 头压缩（行内） */
                    {
                        uint32 tcinfo, orig;
                        int32 n;
                        memcpy(&tcinfo, fp + 4, 4);
                        orig = tcinfo & 0x3FFFFFFFu;
                        if (orig > cols->dscratch_cap || (int32) vsz < 8)
                            ok = 0; /* 目标尺寸超解压缓冲 / 压缩流非法：拒绝 */
                        else
                        {
                            n = pglz_decompress((const char *) (fp + 8), (int32) vsz - 8,
                                                (char *) cols->dscratch, (int32) orig);
                            if (n < 0 || (size_t) n > cols->dscratch_cap)
                                ok = 0;
                            else
                            {
                                data = cols->dscratch;
                                vlen = (uint32) n;
                            }
                        }
                    }
                    else
                    {
                        data = varlena_data(fp);
                        vlen = varlena_size_exhdr(fp);
                    }
                    if (!ok)
                    {
                        *offp = *strpos;
                        *lenp = 0;
                        if (skipped_toast) (*skipped_toast)++;
                    }
                    else
                    {
                        *offp = *strpos;
                        *lenp = vlen;
                        if (*strpos + vlen <= cols->strbuf_cap)
                        {
                            memcpy(cols->strbuf + *strpos, data, vlen);
                            *strpos += vlen;
                        }
                        else
                            *lenp = 0;
                    }
                }
                dpos += vsz;
                break;
            }
            case ATTR_BOOL:
                cols->actives[row] = fp[0] ? 1 : 0;
                dpos += 1;
                break;
            }
        }
    }
}

/*
 * CLOG 可见性判断：PG MVCC 快照语义的物理解读。
 *
 * 无 hint bits（page 未被并发访问写 XMIN_COMMITTED 等）时完全依赖 CLOG；
 * 有 hint bits 时以其为准（与 PG 运行时一致）。
 *
 * 备注：版本差异（详见文件头注释）——heap 头字段字节偏移与 varlena 编码
 * 经 T0301 实测各版本（PG9.6/11/18）一致；仅 CLOG 目录名随版本迁移：
 * PG10+ pg_xact/（pg_clog_reader_pg10.c）、PG9.x 及更早 pg_clog/
 * （pg_clog_legacy_pg9.c），目录由调用方传入。
 *
 * 规则（等效 HeapTupleSatisfiesMVCC 的 commit 判断）：
 *   xmin 状态：
 *     - HEAP_XMIN_FROZEN（INVALID|COMMITTED 同置）→ 可见（VACUUM freeze）
 *     - HEAP_XMIN_INVALID 置位且 COMMITTED 未置位 → 不可见（aborted）
 *     - HEAP_XMIN_COMMITTED 置位 → 提交；否则查 CLOG
 *     - CLOG(xmin)==COMMITTED → 可见候选；==ABORTED/IN_PROGRESS → 不可见
 *   xmax（若有 i.e. !HEAP_XMAX_INVALID）：
 *     - HEAP_XMAX_COMMITTED 置位 或 CLOG(xmax)==COMMITTED → 本行被 delete/update 提交
 *       → 不可见
 *     - 否则 xmax 未提交/aborted → 仍可见
 *   HEAP_UPDATED 仅用于统计（本行是新版本）。
 */
int pg_tuple_visible(const HeapTupleHeader tup, const char *pgxact_dir)
{
    const uint8_t *b = (const uint8_t *) tup;
    uint16 infomask = *(const uint16 *)(b + PG_HEAP_INFOMASK_OFF);
    TransactionId xmin = *(const uint32 *)(b + 0); /* Field4 xmin，各版本一致 */
    TransactionId xmax = *(const uint32 *)(b + 4); /* Field4 xmax */

    /*
     * xmin 可见性。
     * 注意 HEAP_XMIN_FROZEN = HEAP_XMIN_COMMITTED | HEAP_XMIN_INVALID 同置
     * （VACUUM freeze 后 hint bit），frozen 元组恒可见；因此判定顺序必须是：
     * 先看 INVALID 时是否同时 COMMITTED（frozen → 可见），再区分纯 INVALID。
     * 若先判 INVALID，会把 frozen 元组误判为 aborted（T0250 100M 回归根因）。
     */
    if (infomask & HEAP_XMIN_INVALID)
    {
        if (!(infomask & HEAP_XMIN_COMMITTED))
            return 0;   /* 仅 INVALID → aborted/未提交，不可见 */
    }
    else if ((infomask & HEAP_XMIN_COMMITTED) == 0)
    {
        int s = pg_clog_xid_status(pgxact_dir, xmin);
        if (s == TRANSACTION_STATUS_ABORTED || s == TRANSACTION_STATUS_IN_PROGRESS)
            return 0;
        if (s == TRANSACTION_STATUS_SUB_COMMITTED)
            return 0;   /* 保守：subcommit 不在本快照 */
    }

    /* xmax：本通行 delete/update 且已提交 → 不可见 */
    if ((infomask & HEAP_XMAX_INVALID) == 0)
    {
        int deleted = 0;
        if (infomask & HEAP_XMAX_IS_MULTI)
            deleted = 1;    /* 多事务锁：保守不可见 */
        else if (infomask & HEAP_XMAX_COMMITTED)
            deleted = 1;
        else
        {
            int s = pg_clog_xid_status(pgxact_dir, xmax);
            if (s == TRANSACTION_STATUS_COMMITTED)
                deleted = 1;
        }
        if (deleted)
            return 0;
    }
    return 1;
}

/*
 * TOAST 表加载：读 pg_toast_<oid> heap，收集所有可见 (chunk_id, chunk_seq,
 * chunk_data)，按 chunk_id 分组、chunk_seq 升序拼接成 PgToast（内存内）。
 * chunk_data 为 bytea varlena，取数据区（去 varlena 头）。
 *
 * 返回 0 成功；失败（打开/解析错误）返回 -1。toast->blob 等由调用方 free。
 */
int pg_toast_load(const char *path, const char *pgxact_dir, PgToast *toast)
{
    struct stat st;
    int fd;
    uint8_t *file;
    size_t file_len, page_count;
    ToastChunkList list = {0};
    size_t page_idx;
    size_t i, j;
    int rc = -1;

    memset(toast, 0, sizeof(*toast));
    fd = open(path, O_RDONLY);
    if (fd < 0) { fprintf(stderr, "open toast failed: %s\n", path); return -1; }
    if (fstat(fd, &st) != 0 || st.st_size == 0) { close(fd); return -1; }
    file_len = (size_t) st.st_size;
    file = mmap(NULL, file_len, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd);
    if (file == MAP_FAILED) { fprintf(stderr, "mmap toast failed\n"); return -1; }

    page_count = file_len / BLCKSZ;
    for (page_idx = 0; page_idx < page_count; page_idx++)
    {
        Page page = (Page) (file + page_idx * BLCKSZ);
        OffsetNumber maxoff = PageGetMaxOffsetNumber(page);
        OffsetNumber offnum;
        for (offnum = 1; offnum <= maxoff; offnum++)
        {
            ItemId itemid = PageGetItemId(page, offnum);
            HeapTupleHeader tup;
            const uint8_t *b, *dp;
            uint8 t_hoff;
            uint16 infomask;
            int hasnull;
            uint32 cid, cseq, vlen;

            if (!ItemIdIsUsed(itemid) || ItemIdIsRedirected(itemid)) continue;
            if (ItemIdIsDead(itemid)) continue;
            tup = (HeapTupleHeader) PageGetItem(page, itemid);
            if (!pg_tuple_visible(tup, pgxact_dir)) continue;

            b = (const uint8_t *) tup;
            t_hoff = b[PG_HEAP_T_HOFF_OFF];
            infomask = *(const uint16 *)(b + PG_HEAP_INFOMASK_OFF);
            if (t_hoff < PG_HEAP_HEADER_SIZE || t_hoff > BLCKSZ)
                continue; /* 头偏移越界：跳过（防越页读） */
            hasnull = (infomask & HEAP_HASNULL) != 0;
            dp = b + t_hoff;
            if (!hasnull) /* chunk 三列 int4/int4/varlena，无 null */
            {
                if (list.n >= list.cap)
                {
                    size_t ncap = list.cap ? list.cap * 2 : 1024;
                    ToastChunk *ni = realloc(list.items, ncap * sizeof(ToastChunk));
                    if (!ni) goto done;
                    list.items = ni;
                    list.cap = ncap;
                }
                memcpy(&cid, dp, 4);
                memcpy(&cseq, dp + 4, 4);
                {
                    const uint8_t *cd = dp + 8;
                    uint32 clen_all;
                    if (cd[0] == 0)
                        cd = (const uint8_t *) (((uintptr_t) cd + 3) & ~(uintptr_t) 3);
                    /* 合法性防护：拒绝空/过短 varlena 头，防止 exhdr 下溢后
                     * memcpy 越界（mmap 文件可能损坏或异常）。 */
                    clen_all = varlena_size_any(cd);
                    if (clen_all == 0 || ((cd[0] & 0x01) == 0 && clen_all < 5))
                        continue; /* 非法 chunk_data：跳过 */
                    vlen = clen_all - ((cd[0] & 0x01) ? 1 : 4);
                    list.items[list.n].id = cid;
                    list.items[list.n].seq = cseq;
                    list.items[list.n].d = varlena_data(cd);
                    list.items[list.n].len = vlen;
                    list.n++;
                }
            }
        }
    }

    qsort(list.items, list.n, sizeof(ToastChunk), toast_cmp);

    /* 统计唯一 chunk_id 数与 blob 总长 */
    {
        size_t uniq = 0, blob_len = 0;
        for (i = 0; i < list.n;)
        {
            uniq++;
            while (i < list.n)
            {
                uint32 sz = list.items[i].len;
                blob_len += sz;
                i++;
                if (i < list.n && list.items[i].id != list.items[i - 1].id)
                    break;
            }
        }
        toast->n = uniq;
        toast->keys = malloc(uniq * sizeof(uint32));
        toast->offs = malloc(uniq * sizeof(size_t));
        toast->lens = malloc(uniq * sizeof(size_t));
        toast->blob = malloc(blob_len ? blob_len : 1);
        if (!toast->keys || !toast->offs || !toast->lens || !toast->blob)
            goto done;
    }
    j = 0;
    for (i = 0; i < list.n;)
    {
        toast->keys[j] = list.items[i].id;
        toast->offs[j] = toast->blob_len;
        {
            size_t acc = 0;
            while (i < list.n)
            {
                memcpy(toast->blob + toast->offs[j] + acc,
                       list.items[i].d, list.items[i].len);
                acc += list.items[i].len;
                i++;
                if (i < list.n && list.items[i].id != list.items[i - 1].id)
                    break;
            }
            toast->lens[j] = acc;
        }
        toast->blob_len += toast->lens[j];
        j++;
    }
    rc = 0;
done:
    free(list.items);
    munmap(file, file_len);
    if (rc != 0)
    {
        free(toast->keys);
        free(toast->offs);
        free(toast->lens);
        free(toast->blob);
        memset(toast, 0, sizeof(*toast));
    }
    return rc;
}

size_t pg_parse_heap_range(const char *path, const char *pgxact_dir,
                           PgCols *cols, size_t max_rows, ParseCursor *cur,
                           uint64_t *seen_total, uint64_t *skipped_invisible,
                           uint64_t *skipped_dead, uint64_t *skipped_toast,
                           const PgToast *toast)
{
    struct stat st;
    int fd;
    uint8_t *file;
    size_t file_len, page_count;
    size_t page_idx, row = 0, strpos = 0;

    fd = open(path, O_RDONLY);
    if (fd < 0) { fprintf(stderr, "open failed: %s\n", path); return 0; }
    if (fstat(fd, &st) != 0 || st.st_size == 0) { close(fd); return 0; }
    file_len = (size_t) st.st_size;
    file = mmap(NULL, file_len, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd);
    if (file == MAP_FAILED) { fprintf(stderr, "mmap failed\n"); return 0; }

    page_count = file_len / BLCKSZ;
    for (page_idx = cur->page_idx; page_idx < page_count; page_idx++)
    {
        Page page = (Page) (file + page_idx * BLCKSZ);
        OffsetNumber maxoff = PageGetMaxOffsetNumber(page);
        OffsetNumber offnum;
        for (offnum = ((cur->page_idx == page_idx) && cur->next_offnum)
                ? cur->next_offnum : 1;
             offnum <= maxoff; offnum++)
        {
            ItemId itemid = PageGetItemId(page, offnum);
            HeapTupleHeader tup;

            cur->page_idx = page_idx;
            cur->next_offnum = (uint16) (offnum + 1);

            if (!ItemIdIsUsed(itemid) || ItemIdIsRedirected(itemid)) continue;
            if (ItemIdIsDead(itemid))
            {
                if (skipped_dead) (*skipped_dead)++;
                continue;
            }

            tup = (HeapTupleHeader) PageGetItem(page, itemid);
            if (seen_total) (*seen_total)++;

            /* 精确 CLOG 可见性（heap 头布局各版本一致） */
            if (!pg_tuple_visible(tup, pgxact_dir))
            {
                if (skipped_invisible) (*skipped_invisible)++;
                continue;
            }

            if (row >= max_rows)
            {
                cur->next_offnum = offnum;
                goto done;
            }

            decode_tuple(tup, cols, row, skipped_toast, &strpos, toast);
            row++;
        }
    }
done:
    munmap(file, file_len);
    return row;
}