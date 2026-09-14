---
name: code-review-checklist
description: Use when conducting code reviews, reviewing pull requests, or performing quality assurance on C, C++, Rust, Go, or Python code
---

# Code Review Checklist (代码审查检查清单)

## Overview

Systematic code review framework that ensures consistent coverage across all review dimensions. Apply the review flow, then check language-specific items. Never rely on ad-hoc bug hunting alone.

**Companion skills:** `secure-coding` (deep security review), `build-config` (build file correctness)

### 必须遵循 (MANDATORY)

**每次代码审查都必须按 Review Flow 进行，并使用下方的检查清单逐项检查。无例外。**

| 理性化借口 | 现实 |
|-----------|------|
| "代码很小，不需要清单" | 小代码经常有最严重的 bug (off-by-one、空指针、竞争条件)。清单只需 2 分钟。 |
| "我审查过很多次了，知道该看什么" | 经验丰富的审查者也会漏掉盲点。清单是安全网，不是培训工具。 |
| "先快速看一下，有问题再说" | 快速浏览只能发现明显问题，系统性盲点(错误路径、竞争条件、兼容性)会被跳过。 |
| "这个变更很简单" | 简单的变更往往假设调用方行为一致，而这个假设通常是错误的。 |
| "时间不够，先合并再修复" | 审查时没发现的问题，生产环境发现时修复成本高 10-100 倍。 |
| "其他审查者已经看过了" | 每个审查者关注点不同。系统性清单确保每个审查者覆盖全维度。 |

**跳过清单 = 跳过已知会漏掉的 bug。没有"这次特殊"这回事。**

## Review Flow

```
代码变更 → 先理解意图 (PR description / diff scope)
           ↓
        第一遍: 整体架构 & 设计 (5分钟)
           ↓
        第二遍: 逐行逐项检查 (按下方清单)
           ↓
        第三遍: 跨文件一致性 & 边界情况
           ↓
        撰写审查意见 (分类 + 严重度 + 建议)
```

---

## 通用审查维度 (所有语言)

### 正确性 (Correctness)
- [ ] 边界条件有正确处理吗？(空值、零、最大值、空集合)
- [ ] 数值运算有溢出/除零风险吗？
- [ ] 并发访问有竞态条件吗？
- [ ] 资源清理保证执行吗？(RAII / defer / finally)
- [ ] 错误路径有测试吗？(不是只有 happy path)
- [ ] 类型转换安全吗？(隐式转换、窄化转换)

### 安全性 (Security)
- [ ] 用户输入经过验证/转义了吗？
- [ ] 有命令注入/SQL注入/路径穿越风险吗？
- [ ] 敏感信息(密码、密钥、token)是否硬编码？
- [ ] 认证/授权检查是否在正确的层级？
- [ ] 加密实现是否使用了标准库而非自造？
- [ ] 详细审查 → 使用 `secure-coding` skill

### 性能 (Performance)
- [ ] 有无不必要的内存分配(循环内分配)？
- [ ] 有无不必要的拷贝(大对象传值)？
- [ ] 热点路径上有无低效算法(O(n²) 可优化为 O(n log n))？
- [ ] I/O 操作有无适当的缓冲/批量处理？
- [ ] 锁的粒度和范围合理吗？
- [ ] 有无明显的 N+1 查询或重复计算？

### 可维护性 (Maintainability)
- [ ] 命名清晰表达了意图吗？(函数名是动词、布尔变量是谓词)
- [ ] 函数/方法职责单一吗？(单一职责原则)
- [ ] 代码重复可以提取抽象吗？
- [ ] 魔术数字/字符串有命名常量吗？
- [ ] 复杂逻辑有注释说明 WHY 而非 WHAT 吗？
- [ ] 公共 API 有文档注释吗？

### 错误处理 (Error Handling)
- [ ] 所有外部调用(文件/I/O/网络/数据库)都有错误检查吗？
- [ ] 错误信息对用户友好且不泄露内部细节吗？
- [ ] 错误被吞没了吗？(空 catch / 忽略返回值 / `// TODO: handle error`)
- [ ] 资源在错误路径上正确释放了吗？
- [ ] 使用语言的惯用错误处理模式了吗？

### 测试 (Testing)
- [ ] 新代码有对应的单元测试吗？
- [ ] 测试覆盖了正常路径和异常路径吗？
- [ ] 测试是行为验证而非实现验证吗？(不测试私有实现细节)
- [ ] 测试可重复且不依赖外部状态吗？
- [ ] 测试命名清晰地说明了被测试的行为吗？

---

## 语言特定检查

### C

