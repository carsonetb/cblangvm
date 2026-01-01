from enum import Enum, auto
from attr import dataclass

class TokenType(Enum):
    # Single character
    LEFT_PAREN = auto();   RIGHT_PAREN = auto();
    LEFT_BRACKET = auto(); RIGHT_BRACKET = auto();
    LEFT_CURLY = auto();   RIGHT_CURLY = auto();
    LEFT_ANGLE = auto();   RIGHT_ANGLE = auto();
    COMMA = auto(); DOT = auto(); 
    MINUS = auto(); PLUS = auto();
    SLASH = auto(); STAR = auto();
    SEMICOLON = auto(); COLON = auto();
    BANG = auto(); EQUAL = auto();
    CARET = auto(); MODULO = auto(); PIPE = auto();

    # Two character
    BANG_EQUAL = auto(); EQUAL_EQUAL = auto();
    GREATER_EQUAL = auto(); LESS_EQUAL = auto();
    STAR_STAR = auto(); RETURN = auto(); 
    PLUS_EQUAL = auto(); MINUS_EQUAL = auto();
    STAR_EQUAL = auto(); STAR_STAR_EQUAL = auto(); SLASH_EQUAL = auto();
    CARET_EQUAL = auto(); MODULO_EQUAL = auto(); PIPE_EQUAL = auto();
    PIPE_PIPE = auto(); AND_AND = auto();

    # Literals
    IDENTIFIER = auto(); STRING = auto(); CHARACTER = auto();
    FLOAT = auto(); INT = auto();

    # Keywords
    CLASS_KW = auto(); SCOPE_KW = auto();
    TRUE_KW = auto(); FALSE_KW = auto();
    PRIVATE_KW = auto(); STATIC_KW = auto(); CONST_KW = auto();
    OPERATOR_KW = auto(); CAST_KW = auto();
    SUPER_KW = auto(); RETURN_KW = auto(); IMPORT_KW = auto();
    IF_KW = auto(); ELIF_KW = auto(); ELSE_KW = auto();
    FOR_KW = auto(); WHILE_KW = auto(); 
    IN_KW = auto(); CONTINUE_KW = auto(); BREAK_KW = auto();

    ERROR = auto(); EOF = auto()
 
@dataclass
class Token:
    token_type: TokenType
    start_ind: int 
    length: int
    raw: str
    line: int

