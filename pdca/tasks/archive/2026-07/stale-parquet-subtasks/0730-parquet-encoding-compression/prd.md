# Parquet 编码 & 压缩深入

## 范围
- 编码原理详解：PLAIN、RLE、DELTA_BINARY_PACKED、DELTA_BYTE_ARRAY、DELTA_LENGTH_BYTE_ARRAY、BYTE_STREAM_SPLIT
- 各编码适用场景和数据特征分析
- 压缩算法基准对比：Snappy / ZSTD / Gzip / LZ4 / Brotli
- 压缩比 vs 速度 vs 解压速度 trade-off
- 编码+压缩的组合使用策略
- 引用权威 benchmark 数据
