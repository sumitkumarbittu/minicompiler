; ModuleID = 'minipy'
source_filename = "minipy"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "x86_64-apple-macosx14.0.0"

declare void @print_int(i64)
declare void @print_bool(i1)
declare void @print_float(double)
declare void @print_str(i8*)
declare i1 @str_eq(i8*, i8*)
declare i8* @list_new(i64)
declare void @list_append(i8*, i64)
declare i64 @list_get(i8*, i64)
declare void @list_set(i8*, i64, i64)
declare i64 @list_len(i8*)

@.str.0 = private unnamed_addr constant [11 x i8] c"MiniPython\00"

define i64 @main() {
entry:
  %t1.addr = alloca i64
  %a.addr = alloca i64
  %t2.addr = alloca i64
  %b.addr = alloca i64
  %t3.addr = alloca i64
  %t4.addr = alloca i64
  %t5.addr = alloca i64
  %t6.addr = alloca double
  %x.addr = alloca double
  %t7.addr = alloca i64
  %y.addr = alloca i64
  %t8.addr = alloca double
  %t9.addr = alloca i64
  %t10.addr = alloca i8*
  %name.addr = alloca i8*
  %t11.addr = alloca i64
  %t12.addr = alloca i8*
  %t13.addr = alloca i64
  %t14.addr = alloca i64
  %t15.addr = alloca i64
  %total.addr = alloca i64
  %t16.addr = alloca i64
  %i.addr = alloca i64
  %t17.addr = alloca i64
  %t18.addr = alloca i64
  %t19.addr = alloca i64
  %t20.addr = alloca i64
  %t21.addr = alloca i64
  %t22.addr = alloca i64
  %t23.addr = alloca i64
  %t24.addr = alloca i64
  %t25.addr = alloca i64
  %t26.addr = alloca i64
  %t27.addr = alloca i64
  %t28.addr = alloca i64
  %t29.addr = alloca i64
  %t30.addr = alloca i8*
  %xs.addr = alloca i8*
  %t31.addr = alloca i64
  %t32.addr = alloca i64
  %t33.addr = alloca i64
  %t34.addr = alloca i64
  %t35.addr = alloca i64
  %t36.addr = alloca i64
  %t37.addr = alloca i64
  %t38.addr = alloca i64
  %t39.addr = alloca i64
  %t40.addr = alloca i64
  %t41.addr = alloca i64
  %t42.addr = alloca i64
  %t43.addr = alloca i64
  %t44.addr = alloca i64
  br label %start
start:
  store i64 1, i64* %t1.addr
  %_1 = load i64, i64* %t1.addr
  store i64 %_1, i64* %a.addr
  store i64 0, i64* %t2.addr
  %_2 = load i64, i64* %t2.addr
  store i64 %_2, i64* %b.addr
  %_3 = load i64, i64* %b.addr
  %_4 = icmp ne i64 %_3, 0
  %_5 = xor i1 %_4, true
  %_6 = zext i1 %_5 to i64
  store i64 %_6, i64* %t3.addr
  %_7 = load i64, i64* %a.addr
  %_8 = load i64, i64* %t3.addr
  %_9 = mul i64 %_7, %_8
  store i64 %_9, i64* %t4.addr
  %_10 = load i64, i64* %t4.addr
  %_11 = load i64, i64* %t4.addr
  %_12 = icmp ne i64 %_11, 0
  call void @print_bool(i1 %_12)
  store double 3.500000e+00, double* %t6.addr
  %_13 = load double, double* %t6.addr
  store double %_13, double* %x.addr
  store i64 2, i64* %t7.addr
  %_14 = load i64, i64* %t7.addr
  store i64 %_14, i64* %y.addr
  %_15 = load double, double* %x.addr
  %_16 = load i64, i64* %y.addr
  %_17 = sitofp i64 %_16 to double
  %_18 = fadd double %_15, %_17
  store double %_18, double* %t8.addr
  %_19 = load double, double* %t8.addr
  %_20 = load double, double* %t8.addr
  call void @print_float(double %_20)
  %_21 = getelementptr inbounds [11 x i8], [11 x i8]* @.str.0, i64 0, i64 0
  store i8* %_21, i8** %t10.addr
  %_22 = load i8*, i8** %t10.addr
  store i8* %_22, i8** %name.addr
  %_23 = load i8*, i8** %name.addr
  %_24 = load i8*, i8** %name.addr
  call void @print_str(i8* %_24)
  %_25 = getelementptr inbounds [11 x i8], [11 x i8]* @.str.0, i64 0, i64 0
  store i8* %_25, i8** %t12.addr
  %_27 = load i8*, i8** %name.addr
  %_28 = load i8*, i8** %t12.addr
  %_29 = call i1 @str_eq(i8* %_27, i8* %_28)
  %_30 = zext i1 %_29 to i64
  store i64 %_30, i64* %t13.addr
  %_31 = load i64, i64* %t13.addr
  %_32 = load i64, i64* %t13.addr
  %_33 = icmp ne i64 %_32, 0
  call void @print_bool(i1 %_33)
  store i64 0, i64* %t15.addr
  %_34 = load i64, i64* %t15.addr
  store i64 %_34, i64* %total.addr
  store i64 1, i64* %t16.addr
  %_35 = load i64, i64* %t16.addr
  store i64 %_35, i64* %i.addr
  store i64 5, i64* %t17.addr
  %_36 = load i64, i64* %t17.addr
  store i64 %_36, i64* %t18.addr
  store i64 1, i64* %t19.addr
  %_37 = load i64, i64* %t19.addr
  store i64 %_37, i64* %t20.addr
  br label %for_cond_1
for_cond_1:
  %_39 = load i64, i64* %i.addr
  %_40 = load i64, i64* %t18.addr
  %_38 = icmp slt i64 %_39, %_40
  %_41 = zext i1 %_38 to i64
  store i64 %_41, i64* %t21.addr
  %_42 = load i64, i64* %t21.addr
  %_43 = icmp ne i64 %_42, 0
  br i1 %_43, label %for_body_2, label %for_exit_4
for_body_2:
  store i64 3, i64* %t22.addr
  %_45 = load i64, i64* %i.addr
  %_46 = load i64, i64* %t22.addr
  %_44 = icmp eq i64 %_45, %_46
  %_47 = zext i1 %_44 to i64
  store i64 %_47, i64* %t23.addr
  %_48 = load i64, i64* %t23.addr
  %_49 = icmp ne i64 %_48, 0
  br i1 %_49, label %for_incr_3, label %if_cont_7
if_cont_7:
  %_50 = load i64, i64* %total.addr
  %_51 = load i64, i64* %i.addr
  %_52 = add i64 %_50, %_51
  store i64 %_52, i64* %t24.addr
  %_53 = load i64, i64* %t24.addr
  store i64 %_53, i64* %total.addr
  br label %for_incr_3
for_incr_3:
  %_54 = load i64, i64* %i.addr
  %_55 = load i64, i64* %t20.addr
  %_56 = add i64 %_54, %_55
  store i64 %_56, i64* %t25.addr
  %_57 = load i64, i64* %t25.addr
  store i64 %_57, i64* %i.addr
  br label %for_cond_1
for_exit_4:
  %_58 = load i64, i64* %total.addr
  %_59 = load i64, i64* %total.addr
  call void @print_int(i64 %_59)
  store i64 1, i64* %t27.addr
  store i64 2, i64* %t28.addr
  store i64 3, i64* %t29.addr
  %_60 = call i8* @list_new(i64 3)
  store i8* %_60, i8** %t30.addr
  %_61 = load i64, i64* %t27.addr
  call void @list_append(i8* %_60, i64 %_61)
  %_62 = load i64, i64* %t28.addr
  call void @list_append(i8* %_60, i64 %_62)
  %_63 = load i64, i64* %t29.addr
  call void @list_append(i8* %_60, i64 %_63)
  %_64 = load i8*, i8** %t30.addr
  store i8* %_64, i8** %xs.addr
  store i64 4, i64* %t31.addr
  %_65 = load i8*, i8** %xs.addr
  %_66 = load i64, i64* %t31.addr
  %_67 = load i8*, i8** %xs.addr
  %_68 = load i64, i64* %t31.addr
  call void @list_append(i8* %_67, i64 %_68)
  store i64 0, i64* %t33.addr
  store i64 10, i64* %t34.addr
  %_69 = load i8*, i8** %xs.addr
  %_70 = load i64, i64* %t33.addr
  %_71 = load i64, i64* %t34.addr
  call void @list_set(i8* %_69, i64 %_70, i64 %_71)
  store i64 0, i64* %t35.addr
  %_72 = load i8*, i8** %xs.addr
  %_73 = load i64, i64* %t35.addr
  %_74 = call i64 @list_get(i8* %_72, i64 %_73)
  store i64 %_74, i64* %t36.addr
  store i64 3, i64* %t37.addr
  %_75 = load i8*, i8** %xs.addr
  %_76 = load i64, i64* %t37.addr
  %_77 = call i64 @list_get(i8* %_75, i64 %_76)
  store i64 %_77, i64* %t38.addr
  %_78 = load i64, i64* %t36.addr
  %_79 = load i64, i64* %t38.addr
  %_80 = add i64 %_78, %_79
  store i64 %_80, i64* %t39.addr
  %_81 = load i64, i64* %t39.addr
  %_82 = load i64, i64* %t39.addr
  call void @print_int(i64 %_82)
  %_83 = load i8*, i8** %xs.addr
  %_84 = load i8*, i8** %xs.addr
  %_85 = call i64 @list_len(i8* %_84)
  store i64 %_85, i64* %t41.addr
  %_86 = load i64, i64* %t41.addr
  %_87 = load i64, i64* %t41.addr
  call void @print_int(i64 %_87)
  br label %while_cond_8
while_cond_8:
  store i64 1, i64* %t43.addr
  %_88 = load i64, i64* %t43.addr
  %_89 = icmp ne i64 %_88, 0
  br i1 %_89, label %while_exit_10, label %while_exit_10
while_exit_10:
  store i64 0, i64* %t44.addr
  %_90 = load i64, i64* %t44.addr
  ret i64 %_90
}