class Scanner:
    KEYWORDS = {
        "class": TokenType.CLASS_KW,
        "scope": TokenType.SCOPE_KW,
        "true": TokenType.TRUE_KW,
        "false": TokenType.FALSE_KW,
        "private": TokenType.PRIVATE_KW,
        "static": TokenType.STATIC_KW,
        "const": TokenType.CONST_KW,
        "operator": TokenType.OPERATOR_KW,
        "cast": TokenType.CAST_KW,
        "super": TokenType.SUPER_KW,
        "return": TokenType.RETURN_KW,
        "import": TokenType.IMPORT_KW,
        "if": TokenType.IF_KW,
        "elif": TokenType.ELIF_KW,
        "else": TokenType.ELSE_KW,
        "in": TokenType.IN_KW,
        "continue": TokenType.CONTINUE_KW,
        "break": TokenType.BREAK_KW,
    }

    def __init__(self, source: str) -> None:
        self.start_ind: int = 0
        self.current_ind: int = 0
        self.line: int = 1
        self.source = source
    
    def _get_current_raw(self) -> str:
        return self.source[self.start_ind : (self.current_ind + 1)]

    def _make_token(self, token_type: TokenType, raw: str = "") -> Token:
        return Token(token_type, self.start_ind, self.current_ind - self.start_ind, raw if raw else self._get_current_raw(), self.line)

    def _error_token(self, message: str) -> Token:
        return Token(TokenType.ERROR, -1, -1, message, self.line)

    def _advance(self) -> str:
        self.current_ind += 1
        return self.source[self.current_ind - 1]
    
    def _match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self._peek() != expected:
            return False
        self.current_ind += 1
        return True
    
    def _peek(self, amount: int = 0) -> str:
        if self.current_ind + amount >= len(self.source):
            return '\0'
        return self.source[self.current_ind + amount]
    
    def _is_alpha(self, c: str) -> bool:
        return c.isalpha() or c == '_'

    def _string(self) -> Token:
        while self._peek() != '"' and not self.is_at_end():
            if self._peek() == '\n':
                self.line += 1
            self._advance()
        
        if self.is_at_end():
            return self._error_token("Unterminated string.")
        
        self._advance()
        return self._make_token(TokenType.STRING)
    
    def _number(self) -> Token:
        while self._peek().isdigit():
            self._advance()
        
        if self._peek() == '.' and self._peek(1).isdigit():
            self._advance()

            while self._peek().isdigit():
                self._advance()
            
            return self._make_token(TokenType.FLOAT)
        else:
            return self._make_token(TokenType.INT)
    
    def _identifier(self) -> Token:
        while self._is_alpha(self._peek()) or self._peek().isdigit():
            self._advance()
        raw = self._get_current_raw()
        if self.KEYWORDS.get(raw):
            return self._make_token(self.KEYWORDS[raw])
        return self._make_token(TokenType.IDENTIFIER)

    def _skip_whitespace(self) -> None:
        while True:
            c = self._peek()
            match c:
                case ' ': self._advance()
                case '\r': self._advance()
                case '\t': self._advance()
                case '\n':
                    self.line += 1
                    self._advance()
                case '/':
                    if self._peek(1) == '/':
                        while (self._peek() != '\n' and not self.is_at_end()):
                            self._advance()
                    else:
                        return
                case _:
                    return
    
    def scan_token(self) -> Token:
        self._skip_whitespace()
        self.start_ind = self.current_ind

        if self.is_at_end():
            return self._make_token(TokenType.EOF)
        
        c = self._advance()

        if self._is_alpha(c):
            return self._identifier()
        if c.isdigit():
            return self._number()        

        match c:
            case '(': return self._make_token(TokenType.LEFT_PAREN)
            case ')': return self._make_token(TokenType.RIGHT_PAREN)
            case '{': return self._make_token(TokenType.LEFT_CURLY)
            case '}': return self._make_token(TokenType.RIGHT_CURLY)
            case '[': return self._make_token(TokenType.LEFT_BRACKET)
            case ']': return self._make_token(TokenType.RIGHT_BRACKET)
            case ';': return self._make_token(TokenType.SEMICOLON)
            case ',': return self._make_token(TokenType.COMMA)
            case '.': return self._make_token(TokenType.DOT)
            case '^': return self._make_token(TokenType.CARET_EQUAL if self._match('=') else TokenType.CARET)
            case '%': return self._make_token(TokenType.MODULO if self._match('=') else TokenType.MODULO)
            case '|': 
                if self._match('|'):
                    return self._make_token(TokenType.PIPE_PIPE)
                if self._match('='):
                    return self._make_token(TokenType.PIPE_EQUAL)
                return self._make_token(TokenType.PIPE)
            case '-': 
                if self._match('>'):
                    return self._make_token(TokenType.RETURN)
                if self._match('='):
                    return self._make_token(TokenType.MINUS_EQUAL)
                else:
                    return self._make_token(TokenType.MINUS)
            case '+': return self._make_token(TokenType.PLUS_EQUAL if self._match('=') else TokenType.PLUS)
            case '/': return self._make_token(TokenType.SLASH_EQUAL if self._match('=') else TokenType.SLASH)
            case '*': 
                if self._match('*'):
                    if self._match('='):
                        return self._make_token(TokenType.STAR_STAR_EQUAL)
                    return self._make_token(TokenType.STAR_STAR)
                elif self._match('='):
                    return self._make_token(TokenType.STAR_EQUAL)
                return self._make_token(TokenType.STAR)
            case '!': return self._make_token(TokenType.BANG_EQUAL if self._match('=') else TokenType.BANG)
            case '=': return self._make_token(TokenType.EQUAL_EQUAL if self._match('=') else TokenType.EQUAL)
            case '<': return self._make_token(TokenType.LESS_EQUAL if self._match('=') else TokenType.LEFT_ANGLE)
            case '>': return self._make_token(TokenType.BANG_EQUAL if self._match('=') else TokenType.RIGHT_ANGLE)
            case "'": 
                char = self._advance()
                self._advance()
                self._make_token(TokenType.CHARACTER, char)
            case _: pass

        return self._error_token("Unexpected character.")
    
    def is_at_end(self) -> bool:
        return self.current_ind == len(self.source)