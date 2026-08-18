#include "rpc-config.h"

#include <errno.h>
#include <ini.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

static rpc_config _config[2];
static int config_index = 0;
static char g_section_name[64] = "aio-speed";

rpc_config *g_rpc_config = &_config[config_index];

void rpc_set_section_name(const char *section_name)
{
	if (section_name != NULL) {
		snprintf(g_section_name, sizeof(g_section_name), "%s",
			 section_name);
	}
}

const char *rpc_get_section_name(void)
{
	return g_section_name;
}

static int do_parse_config(void *user, const char *section, const char *name,
			   const char *value)
{
	rpc_config *p_config = (rpc_config *)user;

#define MATCH(s, n) strcmp(section, s) == 0 && strcmp(name, n) == 0

	if (MATCH(g_section_name, "debug")) {
		p_config->debug = atoi(value);
	} else if (MATCH(g_section_name, "retry")) {
		p_config->retry = atoi(value);
	} else if (MATCH(g_section_name, "check_data")) {
		p_config->check_data = atoi(value);
	} else if (MATCH(g_section_name, "keepalive")) {
		p_config->keepalive = atoi(value);
	} else if (MATCH(g_section_name, "parallel")) {
		p_config->parallel = atoi(value);
	} else if (MATCH(g_section_name, "read_timeout")) {
		p_config->read_timeout = atoi(value);
	} else if (MATCH(g_section_name, "fsbackup_dev_path")) {
		snprintf(p_config->dev_path, sizeof(p_config->dev_path), "%s",
			 value);
	} else {
		return 0;
	}
	return 1;
}

int rpc_check_config(rpc_config *p_config, char *err_msg, int len)
{
	if (p_config->debug != 0 && p_config->debug != 1) {
		snprintf(err_msg, len, "Invalid debug value: %d",
			 p_config->debug);
		return -1;
	}
	if (p_config->retry <= 0) {
		snprintf(err_msg, len, "retry should be greater than 0");
		return -1;
	}
	if (p_config->check_data != 0 && p_config->check_data != 1) {
		snprintf(err_msg, len, "check_data should be 0 or 1");
		return -1;
	}
	if (p_config->keepalive < 0) {
		snprintf(err_msg, len, "Invalid keepalive value: %d",
			 p_config->keepalive);
		return -1;
	}
	if (p_config->parallel < 1) {
		snprintf(err_msg, len, "Invalid parallel value: %d",
			 p_config->parallel);
		return -1;
	}
	return 0;
}

int rpc_parse_config(const char *config_file, char *err_msg, int len)
{
	int tmp_index = (config_index + 1) % 2;
	rpc_config *p_config = &_config[tmp_index];

	*p_config = *g_rpc_config;

	if (ini_parse(config_file, do_parse_config, p_config) < 0) {
		snprintf(err_msg, len, "Can't load config file: %s",
			 config_file);
		return -1;
	}

	if (rpc_check_config(p_config, err_msg, len) < 0) {
		return -1;
	}
	config_index = tmp_index;
	g_rpc_config = p_config;
	return 0;
}

int rpc_show_config(rpc_config *p_config, char *buf, int len)
{
	int offset = 0;
	offset +=
		snprintf(buf + offset, len - offset, "[%s]\n", g_section_name);
	offset += snprintf(buf + offset, len - offset, "check_data=%d\n",
			   p_config->check_data);
	offset += snprintf(buf + offset, len - offset, "keepalive=%d\n",
			   p_config->keepalive);
	offset += snprintf(buf + offset, len - offset, "parallel=%d\n",
			   p_config->parallel);
	offset += snprintf(buf + offset, len - offset, "read_timeout=%d\n",
			   p_config->read_timeout);
	offset += snprintf(buf + offset, len - offset, "retry=%d\n",
			   p_config->retry);
	offset += snprintf(buf + offset, len - offset, "debug=%d\n",
			   p_config->debug);
	offset += snprintf(buf + offset, len - offset, "id_file=%s\n",
			   p_config->id_file);
	offset += snprintf(buf + offset, len - offset, "log_path=%s\n",
			   p_config->log_path);
	return offset;
}

int rpc_init_config(const char *config_file, char *err_msg, int len)
{
	const char *config_path = config_file != NULL ? config_file :
							DEFAULT_RDB_CONFIG_PATH;
	g_rpc_config->debug = 0;
	g_rpc_config->daemon = 0;
	g_rpc_config->check_data = 0;
	g_rpc_config->keepalive = DEFAULT_KEEPALIVE_INTERVAL;
	g_rpc_config->rpc_port = DEFAULT_RPC_PORT;
	g_rpc_config->retry = DEFAULT_RETRY;
	g_rpc_config->parallel = 4;
	g_rpc_config->read_timeout = 120000;
	g_rpc_config->tls_enable_cli = -1;
	g_rpc_config->tls_ciphersuites_cli[0] = '\0';

	snprintf(g_rpc_config->id_file, sizeof(g_rpc_config->id_file), "%s",
		 UNION_ID_FILE_PATH);

	snprintf(g_rpc_config->dev_path, sizeof(g_rpc_config->dev_path), "%s",
		 DEFAULT_DEV_PATH);

	snprintf(g_rpc_config->log_path, sizeof(g_rpc_config->log_path), "%s",
		 DEFAULT_LOG_DIR);

	snprintf(g_rpc_config->audit_path, sizeof(g_rpc_config->audit_path),
		 "%s", DEFAULT_AUDIT_DIR);

	snprintf(g_rpc_config->work_dir, sizeof(g_rpc_config->work_dir), "%s",
		 DEFAULT_WORK_DIR);

	snprintf(g_rpc_config->config_path, sizeof(g_rpc_config->config_path),
		 "%s", DEFAULT_RDB_CONFIG_PATH);

	if (rpc_parse_config(config_path, err_msg, len) < 0) {
		if (errno == ENOENT) {
			return 0;
		}
		return -1;
	}

	return 0;
}

void rpc_tls_config_set(int cli_enable, const char *cli_ciphersuites)
{
	/* 仅更新显式传入的参数，避免命令行多次调用相互覆盖 */
	if (cli_enable >= 0)
		g_rpc_config->tls_enable_cli = cli_enable;
	if (cli_ciphersuites != NULL && cli_ciphersuites[0] != '\0') {
		snprintf(g_rpc_config->tls_ciphersuites_cli,
			 sizeof(g_rpc_config->tls_ciphersuites_cli), "%s",
			 cli_ciphersuites);
	}
}
