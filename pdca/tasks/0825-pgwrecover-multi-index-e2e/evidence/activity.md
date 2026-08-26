# Do 阶段活动记录 — T3966 多索引集成测试可运行化

## 执行摘要
将 `test_multi_index_mixed` 从 `PGW_MULTI_DIR` 环境变量跳过改为基于 fixtures 的可运行集成测试。

## 关键步骤
1. 在 PG18.4 容器 `t0216-pg` 的 `multi_idx` 库重建样本：
   - 建表 `t(id,a,b,c,d,e)`（无主键/索引）→ CHECKPOINT（redo=C/8FB5F330）→ 拷基线 heap(rel 1946880)。
   - 建主键(btree pkey=1946886)+GIN(1946888)+GiST(1946889)+BRIN(1946890)+HASH(1946891)，INSERT 2500 + DELETE 227 → CHECKPOINT。
2. 停止 PG，拷 pg_control（打补丁 redo/minRecoveryPoint→C/8FB5F330）、WAL 段 8F 起共 26 段、最终 6 个 relfile。
3. 本地验证重放：`./build/pgwrecover` 输出 incremental_applied=14913，6 产物与 PG 最终态 verify_consistency 全部 PASS。
4. 压缩入库 tests/fixtures/（26 段 WAL + pg_control + 基线 heap + 6 期望态）；删除旧 relfilenode 不一致的 expected_multi_1946834/1946840..1946845。
5. 改写测试：默认从 fixtures 解压运行；PGW_MULTI_DIR 仅作可选输入源覆盖。
6. 全量回归 9 passed，构建 0 警告。

## 产物 digest（sha256）
- tests/pgwrecover/test_btree_e2e.py: 341774175801454e340bdf6a69ee768a69dde948c3328e01e3f431e828cbf97f (23709B)
- tests/fixtures/pg_control_multi.bin.bz2: d165efdced87f31c8c486e03896b8cd78997e0427eebb1deda8c44a8d4be24e5 (219B)
- tests/fixtures/baseline_multi_heap_1946880.bin.bz2: d3dda84eb03b9738d118eb2be78e246106900493c0ae07819ad60815134a8058 (14B)
- tests/fixtures/expected_multi_1946880.bin.bz2: 40f528b5e6609007807d17a1df8c17ff7b048294cb8939272b38764a073f5ea2 (39265B)
- tests/fixtures/expected_multi_1946886.bin.bz2: 43a1ba55aa219d2b28b5b80c553115fd415b072564066f6be0b637ab598d4cea (4421B)
- tests/fixtures/expected_multi_1946889.bin.bz2: e05be4ecf096480edeb3639dd09bd93d42078c30ddfd87882b6ccfad436f420c (14133B)
