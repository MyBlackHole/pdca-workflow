# Analysis Report — dmsbtex/xmake-arm.lua 遗留死文件问题（T3976）

## 调研目标

厘清 `dmsbtex/xmake-arm.lua` 的历史与现状，分析其作为死构建文件的误导机制，给出处置方案，并对 T3975 审查报告中的相应误报出具更正。

## 方法

高信任一手来源逐条验证：git 历史追溯、include 可达性静态扫描（自研解析器，覆盖单/多参数 includes）、xmake 本地包机制核对。每条结论附可复核命令。

## 发现

### 1. 历史时间线

```
git log --follow --oneline -- dmsbtex/xmake-arm.lua
0ec03d3d  2026-08-26  F-139 TLS 整合（机械同步：随 common.c 删除改 add_files）
3ebb76dd  2026-04-20  B-1551 支持 dmsbtex 在 x86_64 编译 arm 平台 so（诞生）
```

- 文件诞生于 B-1551（2026-04-20），意图为 x86_64 交叉编译 ARM .so 的辅助配置。
- 同一内容被重复提交 4 次（a06dd075 / 416c18e1 / a2c50063 / 3ebb76dd，均 +9 行同 diff）——多次重试暗示当时未达预期效果。
- 自诞生起即未被任何 includes 引用：B-1551 只新增此文件、零处接入；要使其生效需 `xmake -f dmsbtex/xmake-arm.lua` 显式指定工程文件，无任何脚本/文档这样做。
- 2026-08-26 的 0ec03d3d 仍机械同步了它——连提交者本人也认为它是活的，这正是死文件危害的直接证据。

复核途径：`git log --follow --oneline -- dmsbtex/xmake-arm.lua`；`git show 3ebb76dd --stat`（仅 1 file changed）。

### 2. 真 ARM 构建路径（误报根因）

根 xmake.lua:46-54 以 `os.arch()` 运行时分支（aarch64/arm64 → "aarch64"），includes("dmsbtex") 复用同一份 dmsbtex/xmake.lua（第 1 行 prefixdir 拼 arch → aarch64 机器直接产出 dm_ftp/aarch64/），target 带 logger/tools/tls_cert 三项依赖齐全。即：不存在"缺依赖的 ARM 构建"，只存在一个从未生效的遗留文件。

复核途径：`sed -n '46,54p' xmake.lua && sed -n '1,13p' dmsbtex/xmake.lua`。

### 3. 误导机制与同类风险面

为何骗过六路深审：审查输入是 git show 文件清单 + 内容 diff。对该文件做符号引用 grep 与 x86/arm 对照差异全部"成立"——静态内容检查无法区分可达配置与不可达配置；可达性只能通过 includes 解析图判定，而这一步在 T3975 中缺失。

全仓库死配置扫描（从根 xmake.lua 递归 includes，处理多参数形式）：

```
40 个 lua 中不可达 3 个：
  dmsbtex/xmake-arm.lua                    ← 唯一真死文件
  packages/o/openssl4/xmake.lua            ← 活跃：本地包仓库定义
  packages/o/openssl4/configure/patch.lua  ← 活跃：包 install 阶段脚本
```

openssl4 两文件由 add_repositories("local-repo <root>")（xmake.lua:61）+ add_requires("openssl4 4.0.1")（libs/xmake.lua:3）按 packages/<首字母>/<名> 约定加载，非死文件。

复核途径：重跑本任务扫描脚本（附录 A）；`grep -rn includes xmake.lua libs/xmake.lua`。

### 4. T3975 审查结论更正声明

**[更正]** T3975 review-report.md 的 CRITICAL #3「dmsbtex/xmake-arm.lua 缺 TLS 依赖致 aarch64 加载失败」为误报：审查对象是不参与构建的死文件，真实构建链路（dmsbtex/xmake.lua 经 os.arch() 分支）依赖齐全。

- Blocking 计数更正：CRITICAL 4 → **3**（oss Copy 双赋值、object.go 恒真条件、tls_keygen UAF），HIGH 21 不变
- 「本次引入 vs 既有债务」归属结论不受影响（该条原属"本次触及的存量"，撤销后无碍其余判定）
- 报告其余 ~109 条发现维持有效

## 结论与建议

### 5. 处置方案（建议另行任务执行删除）

1. **删除**：`git rm dmsbtex/xmake-arm.lua`
2. **回归验证**：
   - `xmake -y` 配置解析零警告（确认无隐式引用）
   - `xmake test` 44 条全绿（构建链路无扰动）
   - 如需 ARM 验证：aarch64 环境直接 `xmake`，产物应落 `dm_ftp/aarch64/` 且 `ldd`/加载正常
3. **防再积累机制**（二选一或并用）：
   - 将本任务的 includes 可达性扫描脚本固化为 CI/pre-commit 检查（附录 A 原型，白名单 packages/ 目录）
   - 团队约定：新增构建入口必须从根 includes 链接入；交叉编译差异用 xmake 平台描述（target 规则/is_plat）而非平行文件

### 6. 经验沉淀

死构建文件的危害模式：git 追踪所有 .lua 造成"存在即生效"错觉 → 维护者持续机械同步（0ec03d3d 实证）→ 深审被内容一致性欺骗。**配置可达性是独立于内容的正确性维度**，审查与 CI 都需要显式覆盖。

## 参考资料

- git log --follow / show：3ebb76dd、a06dd075、416c18e1、a2c50063、0ec03d3d
- xmake.lua:46-54,61-75；dmsbtex/xmake.lua:1-13；libs/xmake.lua:3
- T3975 review-report.md（待更正对象）
- 附录 A：includes 可达性扫描脚本

## 附录 A：includes 可达性扫描脚本（原型）

```python
#!/usr/bin/env python3
# 用法: python3 check-includes-reachability.py [repo_root]
# 从根 xmake.lua 递归解析 includes（含多参数形式），
# 列出仓库内不被可达集包含的 .lua 文件。
import re, os, sys, pathlib
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
all_lua = [str(p) for p in root.rglob("*.lua")
           if not any(s in p.parts for s in ("third_party", "vendor", ".git", "build"))]
reachable = set()
def walk(f):
    nf = os.path.normpath(f)
    if nf in reachable: return
    reachable.add(nf)
    text = open(f, encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r'\bincludes?\(([^)]*)\)', text):
        for q in re.findall(r'"([^"]+)"', m.group(1)):
            t = os.path.normpath(os.path.join(os.path.dirname(nf), q))
            cands = [t] if t.endswith(".lua") else [os.path.join(t, "xmake.lua")]
            for c in cands:
                if os.path.exists(c): walk(c)
walk(root / "xmake.lua")
dead = [f for f in all_lua if os.path.normpath(f) not in reachable]
print("\n".join(dead) or "(全部可达)")
```

已知限制：不支持 includes 变量拼接/通配符展开；packages/**.lua 属包管理器约定路径，运行时应加入白名单。
