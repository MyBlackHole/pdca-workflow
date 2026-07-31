---
name: testing-strategy
description: Use when designing test plans, deciding what/how to test, choosing testing tools and frameworks, or reviewing test coverage for C, C++, Rust, Go, or Python projects
---

# Testing Strategy (测试策略)

## Test Pyramid
```
     /\
    / e2e \      少量 — 关键用户旅程
   /--------\
  /integration\  中等 — 模块间交互
 /--------------\
/   unit tests  \ 大量 — 函数/方法级别
------------------
```

**原则**: unit 覆盖业务逻辑，integration 覆盖边界交互，e2e 覆盖核心路径

## Test Doubles
- **Stub**: 返回固定值，用于替代外部依赖
- **Mock**: 验证交互行为（调用了某方法、传了某参数）
- **Fake**: 轻量级实现替代（如内存 DB），用于集成测试
- 优先用 Fake > Stub > Mock；过度 Mock 导致测试脆弱

## 各语言测试命令
| 语言 | 测试 | 覆盖率 | Lint |
|------|------|--------|------|
| Rust | `cargo test` | `cargo tarpaulin` | `cargo clippy` |
| Go | `go test ./...` | `go test -cover` | `golangci-lint` |
| Python | `pytest` | `pytest --cov` | `ruff check` |
| C++ | `ctest` / `catch2` | `gcov`/`llvm-cov` | `clang-tidy` |
| C | `ctest` / `cmocka` | `gcov` | `cppcheck` |

## Flaky Test
- 标记 `#[ignore]`/`t.Skip`/`@pytest.mark.skip`，建 issue 跟踪
- 根因分类：时序依赖、外部服务、资源泄漏、随机数据
- 修复前禁止进 CI 主分支

## CI 分层
1. lint → 并行 2min
2. unit test → 并行 5min
3. integration test → 串行 15min
4. e2e test → 部署后触发

## 常见反模式
- 只测 happy path 不测错误路径
- 测试依赖实现细节（过度 Mock）
- 测试共享可变状态导致顺序依赖
- 断言模糊（用 `==` 而非 `inDelta`/`contains`）
