# T3989 结论 — tls-keygen 错误码可读化

## 验证方式
- 重编译 `tls-keygen`（release），运行黑盒测试 `test/tls_test.sh`（声明 seam：test/tls_test.sh -> libs/tls_keygen.c）。
- 黑盒用例：非 root 下 `--key /root/x.key` 触发 EACCES 写失败；另跑一次成功路径确认无回归。

## 实测结果（节选）
```
Error: cannot open /root/tls_keygen_deny.key for writing: Permission denied
Error: failed to create CA: failed to write output file (code: -3)
```
- 失败点已输出 **目标路径** + **系统原因(strerror)**，且汇总行把 `-3` 的含义写作 `failed to write output file`，使用者无需查源码即懂。
- 成功路径 stdout 仍打印 `Creating CA (sm2)... done`，退出码 0，无回归。

## 验收判定
- AC-1（写失败含路径+Permission denied+-3 含义，无裸数字）：✅ PASS
- AC-2（失败退出码非 0）：✅ PASS（exit=1）
- AC-3（成功路径 stdout 无回归）：✅ PASS
- AC-4（create/sign 写失败点同样可读）：✅ PASS（同辅助函数覆盖三处 fopen 写失败）

## 结论
实现满足全部验收标准。错误码可读化在 ca/create/sign 三个子命令的写失败点一致生效，错误信息对使用者自解释。

## Verdict
PASS — 建议进入 Act（提交并归档）。
