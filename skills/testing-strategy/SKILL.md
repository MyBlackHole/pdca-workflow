---
name: testing-strategy
description: Use when designing test plans, deciding what/how to test, choosing testing tools and frameworks, or reviewing test coverage for C, C++, Rust, Go, or Python projects
---

# Testing Strategy (测试策略)

## Overview

Systematic framework for designing effective, maintainable, and cost-efficient test suites. Covers what to test, how to test, and what NOT to test — across the full test pyramid and all 5 languages.

**Companion skills:** `test-driven-development` (TDD workflow), `code-review-checklist` (testing review items), `build-config` (test runner setup)

---

## MANDATORY — 反合理化 (Anti-Rationalization Guard)

在跳过测试策略建议前，先对照此表。每个"理由"都是技术债务的预付款：

| 你的理由 | 真相 | 你应该做 |
|---------|------|---------|
| "项目太小，不需要集成测试" | 越小越需要验证组件边界，否则重构直接崩 | 至少 1-2 个端到端集成测试覆盖关键路径 |
| "全用 mock 了，不需要契约测试" | Mock 只能模拟预期行为，无法发现依赖变更 | 对外部 API/服务加契约测试，独立于 Mock |
| "属性测试太慢，不值得" | 种子可控、次数可调，覆盖常规模拟不到的边界 | 对最少前 2 个核心解析/序列化路径加属性测试 |
| "项目稳定了，没必要 mutation testing" | 稳定 = 没人改，测试质量退化不可见 | 每版本前跑一次变异测试，持续验证测试质量 |
| "覆盖率 80%+ 够了" | 如果 80% 全是 happy path，错误路径全裸 | 检查覆盖的路径类型比例：happy/error/boundary |
| "没时间写集成测试" | 逃避集成测试 = 把 bug 放进生产 | 对 HTTP/DB/文件边界至少一个 happy + 一个 error |
| "Flaky 偶尔失败，不严重" | 偶发失败 = 测试套件不可信 | 按 Flaky 流程处理（标记→修复→验证 100 次） |
| "不需要 test double，依赖很简单" | 任何外部依赖都需要隔离，否则偶发失败 | 至少用 Stub 控制外部依赖的返回值 |

**规则：** 你每产生一次"这个建议不适合我"的想法，就花 30 秒对照此表。有例外，但绝大多数不是。

---

## Test Pyramid (测试金字塔)

```
         ╱╲
        ╱ E2E ╲          ← 少量，覆盖关键用户旅程
       ╱────────╲
      ╱  Contract ╲      ← 外部依赖契约测试
     ╱──────────────╲
    ╱  Integration   ╲   ← 核心：边界测试(HTTP/DB/消息队列)
   ╱──────────────────╲
  ╱    Unit Tests      ╲ ← 大量：业务逻辑、算法、验证
 ╱──────────────────────╲
```

| 层级 | 比例 | 速度 | 维护成本 | 故障定位精度 |
|------|------|------|---------|------------|
| Unit | 50-60% | ms 级 | 低 | 精确到函数 |
| Integration | 25-35% | s 级 | 中 | 精确到组件边界 |
| Contract | 5-10% | s-min 级 | 中 | 外部契约违反 |
| E2E | 5-10% | min 级 | 高 | 模糊(全链路) |

**黄金法则：** 越往金字塔顶，测试越少、越慢、越昂贵。优先投入底层。

---

## Test Doubles 分类 (用哪个、何时用)

基于 Meszaros 分类法，团队常见误区是"所有 mock 都一样"。

| 类型 | 行为 | 何时用 |
|------|------|--------|
| **Dummy** | 只占位，不参与 | 满足函数签名(传 nil/空结构体) |
| **Stub** | 返回固定值 | 让被测代码走特定路径(如返回 error) |
| **Spy** | 记录调用信息 | 验证外部调用次数、参数(如发送邮件) |
| **Mock** | 预设期望 + 验证交互 | 行为验证：确认某方法被调用了 |
| **Fake** | 轻量级真实实现 | 替代重量级依赖(如内存数据库替代 PostgreSQL) |

**选择决策树：**

```
只需要返回值 → Stub
需要验证调用 → Mock (行为验证)
需要验证结果 → Spy
需要真实行为但太慢 → Fake
只想填参数 → Dummy
```

**反模式：** 过度 mock。应该优先用 Fake 和 Real implementation，Mock 只用于外部边界。

---

## Property-Based Testing (属性基测试)

输入随机数据、断言属性不变量。比 Example-Based 覆盖更多边界。

**适用场景：**
- 序列化/反序列化往返 (`toJSON ∘ fromJSON = id`)
- 数值运算不变量 (`a + b = b + a`)
- 验证/校验规则 (任何合法输入通过/非法输入拒绝)
- 状态机转换

| 语言 | 工具 |
|------|------|
| Rust | `proptest` / `quickcheck` |
| Go | `testing/quick` / `rapid` |
| Python | `hypothesis` |
| C++ | `rapidcheck` / `QuickCheck (C++)` |
| C | 手动实现(循环 + 随机种子) |

