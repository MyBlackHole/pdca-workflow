#include "common.h"
#include "tls_cert.h"
#include "unix_server.h"
#include "fs_service.h"
#include "logger.h"
#include "config.h"
#include "fs_source.h"
#include "backup_helper.h"
#include "utils.h"
#include "version.h"

/* rpc 层工具级 TLS 配置接口（rpc-config.h），此处只声明避免宏重定义冲突 */
extern void rpc_tls_config_set(int cli_enable, const char *cli_ciphersuites);

#include <sys/prctl.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/file.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <getopt.h>
#include <sys/wait.h>
#include <sys/shm.h>
#include <sys/resource.h>
#include <libgen.h>

//---------------------------------------------------------Args-------------------------------------------------
static struct option long_options[] = {
	{ "daemon", no_argument, NULL, 1001 },
	{ "data-path", required_argument, NULL, 1002 },
	{ "log-path", required_argument, NULL, 1006 },
	{ "work-dir", required_argument, NULL, 1016 },
	{ "service-port", required_argument, NULL, 1003 },
	{ "debug", required_argument, NULL, 1007 },
	{ "is_check_data", required_argument, NULL, 1008 },
	{ "app_name", required_argument, NULL, 1009 },
	{ "source-name", required_argument, NULL, 1011 },
	{ "source-host", required_argument, NULL, 1012 },
	{ "source-port", required_argument, NULL, 1013 },
	{ "cache-size", required_argument, NULL, 1015 },
	{ "backup-helper", no_argument, NULL, 2001 },
	{ "remote-dir", required_argument, NULL, 2003 },
	{ "tls-enable", required_argument, NULL, 2004 },
	{ "tls-ciphersuites", required_argument, NULL, 2005 },
	{ "help", no_argument, NULL, 'h' },
	{ "version", no_argument, NULL, 'V' },
	{ 0, 0, 0, 0 }
};

//---------------------------------------------------------Args END-------------------------------------------------
const char *g_version = FSDAEMON_VERSION;

inline static void usage(void)
{
	fprintf(stderr, "usage: command args ...\n");
	fprintf(stderr,
		"\t --data-path:             cache path must be like: (--data-path=/data/backup or --data-path /data/backup).\n");
	fprintf(stderr,
		"\t --log-path:              log path must be like: (--log-path=/var/log/fs-tools or --log-path /var/log/fs-tools).\n");
	fprintf(stderr,
		"\t --service-port:          service port must be like: (--service-port=8901 or --service-port 8901).\n");
	fprintf(stderr, "\t --daemon:                run as daemon.\n");
	fprintf(stderr,
		"\t --debug:                 debug mode must be like: (--debug).\n");
	fprintf(stderr,
		"\t --is_check_data:         check data must be like: (--is_check_data=1 or --is_check_data 1).\n");
	fprintf(stderr,
		"\t --app_name:              app_name must be like: (--app_name=app_name or --app_name app_name).\n");
	fprintf(stderr,
		"\t --type:                  type must be like: (--type=1 or --type 1, 1、2).\n");
	fprintf(stderr,
		"\t --source-host:           source_host must be like: (--source-host=source_host or --source-host source_host).\n");
	fprintf(stderr,
		"\t --source-port:           source_port must be like: (--source-port=8901 or --source-port 8901).\n");
	fprintf(stderr,
		"\t --backup-helper:    run as backup helper server.\n");
	fprintf(stderr,
		"\t --remote-dir:            remote backup directory.\n");
	fprintf(stderr,
		"\t --tls-enable:            rpc tls switch must be like: (--tls-enable=1 or --tls-enable 1).\n");
	fprintf(stderr,
		"\t --tls-ciphersuites:      rpc tls ciphersuites must be like: (--tls-ciphersuites=TLS_SM4_GCM_SM3 or --tls-ciphersuites TLS_SM4_GCM_SM3).\n");
	fprintf(stderr, "\t --help:                  show help info.\n");
	fprintf(stderr, "\t --version:               show version info.\n");
	exit(0);
}

