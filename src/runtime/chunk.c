#include "chunk.h"
#include "memory.h"
#include "value.h"

#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

void init_line_group(LineGroup *line_group, int line, int instruction_range_begin) {
    line_group->num = 1;
    line_group->line = line;
    line_group->instruction_range_begin = instruction_range_begin;
    line_group->instruction_range_end = instruction_range_begin;
}

void init_chunk(Chunk *chunk) {
    chunk->count = 0;
    chunk->capacity = 0;
    chunk->code = NULL;
    chunk->lines = NULL;
    init_value_array(&chunk->constants);
}

void write_chunk(Chunk *chunk, uint8_t byte, int line) {
    if (chunk->count + 1 > chunk->capacity) {
        int old_capacity = chunk->capacity;
        chunk->capacity = GROW_CAPACITY(old_capacity);
        chunk->code = GROW_ARRAY(uint8_t, chunk->code, old_capacity, chunk->capacity);
    }
    if (chunk->lines_count == 0 || (line != chunk->lines[chunk->lines_count - 1].line && chunk->lines_count + 1 > chunk->lines_capacity)) { // If this is a new line, and the lines array is full. Or there are currently no lines stored.
        int old_capacity = chunk->lines_capacity;
        chunk->lines_capacity = GROW_CAPACITY(old_capacity);
        chunk->lines = GROW_ARRAY(LineGroup, chunk->lines, old_capacity, chunk->lines_capacity);
    }

    chunk->code[chunk->count] = byte;
    chunk->count += 1;

    if (chunk->lines_count != 0 && line == chunk->lines[chunk->lines_count - 1].line) {
        LineGroup* last_line_group = &chunk->lines[chunk->lines_count - 1];
        last_line_group->num += 1;
        last_line_group->instruction_range_end = chunk->count - 1;
    }
    else {
        LineGroup new_line_group;
        init_line_group(&new_line_group, line, chunk->count - 1);
        chunk->lines[chunk->lines_count] = new_line_group;
        chunk->lines_count += 1;
    }
}

void free_chunk(Chunk* chunk) {
    FREE_ARRAY(uint8_t, chunk->code, chunk->capacity);
    FREE_ARRAY(int, chunk->lines, chunk->capacity);
    free_value_array(&chunk->constants);
}

int add_constant(Chunk *chunk, Value value) {
    push_value_array(&chunk->constants, value);
    return chunk->constants.count - 1;
}

void write_constant(Chunk* chunk, Value value, int line) {
    int constant = add_constant(chunk, value);
    if (constant >= 0 && value <= UINT8_MAX) {
        write_chunk(chunk, OP_CONSTANT, line);
        write_chunk(chunk, (uint8_t)constant, line);
    }
    else if (constant >= 0 && value < (1 << 24)) {
        uint8_t byte1 = (constant >> 16) & 0xFF;
        uint8_t byte2 = (constant >> 8)  & 0xFF;
        uint8_t byte3 = constant         & 0xFF;
        write_chunk(chunk, OP_CONSTANT_LONG, line);
        write_chunk(chunk, byte1, line);
        write_chunk(chunk, byte2, line);
        write_chunk(chunk, byte3, line);
    }
    else {
        assert(false); // too many constants in this line, or constant number is somehow less than one.
    }
}

int get_line(Chunk* chunk, int instruction_ind) {
    for (int i = 0; i < chunk->lines_count; i++) {
        LineGroup* this_line = &chunk->lines[i];
        if (instruction_ind >= this_line->instruction_range_begin && instruction_ind <= this_line->instruction_range_end) {
            return this_line->line;
        }
    }

    // Seems like this happend pretty often. 
    // Usually because of an invalid instruction index.
    // -- pop() underflow of the stack?
    assert(false);
}