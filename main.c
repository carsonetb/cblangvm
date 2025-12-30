// Disclaimer: This VM is heavily inspired from the book 
// Crafting Interpreters by Robert Nystrom.

#include "chunk.h"
#include "debug.h"
#include "vm.h"

int main(int argc, const char* argv[]) {
    init_vm();

    Chunk chunk;
    init_chunk(&chunk);

    int constant = add_constant(&chunk, 1);
    write_chunk(&chunk, OP_CONSTANT, 123);
    write_chunk(&chunk, constant, 123);

    constant = add_constant(&chunk, 2);
    write_chunk(&chunk, OP_CONSTANT, 123);
    write_chunk(&chunk, constant, 123);

    write_chunk(&chunk, OP_MULTIPLY, 123);

    constant = add_constant(&chunk, 3);
    write_chunk(&chunk, OP_CONSTANT, 123);
    write_chunk(&chunk, constant, 123);

    write_chunk(&chunk, OP_ADD, 123);
    write_chunk(&chunk, OP_NEGATE, 123);

    write_chunk(&chunk, OP_RETURN, 123);

    disasseble_chunk(&chunk, "test chunk");

    interpret(&chunk);
    free_vm();

    free_chunk(&chunk);

    return 0;
}