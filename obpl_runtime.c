#include <emscripten.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// OBPL VM State
typedef struct {
    uint8_t* memory;
    uint32_t mem_size;
    uint32_t ip;        // Instruction pointer
    uint32_t sp;        // Stack pointer
    uint64_t* stack;
    uint32_t stack_size;
    uint8_t* bytecode;
    uint32_t bytecode_size;
} OBPLState;

// OBPL Opcodes
enum {
    OP_PUSH = 1,
    OP_POP,
    OP_ADD,
    OP_SUB,
    OP_MUL,
    OP_DIV,
    OP_STORE,
    OP_LOAD,
    OP_PRINT,
    OP_CALL,
    OP_RET,
    OP_JMP,
    OP_JMPIF,
    OP_EQ,
    OP_GT,
    OP_LT,
    OP_END
};

static OBPLState* vm = NULL;

EMSCRIPTEN_KEEPALIVE
int32_t obpl_init(uint32_t mem_size, uint32_t stack_size) {
    vm = (OBPLState*)malloc(sizeof(OBPLState));
    if (!vm) return -1;

    vm->memory = (uint8_t*)calloc(mem_size, 1);
    vm->stack = (uint64_t*)calloc(stack_size, sizeof(uint64_t));
    
    if (!vm->memory || !vm->stack) {
        free(vm->memory);
        free(vm->stack);
        free(vm);
        vm = NULL;
        return -2;
    }

    vm->mem_size = mem_size;
    vm->stack_size = stack_size;
    vm->ip = 0;
    vm->sp = 0;
    vm->bytecode = NULL;
    vm->bytecode_size = 0;

    return 0;
}

EMSCRIPTEN_KEEPALIVE
int32_t obpl_load_bytecode(uint8_t* bytecode, uint32_t size) {
    if (!vm) return -1;
    
    if (vm->bytecode) free(vm->bytecode);
    
    vm->bytecode = (uint8_t*)malloc(size);
    if (!vm->bytecode) return -2;

    memcpy(vm->bytecode, bytecode, size);
    vm->bytecode_size = size;
    vm->ip = 0;

    return 0;
}

EMSCRIPTEN_KEEPALIVE
int32_t obpl_execute() {
    if (!vm || !vm->bytecode) return -1;

    while (vm->ip < vm->bytecode_size) {
        uint8_t opcode = vm->bytecode[vm->ip++];
        
        switch (opcode) {
            case OP_PUSH: {
                uint64_t value;
                memcpy(&value, &vm->bytecode[vm->ip], sizeof(uint64_t));
                vm->ip += sizeof(uint64_t);
                if (vm->sp >= vm->stack_size) return -2;
                vm->stack[vm->sp++] = value;
                break;
            }
            case OP_POP: {
                if (vm->sp == 0) return -3;
                vm->sp--;
                break;
            }
            case OP_ADD: {
                if (vm->sp < 2) return -3;
                vm->sp--;
                vm->stack[vm->sp - 1] += vm->stack[vm->sp];
                break;
            }
            // ... Additional opcodes implementation ...
            case OP_END:
                return 0;
        }
    }
    return 0;
}

EMSCRIPTEN_KEEPALIVE
void obpl_cleanup() {
    if (!vm) return;
    free(vm->memory);
    free(vm->stack);
    free(vm->bytecode);
    free(vm);
    vm = NULL;
}