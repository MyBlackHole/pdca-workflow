#include "common.h"

#include <arrow/array/array_primitive.h>
#include <arrow/array/builder_decimal.h>
#include <arrow/array/builder_primitive.h>
#include <arrow/buffer.h>
#include <arrow/io/file.h>
#include <arrow/table.h>
#include <parquet/arrow/writer.h>
#include <parquet/properties.h>

#include <unistd.h>
#include <cstring>
#include <stdexcept>

namespace db2parquet {

std::shared_ptr<arrow::DataType> ArrowTypeOf(const ColSpec& s) {
  using arrow::decimal128, arrow::timestamp, arrow::utf8, arrow::boolean;
  using arrow::int32, arrow::int64;
  switch (s.type) {
    case arrow::Type::INT32: return int32();
    case arrow::Type::INT64: return int64();
    case arrow::Type::DECIMAL128: return decimal128(s.precision, s.scale);
    case arrow::Type::TIMESTAMP: return timestamp(arrow::TimeUnit::NANO);
    case arrow::Type::STRING: return utf8();
    case arrow::Type::BOOL: return boolean();
    default: throw std::runtime_error("unsupported column type");
  }
}

arrow::Result<std::shared_ptr<arrow::Schema>> MakeSchema(const std::vector<ColSpec>& cols) {
  std::vector<std::shared_ptr<arrow::Field>> fields;
  fields.reserve(cols.size());
  for (const auto& c : cols)
    fields.push_back(arrow::field(c.name, ArrowTypeOf(c)));
  return arrow::schema(fields);
}

// 通用写 Parquet 管道：接收一个"按需填充 RecordBatch 的 appender"，
// 分 batch 写出，统计指标并返回。
arrow::Result<Stats> WriteParquet(
    const std::string& path, const std::vector<ColSpec>& cols,
    int64_t total_rows, int64_t batch_size,
    BatchAppender& appender) {
  Stats st;
  ARROW_ASSIGN_OR_RESULT(auto schema, MakeSchema(cols));
  ARROW_ASSIGN_OR_RESULT(auto file, arrow::io::FileOutputStream::Open(path));

  parquet::WriterProperties::Builder builder;
  builder.compression(parquet::Compression::ZSTD);
  builder.enable_dictionary();
  ARROW_ASSIGN_OR_RESULT(auto props, parquet::WriterProperties::Builder::Build(builder));
  auto arrow_props = parquet::ArrowWriterProperties::Builder().coerce_timestamps(arrow::TimeUnit::NANO)->build();

  ARROW_ASSIGN_OR_RESULT(auto writer,
      parquet::arrow::FileWriter::Open(*schema, file, props, arrow_props));

  auto t0 = std::chrono::steady_clock::now();
  int64_t written = 0;
  while (written < total_rows) {
    int64_t n = std::min(batch_size, total_rows - written);
    std::shared_ptr<arrow::RecordBatch> batch;
    appender(batch, written, n);
    ARROW_RETURN_NOT_OK(writer->WriteRecordBatch(*batch));
    written += n;
  }
  ARROW_RETURN_NOT_OK(writer->Close());
  auto t1 = std::chrono::steady_clock::now();
  st.write_seconds = std::chrono::duration<double>(t1 - t0).count();

  // RSS
  struct rusage ru;
  if (getrusage(RUSAGE_SELF, &ru) == 0)
    st.peak_rss_bytes = ru.ru_maxrss * 1024;

  st.total_seconds = st.parse_seconds + st.arrays_seconds + st.write_seconds;
  return st;
}

// 打印 JSON 指标（与 T0163 pgbin 同构，供 bench 脚本解析）
void EmitJson(const std::string& tag, const Stats& st) {
  printf("{\"tag\":\"%s\",\"rows\":%lld,\"parse_seconds\":%.6f,"
         "\"arrays_seconds\":%.6f,\"write_seconds\":%.6f,"
         "\"total_seconds\":%.6f,\"peak_rss_bytes\":%lld}\n",
         tag.c_str(), (long long)st.rows, st.parse_seconds, st.arrays_seconds,
         st.write_seconds, st.total_seconds, (long long)st.peak_rss_bytes);
}

}  // namespace db2parquet