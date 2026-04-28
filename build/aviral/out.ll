; ModuleID = 'minipy'
source_filename = "minipy"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "x86_64-apple-macosx14.0.0"

declare i32 @print_int(i64)
declare i32 @print_bool(i1)

define i64 @main() {
entry:
  %t2.addr = alloca i64
  %t1.addr = alloca i64
  %t3.addr = alloca i64
  %t4.addr = alloca i64
  %t5.addr = alloca i64
  br label %start
start:
  store i64 3, i64* %t1.addr
  store i64 5, i64* %t2.addr
  %_1 = load i64, i64* %t1.addr
  %_2 = load i64, i64* %t2.addr
  %_3 = add i64 %_1, %_2
  store i64 %_3, i64* %t3.addr
  %_4 = load i64, i64* %t3.addr
  call i32 @print_int(i64 %_4)
  store i64 0, i64* %t5.addr
  %_5 = load i64, i64* %t5.addr
  ret i64 %_5
}