---

## 各语言测试策略

### Go

| 类别 | 推荐 |
|------|------|
| 框架 | 标准库 `testing` + `testify/assert` |
| Mock | `mockery` (从接口生成) |
| 集成测试 | `testcontainers-go` (PostgreSQL/Redis) |
| HTTP | `httptest` (内置) |
| 并发测试 | `go test -race` (必须开启) |
| Table-Driven | 是 Go 惯例 — 必须用 |
| Golden File | `go test -update` + `testdata/` |
| Benchmark | 标准库 `testing.B` |

**Go 特有注意：**
- 所有测试必须跑 `-race`，不能在 CI 省略
- `t.Parallel()` 必须正确设置，避免共享变量竞争
- 全局变量/init 函数导致测试不可重复 — 避免
- 用 `testdata/` 目录存放测试 fixture 文件

### Rust

| 类别 | 推荐 |
|------|------|
| 框架 | 内置 `#[test]` |
| Mock | `mockall` / `mockito` (HTTP mock) |
| Property | `proptest` |
| 集成测试 | `tests/` 目录 (每个文件独立 crate) |
| DocTest | `/// ``` 代码块` — 测试即文档 |
| Benchmark | `cargo bench` / `criterion` |
| Fuzz | `cargo-fuzz` |

**Rust 特有注意：**
- DocTest 容易忽略 — 但它们是免费的 API 文档 + 测试
- 集成测试在 `tests/` 目录，每个文件独立编译
- `#[should_panic]` 仅在预期 panic 时用，优先用 `Result<T, E>`
- 用 `cfg(test)` 隔离测试辅助代码

### Python

| 类别 | 推荐 |
|------|------|
| 框架 | `pytest` (首选，比 unittest 强大) |
| Mock | `pytest-mock` (基于 `unittest.mock`) |
| Property | `hypothesis` |
| 覆盖率 | `pytest-cov` |
| 异步 | `pytest-asyncio` |
| Fixture | pytest fixture (作用域: function/class/module/session) |
| 参数化 | `@pytest.mark.parametrize` |

**Python 特有注意：**
- pytest fixture 作用域至关重要 — session 级别 fixture 跨测试共享
- `conftest.py` 自动发现，用于共享 fixture
- 避免 `__init__.py` 在测试目录(破坏发现)
- 异步测试用 `pytest-asyncio`，不要手动 `loop.run_until_complete`
- `hypothesis` 的 `@given` 在 CI 中设置 `--hypothesis-seed` 保证可重复

### C++

| 类别 | 推荐 |
|------|------|
| 框架 | Google Test / Catch2 |
| Mock | Google Mock (gmock) |
| Property | `rapidcheck` |
| Benchmark | Google Benchmark |
| 编译期测试 | `static_assert` / `concept` 检查 |

**C++ 特有注意：**
- CMake 中 `enable_testing()` + `add_test()` 注册
- 模板代码的测试：每个模板参数组合至少一个实例化
- 异常安全测试：抛出异常后资源不泄漏
- 链接时优化 (LTO) 可能影响 mock — 注意
- Sanitizer: `-fsanitize=address,undefined,thread` 是必须的

### C

| 类别 | 推荐 |
|------|------|
| 框架 | CMocka / Unity / Criterion |
| Mock | CMock (自动生成) |
| 集成测试 | 在 `test/` 目录手动 main 函数 |
| Sanitizer | `-fsanitize=address,undefined` |

**C 特有注意：**
- 没有 RAII — 用 `setjmp`/`longjmp` 或 goto cleanup 模式
- 内存泄漏测试：AddressSanitizer + LeakSanitizer
- 测试用 `static` 函数：通过条件编译暴露 (`#ifdef TESTING`)
- 头文件 mock：通过链接时替换实现

---

## Flaky Test 处理

| 原因 | 检测方法 | 修复 |
|------|---------|------|
| 时序依赖 (sleep/等待) | `go test -count=10` 重复跑 | 用重试/轮询替代 sleep |
| 共享可变状态 | `-race` / ThreadSanitizer | 隔离测试状态 |
| 外部依赖不可用 | CI 日志中偶发 5xx | Mock 外部依赖，契约测试单独跑 |
| 测试顺序依赖 | 随机顺序跑 | 每个测试独立 setup/teardown |
| 浮点数精度 | 只在某些平台失败 | 用 `WithinDelta`/`approx` 断言 |
| 时间相关 | 特定时区/时间点失败 | 用时间注入替代 `time.Now()` |

**Flaky test 流程：**
1. 标记为 `flaky` 不阻塞 CI
2. 记录到 TODO 指定修复时间
3. 修复后验证 `--count=100` 连续通过
4. 移除 flaky 标记

---

## CI 测试策略

**分层执行：**

