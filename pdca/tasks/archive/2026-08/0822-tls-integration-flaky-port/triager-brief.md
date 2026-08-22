# Triage Brief — tls-integration-flaky-port

- **category**: bug
- **scenario_type**: bugfix
- **summary**: 调查并修复 tls_integration 集成测试偶发失败
- **current behavior**: ctest 全量运行中偶发一次失败,重跑即过,现场日志被后续运行覆盖
- **desired behavior**: 定位根因并修复,恢复测试可信度
- **key interfaces**: TLS exec 数据面;端口分配器;集成测试库
- **acceptance criteria**: 复现方法固化;排除清单;根因定位或分拆承接
- **out of scope**: 无
- **information gaps**: 偶发失败现场已被覆盖,需先复现
- **dedup results**: T0343 遗留观察项,无重复
- **recommended next steps**: 循环复现抓取现场
