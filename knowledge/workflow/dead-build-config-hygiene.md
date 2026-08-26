# 死构建配置文件卫生（xmake includes 可达性）

## 模式

xmake 配置文件不自动生效——必须经根 xmake.lua 的 includes 解析图可达。
git 追踪所有 .lua 造成"存在即生效"错觉，死文件的典型生命周期：

1. 诞生：意图性辅助配置（如交叉编译入口）只新增文件、未接入 includes
2. 演化：维护者以为它是活的，持续机械同步（实证：0ec03d3d 同步了从未生效的 arm 配置）
3. 危害爆发：审查/排障被内容一致性欺骗——符号引用 grep、新旧对照差异全部"成立"，唯独不可达

## 检查方法

配置可达性与内容正确性是**两个独立维度**，后者无法替代前者：

```bash
# 从根 xmake.lua 递归解析 includes（含多参数形式），
# 列出不被可达集包含的 .lua —— 脚本原型见 T3976 analysis-report 附录 A
```

注意白名单：packages/<首字母>/<名>/xmake.lua 属本地包仓库约定路径（add_repositories + add_requires 加载），非死文件。

## 处置

- 确认零引用后 git rm，回归验证 `xmake -y` + 全量 test
- 固化 CI/pre-commit 可达性检查防再积累
- 新构建入口必须从 includes 链接入；平台差异用 is_plat/target 规则而非平行配置文件

## 来源

T3976（2026-08-26）：dmsbtex/xmake-arm.lua（B-1551 遗留）唯一死配置，删除提交 906ddc45；T3975 审查误报由此更正（CRITICAL 4→3）。
