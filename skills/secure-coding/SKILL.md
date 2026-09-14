---
name: secure-coding
description: Use when reviewing code for security vulnerabilities, implementing security-critical logic, or auditing C/C++/Rust/Go/Python code
---

# Secure Coding (安全编码规范)

## Overview

Language-specific secure coding guidelines for C, C++, Rust, Go, and Python. Each section covers the most common security risks with unsafe vs safe code comparisons.

All Chinese annotations follow `// 备注:` format (see `code-comments` skill).

---

## C 安全

### 1. 缓冲区溢出

**风险**: `strcpy`, `strcat`, `sprintf`, `gets`, `scanf("%s")` 不检查缓冲区边界

```
// ❌ 不安全
char buf[64];
strcpy(buf, input);
gets(buf);
sprintf(buf, "%s", input);

// ✅ 安全 — 使用长度受限函数
char buf[64];
strncpy(buf, input, sizeof(buf) - 1);
buf[sizeof(buf) - 1] = '\0';
snprintf(buf, sizeof(buf), "%s", input);
```

### 2. 释放后使用 (Use-After-Free)

**风险**: 指针释放后未置空，继续使用

```
// ❌ 不安全
free(ptr);
// ... 其他代码 ...
ptr->field = value;  //  ptr 已释放

// ✅ 安全 — 释放后立即置空
free(ptr);
ptr = NULL;
```

### 3. 格式字符串漏洞

**风险**: 将用户输入直接作为格式化字符串参数

```
// ❌ 不安全 — 用户输入可能包含 %x %n 等
printf(user_input);
fprintf(log, user_input);

// ✅ 安全 — 固定格式字符串
printf("%s", user_input);
fprintf(log, "%s", user_input);
```

### 4. 整数溢出/回绕

**风险**: 整数运算超出范围，未做检查

```
// ❌ 不安全
size_t total = count * sizeof(element);
if (total > limit) { ... }

// ✅ 安全 — 乘法前检查溢出
if (count > 0 && SIZE_MAX / count < sizeof(element)) {
  // 处理溢出错误
  return ERROR_OVERFLOW;
}
size_t total = count * sizeof(element);
```

### 5. 不安全函数清单

| 不安全函数 | 安全替代 |
|-----------|---------|
| `gets()` | `fgets()` |
| `strcpy()` / `strcat()` | `strncpy()` / `strncat()` 或 `strlcpy()` / `strlcat()` |
| `sprintf()` | `snprintf()` |
| `vsprintf()` | `vsnprintf()` |
| `scanf()` / `sscanf()` | 使用字段宽度: `scanf("%63s", buf)` |
| `system()` | `execve()` 系列 |
| `mktemp()` | `mkstemp()` |

---

## C++ 安全

### 1. 智能指针误用

**风险**: 裸 `new`/`delete`、循环引用导致内存泄漏

```
// ❌ 不安全 — 裸指针 + 手动 delete
auto* obj = new MyClass();
delete obj;

// ✅ 安全 — 使用 unique_ptr / shared_ptr
auto obj = std::make_unique<MyClass>();
auto shared = std::make_shared<MyClass>();
```

### 2. 迭代器失效

**风险**: 修改容器后继续使用旧迭代器

```
// ❌ 不安全 — 插入元素后迭代器失效
std::vector<int> v = {1,2,3,4};
auto it = v.begin();
v.insert(v.begin(), 0);
v.erase(it);  //  it 已失效!

// ✅ 安全 — 从操作结果获取新迭代器
auto it = v.insert(v.begin(), 0);
v.erase(it);  // 使用 insert 返回的有效迭代器
```

### 3. 对象切片 (Object Slicing)

**风险**: 值传递基类时丢失派生类信息

```
// ❌ 不安全 — 按值传递导致切片
void process(Base b) { b.virtualMethod(); }
process(derivedObj);  // 调的是 Base::virtualMethod

// ✅ 安全 — 用引用或指针
void process(Base& b) { b.virtualMethod(); }
process(derivedObj);  // 正确调用派生类方法
```

### 4. 异常安全

