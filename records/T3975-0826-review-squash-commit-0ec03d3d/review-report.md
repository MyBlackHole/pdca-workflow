# Review Report — 提交 0ec03d3d【F-139】TLS 安全链路整合

- **任务**: T3975 · 2026-08-26 · 分支 `6.2.0.0/F/139`
- **基点**: `fe9d4364`..`0ec03d3d`（squash 自六源提交：TLS/mTLS 整合、rpc 开关上下文化、oss HTTPS 开关化/单测接入、tls-keygen SAN 修复）
- **方法**: 六路并行深审（code-review-checklist 清单 + secure-coding 注入 + Fowler 坏味基线），主 session 汇总双轴；`xmake test` 实证 **44/44 passed**
- **范围排除**: `third_party/openssl4`、`oss/vendor`（第三方代码）

## 总体判定

| 严重度 | 数量 |
|--------|------|
| CRITICAL | **4** |
| HIGH | **21** |
| MEDIUM | 40 |
| LOW | 45 |

**门禁判定：Blocking ≠ 0，不建议原样合入远程。** 4 个 CRITICAL 均为确定性功能损坏（详见下节）；HIGH 中 13 条为确定性资源破坏/协议破坏/fail-open，建议同批修复。测试全绿是因为现有用例未覆盖这些路径（Copy 场景、分片上传、短包注入、ARM 链接）。

---

## 一、CRITICAL（必须修复）

**[CRITICAL]** oss/cmd/request.go:299-300 — `SrcBucket` 连续赋值两次，第二行应为 `SrcObject` | x-oss-copy-source 解析后 SrcObject 恒空，CopyObject 全场景 NOT_FOUND，对象复制功能整体失效 | 第二行改 `ossRequest.SrcObject = ...`

**[CRITICAL]** oss/cmd/object.go:117 — `srcObject == srcObject` 恒真，条件退化为同桶即走"自复制"捷径 | 同桶不同对象复制触发 utils.go:81 panic("centent 文件不存在")，跨对象拷贝永不执行 | 改为 `srcObject == dstObject`

**[CRITICAL]** dmsbtex/xmake-arm.lua:8 — ARM 目标缺 `add_deps("tools"/"tls_cert")`，而 network.c 已引用 tls_cert/sec_resolve/hs_algorithm 符号 | shared 库默认允许未定义符号 → 编译通过、DM 加载 dmsbtex.so 时 undefined symbol 直接失败，aarch64 SBT 备份插件整体不可用且静默 | 补依赖或加 `-Wl,--no-undefined`

**[CRITICAL]** libs/tls_keygen.c:512→533 — `EVP_PKEY_free(req_pkey)` 后 533 行 `X509_set_pubkey(cert, req_pkey)` 复用已释放指针（up_ref 于悬空内存=UB） | 签发证书可能持有悬空公钥，产出损坏证书或崩溃；既有缺陷，但该工具是本次 mTLS 链路证书来源且本次修改了同函数体 | free 移至 533 行之后

## 二、HIGH（应随批修复，共 21 条）

### 安全 fail-open / 配置语义分裂（6）
- **[HIGH]** libs/rdb-config.c:56-72 — `parse_strict_int` 未查 `errno==ERANGE`，溢出截断为 -1 恰是 `sec_resolve_int` 未命中哨兵 → 溢出的安全开关配置掉层翻转结果 | 补 ERANGE 返回 -1
- **[HIGH]** libs/rdb-config.c:264-268 — `sec_resolve_int` env 层 `atoi` 脏值 fail-open（`RPC_TLS_ENABLE=abc` → 0 关闭 TLS 且短路后续层），与 sec_resolve_bool 的 fail-closed 分裂 | env 层复用严格解析
- **[HIGH]** libs/tls_cert.c:277-295 — crl.pem 存在但解析失败仅打日志继续，吊销检查静默失效，违背注释声明的 fail-closed | CRL 存在但加载失败应视为 profile 初始化失败
- **[HIGH]** libs/tls_keygen.c:206-214,323-330 — 私钥先 `fopen("w")`(0666&~umask) 后 chmod 0600，权限窗口内其他本地用户可读；SM2 路径使暴露面翻倍 | 改 `open(...,0600)`+fdopen
- **[HIGH]** dmsbtex/sbt.c:789 — `--mtls-enabled` 用 atoi，手误配置静默禁用 mTLS，注释声称 fail-closed 与实现不符 | strtol 全串校验
- **[HIGH]** rpc/rpc-main.cpp:427-439（main.cpp）— 显式配置 mTLS 但证书加载失败仅 WarningLog 继续，服务实质不可用难察觉 | ErrorLog + 拒绝启动

