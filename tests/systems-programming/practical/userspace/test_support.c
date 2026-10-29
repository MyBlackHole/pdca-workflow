#define _POSIX_C_SOURCE 200809L
#include "test_support.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

/* Link-time wrappers interpose system boundaries, never queue internals. */
void *__real_malloc(size_t size);
void __real_free(void *pointer);
int __real_pthread_mutex_init(pthread_mutex_t *lock,
			      const pthread_mutexattr_t *attr);
int __real_pthread_cond_init(pthread_cond_t *cond,
			     const pthread_condattr_t *attr);
int __real_pthread_create(pthread_t *thread, const pthread_attr_t *attr,
			  void *(*start)(void *), void *arg);
int __real_pthread_join(pthread_t thread, void **result);

static _Thread_local enum test_failure next_failure;
static _Thread_local enum test_pause next_pause;
static _Thread_local struct test_gate *pause_gate;
static pthread_mutex_t account_lock = PTHREAD_MUTEX_INITIALIZER;
static void *allocations[2048];
static size_t live_allocations;
static size_t live_threads;
static size_t allocation_calls;

void test_fail(const char *condition, const char *file, int line)
{
	fprintf(stderr, "%s:%d: CHECK(%s) failed\n", file, line, condition);
	fflush(stderr);
	_Exit(1);
}

struct timespec test_deadline(unsigned int milliseconds)
{
	struct timespec deadline;

	CHECK(clock_gettime(CLOCK_REALTIME, &deadline) == 0);
	deadline.tv_sec += milliseconds / 1000;
	deadline.tv_nsec += (long)(milliseconds % 1000) * 1000000L;
	if (deadline.tv_nsec >= 1000000000L) {
		deadline.tv_nsec -= 1000000000L;
		deadline.tv_sec++;
	}
	return deadline;
}

void test_gate_enter(struct test_gate *gate)
{
	struct timespec deadline = test_deadline(5000);

	CHECK(pthread_mutex_lock(&gate->lock) == 0);
	gate->entered = true;
	CHECK(pthread_cond_broadcast(&gate->changed) == 0);
	while (!gate->released)
		CHECK(pthread_cond_timedwait(&gate->changed, &gate->lock,
					     &deadline) == 0);
	CHECK(pthread_mutex_unlock(&gate->lock) == 0);
}

void test_gate_wait(struct test_gate *gate)
{
	struct timespec deadline = test_deadline(5000);

	CHECK(pthread_mutex_lock(&gate->lock) == 0);
	while (!gate->entered)
		CHECK(pthread_cond_timedwait(&gate->changed, &gate->lock,
					     &deadline) == 0);
	CHECK(pthread_mutex_unlock(&gate->lock) == 0);
}

void test_gate_release(struct test_gate *gate)
{
	CHECK(pthread_mutex_lock(&gate->lock) == 0);
	gate->released = true;
	CHECK(pthread_cond_broadcast(&gate->changed) == 0);
	CHECK(pthread_mutex_unlock(&gate->lock) == 0);
}

void test_gate_destroy(struct test_gate *gate)
{
	CHECK(pthread_cond_destroy(&gate->changed) == 0);
	CHECK(pthread_mutex_destroy(&gate->lock) == 0);
}

void test_fail_next(enum test_failure failure)
{
	CHECK(next_failure == TEST_FAIL_NONE);
	next_failure = failure;
}

bool test_failure_consumed(void)
{
	return next_failure == TEST_FAIL_NONE;
}

void test_pause_next(enum test_pause pause, struct test_gate *gate)
{
	CHECK(next_pause == TEST_PAUSE_NONE);
	next_pause = pause;
	pause_gate = gate;
}

static void pause_if_requested(enum test_pause pause)
{
	struct test_gate *gate;

	if (next_pause != pause)
		return;
	gate = pause_gate;
	next_pause = TEST_PAUSE_NONE;
	pause_gate = NULL;
	test_gate_enter(gate);
}

