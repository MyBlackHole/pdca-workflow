# Review Report 附录 — 分模块逐条明细（T3975）

> 本附录收录主报告中 MEDIUM/LOW 级发现的完整明细（严重度 | 定位 | 问题 | 影响 | 建议），CRITICAL/HIGH 已在主报告全文列出。来源：六路并行子审查记录。

## A. libs TLS 工具族（C1/H4/M6/L8）

**[MEDIUM]** libs/tls_cert.c:224-231 — `safe_strcpy` dstsz==0 时 `dstsz-1` 无符号回绕 SIZE_MAX，条件恒真致全量 memcpy | 当前调用点不可达，通用辅助埋雷 | 开头加 `if (!dst || dstsz == 0) return;`
**[MEDIUM]** libs/tls_cert.c:139,160-163 — pick_ed25519_set：(a) ca_in 短于后缀时指针下溢越界读；(b) 长度条件不满足时 fb_cert/fb_key 残留 CA 文件名 | 健壮性缺陷，重构即踩雷 | 先判长度再比较；失败 goto keep_prefixed
**[MEDIUM]** libs/tls_cert.c:196-218 — verify 回调按 issuer CN 字符串比对限定单级 CA 链，中间 CA 整链拒绝；CN 匹配弱身份绑定 | 两级链部署即全断 | 仅 depth==0 校验；改 AKI keyid 绑定
**[MEDIUM]** libs/tls_cert.c:916,926 — tls_cert_ctx_reload 无锁普通指针写 slot->ssl_ctx，与并发握手构成 data race（C11 UB） | reload 期新连接可能读到撕裂指针 | mutex 或 _Atomic
**[MEDIUM]** libs/tls_cert.c:561-599 — 客户端 ctx 缓存 miss 时持全局锁做磁盘 IO 构建 SSL_CTX，阻塞所有线程 acquire | 首连慢放大为全局停顿；容量满错误码语义不符 | 锁外构建锁内插入 double-check
**[MEDIUM]** libs/tls_keygen.c:1230-1231 — CA 证书拷贝 fwrite 返回值未查、fread 不分错误/EOF | 磁盘满产出截断 CA 副本，故障延迟到握手期 | 检查返回值失败即删副本报错
**[LOW]** libs/tls_keygen.c:1471-1484 — inspect 自动识别 fgets 失败路径 fp 未 fclose | fd 泄漏（单次 CLI） | 单一出口 fclose
**[LOW]** libs/tls_keygen.c:340,524 — days 无校验，`days*86400` int 溢出、负值产过期证书 | 运维误输入 | 校验 [1,36500] 用 long
**[LOW]** libs/tls_cert.c:522,580,653 — OOM 返回 INVALID_PARAM、缓存满返回 SSL_CREATE，语义混用 | 排障误导 | 引入 NOMEM/CAPACITY 错误码
**[LOW]** libs/tls_cert.c:630,665-668,683 — init_server ret 双语义复用，首 profile 失败原因被吞 | 排障困难 | 分离最后错误变量
**[LOW]** libs/timed_net_key.h:11 vs .c:12-16 — 注释称 tls_cfg 可 NULL 但签名无此参数；strcpy(output,"noauth") 无长度形参 | 契约脆弱 | 修注释；加 out_sz 改 snprintf
**[LOW]** libs/tls_keygen.c:344-350 — create_ca 中 X509_NAME_new 无 NULL 检查、add_entry/add_ext 返回值未查 | OOM 解引用、扩展静默缺失 | 补齐检查
**[LOW]** libs/tls_cert.h:24-31 vs .c:44 — TLS_SSL 称不透明句柄却暴露成员；ssl_free 声明悬置 .c 中部 | 封装名不副实 | 前置声明，定义移入 .c
**[LOW]** libs/tls_keygen.c:1513 — mtls 子命令帮助文案复制粘贴遗留"Output files..." | 用户误导 | 删除该行
**[LOW]** libs/tests/certs/*.key — 测试私钥入库，命名与生产目录同名易混淆 | fixture 标注 fixture-only，.gitignore 防误拷

## B. libs 基础层（H3/M6/L9）

HIGH 三条见主报告（parse_strict_int ERANGE、rpc-net 短包、sec_resolve_int env fail-open）。
**[MEDIUM]** libs/timed_net_key.h:10-11 vs .c:9-31 — 注释与实现矛盾（声称不做 env/config 查询但 key_is_enabled 实际查询）；TLS 路径删除后永远明文连接 | 契约无法从接口表达 | 修注释或加 cfg 参数
**[MEDIUM]** libs/hs_algorithm.c:24-31 — 未知名静默返回 DEFAULT(0)，rdbcommd-main.c:352 与 rdbcomm-main.c:624 消费语义相反 | 客户端配错名无报错静默降级 | 出参+错误码
**[MEDIUM]** libs/common.c:339-369 — san_ext_valid 不验值格式（"IP:not-an-ip" 通过） | 畸形 SAN 穿透写入证书 | DNS 验字符集、IP 用 inet_pton 回验
**[MEDIUM]** libs/rdb-config.c:165-194 — get_config_store 双缓冲仅 2 槽，慢读者跨两次 reload 被重写；sec_resolve 多层调用可能跨 reload 取不一致快照 | 低概率混合读 | 代际计数或文档标注边界
**[MEDIUM]** libs/rpc-net.c:61-93 — recv 返回 0（EOF）落入 nread<1 分支依赖陈旧 errno，EAGAIN 时 continue 死循环烧 CPU | 非阻塞 socket 断连挂死 | nread==0 直接 break
**[LOW]** libs/xmake.lua:151-161 — rpc-net 仍 add_deps("tls_cert") 但已无 TLS 引用 | 明文消费者拖 OpenSSL | 移除依赖
**[LOW]** libs/rdb-config.c:196-210 — show_config offset 超 len 后负转 size_t 越界写（存量公开 API） | clamp offset
**[LOW]** libs/rdb-config.c:291-303 — sec_parse_strict_bool(NULL/"") 返回成功但不写 *out | 显式 *out=0 或三态
**[LOW]** libs/common.h:162-171 — 函数名别名宏全局词法污染 | alias 属性替代并设移除期限
**[LOW]** libs/hs_algorithm.c:62-67 — unknown 分支返回 _Thread_local 缓冲区生命周期未文档化；成功码走 err_str 表命名误导 | 注释固化；改名 hs_result_str
**[LOW]** libs/common.c:322-337 — cn_name_valid 无 64 字节上限（RFC ub-common-name）、单 "." 合法通过 | 补长度拒绝
**[LOW]** libs/rdb-config.h:5 — CONFIG_KV_MAX 256→1024 致 BSS ~786KB（4 倍）；g_truncated_warned 进程级一次性后续截断不再提示且绕过 logger | 知情确认；告警走 logger

## C. rpc（H5/M9/L7）

HIGH 五条见主报告（close(0)/double-close/NEW_CONN 泄漏/rpc-msg 单次读写/reload 失效）。
**[MEDIUM]** rpc/rpc-config.cpp:102-113 — 先发布 g_rpc_config 新缓冲后回写 audit/auth 字段，工作线程读新指针遇未写字段，数据竞争 | 切指针前完成全部写入
**[MEDIUM]** rpc/rpc-io.cpp:97-110 + rpc-server.cpp:237-239 — 握手帧未校验 bytes>=sizeof(msg_base_t/handshake_resp_t) 即强转 | 短帧读栈垃圾误判握手成功 | 按结构体大小拒绝 HS_ERR_FRAME
**[MEDIUM]** rpc/rpc-io.cpp:109-131 — ca_cn memcpy 整块不保证 NUL 终止即 %s 与传参 strlen 越界读 | 强制尾零
**[MEDIUM]** rpc/main.cpp:427-439 — mTLS 加载失败仅 WarningLog 半死常驻（fail-open 可观测性） | ErrorLog+拒启
**[MEDIUM]** rpc/rpc-server.cpp:48-50 — 新增成员 tls_ctx 构造函数未初始化，漏 Set 时 GetServerTlsCtx 返回野指针 | 默认成员初始化 nullptr
**[MEDIUM]** rpc/rpc-server.cpp:164-167 — sock_recvtimeout/create_thread 失败分支泄漏 client fd | 统一 shutdown+close
**[MEDIUM]** rpc/rpc-io.cpp:200-236 — rpc_get_time 自建 socket 无超时无 read_is_ready，服务端不回包永久挂死 | recv 前 read_is_ready(timeout)
**[MEDIUM]** rpc/rpc-client.cpp:964-975,2760-2771 — HANDSHAKE_RESP 防御只在两份克隆 execute_shell_script 里，其余数十客户端路径误把拒绝帧当业务响应 | 下沉 rpc_recv_io 专用错误码
**[MEDIUM]** rpc/rpc-io.cpp:63-73 — cleanup 后 io 处于"不可用不可检测"态（函数指针 NULL），restart 失败复用即崩 | cleanup 置 fd=-1 + 入口断言
**[LOW]** rpc/rpc-io.h:71-72 — rpc_recv_ssl/send_ssl 声明无定义 | 删除
**[LOW]** rpc/rpc-io.cpp:147-150,432,498 — connect_server/connect_server2 无调用者仍导出，rpc_connect_first_stage 空壳永不握手 | 删或 deprecated 转发 session 版
**[LOW]** rpc/rpc-server.cpp:284-396 — 服务端握手两分支约 40 行克隆 | 抽 handshake_upgrade_tls
**[LOW]** rpc/rpc.cpp:1713-1714 — do_remote_unlink if 缩进错乱（本次引入格式缺陷） | 修正
**[LOW]** rpc/rpc.cpp:1003,1059 — io 裸指针跨多句柄 API 存活，session 先释放则悬空（延续旧风险） | 注释固化生命周期契约
**[LOW]** rpc/rpc-config.cpp:183-201 — mtls 走 sec_resolve_bool 而 audit/auth 走宽松 int，脏配置行为分裂 | audit/auth 改 bool 严格解析
**[LOW]** rpc/rpc.cpp:996-999 — #undef rpc_send/rpc_recv 无对应 #define | 删除

## D. rdbcomm（H1/M3/L4）与 libobk（H2/M3/L5）

HIGH 三条见主报告（server double-close、libobk double-release、拒绝帧契约断裂）。
**[MEDIUM]** rdbcomm/rdbcommd-main.c:378-386 — init 失败且 mtls_enabled=0 组合静默继续；"no cert_dir serving plain only" 文案误导排障 | 补 WarningLog 并区分文案
**[MEDIUM]** rdbcomm/msg.c:41-52 — 两段循环写 n<=0 直接 return -1 无 errno 日志；TLS 下拆两 record 小包效率退化 | 补 ErrorLog 或保留 iovec
**[MEDIUM]** rdbcomm/tests/tool_integration.c — 新增 302 行未接入 rdbcomm/xmake.lua，死测试文件 | 增加 integration target 或移出
**[MEDIUM]** libobk/lib/logic/oracleCmdTbl.c:239 — _baseRecv remain=pHead->bytes 无上限校验即循环 recv 写入 malloc 缓冲 | 恶意 bytes 堆溢出面（存量） | 解析头后立即校验上限
**[MEDIUM]** libobk/lib/logic/oracleCmdTbl.c:96-142 — 拒绝响应构造 ×3 克隆 + hs_send_frame 双份 static 同构实现 | 提取 send_hs_reject 单点
**[MEDIUM]** libobk/test/protocol_test.c:26-31 — 裸 assert 被 release -DNDEBUG 剥离，测试恒通过零有效 | 移植 rdbcomm CHECK 宏
**[LOW]** libobk/lib/sbt/libobk.c:47-48 vs include/oracleCmdTbl.h:9-10 — SBT_MTLS_ENABLE_ENV 等宏双处定义，字符串漂移即 env 解析分裂 | include 单一来源
**[LOW]** libobk/include/protocol.h:47-48 — tls_ssl 重复 typedef（C99 违法）；openssl 头依赖扩散所有包含者 | 删重复 typedef，openssl 下沉 .c
**[LOW]** libobk/lib/sbt/sbtEnv.c:22-29 — size==0 时 buff[0]='\0' 越界 1 字节 | if (size>0) 再写
**[LOW]** libobk/lib/sbt/libobk.c:226-251 — catenate 一行 snprintf 重写为 20 行手工演算，复杂度纯增 | 回退 snprintf 版
**[LOW]** libobk/lib/logic/oracleCmdTbl.c:906-911 — mTLS 强制模式明文业务帧直接 break 不回错误码，rdbcomm 对应路径先应答 | 对齐先应答后断

## E. oss Go 与构建（C2/H7/M11/L8）

CRITICAL/HIGH 九条见主报告。
**[MEDIUM]** oss/cmd/tls.go:95-106 — chooseStr 形参顺序(cli,file,env,def)与实现优先级(cli>env>file>def)及注释错位，现有调用恰按位置传对 | 形参重排或传 struct
**[MEDIUM]** oss/cmd/tls.go:29-75 — parseRDBConfig 把一切 Open 错误当"文件缺失"回退默认；scanner.Err() 未查；声明返 error 恒 nil | 区分 IsNotExist，权限错误上抛
**[MEDIUM]** oss/cmd/utils.go:45-48 — GetFileCreateTime Stat 错误丢弃后解引用 nil panic；bucket.go:151 MkdirAll 错误未查链式放大 | Stat 错误上抛
**[MEDIUM]** oss/cmd/server.go:16,87,136,166 — 四 handler 用 panic 表达 400，recover 后空回复断连，与 GET 的 XML BAD_REQUEST 行为分裂 | 统一 ResponseError(BAD_REQUEST)
**[MEDIUM]** oss/cmd/oss.go:181-183 — 仅监听 SIGINT，systemd/container 的 SIGTERM 强杀，优雅关闭形同虚设 | 加 syscall.SIGTERM
**[MEDIUM]** oss/cmd/oss.go:149-153 — pprof 监听 0.0.0.0:6060 无认证 | 绑 127.0.0.1
**[MEDIUM]** oss/cmd/oss_https_test.go:115-196 — TestResolveCertPaths 读真实进程环境后才 t.Setenv 固化；fail-closed 用例隐式依赖宿主证书不存在，CI 翻转 | 开头统一 Setenv 固化 + TempDir
**[MEDIUM]** packages/o/openssl4/configure/patch.lua:6-24 — io.gsub 就地改写入库源码树（与只读注释矛盾）且非幂等（harmony 二次 install 重复追加块），gsub 无匹配不报错 | 标记检测+替换计数校验或 out-of-tree
**[MEDIUM]** oss/cmd/utils.go:202 — 前缀过滤 `Index(key,prefix)==1` 使 "xfoo" 命中 "foo" | 删除 ==1 分支
**[MEDIUM]** oss/cmd/request.go:235 — Has("multipart/form-data; boundary=(.+)") 恒 false，POST 表单上传恒 400（作者知情 TODO） | 改查 Content-Type 头
**[MEDIUM]** oss/test/xmake_go_test.sh:44-52 — trap 清理漏 INJECT_FILE，脚本中断后注入残留致 xmake test 永久 failed 且污染源码树 | trap 加 $INJECT_FILE
**[LOW]** oss/cmd/bucket.go:14-27 — yaml tag 写作 `yaml:":bucket"` 带前导冒号 | 标准 `yaml:"bucket"`
**[LOW]** oss/cmd/base.go:4-24 — VERSION 常量与 ldflags 注入双版本口径；MAX_OBJECT_FILE_SIZE 注释 5G 实为 5.4GiB | 统一口径
**[LOW]** oss/cmd/object.go:353 — AppendObject perm 传 ModeAppend|ModePerm，ModeAppend 非权限位 | 仅 ModePerm
**[LOW]** packages/o/openssl4/xmake.lua:186-190 — linux/cross 分支内 is_plat("macosx") 死代码 | 删除
**[LOW]** packages/o/openssl4/xmake.lua:214-224 — configure 缺 no-docs | 补充
**[LOW]** oss/cmd/oss.go:121-142 — Profile 块 f 三次遮蔽从不 Close、启动瞬间写 heap/goroutine profile 无诊断价值、StartCPUProfile 错误未查 | startProfile/stopProfile 成对
**[LOW]** oss/cmd/oss.go:157 + tls.go:149,205 — resolveTLSEnabled 与 buildServingTLS 各自重复 parseRDBConfig 读盘 | 结果复用
**[LOW]** oss/test/build_oss.sh:74 — 文件末缺换行符 | 补换行

## F. fs-backup 与 dmsbtex（C1/H1/M5/L5）

CRITICAL/HIGH 见主报告（ARM 缺依赖、mtls atoi fail-open）。
**[MEDIUM]** dmsbtex/main.c:252-253 — CMD_HANDSHAKE 未校验 host->bytes>=2 即 memcpy(&halg,...) | bytes==0/1 读 malloc 残留半随机 halg | 加长度守卫
**[MEDIUM]** dmsbtex/network.c:284-286 — 握手响应恒发 204 字节 body，与接收缓冲 char body[204] 零余量耦合，两端宏必须同步否则溢出 | 按实际长度发送
**[MEDIUM]** dmsbtex/network.c:211-296 — dm_server_handshake 四个拒绝分支 ~15 行块克隆 ×4 | 提取 dm_send_hs_resp 辅助函数
**[MEDIUM]** dmsbtex/test/session_test.c:29,254-284 — #include "../sbt.c" 使测试 TU 与库各持一份静态状态；AC-4b 正确性隐式依赖用例执行顺序（靠 AC-4a prepare 副作用重置全局 ctx） | 提供 ctx 注入/复位钩子消除顺序耦合
**[MEDIUM]** dmsbtex/network.c:306 — sbt_session_server_prepare 重复成功调用覆盖旧 ctx 无 cleanup，server 侧无对称 cleanup API | 入口幂等判断 + 补 server_cleanup
**[LOW]** fs-backup/fsdeamon/fs_kernel_sync.h:12 — sockfd 死字段仍在 backup_helper.cpp 5 处认真赋值 | 注释标废弃或移除
**[LOW]** dmsbtex/sbt.c:44,46 — 连续两行重复 #include "common.h" | 删一行
**[LOW]** dmsbtex/protocol.c:63-67 — 尾部追加 5 个 include 无任何使用，注释与实际位置不符；protocol.h include 位于中部 | 删死 include 收拢头部
**[LOW]** dmsbtex/sbt-config.conf:6-7 — 示例模板不被构建消费且缺必需键 --log-path/--host，照抄启动失败 | 更新为完整可用模板
**[LOW]** dmsbtex/network.h:37-39 — send_packet/recv_packet 单行超长声明不符 clang-format 风格 | 重排

---

*各条目均经子审查以 diff + 当前文件全文交叉验证；标注"存量"者为既有缺陷本次触及未修。*
