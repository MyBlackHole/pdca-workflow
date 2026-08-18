/*
 * pg_heap_reader.c — T0250 重写版 PG heap 物理直读（含精确 CLOG 可见性）。
 *
 * 相对 T0163（启发式 XMAX_INVALID && !UPDATED）的核心升级：
 *   通过读取 pg_xact/CLOG 判断 t_xmin/t_xmax 的提交状态，等效 PG MVCC
 *   快照语义，覆盖正常关闭后残留的 abort 事务元组与死元组场景。
 *
 * 复用官方 heap_deform_tuple（PG 18.4 源码）实现列布局/对齐/varlena 解码；
 * 页面解析用 storage/bufpage.h；numeric 解码为 Decimal128。
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

#include "pg_clog_reader.h"

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
    const union NumericChoice *num = (const union NumericChoice *) data;
    __int128 value = 0;
    int ndigits, weight, dscale;
    const NumericDigit *digits;
    int sign = 1;
    int i;
    int exp10[128];
    int min_exp = INT_MAX;

    if (len < sizeof(uint16))
        return 0;
    if (NUMERIC_IS_SPECIAL(num))
        return 0;
    if (NUMERIC_IS_SHORT(num))
    {
        uint16 header = num->n_short.n_header;
        if (header & NUMERIC_SHORT_SIGN_MASK)
            sign = -1;
        dscale = (header & NUMERIC_SHORT_DSCALE_MASK) >> NUMERIC_SHORT_DSCALE_SHIFT;
        if (header & NUMERIC_SHORT_WEIGHT_SIGN_MASK)
            weight = (~NUMERIC_SHORT_WEIGHT_MASK) | (header & NUMERIC_SHORT_WEIGHT_MASK);
        else
            weight = header & NUMERIC_SHORT_WEIGHT_MASK;
        digits = num->n_short.n_data;
        ndigits = (int) ((len - sizeof(uint16)) / sizeof(NumericDigit));
    }
    else
    {
        sign = (num->n_long.n_sign_dscale & NUMERIC_SIGN_MASK) == NUMERIC_NEG ? -1 : 1;
        dscale = num->n_long.n_sign_dscale & NUMERIC_DSCALE_MASK;
        weight = num->n_long.n_weight;
        digits = num->n_long.n_data;
        ndigits = (int) ((len - sizeof(struct NumericLong)) / sizeof(NumericDigit));
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
        __int128 d = digits[i];
        int e = exp10[i] - min_exp;
        while (e-- > 0)
            d *= 10;
        value += d;
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

/* ---------------- 表结构描述（7 列，同 T0163） ---------------- */
static TupleDesc make_tupdesc(void)
{
    static const struct { int16 attlen; bool attbyval; uint8 attalignby; } info[7] = {
        {8, true, ALIGNOF_DOUBLE},
        {4, true, ALIGNOF_INT},
        {-1, false, ALIGNOF_INT},
        {8, true, ALIGNOF_DOUBLE},
        {-1, false, ALIGNOF_INT},
        {-1, false, ALIGNOF_INT},
        {1, true, 1},
    };
    size_t sz = offsetof(TupleDescData, compact_attrs) + 7 * sizeof(CompactAttribute);
    TupleDescData *d = palloc(sz);
    int i;
    memset(d, 0, sz);
    d->natts = 7;
    for (i = 0; i < 7; i++)
    {
        d->compact_attrs[i].attcacheoff = -1;
        d->compact_attrs[i].attlen = info[i].attlen;
        d->compact_attrs[i].attbyval = info[i].attbyval;
        d->compact_attrs[i].attalignby = info[i].attalignby;
        d->compact_attrs[i].attisdropped = false;
        d->compact_attrs[i].atthasmissing = false;
    }
    return d;
}

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
 * CLOG 可见性判断：PG MVCC 快照语义的物理解读。
 *
 * 无 hint bits（page 未被并发访问写 XMIN_COMMITTED 等）时完全依赖 CLOG；
 * 有 hint bits 时以其为准（与 PG 运行时一致）。
 *
 * 备注：版本差异（详见 pg_versions.h 版本特性矩阵）——t_infomask 等 heap
 *  头字段通过编译期 PG 官方头（HeapTupleHeaderData）访问，字节偏移随版本
 *  变化（PG12+ 偏移 20，PG11 及更早 24，本工程编译依据 PG18.4）；禁止硬编码
 *  旧偏移，否则 frozen 行误判（AC-10 根因之一）。CLOG 目录亦随版本迁移：
 *  PG10+ pg_xact/（pg_clog_reader.c 已实现）、PG9.x 及更早 pg_clog/
 *  （pg_clog_legacy.c 未实现）。
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
    uint16 infomask = tup->t_infomask;
    TransactionId xmin = HeapTupleHeaderGetRawXmin(tup);
    TransactionId xmax = HeapTupleHeaderGetRawXmax(tup);

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
    static TupleDesc tdesc;
    Datum values[7];
    bool isnull[7];
    static bool inited = false;

    if (!inited)
    {
        MemoryContextInit();
        tdesc = make_tupdesc();
        inited = true;
    }

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
            HeapTupleData htup;
            int col;

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

            /* 精确 CLOG 可见性 */
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

            htup.t_data = tup;
            htup.t_len = ItemIdGetLength(itemid);
            htup.t_tableOid = InvalidOid;
            htup.t_self.ip_blkid.bi_hi = 0;
            htup.t_self.ip_blkid.bi_lo = 0;
            htup.t_self.ip_posid = 0;

            heap_deform_tuple(&htup, tdesc, values, isnull);

            cols->ids[row] = isnull[0] ? 0 : DatumGetInt64(values[0]);
            cols->customers[row] = isnull[1] ? 0 : DatumGetInt32(values[1]);

            if (isnull[2])
            {
                cols->amount_lo[row] = 0;
                cols->amount_hi[row] = 0;
            }
            else
            {
                const char *vp = DatumGetPointer(values[2]);
                if (VARATT_IS_EXTERNAL(vp))
                {
                    cols->amount_lo[row] = 0;
                    cols->amount_hi[row] = 0;
                }
                else
                {
                    __int128 v128 = decode_numeric(VARDATA_ANY(vp), VARSIZE_ANY_EXHDR(vp), 2);
                    cols->amount_lo[row] = (int64_t) ((uint64) v128);
                    cols->amount_hi[row] = (int64_t) ((__int128) v128 >> 64);
                }
            }

            if (isnull[3])
                cols->created_at_us[row] = 0;
            else
            {
                int64 pg_us = DatumGetInt64(values[3]);
                cols->created_at_us[row] = pg_us + ((int64) 946684800 * 1000000);
            }

            for (col = 4; col <= 5; col++)
            {
                size_t *offp = (col == 4) ? &cols->status_off[row] : &cols->payload_off[row];
                size_t *lenp = (col == 4) ? &cols->status_len[row] : &cols->payload_len[row];
                const char *dptr = DatumGetPointer(values[col]);
                if (isnull[col] || VARATT_IS_EXTERNAL(dptr) || VARATT_IS_COMPRESSED(dptr))
                {
                    *offp = strpos; *lenp = 0;
                    if (skipped_toast) (*skipped_toast)++;
                    continue;
                }
                const char *vp = DatumGetPointer(values[col]);
                uint32 vlen = VARSIZE_ANY_EXHDR(vp);
                *offp = strpos; *lenp = vlen;
                if (strpos + vlen <= cols->strbuf_cap)
                {
                    memcpy(cols->strbuf + strpos, VARDATA_ANY(vp), vlen);
                    strpos += vlen;
                }
            }

            cols->actives[row] = isnull[6] ? 0 : DatumGetBool(values[6]);
            row++;
        }
    }
done:
    munmap(file, file_len);
    return row;
}