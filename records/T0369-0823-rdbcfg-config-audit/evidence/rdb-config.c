#include "rdb-config.h"
#include "common.h"

#include <errno.h>
#include <ini.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

static config_kv_store _kv_stores[2];
static int config_index = 0;
static pthread_mutex_t g_cfg_lock = PTHREAD_MUTEX_INITIALIZER;

/* T0369 F4：是否允许 config_get_string 在指定 section 未命中时回退到文件顶部
 * 无 section 键。默认关闭，使行为严格对齐文档 4 层模型（避免顶部键泄漏到任意
 * 工具段查询）。确有需要的调用方可通过 config_set_global_fallback(1) 开启。 */
static int g_allow_global_fallback = 0;

/* T0369 F2：CONFIG_KV_MAX 达上限时曾 return 0 导致 inih 停止解析、后续配置静默
 * 截断。现改为继续解析（return 1）并告警一次。 */
static int g_truncated_warned = 0;

void config_set_global_fallback(int on)
{
	g_allow_global_fallback = on ? 1 : 0;
}

static int do_parse_config(void *user, const char *section, const char *name,
			   const char *value)
{
	config_kv_store *store = (config_kv_store *)user;

	if (store->count >= CONFIG_KV_MAX) {
		if (!g_truncated_warned) {
			fprintf(stderr,
				"rdb-config: CONFIG_KV_MAX(%d) reached, config "
				"may be truncated; consider trimming rdb.conf\n",
				CONFIG_KV_MAX);
			g_truncated_warned = 1;
		}
		return 1;
	}

	config_kv_entry *entry = &store->entries[store->count++];
	snprintf(entry->section, sizeof(entry->section), "%s",
		 section ? section : "");
	snprintf(entry->key, sizeof(entry->key), "%s", name ? name : "");
	snprintf(entry->value, sizeof(entry->value), "%s", value ? value : "");
	return 1;
}

/* T0369 F5：严格整数解析，仅接受可选符号 + 十进制数字，空串/脏值返回 -1。
 * 容忍首尾空白（与历史 atoi 行为兼容），但中间含非数字字符视为非法。 */
static int parse_strict_int(const char *s, long *out)
{
	char *end = NULL;
	long v;

	if (s == NULL || s[0] == '\0')
		return -1;
	v = strtol(s, &end, 10);
	if (end == s || end == NULL)
		return -1;
	while (*end == ' ' || *end == '\t')
		end++;
	if (*end != '\0')
		return -1;
	*out = v;
	return 0;
}

const char *config_get_string(config_kv_store *store, const char *section,
			      const char *key)
{
	if (store == NULL || section == NULL || key == NULL) {
		return NULL;
	}

	/* 精确 section 匹配 */
	for (int i = store->count - 1; i >= 0; i--) {
		if (strcmp(store->entries[i].section, section) == 0 &&
		    strcmp(store->entries[i].key, key) == 0) {
			return store->entries[i].value;
		}
	}

	/* 回退到全局 section（文件顶部的无 section 键值）。T0369 F4：默认关闭，
	 * 仅当调用方显式开启 g_allow_global_fallback 时生效。 */
	if (section[0] != '\0' && g_allow_global_fallback) {
		for (int i = store->count - 1; i >= 0; i--) {
			if (store->entries[i].section[0] == '\0' &&
			    strcmp(store->entries[i].key, key) == 0) {
				return store->entries[i].value;
			}
		}
	}

	return NULL;
}

int config_get_int(config_kv_store *store, const char *section, const char *key,
		   int default_val)
{
	const char *value = config_get_string(store, section, key);
	long v;

	if (value == NULL) {
		return default_val;
	}
	/* T0369 F5：脏值/空串不再静默当作 0，而是回退 default_val 并告警 */
	if (parse_strict_int(value, &v) != 0) {
		fprintf(stderr,
			"rdb-config: invalid integer for [%s]%s=%s, fallback to %d\n",
			section ? section : "", key ? key : "", value, default_val);
		return default_val;
	}
	return (int)v;
}

int config_get_int_env(config_kv_store *store, const char *section,
		       const char *key, const char *env_name, int default_val)
{
	/* 环境变量优先（T0369 F5：空串视为未设置，回退配置文件） */
	if (env_name != NULL) {
		const char *env_val = getenv(env_name);
		long v;
		if (env_val != NULL && env_val[0] != '\0' &&
		    parse_strict_int(env_val, &v) == 0) {
			return (int)v;
		}
	}

	/* 回退到配置文件 */
	return config_get_int(store, section, key, default_val);
}

