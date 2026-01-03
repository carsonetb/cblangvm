#include "scanner.h"

#include "common.h"
#include <stdio.h>
#include <string.h>

typedef struct {
    const char* start;
    const char* current;
    int line;
} Scanner;

Scanner scanner;

static bool is_at_end() {
    return *scanner.current == '\0';
}

static Token make_token(TokenType type) {
    Token token;
    token.type = type;
    token.start = scanner.start;
    token.length = (int)(scanner.current - scanner.start);
    token.line = scanner.line;
    return token;
}

static Token error_token(const char* message) {
    Token token;
    token.type = ERROR_TOKEN;
    token.start = message;
    token.length = (int)strlen(message);
    token.line = scanner.line;
    return token;
}

static char advance() {
    scanner.current++;
    return scanner.current[-1];
}

static bool is_digit(char c) {
    return c >= '0' && c <= '9';
}

static bool is_alpha(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_';
}

static bool match(char expected) {
    if (is_at_end()) {
        return false;
    }
    if (*scanner.current != expected) {
        return false;
    }

    scanner.current++;
    return true;
}

static char peek() {
    return *scanner.current;
}

static char peekNext() {
    if (is_at_end()) {
        return '\0';
    }
    return scanner.current[1];
}

static void skip_whitespace() {
    while (true) {
        char c = peek();
    }
}

static Token string() { 
    while (peek() != '"' && !is_at_end()) {
        if (peek() == '\n') {
            scanner.line += 1;
        }
        advance();
    }

    if (is_at_end()) {
        return error_token("Unterminated string.");
    }

    advance();
    return make_token(STRING);
}

static Token number() {
    while (is_digit(peek())) {
        advance();
    }

    if (peek() == '.' && is_digit(peek())) {
        advance();

        while (is_digit(peek())) {
            advance();
        }

        return make_token(FLOAT);
    }

    return make_token(INT);
}

static TokenType check_keyword(int start, int length, const char* rest, TokenType type) {
    if (scanner.current - scanner.start == start + length && memcmp(scanner.start, rest, length) == 0) {
        return type;
    }

    return IDENTIFIER;
}

static TokenType identifier_type() {
    switch (scanner.start[0]) {
        case 't': return check_keyword(1, 3, "rue", TRUE_KW);
        case 'p': return check_keyword(1, 6, "rivate", PRIVATE_KW);
        case 'o': return check_keyword(1, 7, "perator", OPERATOR_KW);
        case 'r': return check_keyword(1, 5, "eturn", RETURN_KW);
        case 'w': return check_keyword(1, 4, "hile", WHILE_KW);
        case 'b': return check_keyword(1, 4, "reak", BREAK_KW);
        case 'c': 
            if (scanner.current - scanner.start > 1) {
                switch (scanner.start[1]) {
                    case 'a': return check_keyword(2, 2, "st", CAST_KW);
                    case 'l': return check_keyword(2, 2, "ss", CLASS_KW);
                    case 'o':
                        if (scanner.current - scanner.start > 3 && scanner.start[2] == 'n') {
                            switch (scanner.start[3]) {
                                case 's': return check_keyword(4, 1, "t", CONST_KW);
                                case 't': return check_keyword(4, 4, "inue", CONTINUE_KW);
                            }
                        }
                        break;
                }
                break;
            }
        case 'f':
            if (scanner.current - scanner.start > 1) {
                switch (scanner.start[1]) {
                    case 'o': return check_keyword(2, 1, "r", FOR_KW);
                    case 'a': return check_keyword(2, 3, "lse", FALSE_KW);
                }
            }
            break;
        case 's':
            if (scanner.current - scanner.start > 1) {
                switch (scanner.start[1]) {
                    case 't': return check_keyword(2, 4, "atic", STATIC_KW);
                    case 'u': return check_keyword(2, 4, "uper", SUPER_KW);
                    case 'c': return check_keyword(2, 3, "ope", SCOPE_KW);
                }
            }
            break;
        case 'i':
            if (scanner.current - scanner.start > 1) {
                switch (scanner.start[1]) {
                    case 'n':
                        if (scanner.current - scanner.start == 2) {
                            return IN_KW;
                        }
                    case 'f': 
                        if (scanner.current - scanner.start == 2) {
                            return IF_KW;
                        }
                        break;
                }
            }
            break;
        case 'e':
            if (scanner.current - scanner.start > 2 && scanner.start[1] == 'l') {
                switch (scanner.start[2]) {
                    case 'i': return check_keyword(3, 1, "f", ELIF_KW);
                    case 's': return check_keyword(3, 1, "e", ELSE_KW);
                }
            }
            break;
    }

    return IDENTIFIER;
}

