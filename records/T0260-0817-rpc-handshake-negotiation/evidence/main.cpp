#include "tls_cert.h"
#include <cstdlib>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <getopt.h>
#include <signal.h>
#include <execinfo.h>

#include "logger.h"
#include "config.h"
#include "rpc-config.h"
#include "json.hpp"
#include "cli_help.h"
#include "cli.h"
#include "fsbackup-common.h"
#include "fs_service_proto.h"
#include "rpc.h"
#include "version.h"

//---------------------------------------------------------DEBUG-------------------------------------------------

void logerr(char *token)
{
	printf("%s\n", token);
}

void dump()
{
	void *array[50];
	size_t size;
	char **strings;
	size_t i;
	size = backtrace(array, 50);
	strings = backtrace_symbols(array, size);
	printf("Obtained %zd stack frames.\n", size);

	for (i = 0; i < size; i++) {
		logerr(strings[i]);
	}
	////free(strings);
}

void sigshutdown(int number)
{
	fprintf(stderr, "sign:%d.", number);
	fprintf(stderr, "[%s]%d,pid:%d\n", __FUNCTION__, number, getpid());
	dump();
	exit(-1);
}

void signalset(void)
{
	// CoolFish: Test Signal 2001/10/26
	signal(SIGINT, sigshutdown);
	// signal(SIGQUIT, sigshutdown);
	signal(SIGILL, sigshutdown);
	signal(SIGTRAP, sigshutdown);
	signal(SIGIOT, sigshutdown);
	signal(SIGBUS, sigshutdown);
	signal(SIGFPE, sigshutdown);
	// signal(SIGKILL, sigshutdown);
	/*signal(SIGSEGV, sigshutdown);*/
	signal(SIGPIPE, SIG_IGN);
	signal(SIGTERM, sigshutdown);
}
//---------------------------------------------------------DEBUG END-------------------------------------------------

int err_code = 0;
using json = nlohmann::json;

static struct option long_options[] = {
	{ "host", required_argument, NULL, 1001 },
	{ "port", required_argument, NULL, 1002 },
	{ "method", required_argument, NULL, 1003 },
	{ "name", required_argument, NULL, 1004 },
	{ "type", required_argument, NULL, 1005 },
	{ "path", required_argument, NULL, 1006 },
	{ "full-path", required_argument, NULL, 1007 },
	{ "resume", required_argument, NULL, 1008 },
	{ "encrypt", optional_argument, NULL, 1009 },
	{ "compress", optional_argument, NULL, 1010 },
	{ "checksum", optional_argument, NULL, 1011 },
	{ "source", required_argument, NULL, 1012 },
	{ "bak-path", required_argument, NULL, 1013 },
	{ "log-path", required_argument, NULL, 1014 },
	{ "kernel-port", required_argument, NULL, 1015 },
	{ "parallel", required_argument, NULL, 1016 },
	{ "cache-rate", required_argument, NULL, 1017 },
	{ "short-path", no_argument, NULL, 1018 },
	{ "rpc-port", required_argument, NULL, 1019 },
	{ "decr", required_argument, NULL, 1020 },
	{ "local_ip", required_argument, NULL, 1021 },
	{ "local_port", required_argument, NULL, 1022 },
	{ "exclude-path", required_argument, NULL, 1023 },
	{ "done-log-path", required_argument, NULL, 1028 },
	{ "is_short", no_argument, NULL, 1024 },
	{ "source-name", required_argument, NULL, 1025 },
	{ "is_check_data", required_argument, NULL, 1026 },
	{ "debug_status", required_argument, NULL, 1027 },
	{ "start-snapshot", required_argument, NULL, 1029 },
	{ "end-snapshot", required_argument, NULL, 1030 },
	{ "config-path", required_argument, NULL, 1031 },
	{ "tls-enable", required_argument, NULL, 1032 },
	{ "tls-ciphersuites", required_argument, NULL, 1033 },
	{ "help", no_argument, NULL, 'h' },
	{ "version", no_argument, NULL, 'v' },
	{ 0, 0, 0, 0 }
};

const char *g_version = FSDAEMON_VERSION;