int config_set_string(config_kv_store *store, const char *section,
		      const char *key, const char *value)
{
	if (store == NULL || section == NULL || key == NULL || value == NULL) {
		return -1;
	}

	for (int i = 0; i < store->count; i++) {
		if (strcmp(store->entries[i].section, section) == 0 &&
		    strcmp(store->entries[i].key, key) == 0) {
			snprintf(store->entries[i].value,
				 sizeof(store->entries[i].value), "%s", value);
			return 0;
		}
	}

	if (store->count >= CONFIG_KV_MAX) {
		return -1;
	}
	config_kv_entry *entry = &store->entries[store->count++];
	snprintf(entry->section, sizeof(entry->section), "%s", section);
	snprintf(entry->key, sizeof(entry->key), "%s", key);
	snprintf(entry->value, sizeof(entry->value), "%s", value);
	return 0;
}

config_kv_store *get_config_store(void)
{
	config_kv_store *store;

	/* T0369 F6：读取当前存储指针加锁，避免与 init_config 切换瞬间竞态 */
	pthread_mutex_lock(&g_cfg_lock);
	store = &_kv_stores[config_index];
	pthread_mutex_unlock(&g_cfg_lock);
	return store;
}

int parse_config(const char *config_file, char *err_msg, int len)
{
	int tmp_index = (config_index + 1) % 2;
	config_kv_store *tmp_store = &_kv_stores[tmp_index];

	tmp_store->count = 0;

	if (ini_parse(config_file, do_parse_config, tmp_store) < 0) {
		snprintf(err_msg, len, "Can't load config file: %s",
			 config_file);
		return -1;
	}

	/* T0369 F6：原子切换存储索引加锁 */
	pthread_mutex_lock(&g_cfg_lock);
	config_index = tmp_index;
	pthread_mutex_unlock(&g_cfg_lock);
	return 0;
}

int show_config(config_kv_store *store, const char *section, char *buf, int len)
{
	int offset = 0;

	offset += snprintf(buf + offset, len - offset, "[%s]\n", section);
	for (int i = 0; i < store->count; i++) {
		if (strcmp(store->entries[i].section, section) != 0) {
			continue;
		}
		offset += snprintf(buf + offset, len - offset, "%s=%s\n",
				   store->entries[i].key,
				   store->entries[i].value);
	}
	return offset;
}

int config_section_count(config_kv_store *store, const char *section)
{
	int count = 0;

	for (int i = 0; i < store->count; i++) {
		if (strcmp(store->entries[i].section, section) == 0) {
			count++;
		}
	}
	return count;
}

config_kv_entry *config_section_entry(config_kv_store *store,
				      const char *section, int index)
{
	for (int i = 0; i < store->count; i++) {
		if (strcmp(store->entries[i].section, section) == 0) {
			if (index == 0) {
				return &store->entries[i];
			}
			index--;
		}
	}
	return NULL;
}

int init_config(const char *config_file, char *err_msg, int len)
{
	const char *config_path = config_file;

	if (config_path == NULL) {
		config_path = getenv(RDB_CONFIG);
	}
	if (config_path == NULL) {
		config_path = DEFAULT_RDB_CONFIG_PATH;
	}

	if (parse_config(config_path, err_msg, len) < 0) {
		if (errno == ENOENT) {
			return 0;
		}
		return -1;
	}

	return 0;
}

int sec_resolve_int(const char *tool_section, const char *tool_key,
		    const char *global_section, const char *global_key,
		    const char *env_name, int default_val)
{
	/* 第1层：env */
	if (env_name != NULL) {
		const char *env_val = getenv(env_name);
		if (env_val != NULL && env_val[0] != '\0')
			return atoi(env_val);
	}

	/* 第2层：工具 section 的独立配置 */
	if (tool_section != NULL && tool_key != NULL) {
		int val = config_get_int(get_config_store(), tool_section,
					 tool_key, -1);
		if (val >= 0)
			return val;
	}

	/* 第3层：全局 section 的配置 */
	if (global_section != NULL && global_key != NULL) {
		int val = config_get_int(get_config_store(), global_section,
					 global_key, -1);
		if (val >= 0)
			return val;
	}

	/* 第4层：默认值 */
	return default_val;
}

/* T0361：严格布尔解析，仅接受全串十进制 "0"/"1"；空串/NULL 视为未设置返回 0 */
static int sec_parse_strict_bool(const char *s, int *out)
{
	char *end = NULL;
	long value;

	if (s == NULL || s[0] == '\0')
		return 0;
	value = strtol(s, &end, 10);
	if (end == NULL || *end != '\0' || (value != 0 && value != 1))
		return -1;
	*out = (int)value;
	return 0;
}

