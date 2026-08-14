// dump_boundary.c — 独立验证工具：用匹配 schema 解析 poc_boundary 表，对照 PG 源数据。
// 编译复用 pg_heap_reader.c 的主体逻辑，但用 8 列 tupdesc 并打印每个字段。
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>

#include "postgres.h"
#include "access/htup_details.h"
#include "access/htup.h"
#include "access/transam.h"
#include "access/slru.h"
#include "access/xact.h"
#include "utils/memutils.h"
#include "utils/palloc.h"
#include "nodes/pg_list.h"
#include "access/heaptoast.h"

#include "../src/pg/pg_clog_reader.h"

/* pg_tuple_visible 实现在 pg_heap_reader.c（对外可见） */
int pg_tuple_visible(const void *tup, const char *pgxact_dir);

#ifndef ALIGNOF
#define ALIGNOF(type) \
    (((offsetof(struct { char c; type t; }, t)) == 0) ? 0 : \
     (offsetof(struct { char c; type t; }, t)))
#endif
#define ALIGNOF_DOUBLE ALIGNOF(double)
#define ALIGNOF_INT ALIGNOF(int32)
#define ALIGNOF_SHORT ALIGNOF(int16)
#define ALIGNOF_CHAR ALIGNOF(char)

static TupleDesc make_tupdesc_boundary(void)
{
    /* poc_boundary: id int8, n_null int4, s_empty text, d_extreme numeric,
       b_large text, u_emoji text, t_ts timestamptz, act bool */
    static const struct { int16 attlen; bool attbyval; uint8 attalignby; } info[8] = {
        {8, true, ALIGNOF_DOUBLE},
        {4, true, ALIGNOF_INT},
        {-1, false, ALIGNOF_INT},
        {-1, false, ALIGNOF_INT},
        {-1, false, ALIGNOF_INT},
        {-1, false, ALIGNOF_INT},
        {8, true, ALIGNOF_DOUBLE},
        {1, true, ALIGNOF_CHAR},
    };
    size_t sz = offsetof(TupleDescData, compact_attrs) + 8 * sizeof(CompactAttribute);
    TupleDescData *d = palloc(sz);
    int i;
    memset(d, 0, sz);
    d->natts = 8;
    for (i = 0; i < 8; i++)
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

int main(int argc, char **argv)
{
    if (argc < 3)
    {
        fprintf(stderr, "usage: %s <heap_path> <pgxact_dir>\n", argv[0]);
        return 1;
    }
    struct stat st;
    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) { perror("open"); return 1; }
    if (fstat(fd, &st) != 0) { perror("fstat"); return 1; }
    size_t file_len = (size_t) st.st_size;
    uint8_t *file = mmap(NULL, file_len, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd);
    if (file == MAP_FAILED) { perror("mmap"); return 1; }

    MemoryContextInit();
    TupleDesc tdesc = make_tupdesc_boundary();
    size_t page_count = file_len / BLCKSZ;
    Datum values[8];
    bool isnull[8];
    unsigned long row = 0;

    for (size_t page_idx = 0; page_idx < page_count; page_idx++)
    {
        Page page = (Page) (file + page_idx * BLCKSZ);
        OffsetNumber maxoff = PageGetMaxOffsetNumber(page);
        for (OffsetNumber offnum = 1; offnum <= maxoff; offnum++)
        {
            ItemId itemid = PageGetItemId(page, offnum);
            if (!ItemIdIsUsed(itemid) || ItemIdIsRedirected(itemid)) continue;
            if (ItemIdIsDead(itemid)) { printf("[dead] offnum=%u (purge pending)\n", offnum); continue; }

            HeapTupleHeader tup = (HeapTupleHeader) PageGetItem(page, itemid);
            if (!pg_tuple_visible(tup, argv[2]))
            {
                printf("[invisible] offnum=%u xmin=%u\n",
                       offnum, (unsigned) HeapTupleHeaderGetRawXmin(tup));
                continue;
            }

            HeapTupleData htup;
            htup.t_data = tup;
            htup.t_len = ItemIdGetLength(itemid);
            htup.t_tableOid = InvalidOid;
            memset(&htup.t_self, 0, sizeof(htup.t_self));
            heap_deform_tuple(&htup, tdesc, values, isnull);

            row++;
            printf("--- row %lu (t_xmin=%u t_xmax=%u t_infomask=0x%x t_infomask2=0x%x t_hoff=%u natts=%u) ---\n",
                   row,
                   (unsigned) HeapTupleHeaderGetRawXmin(tup),
                   (unsigned) HeapTupleHeaderGetRawXmax(tup),
                   (unsigned) tup->t_infomask,
                   (unsigned) tup->t_infomask2,
                   (unsigned) tup->t_hoff,
                   (unsigned) HeapTupleHeaderGetNatts(tup));

            /* id */
            printf("  id = %lld\n", (long long) (isnull[0] ? -1 : DatumGetInt64(values[0])));
            /* n_null */
            printf("  n_null = %s\n", isnull[1] ? "NULL" : "(not null)");
            /* s_empty */
            if (isnull[2]) printf("  s_empty = NULL\n");
            else {
                const char *vp = DatumGetPointer(values[2]);
                if (VARATT_IS_EXTERNAL(vp)) printf("  s_empty = [TOAST external]\n");
                else
                    printf("  s_empty = '%s' (len=%u)\n",
                           VARDATA_ANY(vp), (unsigned) VARSIZE_ANY_EXHDR(vp));
            }
            /* d_extreme numeric -> 二进制 */
            if (isnull[3]) printf("  d_extreme = NULL\n");
            else {
                const char *vp = DatumGetPointer(values[3]);
                if (VARATT_IS_EXTERNAL(vp)) printf("  d_extreme = [TOAST]\n");
                else
                    printf("  d_extreme = [raw %u bytes: %02x %02x %02x %02x %02x]\n",
                           (unsigned) VARSIZE_ANY_EXHDR(vp),
                           (unsigned char) VARDATA_ANY(vp)[0], (unsigned char) VARDATA_ANY(vp)[1],
                           (unsigned char) VARDATA_ANY(vp)[2], (unsigned char) VARDATA_ANY(vp)[3],
                           (unsigned char) VARDATA_ANY(vp)[4]);
            }
            /* b_large */
            if (isnull[4]) printf("  b_large = NULL\n");
            else {
                const char *vp = DatumGetPointer(values[4]);
                if (VARATT_IS_EXTERNAL(vp)) printf("  b_large = [TOAST external]\n");
                else
                    printf("  b_large = len=%u first='%.32s'\n",
                           (unsigned) VARSIZE_ANY_EXHDR(vp), VARDATA_ANY(vp));
            }
            /* u_emoji */
            if (isnull[5]) printf("  u_emoji = NULL\n");
            else {
                const char *vp = DatumGetPointer(values[5]);
                if (VARATT_IS_EXTERNAL(vp)) printf("  u_emoji = [TOAST external]\n");
                else
                    printf("  u_emoji = '%s' (bytes=%u)\n",
                           VARDATA_ANY(vp), (unsigned) VARSIZE_ANY_EXHDR(vp));
            }
            /* t_ts */
            printf("  t_ts = %lld (us since 2000-01-01)\n",
                   (long long) (isnull[6] ? 0 : DatumGetInt64(values[6])));
            /* act */
            printf("  act = %s\n", isnull[7] ? "NULL" : (DatumGetBool(values[7]) ? "t" : "f"));
        }
    }
    munmap(file, file_len);
    return 0;
}