static void usage()
{
	fprintf(stderr, "usage: command args ...\n");
	fprintf(stderr,
		"\t --host:               host ip must be like: (--host=127.0.0.1 or --host 127.0.0.1).\n");
	fprintf(stderr,
		"\t --port:               port must be like: (--port=8901 or --port 8901).\n");
	fprintf(stderr,
		"\t --local_ip:           local ip must be like: (--local_ip=127.0.0.1 or --local_ip 127.0.0.1).\n");
	fprintf(stderr,
		"\t --local_port:         local port must be like: (--local_port=18901 or --local_port 18901).\n");
	fprintf(stderr,
		"\t --rpc-port:           rpc-port be like: (--host=6611 or --host 6611).\n");
	fprintf(stderr,
		"\t --method:             request method must be like: (--method=list or --method list).\n");
	fprintf(stderr,
		"\t --name:               request backup name must be like: (--name=1677048031 or --name 1677048031).\n");
	fprintf(stderr,
		"\t --type:               request type must be like: (--type=full/inc or --type full/inc).\n");
	fprintf(stderr,
		"\t       :               when restore, backup type (value as 1by1,once) must be like: (--restore-type=1by1 or --restore-type once).\n");
	fprintf(stderr,
		"\t --path:               save backup data path must be like: (--path=/backup/data or --path /backup/data).\n");
	fprintf(stderr,
		"\t --full-path:          save full backup data path (as necessary) must be like: (--full-path=/backup/data/full or --full-path /backup/data/full).\n");
	fprintf(stderr,
		"\t --resume:             resume must be like: (--resume=1 or --resume 1).\n");
	fprintf(stderr,
		"\t --checksum:           checksum must be like: (--checksum=1 or --checksum 1).\n");
	fprintf(stderr,
		"\t --encrypt:            encrypt must be like: (--encrypt=1 or --encrypt 1).\n");
	fprintf(stderr,
		"\t --compress:           compress must be like: (--compress=1 or --compress 1).\n");
	fprintf(stderr,
		"\t --bak-path:           source backup path must be like: (--bak-path=/monitor/data or --bak-path /monitor/data).\n");
	fprintf(stderr,
		"\t --log-path:           log-path must be like: (--log-path=/var/kernel/logs or --log-path /var/kernel/logs).\n");
	// fprintf(stderr, "\t --out-mode:           out-mode must be like: (--out-mode=network or --out-mode local).\n");
	fprintf(stderr,
		"\t --parallel:           parallel must be like: (--parallel=4 or --parallel 4).\n");
	fprintf(stderr,
		"\t --cache-rate:         cache-rate must be like: (--cache-rate=50 or --cache-rate 50).\n");
	fprintf(stderr,
		"\t --tls-enable:         rpc tls switch must be like: (--tls-enable=1 or --tls-enable 1).\n");
	fprintf(stderr,
		"\t --tls-ciphersuites:   rpc tls ciphersuites must be like: (--tls-ciphersuites=TLS_SM4_GCM_SM3 or --tls-ciphersuites TLS_SM4_GCM_SM3).\n");
	fprintf(stderr, "\t --short-path:         short-path.\n");
	fprintf(stderr,
		"\t --decr:               decrement number must be like: (--decr=1 or --decr 1).\n");

	show_method_help(g_pConfig->method);
	fprintf(stderr, "\t --help:         -h    usage help\n");
	fprintf(stderr, "\t --version:      -v    version information\n");
}

static int args_process(const int argc, char **argv,
			struct option *long_options)
{
	int c = 0;
	int long_index = 0;

