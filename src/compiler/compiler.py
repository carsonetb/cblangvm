from __future__ import annotations
from numpy import uint8

from ast_generator import AstGenerator
from interpreter import Chunk
from scanner import Scanner

class Compiler:
    def __init__(self) -> None:
        self.chunk = Chunk()
    
    def emit_byte(self, byte: uint8, line: int) -> None:
        self.chunk.write(byte, line)

def compile_source(source: str) -> tuple[Chunk | None, bool]:
    scanner = Scanner(source)

    ast_generator = AstGenerator(scanner)
    ast = ast_generator.generate()
    if ast_generator.had_error:
        return (None, False)
    
    return True