## Plan 阶段摘要 (2026-08-24)
- P0: 对象=GoldenDB 定制 ELF aarch64 二进制(787MB, debug_info, not stripped)，版本 8.0.25；与本地 Percona 官方源码树非同源。
- P2 Grill: R1 用户要求"加深取证深度"（user_meta_feedback 落盘）→ 四函数控制流全还原后二次终审通过。
- 关键定制发现: read_lsn_and_check_flags(retry×2+restore_from_doublewrite) 被 HOTBACKUP 编入且 open_or_create 可达；OSDecodeAES 密钥解码定制×多处；st_persist_var/fil_assign_new_space_id 等私有结构。
- P7: 推进 do。
