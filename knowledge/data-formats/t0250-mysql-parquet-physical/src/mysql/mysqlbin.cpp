#include <arrow/api.h>
#include <arrow/io/api.h>
#include <arrow/util/decimal.h>
#include <parquet/arrow/writer.h>
#include <parquet/properties.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <string>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

extern "C"
{
#include "mysql_parse_pages.h"
#include "mysql_sdi.h"
#include "mysql_layout_schema_56_57.h"
}

#include "tde_decrypt.h"

static double now_s()
{
	using namespace std::chrono;
	return duration<double>(steady_clock::now().time_since_epoch()).count();
}

/* 根据物理 mtype 映射 Arrow 类型 */
static std::shared_ptr<arrow::Field> arrow_field(const MysqlField &f)
{
	const char *name = f.name;
	std::shared_ptr<arrow::DataType> dt;
	switch (f.mtype)
	{
	case MF_INT: dt = f.is_bool ? arrow::boolean()
		: (f.is_unsigned ? arrow::uint64()
			: ((f.dd_type == 22 || f.dd_type == 23) ? arrow::utf8() : arrow::int64())); break;
	case MF_FLOAT: dt = arrow::float32(); break;
	case MF_DOUBLE: dt = arrow::float64(); break;
	case MF_DECIMAL: dt = arrow::decimal128(f.precision, f.scale); break;
	case MF_DATETIME2:
	case MF_TIMESTAMP2:
	case MF_DATE: dt = arrow::timestamp(arrow::TimeUnit::MICRO); break;
	case MF_TIME2: dt = arrow::int64(); break;
	case MF_VARCHAR:
	case MF_STRING:
	case MF_JSON: dt = arrow::utf8(); break;
	case MF_BLOB:
	default: dt = arrow::binary(); break;
	}
	return arrow::field(name, dt, (bool)f.nullable);
}

/* 一个 batch 内按列构建 Arrow 数组 */
struct ColBuilder
{
	int mtype;
	arrow::NumericBuilder<arrow::Int64Type> i64_b;
	arrow::NumericBuilder<arrow::FloatType> f32_b;
	arrow::NumericBuilder<arrow::DoubleType> f64_b;
	arrow::Decimal128Builder dec_b;
	arrow::TimestampBuilder ts_b; /* MICRO */
	arrow::StringBuilder str_b;
	arrow::BinaryBuilder bin_b;
};

static std::shared_ptr<arrow::ArrayBuilder> make_builder(const MysqlField &f)
{
	if (f.mtype == MF_INT && f.is_bool)
		return std::make_shared<arrow::BooleanBuilder>(arrow::default_memory_pool());
	switch (f.mtype)
	{
	case MF_INT:
		if (f.dd_type == 22 || f.dd_type == 23)
			return std::make_shared<arrow::StringBuilder>(arrow::default_memory_pool());
		if (f.is_unsigned)
			return std::make_shared<arrow::NumericBuilder<arrow::UInt64Type>>(arrow::default_memory_pool());
		return std::make_shared<arrow::NumericBuilder<arrow::Int64Type>>(arrow::default_memory_pool());
	case MF_FLOAT: return std::make_shared<arrow::NumericBuilder<arrow::FloatType>>(arrow::default_memory_pool());
	case MF_DOUBLE: return std::make_shared<arrow::NumericBuilder<arrow::DoubleType>>(arrow::default_memory_pool());
	case MF_DECIMAL: return std::make_shared<arrow::Decimal128Builder>(arrow::decimal128(f.precision, f.scale), arrow::default_memory_pool());
	case MF_DATETIME2:
	case MF_TIMESTAMP2:
	case MF_DATE: return std::make_shared<arrow::TimestampBuilder>(arrow::timestamp(arrow::TimeUnit::MICRO), arrow::default_memory_pool());
	case MF_TIME2: return std::make_shared<arrow::NumericBuilder<arrow::Int64Type>>(arrow::default_memory_pool());
	case MF_STRING:
	case MF_VARCHAR:
	case MF_JSON: return std::make_shared<arrow::StringBuilder>(arrow::default_memory_pool());
	case MF_BLOB:
	default: return std::make_shared<arrow::BinaryBuilder>(arrow::default_memory_pool());
	}
}