void *__wrap_malloc(size_t size)
{
	void *pointer;
	size_t slot;

	pause_if_requested(TEST_PAUSE_BEFORE_MALLOC);
	CHECK(pthread_mutex_lock(&account_lock) == 0);
	allocation_calls++;
	CHECK(pthread_mutex_unlock(&account_lock) == 0);
	if (next_failure == TEST_FAIL_MALLOC) {
		next_failure = TEST_FAIL_NONE;
		errno = EDOM;
		return NULL;
	}
	pointer = __real_malloc(size);
	if (pointer) {
		CHECK(pthread_mutex_lock(&account_lock) == 0);
		for (slot = 0; slot < 2048 && allocations[slot]; slot++)
			;
		CHECK(slot < 2048);
		allocations[slot] = pointer;
		live_allocations++;
		CHECK(pthread_mutex_unlock(&account_lock) == 0);
	}
	pause_if_requested(TEST_PAUSE_AFTER_MALLOC);
	return pointer;
}

void __wrap_free(void *pointer)
{
	size_t slot;

	if (!pointer)
		return;
	pause_if_requested(TEST_PAUSE_BEFORE_FREE);
	CHECK(pthread_mutex_lock(&account_lock) == 0);
	for (slot = 0; slot < 2048 && allocations[slot] != pointer; slot++)
		;
	CHECK(slot < 2048);
	__real_free(pointer);
	allocations[slot] = NULL;
	CHECK(live_allocations != 0);
	live_allocations--;
	CHECK(pthread_mutex_unlock(&account_lock) == 0);
}

int __wrap_pthread_mutex_init(pthread_mutex_t *lock,
			     const pthread_mutexattr_t *attr)
{
	if (next_failure == TEST_FAIL_MUTEX_INIT) {
		next_failure = TEST_FAIL_NONE;
		errno = EDOM;
		return EBUSY;
	}
	return __real_pthread_mutex_init(lock, attr);
}

int __wrap_pthread_cond_init(pthread_cond_t *cond,
			    const pthread_condattr_t *attr)
{
	if (next_failure == TEST_FAIL_COND_INIT) {
		next_failure = TEST_FAIL_NONE;
		errno = EDOM;
		return ENOMEM;
	}
	return __real_pthread_cond_init(cond, attr);
}

int __wrap_pthread_create(pthread_t *thread, const pthread_attr_t *attr,
			 void *(*start)(void *), void *arg)
{
	int error;

	if (next_failure == TEST_FAIL_THREAD_CREATE) {
		next_failure = TEST_FAIL_NONE;
		errno = EDOM;
		return EAGAIN;
	}
	error = __real_pthread_create(thread, attr, start, arg);
	if (!error) {
		CHECK(pthread_mutex_lock(&account_lock) == 0);
		live_threads++;
		CHECK(pthread_mutex_unlock(&account_lock) == 0);
	}
	return error;
}

int __wrap_pthread_join(pthread_t thread, void **result)
{
	int error = __real_pthread_join(thread, result);

	if (!error) {
		CHECK(pthread_mutex_lock(&account_lock) == 0);
		CHECK(live_threads != 0);
		live_threads--;
		CHECK(pthread_mutex_unlock(&account_lock) == 0);
	}
	return error;
}

size_t test_allocations(void)
{
	size_t count;

	CHECK(pthread_mutex_lock(&account_lock) == 0);
	count = live_allocations;
	CHECK(pthread_mutex_unlock(&account_lock) == 0);
	return count;
}

size_t test_threads(void)
{
	size_t count;

	CHECK(pthread_mutex_lock(&account_lock) == 0);
	count = live_threads;
	CHECK(pthread_mutex_unlock(&account_lock) == 0);
	return count;
}

size_t test_allocation_calls(void)
{
	size_t count;

	CHECK(pthread_mutex_lock(&account_lock) == 0);
	count = allocation_calls;
	CHECK(pthread_mutex_unlock(&account_lock) == 0);
	return count;
}
