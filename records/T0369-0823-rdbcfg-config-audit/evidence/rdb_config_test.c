#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <errno.h>

#include "../rdb-config.h"

#undef NDEBUG
#include <assert.h>

static int tests_passed = 0;
static int tests_failed = 0;

#define TEST(name) void test_##name(void)
#define RUN_TEST(name)                           \
	do {                                     \
		printf("Running %s... ", #name); \
		test_##name();                   \
		printf("PASSED\n");              \
		tests_passed++;                  \
	} while (0)

static char *write_temp_ini(const char *content)
{
	char template[] = "/tmp/rdb_config_test_XXXXXX";
	int fd = mkstemp(template);
	assert(fd >= 0);
	ssize_t len = write(fd, content, strlen(content));
	assert(len == (ssize_t)strlen(content));
	close(fd);
	return strdup(template);
}

static void cleanup_temp(const char *path)
{
	if (path) {
		unlink(path);
		free((void *)path);
	}
}

TEST(parse_and_get_int)
{
	const char *ini =
		"[section1]\n"
		"int_val = 42\n"
		"neg_val = -7\n"
		"zero_val = 0\n";
	char *path = write_temp_ini(ini);
	char err[256];

	int ret = parse_config(path, err, sizeof(err));
	assert(ret == 0);

	config_kv_store *store = get_config_store();
	assert(store != NULL);

	assert(config_get_int(store, "section1", "int_val", 99) == 42);
	assert(config_get_int(store, "section1", "neg_val", 99) == -7);
	assert(config_get_int(store, "section1", "zero_val", 99) == 0);

	cleanup_temp(path);
}

TEST(config_get_int_default)
{
	const char *ini = "[s]\n" "x = 10\n";
	char *path = write_temp_ini(ini);
	char err[256];

	parse_config(path, err, sizeof(err));
	config_kv_store *store = get_config_store();

	assert(config_get_int(store, "s", "nonexist", 88) == 88);
	assert(config_get_int(store, "nonexist_section", "x", 77) == 77);

	cleanup_temp(path);
}

TEST(config_get_string)
{
	const char *ini =
		"[cfg]\n"
		"name = hello\n"
		"path = /opt/aio/cfg\n"
		"empty_val = \n";
	char *path = write_temp_ini(ini);
	char err[256];

	parse_config(path, err, sizeof(err));
	config_kv_store *store = get_config_store();

	const char *v = config_get_string(store, "cfg", "name");
	assert(v != NULL);
	assert(strcmp(v, "hello") == 0);

	v = config_get_string(store, "cfg", "path");
	assert(v != NULL);
	assert(strcmp(v, "/opt/aio/cfg") == 0);

	v = config_get_string(store, "cfg", "empty_val");
	assert(v != NULL);
	assert(v[0] == '\0');

	cleanup_temp(path);
}

TEST(config_get_string_null_for_missing)
{
	const char *ini = "[s]\n" "k = v\n";
	char *path = write_temp_ini(ini);
	char err[256];

	parse_config(path, err, sizeof(err));
	config_kv_store *store = get_config_store();

	assert(config_get_string(store, "s", "nonexist") == NULL);
	assert(config_get_string(store, "nosection", "k") == NULL);

	cleanup_temp(path);
}

TEST(config_get_string_global_fallback)
{
	const char *ini =
		"global_key = global_val\n"
		"\n"
		"[sec]\n"
		"sec_key = sec_val\n";
	char *path = write_temp_ini(ini);
	char err[256];

	/* T0369 F4：回退默认关闭；显式开启后才会命中顶部无 section 键 */
	config_set_global_fallback(1);
	parse_config(path, err, sizeof(err));
	config_kv_store *store = get_config_store();

	const char *v = config_get_string(store, "sec", "global_key");
	assert(v != NULL);
	assert(strcmp(v, "global_val") == 0);

	v = config_get_string(store, "sec", "sec_key");
	assert(v != NULL);
	assert(strcmp(v, "sec_val") == 0);

	config_set_global_fallback(0);
	cleanup_temp(path);
}

TEST(config_get_string_no_global_fallback_by_default)
{
	const char *ini =
		"global_key = global_val\n"
		"\n"
		"[sec]\n"
		"sec_key = sec_val\n";
	char *path = write_temp_ini(ini);
	char err[256];

	/* T0369 F4：默认关闭隐式回退，严栺对齐文档 4 层模型 */
	parse_config(path, err, sizeof(err));
	config_kv_store *store = get_config_store();

	const char *v = config_get_string(store, "sec", "global_key");
	assert(v == NULL);

	v = config_get_string(store, "sec", "sec_key");
	assert(v != NULL);
	assert(strcmp(v, "sec_val") == 0);

	cleanup_temp(path);
}

TEST(config_get_int_invalid_falls_back)
{
	const char *ini = "[s]\n" "val = not_a_number\n";
	char *path = write_temp_ini(ini);
	char err[256];

	/* T0369 F5：脏值不再静默当作 0，回退 default_val */
	parse_config(path, err, sizeof(err));
	config_kv_store *store = get_config_store();

	assert(config_get_int(store, "s", "val", 7) == 7);

	cleanup_temp(path);
}

TEST(parse_config_over_max_not_truncated_silently)
{
	/* T0369 F2：超过 CONFIG_KV_MAX 不应导致 inih 停止解析（return 0），
	 * 解析整体仍成功返回 0。 */
	char buf[32768];
	int n = 0;
	n += snprintf(buf + n, sizeof(buf) - n, "[sec]\n");
	for (int i = 0; i < CONFIG_KV_MAX + 200; i++) {
		n += snprintf(buf + n, sizeof(buf) - n, "k%d = v%d\n", i, i);
	}
	char *path = write_temp_ini(buf);
	char err[256];

	int ret = parse_config(path, err, sizeof(err));
	assert(ret == 0);

	cleanup_temp(path);
}

TEST(config_set_string)
{
	const char *ini = "[s]\n" "k = old\n";
	char *path = write_temp_ini(ini);
	char err[256];

	parse_config(path, err, sizeof(err));
	config_kv_store *store = get_config_store();

	int ret = config_set_string(store, "s", "k", "new_val");
	assert(ret == 0);

	const char *v = config_get_string(store, "s", "k");
	assert(v != NULL);
	assert(strcmp(v, "new_val") == 0);

	ret = config_set_string(store, "s", "new_key", "created");
	assert(ret == 0);

	v = config_get_string(store, "s", "new_key");
	assert(v != NULL);
	assert(strcmp(v, "created") == 0);

	cleanup_temp(path);
}

TEST(config_section_count_and_entry)
{
	const char *ini =
		"[empty]\n"
		"[abc]\n"
		"a = 1\n"
		"b = 2\n"
		"[xyz]\n"
		"c = 3\n"
		"d = 4\n"
		"e = 5\n";
	char *path = write_temp_ini(ini);
	char err[256];

	parse_config(path, err, sizeof(err));
	config_kv_store *store = get_config_store();

	assert(config_section_count(store, "empty") == 0);

	assert(config_section_count(store, "abc") == 2);
	config_kv_entry *e = config_section_entry(store, "abc", 0);
	assert(e != NULL);
	assert(strcmp(e->key, "a") == 0);
	assert(strcmp(e->value, "1") == 0);
	e = config_section_entry(store, "abc", 1);
	assert(e != NULL);
	assert(strcmp(e->key, "b") == 0);

	assert(config_section_count(store, "xyz") == 3);
	assert(config_section_entry(store, "xyz", 5) == NULL);

	assert(config_section_entry(store, "nosection", 0) == NULL);

	cleanup_temp(path);
}

TEST(parse_nonexistent_file)
{
	char err[256];
	int ret = parse_config("/tmp/rdb_config_test_nonexist_XXXX", err,
			       sizeof(err));
	assert(ret < 0);
}

TEST(init_config_from_env)
{
	const char *ini = "[mysec]\n" "val = 99\n";
	char *path = write_temp_ini(ini);
	char err[256];

	setenv(RDB_CONFIG, path, 1);

	int ret = init_config(NULL, err, sizeof(err));
	assert(ret == 0);

	config_kv_store *store = get_config_store();
	assert(store != NULL);
	assert(config_get_int(store, "mysec", "val", 0) == 99);

	unsetenv(RDB_CONFIG);
	cleanup_temp(path);
}

TEST(parse_config_twice)
{
	const char *ini1 = "[s]\n" "k = first\n";
	const char *ini2 = "[s]\n" "k = second\n";
	char *path1 = write_temp_ini(ini1);
	char *path2 = write_temp_ini(ini2);
	char err[256];

	parse_config(path1, err, sizeof(err));
	config_kv_store *store = get_config_store();
	const char *v = config_get_string(store, "s", "k");
	assert(v != NULL);
	assert(strcmp(v, "first") == 0);

	parse_config(path2, err, sizeof(err));
	store = get_config_store();
	v = config_get_string(store, "s", "k");
	assert(v != NULL);
	assert(strcmp(v, "second") == 0);

	cleanup_temp(path1);
	cleanup_temp(path2);
}

TEST(config_get_int_trailing_spaces)
{
	const char *ini = "[s]\n" "val =  42  \n";
	char *path = write_temp_ini(ini);
	char err[256];

	parse_config(path, err, sizeof(err));
	config_kv_store *store = get_config_store();

	assert(config_get_int(store, "s", "val", 0) == 42);

	cleanup_temp(path);
}

TEST(tool_tls_config_isolated_and_prioritized)
{
	const char *ini =
		"[security]\n"
		"tls_enable = 1\n"
		"ciphersuites = TLS_SM4_GCM_SM3\n"
		"[rdbcomm]\n"
		"mtls_enable = 1\n"
		"tls_algorithm = TLS_AES_256_GCM_SHA384\n"
		"[aio-speed]\n"
		"mtls_enable = 0\n"
		"tls_algorithm = TLS_SM4_GCM_SM3\n";
	char *path = write_temp_ini(ini);
	char err[256];

	unsetenv("RPC_TLS_ENABLE");
	unsetenv("RPC_TLS_CIPHERSUITES");
	unsetenv(RDBCOMM_MTLS_ENABLE_ENV);
	unsetenv(RDBCOMM_TLS_ALGORITHM_ENV);
	unsetenv(AIO_SPEED_MTLS_ENABLE_ENV);
	unsetenv(AIO_SPEED_TLS_ALGORITHM_ENV);
	assert(parse_config(path, err, sizeof(err)) == 0);

	assert(sec_resolve_int(RDBCOMM_TOOL_SECTION, SEC_TOOL_MTLS_KEY, SEC_GLOBAL_SECTION,
			 SEC_GLOBAL_TLS_KEY, RDBCOMM_MTLS_ENABLE_ENV, 0) == 1);
	assert(strcmp(sec_resolve_str(RDBCOMM_TOOL_SECTION,
				 SEC_TOOL_ALGORITHM_KEY,
				 SEC_GLOBAL_SECTION,
				 SEC_GLOBAL_CIPHERSUITES_KEY,
				 RDBCOMM_TLS_ALGORITHM_ENV,
				 RPC_TLS_ALGORITHM_DEFAULT),
		       RPC_TLS_ALGORITHM_AES_256_GCM_SHA384) == 0);
	assert(sec_resolve_int(AIO_SPEED_TOOL_SECTION, SEC_TOOL_MTLS_KEY, SEC_GLOBAL_SECTION,
			 SEC_GLOBAL_TLS_KEY, AIO_SPEED_MTLS_ENABLE_ENV, 0) == 0);
	assert(strcmp(sec_resolve_str(AIO_SPEED_TOOL_SECTION,
				 SEC_TOOL_ALGORITHM_KEY,
				 SEC_GLOBAL_SECTION,
				 SEC_GLOBAL_CIPHERSUITES_KEY,
				 AIO_SPEED_TLS_ALGORITHM_ENV,
				 RPC_TLS_ALGORITHM_DEFAULT),
		       RPC_TLS_ALGORITHM_SM4_GCM_SM3) == 0);

	setenv(RDBCOMM_MTLS_ENABLE_ENV, "0", 1);
	setenv(RDBCOMM_TLS_ALGORITHM_ENV, RPC_TLS_ALGORITHM_SM4_GCM_SM3, 1);
	assert(sec_resolve_int(RDBCOMM_TOOL_SECTION, SEC_TOOL_MTLS_KEY, SEC_GLOBAL_SECTION,
			 SEC_GLOBAL_TLS_KEY, RDBCOMM_MTLS_ENABLE_ENV, 0) == 0);
	assert(strcmp(sec_resolve_str(RDBCOMM_TOOL_SECTION,
				 SEC_TOOL_ALGORITHM_KEY,
				 SEC_GLOBAL_SECTION,
				 SEC_GLOBAL_CIPHERSUITES_KEY,
				 RDBCOMM_TLS_ALGORITHM_ENV,
				 RPC_TLS_ALGORITHM_DEFAULT),
		       RPC_TLS_ALGORITHM_SM4_GCM_SM3) == 0);

	/* env 优先于 config section（无 CLI 覆盖状态） */
	setenv(RDBCOMM_MTLS_ENABLE_ENV, "1", 1);
	setenv(RDBCOMM_TLS_ALGORITHM_ENV, RPC_TLS_ALGORITHM_AES_256_GCM_SHA384, 1);
	assert(sec_resolve_int(RDBCOMM_TOOL_SECTION, SEC_TOOL_MTLS_KEY, SEC_GLOBAL_SECTION,
			 SEC_GLOBAL_TLS_KEY, RDBCOMM_MTLS_ENABLE_ENV, 0) == 1);
	assert(strcmp(sec_resolve_str(RDBCOMM_TOOL_SECTION,
				 SEC_TOOL_ALGORITHM_KEY,
				 SEC_GLOBAL_SECTION,
				 SEC_GLOBAL_CIPHERSUITES_KEY,
				 RDBCOMM_TLS_ALGORITHM_ENV,
				 RPC_TLS_ALGORITHM_DEFAULT),
		       RPC_TLS_ALGORITHM_AES_256_GCM_SHA384) == 0);

	unsetenv(RDBCOMM_MTLS_ENABLE_ENV);
	unsetenv(RDBCOMM_TLS_ALGORITHM_ENV);

	/* sec_resolve_str: env > tool section > global > 默认值 */
	assert(strcmp(sec_resolve_str(RDBCOMM_TOOL_SECTION,
				     SEC_TOOL_ALGORITHM_KEY, SEC_GLOBAL_SECTION,
				     SEC_GLOBAL_CIPHERSUITES_KEY,
				     RDBCOMM_TLS_ALGORITHM_ENV, "default-alg"),
		     RPC_TLS_ALGORITHM_AES_256_GCM_SHA384) == 0);
	assert(strcmp(sec_resolve_str(AIO_SPEED_TOOL_SECTION,
				     SEC_TOOL_ALGORITHM_KEY, SEC_GLOBAL_SECTION,
				     SEC_GLOBAL_CIPHERSUITES_KEY,
				     AIO_SPEED_TLS_ALGORITHM_ENV, "default-alg"),
		     RPC_TLS_ALGORITHM_SM4_GCM_SM3) == 0);
	/* env 优先于 tool section */
	setenv(RDBCOMM_TLS_ALGORITHM_ENV, RPC_TLS_ALGORITHM_SM4_GCM_SM3, 1);
	assert(strcmp(sec_resolve_str(RDBCOMM_TOOL_SECTION,
				     SEC_TOOL_ALGORITHM_KEY, SEC_GLOBAL_SECTION,
				     SEC_GLOBAL_CIPHERSUITES_KEY,
				     RDBCOMM_TLS_ALGORITHM_ENV, "default-alg"),
		     RPC_TLS_ALGORITHM_SM4_GCM_SM3) == 0);
	unsetenv(RDBCOMM_TLS_ALGORITHM_ENV);
	/* 全局 fallback: 工具 section/key 未命中时回退全局 ciphersuites */
	assert(strcmp(sec_resolve_str(NULL, NULL, SEC_GLOBAL_SECTION,
				     SEC_GLOBAL_CIPHERSUITES_KEY, NULL,
				     "default-alg"),
		     RPC_TLS_ALGORITHM_SM4_GCM_SM3) == 0);
	/* 默认值: 全部未命中返回 default */
	assert(strcmp(sec_resolve_str("nonexistent-section", "no-such-key",
				     "nonexistent-global", "no-such-key", NULL,
				     "default-alg"),
		     "default-alg") == 0);

	cleanup_temp(path);
}


/* T0361 AC-2：sec_resolve_bool 严格布尔分层解析 */
TEST(sec_resolve_bool_layers)
{
	const char *ini =
		"[security]\n"
		"tls_enable = 1\n"
		"[rdbcomm]\n"
		"mtls_enable = 0\n";
	char *path = write_temp_ini(ini);
	char err[256];

	unsetenv(RDBCOMM_MTLS_ENABLE_ENV);
	assert(parse_config(path, err, sizeof(err)) == 0);

	/* ini 工具段生效 */
	assert(sec_resolve_bool(RDBCOMM_TOOL_SECTION, SEC_TOOL_MTLS_KEY,
				SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
				RDBCOMM_MTLS_ENABLE_ENV, 0) == 0);
	/* ini 全局段回退（工具段无配置的键） */
	assert(sec_resolve_bool("nonexistent-sec", "no-key",
				SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
				NULL, 0) == 1);
	/* env 覆盖 ini */
	setenv(RDBCOMM_MTLS_ENABLE_ENV, "1", 1);
	assert(sec_resolve_bool(RDBCOMM_TOOL_SECTION, SEC_TOOL_MTLS_KEY,
				SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
				RDBCOMM_MTLS_ENABLE_ENV, 0) == 1);
	/* env 非法 -> -1 错误哨兵（fail-closed） */
	setenv(RDBCOMM_MTLS_ENABLE_ENV, "abc", 1);
	assert(sec_resolve_bool(RDBCOMM_TOOL_SECTION, SEC_TOOL_MTLS_KEY,
				SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
				RDBCOMM_MTLS_ENABLE_ENV, 0) == -1);
	setenv(RDBCOMM_MTLS_ENABLE_ENV, "1x", 1);
	assert(sec_resolve_bool(RDBCOMM_TOOL_SECTION, SEC_TOOL_MTLS_KEY,
				SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
				RDBCOMM_MTLS_ENABLE_ENV, 0) == -1);
	/* 空串 env 与 sec_resolve_int/str 家族约定一致：视为未命中，
	 * 继续回落下层（此处回落 ini 工具段 mtls_enable=0） */
	setenv(RDBCOMM_MTLS_ENABLE_ENV, "", 1);
	assert(sec_resolve_bool(RDBCOMM_TOOL_SECTION, SEC_TOOL_MTLS_KEY,
				SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
				RDBCOMM_MTLS_ENABLE_ENV, 0) == 0);
	unsetenv(RDBCOMM_MTLS_ENABLE_ENV);
	/* ini 非法 -> -1 */
	{
		const char *bad_ini =
			"[security]\n"
			"tls_enable = yes\n";
		char *bpath = write_temp_ini(bad_ini);
		assert(parse_config(bpath, err, sizeof(err)) == 0);
		assert(sec_resolve_bool("nonexistent-sec", "no-key",
					SEC_GLOBAL_SECTION, SEC_GLOBAL_TLS_KEY,
					NULL, 0) == -1);
		cleanup_temp(bpath);
	}
	/* 全部未命中 -> 默认值；空串 env 视为未设置由实现裁决（此处要求 -1） */
	assert(sec_resolve_bool("nonexistent-sec", "no-key",
				"nonexistent-global", "no-key",
				NULL, 1) == 1);

	cleanup_temp(path);
}

int main(void)
{
	printf("=== rdb-config test ===\n\n");

	RUN_TEST(parse_and_get_int);
	RUN_TEST(config_get_int_default);
	RUN_TEST(config_get_string);
	RUN_TEST(config_get_string_null_for_missing);
	RUN_TEST(config_get_string_global_fallback);
	RUN_TEST(config_set_string);
	RUN_TEST(config_section_count_and_entry);
	RUN_TEST(parse_nonexistent_file);
	RUN_TEST(init_config_from_env);
	RUN_TEST(parse_config_twice);
	RUN_TEST(config_get_int_trailing_spaces);
	RUN_TEST(tool_tls_config_isolated_and_prioritized);
	RUN_TEST(sec_resolve_bool_layers);
	RUN_TEST(config_get_string_no_global_fallback_by_default);
	RUN_TEST(config_get_int_invalid_falls_back);
	RUN_TEST(parse_config_over_max_not_truncated_silently);

	printf("\n=== %d passed, %d failed ===\n", tests_passed,
	       tests_failed);
	return tests_failed > 0 ? 1 : 0;
}
