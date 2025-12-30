#include "vm.h"

#include "chunk.h"
#include "debug.h"
#include "value.h"
#include "common.h"

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>

VM vm;

static void reset_stack() {
    vm.stack.count = 0;
}

static InterpretResult run() {
    #define READ_BYTE() (*vm.ip++)
    #define READ_CONSTANT() (vm.chunk->constants.values[READ_BYTE()])
    #define READ_CONSTANT_LONG() (vm.chunk->constants.values[((int)READ_BYTE()) | ((int)READ_BYTE() << 8) | ((int)READ_BYTE() << 16)])
    #define BINARY_OP(op)                                 \
        do {                                              \
            double b = pop();                             \
            Value a = get_value_array_back(&vm.stack);    \
            vm.stack.values[vm.stack.count - 1] = a op b; \
        } while (false)                                   \

    while (true) {
        #ifdef DEBUG_TRACE_EXECUTION
            printf("          ");
            for (int i = 0; i < vm.stack.count; i++) {
                printf("[ ");
                print_value(vm.stack.values[i]);
                printf(" ]");
            }
            printf("\n");
            disassemble_instruction(vm.chunk, (int)(vm.ip - vm.chunk->code));
        #endif

        uint8_t instruction = *vm.ip++;
        switch (instruction) {
            case OP_CONSTANT: {
                Value constant = READ_CONSTANT();
                push(constant);
                break;
            }
            case OP_CONSTANT_LONG: {
                Value constant = READ_CONSTANT_LONG();
                push(constant);
                break;
            }
            case OP_NEGATE: {
                Value to_negate = vm.stack.values[vm.stack.count - 1];
                vm.stack.values[vm.stack.count - 1] = -to_negate;
                break;
            }
            case OP_ADD:      BINARY_OP(+); break;
            case OP_SUBTRACT: BINARY_OP(-); break;
            case OP_MULTIPLY: BINARY_OP(*); break;
            case OP_DIVIDE:   BINARY_OP(/); break;
            case OP_RETURN: {
                print_value(pop());
                printf("\n");
                return INTERPRET_OK;
            }
        }
    }

    #undef READ_BYTE
    #undef READ_CONSTANT
    #undef READ_CONSTANT_LONG
    #undef BINARY_OP
}

void init_vm() {
    reset_stack();
}

void free_vm() {
    free_value_array(&vm.stack);
}

InterpretResult interpret(Chunk *chunk) {
    vm.chunk = chunk;
    vm.ip = vm.chunk->code;
    return run();
}

void push(Value value) {
    push_value_array(&vm.stack, value);
}

Value pop() {
    if (vm.stack.count == 0) {
        fprintf(stderr, "VM internal error: Stack underflow");
        assert(false);
    }

    vm.stack.count -= 1;
    return vm.stack.values[vm.stack.count]; // count subtracted by 1, because count index is one above largest this is now largest.
}