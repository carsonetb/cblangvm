#ifndef CBLANGVM_CHUNK_H
#define CBLANGVM_CHUNK_H

#include "value.h"
#include <stdint.h>

typedef enum {
    OP_CONSTANT,
    OP_CONSTANT_LONG,
    OP_NEGATE,
    OP_ADD,
    OP_SUBTRACT,
    OP_MULTIPLY,
    OP_DIVIDE,
    OP_RETURN,
} OpCode;

typedef struct {
    int num;
    int line;
    int instruction_range_begin;
    int instruction_range_end;
} LineGroup;

typedef struct {
    int count;
    int capacity;
    int lines_count;
    int lines_capacity;
    uint8_t* code;
    LineGroup* lines;
    ValueArray constants;
} Chunk;

void init_line_group(LineGroup* line_group, int line, int instruction_range_begin);
void init_chunk(Chunk* chunk);
void write_chunk(Chunk* chunk, uint8_t byte, int line);
void free_chunk(Chunk* chunk);
int add_constant(Chunk* chunk, Value value);
int get_line(Chunk* chunk, int instruction_ind);

#endif // CBLANGVM_CHUNK_H