# T3987 Dialogue Log

## Plan
- triage 确认 rdbcommd/aio-speedd fail-open，dm-ftp/sbt 已正确；写 prd.md（AC-1..AC-7）、声明的 5 个测试接缝；final_confirmation confirmed。

## Do
- rdbcommd：新增 server_boot.c（rdbcommd_tls_boot_prepare，双条件判据）+ 主流程 fail-closed 接入 + 单测。
- aio-speedd：新增 server_boot.cpp/.h（aio_speedd_tls_boot_prepare）+ main.cpp exit(EXIT_FAILURE) + 单测。
- dm-ftp/sbt：逻辑已正确，既有 session_test 含 bad cert_dir prepare fail，ALL PASS。
- libs：tls_cert_init_server 语义不变，由 boot prepare 间接覆盖。
- 验证：xmake build/run 全绿（含 warnings-as-errors）。

## Check
- 登记 6 条 test-output 证据 + convergence-map；validate-convergence valid。
- 双轴审查（含 secure-coding）Blocking=0；conclusion.md AC-1..AC-7 全 ✅；verdict confirmed。

## Act
- 沉淀知识 tls/server-boot-tls-failclosed.md；disposition=projected；journal 与 dialogue-log 归档。
