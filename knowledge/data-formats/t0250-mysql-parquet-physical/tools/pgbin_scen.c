/* pgbin_scen.c — 场景表（3 列: id BIGINT, val INT, note TEXT）物理可见性计数。
 * 用于 T0250 V2/V3/V4 验证：count(可见元组) 对照 PG SELECT count(*)。
 * 输出: {"visible": N, "dead": D, "invisible": I} 逐行到 stderr 可选。
 */
#include <stdio.h>
#include <stdlib.h>
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

int pg_tuple_visible(const void *tup, const char *pgxact_dir);
int pg_clog_xid_status(const char *pgxact_dir, unsigned int xid);

static TupleDesc make_tupdesc_scen(void)
{
    static const struct { int16 attlen; bool attbyval; uint8 attalignby; } info[3] = {
        {8, true, 8},
        {4, true, 4},
        {-1, false, 4},
    };
    size_t sz = offsetof(TupleDescData, compact_attrs) + 3 * sizeof(CompactAttribute);
    TupleDescData *d = palloc(sz);
    int i;
    memset(d, 0, sz);
    d->natts = 3;
    for (i = 0; i < 3; i++)
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
    TupleDesc tdesc = make_tupdesc_scen();
    size_t page_count = file_len / BLCKSZ;
    Datum values[3];
    bool isnull[3];
    long visible = 0, dead = 0, invisible = 0, toast = 0;

    for (size_t page_idx = 0; page_idx < page_count; page_idx++)
    {
        Page page = (Page) (file + page_idx * BLCKSZ);
        OffsetNumber maxoff = PageGetMaxOffsetNumber(page);
        for (OffsetNumber offnum = 1; offnum <= maxoff; offnum++)
        {
            ItemId itemid = PageGetItemId(page, offnum);
            if (!ItemIdIsUsed(itemid) || ItemIdIsRedirected(itemid)) continue;
            if (ItemIdIsDead(itemid)) { dead++; continue; }

            HeapTupleHeader tup = (HeapTupleHeader) PageGetItem(page, itemid);
            if (!pg_tuple_visible(tup, argv[2]))
            {
                invisible++;
                fprintf(stderr, "  invisible offnum=%u xmin=%u xmax=%u infomask=0x%x clog(xmin)=%d clog(xmax)=%d\n",
                        offnum,
                        (unsigned) HeapTupleHeaderGetRawXmin(tup),
                        (unsigned) HeapTupleHeaderGetRawXmax(tup),
                        (unsigned) tup->t_infomask,
                        pg_clog_xid_status(argv[2], HeapTupleHeaderGetRawXmin(tup)),
                        pg_clog_xid_status(argv[2], HeapTupleHeaderGetRawXmax(tup)));
                continue;
            }

            HeapTupleData htup;
            htup.t_data = tup;
            htup.t_len = ItemIdGetLength(itemid);
            htup.t_tableOid = InvalidOid;
            memset(&htup.t_self, 0, sizeof(htup.t_self));
            heap_deform_tuple(&htup, tdesc, values, isnull);

            visible++;
            long id = isnull[0] ? -1 : DatumGetInt64(values[0]);
            long val = isnull[1] ? -99 : DatumGetInt32(values[1]);
            /* note 文本（可能压缩/外部） */
            if (!isnull[2])
            {
                const char *vp = DatumGetPointer(values[2]);
                if (VARATT_IS_EXTERNAL(vp) || VARATT_IS_COMPRESSED(vp)) toast++;
            }
            fprintf(stderr, "  visible id=%ld val=%ld (xmin=%u infomask=0x%x)\n",
                    id, val, (unsigned) HeapTupleHeaderGetRawXmin(tup), (unsigned) tup->t_infomask);
        }
    }
    munmap(file, file_len);
    printf("{\"visible\": %ld, \"dead\": %ld, \"invisible\": %ld, \"toast\": %ld}\n",
           visible, dead, invisible, toast);
    return 0;
}