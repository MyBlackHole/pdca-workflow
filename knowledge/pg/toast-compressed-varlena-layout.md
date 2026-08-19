# PostgreSQL TOAST 压缩值物理格式（物理直读用）

## 结论
PG 的 TOAST 压缩 varlena（行内压缩与 external 压缩）均基于统一前缀布局，
物理直读解析时必须处理 4B 头与压缩方法位。

## 关键事实（PG9.6/11/18 实测一致）
1. **external 头（18B）**：`01 12` + rawsize@2(4B, 含 4B 头) +
   extinfo@6(4B, 低 30 位=extsize, 高 2 位=压缩方法) + valueid@10 +
   toastrelid@14。压缩判定 `extsize < rawsize-4`
   （=PG `VARATT_EXTERNAL_IS_COMPRESSED` 同式），非 extinfo 高位标志。
2. **压缩数据带 4B rawsize 前缀**（关键）：external 压缩 chunk 数据 =
   `4B(rawsize 低 30 位 | 高 2 位压缩方法)` + 压缩流。pglz/lz4 均如此，
   9.6/11 无 lz4、方法位恒 0。**解压须跳过前 4B**，目标尺寸=前缀低 30 位
   （=external 头 rawsize-4）。可前置校验 `(前缀 & 0x3FFFFFFF) == rawsize-4`。
3. **行内压缩（4B 头）无前缀**：varlena 头 va_tcinfo 低 30 位=原始大小
   （不含 4B 头），高 2 位=压缩方法；压缩流紧跟 8B（4B 头+4B tcinfo）。
4. **PG18 压缩方法 ID**（toast_compression.h）：TOAST_PGLZ=0、TOAST_LZ4=1。
   默认 default_toast_compression=pglz。
5. **LZ4 raw block 格式**（无 frame）：token 高 4 位=literal 长度
   （15 时 255 续字节扩展），低 4 位=match 长度+4（19 时 255 续字节扩展），
   offset 2B 小端，match 重叠复制逐字节（==offset 时等价 memset），末序列仅
   literal 无 offset。解压须做全边界检查 + 目标尺寸前置校验。

## 相邻陷阱
- **CLOG 复制**：`psql -c "INSERT; CHECKPOINT;"` 同串多语句共享一个隐式
  事务，CHECKPOINT 执行时 INSERT 未提交 → CLOG committed 位未落盘 → 物理
  直读全行 invisible。必须**单独连接执行 CHECKPOINT** 后再复制
  数据文件 + pg_xact（9.6 为 pg_clog）。
- 物理直读工具若假定固定列布局（如 id int8），测试表必须同构，否则列错位
  崩溃。

## 适用边界
- 仅物理直读（heap+toast+clog 文件）场景；逻辑复制/协议层无此前缀。
- 压缩方法位覆盖 pglz/lz4；更早版本（PG9.4-）布局需另行实测。
- 来源任务：T0308（research-report 完整版）；复核见 T0301。