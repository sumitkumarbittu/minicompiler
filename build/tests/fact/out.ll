; ModuleID = 'minipy'
source_filename = "minipy"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "x86_64-apple-macosx14.0.0"

declare i32 @print_int(i64)
declare i32 @print_bool(i1)

define i64 @fact(i64 %n) {
entry:
  %t1.addr = alloca i64
  %t4.addr = alloca i64
  %t2.addr = alloca i64
  %t5.addr = alloca i64
  %t7.addr = alloca i64
  %t6.addr = alloca i64
  %n.addr = alloca i64
  %t3.addr = alloca i64
  store i64 %n, i64* %n.addr
  br label %start
start:
  store i64 1, i64* %t1.addr
  %_1 = load i64, i64* %n.addr
  %_2 = load i64, i64* %t1.addr
  %_3 = icmp sle i64 %_1, %_2
  %_4 = zext i1 %_3 to i64
  store i64 %_4, i64* %t2.addr
  %_5 = load i64, i64* %t2.addr
  %_6 = trunc i64 %_5 to i1
  br i1 %_6, label %then_1, label %if_cont_3
then_1:
  store i64 1, i64* %t3.addr
  %_7 = load i64, i64* %t3.addr
  ret i64 %_7
if_cont_3:
  store i64 1, i64* %t4.addr
  %_8 = load i64, i64* %n.addr
  %_9 = load i64, i64* %t4.addr
  %_10 = sub i64 %_8, %_9
  store i64 %_10, i64* %t5.addr
  %_11 = load i64, i64* %t5.addr
  %_12 = call i64 @fact(i64 %_11)
  store i64 %_12, i64* %t6.addr
  %_13 = load i64, i64* %n.addr
  %_14 = load i64, i64* %t6.addr
  %_15 = mul i64 %_13, %_14
  store i64 %_15, i64* %t7.addr
  %_16 = load i64, i64* %t7.addr
  ret i64 %_16
}
define i64 @main() {
entry:
  %t9.addr = alloca i64
  %t10.addr = alloca i64
  %t14.addr = alloca i64
  %t8.addr = alloca i64
  %t13.addr = alloca i64
  %t11.addr = alloca i64
  %t12.addr = alloca i64
  br label %start
start:
  store i64 5, i64* %t8.addr
  %_1 = load i64, i64* %t8.addr
  %_2 = call i64 @fact(i64 %_1)
  store i64 %_2, i64* %t9.addr
  %_3 = load i64, i64* %t9.addr
  call i32 @print_int(i64 %_3)
  store i64 10, i64* %t11.addr
  %_4 = load i64, i64* %t11.addr
  %_5 = call i64 @fact(i64 %_4)
  store i64 %_5, i64* %t12.addr
  %_6 = load i64, i64* %t12.addr
  call i32 @print_int(i64 %_6)
  store i64 0, i64* %t14.addr
  %_7 = load i64, i64* %t14.addr
  ret i64 %_7
}