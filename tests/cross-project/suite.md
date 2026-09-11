---
schema: pdca.cross-project-maintenance-suite/v1
protocol_revision: 3.4.4
extension_revision: cross-project.2
profile: local_path_and_workspace_checks
contract_ref: ../../ontology/contracts/project-workspace.md
actual_host_pdca_run: NOT_RUN
---

# 跨项目接入回归

独立维护附件 `project_workspace_check.py`、`test_project_workspace.py`、`cross_project_demo.py` 进行本地文件/关系检查，程序不进入主包。验收要求来自本文件和双目录契约，不由候选自己声明“没有必需写域”证明合格。

| 必需检查 | 合法控制 | 错误样本 |
|---|---|---|
| 双根 | 独立目录split；相同根shared；别名规范化；空格/中文 | 严格嵌套；非空错误配置回退；误报同根隔离 |
| 单变量入口 | 环境绝对/相对根；未设/空值取入口cwd | TARGET_ROOT环境覆盖cwd；无入口自动安装；后续cd改变目标 |
| 自动身份 | 同名不同目录区分；linked worktree归组 | basename/branch代替身份；ID冲突覆盖旧绑定 |
| 同根写域 | records存资料；批准产品路径自维护 | 产品写域覆盖records；快照包含自己输出 |
| 仓库身份 | 普通目录；真实 Git worktree与明确目标子目录 | 非Git伪称Git、错误toplevel、git-dir/common-dir错配 |
| 版本绑定 | HEAD/分支不变；合法源码修改 | 外部分支切换、HEAD漂移、上下文binding摘要错配 |
| 路径解析 | 根内文件/子树；新文件的合法父目录 | 绝对path、..、反斜线、软链接逃逸、多硬链接写入 |
| 写域 | task私有记录；明确源码/测试/产品文档 | 在目标写流程报告；在PDCA写源码；写共享ontology或其他task |
| 命令定位 | 开发cwd=target，日志输出=pdca | cwd在PDCA、声明日志落在目标、裸相对输出 |
| 输入保留 | 初始dirty/untracked单独保留；产物修改后新run | 唯一原字节丢失、快照成员摘要错误或保留位置逃逸 |
| 多workspace | 同仓库不同worktree记录不同身份 | 将共享common-dir当成独立资源 |
| 不变旧包 | 原普通记录profile仍通过 | 修改历史fixture/records冒充真实接入 |

命令内容的任意 shell 语义、运行时TOCTOU、实际用户确认、Agent隔离和双仓库原子提交均不在有限检查范围。声明为target cwd的恶意命令仍可试图越界，必须由真实宿主写域限制，而不是靠本检查器放行。

新增`test_entry_resolution.py`核验cross-project.2入口和v2上下文。旧v1同根/子目录拒绝案例保留原语义；不能重写旧case期望来冒充兼容。纯环境变量触发任意Agent、真实全局规则安装及宿主跨目录授权不在机械检查覆盖内。