int sec_resolve_bool(const char *tool_section, const char *tool_key,
		     const char *global_section, const char *global_key,
		     const char *env_name, int default_val)
{
	int val = 0;

	/* 第1层：env（非法值 fail-closed 返回 -1） */
	if (env_name != NULL) {
		const char *env_val = getenv(env_name);
		if (env_val != NULL && env_val[0] != '\0') {
			if (sec_parse_strict_bool(env_val, &val) != 0)
				return -1;
			return val;
		}
	}

	/* 第2层：工具 section 的独立配置 */
	if (tool_section != NULL && tool_key != NULL) {
		const char *raw = config_get_string(get_config_store(),
						    tool_section, tool_key);
		if (raw != NULL && raw[0] != '\0') {
			if (sec_parse_strict_bool(raw, &val) != 0)
				return -1;
			return val;
		}
	}

	/* 第3层：全局 section 的配置 */
	if (global_section != NULL && global_key != NULL) {
		const char *raw = config_get_string(get_config_store(),
						    global_section,
						    global_key);
		if (raw != NULL && raw[0] != '\0') {
			if (sec_parse_strict_bool(raw, &val) != 0)
				return -1;
			return val;
		}
	}

	/* 第4层：默认值 */
	return default_val;
}

const char *sec_resolve_str(const char *tool_section, const char *tool_key,
			    const char *global_section, const char *global_key,
			    const char *env_name, const char *default_val)
{
	/* 第1层：env */
	if (env_name != NULL) {
		const char *env_val = getenv(env_name);
		if (env_val != NULL && env_val[0] != '\0')
			return env_val;
	}

	/* 第2层：工具 section 的独立配置 */
	if (tool_section != NULL && tool_key != NULL) {
		const char *val = config_get_string(get_config_store(),
						    tool_section, tool_key);
		if (val != NULL && val[0] != '\0')
			return val;
	}

	/* 第3层：全局 section 的配置 */
	if (global_section != NULL && global_key != NULL) {
		const char *val = config_get_string(get_config_store(),
						    global_section,
						    global_key);
		if (val != NULL && val[0] != '\0')
			return val;
	}

	/* 第4层：默认值 */
	return default_val;
}

static int sec_join_path(char *buf, size_t sz, const char *dir,
			 const char *name)
{
	size_t len = strlen(dir);
	int sep = len && dir[len - 1] != '/' ? 1 : 0;
	return snprintf(buf, sz, "%s%s%s", dir, sep ? "/" : "", name) < (int)sz
		       ? 0 : -1;
}

int sec_tls_client_cert_paths(char *cert_buf, size_t cert_sz, char *key_buf,
			      size_t key_sz, const char *ca_cn)
{
	const char *cert = sec_resolve_str(NULL, NULL, SEC_GLOBAL_SECTION,
					   SEC_GLOBAL_CLIENT_CERT_KEY,
					   RPC_TLS_CLIENT_CERT_ENV, "");
	const char *key = sec_resolve_str(NULL, NULL, SEC_GLOBAL_SECTION,
					  SEC_GLOBAL_CLIENT_KEY_KEY,
					  RPC_TLS_CLIENT_KEY_ENV, "");
	const char *file = CERT_FILE_HOST;
	const char *key_file = CERT_FILE_HOST_KEY;

	if (cert && cert[0] && key && key[0]) {
		snprintf(cert_buf, cert_sz, "%s", cert);
		snprintf(key_buf, key_sz, "%s", key);
		return 0;
	}

	const char *cert_dir = sec_resolve_str(NULL, NULL, SEC_GLOBAL_SECTION,
					      SEC_GLOBAL_CERT_DIR_KEY,
					      RPC_TLS_CERT_DIR_ENV,
					      DEFAULT_CERT_DIR);
	if (!ca_cn || !ca_cn[0]) {
		return -1;
	}
	char dir[512];
	if (sec_join_path(dir, sizeof(dir), cert_dir, ca_cn) != 0 ||
	    sec_join_path(cert_buf, cert_sz, dir, file) != 0 ||
	    sec_join_path(key_buf, key_sz, dir, key_file) != 0) {
		return -1;
	}
	return 0;
}

__attribute__((constructor)) static void rdb_auto_init(void)
{
	char err[256];
	init_config(NULL, err, sizeof(err));
}
