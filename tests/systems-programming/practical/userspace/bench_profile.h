#ifndef BENCH_PROFILE_H
#define BENCH_PROFILE_H
#include <pthread.h>
#include <stddef.h>

void *profile_malloc(size_t size);
void profile_free(void *pointer);
int profile_mutex_lock(pthread_mutex_t *lock);
int profile_mutex_unlock(pthread_mutex_t *lock);
int profile_cond_wait(pthread_cond_t *cond, pthread_mutex_t *lock);
#endif