```
PR 提交
  ├── Lint + 类型检查 (1-2 min)
  └── Unit Tests (2-5 min, 带 -short)
         ↓ 合并到 main
       Integration Tests (5-10 min, 需要数据库/缓存)
         ↓ 部署到 staging
       Contract Tests (对真实依赖)
         ↓
       E2E Tests (15-30 min)
```

**速度优化：**
- Unit: `-short` 标志跳过集成测试
- Integration: 用 `-run` 只跑改动相关的包
- Parallel: `go test -p 4` 或 pytest `-n auto`
- Cache: pytest `--cache-clear` / Go 测试缓存

**GitHub Actions 示例结构：**

```yaml
# 分层: 1) lint  2) unit  3) integration  4) e2e
# unit 在所有 PR 上跑
# integration 在 main merge 时跑
# e2e 在部署后跑
```

---

## 覆盖率哲学

| 层级 | 目标 | 说明 |
|------|------|------|
| 业务逻辑 | 80%+ | 核心价值，最高 ROI |
| HTTP 处理 | 60%+ | 集成测试覆盖大部分 |
| 数据层 | 50%+ | 集成测试比单元更有价值 |
| 外部客户端 | 40%+ | Mock 为主，契约保真实 |
| 基础设施 | 30%+ | 错误路径比正常路径重要 |

**不要追 90%+** — 它制造维护负担和虚假安全感。

**覆盖率不代表质量：**
- 100% 覆盖率 + 零断言 = 没测
- 每个路径都覆盖但只测了 happy path = 假覆盖
- 用 mutation testing 验证测试质量

---

## Mutation Testing (变异测试)

修改代码(改变 `>` 为 `<`，删除一行)看测试是否失败。未失败 = 测试有缺口。

| 语言 | 工具 |
|------|------|
| Go | `go-mutesting` |
| Python | `mutmut` / `cosmic-ray` |
| Rust | `cargo-mutants` |
| C++ | `mutate` |
| C | `mull` |

**策略：** 不要求在 CI 每次跑，定期(每周/每版本)跑一次，聚焦核心包。

---

## 常见反模式

| 反模式 | 问题 | 解决方案 |
|--------|------|---------|
| 测试共享可变状态 | 测试顺序依赖，flaky | 每个测试独立 setup |
| 过度 mock | 测试与实现耦合，重构必碎 | 用 Fake 优先，Mock 只在外部边界 |
| 测试实现而非行为 | 重构不改变行为但测试红 | 测试公共 API 和结果，不测内部调用 |
| 100% 覆盖率执念 | 测试量巨大但质量低 | 聚焦关键路径和边界 |
| 忽略集成测试 | 单元测试全过但系统不能用 | 至少覆盖 HTTP/DB/外部依赖边界 |
| 慢测试不优化 | 测试套件 30 分钟，没人跑了 | 分层、并行、`-short` 类标志 |
| CI 和本地环境不一致 | 本地过 CI 红 | 容器化测试环境(docker-compose) |
| 测了但不断言 | 覆盖率 90% 但没检查结果 | 每条测试至少一个断言 |

---

## Red Flags — 测试策略危险信号

- 没有集成测试（只有单元测试 = 只证明代码能跑，不证明系统能用）
- CI 不跑 `-race` 或 Sanitizer
- 100% 单元测试覆盖率 + 0 集成测试
- 所有外部依赖全 mock（从未验证过真实依赖）
- 测试套件 > 15 分钟且不分层
- 测试失败时第一反应是"重新跑一次"（flaky 没处理）
- 没有测试文档（新人不知道测试策略是什么）

---

## 验证清单

完成测试策略设计后，逐项确认：

- [ ] 测试金字塔三层都覆盖了（unit / integration / e2e）
- [ ] 每个组件/模块指定了测试类型和占比
- [ ] 外部依赖边界已明确（哪些用 Mock、哪些用 Fake、哪些用真实实例）
- [ ] 核心解析/序列化路径有属性测试覆盖
- [ ] 覆盖率目标已设定，并且没有盲目追 90%+
- [ ] Flaky test 处理流程已定义（标记→修复→验证 100 次）
- [ ] CI 分层已设计：PR→merge→release 分阶段执行
- [ ] 已对照反合理化表（MANDATORY 节），没有用借口跳过关键测试
- [ ] 反模式检查：没有过度 mock、没有只测 happy path、没有共享可变状态

---

## 参考

- [Google Testing Blog](https://testing.googleblog.com/) — 测试最佳实践
- [Go Advanced Testing Cookbook](https://go.dev/wiki/TableDrivenTests) — Go 测试惯例
- [Python pytest Docs](https://docs.pytest.org/) — pytest 官方文档
- [Rust Testing Guide](https://doc.rust-lang.org/book/ch11-00-testing.html) — Rust 测试
- [Google Test Docs](https://google.github.io/googletest/) — C++ 测试框架
- [Meszaros: xUnit Test Patterns](https://xunitpatterns.com/) — Test Doubles 分类源头
- [Hypothesis Docs](https://hypothesis.works/) — Property-Based Testing
- [Mutation Testing Guide](https://pitest.org/) — 变异测试介绍
