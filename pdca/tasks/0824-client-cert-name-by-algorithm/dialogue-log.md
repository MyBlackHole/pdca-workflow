## Do → Check 交接摘要 (2026-08-24)

- 实现：build_client_profile SM2 分支（cert_dir/<ca_cn>/sm2_ca.crt+sm2_host.*，仅前缀不下沉）；ED25519 分支原样保留；keygen sign -n 拷贝 CA 进自包含目录；rdb-config.h/Go 侧差异注释化处置。
- TDD：SM4 路径断言先红后绿；tls_cert_test 全绿含新增 sm2_prefixed_layout 集成用例。
- 实机：My_SM2_Root_CA 目录按新布局摆放后 aio-speed 国密握手成功返回 mtls-ok。
- evidence：fix-patch/verify-log/convergence-map；validate valid=true。

## Check 质询修正 (2026-08-24)

- 用户质询 build_client_profile 有问题 → 实测复现 ED25519 场景 CA/主机证书路径双双落空。
- 修正：ED25519 分支对称迁入 <ca_cn>/ 子目录前缀布局（先查 ed25519_* 前缀、缺失下沉无前缀）；fixture 7 处同步；identity_binding 用例等价迁移。
- 实机：SM2 ✅；ED25519 客户端 init ✅、握手被服务端 alert（协商行为，范围外，非回归）。

## Check 二轮质询修正 (2026-08-24)

- 用户澄清"整套"语义：ED25519 默认整套用 ed25519_ 前缀；不存在时整套下沉无前缀，禁止混套。
- 重构 pick_ed25519_{ca,cert,key} 三函数 → tls_cert_pick_ed25519_set 单点整套判定（锚=ed25519_ca.crt 存在性）；slot_create 改单调用。
- fixture 同步：helper 补 host 前缀两件；identity_binding/CRL 用例 host 文件改前缀名；reload fail-closed 破坏目标改 ed25519_host.crt。
- 全部测试与回归绿；SM2 实机 ✅；ED25519 服务端协商边界维持记录。
## Check → Act (2026-08-24) verdict=confirmed 已落盘
