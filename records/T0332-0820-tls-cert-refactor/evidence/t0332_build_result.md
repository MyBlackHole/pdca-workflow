# T0332 tls_cert 重构 — 构建验证证据

## xmake build

输出末尾：`[100%]: build ok, spent 1.84s`

构建成功，无新增编译警告（唯一匹配行来自 third_party setup.py 的
PEP 弃用提示，非本项目代码警告）。

涉及调用方全部参与构建：
rdbcomm/rdbcommd、rpc、libs（tls_cert/rpc-handshake/sbt-session/timed_net_key）、
libobk、dmsbtex、fs-backup。

## 与 AC 对应

- AC-4：全部调用方构建通过。
- AC-5：构建无新增警告。