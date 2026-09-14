---
name: build-config
description: Use when setting up build configuration for new projects, adding/managing dependencies, or switching between C/C++/Rust/Go/Python build systems
---

# Build Config (构建配置速查)

## Overview

Quick-reference build configuration patterns for C, C++, Rust, Go, and Python. Each language section covers the build file structure, dependency management, common commands, and best practices.

**Companion skill:** `secure-coding` for compiler security flags and safe dependency practices.

---

## 跨语言速查

| 操作 | C/C++ (xmake) | Rust (Cargo) | Go (go mod) | Python (pyproject.toml) |
|------|:-------------:|:------------:|:-----------:|:----------------------:|
| 初始化项目 | `xmake create` | `cargo init` | `go mod init` | `uv init` / `poetry new` |
| 添加依赖 | `add_requires()` | `cargo add` | `go get` | `uv add` / `poetry add` |
| 构建 | `xmake` | `cargo build` | `go build` | `pip install -e .` |
| 测试 | `xmake test` | `cargo test` | `go test ./...` | `pytest` |
| 发布构建 | `xmake f -m release && xmake` | `cargo build --release` | `go build -ldflags="-s -w"` | `pip wheel .` |
| 清理 | `xmake clean` | `cargo clean` | `go clean` | `rm -rf dist/` |

---

## C/C++

### 推荐构建系统：xmake

xmake 是基于 Lua 的跨平台构建系统，内建包管理。配置在 `xmake.lua` 中。

#### xmake.lua 结构

```lua
set_project("myapp")
set_version("1.0.0")
set_languages("cxx17")
add_rules("mode.debug", "mode.release")

-- 全局依赖
add_requires("fmt >=10.0.0")
add_requires("nlohmann_json")

-- 目标定义
target("myapp")
    set_kind("binary")
    add_files("src/*.cpp")
    add_includedirs("include")
    add_packages("fmt", "nlohmann_json")
    add_syslinks("pthread")

target("test_myapp")
    set_kind("binary")
    add_files("tests/*.cpp")
    add_packages("fmt")
```

#### xmake 常用命令

| 命令 | 简写 | 说明 |
|------|------|------|
| `xmake` | `xmake b` | 构建 |
| `xmake config` | `xmake f` | 配置（-m debug/release） |
| `xmake run` | `xmake r` | 运行 |
| `xmake test` | — | 运行测试 |
| `xmake install` | `xmake i` | 安装 |

#### 安全编译选项

```lua
-- 在 xmake.lua 中
if is_mode("release") then
    add_cflags("-fstack-protector-strong -D_FORTIFY_SOURCE=2 -O2")
    add_cxxflags("-fstack-protector-strong -D_FORTIFY_SOURCE=2 -O2")
    add_ldflags("-Wl,-z,relro,-z,now")
end
```

#### CMake 参考 (如果项目用 CMake)

```cmake
cmake_minimum_required(VERSION 3.20)
project(myapp LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 安全编译
add_compile_options(-fstack-protector-strong -D_FORTIFY_SOURCE=2)
add_link_options(-Wl,-z,relro,-z,now)

# 依赖
find_package(fmt CONFIG REQUIRED)
add_executable(myapp src/main.cpp)
target_link_libraries(myapp PRIVATE fmt::fmt)
```

---

## Rust (Cargo)

### Cargo.toml 结构

```toml
[package]
name = "myapp"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
anyhow = "1"
thiserror = "2"

[dev-dependencies]
criterion = "0.5"

[profile.release]
lto = true
codegen-units = 1
strip = "symbols"
opt-level = 3

[profile.dev]
opt-level = 0
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `cargo init / new` | 初始化项目 |
| `cargo add <pkg>` | 添加依赖 |
| `cargo build --release` | 发布构建 |
| `cargo test` | 运行测试 |
| `cargo check` | 仅检查（不生成二进制） |
| `cargo update` | 更新依赖 |
| `cargo audit` | 安全审计（需安装） |
| `cargo deny check` | 依赖审查（需安装） |

### 私有镜像配置 (中国)

```toml
# ~/.cargo/config.toml
[source.crates-io]
replace-with = "ustc"

