#ifndef CBLANGVM_VM_H
#define CBLANGVM_VM_H

#include "chunk.h"
#include "value.h"

#define STACK_MAX 256

typedef struct {
    Chunk* chunk;
    uint8_t* ip;
    ValueArray stack;
} VM;

typedef enum {
    INTERPRET_OK,
    INTERPRET_COMPILE_ERROR,
    INTERPRET_RUNTIME_ERROR,
} InterpretResult;

void init_vm();
void free_vm();
InterpretResult interpret(Chunk* chunk);
void push(Value value);
Value pop();

#endif // CBLANGVM_VM_H