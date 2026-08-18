#include <arrow/api.h>
#include <arrow/io/api.h>
#include <arrow/util/decimal.h>
#include <parquet/arrow/writer.h>
#include <parquet/properties.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

/* 由 pg_heap_reader 的 nulls 位图构建 arrow validity buffer（1=非空）。
 * colbit 为列号（bit a）。id(0) 恒非空不建。 */
static std::shared_ptr<arrow::Buffer> validity_buf(const uint8_t *nulls, size_t n, int colbit, size_t *null_count)
{
	arrow::BufferBuilder bb;
	bb.Reserve((n + 7) / 8);
	size_t nc = 0;
	for (size_t i = 0; i < n; i += 8)
	{
		uint8_t b0 = 0;
		size_t end = (i + 8 < n) ? i + 8 : n;
		for (size_t k = i; k < end; k++)
			if (!(nulls[k] & (1u << colbit)))
				b0 |= (uint8_t) (1u << (k & 7));
		bb.Append(&b0, 1);
	}
	for (size_t i = 0; i < n; i++)
		if (nulls[i] & (1u << colbit))
			nc++;
	if (null_count)
		*null_count = nc;
	auto r = bb.Finish();
	if (!r.ok())
	{
		fprintf(stderr, "validity: %s\n", r.status().ToString().c_str());
		std::abort();
	}
	return *r;
}

extern "C"
{
	typedef struct
	{
		int64_t *ids;
		int32_t *customers;
		int64_t *created_at_us;
		int64_t *amount_lo;
		int64_t *amount_hi;
		uint8_t *actives;
		uint8_t *nulls;         /* 每行 1 字节：bit a=第 a 列 NULL（与 pg_heap_reader 一致） */
		char *strbuf;
		size_t *status_off;
		size_t *status_len;
		size_t *payload_off;
		size_t *payload_len;
		size_t strbuf_cap;
	} HeapCols;
	typedef struct
	{
		size_t page_idx;
		unsigned short next_offnum;
	} ParseCursor;
	size_t pg_parse_heap_range(const char *path, const char *pgxact_dir,
	                           HeapCols *cols, size_t max_rows, ParseCursor *cur,
	                           uint64_t *seen_total, uint64_t *skipped_invisible,
	                           uint64_t *skipped_dead, uint64_t *skipped_toast);
}

static double now_s()
{
	using namespace std::chrono;
	return duration<double>(steady_clock::now().time_since_epoch()).count();
}

// 将每行 1 字节的 bool 数组 (0/1) 打包为 Arrow 位图 (LSB-first, row i 占 bit i)。
// Arrow 位图要求的字节序：bit0 为第 0 行。这里同时适配 arrow/buffer.
static std::shared_ptr<arrow::Buffer> bits_pack(const uint8_t *bools, size_t n,
                                                arrow::MemoryPool *pool)
{
	size_t nbytes = (n + 7) / 8;
	auto status_and_buf = arrow::AllocateBuffer(nbytes, pool);
	uint8_t *out = status_and_buf.ValueOrDie()->mutable_data();
	memset(out, 0, nbytes);
	for (size_t i = 0; i < n; i++)
		if (bools[i])
			out[i >> 3] |= (uint8_t) (1u << (i & 7));
	return std::move(status_and_buf).ValueOrDie();
}

