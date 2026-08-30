---
schema: pdca.asset/v1
id: ontology:domain/skill-secure-coding
name: secure-coding
summary: Review code for security vulnerabilities and implement security-critical logic.
description: Use when reviewing code for security vulnerabilities, implementing security-critical logic, or auditing C/C++/Rust/Go/Python code
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/triage
---

---
name: secure-coding
description: Use when reviewing code for security vulnerabilities, implementing security-critical logic, or auditing C/C++/Rust/Go/Python code
---

# Secure Coding (安全编码规范)

## C 安全
- **缓冲区溢出**: 使用 `snprintf`/`strlcpy` 而非 `sprintf`/`strcpy`；边界检查所有数组访问
- **UAF**: 指针置 NULL 后检查解引用；使用静态分析工具
- **格式字符串**: 永远不用用户输入作为 `printf` 格式串；用 `printf("%s", input)`
- **整数溢出**: 运算前检查范围；用 `__builtin_*_overflow` 或安全库

## C++ 安全
- **智能指针**: 用 `unique_ptr`/`shared_ptr` 替代裸 `new`/`delete`；避免 `shared_ptr` 循环引用
- **迭代器失效**: 修改容器后不再使用已有迭代器；用引用或索引替代
- **异常安全**: RAII 管理资源；析构函数不抛异常

## Rust 安全
- **Unsafe 块**: 每个 `unsafe` 必须有注释说明为何安全；优先用安全抽象
- **unwrap()**: 仅用于原型/测试；生产代码用 `?`/`match`/`unwrap_or`
- **transmute**: 尽量用 `safe_transmute` crate 或 `bytemuck`；必须验证布局兼容性

## Go 安全
- **SQL 注入**: 始终用参数化查询 `?` 占位符，禁止拼接 SQL
- **竞态**: 用 `-race` 检测；共享数据用 `sync.Mutex`/`atomic` 或 channel
- **Goroutine 泄漏**: 确保每个 `go` 有退出路径；用 `context.WithCancel` 管理生命周期

## Python 安全
- **注入**: 禁止 `eval()`/`exec()`/`pickle.loads()` 处理未信任输入
- **命令执行**: 用 `subprocess.run` 传列表而非字符串；禁止 `shell=True`
- **依赖**: `pip-audit` 或 `safety` 检查已知 CVE

## 通用规则
- 敏感信息不在日志中输出（密码、token、密钥）
- 认证与会话: JWT 签名验证、CSRF 保护、httpOnly Cookie
- 密钥管理: 环境变量或密钥管理服务，禁止硬编码

## 已知坑

- 审查勿只盯注入类漏洞；低置信的"疑似"问题勿当作已证实漏洞上报（误报破坏信任）。