static int args_process(const int argc, char **argv,
			struct option *long_options)
{
	int c = 0;
	int long_index = 0;
	static int cli_tls_enable = -1;
	while ((c = getopt_long(argc, argv, "d:b:s:hvV", long_options,
				&long_index)) != -1) {
		switch (c) {
		case 1001: {
			g_pConfig->deamon = 1;
			break;
		}
		case 1002: {
			g_pConfig->data_path = optarg;
			break;
		}
		case 1003: {
			g_pConfig->service_port = atoi(optarg);
			break;
		}
		case 1006: {
			g_pConfig->log_path = optarg;
			break;
		}
		case 1007: {
			g_pConfig->debug = atoi(optarg);
			break;
		}
		case 1008: {
			g_pConfig->check_data = atoi(optarg);
			set_rpc_check_data(g_pConfig->check_data);
			break;
		}
		case 1009: {
			g_pConfig->app_name = optarg;
			if (g_pConfig->app_name.size() < 1) {
				ErrorLog("app_name is null");
				exit(1);
			}
			break;
		}
		case 1011: {
			g_pConfig->source_name = optarg;
			if (g_pConfig->source_name.empty()) {
				ErrorLog("source_name is null");
				exit(1);
			}

			if (g_pConfig->source_name.length() > 56) {
				ErrorLog("source_name is too long (>56)");
				exit(1);
			}
			break;
		}
		case 1012: {
			g_pConfig->source_host = optarg;
			if (g_pConfig->source_host.empty()) {
				ErrorLog("source_host is null");
				exit(1);
			}
			break;
		}
		case 1013: {
			g_pConfig->source_port = atoi(optarg);
			if (g_pConfig->source_port <= 0) {
				ErrorLog("source_port is invalid");
				exit(1);
			}
			break;
		}
		case 1015: {
			g_pConfig->cache_size = atoi(optarg);
			if (g_pConfig->cache_size <= 0) {
				ErrorLog("cache_size is invalid");
				exit(1);
			}
			break;
		}
		case 2001: {
			g_pConfig->backup_helper_mode = true;
			break;
		}
		case 2003: {
			g_pConfig->remote_dir = optarg;
			break;
		}
		case 2004: {
			cli_tls_enable = atoi(optarg);
			rpc_tls_config_set(cli_tls_enable, NULL);
			break;
		}
		case 2005: {
			/* ciphersuites 与 enable 独立传参：enable 状态在
			 * args_process 内缓存（命令行顺序无关） */
			rpc_tls_config_set(cli_tls_enable, optarg);
			break;
		}
		case 'h': {
			usage();
			break;
		}
		case 'v':
		case 'V': {
			fprintf(stderr, "%s\n", g_version);
			exit(0);
		}
		default: {
			usage();
			exit(0);
		}
		}
	}
	return 0;
}

static void signal_shield()
{
	sigset_t signal_mask;
	sigemptyset(&signal_mask);
	sigaddset(&signal_mask, SIGPIPE);
	sigaddset(&signal_mask, SIGQUIT);
	sigaddset(&signal_mask, SIGUSR1);
	if (pthread_sigmask(SIG_BLOCK, &signal_mask, NULL) != 0) {
		fprintf(stderr, "block sigpipe error\n");
	}
}

int create_lock_file(const char *lock_file)
{
	int fd = open(lock_file, O_RDWR | O_CREAT, 0640);
	if (fd < 0) {
		perror("open lock file failed");
		return -1;
	}

	struct flock lock;
	lock.l_type = F_WRLCK;
	lock.l_start = 0;
	lock.l_whence = SEEK_SET;
	lock.l_len = 0;

	if (fcntl(fd, F_SETLK, &lock) < 0) {
		if (errno == EACCES || errno == EAGAIN) {
			ErrorLog("fsdeamon is already running");
		} else {
			ErrorLog("lock file failed");
		}
		close(fd);
		return -1;
	}

	char pid_str[16];
	snprintf(pid_str, sizeof(pid_str), "%d", getpid());
	if (ftruncate(fd, 0) != 0) {
		ErrorLog("truncate lock file failed");
		close(fd);
		return -1;
	}

	if ((size_t)write(fd, pid_str, strlen(pid_str)) != strlen(pid_str)) {
		ErrorLog("write pid failed");
		close(fd);
		return -1;
	}
	return fd;
}

void supervise()
{
	pid_t child_pid;
	int status;
	int wait_status;

	while (1) {
		child_pid = fork();

		if (child_pid == 0) {
			if (prctl(PR_SET_PDEATHSIG, SIGKILL) != 0) {
				ErrorLog("prctl failed %s", strerror(errno));
				exit(EXIT_FAILURE);
			}
			if (setsid() == -1) {
				ErrorLog("setsid failed %s", strerror(errno));
				exit(EXIT_FAILURE);
			}
			return;
		} else if (child_pid > 0) {
			InfoLog("fsdeamon started, pid: %d", child_pid);
			wait_status = waitpid(child_pid, &status, 0);
			if (wait_status == -1) {
				ErrorLog("waitpid failed %s", strerror(errno));
			} else if (WIFEXITED(status)) {
				InfoLog("Child exited with status: %d",
					WEXITSTATUS(status));
			} else if (WIFSIGNALED(status)) {
				InfoLog("Child killed by signal: %d",
					WTERMSIG(status));
			}
			sleep(1);
		} else {
			sleep(5);
		}
	}
}

