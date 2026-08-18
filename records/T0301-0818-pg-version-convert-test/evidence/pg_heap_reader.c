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
    char *strbuf;
    size_t *status_off, *status_len;
    size_t *payload_off, *payload_len;
    size_t strbuf_cap;
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
 * 自解码 heap 元组字段（T0301，替代 PG18 编译期 heap_deform_tuple）：
 *   数据区从 t_hoff 起（有无 null bitmap 均已被 t_hoff 计入，无需额外对齐）；
 *   null bitmap 仅在 infomask 置 HEAP_HASNULL 时存在（否则全列非空，bitmap
 *   为 0 字节）；null 列不占数据区空间不推进；非 null 列按 attalign 对齐后
 *   按类型读取（int8/int4/varlena/bool）。
 */
static void decode_tuple(const HeapTupleHeader tup, PgCols *cols,
                         size_t row, uint64_t *skipped_toast, size_t *strpos)
{
    const uint8_t *b = (const uint8_t *) tup;
    uint8 t_hoff = b[PG_HEAP_T_HOFF_OFF];
    uint16 infomask = *(const uint16 *)(b + PG_HEAP_INFOMASK_OFF);
    int hasnull = (infomask & HEAP_HASNULL) != 0;
    const uint8_t *bits = b + PG_HEAP_HEADER_SIZE; /* 仅 hasnull 时有效 */
    const uint8_t *dp = b + t_hoff;           /* 数据区起点 */
    size_t dpos = 0;
    int a;

    for (a = 0; a < 7; a++)
    {
        int nullbit = hasnull ? ((bits[a >> 3] >> (a & 7)) & 1) : 0;
        if (nullbit)
            continue; /* null 列不占数据区空间 */
        {
            int align = PgColAttr[a].align;
            /* 对齐（照抄 heap_deform_tuple 的 att_align_pointer）：
             * 非 varlena 列数学对齐；varlena 列先探测当前字节——
             *   非 0（1B 头 varlena 或已对齐 4B 头）→ 不强制对齐；
             *   =0（pad 字节或 4B 头首字节）→ 按 attalignby 对齐。 */
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
                uint32 vsz = varlena_size_any(fp);
                if (varlena_extended(fp))
                {
                    if (a == 2)
                    {
                        cols->amount_lo[row] = 0;
                        cols->amount_hi[row] = 0;
                    }
                    else
                    {
                        size_t *offp = (a == 4) ? &cols->status_off[row] : &cols->payload_off[row];
                        size_t *lenp = (a == 4) ? &cols->status_len[row] : &cols->payload_len[row];
                        *offp = *strpos; *lenp = 0;
                    }
                    if (skipped_toast) (*skipped_toast)++;
                }
                else if (a == 2) /* amount numeric */
                {
                    __int128 v128 = decode_numeric(varlena_data(fp), varlena_size_exhdr(fp), 2);
                    cols->amount_lo[row] = (int64_t) ((uint64) v128);
                    cols->amount_hi[row] = (int64_t) ((__int128) v128 >> 64);
                }
                else /* status(4) / payload(5) text */
                {
                    size_t *offp = (a == 4) ? &cols->status_off[row] : &cols->payload_off[row];
                    size_t *lenp = (a == 4) ? &cols->status_len[row] : &cols->payload_len[row];
                    uint32 vlen = varlena_size_exhdr(fp);
                    *offp = *strpos; *lenp = vlen;
                    if (*strpos + vlen <= cols->strbuf_cap)
                    {
                        memcpy(cols->strbuf + *strpos, varlena_data(fp), vlen);
                        *strpos += vlen;
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

size_t pg_parse_heap_range(const char *path, const char *pgxact_dir,
                           PgCols *cols, size_t max_rows, ParseCursor *cur,
                           uint64_t *seen_total, uint64_t *skipped_invisible,
                           uint64_t *skipped_dead, uint64_t *skipped_toast)
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

            decode_tuple(tup, cols, row, skipped_toast, &strpos);
            row++;
        }
    }
done:
    munmap(file, file_len);
    return row;
}