```
// ❌ 不安全 — 异常时资源泄漏
void process() {
  auto* res = acquire_resource();
  // 如果此处抛出异常，资源未释放
  do_work(res);  // 可能抛异常
  release_resource(res);
}

// ✅ 安全 — RAII 包装
class ResourceGuard {
  Resource* res;
public:
  ResourceGuard() : res(acquire_resource()) {}
  ~ResourceGuard() { release_resource(res); }
};

void process() {
  ResourceGuard guard;  // 异常安全
  do_work(/* 不需要手动管理 */);
}
```

### 5. 虚析构函数

```
// ❌ 不安全 — 基类没有虚析构
class Base { ~Base(); };
class Derived : public Base { ~Derived(); };
Base* p = new Derived();
delete p;  // 未调用 Derived 析构函数

// ✅ 安全
class Base { virtual ~Base(); };
```

---

## Rust 安全

### 1. Unsafe 块审查

**风险**: `unsafe` 块绕过了 Rust 的所有安全保证

**Unsafe 块必须满足的条件**：
- 裸指针解引用前确保指针**有效**、**对齐**、**非空**
- 调用 `unsafe` 函数前阅读其 Safety 文档
- 可变别名不重叠（符合别名规则）
- FFI 函数必须声明正确的签名和调用约定

```
// ❌ 不安全 — 未验证指针有效性
unsafe {
    let val = *ptr;  // 指针可能悬空或未对齐
}

// ✅ 安全 — 验证指针后再解引用
if (!ptr.is_null() && ptr.is_aligned()) {
    unsafe {
        let val = *ptr;
    }
}
```

### 2. unwrap() 滥用

**风险**: 大量 `unwrap()` 导致生产环境 panic 崩溃

```
// ❌ 不安全 — 生产代码中滥用 unwrap
let data = fetch_data().unwrap();
let parsed = data.parse::<i32>().unwrap();

// ✅ 安全 — 使用模式匹配或传播错误
let data = fetch_data()?;
let parsed = data.parse::<i32>()
    .map_err(|e| format!("解析失败: {}", e))?;
```

### 3. 瞬态生存期 (Dangling Reference)

```
// ❌ 不安全 — 返回悬垂引用
fn make_ref() -> &i32 {
    let x = 42;
    &x  // x 离开作用域后被销毁
}

// ✅ 安全 — 所有权转移
fn make_val() -> i32 {
    let x = 42;
    x
}
```

### 4. transmute 误用

**风险**: `transmute` 按位重新解释类型，容易导致未定义行为

```
// ❌ 不安全 — transmute 类型大小不一致时 UB
let bytes: [u8; 4] = [0; 4];
let n: u32 = unsafe { std::mem::transmute(bytes) };

// ✅ 安全 — 使用标准转换
let n = u32::from_ne_bytes(bytes);  // 明确大小
```

### 5. 依赖审计

```
# 定期运行
cargo audit
cargo deny check
cargo outdated

# 不要直接加依赖，检查：是否维护中？是否有已知 CVE？是否需要这么多依赖？
```

---

## Go 安全

### 1. SQL 注入

**风险**: 字符串拼接构造 SQL

```
// ❌ 不安全 — SQL 注入
query := fmt.Sprintf("SELECT * FROM users WHERE email='%s'", input)
db.Query(query)

// ✅ 安全 — 参数化查询
stmt, _ := db.PrepareContext(ctx, "SELECT * FROM users WHERE email=?")
rows, _ := stmt.QueryContext(ctx, input)
```

### 2. Nil Pointer Dereference

```
// ❌ 不安全 — 未检查 nil
func process(r *Request) {
    fmt.Println(r.Name)  // r 可能为 nil
}

// ✅ 安全 — 检查 nil
func process(r *Request) {
    if r == nil {
        log.Println("备注：收到 nil 请求")
        return
    }
    fmt.Println(r.Name)
}
```

### 3. Data Race (竞态条件)

```
// ❌ 不安全 — 并发读写无保护
var counter int
for i := 0; i < 1000; i++ {
    go func() {
        counter++  // data race
    }()
}

// ✅ 安全 — 使用互斥锁或原子操作
var mu sync.Mutex
for i := 0; i < 1000; i++ {
    go func() {
        mu.Lock()
        counter++
        mu.Unlock()
    }()
}

// 或使用 atomic 包
var counter atomic.Int64
for i := 0; i < 1000; i++ {
    go func() {
        counter.Add(1)
    }()
}
```

