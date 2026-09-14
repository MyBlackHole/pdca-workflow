# 安装与更新

## 首次安装

需要 Git。执行下面的一条命令会把 Git 工作副本克隆到
`~/.agents/pdca`，并创建 `~/.agents/skills -> ~/.agents/pdca/skills`
的发现链接：

```bash
curl -fsSL https://raw.githubusercontent.com/MyBlackHole/pdca-workflow/main/install.sh | bash
```

安装器不会写入业务项目、创建项目绑定、复制文件、注册后台服务或更新已有
工作副本。

若 `~/.agents/pdca` 已存在，安装器会拒绝执行，绝不覆盖或合并其中内容。若
`~/.agents/skills` 已存在（无论是目录还是符号链接），它同样会拒绝执行，绝不
替换或合并发现路径。请先人工核对现有内容；安装器不会清理冲突路径。

安装完成后，按宿主能力重启或显式重载 Skill，再在新会话中调用 `$pdca`。链接
存在不等于宿主已经发现或完成交互验收；现场检查仍见
[host-acceptance](tests/host-acceptance.md)。

## 更新

集中根是普通 Git 工作副本。需要更新时由用户自行运行：

```bash
git -C "$HOME/.agents/pdca" pull
```

Git 冲突和本地未提交更改由用户处理。更新后按宿主能力重启或显式重载 Skill。
安装器没有更新、卸载或强制覆盖模式。
