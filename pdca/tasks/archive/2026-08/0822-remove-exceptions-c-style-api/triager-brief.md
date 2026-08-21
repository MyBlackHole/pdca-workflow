# Triage Brief — remove-exceptions-c-style-api

- **category**: enhancement
- **scenario_type**: development
- **summary**: 移除项目残留的 C++ 异常处理机制，并将 libc/POSIX 系统调用的 `::` 全局作用域前缀改为无前缀的 C 风格调用
- **current behavior**: 全局已 `-fno-exceptions` 编译；唯一异常残留是异常边界模块（以 `-fexceptions` 单独编译，包装 main 与线程入口的 try/catch），并在构建脚本与风格检查中留有豁免规则；约 48 个源文件中共 533 处 `::close`/`::open` 等 `::` 前缀系统调用
- **desired behavior**: 源代码零 try/catch/throw、无异常编译豁免；系统调用统一为 C 风格直接调用（如 close/open/read/write），风格检查规则同步更新
- **key interfaces**: 异常边界模块（线程入口/main 入口包装）；libc 系统调用封装层；风格检查脚本；构建配置
- **acceptance criteria**:
  - 运行风格检查脚本对 try/catch/throw 的扫描输出 0 处命中（含原豁免文件）
  - 运行 grep 扫描 src/ 中 `::close` 等 `::` 前缀 libc 调用输出 0 处命中
  - 运行完整构建（Makefile 与 CMake 双通道）全部目标编译链接成功且无 `-fexceptions` 豁免
  - 运行现有测试套件全部通过
- **out of scope**: 不改变运行时行为与错误码语义；不将 .cpp 改写为纯 C；不重构 namespace 结构（除非用户明确要求）
- **information gaps**: 异常边界模块是否整体删除；线程入口失败兜底策略如何替代；`::` 去前缀的范围界定（仅 libc 还是含 std::）
- **dedup results**: 活跃/归档 task 无重复；out-of-scope 知识库概念级检查无命中
- **recommended next steps**: Grill 澄清边界模块处置与去前缀范围后合成 PRD
