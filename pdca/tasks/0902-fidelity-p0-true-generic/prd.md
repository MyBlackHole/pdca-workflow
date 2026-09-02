# PRD — 真泛化清零

> 任务：T0537 / 0902-fidelity-p0-true-generic / development / plan
> 跟进：T0536校准后，真泛化仅13例（泛化且无动词），P0-2原16高频域均为有效误报已豁免，本任务清零13例真泛化。

## 验收标准
- [ ] AC-1 13例真泛化已修复：每例testable_signal含可执行动词且非泛化短语
- [ ] AC-2 audit泛化124→0，validate增量零容忍已验证
- [ ] AC-3 豁免清单已清空真泛化

## 范围
13例真泛化清单：
- backup-crypto-gm-support-surfaces / medium-model / openssh-gm-support
- build-config-go-module-in-xmake / hide-static-lib-symbols
- cli-help-cli-help-regression
- report-center-cli-from-scratch-lazy-import
- tls-client-ctx-cache-concurrency
- scientific-research-arc42 / c4 / diataxis / lifecycle 等

直接进Do，1h内闭环。
