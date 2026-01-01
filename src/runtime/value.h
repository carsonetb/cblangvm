#ifndef CBLANGVM_VALUE_H
#define CBLANGVM_VALUE_H

typedef double Value;

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