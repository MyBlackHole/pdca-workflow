# 移除C++异常处理并统一C风格API调用 — PRD

## 问题陈述

- **现状**: 项目以"C 风格 C++"为约定（style_check 强制无 class/virtual/lambda/std::thread），全局 `-fno-exceptions` 编译。但异常处理仍有一套完整残留链路：异常边界模块以 `-fexceptions` 单独编译，包装 4 个程序 main 入口与 9 个线程入口的 try/catch；构建系统（Makefile 五处、CMake 四处）、风格检查（豁免行 + 反向强制规则 + wrapper 行数规则）、编译图回归测试均为其保留特殊规则。同时约 48 个源文件存在 533 处 `::close`/`::open` 等 libc 系统调用的 `::` 全局作用域前缀写法，且全部代码包裹在 `namespace bs` 中（172 处），与项目的 C API 化方向不一致。
- **目标**: 源码零异常语法残留、零异常编译豁免；libc 调用统一为 C 风格直接调用；拆除 `namespace bs` 使符号按现有模块前缀命名习惯全局化；防回归规则同步收紧并新增。
- **差距**: 异常边界全链路未删除；`::` 前缀与 namespace 包裹未清理；style_check 缺少对两类风格的禁令规则。

## 解决方案

纯机械重构，零运行时行为变更（错误码/返回值/控制流语义不动）。四步实施，每步独立可验证、可回滚：

1. **删除异常边界全链路**：13 处包装调用点改回直呼 `*_impl/*_run` 函数 → 删除异常边界模块源文件 → 清理 Makefile 三处变量列表、特殊编译规则、测试链接行及 CMake 公共源列表、`-fexceptions` 豁免、observe 目标源列表、测试 target → style_check 删除豁免行、反向强制规则、work_pool wrapper 行数规则 → build_graph 回归脚本删除 `-fexceptions` 校验段。
2. **去 `::` 前缀**：533 处 libc/POSIX 调用去掉 `::` 全局作用域限定符。
3. **拆 namespace**：172 处 `namespace bs {}` 拆除（52 处嵌套匿名命名空间形态保留内层匿名 ns 以维持内部链接），4 处显式 `bs::` 限定符顺带清理；符号保持现名全局化。
4. **新增防回归规则**：style_check 收紧为无豁免禁止 try/catch/throw；新增禁止 `::` 前缀 libc 调用规则（放行 `std::`）。

异常逃逸兜底语义从"边界捕获+日志+_exit(125)"变为 std::terminate（用户已确认接受）：项目自身代码无 throw，唯一第三方依赖 lmdb 为纯 C 库不抛异常，零异常源成立。

## Seam 分析

### 测试接缝
- 静态风格契约由 style_check 脚本扫描全源码树验证（本次新增两条规则即本任务的"新测试"）。
- 行为回归由既有测试套件保障（集成 shell 测试 + 单元/集成 cpp 测试），本次不改任何被测行为，无需新增行为测试。
- 被删除的异常边界专项测试随模块一并移除。

### 声明的测试接缝
- seam: tests/style_check.sh -> src/
- seam: tests/build_graph_regression.sh -> Makefile

### 验收可测性
- 每个 AC 有明确 grep/构建/测试 pass-fail 信号（见下）
- 机械重构的边界条件（嵌套 ns、宏撞名）由双通道构建+全量测试覆盖
- 分层：静态规则检查（快）→ 双通道构建（中）→ 测试套件回归（慢）

## 用户故事

1. 作为维护者，我想要源码中不存在任何异常语法与异常编译豁免，以便 `-fno-exceptions` 承诺可被机器验证。
2. 作为维护者，我想要 libc 调用呈现 C 风格直呼形态且无 namespace 包裹，以便代码审计与 C API 迁移路径一致。
3. 作为 CI 守门人，我想要 style_check 自动拒绝两类风格的回归，以便约定不靠人工记忆维持。

## 实现决策

- 新增/修改模块：删除异常边界模块；其余仅机械改写，不新增/修改任何模块接口
- 接口定义：所有函数签名、类型布局、返回值语义不变；符号链接名变化仅源于 namespace 移除（mangle 变化），项目内自洽
- 技术澄清：`std::` 与匿名命名空间保留；符号不加统一前缀（保现名全局化）；main 直呼 impl 后原 125 退出码路径消失（不可达路径，等价删减）
- 架构决策：异常兜底语义定为 std::terminate（已终审确认，随任务记录，不单独立 ADR）

## 范围外

- 不将 .cpp 改写为纯 C 语言
- 不改写函数签名/错误码语义
- 不重构第三方 lmdb
- 不更新 CHANGELOG 历史记录（新条目归 Do 后处置决定）

## 备注

- 自查修复项（P6 已批准）：style_check 反向强制规则、work_pool wrapper 悬空规则、build_graph `-fexceptions` 校验段、Makefile/CMake 六处构建引用——遗漏任一处将导致构建或检查失败。

## 验收标准

- [ ] AC-1: 运行 `rg '(^|[^[:alnum:]_])(try|catch|throw)([^[:alnum:]_]|$)' src/` 输出 0 命中（含原豁免文件，文件已不存在）
- [ ] AC-2: 运行 `rg '::(close|open|read|write|dup|pipe|socket|bind|listen|accept|connect|recv|send|unlink|rename|stat|mkdir|fsync|fcntl|poll|epoll_|timerfd_)' src/` 输出 0 命中
- [ ] AC-3: 运行 `rg 'namespace bs' src/` 输出 0 命中
- [ ] AC-4: 运行 `rg 'exception_boundary' src/ Makefile CMakeLists.txt tests/style_check.sh tests/build_graph_regression.sh` 输出 0 命中
- [ ] AC-5: 在仓库根目录运行 `make`（build-make 通道）全量目标编译链接成功
- [ ] AC-6: CMake 通道配置+构建成功且不再含 `-fexceptions` 编译豁免
- [ ] AC-7: 运行 `bash tests/style_check.sh .` 通过，且其中包含新增的两条防回归规则（无豁免禁 try/catch/throw、禁 `::` 前缀 libc 调用）
- [ ] AC-8: 运行 `bash tests/build_graph_regression.sh` 通过
- [ ] AC-9: 运行既有测试套件（tests/ 下单元与集成测试）全部通过
