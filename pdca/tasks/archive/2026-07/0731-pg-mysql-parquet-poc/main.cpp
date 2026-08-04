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
	size_t pg_parse_heap_range(const char *path, HeapCols *cols, size_t max_rows, ParseCursor *cur);
}

static double now_s()
{
	using namespace std::chrono;
	return duration<double>(steady_clock::now().time_since_epoch()).count();
}

int main(int argc, char **argv)
{
	const char *heap_path = argc > 1 ? argv[1] : "/tmp/opencode/pgfiledump-test/poc_orders_heap";
	const char *out_path = argc > 2 ? argv[2] : "pg_cpp.parquet";
	const size_t max_rows = argc > 3 ? strtoull(argv[3], nullptr, 10) : 1000000;
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

	for (;;)
	{
		double t_b0 = now_s();
		size_t want = (max_rows - total < batch) ? (max_rows - total) : batch;
		if (want == 0)
			break;
		size_t n = pg_parse_heap_range(heap_path, &cols, want, &cur);
		double t_parse = now_s();
		if (n == 0)
			break;
		total += n;

		// 文本列总长 → 连续 buffer + offsets
		size_t total_text = 0;
		for (size_t i = 0; i < n; i++)
			total_text += cols.status_len[i] + cols.payload_len[i];

		std::string text_blob;
		text_blob.reserve(total_text);
		std::vector<int32_t> status_off, status_len, payload_off, payload_len;
		std::vector<int32_t> text_off_combined;

		// status 数组
		text_off_combined.reserve(n + 1);
		text_off_combined.push_back(0);
		for (size_t i = 0; i < n; i++)
		{
			text_blob.append(cols.strbuf + cols.status_off[i], cols.status_len[i]);
			text_off_combined.push_back((int32_t) text_blob.size());
		}

		// payload 数组
		std::vector<int32_t> payload_off2;
		payload_off2.reserve(n + 1);
		payload_off2.push_back(0);
		for (size_t i = 0; i < n; i++)
		{
			text_blob.append(cols.strbuf + cols.payload_off[i], cols.payload_len[i]);
			payload_off2.push_back((int32_t) text_blob.size());
		}
		double t_text = now_s();

		// Arrow arrays（零拷贝包装）
		auto text_buf = std::make_shared<arrow::Buffer>((const uint8_t *) text_blob.data(), text_blob.size());
		auto status_offsets = std::make_shared<arrow::Buffer>((const uint8_t *) text_off_combined.data(),
															  text_off_combined.size() * sizeof(int32_t));
		auto payload_offsets = std::make_shared<arrow::Buffer>((const uint8_t *) payload_off2.data(),
															   payload_off2.size() * sizeof(int32_t));

		auto id_arr = std::make_shared<arrow::NumericArray<arrow::Int64Type>>(n,
			std::make_shared<arrow::Buffer>((const uint8_t *) cols.ids, n * 8), nullptr, 0);
		auto customer_arr = std::make_shared<arrow::NumericArray<arrow::Int32Type>>(n,
			std::make_shared<arrow::Buffer>((const uint8_t *) cols.customers, n * 4), nullptr, 0);
		auto ts_arr = std::make_shared<arrow::NumericArray<arrow::TimestampType>>(
			arrow::timestamp(arrow::TimeUnit::MICRO), n,
			std::make_shared<arrow::Buffer>((const uint8_t *) cols.created_at_us, n * 8), nullptr, 0);
		auto bool_arr = std::make_shared<arrow::BooleanArray>(n,
			std::make_shared<arrow::Buffer>((const uint8_t *) cols.actives, (n + 7) / 8), nullptr, 0, 0);
		auto status_arr = std::make_shared<arrow::StringArray>(n, status_offsets, text_buf, nullptr, 0);
		auto payload_arr = std::make_shared<arrow::StringArray>(n, payload_offsets, text_buf, nullptr, 0);

		// Decimal128(12,2)：从 lo/hi 位模式构建
		auto decimal_builder = std::make_shared<arrow::Decimal128Builder>(
			arrow::decimal128(12, 2), arrow::default_memory_pool());
		arrow::Status st;
		for (size_t i = 0; i < n; i++)
		{
			arrow::Decimal128 d(cols.amount_hi[i], (uint64_t) cols.amount_lo[i]);
			st = decimal_builder->Append(d);
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
	printf("  \"throughput_rows_per_second\": %.2f\n", (double) total / (t_final - t0));
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