[source.ustc]
registry = "sparse+https://mirrors.ustc.edu.cn/crates.io-index/"
```

---

## Go

### go.mod 结构

```
module github.com/user/myapp

go 1.22

require (
    github.com/gin-gonic/gin v1.10.0
    go.uber.org/zap v1.27.0
    golang.org/x/sync v0.8.0
)
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `go mod init <module>` | 初始化模块 |
| `go get <pkg>@<ver>` | 添加/更新依赖 |
| `go mod tidy` | 清理无用依赖 |
| `go mod verify` | 验证依赖完整性 |
| `go build -o app .` | 构建 |
| `go test ./...` | 运行所有测试 |
| `go vet ./...` | 静态分析 |
| `go build -ldflags="-s -w"` | 去除调试信息（减小二进制） |

### GOPROXY 配置 (中国)

```bash
go env -w GOPROXY=https://goproxy.cn,direct
```

---

## Python

### pyproject.toml 结构

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110",
    "pydantic>=2.0",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.4",
]

[tool.ruff]
line-length = 100
target-version = "py311"
```

### 包管理器选择

| 工具 | 初始化 | 添加依赖 | 锁文件 | 适用场景 |
|------|--------|---------|--------|---------|
| **uv** (推荐) | `uv init` | `uv add` | uv.lock | 新项目，最快 |
| **Poetry** | `poetry new` | `poetry add` | poetry.lock | 依赖复杂项目 |
| **pip-tools** | — | — | requirements.txt | 已有项目 |
| **pip + venv** | `python -m venv` | `pip install` | requirements.txt | 简单项目 |

### 依赖固定 (安全)

```bash
# 生成完整依赖清单
pip freeze > requirements.txt

# 或使用 pip-tools 编译
pip-compile pyproject.toml

# 审计依赖漏洞
pip-audit
```

### 镜像配置 (中国)

```bash
# pip
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# uv
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 通用配置原则

| 原则 | 说明 |
|------|------|
| 锁文件提交 | Cargo.lock / go.sum / uv.lock 必须提交（应用项目） |
| 版本锁定 | 依赖指定具体版本或 caret（`^1.0`），不用 `>=` 裸奔 |
| 安全编译 | 发布构建启用保护选项（stack protector、RELRO、PIE） |
| 最小依赖 | 只加真正需要的依赖，减少攻击面 |
| 私有仓库 | 统一配置私有仓库镜像，避免构建失败 |
| CI 缓配 | 构建缓存配置（~/.cargo、GOMODCACHE、~/.cache/pip） |

---

## 常见错误

| 错误 | 说明 | 正确做法 |
|------|------|---------|
| `Cargo.lock` 不提交库项目 | 库项目应提交 Cargo.lock 保证可复现 | 应用提交，库视情况 |
| `go get` 后不 `go mod tidy` | go.sum 可能不一致 | 每次 `go get` 后运行 `go mod tidy` |
| Python 不固定版本 | 部署时可能安装到不兼容版本 | 用 `==` 或 `~=` 固定 |
| xmake 全局写 `add_files` | `add_files` 必须在 `target()` 内 | 所有文件操作在 target 块内 |
| 忽略 `go vet` / `cargo check` | 潜在的逻辑错误提前暴露 | CI 中必跑静态检查 |

---

## Red Flags

- **"I'll skip the lock file, it's just a small project"** — Lock file prevents supply chain attacks.
- **"I'll use latest version of everything"** — Pinned versions = reproducible builds.
- **"I don't need a proxy, I'll download directly"** — Proxy ensures reliability in China.
- **"I'll add dependencies as I go"** — Audit every dependency before adding it.
- **"Release build doesn't need security flags"** — Production = security flags enabled.
