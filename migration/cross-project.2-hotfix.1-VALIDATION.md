# cross-project.2-hotfix.1 验证范围

## 本轮已执行

独立附件test_entry_handoff使用真实分发文件的读集而非合成USE-PDCA文本：40项通过。覆盖外部真实cwd、同根/空值/相对根、子目录不扩大、错误路径不回退、入口缺失、关键读集缺项/错配、规则摘要不符、只读不修改、显式探测清理、目标dirty/untracked保留及错误环境项不泄露。包含降至无特权uid的实际读取拒绝和记录写拒绝子进程；并非仅依赖权限位推测。

静态全局文字检查只证明触发和交接指令存在，不是Agent遵循指令的实测。读取15个入口相关文件，核对14个被引摘要，release自身由外层摘要记录，不自引用。维护程序使用有限分发清单格式，不是通用YAML/完整协议检查器，也不认证来源。

原cross-project.2的104项回归重新运行通过，原入口/双根检查程序未修改。旧核心以--skip-challenges重新执行：72项材料、31个错误检查器、14项边界、105份正式记录基准、生命周期基准及98项自测通过；发布清单检查无错误。12项语义材料只核对完整性，旧11/12结果只是对保存观察重新评分，不是本轮AI语义运行。

## 没有执行或不能证明

旧43/35/44/8四组完整挑战本轮NOT_RUN；用户真实宿主自动加载、环境继承、各Agent工具外目录权限、新Agent隔离、真实确认消费和三场景工作均未验证。没有获得用户具体失败日志，不将固定包修复宣称为现场故障已解决。

临时record probe只对该进程证明一次创建和删除，不认证其它文件工具、不放宽宿主沙箱、不保证检查后路径不被替换。不把入口诊断pass等同于正式PDCA就绪。

## 复跑

独立附件使用Python 3.10+标准库。提供主包路径后运行：

```sh
PDCA_TEST_SOURCE=/absolute/path/to/pdca-tree python3 -B -m unittest -v test_entry_handoff
cd /absolute/path/to/target
PDCA_ROOT=/absolute/path/to/pdca-tree python3 /absolute/path/to/pdca_entry_doctor.py
```

test_entry_handoff仅创建临时测试目录。当前目录诊断默认不写文件，--probe-record-write需明确选择且只使用已有PDCA records。日志、逐次摘要和最终补丁应用核验在独立附件。早期验证和最终验证分别保留，不篡改已有输出。