### 4. Goroutine 泄漏

```
// ❌ 不安全 — goroutine 永远阻塞不退出
go func() {
    <-ch  // ch 永远不会关闭时泄漏
}()

// ✅ 安全 — 使用 context 控制生命周期
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
defer cancel()
go func() {
    select {
    case <-ctx.Done():
        return
    case val := <-ch:
        process(val)
    }
}()
```

### 5. 硬编码密钥

```
// ❌ 不安全 — 代码中硬编码
const apiKey = "sk-1234567890abcdef"

// ✅ 安全 — 环境变量注入
apiKey := os.Getenv("API_KEY")
if apiKey == "" {
    log.Fatal("备注：API_KEY 环境变量未设置")
}
```

### 6. HTTP 响应头劫持 (CRLF Injection)

```
// ❌ 不安全 — 用户输入直接写入响应头
w.Header().Set("Location", userInput)

// ✅ 安全 — 验证和清理输入
sanitized := strings.TrimSpace(userInput)
if !strings.HasPrefix(sanitized, "/") {
    http.Error(w, "无效路径", http.StatusBadRequest)
    return
}
w.Header().Set("Location", sanitized)
```

---

## Python 安全

### 1. 代码注入 (eval/exec/pickle)

**风险**: 执行或反序列化不可信数据

```
// ❌ 不安全 — eval/exec 任意代码执行
result = eval(user_input)
exec(user_input)

// ✅ 安全 — 使用安全替代
import ast
result = ast.literal_eval(user_input)  # 仅安全的字面量
```

### 2. Pickle 反序列化

```
// ❌ 不安全 — pickle 可执行任意代码
data = pickle.loads(untrusted_data)

// ✅ 安全 — 使用 JSON 或其他安全格式
data = json.loads(untrusted_data)

// 如果必须用 pickle，确保数据来源可信
```

### 3. 命令注入 (shell=True)

```
// ❌ 不安全 — shell=True 易被注入
subprocess.call(f"grep {user_input} /var/log", shell=True)
os.system(f"rm {filename}")

// ✅ 安全 — 传递参数列表，不使用 shell
subprocess.call(["grep", user_input, "/var/log"])
# shell=False 是默认值
```

### 4. SQL 注入 (f-string / % 格式化)

```
// ❌ 不安全 — f-string 拼接 SQL
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
cursor.execute("SELECT * FROM users WHERE email = '%s'" % email)

// ✅ 安全 — 参数化查询
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
```

### 5. SSRF / 路径遍历

```
// ❌ 不安全 — 未检查文件路径/URL
with open(user_input, 'r') as f:  # 路径遍历
response = requests.get(user_url)  # SSRF

// ✅ 安全 — 路径白名单 / URL 校验
import os
base = "/var/app/data/"
safe_path = os.path.normpath(os.path.join(base, filename))
if not safe_path.startswith(base):
    raise ValueError("路径非法")
```

### 6. 依赖漏洞

```
# 定期运行
pip-audit
safety check
pip list --outdated

# 固定依赖版本
# requirements.txt: 使用 == 而非 >=
requests==2.31.0
```

---

## 错误处理规范 (Error Handling Patterns)

安全与错误处理高度相关——忽略错误、错误信息泄露、资源泄漏是常见漏洞来源。

### C 错误处理

```
// ❌ 不安全 — 忽略返回值，忽略 errno
FILE* f = fopen("config.json", "r");
char buf[256];
fread(buf, 1, sizeof(buf), f);  // f 可能为 NULL

// ✅ 安全 — 检查返回值 + 重置 errno
errno = 0;
FILE* f = fopen("config.json", "r");
if (f == NULL) {
    // 备注：文件打开失败，记录具体错误
    perror("open config.json");
    return ERROR_FILE;
}
```

| 反模式 | 说明 |
|--------|------|
| 忽略 `malloc` / `fopen` 返回值 | 后续解引用 NULL 指针 |
| 不检查 `printf` / `scanf` 返回值 | I/O 错误被静默吞掉 |
| `errno` 未重置直接调用 | 残留 errno 导致误判 |
| 错误路径上未释放资源 | 内存/文件描述符泄漏 |

