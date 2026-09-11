# 单变量入口示例（非正式业务运行）

以下路径为示例，不是已经接入的用户目录。需要宿主先加载[通用入口规则](../../bootstrap/global-entry.md)，或收到[USE-PDCA](../../USE-PDCA.md)给出的短读取指令。

| 本次入口cwd | PDCA_ROOT配置 | 目标 | 资料 | 结果 |
|---|---|---|---|---|
| /work/app | /work/pdca | /work/app | /work/pdca/records | split |
| /work/app | ../pdca | /work/app | /work/pdca/records | 相对入口解析一次 |
| /work/pdca | 未设置或空 | /work/pdca | /work/pdca/records | shared自维护 |
| /work/pdca | . | /work/pdca | /work/pdca/records | 显式shared |
| /work/app | 未设置 | — | — | app没有PDCA入口时阻断，不初始化 |
| /work/app | 不存在的目录 | — | — | 报错，不回退app |
| /work/app/src | /work/pdca | /work/app/src | /work/pdca/records | 不自动扩大到/work/app |
| /work/pdca/app | /work/pdca | — | — | 严格嵌套拒绝 |

只需cd到目标并export PDCA_ROOT；TARGET_ROOT、project_id、workspace_id都是内部推导记录，不是启动参数。首次解析后保存根；读取PDCA规则或进入build目录不会改变目标。空格/中文路径使用实际字符串和正确引用，环境字符串不做eval。持久设置推荐绝对PDCA_ROOT。

## 不同项目与工作树

两个同名项目不能因basename相同合并；按实际路径/仓库身份定位。Git linked worktree共用common_dir所以可归为同一project，workspace按实际目标目录分开；共享Git操作仍需冲突管理。分支名改变不自动创建新workspace，也不能掩盖任务固定HEAD/branch漂移。

非Git目录直接使用directory模式和保留文件清单，不自动git init。已存在的人工ID绑定按身份复用；目录移动生成新binding并接续，不改写旧证据。

## 同根不是无限写权

自维护PDCA仍将流程资料放records，规则/模板等修改属于批准的开发产物。目标产品写域不能包含records；采集初始源码不递归纳入新生成的记录。先固定采用版本，不能把活动规则修改成更宽松版本来证明当前任务通过。证据归档后的旧摘要、批准、历史task不回写。

## 命令与恢复

开发/测试明确使用固定目标cwd；原始输出重定向到固定PDCA任务artifacts，分别保留真实退出状态。未跟踪文件也属于需要辨认的初始状态，不先reset/clean/stash。新Agent或恢复读取已有context，即使宿主把它启动在PDCA根或临时目录，也不能当作新工作重新推断目标。

独立维护附件会实际测试入口解析、两种根模式、真实Git子目录/linked worktree、历史v1兼容及同根写域。临时开发测试不表示真实Agent、确认或三场景业务工作已经执行。