int main(int argc, char **argv)
{
	const char *ibd_path = argc > 1 ? argv[1] : "evidence/mysql/poc_orders.ibd";
	const char *out_path = argc > 2 ? argv[2] : "mysql_cpp.parquet";
	size_t max_rows = 1000000;
	const char *schema_file = nullptr;
	const char *keyring_path = nullptr;
	for (int i = 3; i < argc; i++)
	{
		if (strncmp(argv[i], "--rows=", 7) == 0) max_rows = strtoull(argv[i] + 7, nullptr, 10);
		else if (strncmp(argv[i], "--schema=", 9) == 0) schema_file = argv[i] + 9;
		else if (strncmp(argv[i], "--keyring=", 10) == 0) keyring_path = argv[i] + 10;
	}
	const size_t batch = 1 << 20;

	double t0 = now_s();

	int fd = open(ibd_path, O_RDONLY);
	if (fd < 0)
	{
		fprintf(stderr, "open ibd: %s\n", ibd_path);
		return 1;
	}
	struct stat st;
	fstat(fd, &st);
	size_t map_len = (size_t)st.st_size;
	uint8_t *map = (uint8_t *)mmap(NULL, map_len, PROT_READ, MAP_PRIVATE, fd, 0);
	if (map == MAP_FAILED)
	{
		fprintf(stderr, "mmap fail\n");
		return 1;
	}

	/* TDE: 提供 --keyring 时先在内存解密全部页(含 SDI 页), 后续布局/行解析走明文 */
	std::vector<uint8_t> plain_owner;
	if (keyring_path)
	{
		uint8_t mk[32];
		if (!tde::master_key_from_keyring(keyring_path, mk))
		{
			fprintf(stderr, "keyring master key parse failed: %s\n", keyring_path);
			return 1;
		}
		tde::TableKeys K;
		if (!tde::tablespace_keys_from_page0(map, map_len, mk, &K))
		{
			fprintf(stderr, "tablespace keys (lCC) parse failed\n");
			return 1;
		}
		size_t np = map_len / 16384U;
		uint8_t *plain = NULL;
		if (np * 16384U != map_len)
		{
			fprintf(stderr, "ibd size not page aligned\n");
			return 1;
		}
		plain_owner.resize(map_len);
		plain = plain_owner.data();
		double t_dec = now_s();
		for (size_t i = 0; i < np; i++)
			tde::decrypt_page(map + i * 16384U, plain + i * 16384U, K);
		fprintf(stderr, "[tde] %zu pages decrypted in %.3fs\n", np, now_s() - t_dec);
		munmap(map, map_len);
		map = plain;
	}

	MysqlLayout L;
	memset(&L, 0, sizeof(L));
	int layout_rc = 0;
	// 备注：版本差异分派——表定义来源决定布局构建路径：
	// 备注：  8.0+（含 8.4）：SDI 页内嵌 JSON 表定义，自动解析（mysql_layout_from_ibd）
	// 备注：  5.6/5.7      ：无 SDI（表定义在 .frm），必须 --schema= 显式传入
	// 备注：                （布局 = PK + DB_TRX_ID 6B + DB_ROLL_PTR 7B + 其余列，与 SDI 一致）
	// 备注：              若传 --schema 则优先 schema 路径；否则尝试 SDI（8.0+）
	if (schema_file)
		layout_rc = mysql_layout_from_schema_file(schema_file, &L);
	else
		layout_rc = mysql_layout_from_ibd(map, map_len, &L);
	if (layout_rc != 0)
	{
		fprintf(stderr, "%s\n", schema_file ? "schema layout parse failed" : "SDI layout parse failed");
		return 1;
	}
	double t_layout = now_s();
	fprintf(stderr, "[layout] %d fields, %d nullable, pk=%d\n",
	        L.n_fields, L.n_nullable, L.n_pk);

	std::vector<std::shared_ptr<arrow::Field>> fields;
	fields.reserve(L.n_fields);
	std::vector<uint16_t> vis_cols; /* 物理列 → 可见输出列映射（跳过 sys） */
	for (uint16_t i = 0; i < L.n_fields; i++)
	{
		if (L.fields[i].sys)
			continue;
		vis_cols.push_back(i);
		fields.push_back(arrow_field(L.fields[i]));
	}
	std::shared_ptr<arrow::Schema> schema = arrow::schema(fields);

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
	auto writer_result = parquet::arrow::FileWriter::Open(
	    *schema, arrow::default_memory_pool(), *ofs_result, writer_props, arrow_props);
	if (!writer_result.ok())
	{
		fprintf(stderr, "writer: %s\n", writer_result.status().ToString().c_str());
		return 1;
	}

	MysqlCur cur = {};
	cur.fd = -1;
	if (keyring_path)
	{
		cur.map = map;
		cur.map_len = map_len;
		cur.plain = 1; /* 明文缓冲由本进程所有, 不 mmap/munmap */
	}
	size_t n_fields = L.n_fields;
	std::vector<MysqlCell> cells(n_fields * batch);
	std::vector<char> strbuf((size_t)512 * 1024 * 1024);
	size_t strbuf_used = 0;
	size_t total = 0;
	uint64_t leaf_pages = 0, nonleaf_pages = 0, other_pages = 0;
	double t_parse_sum = 0, t_arrays_sum = 0, t_write_sum = 0;

	for (;;)
	{
		double t_b0 = now_s();
		size_t want = (max_rows - total < batch) ? (max_rows - total) : batch;
		if (want == 0)
			break;
		strbuf_used = 0;
		size_t n = mysql_parse_pages_range(ibd_path, &L, cells.data(), n_fields,
		                                   want, &cur, strbuf.data(), strbuf.size(),
		                                   &strbuf_used, &leaf_pages, &nonleaf_pages,
		                                   &other_pages);
		double t_parse = now_s();
		if (n == 0)
			break;
		total += n;

		std::vector<std::shared_ptr<arrow::ArrayBuilder>> builders;
		builders.reserve(vis_cols.size());
		for (size_t ci = 0; ci < vis_cols.size(); ci++)
			builders.push_back(make_builder(L.fields[vis_cols[ci]]));

		for (size_t r = 0; r < n; r++)
		{
			for (size_t ci = 0; ci < vis_cols.size(); ci++)
			{
				const MysqlCell &cell = cells[r * n_fields + vis_cols[ci]];
				auto &b = builders[ci];
				if (cell.kind == 0)
				{
					b->AppendNull();
					continue;
				}
				switch (L.fields[vis_cols[ci]].mtype)
				{
				case MF_INT:
					if (cell.kind == 3) /* ENUM/SET → 字符串 */
						((arrow::StringBuilder *)b.get())->Append(strbuf.data() + cell.off, (int32_t)cell.len);
					else if (L.fields[vis_cols[ci]].is_bool)
						((arrow::BooleanBuilder *)b.get())->Append(cell.i64 != 0);
					else if (L.fields[vis_cols[ci]].is_unsigned)
						((arrow::NumericBuilder<arrow::UInt64Type> *)b.get())->Append((uint64_t)cell.i64);
					else
						((arrow::NumericBuilder<arrow::Int64Type> *)b.get())->Append(cell.i64);
					break;
				case MF_FLOAT:
					((arrow::NumericBuilder<arrow::FloatType> *)b.get())->Append((float)cell.f64);
					break;
				case MF_DOUBLE:
					((arrow::NumericBuilder<arrow::DoubleType> *)b.get())->Append(cell.f64);
					break;
				case MF_DECIMAL:
					((arrow::Decimal128Builder *)b.get())->Append(arrow::Decimal128(cell.i64 < 0 ? -1 : 0, (uint64_t)cell.i64));
					break;
				case MF_DATETIME2:
				case MF_TIMESTAMP2:
				case MF_DATE:
					((arrow::TimestampBuilder *)b.get())->Append(cell.i64);
					break;
				case MF_TIME2:
					((arrow::NumericBuilder<arrow::Int64Type> *)b.get())->Append(cell.i64);
					break;
				case MF_STRING:
				case MF_VARCHAR:
				case MF_JSON:
					((arrow::StringBuilder *)b.get())->Append(strbuf.data() + cell.off, (int32_t)cell.len);
					break;
				case MF_BLOB:
				default:
					((arrow::BinaryBuilder *)b.get())->Append(strbuf.data() + cell.off, (int32_t)cell.len);
					break;
				}
			}
		}
		double t_arrays = now_s();

		std::vector<std::shared_ptr<arrow::Array>> arrays;
		arrays.reserve(n_fields);
		for (auto &b : builders)
		{
			std::shared_ptr<arrow::Array> arr;
			b->Finish(&arr);
			arrays.push_back(arr);
		}
		auto table = arrow::Table::Make(schema, arrays, n);
		auto status_w = (*writer_result)->WriteTable(*table, batch);
		if (!status_w.ok())
		{
			fprintf(stderr, "write: %s\n", status_w.ToString().c_str());
			return 1;
		}
		double t_done = now_s();

		t_parse_sum += t_parse - t_b0;
		t_arrays_sum += t_arrays - t_parse;
		t_write_sum += t_done - t_arrays;
		if (total >= max_rows)
			break;
	}
	(*writer_result)->Close();
	mysql_parse_pages_close(&cur);
	mysql_layout_free(&L);
	if (!keyring_path)
		munmap(map, map_len); /* 加密模式下 map 为内部明文缓冲, 无需/unable munmap */
	close(fd);
	double t_final = now_s();

	printf("{\n");
	printf("  \"rows\": %zu,\n", total);
	printf("  \"layout_seconds\": %.4f,\n", t_layout - t0);
	printf("  \"parse_seconds\": %.4f,\n", t_parse_sum);
	printf("  \"arrays_seconds\": %.4f,\n", t_arrays_sum);
	printf("  \"write_seconds\": %.4f,\n", t_write_sum);
	printf("  \"total_seconds\": %.4f,\n", t_final - t0);
	printf("  \"throughput_rows_per_second\": %.2f,\n",
	       (double)total / (t_final - t0));
	printf("  \"leaf_pages\": %llu,\n", (unsigned long long)leaf_pages);
	printf("  \"nonleaf_pages\": %llu,\n", (unsigned long long)nonleaf_pages);
	printf("  \"other_pages\": %llu\n", (unsigned long long)other_pages);
	printf("}\n");
	return 0;
}