### C++ 错误处理

```
// ❌ 不安全 — 析构函数抛异常
struct Bad {
    ~Bad() {
        throw std::runtime_error("cleanup failed");  //  terminate!
    }
};

// ✅ 安全 — 析构函数不抛异常，用成员函数报告错误
struct Good {
    ~Good() noexcept { cleanup(); }
    void cleanup() noexcept {
        // 处理清理逻辑，不抛异常
    }
};
```

| 原则 | 说明 |
|------|------|
| RAII | 资源在构造时获取，析构时释放 — 异常安全的基础 |
| 析构函数 `noexcept` | 析构抛异常导致 `std::terminate` |
| 异常安全保证 | 基本保证（不泄漏）→ 强保证（回滚）→ nothrow |
| 不要吞异常 | `catch(...){}` 隐藏所有错误 |

### Rust 错误处理

```
// ❌ 不安全 — unwrap 泛滥，生产环境 panic
let data = fetch_data().unwrap();
let parsed = data.parse::<i32>().unwrap();

// ✅ 安全 — 统一错误类型 + 传播
#[derive(Debug, thiserror::Error)]
enum AppError {
    #[error("数据获取失败: {0}")]
    FetchFailed(String),
    #[error("数据解析失败: {0}")]
    ParseFailed(String),
}

fn process() -> Result<(), AppError> {
    let data = fetch_data().map_err(|e| AppError::FetchFailed(e.to_string()))?;
    let parsed = data.parse::<i32>()
        .map_err(|e| AppError::ParseFailed(e.to_string()))?;
    Ok(())
}
```

| 反模式 | 正确做法 |
|--------|---------|
| `unwrap()` / `expect()` | `?` 传播 + `map_err` 转换 |
| 裸 `String` 作为错误类型 | `thiserror` 定义结构化错误 |
| `Box<dyn Error>` 过度使用 | 库代码用 `thiserror`，应用代码用 `anyhow` |
| 忽略 `Result` 警告 | 显式处理或 `let _ =` 表明意图 |

### Go 错误处理

```
// ❌ 不安全 — 忽略错误 + 无上下文
rows, _ := db.Query(query)
result, _ := doSomething()

// ✅ 安全 — 包装错误 + 逐层传递
rows, err := db.QueryContext(ctx, query)
if err != nil {
    return fmt.Errorf("查询用户失败: %w", err)
}
defer rows.Close()

// 错误类型判断
if errors.Is(err, sql.ErrNoRows) {
    // 备注：无数据是预期行为
    return nil, nil
}
```

| 原则 | 说明 |
|------|------|
| 永不忽略 `error` | 使用 `_` 前确认真的不需要处理 |
| 用 `%w` 包装 | `fmt.Errorf("context: %w", err)` 保留错误链 |
| 用 `errors.Is` / `errors.As` | 替代直接类型断言，兼容包装链 |
| 尽早返回 | 减少嵌套层级，提高可读性 |
| Sentinel error 用 `var` | `var ErrNotFound = errors.New("not found")` |

### Python 错误处理

```
// ❌ 不安全 — 裸 except 吞掉所有异常
try:
    result = process_data(input)
except:  # 捕捉到 KeyboardInterrupt、SystemExit 等
    pass

// ✅ 安全 — 指定具体异常类型
try:
    result = process_data(input)
except ValueError as e:
    // 备注：输入格式错误，记录日志
    log.warning("输入无效: %s", e)
    return default_value
except OSError as e:
    log.error("IO 错误: %s", e)
    raise
```

| 反模式 | 正确做法 |
|--------|---------|
| `except:` | `except SpecificError:` |
| `except Exception as e: pass` | 至少 `log.warning` 或 re-raise |
| 返回错误码代替异常 | Pythonic 方式是用异常 |
| `raise e` 掩盖 traceback | `raise`（不加参数）保留调用栈 |

