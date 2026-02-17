; ModuleID = 'minipy'
source_filename = "minipy"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "x86_64-apple-macosx14.0.0"

declare i32 @print_int(i64)
declare i32 @print_bool(i1)

define i64 @main() {
entry:
  %t2.addr = alloca i64
  %t11.addr = alloca i64
  %t4.addr = alloca i64
  %b.addr = alloca i64
  %t9.addr = alloca i64
  %t8.addr = alloca i64
  %t10.addr = alloca i64
  %c.addr = alloca i64
  %t13.addr = alloca i64
  %t1.addr = alloca i64
  %a.addr = alloca i64
  %t6.addr = alloca i64
  %t12.addr = alloca i64
  %t3.addr = alloca i64
  %t7.addr = alloca i64
  %t5.addr = alloca i64
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
  %_4 = load i64, i64* %a.addr
  %_5 = load i64, i64* %b.addr
  %_6 = add i64 %_4, %_5
  store i64 %_6, i64* %t4.addr
  %_7 = load i64, i64* %t4.addr
  %_8 = load i64, i64* %c.addr
  %_9 = sdiv i64 %_7, %_8
  store i64 %_9, i64* %t5.addr
  store i64 3, i64* %t6.addr
  store i64 2, i64* %t7.addr
  %_10 = load i64, i64* %t6.addr
  %_11 = load i64, i64* %t7.addr
  %_12 = mul i64 %_10, %_11
  store i64 %_12, i64* %t8.addr
  %_13 = load i64, i64* %t5.addr
  %_14 = load i64, i64* %t8.addr
  %_15 = add i64 %_13, %_14
  store i64 %_15, i64* %t9.addr
  store i64 1, i64* %t10.addr
  %_16 = load i64, i64* %t9.addr
  %_17 = load i64, i64* %t10.addr
  %_18 = sub i64 %_16, %_17
  store i64 %_18, i64* %t11.addr
  %_19 = load i64, i64* %t11.addr
  call i32 @print_int(i64 %_19)
  store i64 0, i64* %t13.addr
  %_20 = load i64, i64* %t13.addr
  ret i64 %_20
}