; ModuleID = 'minipy'
source_filename = "minipy"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "x86_64-apple-macosx14.0.0"

declare i32 @print_int(i64)
declare i32 @print_bool(i1)

define i64 @main() {
entry:
  %e.addr = alloca i64
  %t4.addr = alloca i64
  %t7.addr = alloca i64
  %b.addr = alloca i64
  %t9.addr = alloca i64
  %t6.addr = alloca i64
  %t3.addr = alloca i64
  %d.addr = alloca i64
  %c.addr = alloca i64
  %t5.addr = alloca i64
  %t2.addr = alloca i64
  %t10.addr = alloca i64
  %a.addr = alloca i64
  %t8.addr = alloca i64
  %t11.addr = alloca i64
  %t1.addr = alloca i64
  br label %start
start:
  store i64 3, i64* %t1.addr
  %_1 = load i64, i64* %t1.addr
  store i64 %_1, i64* %a.addr
  store i64 5, i64* %t2.addr
  %_2 = load i64, i64* %t2.addr
  store i64 %_2, i64* %b.addr
  store i64 2, i64* %t3.addr
  %_3 = load i64, i64* %t3.addr
  store i64 %_3, i64* %c.addr
  store i64 45, i64* %t4.addr
  %_4 = load i64, i64* %t4.addr
  store i64 %_4, i64* %d.addr
  store i64 28232, i64* %t5.addr
  %_5 = load i64, i64* %t5.addr
  store i64 %_5, i64* %e.addr
  %_6 = load i64, i64* %a.addr
  %_7 = load i64, i64* %b.addr
  %_8 = add i64 %_6, %_7
  store i64 %_8, i64* %t6.addr
  %_9 = load i64, i64* %t6.addr
  %_10 = load i64, i64* %c.addr
  %_11 = sdiv i64 %_9, %_10
  store i64 %_11, i64* %t7.addr
  %_12 = load i64, i64* %t7.addr
  %_13 = load i64, i64* %d.addr
  %_14 = add i64 %_12, %_13
  store i64 %_14, i64* %t8.addr
  %_15 = load i64, i64* %t8.addr
  %_16 = load i64, i64* %e.addr
  %_17 = sub i64 %_15, %_16
  store i64 %_17, i64* %t9.addr
  %_18 = load i64, i64* %t9.addr
  call i32 @print_int(i64 %_18)
  store i64 0, i64* %t11.addr
  %_19 = load i64, i64* %t11.addr
  ret i64 %_19
}