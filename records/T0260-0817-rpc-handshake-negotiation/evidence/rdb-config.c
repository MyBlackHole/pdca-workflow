#include "rdb-config.h"

#include <errno.h>
#include <ini.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

static config_kv_store _kv_stores[2];
static int config_index = 0;

static int do_parse_config(void *user, const char *section, const char *name,
			   const char *value)
{
	config_kv_store *store = (config_kv_store *)user;

	if (store->count >= CONFIG_KV_MAX) {
		return 0;
	}

	config_kv_entry *entry = &store->entries[store->count++];
	snprintf(entry->section, sizeof(entry->section), "%s",
		 section ? section : "");
	snprintf(entry->key, sizeof(entry->key), "%s", name ? name : "");
	snprintf(entry->value, sizeof(entry->value), "%s", value ? value : "");
	return 1;
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

	/* 回退到全局 section（文件顶部的无 section 键值） */
	if (section[0] != '\0') {
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
	if (value == NULL) {
		return default_val;
	}
	return atoi(value);
}

int config_get_int_env(config_kv_store *store, const char *section,
		       const char *key, const char *env_name, int default_val)
{
	/* 环境变量优先 */
	if (env_name != NULL) {
		const char *env_val = getenv(env_name);
		if (env_val != NULL) {
			return atoi(env_val);
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
	return &_kv_stores[config_index];
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

	config_index = tmp_index;
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

static int sec_enabled_with_master(const char *sec_key, const char *env_name)
{
	/* 第1层：独立开关（env + 独立配置项） */
	int val = config_get_int_env(get_config_store(), "security", sec_key,
				     env_name, -1);
	if (val >= 0)
		return val;

	/* 第2层：总开关 [auth] enable */
	val = config_get_int(get_config_store(), "auth", "enable", -1);
	if (val >= 0)
		return val;

	/* 第3层：默认关闭 */
	return 0;
}

static int tls_enabled_cache = -1;
static int auth_enabled_cache = -1;
static int audit_enabled_cache = -1;
static const char *ciphersuites_cache = NULL;

void sec_cache_reset(void)
{
	tls_enabled_cache = -1;
	auth_enabled_cache = -1;
	audit_enabled_cache = -1;
	ciphersuites_cache = NULL;
}

int sec_tls_enabled(void)
{
	if (tls_enabled_cache < 0)
		tls_enabled_cache = sec_enabled_with_master("tls_enable",
							    "RPC_TLS_ENABLE");
	return tls_enabled_cache;
}

int sec_auth_enabled(void)
{
	if (auth_enabled_cache < 0)
		auth_enabled_cache = sec_enabled_with_master("auth_enable",
							     "AUTH_ENABLE");
	/* audit 依赖 key：audit 开启时 key 也必须开启 */
	if (!auth_enabled_cache && sec_audit_enabled())
		auth_enabled_cache = 1;
	return auth_enabled_cache;
}

int sec_audit_enabled(void)
{
	if (audit_enabled_cache < 0)
		audit_enabled_cache = sec_enabled_with_master("audit_enable",
							      "AUDIT_ENABLE");
	return audit_enabled_cache;
}

const char *sec_tls_ciphersuites(void)
{
	if (!ciphersuites_cache) {
		/* 环境变量优先，其次配置文件 [security] ciphersuites */
		const char *val = getenv("RPC_TLS_CIPHERSUITES");
		if (val == NULL || val[0] == '\0') {
			val = config_get_string(get_config_store(), "security",
						"ciphersuites");
		}
		if (val != NULL && val[0] != '\0') {
			/* config_get_string 返回 store 内指针，生命周期随 store；
			 * env 指针生命周期为进程级，均可安全缓存 */
			ciphersuites_cache = val;
		}
	}
	return ciphersuites_cache;
}

int sec_tool_tls_enabled(const char *tool_key, int cli_val)
{
	/* 第1层：命令行显式指定 */
	if (cli_val >= 0)
		return cli_val;

	/* 第2层：工具配置键（如 [security] rpc_tls_enable） */
	int val = config_get_int(get_config_store(), "security", tool_key, -1);
	if (val >= 0)
		return val;

	/* 第3层：全局 [security] tls_enable */
	val = config_get_int(get_config_store(), "security", "tls_enable", -1);
	if (val >= 0)
		return val;

	/* 第4层：总开关 [auth] enable */
	val = config_get_int(get_config_store(), "auth", "enable", -1);
	if (val >= 0)
		return val;

	/* 第5层：默认关闭 */
	return 0;
}

const char *sec_tool_tls_ciphersuites(const char *tool_ciphers_key,
				      const char *cli_val)
{
	/* 第1层：命令行显式指定 */
	if (cli_val != NULL && cli_val[0] != '\0')
		return cli_val;

	/* 第2层：工具配置键（如 [security] rpc_tls_ciphersuites） */
	const char *val = config_get_string(get_config_store(), "security",
					    tool_ciphers_key);
	if (val != NULL && val[0] != '\0')
		return val;

	/* 第3层：全局 [security] ciphersuites */
	return sec_tls_ciphersuites();
}

__attribute__((constructor)) static void rdb_auto_init(void)
{
	char err[256];
	init_config(NULL, err, sizeof(err));
}