	while ((c = getopt_long(argc, argv, "h:p:m:n:t:P:f:Hv", long_options,
				&long_index)) != -1) {
		switch (c) {
		case 1001: {
			snprintf(g_pConfig->host, sizeof(g_pConfig->host), "%s",
				 optarg);
			break;
		}
		case 1002: {
			g_pConfig->port = atoi(optarg);
			break;
		}
		case 1003: {
			snprintf(g_pConfig->method, sizeof(g_pConfig->method),
				 "%s", optarg);
			break;
		}
		case 1004: {
			if (strlen(optarg) >= SNAPSHOT_NAME_LEN) {
				fprintf(stderr, "snapshot_name too long\n");
				exit(1);
			}
			if (strlen(optarg) <= 0) {
				fprintf(stderr, "snapshot_name is empty\n");
				exit(1);
			}
			snprintf(g_pConfig->snapshot_name, SNAPSHOT_NAME_LEN,
				 "%s", optarg);
			break;
		}
		case 1025: {
			if (strlen(optarg) >= SOURCE_NAME_LEN) {
				fprintf(stderr, "source_name too long\n");
				exit(1);
			}

			if (strlen(optarg) <= 0) {
				fprintf(stderr, "source_name is empty\n");
				exit(1);
			}

			snprintf(g_pConfig->source_name, SOURCE_NAME_LEN, "%s",
				 optarg);
			break;
		}
		case 1026: {
			g_pConfig->check_data = atoi(optarg);
			set_rpc_check_data(g_pConfig->check_data);
			break;
		}
		case 1027: {
			g_pConfig->debug_status = atoi(optarg);
			break;
		}
		case 1005: {
			if (strlen(optarg) >= BACKUP_TYPE_LEN) {
				fprintf(stderr, "backup_type too long\n");
				exit(1);
			}

			if (strlen(optarg) <= 0) {
				fprintf(stderr, "backup_type is empty\n");
				exit(1);
			}

			snprintf(g_pConfig->backup_type, BACKUP_TYPE_LEN, "%s",
				 optarg);
			if (strcmp(g_pConfig->backup_type, "full") == 0) {
				g_pConfig->snapshot_type = SNAPSHOT_TYPE_FULL;
			} else if (strcmp(g_pConfig->backup_type, "inc") == 0) {
				g_pConfig->snapshot_type = SNAPSHOT_TYPE_INC;
			} else if (strcmp(g_pConfig->backup_type, "merge") ==
				   0) {
				g_pConfig->snapshot_type = SNAPSHOT_TYPE_MERGE;
			} else {
				fprintf(stderr, "backup_type %s error\n",
					optarg);
				exit(1);
			}
			break;
		}
		case 1006: {
			int len = strlen(optarg);
			if (len >= MAX_PATH_LEN) {
				fprintf(stderr, "save_path too long\n");
				exit(1);
			}
			if (len <= 0) {
				fprintf(stderr, "save_path is empty\n");
				exit(1);
			}
			if (optarg[len - 1] != '/') {
				snprintf(g_pConfig->save_dir, MAX_PATH_LEN,
					 "%s/", optarg);
			} else {
				snprintf(g_pConfig->save_dir, MAX_PATH_LEN,
					 "%s", optarg);
			}
			break;
		}
		case 1007: {
			int len = strlen(optarg);
			if (len >= MAX_PATH_LEN) {
				fprintf(stderr, "save_full_path too long\n");
				exit(1);
			}
			if (len <= 0) {
				fprintf(stderr, "save_full_path is empty\n");
				exit(1);
			}
			if (optarg[len - 1] != '/') {
				snprintf(g_pConfig->save_full_dir, MAX_PATH_LEN,
					 "%s/", optarg);
			} else {
				snprintf(g_pConfig->save_full_dir, MAX_PATH_LEN,
					 "%s", optarg);
			}
			break;
		}
		case 1008: {
			if (optarg[0] == '\0') {
				g_pConfig->resume = 1;
			} else {
				g_pConfig->resume = atoi(optarg);
			}
			break;
		}
		case 1009: {
			if (optarg == NULL || optarg[0] == '\0') {
				g_pConfig->encrypt = 1;
			} else {
				g_pConfig->encrypt = atoi(optarg);
			}
			break;
		}
		case 1010: {
			if (optarg == NULL || optarg[0] == '\0') {
				g_pConfig->compress = 1;
			} else {
				g_pConfig->compress = atoi(optarg);
			}
			break;
		}
		case 1011: {
			if (optarg == NULL || optarg[0] == '\0') {
				g_pConfig->crc = 1;
			} else {
				g_pConfig->crc = atoi(optarg);
			}
			break;
		}
		case 1012: {
			// 解析 source_host 和 source_port
			std::string source_host_port = optarg;
			size_t pos = source_host_port.find(':');
			if (pos != std::string::npos) {
				g_pConfig->source_port =
					atoi(source_host_port.substr(pos + 1)
						     .c_str());
				source_host_port.erase(pos);
			}
			strncpy(g_pConfig->source_host,
				source_host_port.c_str(),
				sizeof(g_pConfig->source_host) - 1);
			break;
		}
		case 1013: {
			if (strlen(optarg) >= BACKUP_PATH_LEN) {
				fprintf(stderr, "backup_path too long\n");
				exit(1);
			}

			if (strlen(optarg) <= 0) {
				fprintf(stderr, "backup_path is empty\n");
				exit(1);
			}
			snprintf(g_pConfig->backup_path, BACKUP_PATH_LEN, "%s",
				 optarg);
			break;
		}
		case 1014: {
			snprintf(g_pConfig->logPath, CONF_PATH_MAX_LEN, "%s",
				 optarg);
			g_pConfig->mode = 0;
			break;
		}
		case 1015: //kernel-port
		{
			g_pConfig->mode = 1;
			g_pConfig->kn_port = atoi(optarg);
			break;
		}
		case 1016: {
			g_pConfig->parallel = atoi(optarg);
			if (g_pConfig->parallel <= 0) {
				fprintf(stderr, "parallel must > 0\n");
				exit(1);
			}
			break;
		}
		case 1017: {
			g_pConfig->cacheRate = atol(optarg);
			break;
		}
		case 1018: {
			g_pConfig->shortPath = 1;
			break;
		}
		case 1019: {
			g_pConfig->rpc_port = atoi(optarg);
			break;
		}
		case 1020: {
			g_pConfig->decr = atoi(optarg);
			break;
		}
		case 1021: {
			strncpy(g_pConfig->local_ip, optarg,
				sizeof(g_pConfig->local_ip) - 1);
			break;
		}
		case 1022: {
			g_pConfig->local_port = atoi(optarg);
			break;
		}
		case 1023: {
			if (strlen(optarg) >= EXCLUDE_PATH_LEN) {
				fprintf(stderr, "exclude_path too long\n");
				exit(1);
			}

			if (strlen(optarg) <= 0) {
				fprintf(stderr, "exclude_path is empty\n");
				exit(1);
			}
			snprintf(g_pConfig->exclude_path, EXCLUDE_PATH_LEN,
				 "%s", optarg);
			break;
		}
		case 1028: {
			if (strlen(optarg) >= CONF_PATH_MAX_LEN) {
				fprintf(stderr, "done_log_path too long\n");
				exit(1);
			}

			if (strlen(optarg) <= 0) {
				fprintf(stderr, "done_log_path is empty\n");
				exit(1);
			}
			snprintf(g_pConfig->logPath, CONF_PATH_MAX_LEN, "%s",
				 optarg);
			break;
		}
		case 1029: {
			if (strlen(optarg) >= SNAPSHOT_NAME_LEN) {
				fprintf(stderr,
					"start_snapshot_name too long\n");
				exit(1);
			}
			if (strlen(optarg) <= 0) {
				fprintf(stderr,
					"start_snapshot_name is empty\n");
				exit(1);
			}
			snprintf(g_pConfig->start_snapshot_name,
				 SNAPSHOT_NAME_LEN, "%s", optarg);
			break;
		}
		case 1030: {
			if (strlen(optarg) >= SNAPSHOT_NAME_LEN) {
				fprintf(stderr, "end_snapshot_name too long\n");
				exit(1);
			}
			if (strlen(optarg) <= 0) {
				fprintf(stderr, "end_snapshot_name is empty\n");
				exit(1);
			}
			snprintf(g_pConfig->end_snapshot_name,
				 SNAPSHOT_NAME_LEN, "%s", optarg);
			break;
		}
		case 1024: {
			g_pConfig->is_short = true;
			break;
		}
		case 1031: {
			if (strlen(optarg) >= BACKUP_PATH_LEN) {
				fprintf(stderr, "config_path too long\n");
				exit(1);
			}

			if (strlen(optarg) <= 0) {
				fprintf(stderr, "config_path is empty\n");
				exit(1);
			}
			snprintf(g_pConfig->config_path, BACKUP_PATH_LEN, "%s",
				 optarg);
			break;
		}
		case 1032: {
			rpc_tls_config_set(atoi(optarg), NULL);
			break;
		}
		case 1033: {
			rpc_tls_config_set(g_rpc_config->tls_enable_cli,
					   optarg);
			break;
		}
		case 'h': {
			usage();
			exit(0);
			break;
		}
		case 'v':
		case 'V': {
			fprintf(stderr, "%s\n", g_version);
			exit(0);
			break;
		}
		default: {
			fprintf(stderr, "bad opt: %d, %s\n", c, optarg);
			usage();
			exit(0);
			break;
		}
		}
	}
	if (g_pConfig->kn_port > 0 && g_pConfig->mode != 1) {
		g_pConfig->mode = 1;
	}
	optind = 0;
	return 0;
}
typedef int (*request_method)(CliConfig *);

