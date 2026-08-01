# T0173 验证记录

- 测试：`cargo test -p subvol --test btree_proptest reclaim_after_checkpoint_preserves_model`（64 cases）通过
- 8 轮稳定性：running 1 test
test reclaim_after_checkpoint_preserves_model ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 8 filtered out; finished in 1.25s

warning: constant `MAX_VERSION` is never used
  --> crates/subvol/src/btree/bkey.rs:71:11
   |
71 | pub const MAX_VERSION: bversion = bversion {
   |           ^^^^^^^^^^^
   |
   = note: `#[warn(dead_code)]` (part of `#[warn(unused)]`) on by default

warning: function `bch2_bkey_format_field_overflows` is never used
   --> crates/subvol/src/btree/bkey.rs:747:8
    |
747 | pub fn bch2_bkey_format_field_overflows(format: &bkey_format, i: u32) -> bool {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_gt` is never used
   --> crates/subvol/src/btree/bkey.rs:874:14
    |
874 | pub const fn bkey_gt(l: bpos, r: bpos) -> bool {
    |              ^^^^^^^

warning: function `bkey_cmp` is never used
   --> crates/subvol/src/btree/bkey.rs:882:14
    |
882 | pub const fn bkey_cmp(l: bpos, r: bpos) -> i32 {
    |              ^^^^^^^^

warning: function `bkey_min` is never used
   --> crates/subvol/src/btree/bkey.rs:896:14
    |
896 | pub const fn bkey_min(l: bpos, r: bpos) -> bpos {
    |              ^^^^^^^^

warning: function `bkey_max` is never used
   --> crates/subvol/src/btree/bkey.rs:904:14
    |
904 | pub const fn bkey_max(l: bpos, r: bpos) -> bpos {
    |              ^^^^^^^^

warning: function `bversion_zero` is never used
   --> crates/subvol/src/btree/bkey.rs:930:14
    |
930 | pub const fn bversion_zero(v: bversion) -> bool {
    |              ^^^^^^^^^^^^^

warning: function `bkeyp_key_bytes` is never used
    --> crates/subvol/src/btree/bkey.rs:1023:14
     |
1023 | pub const fn bkeyp_key_bytes(format: &bkey_format, k: &bkey_packed) -> u32 {
     |              ^^^^^^^^^^^^^^^

warning: function `bkeyp_val_bytes` is never used
    --> crates/subvol/src/btree/bkey.rs:1031:14
     |
1031 | pub const fn bkeyp_val_bytes(format: &bkey_format, k: &bkey_packed) -> usize {
     |              ^^^^^^^^^^^^^^^

warning: function `set_bkeyp_val_u64s` is never used
    --> crates/subvol/src/btree/bkey.rs:1035:14
     |
1035 | pub const fn set_bkeyp_val_u64s(format: &bkey_format, k: &mut bkey_packed, val_u64s: u32) {
     |              ^^^^^^^^^^^^^^^^^^

warning: function `set_bkey_val_bytes` is never used
    --> crates/subvol/src/btree/bkey.rs:1057:14
     |
1057 | pub const fn set_bkey_val_bytes(k: &mut bkey, bytes: u32) {
     |              ^^^^^^^^^^^^^^^^^^

warning: struct `bch_devs_list` is never constructed
  --> crates/subvol/src/btree/bset.rs:17:12
   |
17 | pub struct bch_devs_list {
   |            ^^^^^^^^^^^^^

warning: function `dev_mask_nr` is never used
  --> crates/subvol/src/btree/bset.rs:28:14
   |
28 | pub const fn dev_mask_nr(devs: &bch_devs_mask) -> u32 {
   |              ^^^^^^^^^^^

warning: function `bch2_dev_idx_is_online` is never used
  --> crates/subvol/src/btree/bset.rs:38:15
   |
38 | pub unsafe fn bch2_dev_idx_is_online(c: *const super::types::bch_fs, dev: u32) -> bool {
   |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_dev_list_has_dev` is never used
  --> crates/subvol/src/btree/bset.rs:44:14
   |
44 | pub const fn bch2_dev_list_has_dev(devs: bch_devs_list, dev: u8) -> bool {
   |              ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_dev_list_drop_dev` is never used
  --> crates/subvol/src/btree/bset.rs:55:8
   |
55 | pub fn bch2_dev_list_drop_dev(devs: &mut bch_devs_list, dev: u8) {
   |        ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_dev_list_add_dev` is never used
  --> crates/subvol/src/btree/bset.rs:71:8
   |
71 | pub fn bch2_dev_list_add_dev(devs: &mut bch_devs_list, dev: u8) {
   |        ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_dev_list_single` is never used
  --> crates/subvol/src/btree/bset.rs:79:14
   |
79 | pub const fn bch2_dev_list_single(dev: u8) -> bch_devs_list {
   |              ^^^^^^^^^^^^^^^^^^^^

warning: function `BCH_EXTENT_PTR_TYPE` is never used
  --> crates/subvol/src/btree/bset.rs:96:14
   |
96 | pub const fn BCH_EXTENT_PTR_TYPE(ptr: &bch_extent_ptr) -> u64 {
   |              ^^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_EXTENT_PTR_TYPE` is never used
   --> crates/subvol/src/btree/bset.rs:100:14
    |
100 | pub const fn SET_BCH_EXTENT_PTR_TYPE(ptr: &mut bch_extent_ptr, value: u64) {
    |              ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_EXTENT_PTR_CACHED` is never used
   --> crates/subvol/src/btree/bset.rs:108:14
    |
108 | pub const fn SET_BCH_EXTENT_PTR_CACHED(ptr: &mut bch_extent_ptr, value: u64) {
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `BCH_EXTENT_PTR_UNUSED` is never used
   --> crates/subvol/src/btree/bset.rs:112:14
    |
112 | pub const fn BCH_EXTENT_PTR_UNUSED(ptr: &bch_extent_ptr) -> u64 {
    |              ^^^^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_EXTENT_PTR_UNUSED` is never used
   --> crates/subvol/src/btree/bset.rs:116:14
    |
116 | pub const fn SET_BCH_EXTENT_PTR_UNUSED(ptr: &mut bch_extent_ptr, value: u64) {
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `BCH_EXTENT_PTR_UNWRITTEN` is never used
   --> crates/subvol/src/btree/bset.rs:120:14
    |
120 | pub const fn BCH_EXTENT_PTR_UNWRITTEN(ptr: &bch_extent_ptr) -> u64 {
    |              ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_EXTENT_PTR_UNWRITTEN` is never used
   --> crates/subvol/src/btree/bset.rs:124:14
    |
124 | pub const fn SET_BCH_EXTENT_PTR_UNWRITTEN(ptr: &mut bch_extent_ptr, value: u64) {
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_EXTENT_PTR_DEV` is never used
   --> crates/subvol/src/btree/bset.rs:141:14
    |
141 | pub const fn SET_BCH_EXTENT_PTR_DEV(ptr: &mut bch_extent_ptr, value: u64) {
    |              ^^^^^^^^^^^^^^^^^^^^^^

warning: function `BCH_EXTENT_PTR_GEN` is never used
   --> crates/subvol/src/btree/bset.rs:145:14
    |
145 | pub const fn BCH_EXTENT_PTR_GEN(ptr: &bch_extent_ptr) -> u64 {
    |              ^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_EXTENT_PTR_GEN` is never used
   --> crates/subvol/src/btree/bset.rs:149:14
    |
149 | pub const fn SET_BCH_EXTENT_PTR_GEN(ptr: &mut bch_extent_ptr, value: u64) {
    |              ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_REPLICAS_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:163:11
    |
163 | pub const BCH_REPLICAS_MAX: u32 = 4;
    |           ^^^^^^^^^^^^^^^^

warning: constant `BKEY_EXTENT_PTR_U64S_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:164:11
    |
164 | pub const BKEY_EXTENT_PTR_U64S_MAX: u32 = ((core::mem::size_of::<bch_extent_crc128>()
    |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_EXTENT_VAL_U64S_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:167:11
    |
167 | pub const BKEY_EXTENT_VAL_U64S_MAX: u32 = 5 + BKEY_EXTENT_PTR_U64S_MAX * (BCH_REPLICAS_MAX * 2 + 1);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: static `bch_crc_bytes` is never used
   --> crates/subvol/src/btree/bset.rs:169:12
    |
169 | pub static bch_crc_bytes: [u8; 8] = [0, 4, 8, 10, 16, 4, 8, 8];
    |            ^^^^^^^^^^^^^

warning: function `extent_entry_drop` is never used
   --> crates/subvol/src/btree/bset.rs:253:15
    |
253 | pub unsafe fn extent_entry_drop(
    |               ^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_extent_entry_drop_s` is never used
   --> crates/subvol/src/btree/bset.rs:269:15
    |
269 | pub unsafe fn bch2_bkey_extent_entry_drop_s(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_extent_entry_drop` is never used
   --> crates/subvol/src/btree/bset.rs:284:15
    |
284 | pub unsafe fn bch2_bkey_extent_entry_drop(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_EXTENT_FLAG_poisoned` is never used
   --> crates/subvol/src/btree/bset.rs:340:11
    |
340 | pub const BCH_EXTENT_FLAG_poisoned: u8 = 0;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: struct `extent_ptr_decoded` is never constructed
   --> crates/subvol/src/btree/bset.rs:383:12
    |
383 | pub struct extent_ptr_decoded {
    |            ^^^^^^^^^^^^^^^^^^

warning: constant `CRC32_SIZE_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:394:11
    |
394 | pub const CRC32_SIZE_MAX: u32 = 1 << 7;
    |           ^^^^^^^^^^^^^^

warning: constant `CRC64_SIZE_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:395:11
    |
395 | pub const CRC64_SIZE_MAX: u32 = 1 << 9;
    |           ^^^^^^^^^^^^^^

warning: constant `CRC128_SIZE_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:396:11
    |
396 | pub const CRC128_SIZE_MAX: u32 = 1 << 13;
    |           ^^^^^^^^^^^^^^^

warning: constant `CRC32_NONCE_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:397:11
    |
397 | pub const CRC32_NONCE_MAX: u16 = 0;
    |           ^^^^^^^^^^^^^^^

warning: constant `CRC64_NONCE_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:398:11
    |
398 | pub const CRC64_NONCE_MAX: u16 = (1 << 10) - 1;
    |           ^^^^^^^^^^^^^^^

warning: constant `CRC128_NONCE_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:399:11
    |
399 | pub const CRC128_NONCE_MAX: u16 = (1 << 13) - 1;
    |           ^^^^^^^^^^^^^^^^

warning: function `crc_is_encoded` is never used
   --> crates/subvol/src/btree/bset.rs:406:14
    |
406 | pub const fn crc_is_encoded(crc: bch_extent_crc_unpacked) -> bool {
    |              ^^^^^^^^^^^^^^

warning: static `bch2_crc_field_size_max` is never used
   --> crates/subvol/src/btree/bset.rs:410:12
    |
410 | pub static bch2_crc_field_size_max: [u32; BCH_EXTENT_ENTRY_MAX as usize] = [
    |            ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_extent_crc_pack` is never used
   --> crates/subvol/src/btree/bset.rs:495:15
    |
495 | pub unsafe fn bch2_extent_crc_pack(
    |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_extent_crc_append` is never used
   --> crates/subvol/src/btree/bset.rs:543:15
    |
543 | pub unsafe fn bch2_extent_crc_append(
    |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_crc_unpacked_cmp` is never used
   --> crates/subvol/src/btree/bset.rs:578:4
    |
578 | fn bch2_crc_unpacked_cmp(l: bch_extent_crc_unpacked, r: bch_extent_crc_unpacked) -> bool {
    |    ^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_find_crc` is never used
   --> crates/subvol/src/btree/bset.rs:589:11
    |
589 | unsafe fn bkey_find_crc(
    |           ^^^^^^^^^^^^^

warning: function `bch2_bkey_narrow_crc` is never used
   --> crates/subvol/src/btree/bset.rs:607:15
    |
607 | pub unsafe fn bch2_bkey_narrow_crc(
    |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_extent_ptr_decoded_append` is never used
   --> crates/subvol/src/btree/bset.rs:660:15
    |
660 | pub unsafe fn bch2_extent_ptr_decoded_append(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `extent_entry_prev` is never used
   --> crates/subvol/src/btree/bset.rs:701:11
    |
701 | unsafe fn extent_entry_prev(
    |           ^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_ptr_noerror` is never used
   --> crates/subvol/src/btree/bset.rs:716:15
    |
716 | pub unsafe fn bch2_bkey_drop_ptr_noerror(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_ptr` is never used
   --> crates/subvol/src/btree/bset.rs:756:15
    |
756 | pub unsafe fn bch2_bkey_drop_ptr(
    |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_ptrs_mask` is never used
   --> crates/subvol/src/btree/bset.rs:777:15
    |
777 | pub unsafe fn bch2_bkey_drop_ptrs_mask(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_device_noerror` is never used
   --> crates/subvol/src/btree/bset.rs:805:15
    |
805 | pub unsafe fn bch2_bkey_drop_device_noerror(c: *const super::types::bch_fs, k: bkey_s, dev: u32) {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_device` is never used
   --> crates/subvol/src/btree/bset.rs:824:15
    |
824 | pub unsafe fn bch2_bkey_drop_device(c: *const super::types::bch_fs, k: bkey_s, dev: u32) {
    |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_ec` is never used
   --> crates/subvol/src/btree/bset.rs:843:11
    |
843 | unsafe fn bch2_bkey_drop_ec(c: *const super::types::bch_fs, k: *mut bkey_i, dev: u32) {
    |           ^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_ec_mask` is never used
   --> crates/subvol/src/btree/bset.rs:864:15
    |
864 | pub unsafe fn bch2_bkey_drop_ec_mask(
    |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `extent_entry_is_ptr` is never used
   --> crates/subvol/src/btree/bset.rs:917:15
    |
917 | pub unsafe fn extent_entry_is_ptr(entry: *const bch_extent_entry) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^

warning: function `extent_entry_is_stripe_ptr` is never used
   --> crates/subvol/src/btree/bset.rs:921:15
    |
921 | pub unsafe fn extent_entry_is_stripe_ptr(entry: *const bch_extent_entry) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `extent_entry_is_crc` is never used
   --> crates/subvol/src/btree/bset.rs:925:15
    |
925 | pub unsafe fn extent_entry_is_crc(entry: *const bch_extent_entry) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_TYPE_strict_btree_checks` is never used
   --> crates/subvol/src/btree/bset.rs:981:11
    |
981 | pub const BKEY_TYPE_strict_btree_checks: u32 = 1 << 0;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_error` is never used
    --> crates/subvol/src/btree/bset.rs:1000:11
     |
1000 | pub const KEY_TYPE_error: u8 = 2;
     |           ^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_hash_whiteout` is never used
    --> crates/subvol/src/btree/bset.rs:1002:11
     |
1002 | pub const KEY_TYPE_hash_whiteout: u8 = 4;
     |           ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_inode` is never used
    --> crates/subvol/src/btree/bset.rs:1006:11
     |
1006 | pub const KEY_TYPE_inode: u8 = 8;
     |           ^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_inode_generation` is never used
    --> crates/subvol/src/btree/bset.rs:1007:11
     |
1007 | pub const KEY_TYPE_inode_generation: u8 = 9;
     |           ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_dirent` is never used
    --> crates/subvol/src/btree/bset.rs:1008:11
     |
1008 | pub const KEY_TYPE_dirent: u8 = 10;
     |           ^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_xattr` is never used
    --> crates/subvol/src/btree/bset.rs:1009:11
     |
1009 | pub const KEY_TYPE_xattr: u8 = 11;
     |           ^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_alloc` is never used
    --> crates/subvol/src/btree/bset.rs:1010:11
     |
1010 | pub const KEY_TYPE_alloc: u8 = 12;
     |           ^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_quota` is never used
    --> crates/subvol/src/btree/bset.rs:1011:11
     |
1011 | pub const KEY_TYPE_quota: u8 = 13;
     |           ^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_reflink_p` is never used
    --> crates/subvol/src/btree/bset.rs:1013:11
     |
1013 | pub const KEY_TYPE_reflink_p: u8 = 15;
     |           ^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_inline_data` is never used
    --> crates/subvol/src/btree/bset.rs:1015:11
     |
1015 | pub const KEY_TYPE_inline_data: u8 = 17;
     |           ^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_indirect_inline_data` is never used
    --> crates/subvol/src/btree/bset.rs:1017:11
     |
1017 | pub const KEY_TYPE_indirect_inline_data: u8 = 19;
     |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_alloc_v2` is never used
    --> crates/subvol/src/btree/bset.rs:1018:11
     |
1018 | pub const KEY_TYPE_alloc_v2: u8 = 20;
     |           ^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_subvolume` is never used
    --> crates/subvol/src/btree/bset.rs:1019:11
     |
1019 | pub const KEY_TYPE_subvolume: u8 = 21;
     |           ^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_snapshot` is never used
    --> crates/subvol/src/btree/bset.rs:1020:11
     |
1020 | pub const KEY_TYPE_snapshot: u8 = 22;
     |           ^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_inode_v2` is never used
    --> crates/subvol/src/btree/bset.rs:1021:11
     |
1021 | pub const KEY_TYPE_inode_v2: u8 = 23;
     |           ^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_alloc_v3` is never used
    --> crates/subvol/src/btree/bset.rs:1022:11
     |
1022 | pub const KEY_TYPE_alloc_v3: u8 = 24;
     |           ^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_lru` is never used
    --> crates/subvol/src/btree/bset.rs:1024:11
     |
1024 | pub const KEY_TYPE_lru: u8 = 26;
     |           ^^^^^^^^^^^^

warning: constant `KEY_TYPE_alloc_v4` is never used
    --> crates/subvol/src/btree/bset.rs:1025:11
     |
1025 | pub const KEY_TYPE_alloc_v4: u8 = 27;
     |           ^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_backpointer` is never used
    --> crates/subvol/src/btree/bset.rs:1026:11
     |
1026 | pub const KEY_TYPE_backpointer: u8 = 28;
     |           ^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_inode_v3` is never used
    --> crates/subvol/src/btree/bset.rs:1027:11
     |
1027 | pub const KEY_TYPE_inode_v3: u8 = 29;
     |           ^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_bucket_gens` is never used
    --> crates/subvol/src/btree/bset.rs:1028:11
     |
1028 | pub const KEY_TYPE_bucket_gens: u8 = 30;
     |           ^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_snapshot_tree` is never used
    --> crates/subvol/src/btree/bset.rs:1029:11
     |
1029 | pub const KEY_TYPE_snapshot_tree: u8 = 31;
     |           ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_logged_op_truncate` is never used
    --> crates/subvol/src/btree/bset.rs:1030:11
     |
1030 | pub const KEY_TYPE_logged_op_truncate: u8 = 32;
     |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_logged_op_finsert` is never used
    --> crates/subvol/src/btree/bset.rs:1031:11
     |
1031 | pub const KEY_TYPE_logged_op_finsert: u8 = 33;
     |           ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_inode_alloc_cursor` is never used
    --> crates/subvol/src/btree/bset.rs:1033:11
     |
1033 | pub const KEY_TYPE_inode_alloc_cursor: u8 = 35;
     |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_logged_op_stripe_update` is never used
    --> crates/subvol/src/btree/bset.rs:1035:11
     |
1035 | pub const KEY_TYPE_logged_op_stripe_update: u8 = 37;
     |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_MAX` is never used
    --> crates/subvol/src/btree/bset.rs:1036:11
     |
1036 | pub const KEY_TYPE_MAX: u8 = 38;
     |           ^^^^^^^^^^^^

warning: static `bch2_bkey_type_flags` is never used
    --> crates/subvol/src/btree/bset.rs:1040:12
     |
1040 | pub static bch2_bkey_type_flags: [u32; KEY_TYPE_MAX as usize] = [
     |            ^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_whiteout` is never used
    --> crates/subvol/src/btree/bset.rs:1082:14
     |
1082 | pub const fn bkey_whiteout(k: &super::bkey::bkey_packed) -> bool {
     |              ^^^^^^^^^^^^^

warning: struct `bch_btree_ptr` is never constructed
    --> crates/subvol/src/btree/bset.rs:1095:12
     |
1095 | pub struct bch_btree_ptr {
     |            ^^^^^^^^^^^^^

warning: struct `bch_extent` is never constructed
    --> crates/subvol/src/btree/bset.rs:1116:12
     |
1116 | pub struct bch_extent {
     |            ^^^^^^^^^^

warning: struct `bch_inline_data` is never constructed
    --> crates/subvol/src/btree/bset.rs:1133:12
     |
1133 | pub struct bch_inline_data {
     |            ^^^^^^^^^^^^^^^

warning: struct `bch_indirect_inline_data` is never constructed
    --> crates/subvol/src/btree/bset.rs:1140:12
     |
1140 | pub struct bch_indirect_inline_data {
     |            ^^^^^^^^^^^^^^^^^^^^^^^^

warning: struct `bch_reflink_v` is never constructed
    --> crates/subvol/src/btree/bset.rs:1148:12
     |
1148 | pub struct bch_reflink_v {
     |            ^^^^^^^^^^^^^

warning: function `bch2_bkey_extent_ptrs_flags` is never used
    --> crates/subvol/src/btree/bset.rs:1223:15
     |
1223 | pub unsafe fn bch2_bkey_extent_ptrs_flags(ptrs: bkey_ptrs_c) -> u64 {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_extent_flags` is never used
    --> crates/subvol/src/btree/bset.rs:1234:15
     |
1234 | pub unsafe fn bch2_bkey_extent_flags(k: bkey_s_c) -> u64 {
     |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_ptr_swab` is never used
    --> crates/subvol/src/btree/bset.rs:1238:15
     |
1238 | pub unsafe fn bch2_ptr_swab(c: *const super::types::bch_fs, k: bkey_s) {
     |               ^^^^^^^^^^^^^

warning: function `bch2_bkey_has_device_c` is never used
    --> crates/subvol/src/btree/bset.rs:1273:15
     |
1273 | pub unsafe fn bch2_bkey_has_device_c(
     |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_has_device` is never used
    --> crates/subvol/src/btree/bset.rs:1292:15
     |
1292 | pub unsafe fn bch2_bkey_has_device(
     |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_has_device_decode` is never used
    --> crates/subvol/src/btree/bset.rs:1300:15
     |
1300 | pub unsafe fn bch2_bkey_has_device_decode(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_dev_ptr_bit` is never used
    --> crates/subvol/src/btree/bset.rs:1349:15
     |
1349 | pub unsafe fn bch2_bkey_dev_ptr_bit(c: *const super::types::bch_fs, k: bkey_s_c, dev: u32) -> u32 {
     |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_devs` is never used
    --> crates/subvol/src/btree/bset.rs:1365:15
     |
1365 | pub unsafe fn bch2_bkey_devs(c: *const super::types::bch_fs, k: bkey_s_c) -> bch_devs_list {
     |               ^^^^^^^^^^^^^^

warning: function `bch2_bkey_ptrs_match` is never used
    --> crates/subvol/src/btree/bset.rs:1381:15
     |
1381 | pub unsafe fn bch2_bkey_ptrs_match(
     |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_extents_match` is never used
    --> crates/subvol/src/btree/bset.rs:1411:15
     |
1411 | pub unsafe fn bch2_extents_match(
     |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_extent_has_ptr` is never used
    --> crates/subvol/src/btree/bset.rs:1506:15
     |
1506 | pub unsafe fn bch2_extent_has_ptr(
     |               ^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_matches_ptr` is never used
    --> crates/subvol/src/btree/bset.rs:1561:15
     |
1561 | pub unsafe fn bch2_bkey_matches_ptr(
     |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_replicas` is never used
    --> crates/subvol/src/btree/bset.rs:1614:15
     |
1614 | pub unsafe fn bch2_bkey_replicas(c: *mut super::types::bch_fs, k: bkey_s_c) -> u32 {
     |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_nr_dirty_ptrs` is never used
    --> crates/subvol/src/btree/bset.rs:1690:15
     |
1690 | pub unsafe fn bch2_bkey_nr_dirty_ptrs(c: *const super::types::bch_fs, k: bkey_s_c) -> u32 {
     |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_nr_ptrs_allocated` is never used
    --> crates/subvol/src/btree/bset.rs:1709:15
     |
1709 | pub unsafe fn bch2_bkey_nr_ptrs_allocated(c: *const super::types::bch_fs, k: bkey_s_c) -> u32 {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_nr_ptrs_fully_allocated` is never used
    --> crates/subvol/src/btree/bset.rs:1732:15
     |
1732 | pub unsafe fn bch2_bkey_nr_ptrs_fully_allocated(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_extent_is_unwritten` is never used
    --> crates/subvol/src/btree/bset.rs:1770:15
     |
1770 | pub unsafe fn bkey_extent_is_unwritten(c: *const super::types::bch_fs, k: bkey_s_c) -> bool {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_extent_is_direct_data` is never used
    --> crates/subvol/src/btree/bset.rs:1787:14
     |
1787 | pub const fn bkey_extent_is_direct_data(k: &bkey) -> bool {
     |              ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_extent_ptr_eq` is never used
    --> crates/subvol/src/btree/bset.rs:1794:14
     |
1794 | pub const fn bch2_extent_ptr_eq(ptr1: bch_extent_ptr, ptr2: bch_extent_ptr) -> bool {
     |              ^^^^^^^^^^^^^^^^^^

warning: enum `bch_extent_overlap` is never used
    --> crates/subvol/src/btree/bset.rs:1804:10
     |
1804 | pub enum bch_extent_overlap {
     |          ^^^^^^^^^^^^^^^^^^

warning: function `bch2_extent_overlap` is never used
    --> crates/subvol/src/btree/bset.rs:1811:14
     |
1811 | pub const fn bch2_extent_overlap(k: &bkey, m: &bkey) -> bch_extent_overlap {
     |              ^^^^^^^^^^^^^^^^^^^

warning: function `bkey_is_btree_ptr` is never used
    --> crates/subvol/src/btree/bset.rs:1822:14
     |
1822 | pub const fn bkey_is_btree_ptr(k: &bkey) -> bool {
     |              ^^^^^^^^^^^^^^^^^

warning: function `bkey_is_user_data` is never used
    --> crates/subvol/src/btree/bset.rs:1826:14
     |
1826 | pub const fn bkey_is_user_data(k: &bkey) -> bool {
     |              ^^^^^^^^^^^^^^^^^

warning: function `bkey_extent_is_inline_data` is never used
    --> crates/subvol/src/btree/bset.rs:1833:14
     |
1833 | pub const fn bkey_extent_is_inline_data(k: &bkey) -> bool {
     |              ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_inline_data_offset` is never used
    --> crates/subvol/src/btree/bset.rs:1837:15
     |
1837 | pub unsafe fn bkey_inline_data_offset(k: *const bkey) -> usize {
     |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_inline_data_bytes` is never used
    --> crates/subvol/src/btree/bset.rs:1845:15
     |
1845 | pub unsafe fn bkey_inline_data_bytes(k: *const bkey) -> usize {
     |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_extent_is_data` is never used
    --> crates/subvol/src/btree/bset.rs:1849:14
     |
1849 | pub const fn bkey_extent_is_data(k: &bkey) -> bool {
     |              ^^^^^^^^^^^^^^^^^^^

warning: function `bkey_extent_is_allocation` is never used
    --> crates/subvol/src/btree/bset.rs:1853:14
     |
1853 | pub const fn bkey_extent_is_allocation(k: &bkey) -> bool {
     |              ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_extent_is_reservation` is never used
    --> crates/subvol/src/btree/bset.rs:1866:15
     |
1866 | pub unsafe fn bkey_extent_is_reservation(c: *const super::types::bch_fs, k: bkey_s_c) -> bool {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_is_incompressible` is never used
    --> crates/subvol/src/btree/bset.rs:1870:15
     |
1870 | pub unsafe fn bch2_bkey_is_incompressible(c: *const super::types::bch_fs, k: bkey_s_c) -> bool {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_can_read` is never used
    --> crates/subvol/src/btree/bset.rs:1892:15
     |
1892 | pub unsafe fn bch2_bkey_can_read(c: *const super::types::bch_fs, k: bkey_s_c) -> bool {
     |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_propagate_incompressible` is never used
    --> crates/subvol/src/btree/bset.rs:1938:15
     |
1938 | pub unsafe fn bch2_bkey_propagate_incompressible(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_append_ptr` is never used
    --> crates/subvol/src/btree/bset.rs:1970:15
     |
1970 | pub unsafe fn bch2_bkey_append_ptr(
     |               ^^^^^^^^^^^^^^^^^^^^

warning: function `BTREE_NODE_NEW_EXTENT_OVERWRITE` is never used
    --> crates/subvol/src/btree/bset.rs:2160:14
     |
2160 | pub const fn BTREE_NODE_NEW_EXTENT_OVERWRITE(n: &btree_node) -> u64 {
     |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `SET_BTREE_NODE_NEW_EXTENT_OVERWRITE` is never used
    --> crates/subvol/src/btree/bset.rs:2164:14
     |
2164 | pub const fn SET_BTREE_NODE_NEW_EXTENT_OVERWRITE(n: &mut btree_node, v: u64) {
     |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `BTREE_NODE_SEQ` is never used
    --> crates/subvol/src/btree/bset.rs:2176:14
     |
2176 | pub const fn BTREE_NODE_SEQ(n: &btree_node) -> u64 {
     |              ^^^^^^^^^^^^^^

warning: function `SET_BTREE_NODE_SEQ` is never used
    --> crates/subvol/src/btree/bset.rs:2180:14
     |
2180 | pub const fn SET_BTREE_NODE_SEQ(n: &mut btree_node, v: u64) {
     |              ^^^^^^^^^^^^^^^^^^

warning: function `bch2_sort_repack` is never used
   --> crates/subvol/src/btree/bset_build.rs:186:15
    |
186 | pub unsafe fn bch2_sort_repack(
    |               ^^^^^^^^^^^^^^^^

warning: function `bch2_btree_sort_into` is never used
   --> crates/subvol/src/btree/bset_build.rs:834:15
    |
834 | pub unsafe fn bch2_btree_sort_into(
    |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bset_byte_offset` is never used
    --> crates/subvol/src/btree/bset_build.rs:1004:15
     |
1004 | pub unsafe fn bset_byte_offset(b: *const btree, i: *const core::ffi::c_void) -> usize {
     |               ^^^^^^^^^^^^^^^^

warning: function `btree_node_hashed` is never used
   --> crates/subvol/src/btree/cache.rs:109:15
    |
109 | pub unsafe fn btree_node_hashed(b: *const btree) -> bool {
    |               ^^^^^^^^^^^^^^^^^

warning: constant `BTREE_EVICTED_SIZE_HASH_MASK` is never used
   --> crates/subvol/src/btree/cache.rs:113:11
    |
113 | pub const BTREE_EVICTED_SIZE_HASH_MASK: u64 = (1u64 << 48) - 1;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_evicted_size_pack` is never used
   --> crates/subvol/src/btree/cache.rs:115:14
    |
115 | pub const fn btree_evicted_size_pack(hash: u64, live_u64s: u16) -> u64 {
    |              ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_evicted_size_record` is never used
   --> crates/subvol/src/btree/cache.rs:119:15
    |
119 | pub unsafe fn bch2_btree_evicted_size_record(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_evicted_size_lookup` is never used
   --> crates/subvol/src/btree/cache.rs:131:15
    |
131 | pub unsafe fn bch2_btree_evicted_size_lookup(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_fs_btree_evicted_size_init` is never used
   --> crates/subvol/src/btree/cache.rs:148:15
    |
148 | pub unsafe fn bch2_fs_btree_evicted_size_init(c: *mut super::types::bch_fs) -> i32 {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_fs_btree_evicted_size_exit` is never used
   --> crates/subvol/src/btree/cache.rs:158:15
    |
158 | pub unsafe fn bch2_fs_btree_evicted_size_exit(c: *mut super::types::bch_fs) {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_node_cache_state` is never used
   --> crates/subvol/src/btree/cache.rs:166:15
    |
166 | pub unsafe fn btree_node_cache_state(b: *const btree) -> btree_node_cache_state {
    |               ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_NODE_RECLAIM_shrinker` is never used
   --> crates/subvol/src/btree/cache.rs:179:11
    |
179 | pub const BTREE_NODE_RECLAIM_shrinker: u32 = 1 << 0;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_node_is_root` is never used
   --> crates/subvol/src/btree/cache.rs:229:11
    |
229 | unsafe fn btree_node_is_root(c: *const super::types::bch_fs, b: *const btree) -> bool {
    |           ^^^^^^^^^^^^^^^^^^

warning: function `bch2_node_pin` is never used
   --> crates/subvol/src/btree/cache.rs:234:15
    |
234 | pub unsafe fn bch2_node_pin(c: *mut super::types::bch_fs, b: *mut btree) {
    |               ^^^^^^^^^^^^^

warning: function `bch2_btree_cache_unpin` is never used
   --> crates/subvol/src/btree/cache.rs:255:15
    |
255 | pub unsafe fn bch2_btree_cache_unpin(c: *mut super::types::bch_fs) {
    |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_evict` is never used
   --> crates/subvol/src/btree/cache.rs:668:15
    |
668 | pub unsafe fn bch2_btree_node_evict(trans: *mut btree_trans, key: *const super::bkey::bkey_i) {
    |               ^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_WRITE_cache_reclaim` is never used
  --> crates/subvol/src/btree/io.rs:21:11
   |
21 | pub const BTREE_WRITE_cache_reclaim: u32 = 2;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_WRITE_initial` is never used
  --> crates/subvol/src/btree/io.rs:22:11
   |
22 | pub const BTREE_WRITE_initial: u32 = 0;
   |           ^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_WRITE_journal_reclaim` is never used
  --> crates/subvol/src/btree/io.rs:23:11
   |
23 | pub const BTREE_WRITE_journal_reclaim: u32 = 3;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_WRITE_interior` is never used
  --> crates/subvol/src/btree/io.rs:24:11
   |
24 | pub const BTREE_WRITE_interior: u32 = 4;
   |           ^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_WRITE_TYPE_MASK` is never used
  --> crates/subvol/src/btree/io.rs:25:11
   |
25 | pub const BTREE_WRITE_TYPE_MASK: u32 = 7;
   |           ^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_WRITE_TYPE_BITS` is never used
  --> crates/subvol/src/btree/io.rs:26:11
   |
26 | pub const BTREE_WRITE_TYPE_BITS: u32 = 3;
   |           ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_io_unlock` is never used
  --> crates/subvol/src/btree/io.rs:35:15
   |
35 | pub unsafe fn bch2_btree_node_io_unlock(b: *mut btree) {
   |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_io_lock` is never used
  --> crates/subvol/src/btree/io.rs:42:15
   |
42 | pub unsafe fn bch2_btree_node_io_lock(b: *mut btree) {
   |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_wait_on_read` is never used
  --> crates/subvol/src/btree/io.rs:50:15
   |
50 | pub unsafe fn bch2_btree_node_wait_on_read(_trans: *mut super::iter::btree_trans, b: *mut btree) {
   |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_wait_on_write` is never used
  --> crates/subvol/src/btree/io.rs:57:15
   |
57 | pub unsafe fn bch2_btree_node_wait_on_write(_trans: *mut super::iter::btree_trans, b: *mut btree) {
   |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_flush_all_reads` is never used
   --> crates/subvol/src/btree/io.rs:173:15
    |
173 | pub unsafe fn bch2_btree_flush_all_reads(c: *mut super::types::bch_fs) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_flush_all_writes` is never used
   --> crates/subvol/src/btree/io.rs:214:15
    |
214 | pub unsafe fn bch2_btree_flush_all_writes(c: *mut super::types::bch_fs) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_cancel_all_writes` is never used
   --> crates/subvol/src/btree/io.rs:255:15
    |
255 | pub unsafe fn bch2_btree_cancel_all_writes(c: *mut super::types::bch_fs) {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_drop_keys_outside_node` is never used
   --> crates/subvol/src/btree/io.rs:671:15
    |
671 | pub unsafe fn bch2_btree_node_drop_keys_outside_node(b: *mut btree) {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_get_noiter` is never used
   --> crates/subvol/src/btree/io.rs:859:15
    |
859 | pub unsafe fn bch2_btree_node_get_noiter(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_get` is never used
   --> crates/subvol/src/btree/io.rs:890:15
    |
890 | pub unsafe fn bch2_btree_node_get(
    |               ^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_prefetch` is never used
   --> crates/subvol/src/btree/io.rs:973:15
    |
973 | pub unsafe fn bch2_btree_node_prefetch(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_ITER_prefetch` is never used
  --> crates/subvol/src/btree/iter.rs:47:11
   |
47 | pub const BTREE_ITER_prefetch: u16 = 1 << 2;
   |           ^^^^^^^^^^^^^^^^^^^

warning: function `btree_id_cached` is never used
  --> crates/subvol/src/btree/iter.rs:62:4
   |
62 | fn btree_id_cached(btree_id: u8) -> bool {
   |    ^^^^^^^^^^^^^^^

warning: function `btree_type_has_snapshot_field` is never used
  --> crates/subvol/src/btree/iter.rs:66:4
   |
66 | fn btree_type_has_snapshot_field(_btree_id: u8) -> bool {
   |    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_flags` is never used
  --> crates/subvol/src/btree/iter.rs:71:15
   |
71 | pub unsafe fn bch2_btree_iter_flags(
   |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_path_node` is never used
   --> crates/subvol/src/btree/iter.rs:105:15
    |
105 | pub unsafe fn btree_path_node(path: *mut btree_path, level: usize) -> *mut btree {
    |               ^^^^^^^^^^^^^^^

warning: function `btree_node_parent` is never used
   --> crates/subvol/src/btree/iter.rs:112:15
    |
112 | pub unsafe fn btree_node_parent(path: *mut btree_path, b: *mut btree) -> *mut btree {
    |               ^^^^^^^^^^^^^^^^^

warning: function `btree_node_locked_type_nowrite` is never used
   --> crates/subvol/src/btree/iter.rs:195:15
    |
195 | pub unsafe fn btree_node_locked_type_nowrite(path: *const btree_path, level: usize) -> u8 {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_node_write_locked` is never used
   --> crates/subvol/src/btree/iter.rs:204:15
    |
204 | pub unsafe fn btree_node_write_locked(path: *const btree_path, level: usize) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_node_intent_locked` is never used
   --> crates/subvol/src/btree/iter.rs:208:15
    |
208 | pub unsafe fn btree_node_intent_locked(path: *const btree_path, level: usize) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_node_read_locked` is never used
   --> crates/subvol/src/btree/iter.rs:212:15
    |
212 | pub unsafe fn btree_node_read_locked(path: *const btree_path, level: usize) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_path_lowest_level_locked` is never used
   --> crates/subvol/src/btree/iter.rs:253:15
    |
253 | pub unsafe fn btree_path_lowest_level_locked(path: *const btree_path) -> Option<usize> {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_path_upgrade_norestart` is never used
   --> crates/subvol/src/btree/iter.rs:755:15
    |
755 | pub unsafe fn bch2_btree_path_upgrade_norestart(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_upgrade` is never used
   --> crates/subvol/src/btree/iter.rs:848:15
    |
848 | pub unsafe fn bch2_btree_node_upgrade(
    |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_path_can_relock` is never used
    --> crates/subvol/src/btree/iter.rs:1307:15
     |
1307 | pub unsafe fn bch2_btree_path_can_relock(_trans: *mut btree_trans, path: *mut btree_path) -> bool {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_iter_init_outlined` is never used
    --> crates/subvol/src/btree/iter.rs:1760:15
     |
1760 | pub unsafe fn bch2_trans_iter_init_outlined(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_set_snapshot` is never used
    --> crates/subvol/src/btree/iter.rs:1846:15
     |
1846 | pub unsafe fn bch2_btree_iter_set_snapshot(iter: *mut btree_iter, snapshot: u32) {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_set_pos_to_extent_start` is never used
    --> crates/subvol/src/btree/iter.rs:1856:15
     |
1856 | pub unsafe fn bch2_btree_iter_set_pos_to_extent_start(iter: *mut btree_iter) {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_set_btree_iter_dontneed` is never used
    --> crates/subvol/src/btree/iter.rs:1863:15
     |
1863 | pub unsafe fn bch2_set_btree_iter_dontneed(iter: *mut btree_iter) {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_get_iter` is never used
    --> crates/subvol/src/btree/iter.rs:1905:15
     |
1905 | pub unsafe fn bch2_btree_node_get_iter(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_peek_type` is never used
    --> crates/subvol/src/btree/iter.rs:1936:15
     |
1936 | pub unsafe fn bch2_btree_iter_peek_type(iter: *mut btree_iter, flags: u16) -> bkey_s_c {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_peek_prev_type` is never used
    --> crates/subvol/src/btree/iter.rs:1944:15
     |
1944 | pub unsafe fn bch2_btree_iter_peek_prev_type(iter: *mut btree_iter, flags: u16) -> bkey_s_c {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_peek_max_type` is never used
    --> crates/subvol/src/btree/iter.rs:1952:15
     |
1952 | pub unsafe fn bch2_btree_iter_peek_max_type(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_peek_and_restart_outlined` is never used
    --> crates/subvol/src/btree/iter.rs:1969:15
     |
1969 | pub unsafe fn bch2_btree_iter_peek_and_restart_outlined(iter: *mut btree_iter) -> bkey_s_c {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_next_slot` is never used
    --> crates/subvol/src/btree/iter.rs:2620:15
     |
2620 | pub unsafe fn bch2_btree_iter_next_slot(iter: *mut btree_iter) -> bkey_s_c {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_peek_node` is never used
    --> crates/subvol/src/btree/iter.rs:2628:15
     |
2628 | pub unsafe fn bch2_btree_iter_peek_node(iter: *mut btree_iter) -> *mut btree {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_peek_root` is never used
    --> crates/subvol/src/btree/iter.rs:2655:15
     |
2655 | pub unsafe fn bch2_btree_iter_peek_root(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_rewind` is never used
    --> crates/subvol/src/btree/iter.rs:2701:15
     |
2701 | pub unsafe fn bch2_btree_iter_rewind(iter: *mut btree_iter) -> bool {
     |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_prev` is never used
    --> crates/subvol/src/btree/iter.rs:2724:15
     |
2724 | pub unsafe fn bch2_btree_iter_prev(iter: *mut btree_iter) -> bkey_s_c {
     |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_prev_slot` is never used
    --> crates/subvol/src/btree/iter.rs:2732:15
     |
2732 | pub unsafe fn bch2_btree_iter_prev_slot(iter: *mut btree_iter) -> bkey_s_c {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_unlock_write` is never used
    --> crates/subvol/src/btree/iter.rs:3098:15
     |
3098 | pub unsafe fn bch2_trans_unlock_write(trans: *mut btree_trans) {
     |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_relock` is never used
    --> crates/subvol/src/btree/iter.rs:3128:15
     |
3128 | pub unsafe fn bch2_trans_relock(trans: *mut btree_trans) -> i32 {
     |               ^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_relock_notrace` is never used
    --> crates/subvol/src/btree/iter.rs:3132:15
     |
3132 | pub unsafe fn bch2_trans_relock_notrace(trans: *mut btree_trans) -> i32 {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_unlock_long` is never used
    --> crates/subvol/src/btree/iter.rs:3156:15
     |
3156 | pub unsafe fn bch2_trans_unlock_long(trans: *mut btree_trans) {
     |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_downgrade` is never used
    --> crates/subvol/src/btree/iter.rs:3160:15
     |
3160 | pub unsafe fn bch2_trans_downgrade(trans: *mut btree_trans) {
     |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_iter_next_all` is never used
   --> crates/subvol/src/btree/node_iter.rs:345:15
    |
345 | pub unsafe fn bch2_btree_node_iter_next_all(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_USES_WRITE_BUFFER_MASK` is never used
  --> crates/subvol/src/btree/types.rs:24:11
   |
24 | pub const BTREE_USES_WRITE_BUFFER_MASK: u64 = 0;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_type_uses_write_buffer` is never used
  --> crates/subvol/src/btree/types.rs:34:14
   |
34 | pub const fn btree_type_uses_write_buffer(btree: u8) -> bool {
   |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_VALIDATE_write` is never used
  --> crates/subvol/src/btree/types.rs:42:11
   |
42 | pub const BCH_VALIDATE_write: u8 = 1 << 0;
   |           ^^^^^^^^^^^^^^^^^^

warning: constant `BCH_VALIDATE_commit` is never used
  --> crates/subvol/src/btree/types.rs:43:11
   |
43 | pub const BCH_VALIDATE_commit: u8 = 1 << 1;
   |           ^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_VALIDATE_silent` is never used
  --> crates/subvol/src/btree/types.rs:44:11
   |
44 | pub const BCH_VALIDATE_silent: u8 = 1 << 2;
   |           ^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_VALIDATE_unknown` is never used
  --> crates/subvol/src/btree/types.rs:46:11
   |
46 | pub const BKEY_VALIDATE_unknown: u8 = 0;
   |           ^^^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_VALIDATE_superblock` is never used
  --> crates/subvol/src/btree/types.rs:47:11
   |
47 | pub const BKEY_VALIDATE_superblock: u8 = 1;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_VALIDATE_journal` is never used
  --> crates/subvol/src/btree/types.rs:48:11
   |
48 | pub const BKEY_VALIDATE_journal: u8 = 2;
   |           ^^^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_VALIDATE_btree_root` is never used
  --> crates/subvol/src/btree/types.rs:49:11
   |
49 | pub const BKEY_VALIDATE_btree_root: u8 = 3;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_VALIDATE_btree_node` is never used
  --> crates/subvol/src/btree/types.rs:50:11
   |
50 | pub const BKEY_VALIDATE_btree_node: u8 = 4;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_VALIDATE_commit` is never used
  --> crates/subvol/src/btree/types.rs:51:11
   |
51 | pub const BKEY_VALIDATE_commit: u8 = 5;
   |           ^^^^^^^^^^^^^^^^^^^^

warning: struct `bkey_validate_context` is never constructed
  --> crates/subvol/src/btree/types.rs:55:12
   |
55 | pub struct bkey_validate_context {
   |            ^^^^^^^^^^^^^^^^^^^^^

warning: struct `disk_reservation` is never constructed
  --> crates/subvol/src/btree/types.rs:68:12
   |
68 | pub struct disk_reservation {
   |            ^^^^^^^^^^^^^^^^

warning: constant `BCH_DISK_RESERVATION_NOFAIL` is never used
  --> crates/subvol/src/btree/types.rs:74:11
   |
74 | pub const BCH_DISK_RESERVATION_NOFAIL: u32 = 1 << 0;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_DISK_RESERVATION_PARTIAL` is never used
  --> crates/subvol/src/btree/types.rs:75:11
   |
75 | pub const BCH_DISK_RESERVATION_PARTIAL: u32 = 1 << 1;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: struct `bch_fs_usage_base` is never constructed
  --> crates/subvol/src/btree/types.rs:79:12
   |
79 | pub struct bch_fs_usage_base {
   |            ^^^^^^^^^^^^^^^^^

warning: struct `bch_fs_usage_short` is never constructed
  --> crates/subvol/src/btree/types.rs:89:12
   |
89 | pub struct bch_fs_usage_short {
   |            ^^^^^^^^^^^^^^^^^^

warning: struct `bch_fs_capacity_pcpu` is never constructed
  --> crates/subvol/src/btree/types.rs:97:12
   |
97 | pub struct bch_fs_capacity_pcpu {
   |            ^^^^^^^^^^^^^^^^^^^^

warning: constant `BSET_TREE_NR_TYPES` is never used
   --> crates/subvol/src/btree/types.rs:130:11
    |
130 | pub const BSET_TREE_NR_TYPES: usize = 3;
    |           ^^^^^^^^^^^^^^^^^^

warning: function `list_replace` is never used
   --> crates/subvol/src/btree/types.rs:197:15
    |
197 | pub unsafe fn list_replace(old: *const list_head, new: *mut list_head) {
    |               ^^^^^^^^^^^^

warning: function `list_replace_init` is never used
   --> crates/subvol/src/btree/types.rs:204:15
    |
204 | pub unsafe fn list_replace_init(old: *mut list_head, new: *mut list_head) {
    |               ^^^^^^^^^^^^^^^^^

warning: function `list_move` is never used
   --> crates/subvol/src/btree/types.rs:211:15
    |
211 | pub unsafe fn list_move(entry: *mut list_head, head: *mut list_head) {
    |               ^^^^^^^^^

warning: function `list_move_tail` is never used
   --> crates/subvol/src/btree/types.rs:216:15
    |
216 | pub unsafe fn list_move_tail(entry: *mut list_head, head: *mut list_head) {
    |               ^^^^^^^^^^^^^^

warning: function `list_empty` is never used
   --> crates/subvol/src/btree/types.rs:221:15
    |
221 | pub unsafe fn list_empty(head: *const list_head) -> bool {
    |               ^^^^^^^^^^

warning: function `list_empty_careful` is never used
   --> crates/subvol/src/btree/types.rs:225:15
    |
225 | pub unsafe fn list_empty_careful(head: *const list_head) -> bool {
    |               ^^^^^^^^^^^^^^^^^^

warning: function `list_splice_init` is never used
   --> crates/subvol/src/btree/types.rs:239:15
    |
239 | pub unsafe fn list_splice_init(list: *mut list_head, head: *mut list_head) {
    |               ^^^^^^^^^^^^^^^^

warning: function `list_splice_tail` is never used
   --> crates/subvol/src/btree/types.rs:244:15
    |
244 | pub unsafe fn list_splice_tail(list: *mut list_head, head: *mut list_head) {
    |               ^^^^^^^^^^^^^^^^

warning: function `list_splice_tail_init` is never used
   --> crates/subvol/src/btree/types.rs:257:15
    |
257 | pub unsafe fn list_splice_tail_init(list: *mut list_head, head: *mut list_head) {
    |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `list_count_nodes` is never used
   --> crates/subvol/src/btree/types.rs:262:15
    |
262 | pub unsafe fn list_count_nodes(head: *mut list_head) -> usize {
    |               ^^^^^^^^^^^^^^^^

warning: function `list_is_last` is never used
   --> crates/subvol/src/btree/types.rs:272:15
    |
272 | pub unsafe fn list_is_last(list: *const list_head, head: *const list_head) -> bool {
    |               ^^^^^^^^^^^^

warning: function `btree_node_pos` is never used
   --> crates/subvol/src/btree/types.rs:620:15
    |
620 | pub unsafe fn btree_node_pos(b: *mut btree_bkey_cached_common) -> super::bkey::bpos {
    |               ^^^^^^^^^^^^^^

warning: constant `BTREE_NODE_FLAGS_START` is never used
   --> crates/subvol/src/btree/types.rs:654:11
    |
654 | pub const BTREE_NODE_FLAGS_START: usize = 2;
    |           ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_NODE_dying` is never used
   --> crates/subvol/src/btree/types.rs:667:11
    |
667 | pub const BTREE_NODE_dying: usize = 15;
    |           ^^^^^^^^^^^^^^^^

warning: constant `BTREE_NODE_need_rewrite_error` is never used
   --> crates/subvol/src/btree/types.rs:670:11
    |
670 | pub const BTREE_NODE_need_rewrite_error: usize = 18;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_NODE_need_rewrite_ptr_written_zero` is never used
   --> crates/subvol/src/btree/types.rs:671:11
    |
671 | pub const BTREE_NODE_need_rewrite_ptr_written_zero: usize = 19;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `clear_btree_node_read_error` is never used
   --> crates/subvol/src/btree/types.rs:701:5
    |
701 |     clear_btree_node_read_error,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_need_write` is never used
   --> crates/subvol/src/btree/types.rs:712:5
    |
712 |     set_btree_node_need_write,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_need_write` is never used
   --> crates/subvol/src/btree/types.rs:713:5
    |
713 |     clear_btree_node_need_write,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_write_blocked` is never used
   --> crates/subvol/src/btree/types.rs:718:5
    |
718 |     set_btree_node_write_blocked,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_write_blocked` is never used
   --> crates/subvol/src/btree/types.rs:719:5
    |
719 |     clear_btree_node_write_blocked,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_will_make_reachable` is never used
   --> crates/subvol/src/btree/types.rs:724:5
    |
724 |     set_btree_node_will_make_reachable,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_will_make_reachable` is never used
   --> crates/subvol/src/btree/types.rs:725:5
    |
725 |     clear_btree_node_will_make_reachable,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_noevict` is never used
   --> crates/subvol/src/btree/types.rs:730:5
    |
730 |     set_btree_node_noevict,
    |     ^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_write_idx` is never used
   --> crates/subvol/src/btree/types.rs:734:15
    |
734 | pub unsafe fn set_btree_node_write_idx(b: *mut btree) {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `clear_btree_node_write_idx` is never used
   --> crates/subvol/src/btree/types.rs:738:15
    |
738 | pub unsafe fn clear_btree_node_write_idx(b: *mut btree) {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `clear_btree_node_accessed` is never used
   --> crates/subvol/src/btree/types.rs:744:5
    |
744 |     clear_btree_node_accessed,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_write_in_flight` is never used
   --> crates/subvol/src/btree/types.rs:749:5
    |
749 |     set_btree_node_write_in_flight,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_write_in_flight` is never used
   --> crates/subvol/src/btree/types.rs:750:5
    |
750 |     clear_btree_node_write_in_flight,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_node_write_in_flight_inner` is never used
   --> crates/subvol/src/btree/types.rs:754:5
    |
754 |     btree_node_write_in_flight_inner,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_write_in_flight_inner` is never used
   --> crates/subvol/src/btree/types.rs:755:5
    |
755 |     set_btree_node_write_in_flight_inner,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_write_in_flight_inner` is never used
   --> crates/subvol/src/btree/types.rs:756:5
    |
756 |     clear_btree_node_write_in_flight_inner,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_just_written` is never used
   --> crates/subvol/src/btree/types.rs:761:5
    |
761 |     set_btree_node_just_written,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_node_dying` is never used
   --> crates/subvol/src/btree/types.rs:766:5
    |
766 |     btree_node_dying,
    |     ^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_dying` is never used
   --> crates/subvol/src/btree/types.rs:767:5
    |
767 |     set_btree_node_dying,
    |     ^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_dying` is never used
   --> crates/subvol/src/btree/types.rs:768:5
    |
768 |     clear_btree_node_dying,
    |     ^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_node_fake` is never used
   --> crates/subvol/src/btree/types.rs:772:5
    |
772 |     btree_node_fake,
    |     ^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_node_need_rewrite` is never used
   --> crates/subvol/src/btree/types.rs:778:5
    |
778 |     btree_node_need_rewrite,
    |     ^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_node_need_rewrite_error` is never used
   --> crates/subvol/src/btree/types.rs:784:5
    |
784 |     btree_node_need_rewrite_error,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_need_rewrite_error` is never used
   --> crates/subvol/src/btree/types.rs:785:5
    |
785 |     set_btree_node_need_rewrite_error,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_need_rewrite_error` is never used
   --> crates/subvol/src/btree/types.rs:786:5
    |
786 |     clear_btree_node_need_rewrite_error,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_node_need_rewrite_ptr_written_zero` is never used
   --> crates/subvol/src/btree/types.rs:790:5
    |
790 |     btree_node_need_rewrite_ptr_written_zero,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_need_rewrite_ptr_written_zero` is never used
   --> crates/subvol/src/btree/types.rs:791:5
    |
791 |     set_btree_node_need_rewrite_ptr_written_zero,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_need_rewrite_ptr_written_zero` is never used
   --> crates/subvol/src/btree/types.rs:792:5
    |
792 |     clear_btree_node_need_rewrite_ptr_written_zero,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_never_write` is never used
   --> crates/subvol/src/btree/types.rs:797:5
    |
797 |     set_btree_node_never_write,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_never_write` is never used
   --> crates/subvol/src/btree/types.rs:798:5
    |
798 |     clear_btree_node_never_write,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_pinned` is never used
   --> crates/subvol/src/btree/types.rs:803:5
    |
803 |     set_btree_node_pinned,
    |     ^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_pinned` is never used
   --> crates/subvol/src/btree/types.rs:804:5
    |
804 |     clear_btree_node_pinned,
    |     ^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_bset_last` is never used
   --> crates/subvol/src/btree/types.rs:927:15
    |
927 | pub unsafe fn btree_bset_last(b: *mut btree) -> *mut disk_bset {
    |               ^^^^^^^^^^^^^^^

warning: function `bch2_trans_kmalloc_ip` is never used
   --> crates/subvol/src/btree/update.rs:133:15
    |
133 | pub unsafe fn bch2_trans_kmalloc_ip(trans: *mut btree_trans, size: usize, _ip: usize) -> *mut u8 {
    |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_kmalloc_nomemzero_ip` is never used
   --> crates/subvol/src/btree/update.rs:137:15
    |
137 | pub unsafe fn bch2_trans_kmalloc_nomemzero_ip(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_subbuf_alloc` is never used
   --> crates/subvol/src/btree/update.rs:191:15
    |
191 | pub unsafe fn bch2_trans_subbuf_alloc(
    |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_subbuf_alloc_ip` is never used
   --> crates/subvol/src/btree/update.rs:203:15
    |
203 | pub unsafe fn bch2_trans_subbuf_alloc_ip(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_subbuf_reserve` is never used
   --> crates/subvol/src/btree/update.rs:212:15
    |
212 | pub unsafe fn bch2_trans_subbuf_reserve(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_jset_entry_alloc_ip` is never used
   --> crates/subvol/src/btree/update.rs:225:15
    |
225 | pub unsafe fn bch2_trans_jset_entry_alloc_ip(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_jset_entry_alloc` is never used
   --> crates/subvol/src/btree/update.rs:246:15
    |
246 | pub unsafe fn bch2_trans_jset_entry_alloc(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_get_mut_noupdate` is never used
   --> crates/subvol/src/btree/update.rs:287:15
    |
287 | pub unsafe fn bch2_bkey_get_mut_noupdate(iter: *mut btree_iter) -> *mut bkey_i {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_make_mut` is never used
   --> crates/subvol/src/btree/update.rs:298:15
    |
298 | pub unsafe fn bch2_bkey_make_mut(
    |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_get_mut` is never used
   --> crates/subvol/src/btree/update.rs:318:15
    |
318 | pub unsafe fn bch2_bkey_get_mut(
    |               ^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_get_mut_minsize` is never used
   --> crates/subvol/src/btree/update.rs:327:15
    |
327 | pub unsafe fn bch2_bkey_get_mut_minsize(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_alloc` is never used
   --> crates/subvol/src/btree/update.rs:378:15
    |
378 | pub unsafe fn bch2_bkey_alloc(
    |               ^^^^^^^^^^^^^^^

warning: constant `BTREE_UPDATE_none` is never used
   --> crates/subvol/src/btree/update.rs:410:11
    |
410 | pub const BTREE_UPDATE_none: u32 = 0;
    |           ^^^^^^^^^^^^^^^^^

warning: constant `BTREE_TRIGGER_transactional` is never used
   --> crates/subvol/src/btree/update.rs:414:11
    |
414 | pub const BTREE_TRIGGER_transactional: u32 = 1 << 22;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_TRIGGER_gc` is never used
   --> crates/subvol/src/btree/update.rs:416:11
    |
416 | pub const BTREE_TRIGGER_gc: u32 = 1 << 24;
    |           ^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_no_enospc` is never used
   --> crates/subvol/src/btree/update.rs:420:11
    |
420 | pub const BCH_TRANS_COMMIT_no_enospc: u32 = 1 << (crate::journal::BCH_WATERMARK_BITS + 0);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_no_check_rw` is never used
   --> crates/subvol/src/btree/update.rs:421:11
    |
421 | pub const BCH_TRANS_COMMIT_no_check_rw: u32 = 1 << (crate::journal::BCH_WATERMARK_BITS + 1);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_no_journal_res` is never used
   --> crates/subvol/src/btree/update.rs:422:11
    |
422 | pub const BCH_TRANS_COMMIT_no_journal_res: u32 = 1 << (crate::journal::BCH_WATERMARK_BITS + 2);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_no_skip_noops` is never used
   --> crates/subvol/src/btree/update.rs:423:11
    |
423 | pub const BCH_TRANS_COMMIT_no_skip_noops: u32 = 1 << (crate::journal::BCH_WATERMARK_BITS + 3);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_journal_reclaim` is never used
   --> crates/subvol/src/btree/update.rs:424:11
    |
424 | pub const BCH_TRANS_COMMIT_journal_reclaim: u32 = 1 << (crate::journal::BCH_WATERMARK_BITS + 4);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_journal_replay` is never used
   --> crates/subvol/src/btree/update.rs:425:11
    |
425 | pub const BCH_TRANS_COMMIT_journal_replay: u32 = 1 << (crate::journal::BCH_WATERMARK_BITS + 5);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_skip_accounting_apply` is never used
   --> crates/subvol/src/btree/update.rs:426:11
    |
426 | pub const BCH_TRANS_COMMIT_skip_accounting_apply: u32 =
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trigger_get_mutable_new` is never used
   --> crates/subvol/src/btree/update.rs:920:15
    |
920 | pub unsafe fn bch2_trigger_get_mutable_new(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_delete` is never used
    --> crates/subvol/src/btree/update.rs:1086:15
     |
1086 | pub unsafe fn bch2_btree_delete(
     |               ^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_insert_trans` is never used
    --> crates/subvol/src/btree/update.rs:1139:15
     |
1139 | pub unsafe fn bch2_btree_insert_trans(
     |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_insert` is never used
    --> crates/subvol/src/btree/update.rs:1164:15
     |
1164 | pub unsafe fn bch2_btree_insert(
     |               ^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_insert_clone_trans` is never used
    --> crates/subvol/src/btree/update.rs:1184:15
     |
1184 | pub unsafe fn bch2_btree_insert_clone_trans(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_get_empty_slot` is never used
    --> crates/subvol/src/btree/update.rs:1200:15
     |
1200 | pub unsafe fn bch2_bkey_get_empty_slot(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_delete_range_trans` is never used
    --> crates/subvol/src/btree/update.rs:1234:15
     |
1234 | pub unsafe fn bch2_btree_delete_range_trans(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_delete_range` is never used
    --> crates/subvol/src/btree/update.rs:1309:15
     |
1309 | pub unsafe fn bch2_btree_delete_range(
     |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_bit_mod_iter` is never used
    --> crates/subvol/src/btree/update.rs:1329:15
     |
1329 | pub unsafe fn bch2_btree_bit_mod_iter(
     |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_bit_mod` is never used
    --> crates/subvol/src/btree/update.rs:1354:15
     |
1354 | pub unsafe fn bch2_btree_bit_mod(
     |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_update_buffered` is never used
    --> crates/subvol/src/btree/update.rs:1375:15
     |
1375 | pub unsafe fn bch2_trans_update_buffered(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_bit_mod_buffered` is never used
    --> crates/subvol/src/btree/update.rs:1402:15
     |
1402 | pub unsafe fn bch2_btree_bit_mod_buffered(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_delete_at_buffered` is never used
    --> crates/subvol/src/btree/update.rs:1424:15
     |
1424 | pub unsafe fn bch2_btree_delete_at_buffered(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_log_bkey` is never used
    --> crates/subvol/src/btree/update.rs:1432:15
     |
1432 | pub unsafe fn bch2_trans_log_bkey(
     |               ^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_log_str` is never used
    --> crates/subvol/src/btree/update.rs:1457:15
     |
1457 | pub unsafe fn bch2_trans_log_str(trans: *mut btree_trans, str_: *const u8) -> i32 {
     |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_update_buf` is never used
    --> crates/subvol/src/btree/update.rs:1535:15
     |
1535 | pub unsafe fn bch2_trans_update_buf(
     |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_commit_hook` is never used
    --> crates/subvol/src/btree/update.rs:1552:15
     |
1552 | pub unsafe fn bch2_trans_commit_hook(trans: *mut btree_trans, hook: *mut btree_trans_commit_hook) {
     |               ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_CSUM_chacha20_poly1305_80` is never used
 --> crates/subvol/src/checksum.rs:4:11
  |
4 | pub const BCH_CSUM_chacha20_poly1305_80: u32 = 3;
  |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_CSUM_chacha20_poly1305_128` is never used
 --> crates/subvol/src/checksum.rs:5:11
  |
5 | pub const BCH_CSUM_chacha20_poly1305_128: u32 = 4;
  |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_checksum_mergeable` is never used
  --> crates/subvol/src/checksum.rs:12:14
   |
12 | pub const fn bch2_checksum_mergeable(type_: u32) -> bool {
   |              ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_checksum_merge` is never used
  --> crates/subvol/src/checksum.rs:16:8
   |
16 | pub fn bch2_checksum_merge(
   |        ^^^^^^^^^^^^^^^^^^^

warning: function `bch2_keylist_empty` is never used
  --> crates/subvol/src/data/keylist.rs:51:15
   |
51 | pub unsafe fn bch2_keylist_empty(list: *const keylist) -> bool {
   |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_keylist_u64s` is never used
  --> crates/subvol/src/data/keylist.rs:55:15
   |
55 | pub unsafe fn bch2_keylist_u64s(list: *const keylist) -> usize {
   |               ^^^^^^^^^^^^^^^^^

warning: function `bch2_keylist_bytes` is never used
  --> crates/subvol/src/data/keylist.rs:59:15
   |
59 | pub unsafe fn bch2_keylist_bytes(list: *const keylist) -> usize {
   |               ^^^^^^^^^^^^^^^^^^

warning: constant `JOURNAL_ENTRY_SIZE_MIN` is never used
  --> crates/subvol/src/journal.rs:12:11
   |
12 | pub const JOURNAL_ENTRY_SIZE_MIN: usize = 64 << 10;
   |           ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_JSET_ENTRY_overwrite` is never used
  --> crates/subvol/src/journal.rs:25:11
   |
25 | pub const BCH_JSET_ENTRY_overwrite: u8 = 10;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_JSET_ENTRY_log` is never used
  --> crates/subvol/src/journal.rs:27:11
   |
27 | pub const BCH_JSET_ENTRY_log: u8 = 9;
   |           ^^^^^^^^^^^^^^^^^^

warning: constant `BCH_JSET_ENTRY_log_bkey` is never used
  --> crates/subvol/src/journal.rs:28:11
   |
28 | pub const BCH_JSET_ENTRY_log_bkey: u8 = 13;
   |           ^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `JOURNAL_degraded` is never used
  --> crates/subvol/src/journal.rs:31:11
   |
31 | pub const JOURNAL_degraded: usize = 0;
   |           ^^^^^^^^^^^^^^^^

warning: constant `JOURNAL_running` is never used
  --> crates/subvol/src/journal.rs:33:11
   |
33 | pub const JOURNAL_running: usize = 2;
   |           ^^^^^^^^^^^^^^^

warning: constant `JOURNAL_need_flush_write` is never used
  --> crates/subvol/src/journal.rs:35:11
   |
35 | pub const JOURNAL_need_flush_write: usize = 4;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `JOURNAL_low_on_wb` is never used
  --> crates/subvol/src/journal.rs:39:11
   |
39 | pub const JOURNAL_low_on_wb: usize = 8;
   |           ^^^^^^^^^^^^^^^^^

warning: function `JSET_CSUM_TYPE` is never used
  --> crates/subvol/src/journal.rs:76:14
   |
76 | pub const fn JSET_CSUM_TYPE(j: &jset) -> u32 {
   |              ^^^^^^^^^^^^^^

warning: function `JSET_BIG_ENDIAN` is never used
  --> crates/subvol/src/journal.rs:81:14
   |
81 | pub const fn JSET_BIG_ENDIAN(j: &jset) -> u32 {
   |              ^^^^^^^^^^^^^^^

warning: function `SET_JSET_NO_FLUSH` is never used
  --> crates/subvol/src/journal.rs:91:8
   |
91 | pub fn SET_JSET_NO_FLUSH(j: &mut jset, value: u32) {
   |        ^^^^^^^^^^^^^^^^^

warning: variants `BCH_WATERMARK_normal`, `BCH_WATERMARK_copygc`, `BCH_WATERMARK_btree`, `BCH_WATERMARK_btree_copygc`, and `BCH_WATERMARK_interior_updates` are never constructed
   --> crates/subvol/src/journal.rs:160:5
    |
158 | pub enum bch_watermark {
    |          ------------- variants in this enum
159 |     BCH_WATERMARK_stripe,
160 |     BCH_WATERMARK_normal,
    |     ^^^^^^^^^^^^^^^^^^^^
161 |     BCH_WATERMARK_copygc,
    |     ^^^^^^^^^^^^^^^^^^^^
162 |     BCH_WATERMARK_btree,
    |     ^^^^^^^^^^^^^^^^^^^
163 |     BCH_WATERMARK_btree_copygc,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^
164 |     BCH_WATERMARK_reclaim,
165 |     BCH_WATERMARK_interior_updates,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: `bch_watermark` has derived impls for the traits `Debug` and `Clone`, but these are intentionally ignored during dead code analysis

warning: variant `JOURNAL_PIN_TYPE_key_cache` is never constructed
   --> crates/subvol/src/journal.rs:190:5
    |
185 | pub enum journal_pin_type {
    |          ---------------- variant in this enum
...
190 |     JOURNAL_PIN_TYPE_key_cache,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: `journal_pin_type` has derived impls for the traits `Debug` and `Clone`, but these are intentionally ignored during dead code analysis

warning: fields `devs_nr`, `devs`, and `bytes` are never read
   --> crates/subvol/src/journal.rs:203:9
    |
198 | pub struct journal_entry_pin_list {
    |            ---------------------- fields in this struct
...
203 |     pub devs_nr: u8,
    |         ^^^^^^^
204 |     pub devs: [u8; crate::btree::types::BCH_BKEY_PTRS_MAX],
    |         ^^^^
205 |     pub bytes: u32,
    |         ^^^^^
    |
    = note: `journal_entry_pin_list` has a derived impl for the trait `Debug`, but this is intentionally ignored during dead code analysis

warning: function `journal_pin_list_init` is never used
   --> crates/subvol/src/journal.rs:338:8
    |
338 | pub fn journal_pin_list_init(p: &mut journal_entry_pin_list, count: u32) {
    |        ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_journal_pin_update` is never used
   --> crates/subvol/src/journal.rs:614:15
    |
614 | pub unsafe fn bch2_journal_pin_update(
    |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_key_deleted_in_journal` is never used
    --> crates/subvol/src/journal.rs:2081:15
     |
2081 | pub unsafe fn bch2_key_deleted_in_journal(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `six_lock_contended` is never used
   --> crates/subvol/src/lock/six.rs:510:8
    |
510 | pub fn six_lock_contended(
    |        ^^^^^^^^^^^^^^^^^^

warning: function `six_trylock_convert` is never used
   --> crates/subvol/src/lock/six.rs:555:8
    |
555 | pub fn six_trylock_convert(lock: &six_lock, from: six_lock_type, to: six_lock_type) -> bool {
    |        ^^^^^^^^^^^^^^^^^^^

warning: function `six_trylock_read` is never used
   --> crates/subvol/src/lock/six.rs:654:5
    |
654 |     six_trylock_read,
    |     ^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `six_type_wrappers` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `six_relock_read` is never used
   --> crates/subvol/src/lock/six.rs:655:5
    |
655 |     six_relock_read,
    |     ^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `six_type_wrappers` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `six_relock_intent` is never used
   --> crates/subvol/src/lock/six.rs:662:5
    |
662 |     six_relock_intent,
    |     ^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `six_type_wrappers` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `six_relock_write` is never used
   --> crates/subvol/src/lock/six.rs:669:5
    |
669 |     six_relock_write,
    |     ^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `six_type_wrappers` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: constant `BCH_SB_SECTOR` is never used
 --> crates/subvol/src/sb/mod.rs:4:11
  |
4 | pub const BCH_SB_SECTOR: u64 = 8;
  |           ^^^^^^^^^^^^^

warning: constant `BCH_SB_LAYOUT_SECTOR` is never used
 --> crates/subvol/src/sb/mod.rs:5:11
  |
5 | pub const BCH_SB_LAYOUT_SECTOR: u64 = 7;
  |           ^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_SB_LAYOUT_SIZE_BITS_MAX` is never used
 --> crates/subvol/src/sb/mod.rs:6:11
  |
6 | pub const BCH_SB_LAYOUT_SIZE_BITS_MAX: u8 = 16;
  |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_SB_MEMBERS_MAX` is never used
 --> crates/subvol/src/sb/mod.rs:7:11
  |
7 | pub const BCH_SB_MEMBERS_MAX: usize = 256;
  |           ^^^^^^^^^^^^^^^^^^

warning: constant `BCH_SB_MEMBER_INVALID` is never used
 --> crates/subvol/src/sb/mod.rs:8:11
  |
8 | pub const BCH_SB_MEMBER_INVALID: u8 = 255;
  |           ^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_SB_MEMBER_DELETED_UUID` is never used
 --> crates/subvol/src/sb/mod.rs:9:11
  |
9 | pub const BCH_SB_MEMBER_DELETED_UUID: [u8; 16] = [
  |           ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `BCH_VERSION_MAJOR` is never used
  --> crates/subvol/src/sb/mod.rs:23:14
   |
23 | pub const fn BCH_VERSION_MAJOR(version: u16) -> u16 {
   |              ^^^^^^^^^^^^^^^^^

warning: function `BCH_VERSION_MINOR` is never used
  --> crates/subvol/src/sb/mod.rs:27:14
   |
27 | pub const fn BCH_VERSION_MINOR(version: u16) -> u16 {
   |              ^^^^^^^^^^^^^^^^^

warning: function `bch2_member_alive` is never used
  --> crates/subvol/src/sb/mod.rs:33:8
   |
33 | pub fn bch2_member_alive(member: &bch_member) -> bool {
   |        ^^^^^^^^^^^^^^^^^

warning: function `bch2_mi_to_cpu` is never used
  --> crates/subvol/src/sb/mod.rs:37:8
   |
37 | pub fn bch2_mi_to_cpu(member: &bch_member) -> bch_member_cpu {
   |        ^^^^^^^^^^^^^^

warning: struct `bch_member_cpu` is never constructed
  --> crates/subvol/src/sb/mod.rs:93:12
   |
93 | pub struct bch_member_cpu {
   |            ^^^^^^^^^^^^^^

warning: constant `BCH_SB_HANDLE_HAVE_BIO` is never used
   --> crates/subvol/src/sb/mod.rs:280:11
    |
280 | pub const BCH_SB_HANDLE_HAVE_BIO: u32 = 1 << 1;
    |           ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_layout` is never used
 --> crates/subvol/src/sb/io.rs:8:7
  |
8 | const BCH_ERR_invalid_sb_layout: i32 = -1;
  |       ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_layout_type` is never used
 --> crates/subvol/src/sb/io.rs:9:7
  |
9 | const BCH_ERR_invalid_sb_layout_type: i32 = -2;
  |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_layout_nr_superblocks` is never used
  --> crates/subvol/src/sb/io.rs:10:7
   |
10 | const BCH_ERR_invalid_sb_layout_nr_superblocks: i32 = -3;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_layout_superblocks_overlap` is never used
  --> crates/subvol/src/sb/io.rs:11:7
   |
11 | const BCH_ERR_invalid_sb_layout_superblocks_overlap: i32 = -4;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_layout_sb_max_size_bits` is never used
  --> crates/subvol/src/sb/io.rs:12:7
   |
12 | const BCH_ERR_invalid_sb_layout_sb_max_size_bits: i32 = -5;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_version` is never used
  --> crates/subvol/src/sb/io.rs:13:7
   |
13 | const BCH_ERR_invalid_sb_version: i32 = -6;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_features` is never used
  --> crates/subvol/src/sb/io.rs:16:7
   |
16 | const BCH_ERR_invalid_sb_features: i32 = -15;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_uuid` is never used
  --> crates/subvol/src/sb/io.rs:17:7
   |
17 | const BCH_ERR_invalid_sb_uuid: i32 = -16;
   |       ^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_offset` is never used
  --> crates/subvol/src/sb/io.rs:18:7
   |
18 | const BCH_ERR_invalid_sb_offset: i32 = -17;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_too_many_members` is never used
  --> crates/subvol/src/sb/io.rs:19:7
   |
19 | const BCH_ERR_invalid_sb_too_many_members: i32 = -18;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_dev_idx` is never used
  --> crates/subvol/src/sb/io.rs:20:7
   |
20 | const BCH_ERR_invalid_sb_dev_idx: i32 = -19;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_time_precision` is never used
  --> crates/subvol/src/sb/io.rs:21:7
   |
21 | const BCH_ERR_invalid_sb_time_precision: i32 = -20;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_field_size` is never used
  --> crates/subvol/src/sb/io.rs:22:7
   |
22 | const BCH_ERR_invalid_sb_field_size: i32 = -21;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_members_missing` is never used
  --> crates/subvol/src/sb/io.rs:23:7
   |
23 | const BCH_ERR_invalid_sb_members_missing: i32 = -22;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_members` is never used
  --> crates/subvol/src/sb/io.rs:24:7
   |
24 | const BCH_ERR_invalid_sb_members: i32 = -23;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_journal` is never used
  --> crates/subvol/src/sb/io.rs:25:7
   |
25 | const BCH_ERR_invalid_sb_journal: i32 = -24;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_field_type` is never used
  --> crates/subvol/src/sb/io.rs:26:7
   |
26 | const BCH_ERR_invalid_sb_field_type: i32 = -25;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_sb_field_get_minsize_id` is never used
   --> crates/subvol/src/sb/io.rs:166:15
    |
166 | pub unsafe fn bch2_sb_field_get_minsize_id(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_sb_field_delete` is never used
   --> crates/subvol/src/sb/io.rs:178:15
    |
178 | pub unsafe fn bch2_sb_field_delete(sb: *mut bch_sb_handle, type_: u32) {
    |               ^^^^^^^^^^^^^^^^^^^^

warning: function `validate_sb_layout` is never used
   --> crates/subvol/src/sb/io.rs:185:8
    |
185 | pub fn validate_sb_layout(layout: &bch_sb_layout) -> i32 {
    |        ^^^^^^^^^^^^^^^^^^

warning: function `bch2_sb_compatible` is never used
   --> crates/subvol/src/sb/io.rs:214:8
    |
214 | pub fn bch2_sb_compatible(sb: &bch_sb) -> i32 {
    |        ^^^^^^^^^^^^^^^^^^

warning: function `BCH_SB_VERSION_INCOMPAT` is never used
   --> crates/subvol/src/sb/io.rs:260:4
    |
260 | fn BCH_SB_VERSION_INCOMPAT(sb: &bch_sb) -> u16 {
    |    ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `BCH_SB_VERSION_INCOMPAT_ALLOWED` is never used
   --> crates/subvol/src/sb/io.rs:264:4
    |
264 | fn BCH_SB_VERSION_INCOMPAT_ALLOWED(sb: &bch_sb) -> u16 {
    |    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_SB_VERSION_INCOMPAT_ALLOWED` is never used
   --> crates/subvol/src/sb/io.rs:268:4
    |
268 | fn SET_BCH_SB_VERSION_INCOMPAT_ALLOWED(sb: &mut bch_sb, value: u16) {
    |    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `validate_member` is never used
   --> crates/subvol/src/sb/io.rs:273:4
    |
273 | fn validate_member(member: bch_member, sb: &bch_sb, _index: usize) -> i32 {
    |    ^^^^^^^^^^^^^^^

warning: function `bch2_sb_members_v2_validate` is never used
   --> crates/subvol/src/sb/io.rs:299:11
    |
299 | unsafe fn bch2_sb_members_v2_validate(sb: *mut bch_sb, field: *mut bch_sb_field) -> i32 {
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_sb_journal_v2_validate` is never used
   --> crates/subvol/src/sb/io.rs:319:11
    |
319 | unsafe fn bch2_sb_journal_v2_validate(sb: *mut bch_sb, field: *mut bch_sb_field) -> i32 {
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_sb_field_validate` is never used
   --> crates/subvol/src/sb/io.rs:365:11
    |
365 | unsafe fn bch2_sb_field_validate(sb: *mut bch_sb, field: *mut bch_sb_field) -> i32 {
    |           ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_sb_validate` is never used
   --> crates/subvol/src/sb/io.rs:373:15
    |
373 | pub unsafe fn bch2_sb_validate(
    |               ^^^^^^^^^^^^^^^^

warning: function `BCH_SB_CSUM_TYPE` is never used
   --> crates/subvol/src/sb/io.rs:471:4
    |
471 | fn BCH_SB_CSUM_TYPE(sb: &bch_sb) -> u32 {
    |    ^^^^^^^^^^^^^^^^

warning: function `read_one_super` is never used
   --> crates/subvol/src/sb/io.rs:481:11
    |
481 | unsafe fn read_one_super(sb: *mut bch_sb_handle, offset: u64) -> i32 {
    |           ^^^^^^^^^^^^^^

warning: function `read_layout_sector` is never used
   --> crates/subvol/src/sb/io.rs:539:11
    |
539 | unsafe fn read_layout_sector(sb: *mut bch_sb_handle, layout: *mut bch_sb_layout) -> i32 {
    |           ^^^^^^^^^^^^^^^^^^

warning: function `read_backup_supers` is never used
   --> crates/subvol/src/sb/io.rs:559:11
    |
559 | unsafe fn read_backup_supers(
    |           ^^^^^^^^^^^^^^^^^^

warning: function `bch2_read_super` is never used
   --> crates/subvol/src/sb/io.rs:597:15
    |
597 | pub unsafe fn bch2_read_super(
    |               ^^^^^^^^^^^^^^^

warning: function `snapshot_list_merge` is never used
  --> crates/subvol/src/snapshot.rs:91:15
   |
91 | pub unsafe fn snapshot_list_merge(
   |               ^^^^^^^^^^^^^^^^^^^

warning: struct `bch_snapshot_tree` is never constructed
   --> crates/subvol/src/snapshot.rs:123:12
    |
123 | pub struct bch_snapshot_tree {
    |            ^^^^^^^^^^^^^^^^^

warning: struct `bkey_i_snapshot` is never constructed
   --> crates/subvol/src/snapshot.rs:131:12
    |
131 | pub struct bkey_i_snapshot {
    |            ^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_parent` is never used
   --> crates/subvol/src/snapshot.rs:193:8
    |
193 | pub fn bch2_snapshot_parent(c: &bch_fs, id: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_tree` is never used
   --> crates/subvol/src/snapshot.rs:198:8
    |
198 | pub fn bch2_snapshot_tree(c: &bch_fs, id: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshots_same_tree` is never used
   --> crates/subvol/src/snapshot.rs:203:8
    |
203 | pub fn bch2_snapshots_same_tree(c: &bch_fs, id1: u32, id2: u32) -> bool {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_nth_parent` is never used
   --> crates/subvol/src/snapshot.rs:214:8
    |
214 | pub fn bch2_snapshot_nth_parent(c: &bch_fs, mut id: u32, mut n: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_skiplist_get` is never used
   --> crates/subvol/src/snapshot.rs:223:8
    |
223 | pub fn bch2_snapshot_skiplist_get(c: &bch_fs, mut id: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_root` is never used
   --> crates/subvol/src/snapshot.rs:248:8
    |
248 | pub fn bch2_snapshot_root(c: &bch_fs, mut id: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_id_state` is never used
   --> crates/subvol/src/snapshot.rs:259:8
    |
259 | pub fn bch2_snapshot_id_state(c: &bch_fs, id: u32) -> snapshot_id_state {
    |        ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_exists` is never used
   --> crates/subvol/src/snapshot.rs:264:8
    |
264 | pub fn bch2_snapshot_exists(c: &bch_fs, id: u32) -> bool {
    |        ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_depth` is never used
   --> crates/subvol/src/snapshot.rs:285:8
    |
285 | pub fn bch2_snapshot_depth(c: &bch_fs, parent: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_has_children` is never used
   --> crates/subvol/src/snapshot.rs:296:8
    |
296 | pub fn bch2_snapshot_has_children(c: &bch_fs, id: u32) -> bool {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_live_descendent` is never used
   --> crates/subvol/src/snapshot.rs:303:8
    |
303 | pub fn bch2_snapshot_live_descendent(c: &bch_fs, mut id: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_is_ancestor_early` is never used
   --> crates/subvol/src/snapshot.rs:339:8
    |
339 | pub fn bch2_snapshot_is_ancestor_early(c: &bch_fs, mut id: u32, ancestor: u32) -> bool {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_tree_next` is never used
   --> crates/subvol/src/snapshot.rs:470:8
    |
470 | pub fn bch2_snapshot_tree_next(c: &bch_fs, id: u32, depth: &mut u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bit_spin_wake` is never used
  --> crates/subvol/src/util/bit_spinlock.rs:15:15
   |
15 | pub unsafe fn bit_spin_wake(_nr: usize, _addr: *const AtomicUsize) {}
   |               ^^^^^^^^^^^^^

warning: function `eytzinger1_last` is never used
  --> crates/subvol/src/util/eytzinger.rs:26:14
   |
26 | pub const fn eytzinger1_last(size: u32) -> u32 {
   |              ^^^^^^^^^^^^^^^

warning: function `eytzinger1_to_inorder` is never used
  --> crates/subvol/src/util/eytzinger.rs:93:14
   |
93 | pub const fn eytzinger1_to_inorder(i: u32, size: u32) -> u32 {
   |              ^^^^^^^^^^^^^^^^^^^^^

warning: function `inorder_to_eytzinger1` is never used
  --> crates/subvol/src/util/eytzinger.rs:97:14
   |
97 | pub const fn inorder_to_eytzinger1(i: u32, size: u32) -> u32 {
   |              ^^^^^^^^^^^^^^^^^^^^^

warning: function `jhash_size` is never used
 --> crates/subvol/src/util/jhash.rs:3:14
  |
3 | pub const fn jhash_size(n: u32) -> u32 {
  |              ^^^^^^^^^^

warning: function `jhash_mask` is never used
 --> crates/subvol/src/util/jhash.rs:7:14
  |
7 | pub const fn jhash_mask(n: u32) -> u32 {
  |              ^^^^^^^^^^

warning: function `jhash_3words` is never used
   --> crates/subvol/src/util/jhash.rs:146:8
    |
146 | pub fn jhash_3words(a: u32, b: u32, c: u32, initval: u32) -> u32 {
    |        ^^^^^^^^^^^^

warning: function `jhash_2words` is never used
   --> crates/subvol/src/util/jhash.rs:155:8
    |
155 | pub fn jhash_2words(a: u32, b: u32, initval: u32) -> u32 {
    |        ^^^^^^^^^^^^

warning: function `jhash_1word` is never used
   --> crates/subvol/src/util/jhash.rs:164:8
    |
164 | pub fn jhash_1word(a: u32, initval: u32) -> u32 {
    |        ^^^^^^^^^^^

warning: function `init_from_env` is never used
  --> crates/subvol/src/util/log.rs:43:8
   |
43 | pub fn init_from_env() {
   |        ^^^^^^^^^^^^^

warning: function `rcu_head_after_call_rcu` is never used
  --> crates/subvol/src/util/rcu.rs:93:15
   |
93 | pub unsafe fn rcu_head_after_call_rcu(head: *const rcu_head, func: rcu_callback_t) -> bool {
   |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `rcu_assign_pointer` is never used
   --> crates/subvol/src/util/rcu.rs:103:15
    |
103 | pub unsafe fn rcu_assign_pointer<T>(dst: *mut *mut T, value: *mut T) {
    |               ^^^^^^^^^^^^^^^^^^

warning: function `rcu_dereference` is never used
   --> crates/subvol/src/util/rcu.rs:108:15
    |
108 | pub unsafe fn rcu_dereference<T>(src: *const *mut T) -> *mut T {
    |               ^^^^^^^^^^^^^^^

warning: function `rhashtable_insert_fast` is never used
   --> crates/subvol/src/util/rhashtable.rs:375:15
    |
375 | pub unsafe fn rhashtable_insert_fast(ht: *mut rhashtable, obj: *mut rhash_head) -> i32 {
    |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `work_pending` is never used
   --> crates/subvol/src/util/workqueue.rs:103:15
    |
103 | pub unsafe fn work_pending(work: *const work_struct) -> bool {
    |               ^^^^^^^^^^^^

warning: function `alloc_workqueue` is never used
   --> crates/subvol/src/util/workqueue.rs:107:8
    |
107 | pub fn alloc_workqueue(name: &str) -> *mut workqueue_struct {
    |        ^^^^^^^^^^^^^^^

warning: function `flush_work` is never used
   --> crates/subvol/src/util/workqueue.rs:123:15
    |
123 | pub unsafe fn flush_work(work: *mut work_struct) -> bool {
    |               ^^^^^^^^^^

warning: function `destroy_workqueue` is never used
   --> crates/subvol/src/util/workqueue.rs:174:15
    |
174 | pub unsafe fn destroy_workqueue(wq: *mut workqueue_struct) {
    |               ^^^^^^^^^^^^^^^^^

warning: function `drain_workqueue` is never used
   --> crates/subvol/src/util/workqueue.rs:188:15
    |
188 | pub unsafe fn drain_workqueue(wq: *mut workqueue_struct) {
    |               ^^^^^^^^^^^^^^^

warning: `subvol` (lib) generated 420 warnings
warning: constant `CASES` is never used
  --> crates/subvol/tests/btree_proptest.rs:23:7
   |
23 | const CASES: u32 = 64;
   |       ^^^^^
   |
   = note: `#[warn(dead_code)]` (part of `#[warn(unused)]`) on by default

warning: `subvol` (test "btree_proptest") generated 1 warning
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.06s
     Running tests/btree_proptest.rs (target/debug/deps/btree_proptest-bfb308438dcdd790)
- 全量回归：running 173 tests
test btree::bkey::tests::bcachefs_disk_layout ... ok
test btree::bkey::tests::bcachefs_pack_rejects_field_underflow_and_overflow ... ok
test btree::bkey::tests::bcachefs_position_order_and_wrap ... ok
test btree::bkey::tests::bcachefs_format_state_builds_packable_format ... ok
test btree::bkey::tests::bcachefs_pack_unpack_key_fields ... ok
test btree::bkey::tests::bcachefs_precomputes_byte_aligned_unpack_fields ... ok
test btree::bkey::tests::bkey_and_val_eq_matches_local_memcmp_rule ... ok
test btree::bkey::tests::reservation_key_merge_dispatches_to_extent_merge_table ... ok
test btree::bkey::tests::bcachefs_pack_pos_exact_and_lossy_roll_down ... ok
test btree::bkey::tests::set_key_merge_resizes_only_matching_adjacent_keys ... ok
test btree::bkey::tests::maybe_mergable_matches_bcachefs_predicate ... ok
test btree::bset::tests::bcachefs_bkey_can_read_skips_cached_and_invalid_pointers ... ok
test btree::bset::tests::bcachefs_bkey_sectors_compressed_counts_uncached_pointers ... ok
test btree::bset::tests::bcachefs_bset_and_node_bitfields ... ok
test btree::bset::tests::bcachefs_bset_and_node_layout ... ok
test btree::bset::tests::bcachefs_extent_crc_append_selects_smallest_valid_encoding ... ok
test btree::bset::tests::bcachefs_drop_ptr_noerror_removes_orphaned_crc ... ok
test btree::bset::tests::bcachefs_extent_crc_pack_unpack_round_trip ... ok
test btree::bset::tests::bcachefs_extent_entry_drop_wrappers_shift_and_shrink_values ... ok
test btree::bset::tests::bcachefs_extent_entry_layout_and_types ... ok
test btree::bset::tests::bcachefs_dev_idx_is_online_reads_local_device_mask ... ok
test btree::bset::tests::bcachefs_extent_flags_read_from_leading_flags_entry ... ok
test btree::bset::tests::bcachefs_extent_entry_next_uses_known_u64_sizes ... ok
test btree::bset::tests::bcachefs_extent_ptr_bits_and_btree_ptr_range ... ok
test btree::bset::tests::bcachefs_extent_replicas_counts_ec_redundancy_and_cached_skip ... ok
test btree::bset::tests::bcachefs_extent_ptr_decoded_append_keeps_crc_and_ec_order ... ok
test btree::bset::tests::bcachefs_key_type_numbers_match_format ... ok
test btree::bset::tests::bcachefs_extent_cut_front_and_back_adjust_range_and_pointer ... ok
test btree::bset::tests::bcachefs_narrow_crc_moves_following_pointer_and_repacks_crc ... ok
test btree::bset::tests::bcachefs_propagate_incompressible_updates_none_crc_entries ... ok
test btree::bset::tests::bcachefs_reservation_merge_requires_matching_generation_and_replicas ... ok
test btree::bset::tests::bcachefs_reservation_merge_size_wraps_like_c_unsigned_addition ... ok
test btree::bset::tests::bcachefs_extent_key_classification_matches_format_types ... ok
test btree::bset::tests::bcachefs_whiteout_key_predicates ... ok
test btree::bset::tests::bcachefs_extent_cut_front_updates_crc_offset_and_stops_pointer_shift ... ok
test btree::bset_build::tests::btree_node_sort_merges_sets_and_preserves_accounting_and_journal_seq ... ok
test btree::bset::tests::bcachefs_extent_entry_insert_and_drop_update_packed_value ... ok
test btree::bset_build::tests::btree_sort_into_repacks_and_filters_deleted_keys ... ok
test btree::bset_build::tests::drop_whiteouts_relocates_unwritten_bset_without_dead_keys ... ok
test btree::bset_build::tests::builds_ro_aux_tree_with_live_bfloats ... ok
test btree::bset_build::tests::key_sort_fix_overlapping_keeps_newest_non_deleted_key ... ok
test btree::bset::tests::bcachefs_extent_key_ptr_range_starts_at_value ... ok
test btree::bset_build::tests::sort_keys_keeps_only_live_keys ... ok
test btree::bset::tests::bcachefs_extent_pointer_match_checks_disk_overlap_and_generation ... ok
test btree::bset_build::tests::sort_whiteouts_and_keep_only_unwritten_winners ... ok
test btree::bset_search::tests::searches_ro_aux_eytzinger_tree_and_linear_tail ... ok
test btree::bset_build::tests::sort_repack_transforms_keys_and_falls_back_to_current_format ... ok
test btree::bset_update::tests::inserts_replaces_and_deletes_in_last_bset ... ok
test btree::cache::tests::allocates_standalone_node_shell_and_buffers ... ok
test btree::cache::tests::allocates_and_initializes_node_buffers_from_cache_geometry ... ok
test btree::cache::tests::hash_and_live_state_follow_current_btree_pointer_and_flags ... ok
test btree::cache::tests::allocates_percpu_reader_nodes_with_matching_lock_layout ... ok
test btree::cache::tests::data_and_node_shell_are_freed_in_separate_stages ... ok
test btree::io::tests::drops_keys_outside_repaired_node_range_and_rebuilds_accounting ... ok
test btree::cache::tests::cache_init_preallocates_reserved_freeable_nodes ... ok
test btree::cache::tests::noiter_get_returns_read_locked_cached_node ... ok
test btree::cache::tests::evicts_clean_node_and_records_live_size ... ok
test btree::io::tests::appends_and_replays_multiple_bsets_in_sequence_order ... ok
test btree::io::tests::writes_reads_and_checksums_current_leaf_node ... ok
test btree::cache::tests::cache_state_transition_updates_hash_lists_and_counters ... ok
test btree::iter::tests::iter_flags_match_local_btree_property_normalization ... ok
test btree::interior::tests::insert_fit_leaves_varint_slop_u64 ... ok
test btree::iter::tests::path_node_unlock_keeps_node_for_reuse ... ok
test btree::iter::tests::path_peek_slot_reads_cached_key ... ok
test btree::iter::tests::path_peek_slot_exact_returns_position_on_miss ... ok
test btree::iter::tests::path_node_helpers_follow_node_level ... ok
test btree::iter::tests::path_get_preserves_cached_iterator_flag ... ok
test btree::iter::tests::path_relock_stops_at_unfilled_level ... ok
test btree::iter::tests::copy_iter_keeps_path_reference_until_both_exit ... ok
test btree::interior::tests::allocates_fake_root_for_recovery ... ok
test btree::node_iter::tests::merges_three_bsets_and_skips_deleted_keys ... ok
test btree::iter::tests::transaction_begin_preserves_unused_path_during_restart ... ok
test btree::io::tests::post_write_cleanup_drops_single_bset_whiteouts ... ok
test btree::types::tests::bcachefs_bkey_validate_context_layout_matches_local_header ... ok
test btree::node_iter::tests::searches_rw_aux_tree_then_scans_within_range ... ok
test btree::types::tests::bcachefs_btree_memory_type_layout ... ok
test btree::types::tests::bcachefs_bset_aux_tree_encoding ... ok
test btree::iter::tests::transaction_relock_restores_unreferenced_preserved_path ... ok
test btree::iter::tests::transaction_unlock_releases_unreferenced_allocated_path ... ok
test btree::io::tests::nofill_lookup_does_not_allocate_missing_node ... ok
test btree::iter::tests::path_set_pos_reuses_path_for_equal_position ... ok
test btree::types::tests::bcachefs_node_iter_set_drop_matches_memmove ... ok
test btree::types::tests::btree_property_masks_match_local_first_eight_ids ... ok
test btree::types::tests::local_intrusive_list_operations_preserve_links_and_order ... ok
test btree::iter::tests::path_make_mut_reuses_unique_nonpreserved_path ... ok
test btree::update::tests::bit_mod_allocates_key_from_transaction_memory ... ok
test btree::update::tests::buffered_bit_mod_builds_set_key ... ok
test btree::iter::tests::cached_path_reposition_invalidates_old_node ... ok
test btree::iter::tests::transaction_unlock_write_updates_linked_path_sequences ... ok
test btree::iter::tests::node_upgrade_relocks_read_path ... ok
test btree::update::tests::buffered_delete_wrapper_builds_deleted_key ... ok
test btree::update::tests::buffered_update_queues_write_buffer_journal_entry ... ok
test btree::update::tests::empty_slot_rejects_missing_transaction_or_iterator ... ok
test btree::update::tests::empty_snapshot_whiteout_list_is_a_noop ... ok
test btree::update::tests::commit_flag_bits_follow_bcachefs_watermark_prefix ... ok
test btree::io::tests::root_read_lazily_loads_child_from_disk_pointer ... ok
test btree::update::tests::commit_hook_registration_matches_bcachefs_chain_order ... ok
test btree::iter::tests::traverses_root_and_advances_across_leaf_nodes ... ok
test btree::iter::tests::transaction_unlock_write_keeps_intent_lock ... ok
test btree::iter::tests::path_upgrade_norestart_raises_lock_demand ... ok
test btree::update::tests::transaction_jset_entry_alloc_is_u64_aligned ... ok
test btree::update::tests::transaction_log_bkey_queues_structured_entry ... ok
test btree::update::tests::transaction_log_string_pads_to_u64_boundary ... ok
test btree::update::tests::mutable_key_copy_uses_transaction_memory ... ok
test checksum::tests::bch2_checksum_uses_local_seed_and_final_xor_rules ... ok
test btree::update::tests::transaction_subbuf_reserve_tracks_used_u64s ... ok
test checksum::tests::checksum_merge_matches_local_zero_fill_rule ... ok
test checksum::tests::local_checksum_vectors ... ok
test checksum::tests::checksum_mergeability_matches_bcachefs ... ok
test data::keylist::tests::keylist_layout_and_inline_operations_match_local_source ... ok
test btree::update::tests::transaction_update_order_keeps_alloc_after_stripes ... ok
test btree::update::tests::trigger_mutable_new_rewires_matching_update ... ok
test btree::update::tests::failing_commit_hook_leaves_leaf_unchanged_and_transaction_retryable ... ok
test btree::update::tests::extent_whiteout_type_matches_current_snapshot_leaf_rules ... ok
test btree::update::tests::need_whiteout_for_snapshot_matches_parent_short_circuit ... ok
test btree::update::tests::mutable_key_copy_honors_type_and_minimum_size ... ok
test btree::update::tests::transaction_bump_allocator_reuses_memory_after_begin ... ok
test btree::update::tests::transaction_compacts_max_bsets_before_starting_next ... ok
test btree::update::tests::transaction_starts_block_aligned_bset_after_written_set ... ok
test btree::update::tests::transaction_writes_large_middle_bset_before_compacting_all ... ok
test engine::tests::process_crash_child ... ok
test btree::update::tests::transaction_replaces_and_inserts_under_write_lock ... ok

running 1 test
test btree::interior::tests::full_root_leaf_splits_grows_root_and_retries_insert ... ok
test engine::tests::single_transaction_many_keys_into_one_leaf_splits_without_overflowing ... ok
test engine::tests::dropped_transaction_never_changes_the_tree_or_journal ... ok
test engine::tests::high_watermark_kicks_background_reclaim_and_preserves_the_tail ... ok
test journal::journal_key_overlay_tests::replaces_same_slot_and_reads_ranges ... ok
test journal::tests::journal_disk_layout_matches_local_format ... ok
test journal::tests::replay_rejects_conflicting_duplicate_journal_records ... ok
test journal::tests::direct_reclaim_keeps_btree_pin_unflushed_after_write_error ... ok
test journal::tests::replay_uses_the_newest_flushed_boundary_before_replaying_roots ... ok
test journal::tests::replay_restarts_after_a_leaf_split ... ok
test lock::six::tests::bcachefs_six_blocking_writer_waits_for_readers ... ok
test lock::six::tests::bcachefs_six_compatibility_and_sequence ... ok
test journal::tests::btree_roots_round_trip_through_current_journal_entry ... ok
test journal::tests::reservations_encode_entries_and_cycle_sequence ... ok
test lock::six::tests::bcachefs_six_upgrade_downgrade_and_relock ... ok
test sb::io::tests::accepts_only_the_current_metadata_version ... ok
test sb::io::tests::realloc_and_resize_fields_preserve_vstruct_order ... ok
test sb::io::tests::backup_scan_selects_highest_seq_and_recovers_without_primary ... ok
test sb::io::tests::read_one_super_reallocates_rereads_and_checks_checksum ... ok
test sb::io::tests::realloc_preserves_header_and_enforces_layout_limit ... ok
test sb::io::tests::validates_every_local_layout_branch ... ok
test sb::io::tests::validates_fixed_fields_and_members_v2_in_local_order ... ok
test sb::io::tests::validates_journal_v2_ranges_in_local_order ... ok
test sb::tests::metadata_version_encoding_matches_local_macros ... ok
test sb::tests::superblock_fixed_layout_matches_local_format ... ok
test snapshot::tests::snapshot_id_list_lookup_matches_local_darray_find ... ok
test snapshot::tests::snapshot_id_list_push_and_merge_follow_darray_growth ... ok
test snapshot::tests::snapshot_layout_matches_local_format ... ok
test snapshot::tests::atomic_snapshot_trigger_updates_memory_table ... ok
test snapshot::tests::snapshot_parent_bitmap_skip_and_tree_walk ... ok
test util::bit_spinlock::tests::bit_lock_uses_low_bit_and_releases_with_ordering ... ok
test util::jhash::tests::matches_local_linux_jhash_vectors ... ok
test util::log::tests::level_can_be_disabled_and_enabled ... ok
test util::rcu::tests::assign_and_dereference_preserve_pointer_value ... ok
test util::rhashtable::tests::fixed_key_lookup_insert_remove_and_resize_preserve_objects ... ok
test util::workqueue::tests::workqueue_runs_pending_work_once_and_flushes ... ok
test util::eytzinger::tests::bcachefs_eytzinger_round_trip_and_walk ... ok
test util::rcu::tests::callback_waits_for_read_side_grace_period ... ok
test engine::tests::transaction_restart_retraverses_before_committing_once ... ok
test engine::tests::one_transaction_replays_all_of_its_btree_updates ... ok
test journal::journal_key_overlay_tests::copies_each_variable_length_journal_key ... ok
test engine::tests::persistent_journal_reopens_after_process_style_drop ... ok
test engine::tests::durability_api_and_metrics_report_the_committed_boundary ... ok
test engine::tests::reclaim_releases_old_records_and_replays_the_tail ... ok
test engine::tests::failed_flush_does_not_make_a_transaction_recoverable ... ok
test engine::tests::corrupt_journal_tail_never_survives_recovery ... ok
test journal::tests::journal_device_round_trip_resumes_bucket_position_and_rejects_corruption ... ok
test engine::tests::concurrent_rcu_read_transactions_and_writers_keep_iterator_order ... ok

running 1 test
test engine::tests::generated_reclaim_recovery_matches_the_model ... ok

running 1 test
test engine::tests::process_abort_recovery_observes_only_durable_boundaries ... ok
test engine::tests::generated_transaction_journal_recovery_matches_the_model ... ok

test result: ok. 173 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 2.25s


running 9 tests
test deterministic_scan_loss_repro ... ok
test deterministic_delete_hang_repro ... ok
test random_operations_match_btree_map_model ... ok
test journal_corruption_benign_tail_ignored ... ok
test journal_corruption_detection_in_random_state ... ok
test reclaim_after_checkpoint_preserves_model ... ok
test crash_recovery_restores_sync_point_state ... ok
test multi_snapshot_versions_coexist_and_recover ... ok
test fault_injection_preserves_model_and_recovery ... ok

test result: ok. 9 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 1.53s


running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

warning: constant `MAX_VERSION` is never used
  --> crates/subvol/src/btree/bkey.rs:71:11
   |
71 | pub const MAX_VERSION: bversion = bversion {
   |           ^^^^^^^^^^^
   |
   = note: `#[warn(dead_code)]` (part of `#[warn(unused)]`) on by default

warning: function `bch2_bkey_format_field_overflows` is never used
   --> crates/subvol/src/btree/bkey.rs:747:8
    |
747 | pub fn bch2_bkey_format_field_overflows(format: &bkey_format, i: u32) -> bool {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_gt` is never used
   --> crates/subvol/src/btree/bkey.rs:874:14
    |
874 | pub const fn bkey_gt(l: bpos, r: bpos) -> bool {
    |              ^^^^^^^

warning: function `bkey_cmp` is never used
   --> crates/subvol/src/btree/bkey.rs:882:14
    |
882 | pub const fn bkey_cmp(l: bpos, r: bpos) -> i32 {
    |              ^^^^^^^^

warning: function `bkey_min` is never used
   --> crates/subvol/src/btree/bkey.rs:896:14
    |
896 | pub const fn bkey_min(l: bpos, r: bpos) -> bpos {
    |              ^^^^^^^^

warning: function `bkey_max` is never used
   --> crates/subvol/src/btree/bkey.rs:904:14
    |
904 | pub const fn bkey_max(l: bpos, r: bpos) -> bpos {
    |              ^^^^^^^^

warning: function `bversion_zero` is never used
   --> crates/subvol/src/btree/bkey.rs:930:14
    |
930 | pub const fn bversion_zero(v: bversion) -> bool {
    |              ^^^^^^^^^^^^^

warning: function `bkeyp_key_bytes` is never used
    --> crates/subvol/src/btree/bkey.rs:1023:14
     |
1023 | pub const fn bkeyp_key_bytes(format: &bkey_format, k: &bkey_packed) -> u32 {
     |              ^^^^^^^^^^^^^^^

warning: function `bkeyp_val_bytes` is never used
    --> crates/subvol/src/btree/bkey.rs:1031:14
     |
1031 | pub const fn bkeyp_val_bytes(format: &bkey_format, k: &bkey_packed) -> usize {
     |              ^^^^^^^^^^^^^^^

warning: function `set_bkeyp_val_u64s` is never used
    --> crates/subvol/src/btree/bkey.rs:1035:14
     |
1035 | pub const fn set_bkeyp_val_u64s(format: &bkey_format, k: &mut bkey_packed, val_u64s: u32) {
     |              ^^^^^^^^^^^^^^^^^^

warning: function `set_bkey_val_bytes` is never used
    --> crates/subvol/src/btree/bkey.rs:1057:14
     |
1057 | pub const fn set_bkey_val_bytes(k: &mut bkey, bytes: u32) {
     |              ^^^^^^^^^^^^^^^^^^

warning: struct `bch_devs_list` is never constructed
  --> crates/subvol/src/btree/bset.rs:17:12
   |
17 | pub struct bch_devs_list {
   |            ^^^^^^^^^^^^^

warning: function `dev_mask_nr` is never used
  --> crates/subvol/src/btree/bset.rs:28:14
   |
28 | pub const fn dev_mask_nr(devs: &bch_devs_mask) -> u32 {
   |              ^^^^^^^^^^^

warning: function `bch2_dev_idx_is_online` is never used
  --> crates/subvol/src/btree/bset.rs:38:15
   |
38 | pub unsafe fn bch2_dev_idx_is_online(c: *const super::types::bch_fs, dev: u32) -> bool {
   |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_dev_list_has_dev` is never used
  --> crates/subvol/src/btree/bset.rs:44:14
   |
44 | pub const fn bch2_dev_list_has_dev(devs: bch_devs_list, dev: u8) -> bool {
   |              ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_dev_list_drop_dev` is never used
  --> crates/subvol/src/btree/bset.rs:55:8
   |
55 | pub fn bch2_dev_list_drop_dev(devs: &mut bch_devs_list, dev: u8) {
   |        ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_dev_list_add_dev` is never used
  --> crates/subvol/src/btree/bset.rs:71:8
   |
71 | pub fn bch2_dev_list_add_dev(devs: &mut bch_devs_list, dev: u8) {
   |        ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_dev_list_single` is never used
  --> crates/subvol/src/btree/bset.rs:79:14
   |
79 | pub const fn bch2_dev_list_single(dev: u8) -> bch_devs_list {
   |              ^^^^^^^^^^^^^^^^^^^^

warning: function `BCH_EXTENT_PTR_TYPE` is never used
  --> crates/subvol/src/btree/bset.rs:96:14
   |
96 | pub const fn BCH_EXTENT_PTR_TYPE(ptr: &bch_extent_ptr) -> u64 {
   |              ^^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_EXTENT_PTR_TYPE` is never used
   --> crates/subvol/src/btree/bset.rs:100:14
    |
100 | pub const fn SET_BCH_EXTENT_PTR_TYPE(ptr: &mut bch_extent_ptr, value: u64) {
    |              ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_EXTENT_PTR_CACHED` is never used
   --> crates/subvol/src/btree/bset.rs:108:14
    |
108 | pub const fn SET_BCH_EXTENT_PTR_CACHED(ptr: &mut bch_extent_ptr, value: u64) {
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `BCH_EXTENT_PTR_UNUSED` is never used
   --> crates/subvol/src/btree/bset.rs:112:14
    |
112 | pub const fn BCH_EXTENT_PTR_UNUSED(ptr: &bch_extent_ptr) -> u64 {
    |              ^^^^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_EXTENT_PTR_UNUSED` is never used
   --> crates/subvol/src/btree/bset.rs:116:14
    |
116 | pub const fn SET_BCH_EXTENT_PTR_UNUSED(ptr: &mut bch_extent_ptr, value: u64) {
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `BCH_EXTENT_PTR_UNWRITTEN` is never used
   --> crates/subvol/src/btree/bset.rs:120:14
    |
120 | pub const fn BCH_EXTENT_PTR_UNWRITTEN(ptr: &bch_extent_ptr) -> u64 {
    |              ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_EXTENT_PTR_UNWRITTEN` is never used
   --> crates/subvol/src/btree/bset.rs:124:14
    |
124 | pub const fn SET_BCH_EXTENT_PTR_UNWRITTEN(ptr: &mut bch_extent_ptr, value: u64) {
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_EXTENT_PTR_DEV` is never used
   --> crates/subvol/src/btree/bset.rs:141:14
    |
141 | pub const fn SET_BCH_EXTENT_PTR_DEV(ptr: &mut bch_extent_ptr, value: u64) {
    |              ^^^^^^^^^^^^^^^^^^^^^^

warning: function `BCH_EXTENT_PTR_GEN` is never used
   --> crates/subvol/src/btree/bset.rs:145:14
    |
145 | pub const fn BCH_EXTENT_PTR_GEN(ptr: &bch_extent_ptr) -> u64 {
    |              ^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_EXTENT_PTR_GEN` is never used
   --> crates/subvol/src/btree/bset.rs:149:14
    |
149 | pub const fn SET_BCH_EXTENT_PTR_GEN(ptr: &mut bch_extent_ptr, value: u64) {
    |              ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_REPLICAS_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:163:11
    |
163 | pub const BCH_REPLICAS_MAX: u32 = 4;
    |           ^^^^^^^^^^^^^^^^

warning: constant `BKEY_EXTENT_PTR_U64S_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:164:11
    |
164 | pub const BKEY_EXTENT_PTR_U64S_MAX: u32 = ((core::mem::size_of::<bch_extent_crc128>()
    |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_EXTENT_VAL_U64S_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:167:11
    |
167 | pub const BKEY_EXTENT_VAL_U64S_MAX: u32 = 5 + BKEY_EXTENT_PTR_U64S_MAX * (BCH_REPLICAS_MAX * 2 + 1);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: static `bch_crc_bytes` is never used
   --> crates/subvol/src/btree/bset.rs:169:12
    |
169 | pub static bch_crc_bytes: [u8; 8] = [0, 4, 8, 10, 16, 4, 8, 8];
    |            ^^^^^^^^^^^^^

warning: function `extent_entry_drop` is never used
   --> crates/subvol/src/btree/bset.rs:253:15
    |
253 | pub unsafe fn extent_entry_drop(
    |               ^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_extent_entry_drop_s` is never used
   --> crates/subvol/src/btree/bset.rs:269:15
    |
269 | pub unsafe fn bch2_bkey_extent_entry_drop_s(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_extent_entry_drop` is never used
   --> crates/subvol/src/btree/bset.rs:284:15
    |
284 | pub unsafe fn bch2_bkey_extent_entry_drop(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_EXTENT_FLAG_poisoned` is never used
   --> crates/subvol/src/btree/bset.rs:340:11
    |
340 | pub const BCH_EXTENT_FLAG_poisoned: u8 = 0;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: struct `extent_ptr_decoded` is never constructed
   --> crates/subvol/src/btree/bset.rs:383:12
    |
383 | pub struct extent_ptr_decoded {
    |            ^^^^^^^^^^^^^^^^^^

warning: constant `CRC32_SIZE_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:394:11
    |
394 | pub const CRC32_SIZE_MAX: u32 = 1 << 7;
    |           ^^^^^^^^^^^^^^

warning: constant `CRC64_SIZE_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:395:11
    |
395 | pub const CRC64_SIZE_MAX: u32 = 1 << 9;
    |           ^^^^^^^^^^^^^^

warning: constant `CRC128_SIZE_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:396:11
    |
396 | pub const CRC128_SIZE_MAX: u32 = 1 << 13;
    |           ^^^^^^^^^^^^^^^

warning: constant `CRC32_NONCE_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:397:11
    |
397 | pub const CRC32_NONCE_MAX: u16 = 0;
    |           ^^^^^^^^^^^^^^^

warning: constant `CRC64_NONCE_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:398:11
    |
398 | pub const CRC64_NONCE_MAX: u16 = (1 << 10) - 1;
    |           ^^^^^^^^^^^^^^^

warning: constant `CRC128_NONCE_MAX` is never used
   --> crates/subvol/src/btree/bset.rs:399:11
    |
399 | pub const CRC128_NONCE_MAX: u16 = (1 << 13) - 1;
    |           ^^^^^^^^^^^^^^^^

warning: function `crc_is_encoded` is never used
   --> crates/subvol/src/btree/bset.rs:406:14
    |
406 | pub const fn crc_is_encoded(crc: bch_extent_crc_unpacked) -> bool {
    |              ^^^^^^^^^^^^^^

warning: static `bch2_crc_field_size_max` is never used
   --> crates/subvol/src/btree/bset.rs:410:12
    |
410 | pub static bch2_crc_field_size_max: [u32; BCH_EXTENT_ENTRY_MAX as usize] = [
    |            ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_extent_crc_pack` is never used
   --> crates/subvol/src/btree/bset.rs:495:15
    |
495 | pub unsafe fn bch2_extent_crc_pack(
    |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_extent_crc_append` is never used
   --> crates/subvol/src/btree/bset.rs:543:15
    |
543 | pub unsafe fn bch2_extent_crc_append(
    |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_crc_unpacked_cmp` is never used
   --> crates/subvol/src/btree/bset.rs:578:4
    |
578 | fn bch2_crc_unpacked_cmp(l: bch_extent_crc_unpacked, r: bch_extent_crc_unpacked) -> bool {
    |    ^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_find_crc` is never used
   --> crates/subvol/src/btree/bset.rs:589:11
    |
589 | unsafe fn bkey_find_crc(
    |           ^^^^^^^^^^^^^

warning: function `bch2_bkey_narrow_crc` is never used
   --> crates/subvol/src/btree/bset.rs:607:15
    |
607 | pub unsafe fn bch2_bkey_narrow_crc(
    |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_extent_ptr_decoded_append` is never used
   --> crates/subvol/src/btree/bset.rs:660:15
    |
660 | pub unsafe fn bch2_extent_ptr_decoded_append(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `extent_entry_prev` is never used
   --> crates/subvol/src/btree/bset.rs:701:11
    |
701 | unsafe fn extent_entry_prev(
    |           ^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_ptr_noerror` is never used
   --> crates/subvol/src/btree/bset.rs:716:15
    |
716 | pub unsafe fn bch2_bkey_drop_ptr_noerror(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_ptr` is never used
   --> crates/subvol/src/btree/bset.rs:756:15
    |
756 | pub unsafe fn bch2_bkey_drop_ptr(
    |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_ptrs_mask` is never used
   --> crates/subvol/src/btree/bset.rs:777:15
    |
777 | pub unsafe fn bch2_bkey_drop_ptrs_mask(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_device_noerror` is never used
   --> crates/subvol/src/btree/bset.rs:805:15
    |
805 | pub unsafe fn bch2_bkey_drop_device_noerror(c: *const super::types::bch_fs, k: bkey_s, dev: u32) {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_device` is never used
   --> crates/subvol/src/btree/bset.rs:824:15
    |
824 | pub unsafe fn bch2_bkey_drop_device(c: *const super::types::bch_fs, k: bkey_s, dev: u32) {
    |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_ec` is never used
   --> crates/subvol/src/btree/bset.rs:843:11
    |
843 | unsafe fn bch2_bkey_drop_ec(c: *const super::types::bch_fs, k: *mut bkey_i, dev: u32) {
    |           ^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_drop_ec_mask` is never used
   --> crates/subvol/src/btree/bset.rs:864:15
    |
864 | pub unsafe fn bch2_bkey_drop_ec_mask(
    |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `extent_entry_is_ptr` is never used
   --> crates/subvol/src/btree/bset.rs:917:15
    |
917 | pub unsafe fn extent_entry_is_ptr(entry: *const bch_extent_entry) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^

warning: function `extent_entry_is_stripe_ptr` is never used
   --> crates/subvol/src/btree/bset.rs:921:15
    |
921 | pub unsafe fn extent_entry_is_stripe_ptr(entry: *const bch_extent_entry) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `extent_entry_is_crc` is never used
   --> crates/subvol/src/btree/bset.rs:925:15
    |
925 | pub unsafe fn extent_entry_is_crc(entry: *const bch_extent_entry) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_TYPE_strict_btree_checks` is never used
   --> crates/subvol/src/btree/bset.rs:981:11
    |
981 | pub const BKEY_TYPE_strict_btree_checks: u32 = 1 << 0;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_error` is never used
    --> crates/subvol/src/btree/bset.rs:1000:11
     |
1000 | pub const KEY_TYPE_error: u8 = 2;
     |           ^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_hash_whiteout` is never used
    --> crates/subvol/src/btree/bset.rs:1002:11
     |
1002 | pub const KEY_TYPE_hash_whiteout: u8 = 4;
     |           ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_inode` is never used
    --> crates/subvol/src/btree/bset.rs:1006:11
     |
1006 | pub const KEY_TYPE_inode: u8 = 8;
     |           ^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_inode_generation` is never used
    --> crates/subvol/src/btree/bset.rs:1007:11
     |
1007 | pub const KEY_TYPE_inode_generation: u8 = 9;
     |           ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_dirent` is never used
    --> crates/subvol/src/btree/bset.rs:1008:11
     |
1008 | pub const KEY_TYPE_dirent: u8 = 10;
     |           ^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_xattr` is never used
    --> crates/subvol/src/btree/bset.rs:1009:11
     |
1009 | pub const KEY_TYPE_xattr: u8 = 11;
     |           ^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_alloc` is never used
    --> crates/subvol/src/btree/bset.rs:1010:11
     |
1010 | pub const KEY_TYPE_alloc: u8 = 12;
     |           ^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_quota` is never used
    --> crates/subvol/src/btree/bset.rs:1011:11
     |
1011 | pub const KEY_TYPE_quota: u8 = 13;
     |           ^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_reflink_p` is never used
    --> crates/subvol/src/btree/bset.rs:1013:11
     |
1013 | pub const KEY_TYPE_reflink_p: u8 = 15;
     |           ^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_inline_data` is never used
    --> crates/subvol/src/btree/bset.rs:1015:11
     |
1015 | pub const KEY_TYPE_inline_data: u8 = 17;
     |           ^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_indirect_inline_data` is never used
    --> crates/subvol/src/btree/bset.rs:1017:11
     |
1017 | pub const KEY_TYPE_indirect_inline_data: u8 = 19;
     |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_alloc_v2` is never used
    --> crates/subvol/src/btree/bset.rs:1018:11
     |
1018 | pub const KEY_TYPE_alloc_v2: u8 = 20;
     |           ^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_subvolume` is never used
    --> crates/subvol/src/btree/bset.rs:1019:11
     |
1019 | pub const KEY_TYPE_subvolume: u8 = 21;
     |           ^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_snapshot` is never used
    --> crates/subvol/src/btree/bset.rs:1020:11
     |
1020 | pub const KEY_TYPE_snapshot: u8 = 22;
     |           ^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_inode_v2` is never used
    --> crates/subvol/src/btree/bset.rs:1021:11
     |
1021 | pub const KEY_TYPE_inode_v2: u8 = 23;
     |           ^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_alloc_v3` is never used
    --> crates/subvol/src/btree/bset.rs:1022:11
     |
1022 | pub const KEY_TYPE_alloc_v3: u8 = 24;
     |           ^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_lru` is never used
    --> crates/subvol/src/btree/bset.rs:1024:11
     |
1024 | pub const KEY_TYPE_lru: u8 = 26;
     |           ^^^^^^^^^^^^

warning: constant `KEY_TYPE_alloc_v4` is never used
    --> crates/subvol/src/btree/bset.rs:1025:11
     |
1025 | pub const KEY_TYPE_alloc_v4: u8 = 27;
     |           ^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_backpointer` is never used
    --> crates/subvol/src/btree/bset.rs:1026:11
     |
1026 | pub const KEY_TYPE_backpointer: u8 = 28;
     |           ^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_inode_v3` is never used
    --> crates/subvol/src/btree/bset.rs:1027:11
     |
1027 | pub const KEY_TYPE_inode_v3: u8 = 29;
     |           ^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_bucket_gens` is never used
    --> crates/subvol/src/btree/bset.rs:1028:11
     |
1028 | pub const KEY_TYPE_bucket_gens: u8 = 30;
     |           ^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_snapshot_tree` is never used
    --> crates/subvol/src/btree/bset.rs:1029:11
     |
1029 | pub const KEY_TYPE_snapshot_tree: u8 = 31;
     |           ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_logged_op_truncate` is never used
    --> crates/subvol/src/btree/bset.rs:1030:11
     |
1030 | pub const KEY_TYPE_logged_op_truncate: u8 = 32;
     |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_logged_op_finsert` is never used
    --> crates/subvol/src/btree/bset.rs:1031:11
     |
1031 | pub const KEY_TYPE_logged_op_finsert: u8 = 33;
     |           ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_inode_alloc_cursor` is never used
    --> crates/subvol/src/btree/bset.rs:1033:11
     |
1033 | pub const KEY_TYPE_inode_alloc_cursor: u8 = 35;
     |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_logged_op_stripe_update` is never used
    --> crates/subvol/src/btree/bset.rs:1035:11
     |
1035 | pub const KEY_TYPE_logged_op_stripe_update: u8 = 37;
     |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `KEY_TYPE_MAX` is never used
    --> crates/subvol/src/btree/bset.rs:1036:11
     |
1036 | pub const KEY_TYPE_MAX: u8 = 38;
     |           ^^^^^^^^^^^^

warning: static `bch2_bkey_type_flags` is never used
    --> crates/subvol/src/btree/bset.rs:1040:12
     |
1040 | pub static bch2_bkey_type_flags: [u32; KEY_TYPE_MAX as usize] = [
     |            ^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_whiteout` is never used
    --> crates/subvol/src/btree/bset.rs:1082:14
     |
1082 | pub const fn bkey_whiteout(k: &super::bkey::bkey_packed) -> bool {
     |              ^^^^^^^^^^^^^

warning: struct `bch_btree_ptr` is never constructed
    --> crates/subvol/src/btree/bset.rs:1095:12
     |
1095 | pub struct bch_btree_ptr {
     |            ^^^^^^^^^^^^^

warning: struct `bch_extent` is never constructed
    --> crates/subvol/src/btree/bset.rs:1116:12
     |
1116 | pub struct bch_extent {
     |            ^^^^^^^^^^

warning: struct `bch_inline_data` is never constructed
    --> crates/subvol/src/btree/bset.rs:1133:12
     |
1133 | pub struct bch_inline_data {
     |            ^^^^^^^^^^^^^^^

warning: struct `bch_indirect_inline_data` is never constructed
    --> crates/subvol/src/btree/bset.rs:1140:12
     |
1140 | pub struct bch_indirect_inline_data {
     |            ^^^^^^^^^^^^^^^^^^^^^^^^

warning: struct `bch_reflink_v` is never constructed
    --> crates/subvol/src/btree/bset.rs:1148:12
     |
1148 | pub struct bch_reflink_v {
     |            ^^^^^^^^^^^^^

warning: function `bch2_bkey_extent_ptrs_flags` is never used
    --> crates/subvol/src/btree/bset.rs:1223:15
     |
1223 | pub unsafe fn bch2_bkey_extent_ptrs_flags(ptrs: bkey_ptrs_c) -> u64 {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_extent_flags` is never used
    --> crates/subvol/src/btree/bset.rs:1234:15
     |
1234 | pub unsafe fn bch2_bkey_extent_flags(k: bkey_s_c) -> u64 {
     |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_ptr_swab` is never used
    --> crates/subvol/src/btree/bset.rs:1238:15
     |
1238 | pub unsafe fn bch2_ptr_swab(c: *const super::types::bch_fs, k: bkey_s) {
     |               ^^^^^^^^^^^^^

warning: function `bch2_bkey_has_device_c` is never used
    --> crates/subvol/src/btree/bset.rs:1273:15
     |
1273 | pub unsafe fn bch2_bkey_has_device_c(
     |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_has_device` is never used
    --> crates/subvol/src/btree/bset.rs:1292:15
     |
1292 | pub unsafe fn bch2_bkey_has_device(
     |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_has_device_decode` is never used
    --> crates/subvol/src/btree/bset.rs:1300:15
     |
1300 | pub unsafe fn bch2_bkey_has_device_decode(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_dev_ptr_bit` is never used
    --> crates/subvol/src/btree/bset.rs:1349:15
     |
1349 | pub unsafe fn bch2_bkey_dev_ptr_bit(c: *const super::types::bch_fs, k: bkey_s_c, dev: u32) -> u32 {
     |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_devs` is never used
    --> crates/subvol/src/btree/bset.rs:1365:15
     |
1365 | pub unsafe fn bch2_bkey_devs(c: *const super::types::bch_fs, k: bkey_s_c) -> bch_devs_list {
     |               ^^^^^^^^^^^^^^

warning: function `bch2_bkey_ptrs_match` is never used
    --> crates/subvol/src/btree/bset.rs:1381:15
     |
1381 | pub unsafe fn bch2_bkey_ptrs_match(
     |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_extents_match` is never used
    --> crates/subvol/src/btree/bset.rs:1411:15
     |
1411 | pub unsafe fn bch2_extents_match(
     |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_extent_has_ptr` is never used
    --> crates/subvol/src/btree/bset.rs:1506:15
     |
1506 | pub unsafe fn bch2_extent_has_ptr(
     |               ^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_matches_ptr` is never used
    --> crates/subvol/src/btree/bset.rs:1561:15
     |
1561 | pub unsafe fn bch2_bkey_matches_ptr(
     |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_replicas` is never used
    --> crates/subvol/src/btree/bset.rs:1614:15
     |
1614 | pub unsafe fn bch2_bkey_replicas(c: *mut super::types::bch_fs, k: bkey_s_c) -> u32 {
     |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_nr_dirty_ptrs` is never used
    --> crates/subvol/src/btree/bset.rs:1690:15
     |
1690 | pub unsafe fn bch2_bkey_nr_dirty_ptrs(c: *const super::types::bch_fs, k: bkey_s_c) -> u32 {
     |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_nr_ptrs_allocated` is never used
    --> crates/subvol/src/btree/bset.rs:1709:15
     |
1709 | pub unsafe fn bch2_bkey_nr_ptrs_allocated(c: *const super::types::bch_fs, k: bkey_s_c) -> u32 {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_nr_ptrs_fully_allocated` is never used
    --> crates/subvol/src/btree/bset.rs:1732:15
     |
1732 | pub unsafe fn bch2_bkey_nr_ptrs_fully_allocated(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_extent_is_unwritten` is never used
    --> crates/subvol/src/btree/bset.rs:1770:15
     |
1770 | pub unsafe fn bkey_extent_is_unwritten(c: *const super::types::bch_fs, k: bkey_s_c) -> bool {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_extent_is_direct_data` is never used
    --> crates/subvol/src/btree/bset.rs:1787:14
     |
1787 | pub const fn bkey_extent_is_direct_data(k: &bkey) -> bool {
     |              ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_extent_ptr_eq` is never used
    --> crates/subvol/src/btree/bset.rs:1794:14
     |
1794 | pub const fn bch2_extent_ptr_eq(ptr1: bch_extent_ptr, ptr2: bch_extent_ptr) -> bool {
     |              ^^^^^^^^^^^^^^^^^^

warning: enum `bch_extent_overlap` is never used
    --> crates/subvol/src/btree/bset.rs:1804:10
     |
1804 | pub enum bch_extent_overlap {
     |          ^^^^^^^^^^^^^^^^^^

warning: function `bch2_extent_overlap` is never used
    --> crates/subvol/src/btree/bset.rs:1811:14
     |
1811 | pub const fn bch2_extent_overlap(k: &bkey, m: &bkey) -> bch_extent_overlap {
     |              ^^^^^^^^^^^^^^^^^^^

warning: function `bkey_is_btree_ptr` is never used
    --> crates/subvol/src/btree/bset.rs:1822:14
     |
1822 | pub const fn bkey_is_btree_ptr(k: &bkey) -> bool {
     |              ^^^^^^^^^^^^^^^^^

warning: function `bkey_is_user_data` is never used
    --> crates/subvol/src/btree/bset.rs:1826:14
     |
1826 | pub const fn bkey_is_user_data(k: &bkey) -> bool {
     |              ^^^^^^^^^^^^^^^^^

warning: function `bkey_extent_is_inline_data` is never used
    --> crates/subvol/src/btree/bset.rs:1833:14
     |
1833 | pub const fn bkey_extent_is_inline_data(k: &bkey) -> bool {
     |              ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_inline_data_offset` is never used
    --> crates/subvol/src/btree/bset.rs:1837:15
     |
1837 | pub unsafe fn bkey_inline_data_offset(k: *const bkey) -> usize {
     |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_inline_data_bytes` is never used
    --> crates/subvol/src/btree/bset.rs:1845:15
     |
1845 | pub unsafe fn bkey_inline_data_bytes(k: *const bkey) -> usize {
     |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_extent_is_data` is never used
    --> crates/subvol/src/btree/bset.rs:1849:14
     |
1849 | pub const fn bkey_extent_is_data(k: &bkey) -> bool {
     |              ^^^^^^^^^^^^^^^^^^^

warning: function `bkey_extent_is_allocation` is never used
    --> crates/subvol/src/btree/bset.rs:1853:14
     |
1853 | pub const fn bkey_extent_is_allocation(k: &bkey) -> bool {
     |              ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bkey_extent_is_reservation` is never used
    --> crates/subvol/src/btree/bset.rs:1866:15
     |
1866 | pub unsafe fn bkey_extent_is_reservation(c: *const super::types::bch_fs, k: bkey_s_c) -> bool {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_is_incompressible` is never used
    --> crates/subvol/src/btree/bset.rs:1870:15
     |
1870 | pub unsafe fn bch2_bkey_is_incompressible(c: *const super::types::bch_fs, k: bkey_s_c) -> bool {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_can_read` is never used
    --> crates/subvol/src/btree/bset.rs:1892:15
     |
1892 | pub unsafe fn bch2_bkey_can_read(c: *const super::types::bch_fs, k: bkey_s_c) -> bool {
     |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_propagate_incompressible` is never used
    --> crates/subvol/src/btree/bset.rs:1938:15
     |
1938 | pub unsafe fn bch2_bkey_propagate_incompressible(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_append_ptr` is never used
    --> crates/subvol/src/btree/bset.rs:1970:15
     |
1970 | pub unsafe fn bch2_bkey_append_ptr(
     |               ^^^^^^^^^^^^^^^^^^^^

warning: function `BTREE_NODE_NEW_EXTENT_OVERWRITE` is never used
    --> crates/subvol/src/btree/bset.rs:2160:14
     |
2160 | pub const fn BTREE_NODE_NEW_EXTENT_OVERWRITE(n: &btree_node) -> u64 {
     |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `SET_BTREE_NODE_NEW_EXTENT_OVERWRITE` is never used
    --> crates/subvol/src/btree/bset.rs:2164:14
     |
2164 | pub const fn SET_BTREE_NODE_NEW_EXTENT_OVERWRITE(n: &mut btree_node, v: u64) {
     |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `BTREE_NODE_SEQ` is never used
    --> crates/subvol/src/btree/bset.rs:2176:14
     |
2176 | pub const fn BTREE_NODE_SEQ(n: &btree_node) -> u64 {
     |              ^^^^^^^^^^^^^^

warning: function `SET_BTREE_NODE_SEQ` is never used
    --> crates/subvol/src/btree/bset.rs:2180:14
     |
2180 | pub const fn SET_BTREE_NODE_SEQ(n: &mut btree_node, v: u64) {
     |              ^^^^^^^^^^^^^^^^^^

warning: function `bch2_sort_repack` is never used
   --> crates/subvol/src/btree/bset_build.rs:186:15
    |
186 | pub unsafe fn bch2_sort_repack(
    |               ^^^^^^^^^^^^^^^^

warning: function `bch2_btree_sort_into` is never used
   --> crates/subvol/src/btree/bset_build.rs:834:15
    |
834 | pub unsafe fn bch2_btree_sort_into(
    |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bset_byte_offset` is never used
    --> crates/subvol/src/btree/bset_build.rs:1004:15
     |
1004 | pub unsafe fn bset_byte_offset(b: *const btree, i: *const core::ffi::c_void) -> usize {
     |               ^^^^^^^^^^^^^^^^

warning: function `btree_node_hashed` is never used
   --> crates/subvol/src/btree/cache.rs:109:15
    |
109 | pub unsafe fn btree_node_hashed(b: *const btree) -> bool {
    |               ^^^^^^^^^^^^^^^^^

warning: constant `BTREE_EVICTED_SIZE_HASH_MASK` is never used
   --> crates/subvol/src/btree/cache.rs:113:11
    |
113 | pub const BTREE_EVICTED_SIZE_HASH_MASK: u64 = (1u64 << 48) - 1;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_evicted_size_pack` is never used
   --> crates/subvol/src/btree/cache.rs:115:14
    |
115 | pub const fn btree_evicted_size_pack(hash: u64, live_u64s: u16) -> u64 {
    |              ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_evicted_size_record` is never used
   --> crates/subvol/src/btree/cache.rs:119:15
    |
119 | pub unsafe fn bch2_btree_evicted_size_record(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_evicted_size_lookup` is never used
   --> crates/subvol/src/btree/cache.rs:131:15
    |
131 | pub unsafe fn bch2_btree_evicted_size_lookup(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_fs_btree_evicted_size_init` is never used
   --> crates/subvol/src/btree/cache.rs:148:15
    |
148 | pub unsafe fn bch2_fs_btree_evicted_size_init(c: *mut super::types::bch_fs) -> i32 {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_fs_btree_evicted_size_exit` is never used
   --> crates/subvol/src/btree/cache.rs:158:15
    |
158 | pub unsafe fn bch2_fs_btree_evicted_size_exit(c: *mut super::types::bch_fs) {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_node_cache_state` is never used
   --> crates/subvol/src/btree/cache.rs:166:15
    |
166 | pub unsafe fn btree_node_cache_state(b: *const btree) -> btree_node_cache_state {
    |               ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_NODE_RECLAIM_shrinker` is never used
   --> crates/subvol/src/btree/cache.rs:179:11
    |
179 | pub const BTREE_NODE_RECLAIM_shrinker: u32 = 1 << 0;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_node_is_root` is never used
   --> crates/subvol/src/btree/cache.rs:229:11
    |
229 | unsafe fn btree_node_is_root(c: *const super::types::bch_fs, b: *const btree) -> bool {
    |           ^^^^^^^^^^^^^^^^^^

warning: function `bch2_node_pin` is never used
   --> crates/subvol/src/btree/cache.rs:234:15
    |
234 | pub unsafe fn bch2_node_pin(c: *mut super::types::bch_fs, b: *mut btree) {
    |               ^^^^^^^^^^^^^

warning: function `bch2_btree_cache_unpin` is never used
   --> crates/subvol/src/btree/cache.rs:255:15
    |
255 | pub unsafe fn bch2_btree_cache_unpin(c: *mut super::types::bch_fs) {
    |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_evict` is never used
   --> crates/subvol/src/btree/cache.rs:668:15
    |
668 | pub unsafe fn bch2_btree_node_evict(trans: *mut btree_trans, key: *const super::bkey::bkey_i) {
    |               ^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_WRITE_cache_reclaim` is never used
  --> crates/subvol/src/btree/io.rs:21:11
   |
21 | pub const BTREE_WRITE_cache_reclaim: u32 = 2;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_WRITE_initial` is never used
  --> crates/subvol/src/btree/io.rs:22:11
   |
22 | pub const BTREE_WRITE_initial: u32 = 0;
   |           ^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_WRITE_journal_reclaim` is never used
  --> crates/subvol/src/btree/io.rs:23:11
   |
23 | pub const BTREE_WRITE_journal_reclaim: u32 = 3;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_WRITE_interior` is never used
  --> crates/subvol/src/btree/io.rs:24:11
   |
24 | pub const BTREE_WRITE_interior: u32 = 4;
   |           ^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_WRITE_TYPE_MASK` is never used
  --> crates/subvol/src/btree/io.rs:25:11
   |
25 | pub const BTREE_WRITE_TYPE_MASK: u32 = 7;
   |           ^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_WRITE_TYPE_BITS` is never used
  --> crates/subvol/src/btree/io.rs:26:11
   |
26 | pub const BTREE_WRITE_TYPE_BITS: u32 = 3;
   |           ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_io_unlock` is never used
  --> crates/subvol/src/btree/io.rs:35:15
   |
35 | pub unsafe fn bch2_btree_node_io_unlock(b: *mut btree) {
   |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_io_lock` is never used
  --> crates/subvol/src/btree/io.rs:42:15
   |
42 | pub unsafe fn bch2_btree_node_io_lock(b: *mut btree) {
   |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_wait_on_read` is never used
  --> crates/subvol/src/btree/io.rs:50:15
   |
50 | pub unsafe fn bch2_btree_node_wait_on_read(_trans: *mut super::iter::btree_trans, b: *mut btree) {
   |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_wait_on_write` is never used
  --> crates/subvol/src/btree/io.rs:57:15
   |
57 | pub unsafe fn bch2_btree_node_wait_on_write(_trans: *mut super::iter::btree_trans, b: *mut btree) {
   |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_flush_all_reads` is never used
   --> crates/subvol/src/btree/io.rs:173:15
    |
173 | pub unsafe fn bch2_btree_flush_all_reads(c: *mut super::types::bch_fs) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_flush_all_writes` is never used
   --> crates/subvol/src/btree/io.rs:214:15
    |
214 | pub unsafe fn bch2_btree_flush_all_writes(c: *mut super::types::bch_fs) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_cancel_all_writes` is never used
   --> crates/subvol/src/btree/io.rs:255:15
    |
255 | pub unsafe fn bch2_btree_cancel_all_writes(c: *mut super::types::bch_fs) {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_drop_keys_outside_node` is never used
   --> crates/subvol/src/btree/io.rs:671:15
    |
671 | pub unsafe fn bch2_btree_node_drop_keys_outside_node(b: *mut btree) {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_get_noiter` is never used
   --> crates/subvol/src/btree/io.rs:859:15
    |
859 | pub unsafe fn bch2_btree_node_get_noiter(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_get` is never used
   --> crates/subvol/src/btree/io.rs:890:15
    |
890 | pub unsafe fn bch2_btree_node_get(
    |               ^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_prefetch` is never used
   --> crates/subvol/src/btree/io.rs:973:15
    |
973 | pub unsafe fn bch2_btree_node_prefetch(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_ITER_prefetch` is never used
  --> crates/subvol/src/btree/iter.rs:47:11
   |
47 | pub const BTREE_ITER_prefetch: u16 = 1 << 2;
   |           ^^^^^^^^^^^^^^^^^^^

warning: function `btree_id_cached` is never used
  --> crates/subvol/src/btree/iter.rs:62:4
   |
62 | fn btree_id_cached(btree_id: u8) -> bool {
   |    ^^^^^^^^^^^^^^^

warning: function `btree_type_has_snapshot_field` is never used
  --> crates/subvol/src/btree/iter.rs:66:4
   |
66 | fn btree_type_has_snapshot_field(_btree_id: u8) -> bool {
   |    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_flags` is never used
  --> crates/subvol/src/btree/iter.rs:71:15
   |
71 | pub unsafe fn bch2_btree_iter_flags(
   |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_path_node` is never used
   --> crates/subvol/src/btree/iter.rs:105:15
    |
105 | pub unsafe fn btree_path_node(path: *mut btree_path, level: usize) -> *mut btree {
    |               ^^^^^^^^^^^^^^^

warning: function `btree_node_parent` is never used
   --> crates/subvol/src/btree/iter.rs:112:15
    |
112 | pub unsafe fn btree_node_parent(path: *mut btree_path, b: *mut btree) -> *mut btree {
    |               ^^^^^^^^^^^^^^^^^

warning: function `btree_node_locked_type_nowrite` is never used
   --> crates/subvol/src/btree/iter.rs:195:15
    |
195 | pub unsafe fn btree_node_locked_type_nowrite(path: *const btree_path, level: usize) -> u8 {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_node_write_locked` is never used
   --> crates/subvol/src/btree/iter.rs:204:15
    |
204 | pub unsafe fn btree_node_write_locked(path: *const btree_path, level: usize) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_node_intent_locked` is never used
   --> crates/subvol/src/btree/iter.rs:208:15
    |
208 | pub unsafe fn btree_node_intent_locked(path: *const btree_path, level: usize) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_node_read_locked` is never used
   --> crates/subvol/src/btree/iter.rs:212:15
    |
212 | pub unsafe fn btree_node_read_locked(path: *const btree_path, level: usize) -> bool {
    |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_path_lowest_level_locked` is never used
   --> crates/subvol/src/btree/iter.rs:253:15
    |
253 | pub unsafe fn btree_path_lowest_level_locked(path: *const btree_path) -> Option<usize> {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_path_upgrade_norestart` is never used
   --> crates/subvol/src/btree/iter.rs:755:15
    |
755 | pub unsafe fn bch2_btree_path_upgrade_norestart(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_upgrade` is never used
   --> crates/subvol/src/btree/iter.rs:848:15
    |
848 | pub unsafe fn bch2_btree_node_upgrade(
    |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_path_can_relock` is never used
    --> crates/subvol/src/btree/iter.rs:1307:15
     |
1307 | pub unsafe fn bch2_btree_path_can_relock(_trans: *mut btree_trans, path: *mut btree_path) -> bool {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_iter_init_outlined` is never used
    --> crates/subvol/src/btree/iter.rs:1760:15
     |
1760 | pub unsafe fn bch2_trans_iter_init_outlined(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_set_snapshot` is never used
    --> crates/subvol/src/btree/iter.rs:1846:15
     |
1846 | pub unsafe fn bch2_btree_iter_set_snapshot(iter: *mut btree_iter, snapshot: u32) {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_set_pos_to_extent_start` is never used
    --> crates/subvol/src/btree/iter.rs:1856:15
     |
1856 | pub unsafe fn bch2_btree_iter_set_pos_to_extent_start(iter: *mut btree_iter) {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_set_btree_iter_dontneed` is never used
    --> crates/subvol/src/btree/iter.rs:1863:15
     |
1863 | pub unsafe fn bch2_set_btree_iter_dontneed(iter: *mut btree_iter) {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_get_iter` is never used
    --> crates/subvol/src/btree/iter.rs:1905:15
     |
1905 | pub unsafe fn bch2_btree_node_get_iter(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_peek_type` is never used
    --> crates/subvol/src/btree/iter.rs:1936:15
     |
1936 | pub unsafe fn bch2_btree_iter_peek_type(iter: *mut btree_iter, flags: u16) -> bkey_s_c {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_peek_prev_type` is never used
    --> crates/subvol/src/btree/iter.rs:1944:15
     |
1944 | pub unsafe fn bch2_btree_iter_peek_prev_type(iter: *mut btree_iter, flags: u16) -> bkey_s_c {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_peek_max_type` is never used
    --> crates/subvol/src/btree/iter.rs:1952:15
     |
1952 | pub unsafe fn bch2_btree_iter_peek_max_type(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_peek_and_restart_outlined` is never used
    --> crates/subvol/src/btree/iter.rs:1969:15
     |
1969 | pub unsafe fn bch2_btree_iter_peek_and_restart_outlined(iter: *mut btree_iter) -> bkey_s_c {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_next_slot` is never used
    --> crates/subvol/src/btree/iter.rs:2620:15
     |
2620 | pub unsafe fn bch2_btree_iter_next_slot(iter: *mut btree_iter) -> bkey_s_c {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_peek_node` is never used
    --> crates/subvol/src/btree/iter.rs:2628:15
     |
2628 | pub unsafe fn bch2_btree_iter_peek_node(iter: *mut btree_iter) -> *mut btree {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_peek_root` is never used
    --> crates/subvol/src/btree/iter.rs:2655:15
     |
2655 | pub unsafe fn bch2_btree_iter_peek_root(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_rewind` is never used
    --> crates/subvol/src/btree/iter.rs:2701:15
     |
2701 | pub unsafe fn bch2_btree_iter_rewind(iter: *mut btree_iter) -> bool {
     |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_prev` is never used
    --> crates/subvol/src/btree/iter.rs:2724:15
     |
2724 | pub unsafe fn bch2_btree_iter_prev(iter: *mut btree_iter) -> bkey_s_c {
     |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_iter_prev_slot` is never used
    --> crates/subvol/src/btree/iter.rs:2732:15
     |
2732 | pub unsafe fn bch2_btree_iter_prev_slot(iter: *mut btree_iter) -> bkey_s_c {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_unlock_write` is never used
    --> crates/subvol/src/btree/iter.rs:3098:15
     |
3098 | pub unsafe fn bch2_trans_unlock_write(trans: *mut btree_trans) {
     |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_relock` is never used
    --> crates/subvol/src/btree/iter.rs:3128:15
     |
3128 | pub unsafe fn bch2_trans_relock(trans: *mut btree_trans) -> i32 {
     |               ^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_relock_notrace` is never used
    --> crates/subvol/src/btree/iter.rs:3132:15
     |
3132 | pub unsafe fn bch2_trans_relock_notrace(trans: *mut btree_trans) -> i32 {
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_unlock_long` is never used
    --> crates/subvol/src/btree/iter.rs:3156:15
     |
3156 | pub unsafe fn bch2_trans_unlock_long(trans: *mut btree_trans) {
     |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_downgrade` is never used
    --> crates/subvol/src/btree/iter.rs:3160:15
     |
3160 | pub unsafe fn bch2_trans_downgrade(trans: *mut btree_trans) {
     |               ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_node_iter_next_all` is never used
   --> crates/subvol/src/btree/node_iter.rs:345:15
    |
345 | pub unsafe fn bch2_btree_node_iter_next_all(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_USES_WRITE_BUFFER_MASK` is never used
  --> crates/subvol/src/btree/types.rs:24:11
   |
24 | pub const BTREE_USES_WRITE_BUFFER_MASK: u64 = 0;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `btree_type_uses_write_buffer` is never used
  --> crates/subvol/src/btree/types.rs:34:14
   |
34 | pub const fn btree_type_uses_write_buffer(btree: u8) -> bool {
   |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_VALIDATE_write` is never used
  --> crates/subvol/src/btree/types.rs:42:11
   |
42 | pub const BCH_VALIDATE_write: u8 = 1 << 0;
   |           ^^^^^^^^^^^^^^^^^^

warning: constant `BCH_VALIDATE_commit` is never used
  --> crates/subvol/src/btree/types.rs:43:11
   |
43 | pub const BCH_VALIDATE_commit: u8 = 1 << 1;
   |           ^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_VALIDATE_silent` is never used
  --> crates/subvol/src/btree/types.rs:44:11
   |
44 | pub const BCH_VALIDATE_silent: u8 = 1 << 2;
   |           ^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_VALIDATE_unknown` is never used
  --> crates/subvol/src/btree/types.rs:46:11
   |
46 | pub const BKEY_VALIDATE_unknown: u8 = 0;
   |           ^^^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_VALIDATE_superblock` is never used
  --> crates/subvol/src/btree/types.rs:47:11
   |
47 | pub const BKEY_VALIDATE_superblock: u8 = 1;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_VALIDATE_journal` is never used
  --> crates/subvol/src/btree/types.rs:48:11
   |
48 | pub const BKEY_VALIDATE_journal: u8 = 2;
   |           ^^^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_VALIDATE_btree_root` is never used
  --> crates/subvol/src/btree/types.rs:49:11
   |
49 | pub const BKEY_VALIDATE_btree_root: u8 = 3;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_VALIDATE_btree_node` is never used
  --> crates/subvol/src/btree/types.rs:50:11
   |
50 | pub const BKEY_VALIDATE_btree_node: u8 = 4;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BKEY_VALIDATE_commit` is never used
  --> crates/subvol/src/btree/types.rs:51:11
   |
51 | pub const BKEY_VALIDATE_commit: u8 = 5;
   |           ^^^^^^^^^^^^^^^^^^^^

warning: struct `bkey_validate_context` is never constructed
  --> crates/subvol/src/btree/types.rs:55:12
   |
55 | pub struct bkey_validate_context {
   |            ^^^^^^^^^^^^^^^^^^^^^

warning: struct `disk_reservation` is never constructed
  --> crates/subvol/src/btree/types.rs:68:12
   |
68 | pub struct disk_reservation {
   |            ^^^^^^^^^^^^^^^^

warning: constant `BCH_DISK_RESERVATION_NOFAIL` is never used
  --> crates/subvol/src/btree/types.rs:74:11
   |
74 | pub const BCH_DISK_RESERVATION_NOFAIL: u32 = 1 << 0;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_DISK_RESERVATION_PARTIAL` is never used
  --> crates/subvol/src/btree/types.rs:75:11
   |
75 | pub const BCH_DISK_RESERVATION_PARTIAL: u32 = 1 << 1;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: struct `bch_fs_usage_base` is never constructed
  --> crates/subvol/src/btree/types.rs:79:12
   |
79 | pub struct bch_fs_usage_base {
   |            ^^^^^^^^^^^^^^^^^

warning: struct `bch_fs_usage_short` is never constructed
  --> crates/subvol/src/btree/types.rs:89:12
   |
89 | pub struct bch_fs_usage_short {
   |            ^^^^^^^^^^^^^^^^^^

warning: struct `bch_fs_capacity_pcpu` is never constructed
  --> crates/subvol/src/btree/types.rs:97:12
   |
97 | pub struct bch_fs_capacity_pcpu {
   |            ^^^^^^^^^^^^^^^^^^^^

warning: constant `BSET_TREE_NR_TYPES` is never used
   --> crates/subvol/src/btree/types.rs:130:11
    |
130 | pub const BSET_TREE_NR_TYPES: usize = 3;
    |           ^^^^^^^^^^^^^^^^^^

warning: function `list_replace` is never used
   --> crates/subvol/src/btree/types.rs:197:15
    |
197 | pub unsafe fn list_replace(old: *const list_head, new: *mut list_head) {
    |               ^^^^^^^^^^^^

warning: function `list_replace_init` is never used
   --> crates/subvol/src/btree/types.rs:204:15
    |
204 | pub unsafe fn list_replace_init(old: *mut list_head, new: *mut list_head) {
    |               ^^^^^^^^^^^^^^^^^

warning: function `list_move` is never used
   --> crates/subvol/src/btree/types.rs:211:15
    |
211 | pub unsafe fn list_move(entry: *mut list_head, head: *mut list_head) {
    |               ^^^^^^^^^

warning: function `list_move_tail` is never used
   --> crates/subvol/src/btree/types.rs:216:15
    |
216 | pub unsafe fn list_move_tail(entry: *mut list_head, head: *mut list_head) {
    |               ^^^^^^^^^^^^^^

warning: function `list_empty` is never used
   --> crates/subvol/src/btree/types.rs:221:15
    |
221 | pub unsafe fn list_empty(head: *const list_head) -> bool {
    |               ^^^^^^^^^^

warning: function `list_empty_careful` is never used
   --> crates/subvol/src/btree/types.rs:225:15
    |
225 | pub unsafe fn list_empty_careful(head: *const list_head) -> bool {
    |               ^^^^^^^^^^^^^^^^^^

warning: function `list_splice_init` is never used
   --> crates/subvol/src/btree/types.rs:239:15
    |
239 | pub unsafe fn list_splice_init(list: *mut list_head, head: *mut list_head) {
    |               ^^^^^^^^^^^^^^^^

warning: function `list_splice_tail` is never used
   --> crates/subvol/src/btree/types.rs:244:15
    |
244 | pub unsafe fn list_splice_tail(list: *mut list_head, head: *mut list_head) {
    |               ^^^^^^^^^^^^^^^^

warning: function `list_splice_tail_init` is never used
   --> crates/subvol/src/btree/types.rs:257:15
    |
257 | pub unsafe fn list_splice_tail_init(list: *mut list_head, head: *mut list_head) {
    |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `list_count_nodes` is never used
   --> crates/subvol/src/btree/types.rs:262:15
    |
262 | pub unsafe fn list_count_nodes(head: *mut list_head) -> usize {
    |               ^^^^^^^^^^^^^^^^

warning: function `list_is_last` is never used
   --> crates/subvol/src/btree/types.rs:272:15
    |
272 | pub unsafe fn list_is_last(list: *const list_head, head: *const list_head) -> bool {
    |               ^^^^^^^^^^^^

warning: function `btree_node_pos` is never used
   --> crates/subvol/src/btree/types.rs:620:15
    |
620 | pub unsafe fn btree_node_pos(b: *mut btree_bkey_cached_common) -> super::bkey::bpos {
    |               ^^^^^^^^^^^^^^

warning: constant `BTREE_NODE_FLAGS_START` is never used
   --> crates/subvol/src/btree/types.rs:654:11
    |
654 | pub const BTREE_NODE_FLAGS_START: usize = 2;
    |           ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_NODE_dying` is never used
   --> crates/subvol/src/btree/types.rs:667:11
    |
667 | pub const BTREE_NODE_dying: usize = 15;
    |           ^^^^^^^^^^^^^^^^

warning: constant `BTREE_NODE_need_rewrite_error` is never used
   --> crates/subvol/src/btree/types.rs:670:11
    |
670 | pub const BTREE_NODE_need_rewrite_error: usize = 18;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_NODE_need_rewrite_ptr_written_zero` is never used
   --> crates/subvol/src/btree/types.rs:671:11
    |
671 | pub const BTREE_NODE_need_rewrite_ptr_written_zero: usize = 19;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `clear_btree_node_read_error` is never used
   --> crates/subvol/src/btree/types.rs:701:5
    |
701 |     clear_btree_node_read_error,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_need_write` is never used
   --> crates/subvol/src/btree/types.rs:712:5
    |
712 |     set_btree_node_need_write,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_need_write` is never used
   --> crates/subvol/src/btree/types.rs:713:5
    |
713 |     clear_btree_node_need_write,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_write_blocked` is never used
   --> crates/subvol/src/btree/types.rs:718:5
    |
718 |     set_btree_node_write_blocked,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_write_blocked` is never used
   --> crates/subvol/src/btree/types.rs:719:5
    |
719 |     clear_btree_node_write_blocked,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_will_make_reachable` is never used
   --> crates/subvol/src/btree/types.rs:724:5
    |
724 |     set_btree_node_will_make_reachable,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_will_make_reachable` is never used
   --> crates/subvol/src/btree/types.rs:725:5
    |
725 |     clear_btree_node_will_make_reachable,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_noevict` is never used
   --> crates/subvol/src/btree/types.rs:730:5
    |
730 |     set_btree_node_noevict,
    |     ^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_write_idx` is never used
   --> crates/subvol/src/btree/types.rs:734:15
    |
734 | pub unsafe fn set_btree_node_write_idx(b: *mut btree) {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `clear_btree_node_write_idx` is never used
   --> crates/subvol/src/btree/types.rs:738:15
    |
738 | pub unsafe fn clear_btree_node_write_idx(b: *mut btree) {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `clear_btree_node_accessed` is never used
   --> crates/subvol/src/btree/types.rs:744:5
    |
744 |     clear_btree_node_accessed,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_write_in_flight` is never used
   --> crates/subvol/src/btree/types.rs:749:5
    |
749 |     set_btree_node_write_in_flight,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_write_in_flight` is never used
   --> crates/subvol/src/btree/types.rs:750:5
    |
750 |     clear_btree_node_write_in_flight,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_node_write_in_flight_inner` is never used
   --> crates/subvol/src/btree/types.rs:754:5
    |
754 |     btree_node_write_in_flight_inner,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_write_in_flight_inner` is never used
   --> crates/subvol/src/btree/types.rs:755:5
    |
755 |     set_btree_node_write_in_flight_inner,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_write_in_flight_inner` is never used
   --> crates/subvol/src/btree/types.rs:756:5
    |
756 |     clear_btree_node_write_in_flight_inner,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_just_written` is never used
   --> crates/subvol/src/btree/types.rs:761:5
    |
761 |     set_btree_node_just_written,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_node_dying` is never used
   --> crates/subvol/src/btree/types.rs:766:5
    |
766 |     btree_node_dying,
    |     ^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_dying` is never used
   --> crates/subvol/src/btree/types.rs:767:5
    |
767 |     set_btree_node_dying,
    |     ^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_dying` is never used
   --> crates/subvol/src/btree/types.rs:768:5
    |
768 |     clear_btree_node_dying,
    |     ^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_node_fake` is never used
   --> crates/subvol/src/btree/types.rs:772:5
    |
772 |     btree_node_fake,
    |     ^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_node_need_rewrite` is never used
   --> crates/subvol/src/btree/types.rs:778:5
    |
778 |     btree_node_need_rewrite,
    |     ^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_node_need_rewrite_error` is never used
   --> crates/subvol/src/btree/types.rs:784:5
    |
784 |     btree_node_need_rewrite_error,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_need_rewrite_error` is never used
   --> crates/subvol/src/btree/types.rs:785:5
    |
785 |     set_btree_node_need_rewrite_error,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_need_rewrite_error` is never used
   --> crates/subvol/src/btree/types.rs:786:5
    |
786 |     clear_btree_node_need_rewrite_error,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_node_need_rewrite_ptr_written_zero` is never used
   --> crates/subvol/src/btree/types.rs:790:5
    |
790 |     btree_node_need_rewrite_ptr_written_zero,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_need_rewrite_ptr_written_zero` is never used
   --> crates/subvol/src/btree/types.rs:791:5
    |
791 |     set_btree_node_need_rewrite_ptr_written_zero,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_need_rewrite_ptr_written_zero` is never used
   --> crates/subvol/src/btree/types.rs:792:5
    |
792 |     clear_btree_node_need_rewrite_ptr_written_zero,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_never_write` is never used
   --> crates/subvol/src/btree/types.rs:797:5
    |
797 |     set_btree_node_never_write,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_never_write` is never used
   --> crates/subvol/src/btree/types.rs:798:5
    |
798 |     clear_btree_node_never_write,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `set_btree_node_pinned` is never used
   --> crates/subvol/src/btree/types.rs:803:5
    |
803 |     set_btree_node_pinned,
    |     ^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `clear_btree_node_pinned` is never used
   --> crates/subvol/src/btree/types.rs:804:5
    |
804 |     clear_btree_node_pinned,
    |     ^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `btree_node_flag_fns` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `btree_bset_last` is never used
   --> crates/subvol/src/btree/types.rs:927:15
    |
927 | pub unsafe fn btree_bset_last(b: *mut btree) -> *mut disk_bset {
    |               ^^^^^^^^^^^^^^^

warning: function `bch2_trans_kmalloc_ip` is never used
   --> crates/subvol/src/btree/update.rs:133:15
    |
133 | pub unsafe fn bch2_trans_kmalloc_ip(trans: *mut btree_trans, size: usize, _ip: usize) -> *mut u8 {
    |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_kmalloc_nomemzero_ip` is never used
   --> crates/subvol/src/btree/update.rs:137:15
    |
137 | pub unsafe fn bch2_trans_kmalloc_nomemzero_ip(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_subbuf_alloc` is never used
   --> crates/subvol/src/btree/update.rs:191:15
    |
191 | pub unsafe fn bch2_trans_subbuf_alloc(
    |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_subbuf_alloc_ip` is never used
   --> crates/subvol/src/btree/update.rs:203:15
    |
203 | pub unsafe fn bch2_trans_subbuf_alloc_ip(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_subbuf_reserve` is never used
   --> crates/subvol/src/btree/update.rs:212:15
    |
212 | pub unsafe fn bch2_trans_subbuf_reserve(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_jset_entry_alloc_ip` is never used
   --> crates/subvol/src/btree/update.rs:225:15
    |
225 | pub unsafe fn bch2_trans_jset_entry_alloc_ip(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_jset_entry_alloc` is never used
   --> crates/subvol/src/btree/update.rs:246:15
    |
246 | pub unsafe fn bch2_trans_jset_entry_alloc(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_get_mut_noupdate` is never used
   --> crates/subvol/src/btree/update.rs:287:15
    |
287 | pub unsafe fn bch2_bkey_get_mut_noupdate(iter: *mut btree_iter) -> *mut bkey_i {
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_make_mut` is never used
   --> crates/subvol/src/btree/update.rs:298:15
    |
298 | pub unsafe fn bch2_bkey_make_mut(
    |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_get_mut` is never used
   --> crates/subvol/src/btree/update.rs:318:15
    |
318 | pub unsafe fn bch2_bkey_get_mut(
    |               ^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_get_mut_minsize` is never used
   --> crates/subvol/src/btree/update.rs:327:15
    |
327 | pub unsafe fn bch2_bkey_get_mut_minsize(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_alloc` is never used
   --> crates/subvol/src/btree/update.rs:378:15
    |
378 | pub unsafe fn bch2_bkey_alloc(
    |               ^^^^^^^^^^^^^^^

warning: constant `BTREE_UPDATE_none` is never used
   --> crates/subvol/src/btree/update.rs:410:11
    |
410 | pub const BTREE_UPDATE_none: u32 = 0;
    |           ^^^^^^^^^^^^^^^^^

warning: constant `BTREE_TRIGGER_transactional` is never used
   --> crates/subvol/src/btree/update.rs:414:11
    |
414 | pub const BTREE_TRIGGER_transactional: u32 = 1 << 22;
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BTREE_TRIGGER_gc` is never used
   --> crates/subvol/src/btree/update.rs:416:11
    |
416 | pub const BTREE_TRIGGER_gc: u32 = 1 << 24;
    |           ^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_no_enospc` is never used
   --> crates/subvol/src/btree/update.rs:420:11
    |
420 | pub const BCH_TRANS_COMMIT_no_enospc: u32 = 1 << (crate::journal::BCH_WATERMARK_BITS + 0);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_no_check_rw` is never used
   --> crates/subvol/src/btree/update.rs:421:11
    |
421 | pub const BCH_TRANS_COMMIT_no_check_rw: u32 = 1 << (crate::journal::BCH_WATERMARK_BITS + 1);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_no_journal_res` is never used
   --> crates/subvol/src/btree/update.rs:422:11
    |
422 | pub const BCH_TRANS_COMMIT_no_journal_res: u32 = 1 << (crate::journal::BCH_WATERMARK_BITS + 2);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_no_skip_noops` is never used
   --> crates/subvol/src/btree/update.rs:423:11
    |
423 | pub const BCH_TRANS_COMMIT_no_skip_noops: u32 = 1 << (crate::journal::BCH_WATERMARK_BITS + 3);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_journal_reclaim` is never used
   --> crates/subvol/src/btree/update.rs:424:11
    |
424 | pub const BCH_TRANS_COMMIT_journal_reclaim: u32 = 1 << (crate::journal::BCH_WATERMARK_BITS + 4);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_journal_replay` is never used
   --> crates/subvol/src/btree/update.rs:425:11
    |
425 | pub const BCH_TRANS_COMMIT_journal_replay: u32 = 1 << (crate::journal::BCH_WATERMARK_BITS + 5);
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_TRANS_COMMIT_skip_accounting_apply` is never used
   --> crates/subvol/src/btree/update.rs:426:11
    |
426 | pub const BCH_TRANS_COMMIT_skip_accounting_apply: u32 =
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trigger_get_mutable_new` is never used
   --> crates/subvol/src/btree/update.rs:920:15
    |
920 | pub unsafe fn bch2_trigger_get_mutable_new(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_delete` is never used
    --> crates/subvol/src/btree/update.rs:1086:15
     |
1086 | pub unsafe fn bch2_btree_delete(
     |               ^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_insert_trans` is never used
    --> crates/subvol/src/btree/update.rs:1139:15
     |
1139 | pub unsafe fn bch2_btree_insert_trans(
     |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_insert` is never used
    --> crates/subvol/src/btree/update.rs:1164:15
     |
1164 | pub unsafe fn bch2_btree_insert(
     |               ^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_insert_clone_trans` is never used
    --> crates/subvol/src/btree/update.rs:1184:15
     |
1184 | pub unsafe fn bch2_btree_insert_clone_trans(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_bkey_get_empty_slot` is never used
    --> crates/subvol/src/btree/update.rs:1200:15
     |
1200 | pub unsafe fn bch2_bkey_get_empty_slot(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_delete_range_trans` is never used
    --> crates/subvol/src/btree/update.rs:1234:15
     |
1234 | pub unsafe fn bch2_btree_delete_range_trans(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_delete_range` is never used
    --> crates/subvol/src/btree/update.rs:1309:15
     |
1309 | pub unsafe fn bch2_btree_delete_range(
     |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_bit_mod_iter` is never used
    --> crates/subvol/src/btree/update.rs:1329:15
     |
1329 | pub unsafe fn bch2_btree_bit_mod_iter(
     |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_bit_mod` is never used
    --> crates/subvol/src/btree/update.rs:1354:15
     |
1354 | pub unsafe fn bch2_btree_bit_mod(
     |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_update_buffered` is never used
    --> crates/subvol/src/btree/update.rs:1375:15
     |
1375 | pub unsafe fn bch2_trans_update_buffered(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_bit_mod_buffered` is never used
    --> crates/subvol/src/btree/update.rs:1402:15
     |
1402 | pub unsafe fn bch2_btree_bit_mod_buffered(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_btree_delete_at_buffered` is never used
    --> crates/subvol/src/btree/update.rs:1424:15
     |
1424 | pub unsafe fn bch2_btree_delete_at_buffered(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_log_bkey` is never used
    --> crates/subvol/src/btree/update.rs:1432:15
     |
1432 | pub unsafe fn bch2_trans_log_bkey(
     |               ^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_log_str` is never used
    --> crates/subvol/src/btree/update.rs:1457:15
     |
1457 | pub unsafe fn bch2_trans_log_str(trans: *mut btree_trans, str_: *const u8) -> i32 {
     |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_update_buf` is never used
    --> crates/subvol/src/btree/update.rs:1535:15
     |
1535 | pub unsafe fn bch2_trans_update_buf(
     |               ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_trans_commit_hook` is never used
    --> crates/subvol/src/btree/update.rs:1552:15
     |
1552 | pub unsafe fn bch2_trans_commit_hook(trans: *mut btree_trans, hook: *mut btree_trans_commit_hook) {
     |               ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_CSUM_chacha20_poly1305_80` is never used
 --> crates/subvol/src/checksum.rs:4:11
  |
4 | pub const BCH_CSUM_chacha20_poly1305_80: u32 = 3;
  |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_CSUM_chacha20_poly1305_128` is never used
 --> crates/subvol/src/checksum.rs:5:11
  |
5 | pub const BCH_CSUM_chacha20_poly1305_128: u32 = 4;
  |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_checksum_mergeable` is never used
  --> crates/subvol/src/checksum.rs:12:14
   |
12 | pub const fn bch2_checksum_mergeable(type_: u32) -> bool {
   |              ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_checksum_merge` is never used
  --> crates/subvol/src/checksum.rs:16:8
   |
16 | pub fn bch2_checksum_merge(
   |        ^^^^^^^^^^^^^^^^^^^

warning: function `bch2_keylist_empty` is never used
  --> crates/subvol/src/data/keylist.rs:51:15
   |
51 | pub unsafe fn bch2_keylist_empty(list: *const keylist) -> bool {
   |               ^^^^^^^^^^^^^^^^^^

warning: function `bch2_keylist_u64s` is never used
  --> crates/subvol/src/data/keylist.rs:55:15
   |
55 | pub unsafe fn bch2_keylist_u64s(list: *const keylist) -> usize {
   |               ^^^^^^^^^^^^^^^^^

warning: function `bch2_keylist_bytes` is never used
  --> crates/subvol/src/data/keylist.rs:59:15
   |
59 | pub unsafe fn bch2_keylist_bytes(list: *const keylist) -> usize {
   |               ^^^^^^^^^^^^^^^^^^

warning: constant `JOURNAL_ENTRY_SIZE_MIN` is never used
  --> crates/subvol/src/journal.rs:12:11
   |
12 | pub const JOURNAL_ENTRY_SIZE_MIN: usize = 64 << 10;
   |           ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_JSET_ENTRY_overwrite` is never used
  --> crates/subvol/src/journal.rs:25:11
   |
25 | pub const BCH_JSET_ENTRY_overwrite: u8 = 10;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_JSET_ENTRY_log` is never used
  --> crates/subvol/src/journal.rs:27:11
   |
27 | pub const BCH_JSET_ENTRY_log: u8 = 9;
   |           ^^^^^^^^^^^^^^^^^^

warning: constant `BCH_JSET_ENTRY_log_bkey` is never used
  --> crates/subvol/src/journal.rs:28:11
   |
28 | pub const BCH_JSET_ENTRY_log_bkey: u8 = 13;
   |           ^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `JOURNAL_degraded` is never used
  --> crates/subvol/src/journal.rs:31:11
   |
31 | pub const JOURNAL_degraded: usize = 0;
   |           ^^^^^^^^^^^^^^^^

warning: constant `JOURNAL_running` is never used
  --> crates/subvol/src/journal.rs:33:11
   |
33 | pub const JOURNAL_running: usize = 2;
   |           ^^^^^^^^^^^^^^^

warning: constant `JOURNAL_need_flush_write` is never used
  --> crates/subvol/src/journal.rs:35:11
   |
35 | pub const JOURNAL_need_flush_write: usize = 4;
   |           ^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `JOURNAL_low_on_wb` is never used
  --> crates/subvol/src/journal.rs:39:11
   |
39 | pub const JOURNAL_low_on_wb: usize = 8;
   |           ^^^^^^^^^^^^^^^^^

warning: function `JSET_CSUM_TYPE` is never used
  --> crates/subvol/src/journal.rs:76:14
   |
76 | pub const fn JSET_CSUM_TYPE(j: &jset) -> u32 {
   |              ^^^^^^^^^^^^^^

warning: function `JSET_BIG_ENDIAN` is never used
  --> crates/subvol/src/journal.rs:81:14
   |
81 | pub const fn JSET_BIG_ENDIAN(j: &jset) -> u32 {
   |              ^^^^^^^^^^^^^^^

warning: function `SET_JSET_NO_FLUSH` is never used
  --> crates/subvol/src/journal.rs:91:8
   |
91 | pub fn SET_JSET_NO_FLUSH(j: &mut jset, value: u32) {
   |        ^^^^^^^^^^^^^^^^^

warning: variants `BCH_WATERMARK_normal`, `BCH_WATERMARK_copygc`, `BCH_WATERMARK_btree`, `BCH_WATERMARK_btree_copygc`, and `BCH_WATERMARK_interior_updates` are never constructed
   --> crates/subvol/src/journal.rs:160:5
    |
158 | pub enum bch_watermark {
    |          ------------- variants in this enum
159 |     BCH_WATERMARK_stripe,
160 |     BCH_WATERMARK_normal,
    |     ^^^^^^^^^^^^^^^^^^^^
161 |     BCH_WATERMARK_copygc,
    |     ^^^^^^^^^^^^^^^^^^^^
162 |     BCH_WATERMARK_btree,
    |     ^^^^^^^^^^^^^^^^^^^
163 |     BCH_WATERMARK_btree_copygc,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^
164 |     BCH_WATERMARK_reclaim,
165 |     BCH_WATERMARK_interior_updates,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: `bch_watermark` has derived impls for the traits `Debug` and `Clone`, but these are intentionally ignored during dead code analysis

warning: variant `JOURNAL_PIN_TYPE_key_cache` is never constructed
   --> crates/subvol/src/journal.rs:190:5
    |
185 | pub enum journal_pin_type {
    |          ---------------- variant in this enum
...
190 |     JOURNAL_PIN_TYPE_key_cache,
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
    = note: `journal_pin_type` has derived impls for the traits `Debug` and `Clone`, but these are intentionally ignored during dead code analysis

warning: fields `devs_nr`, `devs`, and `bytes` are never read
   --> crates/subvol/src/journal.rs:203:9
    |
198 | pub struct journal_entry_pin_list {
    |            ---------------------- fields in this struct
...
203 |     pub devs_nr: u8,
    |         ^^^^^^^
204 |     pub devs: [u8; crate::btree::types::BCH_BKEY_PTRS_MAX],
    |         ^^^^
205 |     pub bytes: u32,
    |         ^^^^^
    |
    = note: `journal_entry_pin_list` has a derived impl for the trait `Debug`, but this is intentionally ignored during dead code analysis

warning: function `journal_pin_list_init` is never used
   --> crates/subvol/src/journal.rs:338:8
    |
338 | pub fn journal_pin_list_init(p: &mut journal_entry_pin_list, count: u32) {
    |        ^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_journal_pin_update` is never used
   --> crates/subvol/src/journal.rs:614:15
    |
614 | pub unsafe fn bch2_journal_pin_update(
    |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_key_deleted_in_journal` is never used
    --> crates/subvol/src/journal.rs:2081:15
     |
2081 | pub unsafe fn bch2_key_deleted_in_journal(
     |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `six_lock_contended` is never used
   --> crates/subvol/src/lock/six.rs:510:8
    |
510 | pub fn six_lock_contended(
    |        ^^^^^^^^^^^^^^^^^^

warning: function `six_trylock_convert` is never used
   --> crates/subvol/src/lock/six.rs:555:8
    |
555 | pub fn six_trylock_convert(lock: &six_lock, from: six_lock_type, to: six_lock_type) -> bool {
    |        ^^^^^^^^^^^^^^^^^^^

warning: function `six_trylock_read` is never used
   --> crates/subvol/src/lock/six.rs:654:5
    |
654 |     six_trylock_read,
    |     ^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `six_type_wrappers` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `six_relock_read` is never used
   --> crates/subvol/src/lock/six.rs:655:5
    |
655 |     six_relock_read,
    |     ^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `six_type_wrappers` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `six_relock_intent` is never used
   --> crates/subvol/src/lock/six.rs:662:5
    |
662 |     six_relock_intent,
    |     ^^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `six_type_wrappers` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: function `six_relock_write` is never used
   --> crates/subvol/src/lock/six.rs:669:5
    |
669 |     six_relock_write,
    |     ^^^^^^^^^^^^^^^^
    |
    = note: this warning originates in the macro `six_type_wrappers` (in Nightly builds, run with -Z macro-backtrace for more info)

warning: constant `BCH_SB_SECTOR` is never used
 --> crates/subvol/src/sb/mod.rs:4:11
  |
4 | pub const BCH_SB_SECTOR: u64 = 8;
  |           ^^^^^^^^^^^^^

warning: constant `BCH_SB_LAYOUT_SECTOR` is never used
 --> crates/subvol/src/sb/mod.rs:5:11
  |
5 | pub const BCH_SB_LAYOUT_SECTOR: u64 = 7;
  |           ^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_SB_LAYOUT_SIZE_BITS_MAX` is never used
 --> crates/subvol/src/sb/mod.rs:6:11
  |
6 | pub const BCH_SB_LAYOUT_SIZE_BITS_MAX: u8 = 16;
  |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_SB_MEMBERS_MAX` is never used
 --> crates/subvol/src/sb/mod.rs:7:11
  |
7 | pub const BCH_SB_MEMBERS_MAX: usize = 256;
  |           ^^^^^^^^^^^^^^^^^^

warning: constant `BCH_SB_MEMBER_INVALID` is never used
 --> crates/subvol/src/sb/mod.rs:8:11
  |
8 | pub const BCH_SB_MEMBER_INVALID: u8 = 255;
  |           ^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_SB_MEMBER_DELETED_UUID` is never used
 --> crates/subvol/src/sb/mod.rs:9:11
  |
9 | pub const BCH_SB_MEMBER_DELETED_UUID: [u8; 16] = [
  |           ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `BCH_VERSION_MAJOR` is never used
  --> crates/subvol/src/sb/mod.rs:23:14
   |
23 | pub const fn BCH_VERSION_MAJOR(version: u16) -> u16 {
   |              ^^^^^^^^^^^^^^^^^

warning: function `BCH_VERSION_MINOR` is never used
  --> crates/subvol/src/sb/mod.rs:27:14
   |
27 | pub const fn BCH_VERSION_MINOR(version: u16) -> u16 {
   |              ^^^^^^^^^^^^^^^^^

warning: function `bch2_member_alive` is never used
  --> crates/subvol/src/sb/mod.rs:33:8
   |
33 | pub fn bch2_member_alive(member: &bch_member) -> bool {
   |        ^^^^^^^^^^^^^^^^^

warning: function `bch2_mi_to_cpu` is never used
  --> crates/subvol/src/sb/mod.rs:37:8
   |
37 | pub fn bch2_mi_to_cpu(member: &bch_member) -> bch_member_cpu {
   |        ^^^^^^^^^^^^^^

warning: struct `bch_member_cpu` is never constructed
  --> crates/subvol/src/sb/mod.rs:93:12
   |
93 | pub struct bch_member_cpu {
   |            ^^^^^^^^^^^^^^

warning: constant `BCH_SB_HANDLE_HAVE_BIO` is never used
   --> crates/subvol/src/sb/mod.rs:280:11
    |
280 | pub const BCH_SB_HANDLE_HAVE_BIO: u32 = 1 << 1;
    |           ^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_layout` is never used
 --> crates/subvol/src/sb/io.rs:8:7
  |
8 | const BCH_ERR_invalid_sb_layout: i32 = -1;
  |       ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_layout_type` is never used
 --> crates/subvol/src/sb/io.rs:9:7
  |
9 | const BCH_ERR_invalid_sb_layout_type: i32 = -2;
  |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_layout_nr_superblocks` is never used
  --> crates/subvol/src/sb/io.rs:10:7
   |
10 | const BCH_ERR_invalid_sb_layout_nr_superblocks: i32 = -3;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_layout_superblocks_overlap` is never used
  --> crates/subvol/src/sb/io.rs:11:7
   |
11 | const BCH_ERR_invalid_sb_layout_superblocks_overlap: i32 = -4;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_layout_sb_max_size_bits` is never used
  --> crates/subvol/src/sb/io.rs:12:7
   |
12 | const BCH_ERR_invalid_sb_layout_sb_max_size_bits: i32 = -5;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_version` is never used
  --> crates/subvol/src/sb/io.rs:13:7
   |
13 | const BCH_ERR_invalid_sb_version: i32 = -6;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_features` is never used
  --> crates/subvol/src/sb/io.rs:16:7
   |
16 | const BCH_ERR_invalid_sb_features: i32 = -15;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_uuid` is never used
  --> crates/subvol/src/sb/io.rs:17:7
   |
17 | const BCH_ERR_invalid_sb_uuid: i32 = -16;
   |       ^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_offset` is never used
  --> crates/subvol/src/sb/io.rs:18:7
   |
18 | const BCH_ERR_invalid_sb_offset: i32 = -17;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_too_many_members` is never used
  --> crates/subvol/src/sb/io.rs:19:7
   |
19 | const BCH_ERR_invalid_sb_too_many_members: i32 = -18;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_dev_idx` is never used
  --> crates/subvol/src/sb/io.rs:20:7
   |
20 | const BCH_ERR_invalid_sb_dev_idx: i32 = -19;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_time_precision` is never used
  --> crates/subvol/src/sb/io.rs:21:7
   |
21 | const BCH_ERR_invalid_sb_time_precision: i32 = -20;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_field_size` is never used
  --> crates/subvol/src/sb/io.rs:22:7
   |
22 | const BCH_ERR_invalid_sb_field_size: i32 = -21;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_members_missing` is never used
  --> crates/subvol/src/sb/io.rs:23:7
   |
23 | const BCH_ERR_invalid_sb_members_missing: i32 = -22;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_members` is never used
  --> crates/subvol/src/sb/io.rs:24:7
   |
24 | const BCH_ERR_invalid_sb_members: i32 = -23;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_journal` is never used
  --> crates/subvol/src/sb/io.rs:25:7
   |
25 | const BCH_ERR_invalid_sb_journal: i32 = -24;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: constant `BCH_ERR_invalid_sb_field_type` is never used
  --> crates/subvol/src/sb/io.rs:26:7
   |
26 | const BCH_ERR_invalid_sb_field_type: i32 = -25;
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_sb_field_get_minsize_id` is never used
   --> crates/subvol/src/sb/io.rs:166:15
    |
166 | pub unsafe fn bch2_sb_field_get_minsize_id(
    |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_sb_field_delete` is never used
   --> crates/subvol/src/sb/io.rs:178:15
    |
178 | pub unsafe fn bch2_sb_field_delete(sb: *mut bch_sb_handle, type_: u32) {
    |               ^^^^^^^^^^^^^^^^^^^^

warning: function `validate_sb_layout` is never used
   --> crates/subvol/src/sb/io.rs:185:8
    |
185 | pub fn validate_sb_layout(layout: &bch_sb_layout) -> i32 {
    |        ^^^^^^^^^^^^^^^^^^

warning: function `bch2_sb_compatible` is never used
   --> crates/subvol/src/sb/io.rs:214:8
    |
214 | pub fn bch2_sb_compatible(sb: &bch_sb) -> i32 {
    |        ^^^^^^^^^^^^^^^^^^

warning: function `BCH_SB_VERSION_INCOMPAT` is never used
   --> crates/subvol/src/sb/io.rs:260:4
    |
260 | fn BCH_SB_VERSION_INCOMPAT(sb: &bch_sb) -> u16 {
    |    ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `BCH_SB_VERSION_INCOMPAT_ALLOWED` is never used
   --> crates/subvol/src/sb/io.rs:264:4
    |
264 | fn BCH_SB_VERSION_INCOMPAT_ALLOWED(sb: &bch_sb) -> u16 {
    |    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `SET_BCH_SB_VERSION_INCOMPAT_ALLOWED` is never used
   --> crates/subvol/src/sb/io.rs:268:4
    |
268 | fn SET_BCH_SB_VERSION_INCOMPAT_ALLOWED(sb: &mut bch_sb, value: u16) {
    |    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `validate_member` is never used
   --> crates/subvol/src/sb/io.rs:273:4
    |
273 | fn validate_member(member: bch_member, sb: &bch_sb, _index: usize) -> i32 {
    |    ^^^^^^^^^^^^^^^

warning: function `bch2_sb_members_v2_validate` is never used
   --> crates/subvol/src/sb/io.rs:299:11
    |
299 | unsafe fn bch2_sb_members_v2_validate(sb: *mut bch_sb, field: *mut bch_sb_field) -> i32 {
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_sb_journal_v2_validate` is never used
   --> crates/subvol/src/sb/io.rs:319:11
    |
319 | unsafe fn bch2_sb_journal_v2_validate(sb: *mut bch_sb, field: *mut bch_sb_field) -> i32 {
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_sb_field_validate` is never used
   --> crates/subvol/src/sb/io.rs:365:11
    |
365 | unsafe fn bch2_sb_field_validate(sb: *mut bch_sb, field: *mut bch_sb_field) -> i32 {
    |           ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_sb_validate` is never used
   --> crates/subvol/src/sb/io.rs:373:15
    |
373 | pub unsafe fn bch2_sb_validate(
    |               ^^^^^^^^^^^^^^^^

warning: function `BCH_SB_CSUM_TYPE` is never used
   --> crates/subvol/src/sb/io.rs:471:4
    |
471 | fn BCH_SB_CSUM_TYPE(sb: &bch_sb) -> u32 {
    |    ^^^^^^^^^^^^^^^^

warning: function `read_one_super` is never used
   --> crates/subvol/src/sb/io.rs:481:11
    |
481 | unsafe fn read_one_super(sb: *mut bch_sb_handle, offset: u64) -> i32 {
    |           ^^^^^^^^^^^^^^

warning: function `read_layout_sector` is never used
   --> crates/subvol/src/sb/io.rs:539:11
    |
539 | unsafe fn read_layout_sector(sb: *mut bch_sb_handle, layout: *mut bch_sb_layout) -> i32 {
    |           ^^^^^^^^^^^^^^^^^^

warning: function `read_backup_supers` is never used
   --> crates/subvol/src/sb/io.rs:559:11
    |
559 | unsafe fn read_backup_supers(
    |           ^^^^^^^^^^^^^^^^^^

warning: function `bch2_read_super` is never used
   --> crates/subvol/src/sb/io.rs:597:15
    |
597 | pub unsafe fn bch2_read_super(
    |               ^^^^^^^^^^^^^^^

warning: function `snapshot_list_merge` is never used
  --> crates/subvol/src/snapshot.rs:91:15
   |
91 | pub unsafe fn snapshot_list_merge(
   |               ^^^^^^^^^^^^^^^^^^^

warning: struct `bch_snapshot_tree` is never constructed
   --> crates/subvol/src/snapshot.rs:123:12
    |
123 | pub struct bch_snapshot_tree {
    |            ^^^^^^^^^^^^^^^^^

warning: struct `bkey_i_snapshot` is never constructed
   --> crates/subvol/src/snapshot.rs:131:12
    |
131 | pub struct bkey_i_snapshot {
    |            ^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_parent` is never used
   --> crates/subvol/src/snapshot.rs:193:8
    |
193 | pub fn bch2_snapshot_parent(c: &bch_fs, id: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_tree` is never used
   --> crates/subvol/src/snapshot.rs:198:8
    |
198 | pub fn bch2_snapshot_tree(c: &bch_fs, id: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshots_same_tree` is never used
   --> crates/subvol/src/snapshot.rs:203:8
    |
203 | pub fn bch2_snapshots_same_tree(c: &bch_fs, id1: u32, id2: u32) -> bool {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_nth_parent` is never used
   --> crates/subvol/src/snapshot.rs:214:8
    |
214 | pub fn bch2_snapshot_nth_parent(c: &bch_fs, mut id: u32, mut n: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_skiplist_get` is never used
   --> crates/subvol/src/snapshot.rs:223:8
    |
223 | pub fn bch2_snapshot_skiplist_get(c: &bch_fs, mut id: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_root` is never used
   --> crates/subvol/src/snapshot.rs:248:8
    |
248 | pub fn bch2_snapshot_root(c: &bch_fs, mut id: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_id_state` is never used
   --> crates/subvol/src/snapshot.rs:259:8
    |
259 | pub fn bch2_snapshot_id_state(c: &bch_fs, id: u32) -> snapshot_id_state {
    |        ^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_exists` is never used
   --> crates/subvol/src/snapshot.rs:264:8
    |
264 | pub fn bch2_snapshot_exists(c: &bch_fs, id: u32) -> bool {
    |        ^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_depth` is never used
   --> crates/subvol/src/snapshot.rs:285:8
    |
285 | pub fn bch2_snapshot_depth(c: &bch_fs, parent: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_has_children` is never used
   --> crates/subvol/src/snapshot.rs:296:8
    |
296 | pub fn bch2_snapshot_has_children(c: &bch_fs, id: u32) -> bool {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_live_descendent` is never used
   --> crates/subvol/src/snapshot.rs:303:8
    |
303 | pub fn bch2_snapshot_live_descendent(c: &bch_fs, mut id: u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_is_ancestor_early` is never used
   --> crates/subvol/src/snapshot.rs:339:8
    |
339 | pub fn bch2_snapshot_is_ancestor_early(c: &bch_fs, mut id: u32, ancestor: u32) -> bool {
    |        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bch2_snapshot_tree_next` is never used
   --> crates/subvol/src/snapshot.rs:470:8
    |
470 | pub fn bch2_snapshot_tree_next(c: &bch_fs, id: u32, depth: &mut u32) -> u32 {
    |        ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `bit_spin_wake` is never used
  --> crates/subvol/src/util/bit_spinlock.rs:15:15
   |
15 | pub unsafe fn bit_spin_wake(_nr: usize, _addr: *const AtomicUsize) {}
   |               ^^^^^^^^^^^^^

warning: function `eytzinger1_last` is never used
  --> crates/subvol/src/util/eytzinger.rs:26:14
   |
26 | pub const fn eytzinger1_last(size: u32) -> u32 {
   |              ^^^^^^^^^^^^^^^

warning: function `eytzinger1_to_inorder` is never used
  --> crates/subvol/src/util/eytzinger.rs:93:14
   |
93 | pub const fn eytzinger1_to_inorder(i: u32, size: u32) -> u32 {
   |              ^^^^^^^^^^^^^^^^^^^^^

warning: function `inorder_to_eytzinger1` is never used
  --> crates/subvol/src/util/eytzinger.rs:97:14
   |
97 | pub const fn inorder_to_eytzinger1(i: u32, size: u32) -> u32 {
   |              ^^^^^^^^^^^^^^^^^^^^^

warning: function `jhash_size` is never used
 --> crates/subvol/src/util/jhash.rs:3:14
  |
3 | pub const fn jhash_size(n: u32) -> u32 {
  |              ^^^^^^^^^^

warning: function `jhash_mask` is never used
 --> crates/subvol/src/util/jhash.rs:7:14
  |
7 | pub const fn jhash_mask(n: u32) -> u32 {
  |              ^^^^^^^^^^

warning: function `jhash_3words` is never used
   --> crates/subvol/src/util/jhash.rs:146:8
    |
146 | pub fn jhash_3words(a: u32, b: u32, c: u32, initval: u32) -> u32 {
    |        ^^^^^^^^^^^^

warning: function `jhash_2words` is never used
   --> crates/subvol/src/util/jhash.rs:155:8
    |
155 | pub fn jhash_2words(a: u32, b: u32, initval: u32) -> u32 {
    |        ^^^^^^^^^^^^

warning: function `jhash_1word` is never used
   --> crates/subvol/src/util/jhash.rs:164:8
    |
164 | pub fn jhash_1word(a: u32, initval: u32) -> u32 {
    |        ^^^^^^^^^^^

warning: function `init_from_env` is never used
  --> crates/subvol/src/util/log.rs:43:8
   |
43 | pub fn init_from_env() {
   |        ^^^^^^^^^^^^^

warning: function `rcu_head_after_call_rcu` is never used
  --> crates/subvol/src/util/rcu.rs:93:15
   |
93 | pub unsafe fn rcu_head_after_call_rcu(head: *const rcu_head, func: rcu_callback_t) -> bool {
   |               ^^^^^^^^^^^^^^^^^^^^^^^

warning: function `rcu_assign_pointer` is never used
   --> crates/subvol/src/util/rcu.rs:103:15
    |
103 | pub unsafe fn rcu_assign_pointer<T>(dst: *mut *mut T, value: *mut T) {
    |               ^^^^^^^^^^^^^^^^^^

warning: function `rcu_dereference` is never used
   --> crates/subvol/src/util/rcu.rs:108:15
    |
108 | pub unsafe fn rcu_dereference<T>(src: *const *mut T) -> *mut T {
    |               ^^^^^^^^^^^^^^^

warning: function `rhashtable_insert_fast` is never used
   --> crates/subvol/src/util/rhashtable.rs:375:15
    |
375 | pub unsafe fn rhashtable_insert_fast(ht: *mut rhashtable, obj: *mut rhash_head) -> i32 {
    |               ^^^^^^^^^^^^^^^^^^^^^^

warning: function `work_pending` is never used
   --> crates/subvol/src/util/workqueue.rs:103:15
    |
103 | pub unsafe fn work_pending(work: *const work_struct) -> bool {
    |               ^^^^^^^^^^^^

warning: function `alloc_workqueue` is never used
   --> crates/subvol/src/util/workqueue.rs:107:8
    |
107 | pub fn alloc_workqueue(name: &str) -> *mut workqueue_struct {
    |        ^^^^^^^^^^^^^^^

warning: function `flush_work` is never used
   --> crates/subvol/src/util/workqueue.rs:123:15
    |
123 | pub unsafe fn flush_work(work: *mut work_struct) -> bool {
    |               ^^^^^^^^^^

warning: function `destroy_workqueue` is never used
   --> crates/subvol/src/util/workqueue.rs:174:15
    |
174 | pub unsafe fn destroy_workqueue(wq: *mut workqueue_struct) {
    |               ^^^^^^^^^^^^^^^^^

warning: function `drain_workqueue` is never used
   --> crates/subvol/src/util/workqueue.rs:188:15
    |
188 | pub unsafe fn drain_workqueue(wq: *mut workqueue_struct) {
    |               ^^^^^^^^^^^^^^^

warning: `subvol` (lib) generated 420 warnings
warning: constant `CASES` is never used
  --> crates/subvol/tests/btree_proptest.rs:23:7
   |
23 | const CASES: u32 = 64;
   |       ^^^^^
   |
   = note: `#[warn(dead_code)]` (part of `#[warn(unused)]`) on by default

warning: `subvol` (test "btree_proptest") generated 1 warning
warning: `subvol` (lib test) generated 141 warnings (141 duplicates)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.07s
     Running unittests src/lib.rs (target/debug/deps/subvol-17c17c3b67a4a255)
     Running tests/btree_proptest.rs (target/debug/deps/btree_proptest-bfb308438dcdd790)
   Doc-tests subvol
- fmt：cargo fmt --check -p subvol 通过