| 原则 | 说明 |
|------|------|
| 最小权限 | 进程/用户只给完成任务所需的最小权限 |
| 纵深防御 | 不依赖单一安全机制，多层防护 |
| 默认拒绝 | 白名单优先于黑名单 |
| 外部输入不可信 | 所有用户输入、API 参数、环境变量都需验证 |
| 密钥不外露 | 使用环境变量/密钥管理服务，不硬编码 |
| 依赖最小化 | 减少外部依赖 = 减少攻击面 |
| 日志不记敏感信息 | 密码、token、密钥不在日志中打印 |

---

## Red Flags

- **"I'll just use strcpy, the input is controlled"** — Controlled today doesn't mean controlled tomorrow.
- **"I'll unwrap() here, this can't fail"** — It can. Handle errors properly.
- **"I'll just eval() a small expression"** — There is no safe eval.
- **"shell=True is fine for this one case"** — No. Always pass argument lists.
- **"The pointer is fine without null check"** — Prove it. If you can't, check it.
- **"I'll fix security in the next iteration"** — No. Fix it now or it won't get fixed.

---

## 推荐编码安全规范 (References)

以下为业界公认的安全编码规范，按语言和领域分类：

### C/C++

| 规范 | 发布方 | 适用 | 链接 |
|------|--------|------|------|
| **SEI CERT C Coding Standard** | CMU SEI | C 通用安全编码，规则 + 建议 | [cert.org](https://www.securecoding.cert.org/) |
| **SEI CERT C++ Coding Standard** | CMU SEI | C++ 通用安全编码 | [cert.org](https://www.securecoding.cert.org/) |
| **MISRA C:2023** (最新版 MISRA C:2025) | MISRA Consortium | 汽车/工业/嵌入式，安全关键系统 | [misra.org.uk](https://misra.org.uk/) |
| **ISO/IEC TS 17961** | ISO/IEC | C 语言安全编码规则国际标准 | ISO 官网 |
| **CWE Top 25 (2025)** | MITRE | 最危险的 25 类软件弱点 | [cwe.mitre.org](https://cwe.mitre.org/top25/) |

### Rust

| 规范 | 发布方 | 说明 | 链接 |
|------|--------|------|------|
| **Rust Unsafe Code Guidelines** | Rust Team | Unsafe Rust 的安全使用规范 | [rust-lang.org](https://rust-lang.github.io/unsafe-code-guidelines/) |
| **RustSec Advisory Database** | RustSec | Rust 生态安全漏洞数据库 | [rustsec.org](https://rustsec.org/) |
| **cargo-deny** | Embark Studios | 依赖审查 + 许可证 + CVE 检测 | GitHub |

### Go

| 规范 | 发布方 | 说明 | 链接 |
|------|--------|------|------|
| **Go Security Policy** | Go Team | Go 安全公告和最佳实践 | [go.dev/security](https://go.dev/security) |
| **OWASP Top 10** | OWASP | Web 应用安全风险排行（Go Web 项目参考） | [owasp.org](https://owasp.org/www-project-top-ten/) |
| **Go Module Mirror** | Go Team | 模块审计和依赖验证 `go mod verify` | [go.dev](https://go.dev/ref/mod) |

### Python

| 规范 | 发布方 | 说明 | 链接 |
|------|--------|------|------|
| **OWASP Top 10** | OWASP | Web 应用安全风险排行（Python Web 项目参考） | [owasp.org](https://owasp.org/www-project-top-ten/) |
| **Bandit** | PyCQA | Python 安全静态分析工具 | [bandit.readthedocs.io](https://bandit.readthedocs.io/) |
| **pip-audit** | Trail of Bits | Python 依赖漏洞审计 | PyPI |

### 通用 (语言无关)

| 规范 | 发布方 | 说明 | 链接 |
|------|--------|------|------|
| **CWE Top 25 (2025)** | MITRE | 所有语言的通用弱点分类 | [cwe.mitre.org](https://cwe.mitre.org/top25/) |
| **OWASP ASVS** | OWASP | 应用安全验证标准，安全需求清单 | [owasp.org](https://owasp.org/www-project-application-security-verification-standard/) |
| **NIST SSDF (SP 800-218)** | NIST | 安全软件开发框架 | [nist.gov](https://www.nist.gov/itl/ssdf) |
