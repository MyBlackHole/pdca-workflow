# Parquet 文件物理结构 & 读写流程

## 范围
- Parquet 二进制布局：Magic bytes、Footer 元数据、Row Group / Column Chunk / Page 三层结构
- 元数据格式：FileMetaData、RowGroupMetaData、ColumnChunkMetaData、PageHeader
- Dremel 编码原理：Repetition Level 和 Definition Level 如何编码嵌套数据
- 完整读写生命周期：写入（编码→压缩→写盘）到读取（读盘→解压→解码）的全链路
- ASCII 图表展示各层级关系
