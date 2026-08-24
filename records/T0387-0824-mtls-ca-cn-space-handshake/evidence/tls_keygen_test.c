/* tls_keygen CN 合法性校验单元测试（T0387）。
 * 被测：common.c 的 cn_name_valid（keygen 与客户端 tls_cert_ca_cn_valid 共用规则：
 * [A-Za-z0-9._-]，拒绝空串/NULL/".." 子串，禁止空格）。 */
#include <stdio.h>
#include <string.h>

#include "../common.h"

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

TEST(reject_space_cn)
{
	/* keygen 旧示例名含空格，必须被拒绝 */
	assert(cn_name_valid("My SM2 Root CA") == 0);
}

TEST(accept_legal_cn)
{
	assert(cn_name_valid("My_SM2_Root_CA") == 1);
	assert(cn_name_valid("a.b_C-d") == 1);
	assert(cn_name_valid("A9") == 1);
}

TEST(reject_empty_and_null)
{
	assert(cn_name_valid("") == 0);
	assert(cn_name_valid(NULL) == 0);
}

TEST(reject_dotdot_traversal)
{
	assert(cn_name_valid("..") == 0);
	assert(cn_name_valid("a..b") == 0);
}

TEST(reject_other_metachars)
{
	assert(cn_name_valid("a/b") == 0);
	assert(cn_name_valid("a\tb") == 0);
}

int main(void)
{
	RUN_TEST(reject_space_cn);
	RUN_TEST(accept_legal_cn);
	RUN_TEST(reject_empty_and_null);
	RUN_TEST(reject_dotdot_traversal);
	RUN_TEST(reject_other_metachars);

	printf("\n%d passed, %d failed\n", tests_passed, tests_failed);
	return tests_failed == 0 ? 0 : 1;
}
