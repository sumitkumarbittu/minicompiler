; ModuleID = 'minipy'
source_filename = "minipy"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "x86_64-apple-macosx14.0.0"

declare i32 @print_int(i64)
declare i32 @print_bool(i1)

define i64 @fib(i64 %n) {
entry:
  %t1.addr = alloca i64
  %a.addr = alloca i64
  %t5.addr = alloca i64
  %i.addr = alloca i64
  %n.addr = alloca i64
  %temp.addr = alloca i64
  %t3.addr = alloca i64
  %t4.addr = alloca i64
  %t2.addr = alloca i64
  %t6.addr = alloca i64
  %t7.addr = alloca i64
  %b.addr = alloca i64
  store i64 %n, i64* %n.addr
  br label %start
start:
  store i64 0, i64* %t1.addr
  %_1 = load i64, i64* %t1.addr
  store i64 %_1, i64* %a.addr
  store i64 1, i64* %t2.addr
  %_2 = load i64, i64* %t2.addr
  store i64 %_2, i64* %b.addr
  store i64 0, i64* %t3.addr
  %_3 = load i64, i64* %t3.addr
  store i64 %_3, i64* %i.addr
  br label %while_cond_1
while_cond_1:
  %_4 = load i64, i64* %i.addr
  %_5 = load i64, i64* %n.addr
  %_6 = icmp slt i64 %_4, %_5
  %_7 = zext i1 %_6 to i64
  store i64 %_7, i64* %t4.addr
  %_8 = load i64, i64* %t4.addr
  %_9 = trunc i64 %_8 to i1
  br i1 %_9, label %while_body_2, label %while_exit_3
while_body_2:
  %_10 = load i64, i64* %a.addr
  %_11 = load i64, i64* %b.addr
  %_12 = add i64 %_10, %_11
  store i64 %_12, i64* %t5.addr
  %_13 = load i64, i64* %t5.addr
  store i64 %_13, i64* %temp.addr
  %_14 = load i64, i64* %b.addr
  store i64 %_14, i64* %a.addr
  %_15 = load i64, i64* %temp.addr
  store i64 %_15, i64* %b.addr
  store i64 1, i64* %t6.addr
  %_16 = load i64, i64* %i.addr
  %_17 = load i64, i64* %t6.addr
  %_18 = add i64 %_16, %_17
  store i64 %_18, i64* %t7.addr
  %_19 = load i64, i64* %t7.addr
  store i64 %_19, i64* %i.addr
  br label %while_cond_1
while_exit_3:
  %_20 = load i64, i64* %a.addr
  ret i64 %_20
}
define i64 @main() {
entry:
  %t9.addr = alloca i64
  %t8.addr = alloca i64
  %t10.addr = alloca i64
  %t11.addr = alloca i64
  br label %start
start:
  store i64 10, i64* %t8.addr
  %_1 = load i64, i64* %t8.addr
  %_2 = call i64 @fib(i64 %_1)
  store i64 %_2, i64* %t9.addr
  %_3 = load i64, i64* %t9.addr
  call i32 @print_int(i64 %_3)
  store i64 0, i64* %t11.addr
  %_4 = load i64, i64* %t11.addr
  ret i64 %_4
}