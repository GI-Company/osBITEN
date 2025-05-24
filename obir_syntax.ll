; OBIR Syntax Definition

; Types
types {
    int = i64
    float = double
    string = %String*
    array = %Array*
    object = %Object*
}

; Class Definition
%Class = type {
    i8*,            ; name
    i32,            ; size
    %Method**,      ; methods
    %Field**        ; fields
}

; Method Definition
%Method = type {
    i8*,            ; name
    i8*,            ; signature
    i8*             ; bytecode
}

; Sample OBIR code:
; Define a class
%MyClass = type {
    %Object,        ; base class
    i64,            ; field1
    %String*        ; field2
}

; Define a method
define %Object* @MyClass_method(%MyClass* %this) {
entry:
    %field1 = getelementptr %MyClass, %MyClass* %this, i32 0, i32 1
    %value = load i64, i64* %field1
    
    ; Call system function
    %result = call i64 @syscall_process(i64 %value)
    
    ; Create return object
    %obj = call %Object* @Object_create()
    ret %Object* %obj
}

; Memory management
declare i8* @gc_alloc(i64)
declare void @gc_free(i8*)

; System integration
declare i64 @syscall_process(i64)
declare void @security_check(i8*)