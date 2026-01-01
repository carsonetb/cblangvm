import sys

from interpreter import interpret

def read_file(path: str) -> str:
    file = open(path, "r")
    out = file.read()
    file.close()
    return out

def run_file(path: str) -> None:
    source = read_file(path)
    interpret(source)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        run_file(sys.argv[1])