# CblangVM

## Sample VSCode launch.json

```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "C/C++ Debug (gdb Launch)",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}/build/cblangvm",
            "args": [],
            "cwd": "${workspaceFolder}",
            "environment": [],
            "MIMode": "gdb",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ],
            "preLaunchTask": "C: Build project"
        }
    ]
}
```

## Sample VSCode tasks.json

```
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "C: Build project",
            "type": "shell",
            "command": "clang", // Or GCC I think will work.
            "args": [
                "-g",
                "-fsanitize=address,undefined",
                "main.c",
                "memory.c",
                "debug.c",
                "chunk.c",
                "value.c",
                "vm.c",
                "-o", "build/cblangvm"
            ],
            "options": {
                "cwd": "${workspaceFolder}"
            },
            "group": {
                "kind": "build",
                "isDefault": true
            }
        }
    ]
}
```