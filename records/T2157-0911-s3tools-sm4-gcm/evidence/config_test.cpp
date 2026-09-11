#include "config.h"
#include "rdb-config.h"

#include <cstdio>
#include <cstring>

static int failures = 0;
#define CHECK(cond, msg)                                                     \
	do {                                                                 \
		if (!(cond)) {                                                 \
			printf("FAIL: %s\n", msg);                             \
			failures++;                                            \
		} else {                                                       \
			printf("ok:   %s\n", msg);                             \
		}                                                              \
	} while (0)

static void write_conf(const char *path, const char *content)
{
	FILE *f = fopen(path, "w");
	if (!f) {
		printf("FAIL: cannot write %s\n", path);
		failures++;
		return;
	}
	fputs(content, f);
	fclose(f);
}

int main(void)
{
	char err[256];
	const char *tf = "/tmp/s3file_cfg_test.conf";

	/* Case 1: 正常读取 [s3file] 各参数，经 sec_get_* 生效 */
	write_conf(tf,
		   "[s3file]\n"
		   "cache_path=/var/cache/s3/\n"
		   "gmssl=1\n"
		   "parallel=4\n");
	memset(err, 0, sizeof(err));
	int rc = s3file_init_config(tf, err, sizeof(err));
	CHECK(rc == 0, "s3file init ok with valid config");
	CHECK(g_config->parallel == 4, "parallel read=4");
	CHECK(g_config->gmssl == 1, "gmssl read=1");
	CHECK(strcmp(g_config->cache_path.c_str(), "/var/cache/s3/") == 0,
	      "cache_path read");

	/* Case 2: 缺省回落（文件存在但无 [s3file] 键） */
	write_conf(tf, "[other]\nx=1\n");
	memset(err, 0, sizeof(err));
	rc = s3file_init_config(tf, err, sizeof(err));
	CHECK(rc == 0, "s3file init ok with empty [s3file]");
	CHECK(g_config->parallel == 8, "parallel default=8");
	CHECK(g_config->gmssl == 0, "gmssl default=0");
	CHECK(strcmp(g_config->cache_path.c_str(), "/tmp/s3-cache/") == 0,
	      "cache_path default=/tmp/s3-cache/");

	/* Case 3: 缺文件容忍（ENOENT）回落默认，与 fs-backup 一致 */
	memset(err, 0, sizeof(err));
	rc = s3file_init_config("/tmp/does_not_exist_xyz.conf", err,
				sizeof(err));
	CHECK(rc == 0, "s3file init ok with missing file (tolerant)");
	CHECK(g_config->parallel == 8, "parallel default after missing file");

	/* Case 4: parallel 非整数 fail-closed 拒绝 */
	write_conf(tf, "[s3file]\nparallel=abc\n");
	memset(err, 0, sizeof(err));
	rc = s3file_init_config(tf, err, sizeof(err));
	CHECK(rc == -1, "s3file reject non-integer parallel");

	/* Case 5: gmssl 三态 0/1/2 合法，越界与非整数 fail-closed 拒绝 */
	write_conf(tf, "[s3file]\ngmssl=2\n");
	memset(err, 0, sizeof(err));
	rc = s3file_init_config(tf, err, sizeof(err));
	CHECK(rc == 0, "s3file accept gmssl=2 (SM4-GCM)");
	CHECK(g_config->gmssl == 2, "gmssl read=2");

	write_conf(tf, "[s3file]\ngmssl=3\n");
	memset(err, 0, sizeof(err));
	rc = s3file_init_config(tf, err, sizeof(err));
	CHECK(rc == -1, "s3file reject gmssl=3");

	write_conf(tf, "[s3file]\ngmssl=abc\n");
	memset(err, 0, sizeof(err));
	rc = s3file_init_config(tf, err, sizeof(err));
	CHECK(rc == -1, "s3file reject non-integer gmssl");

	/* Case 6: cache_path 空值（inih 丢弃空值）回落默认，与历史一致 */
	write_conf(tf, "[s3file]\ncache_path=\n");
	memset(err, 0, sizeof(err));
	rc = s3file_init_config(tf, err, sizeof(err));
	CHECK(rc == 0, "s3file empty cache_path falls back to default");
	CHECK(strcmp(g_config->cache_path.c_str(), "/tmp/s3-cache/") == 0,
	      "cache_path default after empty value");

	printf("\n%s\n", failures == 0 ? "ALL TESTS PASSED"
				    : "SOME TESTS FAILED");
	return failures == 0 ? 0 : 1;
}
