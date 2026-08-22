# Triage Brief — libobk-handshake-fix

- **category**: bug
- **scenario_type**: bugfix
- **summary**: 修复 libobk mTLS 握手客户端栈溢出与双端帧长度校验必败（T0355 C1/C2），并补真实 TLS 往返集成测试。
- **current behavior**: 客户端以 body 大小的缓冲区承接 header+body 总长读取（栈溢出）；客户端期望 body=175 字节而服务端发送 h.bytes=205，mTLS 升级成功路径必败；服务端从 buf[204] 发送 205 字节越界读。缺陷因缺少客户端↔服务端完整握手往返测试而未被发现。
- **desired behavior**: 帧长度由单一宏定义且双端共用；缓冲区按 header+body 总长分配；握手成功路径真实可达；新增 socketpair 级真实 TLS 升级往返用例且全绿。
- **key interfaces**: SBT 会话握手层——客户端协商函数与服务端握手应答函数（均需去 static 导出供测试）；握手响应体长度常量（protocol.h 单点定义）。
- **acceptance criteria**:
  - 运行 xmake build libobk_session_test 与 xmake test 得到构建成功且全部用例通过，含新增 mTLS 往返用例。
  - 运行新增往返用例得到双方会话读写函数切换为 TLS 实现的断言通过。
  - 运行 grep 检查握手路径源码得到长度常量宏为唯一来源、无 4+201/205 类字面量残留。
  - 运行 ASan 构建的往返用例得到无内存错误报告。
- **out of scope**: dmsbtex 同域代码（其校验为弹性范围无此缺陷）；M1/M3 等中低风险语义收敛项；证书管理本身。
- **information gaps**: 无关键缺口；最小失败诊断日志是否纳入范围待用户确认。
- **dedup results**: 父任务 T0355 为审查任务不改代码，本任务是其后继修复，无重复。
- **recommended next steps**: 确认 seam 与日志范围后合成 PRD 并终审。