struct fs_client_handler {
	const char *name;
	u_int type;
	request_method handler;
};

static const struct fs_client_handler handlers[] = {
	{ "list", FS_LIST, backup_list },
	{ "snapshot", FS_BACKUP, make_snapshot },
	{ "merge-snapshot", FS_SNAPSHOT_LIST, make_merge_snapshot },
	{ "backup", FS_CHECK, make_backup },
	{ "restore", FS_RESTORE, restore_backup },
	{ "del-backup", FS_DEL_BACKUP, del_backup },
	{ "add-trackup", FS_ADD_TRACKUP, addTrackup },
	{ "del-trackup", FS_DEL_TRACKUP, delTrackup },
	{ "add-exclude", FS_ADD_EXCLUDE, addExclude },
	{ "del-exclude", FS_DEL_EXCLUDE, delExclude },
	{ "add-source", FS_ADD_SOURCE, addSource },
	{ "del-source", FS_DEL_SOURCE, delSource },
	{ "update-source-host", FS_UPDATE_SOURCE_HOST, update_source_host },
	{ "list-source", FS_LIST_SOURCE, listSource },
	{ "check", FS_CHECK, check },
	{ "debug-source", FS_DEBUG_SOURCE, debug_source },
	{ "update-log-dir", FS_UPDATE_LOG_DIR, update_log_dir },
	{ "fsdev-read-count", FS_FSDEV_READ_COUNT, ioctlFsbackupDevReadCount },
	{ "fsdev-decr-count", FS_FSDEV_DECR_COUNT,
	  ioctlFsbackupDevDeincrCount },
	{ "reload-config", FS_RELOAD_CONFIG, reload_config },
	{ "show-config", FS_SHOW_CONFIG, show_config },
	{ NULL, 0, NULL }
};

