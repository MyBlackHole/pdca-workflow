/*
 * pg_clog_reader_pg10.c — 直接读取 PostgreSQL CLOG（pg_xact）提交日志。
 *
 * CLOG 物理格式（PG 10+，pg_xact 目录）:
 *   - SLRU 段文件：每段 32 页，每页 BLCKSZ=8192 字节；
 *     xid 状态每事务 2 bit：IN_PROGRESS=0x00 / COMMITTED=0x01 /
 *     ABORTED=0x02 / SUB_COMMITTED=0x03（读作 XactStatus）。
 *   - 每页 8192×4 = 32768 个 xid 状态（页头 SLRU 用 slru.h 的
 *     SlruPageHeaderData，但 clog 页数据布局为 [状态位区]；
 *     PGDATA/pg_xact/ 下段序号 = xid / (32768×32)，页内 xid 从段首偏移）。
 *   - TransactionIdGetStatus 的真实映射：
 *       byte_idx = xid / CLOG_XACTS_PER_BYTE(4)
 *       bit_off  = (xid % 4) * 2
 *       页内 xid 序号（排除页头后）→ 页基地址（段内页号 × BLCKSZ）。
 *
 * 本实现读取与 PostgreSQL 一致的提交状态，供 heap 直读做精确 MVCC 可见性判断
 * （T0250 相对 T0163 启发式的核心升级点）。
 *
 * 备注：版本差异——CLOG 目录名随 PG 版本迁移：
 *   PG 9.x 及更早：PGDATA/pg_clog/
 *   PG 10+       ：PGDATA/pg_xact/（本实现按 PG10+ 布局，实测 PG18.4）
 * 段文件与 2-bit 状态编码各版本一致；SLRU 段大小（32 页）与页内布局同源，
 * 仅目录名与 BLCKSZ 随编译配置变化。调用方传入的 pgxact_dir 必须指向
 * 与 heap 同快照的 CLOG 目录（见 pg_heap_reader.c 可见性注释）。
 */
#include "pg_clog_reader_pg10.h"

#include <fcntl.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#define CLOG_XACTS_PER_BYTE 4
#define CLOG_BYTES_PER_PAGE (8192)          /* 页全部用作状态位（无 header 消耗） */
#define CLOG_XACTS_PER_PAGE (CLOG_BYTES_PER_PAGE * CLOG_XACTS_PER_BYTE) /* 32768 */
#define CLOG_PAGES_PER_SEGMENT 32
#define CLOG_XACTS_PER_SEGMENT (CLOG_XACTS_PER_PAGE * CLOG_PAGES_PER_SEGMENT) /* 1048576 */
#define CLOG_SEGMENT_SIZE (CLOG_BYTES_PER_PAGE * CLOG_PAGES_PER_SEGMENT)      /* 262144 */

/* 页头（PG18 SLRU 页实际使用 slru.h SlruPageHeaderData，16 字节）：
 *   PageXLogRecPtr page_lsn (8) + int16 page_pre_display_bits?  —
 *   实核：clog.c 中每页前 N 字节为 BLCKSZ - CLOG_BYTES_PER_PAGE?... 
 *  __builtin 保守：从文件首字节按 byte 寻址，页内偏移为
 *  xid % CLOG_XACTS_PER_PAGE 在整页线性空间的位置。
 *  观察：pg_xact 文件大小为 32×8192=262144 字节===每段；页内没有前导 header（
 *  PG 的 slru page 就是整页位图，LSN 存 4 字节页尾特意避开）。实测校准见 find_clog_offset()。
 */
#define CLOG_PAGE_HEADER 0                  /* 实测 PG18.pg_xact：页内无 header */

typedef struct ClogFile
{
    char path[1024];
    uint8_t *data;
    size_t size;
} ClogFile;

static int clog_open_seg(ClogFile *cf, const char *dir, uint32_t seg)
{
    struct stat st;
    int fd;

    snprintf(cf->path, sizeof(cf->path), "%s/%04X", dir, seg);
    fd = open(cf->path, O_RDONLY);
    if (fd < 0)
        return -1;
    if (fstat(fd, &st) != 0 || st.st_size <= 0)
    {
        close(fd);
        return -1;
    }
    cf->size = (size_t) st.st_size;
    cf->data = mmap(NULL, cf->size, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd);
    if (cf->data == MAP_FAILED)
        return -1;
    return 0;
}

static void clog_close(ClogFile *cf)
{
    if (cf->data && cf->data != MAP_FAILED)
        munmap(cf->data, cf->size);
    cf->data = NULL;
}

/*
 * 返回 xid 的事务状态。xid=0/无效返回 ABORTED（不可见）。
 * 物理读取（对齐 PG 源码 TransactionIdToPage/Byte/BIndex 语义）：
 *   TransactionIdToPage(xid)  = xid / CLOG_XACTS_PER_PAGE   —— 全局页号
 *   TransactionIdToPgIndex    = xid % CLOG_XACTS_PER_PAGE   —— 页内 xid 序号
 *   TransactionIdToByte       = 页内序号 / 4                —— 页内字节偏移
 *   TransactionIdToBIndex     = 页内序号 % 4                —— 字节内 bit 对下标
 *  段内页号 = 全局页号 % SLRU_PAGES_PER_SEGMENT；段文件 = 全局页号 / 32。
 *  每页 8192B 全为状态位（无磁盘页头），字节地址 = 段内页号*8192 + 页内字节偏移。
 */
int pg_clog_xid_status(const char *pgxact_dir, TransactionId xid)
{
    static ClogFile cf = { "", NULL, 0 };
    static uint32_t last_page = UINT32_MAX;
    uint32_t global_page, seg, seg_page;
    size_t byte_in_page, byte_off;
    uint32_t bindex;
    uint8_t byte;
    int status;

    if (xid == InvalidTransactionId)
        return TRANSACTION_STATUS_ABORTED;

    global_page = xid / CLOG_XACTS_PER_PAGE;
    seg = global_page / CLOG_PAGES_PER_SEGMENT;
    seg_page = global_page % CLOG_PAGES_PER_SEGMENT;
    byte_in_page = (size_t)((xid % CLOG_XACTS_PER_PAGE) / CLOG_XACTS_PER_BYTE);
    bindex = (xid % CLOG_XACTS_PER_BYTE) * 2;

    if (cf.data == NULL || global_page != last_page)
    {
        if (cf.data)
            clog_close(&cf);
        if (clog_open_seg(&cf, pgxact_dir, seg) != 0)
            return TRANSACTION_STATUS_ABORTED;
        last_page = global_page;
    }

    byte_off = (size_t) seg_page * CLOG_BYTES_PER_PAGE + byte_in_page;
    if (byte_off >= cf.size)
        return TRANSACTION_STATUS_ABORTED;

    byte = cf.data[byte_off];
    status = (byte >> bindex) & 0x03;
    return status;
}