### 资源破坏（7）
- **[HIGH]** rpc/rpc.cpp:1310,1362-1363 — 预置 `io.fd=-1` 后又 memset 清零 → 失败路径 `close(0)` 误关标准输入 | 删 memset，收尾加 fd>=0 保护
- **[HIGH]** rpc/rpc-io.cpp:189-196 — connect_server_session 失败已 close(fd) 但不重置 io->fd，调用方再 close 构成 double-close | cleanup 后置 io->fd=-1
- **[HIGH]** rpc/rpc-server.cpp:495-500,594-600,840-847 — MT_EXECUTE_NEW_CONN 无条件 goto exit__ 不清理 io/client，fail: 先置 -1 使 conn_free 内 close 变空操作 → 每次 NEW_CONN 泄漏一个 fd（+TLS_SSL） | exit__ 补清理
- **[HIGH]** rdbcomm/server.c:620-623 与 :341 — connection_create 内部 close 后 server_loop 再 close，双重关闭可误杀复用 fd 的无关连接 | 删 create 内 close
- **[HIGH]** libobk/lib/sbt/libobk.c:201-212 — 握手失败分支显式 release 后 error 标签再次 release，引用计数双重递减，并发下可能误清理他人 ctx | 删 ：201 显式 release
- **[HIGH]** oss/cmd/response.go:156-168,170-178 — ResponseGetObjectByChunk 两处 os.Open 无 Close，GET 热路径每次泄漏 fd | defer file.Close()
- **[HIGH]** oss/cmd/object.go:159-204 — (a)165 行 `if !exist` 恒假致目标目录永不创建；(b)循环内 4 处 OpenFile 无 Close | 无条件 MkdirAll + defer Close

### 协议/功能破坏（8）
- **[HIGH]** libobk/lib/logic/oracleCmdTbl.c:109,124,141,147 — 服务端拒绝分支发 4 字节帧或不回帧，客户端强制要求 204 字节 body → 所有显式拒绝场景 result 码丢失，T3956 可读化目标在此协议上失效；session_test 还固化了坏契约 | 拒绝也发全量 body，对齐 rdbcomm
- **[HIGH]** rpc/rpc-msg.c:48-84 — send 由 writev 退化为两次独立写、recv 由 readn 循环退化为单次读 | TCP 分片/TLS record 边界下大消息必现失败、两段写之间失败造成协议流错位 | 恢复循环读写满语义
- **[HIGH]** oss/cmd/request.go:275 — `Query.Has("partNumber=")` 恒 false（Has 匹配 key 名）| 分片上传分支永不可达，分片请求落为整体覆盖 | `Has("partNumber")`
- **[HIGH]** oss/cmd/object.go:291-301 — 开放式 Range `bytes=N-` 经 Atoi("") panic | 最常用的 `bytes=0-` 直接炸连接 | 空 rets[1] 视为末尾
- **[HIGH]** oss/cmd/response.go:154-155 — 先 WriteHeader(206) 后 Set Content-Range，header 快照已冻结 | 206 缺 RFC 必需头，续传客户端无法定位分片 | Set 移到 WriteHeader 前
- **[HIGH]** oss/cmd/response.go:525 — pathExists 丢 GConfig.StoreRoot 前缀，探测恒不存在 | MAX_BUCKET_NUM=30 上限永不生效，可无限建桶 | 补 StoreRoot 前缀
- **[HIGH]** oss/cmd/oss.go:166-179 — ListenAndServe 在 goroutine 内失败仅 log.Println，主流程阻塞信号等待 | 端口被占时进程假活不报错 | 错误传回 serverMain 即退出
- **[HIGH]** libs/tls_keygen.c:338,522 — serial 硬编码 1/2，违反 RFC 5280 唯一性，且与本提交新增 CRL 直接冲突（吊销一张=吊销全部） | BN_rand 随机 serial

### 出参契约（1）
- **[HIGH]** libs/tls_cert.c:771-857 — 握手失败时 result->code 保持初始 OK，调用方拿到矛盾状态无法区分失败原因；头文件注释引用的 ca_cn 字段在结构体中不存在 | 失败路径回填错误码；修注释或补字段

> 另有 HIGH：libs/rpc-net.c:76-98 响应短包（uiLEN∈[0,24)）时上层按 24 字节解析未初始化栈内存（时间源用于授权 key 校验）（存量，本次重构范围内建议顺带修）。计入上表后 HIGH 共 22 条中的 21 条独立条目，部分条目含双子问题。