| 类别 | 检查项 |
|------|--------|
| 内存安全 | [ ] `malloc`/`calloc`/`realloc` 返回值检查了吗？ |
| 内存安全 | [ ] 数组/指针访问在边界内吗？(off-by-one 是最常见 bug) |
| 内存安全 | [ ] `free` 后指针置 NULL 了吗？(use-after-free 预防) |
| 缓冲区 | [ ] `strcpy`/`sprintf`/`gets`/`scanf("%s")` 等不安全函数被替换为 `strncpy`/`snprintf`/`fgets` 了吗？ |
| 缓冲区 | [ ] `strncpy`/`strncat` 结果是否确保 NULL 终止？ |
| 资源 | [ ] 文件描述符、互斥锁、socket 在所有路径上都关闭了吗？ |
| 指针 | [ ] 函数指针/回调的合法性有校验吗？ |
| 整数 | [ ] 整数运算有溢出检查吗？(特别是来自用户输入的大小计算) |
| 约定 | [ ] 头文件有 `#pragma once` 或 include guard 吗？ |
| 约定 | [ ] 全局变量有 `static` 限制作用域吗？(`static` within file) |

### C++

| 类别 | 检查项 |
|------|--------|
| 资源管理 | [ ] 使用 RAII (智能指针/容器) 而非手动 `new`/`delete` 吗？ |
| 资源管理 | [ ] 异常安全：异常抛出时资源正确释放了吗？ |
| 移动语义 | [ ] 大对象按值传递时提供了移动构造函数/赋值吗？ |
| 移动语义 | [ ] `std::move` 使用后原对象状态有注释说明吗？ |
| 模板 | [ ] 模板代码有关键字 `typename`/`template` 正确使用吗？ |
| 模板 | [ ] SFINAE / concept / requires 约束正确吗？ |
| 虚函数 | [ ] 基类析构函数是 `virtual` 吗？ |
| 虚函数 | [ ] `override` 关键字标记所有重写函数吗？ |
| 并发 | [ ] `std::mutex` 作用域最小化了吗？(使用 `std::lock_guard`/`std::scoped_lock`) |
| 并发 | [ ] 条件变量有 spurious wakeup 处理吗？ |
| STL | [ ] 迭代器使用时容器没有被修改吗？(迭代器失效) |
| STL | [ ] 引用/指针没有悬空吗？(局部变量地址返回) |

### Rust

| 类别 | 检查项 |
|------|--------|
| 所有权 | [ ] 借用检查器无法捕获的运行时借用规则违反了吗？(内部可变性: `RefCell`/`Mutex` 运行时 panic) |
| 所有权 | [ ] `unsafe` 代码块有安全注释说明不变式吗？ |
| 所有权 | [ ] `unsafe` 块最小化了吗？(能封装在 safe 抽象中吗？) |
| 错误处理 | [ ] 使用了 `Result<T, E>` 而非 `panic!`/`unwrap()`/`expect()` 处理可恢复错误吗？ |
| 错误处理 | [ ] 自定义错误类型实现了 `std::error::Error` 吗？ |
| 并发 | [ ] `Send`/`Sync` 的自动实现是否安全？(特殊成员) |
| 并发 | [ ] `Arc` 用于跨线程共享，`Rc` 仅用于单线程吗？ |
| 性能 | [ ] 热点路径有无不必要的 `clone()`？(考虑借用替代) |
| 性能 | [ ] `String` vs `&str` 选择是否合理？ |
| 异步 | [ ] 异步函数中避免阻塞调用了吗？(`std::thread::sleep` vs `tokio::time::sleep`) |
| 宏 | [ ] 声明宏(`macro_rules!`)/过程宏的参数处理有边缘情况吗？ |

### Go

| 类别 | 检查项 |
|------|--------|
| 错误处理 | [ ] 错误被检查了吗？(不会被 `_` 忽略) |
| 错误处理 | [ ] 错误适当地包装了上下文吗？(`fmt.Errorf("做某事: %w", err)`) |
| 并发 | [ ] goroutine 泄漏预防：有明确的退出机制吗？(channel close / context cancel) |
| 并发 | [ ] `sync.WaitGroup` 的 `Add` 在 goroutine 启动前调用吗？ |
| 并发 | [ ] `select` 中多个 channel 都关闭时的处理合理吗？(nil channel 不会被 select) |
| 接口 | [ ] 接口定义最小化了吗？(接受接口，返回结构体) |
| 接口 | [ ] 接口被定义在使用方而非实现方吗？ |
| 指针 | [ ] 指针接收者和值接收者的选择一致吗？ |
| 指针 | [ ] 切片/map 作为函数参数时的修改是否影响调用方？ |
| 资源 | [ ] `defer` 关闭资源，且不在循环中使用 `defer`？ |
| 资源 | [ ] `http.Response.Body` 在所有路径上都 `Close()` 了吗？ |
| 测试 | [ ] 表驱动测试(Table Driven Test)用于多场景了吗？ |

### Python

