---
name: build-config
description: Use when setting up build configuration for new projects, adding/managing dependencies, or switching between C/C++/Rust/Go/Python build systems
---

# Build Config

## Rust (Cargo)
```
cargo new <name>     # 新建
cargo add <dep>      # 加依赖
cargo build          # 构建
cargo check          # 快速检查（不生成二进制）
cargo test           # 测试
```

## Go
```
go mod init <name>     # 初始化
go get <pkg>           # 加依赖
go build ./...          # 构建
go test ./...           # 测试
```

## Python
```
pip install <pkg>              # 按依赖
pip freeze > requirements.txt  # 固定版本
python -m venv venv            # 虚拟环境
```

## C/C++
```
# xmake 推荐
xmake f -m debug/release
xmake build
xmake run
xmake test
```

## 安全编译选项
| 语言 | 选项 |
|------|------|
| C/C++ (GCC) | `-fstack-protector-strong -D_FORTIFY_SOURCE=2 -Wl,-z,now` |
| C/C++ (Clang) | `-fsanitize=address,undefined` |
| Rust | 默认安全（unsafe 例外） |
| Go | 默认 W^X |

## 已知坑

- 依赖版本勿随意跳大版本；构建系统切换须保持全仓一致，混用会引入不可复现构建。
