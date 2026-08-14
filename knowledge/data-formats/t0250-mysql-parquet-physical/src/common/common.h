#pragma once
#include <arrow/api.h>
#include <parquet/arrow/writer.h>
#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace db2parquet {

struct ColSpec {
  std::string name;
  arrow::Type::type type;  // INT32/INT64/DECIMAL128/TIMESTAMP/STRING/BOOLEAN
  int32_t precision = 0;
  int32_t scale = 0;
};

struct Stats {
  int64_t rows = 0;
  double parse_seconds = 0;
  double arrays_seconds = 0;
  double write_seconds = 0;
  double total_seconds = 0;
  int64_t peak_rss_bytes = 0;
};

// 并发安全分批打印不支持；仅供 bench 脚本 grep 解析
void EmitJson(const std::string& tag, const Stats& st);

using BatchAppender = std::function<void(
    std::shared_ptr<arrow::RecordBatch>&,
    int64_t start, int64_t count)>;

}  // namespace db2parquet
