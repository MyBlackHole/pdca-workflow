# T0329 Oracle 数据文件直读转换 → Parquet（PRD）

## 问题
延续 T0250/T0301 物理直读体系，新增 Oracle 平台：把 Oracle 数据文件（.dbf）中的表数据
直接转换为 Parquet。Oracle 块格式与 MySQL/PG 完全不同（block header/ITL/row directory/
row piece/压缩块/LOB），需从零逆向并实现解析器。

## 目标
- 版本：11g（11.2.0.2）与 12c+（19c 无官方免费容器镜像，以 21c 代表同代行格式）
- 范围：普通堆表数据 + 行删除/多 piece 行拼接 + LOB（BASICFILE/SECUREFILE）+ Basic/OLTP 压缩表
- 场景：数据库正常关闭后复制 .dbf 再转换（用户指定）
- 输出：Parquet（沿用 7 列 poc_orders 同构模式）

## 方案方向
1. **块格式**：block header(20B) + ITL(24B/entry) + data header(14B) + table directory(4B)
   + row directory(2B/slot，从块尾向块头) + row data + tail(4B, frmt+type+scn+seq+chkval)
2. **行格式**：row piece = flag(1B)+lock(1B)+col_count(1B)[+cluster_key(1B)] + 列数据。
   flag 位：K(0x80)/C(0x40)/H(0x20)/D=deleted(0x10)/F(0x08)/L(0x04)/P(0x02)/N(0x01)。
   列编码：1B 长度(0xFF=NULL) + 数据；VARCHAR2/NUMBER/DATE/CHAR 各类型解码。
3. **可见性（正常关闭场景）**：过滤 D(0x10) 已删除行；ITL/SCN 不用于可见性
   （正常关闭后无未提交事务，等效 MySQL delete-mark 语义）。
4. **多 piece 行**：F/L/P/N 位 + NRID(6B 指针)跨块链，需按 NRID 定位续 piece 拼接。
5. **表定位（关键取舍）**：不解析 SYSTEM 字典/segment header extent map；由用户提供
   "数据文件 + 段起始块"（SQL 辅助：`SELECT segment_name, header_file, header_block FROM dba_segments`），
   同 MySQL 5.6 的 --schema 模式。表段块从段起始按 extent 遍历（extent map 块跳过）。
6. **LOB**：LOB 索引 + LOB 数据块（chunk）遍历，BASICFILE/SECUREFILE 分别处理。
7. **压缩**：Basic 压缩块（KDH/HDO 头 + deflate 压缩单元）先行；OLTP 压缩跟进。
8. **TDE 表空间加密**：范围外（磁盘密文，需 wallet 密钥）。

## 验收标准
- [ ] AC-1: 11g 端到端：建表灌数（含 NULL/长行 4000B/迁移行）→ 正常关闭 → 复制 .dbf →
  orabin 转换 parquet → 与 SQL 全值逐字段对照 PASS
- [ ] AC-2: 21c 端到端：同 AC-1，覆盖 12c+ 行格式
- [ ] AC-3: 删除行过滤（flag D）与多 piece 行拼接（NRID 链）验证 PASS
- [ ] AC-4: LOB 列读取（BASICFILE + SECUREFILE）PASS
- [ ] AC-5: Basic 压缩表读取 PASS
- [ ] AC-6: 表定位契约（--segment 起始块 + --schema 列定义）文档化
- [ ] AC-7: research-report + evidence 登记 + 一致性验证工具

## 范围外
- TDE 表空间/列加密解密
- 数据字典（tab$/col$）物理解析（用户提供列定义）
- 索引/UNDO/SYSTEM/SYSAUX 段解析
- ASM、RAC、Exadata 存储
- 在线复制（非正常关闭）

## 备注
- 19c 无官方免费容器镜像（XE 仅 11g/18c/21c；Free 仅 23c），用 21c 代表 12c+ 行格式；
  如需真 19c 验证需商业镜像或远程实例（可后续补充）。
- 验证环境已就绪：容器 t0329-ora11（11g XE, 端口 1522）、t0329-ora21（21c, 端口 1523），
  users.dbf 表数据已灌 1000 行，块 dump 已验证行目录/行数据可见。