#define UNIX_SOCKET ".sock"
#define WORKER_NAME "worker"
#define NET_NAME "network"
#define NET_UNIX_SOCKET NET_NAME UNIX_SOCKET
#define WORKER_UNIX_SOCKET WORKER_NAME UNIX_SOCKET
#define PID_NAME "fsdaemon.pid"

static int get_binary_path()
{
	char exe_path[PATH_MAX];
	ssize_t len =
		readlink("/proc/self/exe", exe_path, sizeof(exe_path) - 1);
	if (len != -1) {
		exe_path[len] = '\0';
		g_pConfig->binary_path = exe_path;
		return 0;
	} else {
		return -1;
	}
}

int main(int argc, char *argv[])
{
	char err_msg[1024];
	const char *config_file = getenv(RDB_CONFIG);

	if (get_binary_path()) {
		fprintf(stderr, "failed to get binary path: %s\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	if (set_rpc_init_config(config_file, err_msg, 1024) != 0 ||
	    fsdeamon_init_config(config_file, err_msg, sizeof(err_msg)) != 0) {
		ErrorLog("init config failed: %s", err_msg);
		exit(EXIT_FAILURE);
	}

	if (args_process(argc, argv, long_options) != 0) {
		ErrorLog("args process failed");
		exit(EXIT_FAILURE);
	}

	std::string source_host = g_pConfig->source_host;
	std::string data_path = g_pConfig->data_path;
	std::string log_path = g_pConfig->log_path;

	if (data_path.empty() || log_path.empty()) {
		ErrorLog("data_path or log_path is null");
		exit(EXIT_FAILURE);
	}

	if (mkdir_path(data_path.c_str()) != 0) {
		ErrorLog("create data directory failure, path:%s. [%s]",
			 data_path.c_str(), strerror(errno));
		exit(EXIT_FAILURE);
	}

	if (mkdir_path(log_path.c_str()) != 0) {
		ErrorLog("create log directory failure, path:%s. [%s]",
			 log_path.c_str(), strerror(errno));
		exit(EXIT_FAILURE);
	}

	if (chdir(data_path.c_str()) != 0) {
		ErrorLog("change to working directory:[%s] failure.",
			 data_path.c_str());
		exit(EXIT_FAILURE);
	} else {
		InfoLog("change to working directory:[%s] success.",
			data_path.c_str());
	}

	if (tls_cert_init_client_from_env() != 0) {
		ErrorLog("tls_cert_init_client_from_env failed");
		exit(EXIT_FAILURE);
	}

	if (g_pConfig->backup_helper_mode) {
		if (create_lock_file(PID_NAME) == -1) {
			exit(EXIT_FAILURE);
		}

		if (!fs_start_unix_server(WORKER_UNIX_SOCKET)) {
			ErrorLog("start unix server failed");
			exit(EXIT_FAILURE);
		} else {
			InfoLog("start unix server success");
		}

		return BackupHelper::RunAsServer(argc, argv);
	}

	signal_shield();

	if (g_pConfig->deamon) {
		if (init_log(log_path.c_str(), "deamon") < 0) {
			exit(EXIT_FAILURE);
		}

		if (daemon(1, 0) != 0) {
			ErrorLog("daemon failed");
			return EXIT_FAILURE;
		}

		if (create_lock_file(PID_NAME) == -1) {
			exit(EXIT_FAILURE);
		}

		supervise();
	} else {
		if (create_lock_file(PID_NAME) == -1) {
			exit(EXIT_FAILURE);
		}
	}

	if (!fs_start_unix_server(NET_UNIX_SOCKET)) {
		ErrorLog("start unix server failed");
		exit(EXIT_FAILURE);
	} else {
		InfoLog("start unix server success");
	}

	FsService service(NET_NAME, data_path, log_path);

	if (service.InitEnv() != 0) {
		ErrorLog("init service failed");
		exit(EXIT_FAILURE);
	}

	if (service.LoadAllSources() != 0) {
		WarningLog("load sources failed, continue...");
	}

	if (service.StartServiceThread() == false) {
		ErrorLog("run service failed");
		exit(EXIT_FAILURE);
	}

	service.WaitChildPid();

	return 0;
}
