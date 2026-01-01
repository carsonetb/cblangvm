from enum import Enum, auto

from attr import dataclass
from numpy import array, uint8

from compiler.compiler import compile_source

@dataclass
class LinesGroup:
    num: int
    line: int
    instruction_range_begin: int
    instruction_range_end: int

class Chunk:
    def __init__(self) -> None:
        self.code: list[uint8] = []
        self.lines: list[LinesGroup] = []

    def write(self, byte: uint8, line: int) -> None:
        self.code.append(byte)
        
        if len(self.lines) == 0 or self.lines[-1].line != line:
            self.lines.append(LinesGroup(1, line, len(self.code) - 1, len(self.code) - 1))
        else:
            self.lines[-1].num += 1
            self.lines[-1].instruction_range_end = len(self.code) - 1
    
    def to_bytes(self) -> bytes:
        return array(self.code).tobytes()

class InterpretResult(Enum):
    OK = auto()
    COMPILE_ERROR = auto()
    RUNTIME_ERROR = auto()

def interpret(source: str) -> InterpretResult:
    chunk, success = compile_source(source)

    if not success:
        return InterpretResult.COMPILE_ERROR
    
    # SAVE TO FILE AND INVOKE C RUNTIME

    return InterpretResult.OK