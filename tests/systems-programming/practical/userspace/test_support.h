#ifndef TEST_SUPPORT_H
#define TEST_SUPPORT_H

#include <pthread.h>
#include <stdbool.h>
#include <stddef.h>
#include <time.h>

#define CHECK(condition) do { \
	if (!(condition)) \
		test_fail(#condition, __FILE__, __LINE__); \
} while (0)

void test_fail(const char *condition, const char *file, int line);
struct timespec test_deadline(unsigned int milliseconds);

struct test_gate {
	pthread_mutex_t lock;
	pthread_cond_t changed;
	bool entered;
	bool released;
};

#define TEST_GATE_INIT { PTHREAD_MUTEX_INITIALIZER, \
	PTHREAD_COND_INITIALIZER, false, false }

void test_gate_enter(struct test_gate *gate);
void test_gate_wait(struct test_gate *gate);
void test_gate_release(struct test_gate *gate);
void test_gate_destroy(struct test_gate *gate);

enum test_failure {
	TEST_FAIL_NONE,
	TEST_FAIL_MALLOC,
	TEST_FAIL_MUTEX_INIT,
	TEST_FAIL_COND_INIT,
	TEST_FAIL_THREAD_CREATE
};

enum test_pause {
	TEST_PAUSE_NONE,
	TEST_PAUSE_BEFORE_MALLOC,
	TEST_PAUSE_AFTER_MALLOC,
	TEST_PAUSE_BEFORE_FREE
};

void test_fail_next(enum test_failure failure);
bool test_failure_consumed(void);
void test_pause_next(enum test_pause pause, struct test_gate *gate);
size_t test_allocations(void);
size_t test_threads(void);
size_t test_allocation_calls(void);

#endif