| 类别 | 检查项 |
|------|--------|
| 类型安全 | [ ] 函数签名有类型注解(type hints)吗？ |
| 类型安全 | [ ] 类型检查工具(mypy/pyright)能通过吗？ |
| 异常 | [ ] `except:` 裸异常被避免了？(应指定具体异常类型) |
| 异常 | [ ] `try` 块范围最小化了吗？(只包裹可能抛异常的代码) |
| 性能 | [ ] 热点路径上避免循环内属性查找了吗？(局部变量缓存) |
| 性能 | [ ] 列表推导式/生成器表达式替代了显式循环吗？(适当场景) |
| 资源 | [ ] 文件/socket/db 连接使用了 `with` 语句吗？ |
| 并发 | [ ] GIL 限制被正确理解了吗？(CPU 密集型用 `multiprocessing`, I/O 用 `asyncio`) |
| 并发 | [ ] 异步代码中避免 `time.sleep()`？(使用 `asyncio.sleep()`) |
| 可变性 | [ ] 可变默认参数被避免了？(`def f(x=[])` → `def f(x=None)`) |
| 导入 | [ ] 导入按标准分组了吗？(标准库 → 第三方 → 本地) |
| 测试 | [ ] pytest fixture 作用域合理吗？(function/class/module/session) |

---

## 严重度分类

| 等级 | 定义 | 行动要求 |
|------|------|----------|
| **CRITICAL** | 导致数据丢失/安全漏洞/生产宕机 | 必须修复才能合并 |
| **HIGH** | 确定性的错误行为/重大性能退化 | 应修复，可商议变通方案 |
| **MEDIUM** | 潜在 bug/可维护性问题/轻度性能问题 | 建议修复，可记录为后续技术债务 |
| **LOW** | 风格/命名/注释/代码组织 | 可修复，不 blocking |

---

## 审查意见格式

```
**文件:** path/to/file.rs:42-50
**严重度:** HIGH
**问题:** 此处 unwrap() 在输入非法时会 panic
**建议:** 使用 ? 运算符将错误传播给调用方处理
```

---

## 常见盲点 (Reviewers Often Miss)

| 盲点 | 为什么容易漏掉 |
|------|---------------|
| 错误路径的资源清理 | 审查者主要关注正常流程，忘记检查错误分支的资源释放 |
| 并发竞争条件 | 静态代码审查难以发现动态时序问题 |
| API 的前后向兼容性 | 修改公共 API 时未考虑已有调用方 |
| 分布式/跨服务的超时和重试 | 单服务审查容易忽略外部依赖的超时设置 |
| 空值/零值/空集合的一致性处理 | 一个函数的空值处理假设调用方也会空值检查 |
| 密码学误用 | 看起来正确但安全性不足(如 ECB 模式、不安全的随机数) |
| 整数溢出(非 C/C++ 也有) | 很多语言在大数场景下仍有溢出风险(Go/Python int 除外但转换时可能) |
| 配置默认值的安全影响 | 调试模式、宽松 CORS、完整错误信息泄露在生产环境的风险 |
| PR 描述和代码行为不一致 | 审查者假设描述正确，不会逐字验证每个变更点 |
| 删除/注释掉的代码 | 注释掉的代码块通常不被审查，但可能影响后续理解 |
| 跨语言/跨服务的契约变更 | 修改 API 返回格式时未检查所有消费方(前端/其他服务) |

---

## Pre-Review Self-Check (审查前自检)

开始审查前，先确认：

- [ ] 我理解这份 PR/变更的意图和背景了吗？(读了 description / ticket)
- [ ] 我知道这次变更的范围有多大？(哪些文件是核心改动，哪些是附带修改)
- [ ] 我准备好按清单逐项检查了吗？(不跳步骤、不凭感觉)
- [ ] 如果这是紧急修复，我是否仍然按流程审查了？(紧急≠跳过检查)

**如果以上任何一项回答"否"，先完成它再开始审查。**

---

## Red Flags — 审查中需要特别警惕

- 大量代码变更没有拆分审查(500+ 行 diff → 要求拆分)
- 没有对应测试的变更(bugfix 应该有回归测试)
- TODO/FIXME/HACK 遗留注释
- 注释和代码行为不一致(复制粘贴忘记改)
- "和之前一样" 的克隆代码(重复代码 bug 也会被克隆)
- `as any` / `unsafe` / `#pragma pack` 等绕过安全机制的关键字(审查其必要性)
- 徒有外表的变更：只改了命名没改逻辑(可能是不完整重构)
- 审查者感到困惑或直觉觉得不对 — 永远不要忽视 gut feeling

---

## 参考

- [SEI CERT Coding Standards](https://wiki.sei.cmu.edu/confluence/display/seccode/) — 各语言安全编码标准
- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/) — Web 安全审查
- [Google Code Review Guidelines](https://google.github.io/eng-practices/review/) — 工程实践
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) — Rust API 设计检查
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments) — Go 代码审查惯例
