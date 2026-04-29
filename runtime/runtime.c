#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// MiniPython Runtime

void print_int(int64_t val) { printf("%lld\n", val); }

void print_bool(int val) {
  if (val)
    printf("True\n");
  else
    printf("False\n");
}

void print_float(double val) { printf("%g\n", val); }

void print_str(const char *val) { printf("%s\n", val); }

int str_eq(const char *a, const char *b) { return strcmp(a, b) == 0; }

typedef struct {
  int64_t len;
  int64_t cap;
  int64_t *items;
} MiniList;

static void bounds_check(MiniList *list, int64_t index) {
  if (!list || index < 0 || index >= list->len) {
    fprintf(stderr, "MiniPython runtime error: list index out of bounds\n");
    exit(1);
  }
}

void *list_new(int64_t initial_capacity) {
  MiniList *list = (MiniList *)malloc(sizeof(MiniList));
  if (!list) {
    fprintf(stderr, "MiniPython runtime error: allocation failed\n");
    exit(1);
  }
  list->len = 0;
  list->cap = initial_capacity > 0 ? initial_capacity : 4;
  list->items = (int64_t *)malloc(sizeof(int64_t) * list->cap);
  if (!list->items) {
    fprintf(stderr, "MiniPython runtime error: allocation failed\n");
    exit(1);
  }
  return list;
}

void list_append(void *ptr, int64_t value) {
  MiniList *list = (MiniList *)ptr;
  if (list->len >= list->cap) {
    list->cap *= 2;
    int64_t *items = (int64_t *)realloc(list->items, sizeof(int64_t) * list->cap);
    if (!items) {
      fprintf(stderr, "MiniPython runtime error: allocation failed\n");
      exit(1);
    }
    list->items = items;
  }
  list->items[list->len++] = value;
}

int64_t list_get(void *ptr, int64_t index) {
  MiniList *list = (MiniList *)ptr;
  bounds_check(list, index);
  return list->items[index];
}

void list_set(void *ptr, int64_t index, int64_t value) {
  MiniList *list = (MiniList *)ptr;
  bounds_check(list, index);
  list->items[index] = value;
}

int64_t list_len(void *ptr) {
  MiniList *list = (MiniList *)ptr;
  return list ? list->len : 0;
}