int main(int argc, char **argv)
{
	// T0301：--pg-version=N 标注源 PG 版本（N 为版本号数字，如 96/11/18）。
	// 经实测 PG9.6/11/18 的 heap 头布局与 varlena 编码一致，版本仅决定
	// CLOG 目录名语义（pg9.x 及更早 pg_clog/，PG10+ pg_xact/）；目录实际
	// 由位置参数 clog 给出，此处仅打印提示供核对。
	int src_ver = 0;
	const char *heap_path = nullptr;
	const char *pgxact_dir = "";
	const char *out_path = "pg_cpp.parquet";
	size_t max_rows = 1000000;
	for (int i = 1; i < argc; i++)
	{
		if (strncmp(argv[i], "--pg-version=", 13) == 0)
		{
			src_ver = atoi(argv[i] + 13);
		}
		else if (strncmp(argv[i], "--", 2) == 0)
			;
		else if (heap_path == nullptr)
			heap_path = argv[i];
		else if (pgxact_dir == nullptr || *pgxact_dir == 0)
			pgxact_dir = argv[i];
		else if (out_path == nullptr || strcmp(out_path, "pg_cpp.parquet") == 0)
			out_path = argv[i];
		else
			max_rows = strtoull(argv[i], nullptr, 10);
	}
	if (heap_path == nullptr)
		heap_path = "/tmp/opencode/pgfiledump-test/poc_orders_heap";
	if (src_ver > 0)
		fprintf(stderr, "[info] src PG version: %d (heap/varlena layout same across "
		        "PG9.6/11/18; CLOG dir taken from positional arg)\n", src_ver);
	const size_t batch = 1 << 20;

	double t0 = now_s();

	// 列式布局（每批 1M 行）
	HeapCols cols = {};
	cols.ids = new int64_t[batch];
	cols.customers = new int32_t[batch];
	cols.created_at_us = new int64_t[batch];
	cols.amount_lo = new int64_t[batch];
	cols.amount_hi = new int64_t[batch];
	cols.actives = new uint8_t[batch];
	cols.nulls = new uint8_t[batch];
	cols.strbuf_cap = (size_t) 128 * 1024 * 1024;
	cols.strbuf = new char[cols.strbuf_cap];
	cols.status_off = new size_t[batch];
	cols.status_len = new size_t[batch];
	cols.payload_off = new size_t[batch];
	cols.payload_len = new size_t[batch];

	// schema 与 writer 只建一次，按批 WriteTable
	std::shared_ptr<arrow::Schema> schema = arrow::schema(
		{arrow::field("id", arrow::int64()),
		 arrow::field("customer_id", arrow::int32()),
		 arrow::field("amount", arrow::decimal128(12, 2)),
		 arrow::field("created_at", arrow::timestamp(arrow::TimeUnit::MICRO)),
		 arrow::field("status", arrow::utf8()),
		 arrow::field("payload", arrow::utf8()),
		 arrow::field("active", arrow::boolean())});
	parquet::WriterProperties::Builder wb;
	wb.compression(parquet::Compression::ZSTD);
	auto writer_props = wb.build();
	parquet::ArrowWriterProperties::Builder ab;
	auto arrow_props = ab.store_schema()->build();
	auto ofs_result = arrow::io::FileOutputStream::Open(out_path);
	if (!ofs_result.ok())
	{
		fprintf(stderr, "open out: %s\n", ofs_result.status().ToString().c_str());
		return 1;
	}
	auto writer_result = parquet::arrow::FileWriter::Open(*schema, arrow::default_memory_pool(), *ofs_result, writer_props, arrow_props);
	if (!writer_result.ok())
	{
		fprintf(stderr, "writer: %s\n", writer_result.status().ToString().c_str());
		return 1;
	}

	ParseCursor cur = {};
	size_t total = 0;
	double t_parse_sum = 0, t_text_sum = 0, t_arrays_sum = 0, t_write_sum = 0;
	uint64_t seen_total = 0, skipped_invisible = 0, skipped_dead = 0, skipped_toast = 0;

	for (;;)
	{
		double t_b0 = now_s();
		size_t want = (max_rows - total < batch) ? (max_rows - total) : batch;
		if (want == 0)
			break;
size_t n = pg_parse_heap_range(heap_path, pgxact_dir, &cols, want, &cur,
			                               &seen_total, &skipped_invisible, &skipped_dead, &skipped_toast);
		double t_parse = now_s();
		if (n == 0)
			break;
		total += n;

		// 文本列总长 → 连续 buffer + offsets
		size_t total_status = 0, total_payload = 0;
		for (size_t i = 0; i < n; i++)
		{
			total_status += cols.status_len[i];
			total_payload += cols.payload_len[i];
		}

		std::string status_blob, payload_blob;
		status_blob.reserve(total_status);
		payload_blob.reserve(total_payload);
		std::vector<int32_t> status_off2, payload_off2;
		status_off2.reserve(n + 1);
		payload_off2.reserve(n + 1);

		// status 数组（独立 buffer）
		status_off2.push_back(0);
		for (size_t i = 0; i < n; i++)
		{
			status_blob.append(cols.strbuf + cols.status_off[i], cols.status_len[i]);
			status_off2.push_back((int32_t) status_blob.size());
		}

		// payload 数组（独立 buffer）
		payload_off2.push_back(0);
		for (size_t i = 0; i < n; i++)
		{
			payload_blob.append(cols.strbuf + cols.payload_off[i], cols.payload_len[i]);
			payload_off2.push_back((int32_t) payload_blob.size());
		}
		double t_text = now_s();

		// Arrow arrays（零拷贝包装）
		auto status_buf = std::make_shared<arrow::Buffer>((const uint8_t *) status_blob.data(), status_blob.size());
		auto status_offsets = std::make_shared<arrow::Buffer>((const uint8_t *) status_off2.data(),
															  status_off2.size() * sizeof(int32_t));
		auto payload_buf = std::make_shared<arrow::Buffer>((const uint8_t *) payload_blob.data(), payload_blob.size());
		auto payload_offsets = std::make_shared<arrow::Buffer>((const uint8_t *) payload_off2.data(),
															   payload_off2.size() * sizeof(int32_t));

		// validity buffers：id(0) 恒非空；其余 6 列从 nulls 位图构建
		size_t nc_cust = 0, nc_ts = 0, nc_amt = 0, nc_st = 0, nc_pl = 0, nc_act = 0;
		auto v_cust = validity_buf(cols.nulls, n, 1, &nc_cust);
		auto v_amt  = validity_buf(cols.nulls, n, 2, &nc_amt);
		auto v_ts   = validity_buf(cols.nulls, n, 3, &nc_ts);
		auto v_st   = validity_buf(cols.nulls, n, 4, &nc_st);
		auto v_pl   = validity_buf(cols.nulls, n, 5, &nc_pl);
		auto v_act  = validity_buf(cols.nulls, n, 6, &nc_act);

		auto id_arr = std::make_shared<arrow::NumericArray<arrow::Int64Type>>(n,
			std::make_shared<arrow::Buffer>((const uint8_t *) cols.ids, n * 8), nullptr, 0);
		auto customer_arr = std::make_shared<arrow::NumericArray<arrow::Int32Type>>(n,
			std::make_shared<arrow::Buffer>((const uint8_t *) cols.customers, n * 4), v_cust, (int64_t) nc_cust);
		auto ts_arr = std::make_shared<arrow::NumericArray<arrow::TimestampType>>(
			arrow::timestamp(arrow::TimeUnit::MICRO), n,
			std::make_shared<arrow::Buffer>((const uint8_t *) cols.created_at_us, n * 8), v_ts, (int64_t) nc_ts);
		auto bool_arr = std::make_shared<arrow::BooleanArray>(n,
			bits_pack(cols.actives, n, arrow::default_memory_pool()), v_act, (int64_t) nc_act, 0);
		auto status_arr = std::make_shared<arrow::StringArray>(n, status_offsets, status_buf, v_st, (int64_t) nc_st);
		auto payload_arr = std::make_shared<arrow::StringArray>(n, payload_offsets, payload_buf, v_pl, (int64_t) nc_pl);

		// Decimal128(12,2)：从 lo/hi 位模式构建（NULL 列 AppendNull）
		auto decimal_builder = std::make_shared<arrow::Decimal128Builder>(
			arrow::decimal128(12, 2), arrow::default_memory_pool());
		arrow::Status st;
		for (size_t i = 0; i < n; i++)
		{
			if (cols.nulls[i] & (1u << 2))
			{
				st = decimal_builder->AppendNull();
			}
			else
			{
				arrow::Decimal128 d(cols.amount_hi[i], (uint64_t) cols.amount_lo[i]);
				st = decimal_builder->Append(d);
			}
			if (!st.ok())
			{
				fprintf(stderr, "decimal append: %s\n", st.ToString().c_str());
				return 1;
			}
		}
		std::shared_ptr<arrow::Array> dec_arr;
		decimal_builder->Finish(&dec_arr);
		double t_arrays = now_s();

		auto table = arrow::Table::Make(schema, {id_arr, customer_arr, dec_arr, ts_arr, status_arr, payload_arr, bool_arr}, n);
		auto status_w =   (*writer_result)->WriteTable(*table, batch);
		if (!status_w.ok())
		{
			fprintf(stderr, "write: %s\n", status_w.ToString().c_str());
			return 1;
		}
		double t_done = now_s();

		t_parse_sum += t_parse - t_b0;
		t_text_sum += t_text - t_parse;
		t_arrays_sum += t_arrays - t_text;
		t_write_sum += t_done - t_arrays;
		if (total >= max_rows)
			break;
	}
	(*writer_result)->Close();
	double t_final = now_s();

	printf("{\n");
	printf("  \"rows\": %zu,\n", total);
	printf("  \"parse_seconds\": %.4f,\n", t_parse_sum);
	printf("  \"text_seconds\": %.4f,\n", t_text_sum);
	printf("  \"arrays_seconds\": %.4f,\n", t_arrays_sum);
	printf("  \"write_seconds\": %.4f,\n", t_write_sum);
	printf("  \"total_seconds\": %.4f,\n", t_final - t0);
	printf("  \"throughput_rows_per_second\": %.2f,\n", (double) total / (t_final - t0));
	printf("  \"seen_total\": %llu,\n", (unsigned long long) seen_total);
	printf("  \"skipped_invisible\": %llu,\n", (unsigned long long) skipped_invisible);
	printf("  \"skipped_dead\": %llu,\n", (unsigned long long) skipped_dead);
	printf("  \"skipped_toast\": %llu\n", (unsigned long long) skipped_toast);
	printf("}\n");

	delete[] cols.ids;
	delete[] cols.customers;
	delete[] cols.created_at_us;
	delete[] cols.amount_lo;
	delete[] cols.amount_hi;
	delete[] cols.actives;
	delete[] cols.strbuf;
	delete[] cols.status_off;
	delete[] cols.status_len;
	delete[] cols.payload_off;
	delete[] cols.payload_len;
	return 0;
}
