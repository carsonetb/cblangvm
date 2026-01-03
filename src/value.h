#ifndef CBLANGVM_VALUE_H
#define CBLANGVM_VALUE_H

#include "common.h"

#define BOOL_VAL(value)   ((Value)(VAL_BOOL, {.boolean = value}))
#define FLOAT_VAL(value)  ((Value)(VAL_FLOAT, {.floating = value}))
#define INT_VAL(value)    ((Value)(VAL_INT, {.integer = value}))

#define AS_BOOL(value)    ((value).as.boolean)
#define AS_FLOAT(value)   ((value).as.floating)
#define AS_INT(value)     ((value).as.integer)

#define IS_BOOL(value)    ((value).type == VAL_BOOL)
#define IS_FLOAT(value)   ((value).type == VAL_FLOAT)
#define IS_INT(value)     ((value).type == VAL_INT)

typedef enum {
    VAL_BOOL,
    VAL_INT,
    VAL_FLOAT
} ValueType;

typedef struct {
    ValueType type;
    union {
        bool boolean;
        float floating;
        int integer;
    } as;
} Value;

typedef struct {
    int capacity;
    int count;
    Value* values;
} ValueArray;

void init_value_array(ValueArray* array);
void push_value_array(ValueArray* array, Value value);
void free_value_array(ValueArray* array);
void print_value(Value value);
Value get_value_array_back(ValueArray* array);

#endif // CBLANGVM_VALUE_H