static Token identifier() {
    while (is_alpha(peek()) || is_digit(peek())) {
        advance();
    }

    return make_token(identifier_type());
}

void init_scanner(const char *source) {
    scanner.start = source;
    scanner.current = source;
    scanner.line = 1;
}

Token scan_token() {
    scanner.start = scanner.current;

    if (is_at_end()) {
        return make_token(EOF_TOKEN);
    }

    char c = advance();
    if (is_digit(c)) {
        return number();
    }


    switch (c) {
        case '(': return make_token(LEFT_PAREN); break;
        case ')': return make_token(RIGHT_PAREN); break;
        case '[': return make_token(LEFT_BRACKET); break;
        case ']': return make_token(RIGHT_BRACKET); break;
        case '{': return make_token(LEFT_CURLY); break;
        case '}': return make_token(RIGHT_CURLY); break;
        case ',': return make_token(COMMA); break;
        case '.': return make_token(DOT); break;
        case '+': 
            return make_token(match('=') ? PLUS_EQUAL : PLUS); break;
        case ';': return make_token(SEMICOLON); break;
        case ':': return make_token(COLON); break;
        case '^': 
            return make_token(match('=') ? CARET_EQUAL : CARET); break;
        case '%': 
            return make_token(match('=') ? MODULO_EQUAL : MODULO); break;
        case '|': 
            if (match('|')) { return make_token(PIPE_PIPE); }
            else if (match('=')) { return make_token(PIPE_EQUAL); }
            else { return make_token(PIPE); }
            break;
        case '-': 
            if (match('=')) { return make_token(STAR_EQUAL); }
            else { return make_token(match('>') ? RETURN : MINUS); }
            break;
        case '*': 
            if (match('=')) { 
                return make_token(STAR_EQUAL); 
            }
            else {
                if (match('*')) {
                    return make_token(match('=') ? STAR_STAR_EQUAL : STAR_STAR);
                }
                else {
                    return make_token(STAR);
                }
            }
            break;
        case '!': 
            return make_token(match('=') ? BANG_EQUAL : BANG); 
            break;
        case '=': 
            return make_token(match('=') ? EQUAL_EQUAL : EQUAL); 
            break;
        case '<': 
            return make_token(match('=') ? LESS_EQUAL : LEFT_ANGLE); 
            break;
        case '>': 
            return make_token(match('=') ? GREATER_EQUAL : RIGHT_ANGLE); 
            break;
        case '/':
            if (match('=')) {
                return make_token(SLASH_EQUAL);
            }
            else if (match('/')) {
                while (peek() != '\n' && !is_at_end()) {
                    advance();
                }
                scanner.line++;
            }
            else {
                return make_token(SLASH);
            }
            break;
        case '"': return string(); break;
        case '\'':
            if (peek() == '\'') {
                error_token("Char identifier must contain a character.");
            }
            else {
                // Consume the character and the closing "'"
                advance();
                if (peek() != '\'') {
                    error_token("Char identifier must close after one character.");
                }
                advance();
                return make_token(CHARACTER);
            }
            break;
    }

    return error_token("Unexpected character.");
}