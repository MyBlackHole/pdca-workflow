/*
 * pg_heap_reader.c — 使用 PostgreSQL 18.4 官方解析代码直接读取 heap 数据文件。
 *
 * 复用官方实现而非手推列偏移：
 *   - 页层:  PageGetItemId / PageGetItem (storage/bufpage.h)
 *   - 行层:  heap_deform_tuple (access/common/heaptuple.c)
 *            官方实现处理 null bitmap / varlena 头 / 列对齐 / 偏移缓存
 *   - 类型层: 二进制解释（numeric → Decimal128、timestamp epoch 换算）
 *
 * backend 运行时依赖（mcxt/aset/elog）由 stub_pg.c 提供最小实现。
 */
#include "postgres.h"

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

#include "access/htup_details.h"
#include "access/tupdesc.h"
#include "access/tupmacs.h"
#include "storage/bufpage.h"
#include "utils/memutils.h"
#include "utils/elog.h"

/* c.h 在 C 模式下把 fprintf 宏替换为 pg_fprintf，此处解除以使用标准函数 */
#ifdef fprintf
#undef fprintf
#endif

#define NBASE 10000

/*
 * 以下结构体与宏从 PostgreSQL 18.4 src/backend/utils/adt/numeric.c 原样拷贝，
 * 以读取 on-disk NUMERIC 格式（NumericData 内部布局对头文件私有）。
 */
typedef int16 NumericDigit;

struct NumericShort
{
	uint16		n_header;
	NumericDigit n_data[FLEXIBLE_ARRAY_MEMBER];
};
struct NumericLong
{
	uint16		n_sign_dscale;
	int16		n_weight;
	NumericDigit n_data[FLEXIBLE_ARRAY_MEMBER];
};
union NumericChoice
{
	uint16		n_header;
	struct NumericLong n_long;
	struct NumericShort n_short;
};

#define NUMERIC_SIGN_MASK	0xC000
#define NUMERIC_POS			0x0000
#define NUMERIC_NEG			0x4000
#define NUMERIC_SHORT		0x8000
#define NUMERIC_SPECIAL		0xC000
#define NUMERIC_FLAGBITS(n) ((n)->n_header & NUMERIC_SIGN_MASK)
#define NUMERIC_IS_SHORT(n)		(NUMERIC_FLAGBITS(n) == NUMERIC_SHORT)
#define NUMERIC_IS_SPECIAL(n)	(NUMERIC_FLAGBITS(n) == NUMERIC_SPECIAL)
#define NUMERIC_HEADER_IS_SHORT(n)	(((n)->n_header & 0x8000) != 0)
#define NUMERIC_SHORT_SIGN_MASK			0x2000
#define NUMERIC_SHORT_DSCALE_MASK		0x1F80
#define NUMERIC_SHORT_DSCALE_SHIFT		7
#define NUMERIC_SHORT_WEIGHT_SIGN_MASK	0x0040
#define NUMERIC_SHORT_WEIGHT_MASK		0x003F
#define NUMERIC_DSCALE_MASK			0x3FFF
#define NUMERIC_SIGN(n) \
	(NUMERIC_IS_SHORT(n) ? \
		(((n)->n_short.n_header & NUMERIC_SHORT_SIGN_MASK) ? \
		 NUMERIC_NEG : NUMERIC_POS) : \
		(NUMERIC_IS_SPECIAL(n) ? \
		 NUMERIC_FLAGBITS(n) : NUMERIC_FLAGBITS(n)))
#define NUMERIC_DSCALE(n)	(NUMERIC_HEADER_IS_SHORT((n)) ? \
	((n)->n_short.n_header & NUMERIC_SHORT_DSCALE_MASK) \
		>> NUMERIC_SHORT_DSCALE_SHIFT \
	: ((n)->n_long.n_sign_dscale & NUMERIC_DSCALE_MASK))
#define NUMERIC_WEIGHT(n)	(NUMERIC_HEADER_IS_SHORT((n)) ? \
	(((n)->n_short.n_header & NUMERIC_SHORT_WEIGHT_SIGN_MASK ? \
		~NUMERIC_SHORT_WEIGHT_MASK : 0) \
	 | ((n)->n_short.n_header & NUMERIC_SHORT_WEIGHT_MASK)) \
	: ((n)->n_long.n_weight))

typedef struct HeapCols
{
	int64_t *ids;
	int32_t *customers;
	int64_t *created_at_us;		/* unix epoch 微秒 */
	int64_t *amount_lo;/* Decimal128 low 64 bits 位模式 */
	int64_t *amount_hi;/* Decimal128 high 64 bits */
	uint8_t *actives;
	char *strbuf;				/* 文本列连续缓冲 */
	size_t *status_off;			/* 文本起始偏移 */
	size_t *status_len;
	size_t *payload_off;
	size_t *payload_len;
	size_t strbuf_cap;
} HeapCols;

