CC = gcc
CXX = g++
ifndef OUTPUT_ROOT
$(error Set OUTPUT_ROOT to an absolute workspace output directory outside this asset tree)
endif
ROOT := $(abspath $(OUTPUT_ROOT))
ifneq ($(filter /tmp /tmp/%,$(ROOT)),)
$(error OUTPUT_ROOT must not use /tmp)
endif
MODE ?= normal
BUILD := $(ROOT)/$(MODE)
COMMON = -O2 -g -Wall -Wextra -Werror -Wpedantic -pthread -save-temps=obj
SAN =
ifeq ($(MODE),asan)
SAN = -fsanitize=address,undefined -fno-omit-frame-pointer
endif
ifeq ($(MODE),tsan)
SAN = -fsanitize=thread -fno-omit-frame-pointer
endif
CFLAGS = -std=c11 $(COMMON) $(SAN)
CXXFLAGS = -std=c++11 $(COMMON) $(SAN) -fno-exceptions -fno-rtti
WRAPS = -Wl,--wrap=malloc,--wrap=free,--wrap=pthread_mutex_init
WRAPS += -Wl,--wrap=pthread_cond_init,--wrap=pthread_create,--wrap=pthread_join

override export TMPDIR := $(ROOT)/tmp
override export TMP := $(TMPDIR)
override export TEMP := $(TMPDIR)
override export ASAN_OPTIONS := detect_leaks=0:halt_on_error=1:symbolize=0:log_path=$(ROOT)/logs/asan
override export UBSAN_OPTIONS := halt_on_error=1:print_stacktrace=0:log_path=$(ROOT)/logs/ubsan
override export TSAN_OPTIONS := halt_on_error=1:symbolize=0:log_path=$(ROOT)/logs/tsan

.PHONY: all check check-c asan tsan bench
all: $(BUILD)/test_rq $(BUILD)/test_cpp $(BUILD)/test_parent

$(BUILD) $(ROOT)/tmp $(ROOT)/logs:
	mkdir -p "$@"

$(BUILD)/rq.o: rq.c rq.h | $(BUILD) $(ROOT)/tmp $(ROOT)/logs
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/rq-test.o: rq.c rq.h | $(BUILD) $(ROOT)/tmp $(ROOT)/logs
	$(CC) $(CFLAGS) -fno-builtin -c $< -o $@

$(BUILD)/test_rq.o: test_rq.c rq.h test_support.h | $(BUILD) $(ROOT)/tmp
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/test_support.o: test_support.c test_support.h | $(BUILD) $(ROOT)/tmp
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/test_parent.o: test_parent.c rq.h | $(BUILD) $(ROOT)/tmp
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/test_cpp.o: test_cpp.cc rq.h | $(BUILD) $(ROOT)/tmp
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(BUILD)/test_rq: $(BUILD)/rq-test.o $(BUILD)/test_rq.o $(BUILD)/test_support.o
	$(CC) $^ -pthread $(SAN) $(WRAPS) -o $@

$(BUILD)/test_cpp: $(BUILD)/rq.o $(BUILD)/test_cpp.o
	$(CC) $^ -pthread $(SAN) -o $@

$(BUILD)/test_parent: $(BUILD)/rq.o $(BUILD)/test_parent.o
	$(CC) $^ -pthread $(SAN) -o $@

check-c: $(BUILD)/test_rq $(BUILD)/test_parent
	timeout 60 "$(BUILD)/test_rq"
	timeout 60 "$(BUILD)/test_parent"

check: check-c $(BUILD)/test_cpp
	timeout 30 "$(BUILD)/test_cpp"

asan:
	$(MAKE) MODE=asan check

tsan:
	$(MAKE) MODE=tsan check

$(BUILD)/bench_rq.o: bench_rq.c rq.h bench_profile.h | $(BUILD) $(ROOT)/tmp
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/rq-profile.o: rq.c rq.h bench_profile.h | $(BUILD) $(ROOT)/tmp
	$(CC) $(CFLAGS) -fno-builtin -Dmalloc=profile_malloc -Dfree=profile_free -Dpthread_mutex_lock=profile_mutex_lock -Dpthread_mutex_unlock=profile_mutex_unlock -Dpthread_cond_wait=profile_cond_wait -c $< -o $@

$(BUILD)/bench_plain: $(BUILD)/rq.o $(BUILD)/bench_rq.o
	$(CC) $^ -pthread $(SAN) -o $@

$(BUILD)/bench_profile: $(BUILD)/rq-profile.o $(BUILD)/bench_rq.o
	$(CC) $^ -pthread $(SAN) -o $@

# Each process emits one JSON record. Repeat externally; do not mix profile timing with plain timing.
bench: $(BUILD)/bench_plain $(BUILD)/bench_profile
