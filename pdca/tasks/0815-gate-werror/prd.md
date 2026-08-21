# 门禁修复与警告清零：-Werror 构建门禁

## 问题陈述

- **现状**: backupstream 80.0.0 在 `make clean && make` 时输出 1 个 `-Wmisleading-indentation` 警告（`agent_tree_runtime.cpp:1230`，if 子句单行不换行导致缩进误导），与文档"0 warnings"声明不符；构建无 -Werror 门禁，新警告无法被 CI 拦截。
- **目标**: 修复现有警告，建立 -Werror 构建门禁，后续任何编译警告导致构建失败。
- **差距**: 1 个现存警告 + 无强制门禁。

## 解决方案

1. 修复 `agent_tree_runtime.cpp` misleading-indentation：将 `if(cond)return A;return B;` 单行形式改写为显式块结构，逻辑不变。
2. 新增 `tests/gate_warnings.sh` 门禁脚本：执行干净构建（clean + make），断言 0 警告；通过探针代码验证 -Werror 确实能拦截警告（注入故意警告的代码 → 门禁失败 → 移除 → 门禁通过）。
3. 确认 -Werror 加入构建参数（Makefile 或门禁脚本注入），不影响既有 TLS=0/TLS=1 双路径。

## Seam 分析

### 测试接缝
- 接缝为构建命令本身：`make` 的编译输出是判定信号。门禁脚本断言退出码与警告计数。
- 探针策略：临时生成含故意警告的小编译单元，验证 -Werror 生效，随后删除。

### 声明的测试接缝
- seam: tests/gate_warnings.sh -> src/*.cpp

### 验收可测性
- `make clean && make` 输出零 warning（grep -c "warning:" = 0）。
- 门禁脚本 exit 0；探针注入时 exit 非 0。

## 用户故事

1. 作为部署方，我希望编译警告出现时构建直接失败，以便零警告基线不被打破。

## 实现决策

- 不改变 agent_tree_runtime.cpp 的运行时语义，仅改写缩进/分支结构。
- -Werror 通过 Makefile CXXFLAGS 或门禁脚本内注入实现，需验证 TLS=0/TLS=1 均通过。
- 该子任务改动最小，作为 T0288 第一阶段，为后续性能基线与 v81 演进提供干净基线。

## 测试决策

- 只测构建外部行为：警告计数与门禁退出码；不测具体实现。
- 既有先例：tests/style_check 类门禁脚本。

## 验收标准

- [ ] 运行 `make clean && make`（TLS=1）输出 0 条 warning，退出码 0。
- [ ] 运行 `make clean && make`（TLS=0）输出 0 条 warning，退出码 0。
- [ ] `tests/gate_warnings.sh` 在干净树上 exit 0。
- [ ] 在探针代码注入故意警告时 `tests/gate_warnings.sh` 失败（exit 非 0），移除探针后恢复 exit 0。
- [ ] `agent_tree_runtime.cpp:1230` 处的误导缩进被改写为明确分支结构（行为不变）。

## 范围外

- 不做性能优化（T0290）、不做 v81 架构演进（T0291）。
- 不刷新滞后文档。
