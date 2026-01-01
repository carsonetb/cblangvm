#ifndef CBLANGVM_DEBUG_H
#define CBLANGVM_DEBUG_H

#include "chunk.h"

void disasseble_chunk(Chunk* chunk, const char* name);
int disassemble_instruction(Chunk* chunk, int offset);

#endif // CBLANGVM_DEBUG_H