## 三、MEDIUM 要点（40 条，摘要）

- **并发**：tls_cert ctx 热轮换无锁普通指针写（data race）；rpc-config 先发布新缓冲后回写字段；get_config_store 双缓冲仅 2 槽慢读者竞态
- **健壮性**：握手帧普遍缺长度校验（rpc-io/dmsbtex main）；ca_cn memcpy 不保证 NUL 终止即 %s；libobk _baseRecv remain 无上限校验（恶意 bytes 溢出面，存量）；rpc_get_time 无超时可永久挂死
- **设计一致性**：reload 收敛不彻底（mtls/算法/cert_dir 不随 reload 刷新、audit/auth 数据源 store 亦不刷新——规范轴目标落空）；hs_algorithm_from_name 未知名静默降级 DEFAULT 且两消费方语义相反；san_ext_valid 只验前缀不验值格式；chooseStr 形参顺序与优先级错位
- **测试**：libobk protocol_test 裸 assert 被 -DNDEBUG 剥离（release 下零有效）；tool_integration.c 未接入 xmake；oss https_test 读真实环境变量不可重复；dmsbtex 测试 include 实现源文件且用例顺序耦合全局状态
- **构建**：openssl4 patch.lua io.gsub 就地改写入库源码树且非幂等（harmony 二次构建重复追加块）；rpc-net 仍链入 tls_cert 致明文消费者拖 OpenSSL
- 其余：错误码语义混用、克隆代码（服务端握手×2、execute_shell_script×2、dm_server_handshake 拒绝分支×4）、panic-as-control-flow、pprof 绑 0.0.0.0、SIGTERM 未处理等

## 四、LOW（45 条）

命名/注释失配（timed_net_key.h 注释引用不存在参数、mtls 帮助文案复制残留、hs_err_str 命名误导）、include 卫生（重复包含、死 include、双定义宏）、缩进噪音（机械替换遗留 ×5 处）、死代码（rpc_recv_ssl 声明无定义、connect_server 无调用者、#undef 无来源、macosx 死分支）、版本口径混乱、build_oss.sh 缺末行换行、测试 fixture 私钥入库标注等。全文备查于各子审查记录。

## 五、五维总结论

| 维度 | 结论 |
|------|------|
| **设计模式** | 方向优秀：env 全局单例→显式 options+ctx、profile/slot 双算法抽象、四层配置解析模型、单一来源收敛（cfg_path.h/common.h HS_*/cert_file 常量）、fail-closed 单点化。扣分：出参契约残缺、错误码语义混杂、别名宏贯穿、收敛不彻底（reload 名实不符） |
| **代码可读性** | 高水准：WHY 型注释+任务号可追溯是亮点；扣分点为注释与签名脱节、ret 双语义、缩进噪音、帮助文案残留 |
| **代码可维护性** | 中上：常量收敛消除四模块漂移、接口签名替换干净；债务集中在五组克隆代码（bug 随克隆扩散已被证实）、死代码三组、测试脆弱性（顺序耦合/assert 剥离/未接入） |
| **代码可靠性** | 最大风险面：fd 生命周期管理回归（close(0)/double-close/NEW_CONN 泄漏/GET 热路径泄漏）、监听假活、SIGTERM 缺失、热轮换数据竞争；长跑与容器部署下必然显现 |
| **正确性** | 两个 CRITICAL 使 oss 对象复制确定性不可用；UAF/固定 serial/溢出截断哨兵值/单次读写退化均为确定性缺陷；基础 CRUD 主路径经实跑验证可用，44 条测试全绿但覆盖面存在系统性盲区（负路径/分片/Copy/ARM） |

## 六、Blocking 汇总与合并建议

- **Blocking = 4 CRITICAL + 13~14 确定性 HIGH ≈ 17~18 项**（安全 fail-open 类 6 条可视发布策略协商，其余建议必修）
- **建议**：暂缓 force push 远程；先修 4 CRITICAL（预计均小改动：一行赋值、一处条件、一处依赖声明、free 位置移动）与资源破坏类 HIGH，再补负路径测试（短包注入、Copy 场景、Range 边界），随后复审
- **规范轴结论**：六源提交的声明目标基本达成（开关上下文化运行期零残留、SAN 修复落地、xmake test 接入、HTTPS 默认 HTTP 保持 fail-closed），唯"配置重载重新解析"一条名实不符需修正实现或文档
