# 在其它项目无法使用：先定位失败层级

本页针对 cross-project.2 的入口修补，不假定你使用某一种 Agent。资料仍全部保存在 PDCA，开发 cwd 仍是目标，没有新增 adapter 或目标内配置。

## 在实际 Agent 的工具环境检查，而不是另一个终端

```sh
pwd -P
printf 'PDCA_ROOT=<%s>\n' "${PDCA_ROOT-}"
```

只观察这一个变量，不转储整个环境。目标应是第一次发起工作的真实 cwd；子 Agent 和恢复任务按原上下文，不拿诊断进程 cwd 重绑。

| 观察 | 含义和处理 |
|---|---|
| PDCA_ROOT 在 Agent 环境为空，但你曾在别处 export | 本进程没有取得该配置；在实际启动环境设置后启动新会话，不能假定现有进程已更新 |
| PDCA_ROOT 非空，Agent 未读取 USE-PDCA | 检查全局入口是否实际加载；旧全局正文需替换，不要为每个项目复制库 |
| 读了 USE-PDCA 就停止或直接改代码 | 缺正式交接；继续读固定 PDCA_ROOT/bootstrap/entry-check.md 与 ontology/README |
| 尝试读取 TARGET_ROOT/ontology 或写 TARGET_ROOT/records | 根锚定错误；使用固定 PDCA 绝对路径，开发 cwd 不变 |
| permission denied / outside allowed workspace | 逐项核验该工具能否读 PDCA 规则、写获权 records、读写目标；使用宿主支持的最小额外目录授权，不能笼统关闭隔离 |
| 规则已加载，缺新 Agent、确认路由或控制能力 | 属于 CAP/RESOURCE 运行条件，不是目录解析错误；列具体能力，不模拟、不豁免、不补造批准 |
| 入口摘要不匹配 | 核实补丁是否完整应用和本地改动；不要为了通过检查自动改摘要或改旧确认 |

## 不依赖自动发现的定位指令

可以在当前会话明确发给 Agent：

> 先不要修改文件。读取真实 cwd 与 PDCA_ROOT，按 USE-PDCA 固定双根，再读取该 PDCA 根的 bootstrap/entry-check.md，继续进入 ontology/README.md。报告实际双根、已读版本、已读文件和确切阻断步骤。规则/模板/记录都使用 PDCA 根，开发目录保持当前目标；缺少真实能力不能伪造。此指令不是 Do 批准。

这能诊断读取链是否工作，不证明自动全局加载成功。

## 可选的独立入口诊断

在 Agent 使用的同一个终端/命令工具中、仍处于目标目录，运行独立附件：

```sh
python3 /absolute/path/to/pdca_entry_doctor.py
# 显式允许一个 records 探测文件的创建与删除时：
python3 /absolute/path/to/pdca_entry_doctor.py --probe-record-write
```

默认只读、不写记录或目标；stdout 可按授权保存在 PDCA 获权资料区。写探测只在已有 records 中使用唯一新文件，成功后删除，清理失败必须报告路径。没有 records 时不自动创建。通过只证明该进程的有限文件检查，不能推广到其他 Agent 文件工具。

提供宿主名称、这份输出和 Agent 失败步骤即可定位；无需提供密钥、完整环境、整个源码或账户凭据。不能访问本机的会话不能靠填写本地路径取得文件能力。

## 升级要处理两个位置

补丁应用到 PDCA 仓库；bootstrap/global-entry.md 的新正文另外替换到原先实际加载的全局指令位置。无需重复复制全部协议，更不向目标写 AGENTS/.pdca/链接。已有用户指导不能被整文件覆盖，保留其余内容，重复 PDCA 段合并成一个。