int main(int argc, char *argv[])
{
	int ret = -1;
	int i = 0;
	int sockfd = -1;
	request_method method_handler = NULL;
	char err_msg[1024];
	const char *config_file = getenv(RDB_CONFIG);

	if (set_rpc_init_config(config_file, err_msg, 1024) != 0 ||
	    fsclient_init_config(config_file, err_msg, 1024) != 0) {
		ErrorLog("init config failure, %s", err_msg);
		exit(EXIT_FAILURE);
	}

	if (args_process(argc, argv, long_options) < 0) {
		usage();
		exit(0);
	}

	if (argc < 3 || g_pConfig->method[0] == 0x00) {
		if (argc == 2) {
			show_method_help(argv[1]);
			return EXIT_FAILURE;
		}
		usage();
		exit(0);
	}

	if (tls_cert_init_client_from_env() != 0) {
		ErrorLog("tls_cert_init_client_from_env failed");
		exit(EXIT_FAILURE);
	}

	for (i = 0; handlers[i].handler != NULL; i++) {
		if (strncmp(g_pConfig->method, handlers[i].name,
			    strlen(g_pConfig->method)) == 0) {
			method_handler = handlers[i].handler;
			g_pConfig->type = handlers[i].type;
			break;
		}
	}

	if (method_handler == NULL) {
		fprintf(stderr, "bad request: %s\n", g_pConfig->method);
		show_method_help(g_pConfig->method);
		goto exit__;
	}

	signalset();

	if (g_pConfig->type != FS_RESTORE) {
		if (g_pConfig->host[0] == '\0' || g_pConfig->port == 0) {
			fprintf(stderr, "method:%s need host and port\n",
				g_pConfig->method);
			goto exit__;
		}

		sockfd = open_service(g_pConfig->host, g_pConfig->port);
		if (sockfd < 0) {
			goto exit__;
		}

		g_pConfig->sockFd = sockfd;
	}

	ret = method_handler(g_pConfig);
	if (err_code != 0) {
		ret = err_code;
	}
	close(sockfd);
exit__:
	return ret;
}
