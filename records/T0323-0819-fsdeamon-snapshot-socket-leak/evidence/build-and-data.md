# AC-4/AC-5/AC-6 验证

## AC-4: build 与测试
- xmake build：100% build ok（修改 files_meta.cpp/files_meta_mgr.cpp/files_meta.h 后重新编译通过）
- xmake test：nothing to test（项目无既有测试套件，B3 说明中注明限制）

## AC-5: 不影响快照正确性
- J1~J4 四次增量快照均返回 result=true，数据正确生成（bitmap/meta/trackup-list 完整）

## AC-6: 三路径释放正确
- SnapshotSync: m_FilesMeta_ver.CloseSession()（成功路径 ver 用完释放）
- SnapshotEnd: m_FilesMeta_bak.CloseSession()（成功路径 bak 用完释放）
- SnapshotFailed: ver+bak 均 CloseSession()（统一 error__ 出口）
- DEFAULT session（fd5/7/10 常驻 3 连接）不受影响，随对象析构释放
