#include <stdint.h>
#include <stdio.h>

// MiniPython v1 Runtime

void print_int(int64_t val) { printf("%lld\n", val); }

void print_bool(int val) {
  if (val)
    printf("True\n");
  else
    printf("False\n");
}