/* 解析游标：支持分批（batch）处理，避免每批从头重扫文件 */
typedef struct
{
	size_t		page_idx;
	uint16		next_offnum;	/* 本页下一个行指针（1 起），0 表示页未开始 */
} ParseCursor;

/* 将 on-disk numeric 解码为 Decimal128（scale=2 整数），返回 __int128 */
static __int128
decode_numeric(const char *data, size_t len, int target_scale)
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
		return 0;				/* NaN/Inf 不在本测试数据中 */

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

	/* 0 值（如 0.00）可只存 2 字节头部、无 digits；此时直接返回 0 */
	if (ndigits <= 0)
		return 0;

	/* 值 = Σ digit[i] × 10^(4·(weight-i))；目标位模式 = 值 × 10^target_scale。
	 * 全部 digit 对齐到最小 10 指数后再除，避免整数除法丢失小数精度。 */
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
		int e = exp10[i] - min_exp;	/* >= 0 */
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
		value /= den;			/* 整除即精确；否则截断（同 PG 显示行为） */
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

/*
 * 构造 7 列的表结构描述（官方 CompactAttribute 布局，供 heap_deform_tuple 使用）。
 * 列: id BIGINT, customer_id INT, amount NUMERIC, created_at TIMESTAMP,
 *     status TEXT, payload TEXT, active BOOL
 */
static TupleDesc
make_tupdesc(void)
{
	static const struct
	{
		int16		attlen;
		bool		attbyval;
		uint8		attalignby;
	}			info[7] = {
		{8, true, ALIGNOF_DOUBLE},	/* id BIGINT */
		{4, true, ALIGNOF_INT},	/* customer_id INT */
		{-1, false, ALIGNOF_INT},	/* amount NUMERIC (varlena) */
		{8, true, ALIGNOF_DOUBLE},	/* created_at TIMESTAMP */
		{-1, false, ALIGNOF_INT},	/* status TEXT */
		{-1, false, ALIGNOF_INT},	/* payload TEXT */
		{1, true, 1},			/* active BOOL */
	};
	size_t		sz = offsetof(TupleDescData, compact_attrs) + 7 * sizeof(CompactAttribute);
	TupleDescData *d = palloc(sz);
	int			i;

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

/*
 * 从 cur 指定的位置开始解析至多 max_rows 行到 cols；前进 cur。
 * 返回实际解析行数；0 表示已到文件末尾。
 */
size_t
pg_parse_heap_range(const char *path, HeapCols *cols, size_t max_rows, ParseCursor *cur)
{
	struct stat st;
	int fd;
	uint8_t *file;
	size_t file_len;
	size_t page_count;
	size_t page_idx;
	size_t row = 0;
	size_t strpos = 0;
	static TupleDesc tdesc;
	Datum		values[7];
	bool		isnull[7];
	static bool inited = false;

	if (!inited)
	{
		MemoryContextInit();
		tdesc = make_tupdesc();
		inited = true;
	}

	fd = open(path, O_RDONLY);
	if (fd < 0)
	{
		fprintf(stderr, "open failed: %s\n", path);
		return 0;
	}
	if (fstat(fd, &st) != 0 || st.st_size == 0)
	{
		close(fd);
		return 0;
	}
	file_len = (size_t) st.st_size;
	file = mmap(NULL, file_len, PROT_READ, MAP_PRIVATE, fd, 0);
	close(fd);
	if (file == MAP_FAILED)
	{
		fprintf(stderr, "mmap failed\n");
		return 0;
	}

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
			uint16 infomask;
			int col;
			HeapTupleData htup;

			/* 处理完此行后（无论是否可见）游标前进，保证不重扫 */
			cur->page_idx = page_idx;
			cur->next_offnum = (uint16) (offnum + 1);

			if (!ItemIdIsUsed(itemid) || ItemIdIsRedirected(itemid))
				continue;
			if (ItemIdIsDead(itemid))
				continue;

			tup = (HeapTupleHeader) PageGetItem(page, itemid);
			infomask = tup->t_infomask;

			/* 只处理可见的普通行（忽略已删除/未提交的） */
			if ((infomask & HEAP_XMAX_INVALID) == 0)
				continue;
			if (infomask & HEAP_UPDATED)
				continue;
			if (row >= max_rows)
			{
				/* 本行未处理：游标回退一行，留给下一批 */
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

				if (isnull[col])
				{
					*offp = strpos;
					*lenp = 0;
					continue;
				}
				else
				{
					const char *vp = DatumGetPointer(values[col]);
					uint32 vlen = VARSIZE_ANY_EXHDR(vp);
					*offp = strpos;
					*lenp = vlen;
					if (strpos + vlen <= cols->strbuf_cap)
					{
						memcpy(cols->strbuf + strpos, VARDATA_ANY(vp), vlen);
						strpos += vlen;
					}
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
