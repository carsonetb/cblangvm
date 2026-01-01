from __future__ import annotations
from copy import copy
from typing import Callable
from attr import dataclass

from scanner import Scanner, Token, TokenType


@dataclass
class Templated:
    name: Token
    templates: list[Templated]

@dataclass
class Statement:
    start_index: int
    end_index: int
    tokens: list[Token]

@dataclass
class Import(Statement):
    import_path: list[Token]

@dataclass
class Return(Statement):
    expression: Expression

@dataclass 
class Continue(Statement):
    pass

@dataclass
class Break(Statement):
    pass

@dataclass 
class SetVar(Statement):
    name: Token
    val: Expression

@dataclass 
class CreateVar(Statement):
    var_type: Templated
    name: Token
    val: Expression

@dataclass 
class If(Statement):
    check: Expression
    following: Elif | Else | None
    run: list[Statement]

@dataclass 
class Elif(If):
    pass

@dataclass 
class Else(Statement):
    run: list[Statement]

@dataclass
class While(Statement):
    check: Expression
    run: list[Statement]

@dataclass
class For(Statement):
    looper: tuple[Templated, Token]
    looped: Expression
    run: list[Statement]

@dataclass
class Declaration(Statement):
    pass

@dataclass 
class MemberFlags:
    is_private: bool
    is_static: bool
    is_const: bool

@dataclass
class FunctionFlags:
    is_cast: bool
    is_operator: bool

@dataclass
class Function(Declaration):
    name: Templated
    params: list[tuple[Templated, Token]]
    returns: Templated | None
    body: list[Statement]
    member_flags: MemberFlags
    function_flags: FunctionFlags

@dataclass
class Variable(Declaration):
    var_type: Templated
    name: Token
    value: Expression
    member_flags: MemberFlags

@dataclass
class Class(Declaration):
    name: Templated
    inherits: list[Templated]
    params: list[tuple[Templated, Token]]
    members: list[Declaration]

@dataclass
class Expression(Statement):
    pass

@dataclass
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression

@dataclass
class Unary(Expression):
    operator: Token
    right: Expression

@dataclass
class Grouping(Expression):
    expression: Expression

@dataclass
class Literal(Expression):
    literal: Token

@dataclass
class Scope(Expression):
    statements: list[Statement]

@dataclass
class Array(Expression):
    items: list[Expression]

@dataclass
class Accessible(Expression):
    access: Accessible | None

@dataclass
class Call(Accessible):
    name: Templated
    args: list[Expression]

@dataclass
class Var(Accessible):
    name: Token

@dataclass 
class ParsedProgram:
    internal_declarations: list[Import | Function | Class]

class ParseException(Exception):
    pass

class AstGenerator:
    def __init__(self, scanner: Scanner) -> None:
        self.scanner = scanner
        self.previous: Token | None = None
        self.current = scanner.scan_token()
        self.had_error = False
        self.panic_mode = False
        self.token_history: list[list[Token]] = []
    
    def generate(self) -> ParsedProgram:
        declarations: list[Import | Function | Class] = []

        while True:
            if self._match(TokenType.EOF):
                break

            if self._match(TokenType.IMPORT_KW):
                declarations.append(self._import())
            if self._check(TokenType.PRIVATE_KW, TokenType.STATIC_KW, TokenType.CONST_KW, TokenType.OPERATOR_KW, TokenType.CAST_KW, TokenType.SCOPE_KW):
                member_flags = MemberFlags(False, False, False)
                function_flags = FunctionFlags(False, False)
                while not self._check(TokenType.SCOPE_KW):
                    if self._match(TokenType.PRIVATE_KW):
                        member_flags.is_private = True
                    elif self._match(TokenType.STATIC_KW):
                        member_flags.is_static = True
                    elif self._match(TokenType.CONST_KW):
                        member_flags.is_const = True
                    elif self._match(TokenType.OPERATOR_KW):
                        function_flags.is_operator = True
                    elif self._match(TokenType.CAST_KW):
                        function_flags.is_cast = True
                    self._error_at_current("Expected 'scope', 'private', 'static', 'const', 'operator', or 'cast' keyword.")
                declarations.append(self._function(member_flags, function_flags))
        
        return ParsedProgram(declarations)
    
    def _import(self) -> Import:
        self.token_history.append([])

        modules_list: list[Token] = []
        modules_list.append(self._consume(TokenType.IDENTIFIER, "Expected identifier after 'import' keyword."))
        while self._match(TokenType.DOT):
            modules_list.append(self._consume(TokenType.IDENTIFIER, "Expected identifier after '.' in import statement."))

        self._consume(TokenType.SEMICOLON, "Expected ';' after import statement.")

        start, end = self._statement_start_end()
        return Import(start, end, self.token_history.pop(), modules_list)

    def _variable(self, member_flags: MemberFlags) -> Variable:
        self.token_history.append([])

        var_type = self._templated("variable declaration")
        name = self._consume(TokenType.IDENTIFIER, "Expected identifier after variable type.")
        self._consume(TokenType.EQUAL, "Expected '=' after variable name.")
        expr = self._expression()
        
        start, end = self._statement_start_end()
        return Variable(start, end, self.token_history.pop(), var_type, name, expr, member_flags, )
    
    def _function(self, member_flags: MemberFlags, function_flags: FunctionFlags) -> Function:
        self.token_history.append([])
        
        self._consume(TokenType.SCOPE_KW, "Expect 'scope' keyword.")
        name = self._templated_definition("'scope' keyword")
        params: list[tuple[Templated, Token]] = []
        if self._match(TokenType.LEFT_PAREN):
            params = self._param_definition()
        returns: Templated | None = None
        if self._match(TokenType.RETURN):
            returns = self._templated("'->'")
        self._consume(TokenType.EQUAL, "Expected '=' after function definition.")
        body = self._scope()

        start, end = self._statement_start_end()
        return Function(
            start, end, self.token_history.pop(), 
            name, params, returns, body, 
            member_flags, function_flags
        )
    
    def _class(self) -> Class:
        self.token_history.append([])

        name = self._templated_definition("'class' keyword")
        inherits: list[Templated] = []
        if self._match(TokenType.COLON):
            while True:
                inherits.append(self._templated("inherits"))
                if self._match(TokenType.COMMA):
                    continue
                break
        params: list[tuple[Templated, Token]] = []
        if self._match(TokenType.LEFT_PAREN):
            params = self._param_definition()
        self._consume(TokenType.EQUAL, "Expected '=' after class definition.")
        members = self._members()

        start, end = self._statement_start_end()
        return Class(
            start, end, self.token_history.pop(), 
            name, inherits, params, members
        )

    def _expression(self) -> Expression:
        return self._logic_or()
    
    def _logic_or(self) -> Expression:
        self.token_history.append([])

        out = self._logic_and()
        while self._match(TokenType.PIPE_PIPE):
            out = self._binary_right_side(out, self._logic_and)
        
        self.token_history.pop()
        return out
    
    def _logic_and(self) -> Expression:
        self.token_history.append([])

        out = self._equality()
        while self._match(TokenType.AND_AND):
            out = self._binary_right_side(out, self._equality)
        
        self.token_history.pop()
        return out
    
    def _equality(self) -> Expression:
        self.token_history.append([])

        out = self._comparison()
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            out = self._binary_right_side(out, self._comparison)
        
        self.token_history.pop()
        return out
    
    def _comparison(self) -> Expression:
        self.token_history.append([])

        out = self._term()
        while self._match(TokenType.LEFT_ANGLE, TokenType.LESS_EQUAL, TokenType.RIGHT_ANGLE, TokenType.GREATER_EQUAL):
            out = self._binary_right_side(out, self._term)
        
        self.token_history.pop()
        return out
    
    def _term(self) -> Expression:
        self.token_history.append([])

        out = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            out = self._binary_right_side(out, self._factor)
        
        self.token_history.pop()
        return out

    def _factor(self) -> Expression:
        self.token_history.append([])

        out = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH):
            out = self._binary_right_side(out, self._unary)
        
        self.token_history.pop()
        return out

    def _unary(self) -> Expression:
        if self._match(TokenType.BANG, TokenType.MINUS):
            self.token_history.append([])
            assert not self.previous is None
            start, end = self._statement_start_end()
            oper = self.previous
            right = self._unary()
            return Unary(start, end, self.token_history.pop(), oper, right)

        return self._primary()
    
    def _primary(self) -> Expression:
        if self._match(TokenType.TRUE_KW, TokenType.FALSE_KW, TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.CHARACTER):
            assert not self.previous is None
            return Literal(self.previous.start_ind, self.previous.start_ind + self.previous.length, [self.previous], self.previous)
        
        if self._check(TokenType.IDENTIFIER):
            return self._function_or_variable()
        
        if self._check(TokenType.LEFT_CURLY):
            self.token_history.append([])
            statements = self._scope()
            start, end = self._statement_start_end()
            return Scope(start, end, self.token_history.pop(), statements)
        
        if self._match(TokenType.LEFT_PAREN):
            self.token_history.append([])
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression in grouping.")
            start, end = self._statement_start_end()
            return Grouping(start, end, self.token_history.pop(), expr)
        
        if self._match(TokenType.LEFT_BRACKET):
            self.token_history.append([])
            array_items: list[Expression] = []
            if not self._match(TokenType.RIGHT_BRACKET):
                array_items = self._expression_list()
            self._consume(TokenType.RIGHT_BRACKET, "Expected ']'.")

            start, end = self._statement_start_end()
            return Array(start, end, self.token_history.pop(), array_items)
        
        raise self._error_at_current("Expected literal, identifier, '{', '(', or '['.")

    def _function_or_variable(self) -> Accessible:
        self.token_history.append([])

        name = self._consume(TokenType.IDENTIFIER, "")
        if self._check(TokenType.LEFT_ANGLE, TokenType.LEFT_PAREN):
            templates: list[Templated] = []
            if self._match(TokenType.LEFT_ANGLE):
                while True:
                    templates.append(self._templated("templated argument"))
                    if self._match(TokenType.COMMA):
                        continue
                    self._consume(TokenType.RIGHT_ANGLE, "Expected '>' or ',' after templated argument.")
                    break
            templated_name = Templated(name, templates)
            self._consume(TokenType.LEFT_PAREN, "Expected '(' after templated function name.")
            arguments: list[Expression] = []
            if not self._match(TokenType.RIGHT_PAREN):
                arguments = self._expression_list()
            
            access: Accessible | None = None
            if self._match(TokenType.DOT):
                access = self._function_or_variable()
            
            start, end = self._statement_start_end()
            return Call(start, end, self.token_history.pop(), access, templated_name, arguments)
        
        access: Accessible | None = None
        if self._match(TokenType.DOT):
            access = self._function_or_variable()
        
        start, end = self._statement_start_end()
        return Var(start, end, self.token_history.pop(), access, name)
    
    def _expression_list(self) -> list[Expression]:
        out: list[Expression] = []
        while True:
            out.append(self._expression())
            if self._match(TokenType.COMMA):
                continue
            break
        return out
    
    def _binary_right_side(self, out: Expression, right_function: Callable[[], Expression]) -> Expression:
        assert not self.previous is None
        start, end = self._statement_start_end()
        oper = self.previous
        right = right_function()
        return Binary(start, end, copy(self.token_history[-1]), out, oper, right)
    
    def _members(self) -> list[Declaration]:
        out: list[Declaration] = []

        while not self._match(TokenType.RIGHT_PAREN):
            if self._match(TokenType.CLASS_KW):
                out.append(self._class())
                self._consume(TokenType.COMMA, "Expected ',' after class declaration.")
                continue

            member_flags = MemberFlags(False, False, False)
            function_flags = FunctionFlags(False, False)
            is_function = False
            while True:
                found_qualifier = True
                if self._match(TokenType.PRIVATE_KW):
                    member_flags.is_private = True
                elif self._match(TokenType.STATIC_KW):
                    member_flags.is_static = True
                elif self._match(TokenType.CONST_KW):
                    member_flags.is_const = True
                elif self._match(TokenType.OPERATOR_KW):
                    function_flags.is_operator = True
                elif self._match(TokenType.CAST_KW):
                    function_flags.is_cast = True
                else:
                    found_qualifier = False

                if self._check(TokenType.SCOPE_KW):
                    is_function = True
                    break
                elif self._check(TokenType.IDENTIFIER):
                    break
                elif not found_qualifier:
                    self._error_at_current("Expected 'scope', 'private', 'static', 'const', 'operator', or 'cast' keyword, or identifier.")
            
            if is_function:
                out.append(self._function(member_flags, function_flags))
                self._consume(TokenType.COMMA, "Expected ',' after function declaration.")
            else:
                out.append(self._variable(member_flags))
                self._consume(TokenType.COMMA, "expected ',' after variable declaration.")

        return out

    def _scope(self) -> list[Statement]:
        self._consume(TokenType.LEFT_CURLY, "")

        out: list[Statement] = []

        while not self._match(TokenType.RIGHT_CURLY):
            out.append(self._statement())

        return out
    
    def _statement(self) -> Statement:
        self.token_history.append([])
        
        if self._match(TokenType.IDENTIFIER):
            assert not self.previous is None
            name = self.previous
            if self._check(TokenType.EQUAL):
                val = self._expression()
                self._consume(TokenType.SEMICOLON, "Expected ';' after setting a variable.")

                start, end = self._statement_start_end()
                return SetVar(start, end, self.token_history.pop(), name, val)
            
            templated = Templated(name, self._templated_list())
            name = self._consume(TokenType.IDENTIFIER, "Expected identifier after variable type.")
            self._consume(TokenType.EQUAL, "Expected '=' after variable name.")
            expr = self._expression()
            self._consume(TokenType.SEMICOLON, "Expected ';' after creating a variable.")

            start, end = self._statement_start_end()
            return CreateVar(start, end, self.token_history.pop(), templated, name, expr)

        if self._match(TokenType.RETURN):
            expr = self._expression()
            self._consume(TokenType.SEMICOLON, "Expected ';' after return statement.")
            start, end = self._statement_start_end()
            return Return(start, end, self.token_history.pop(), expr)
        
        if self._match(TokenType.BREAK_KW):
            self._consume(TokenType.SEMICOLON, "Expected ';' after 'break' statement.")
            start, end = self._statement_start_end()
            return Break(start, end, self.token_history.pop())
        
        if self._match(TokenType.CONTINUE_KW):
            self._consume(TokenType.SEMICOLON, "Expected ';' after 'continue' statement.")
            start, end = self._statement_start_end()
            return Continue(start, end, self.token_history.pop())
        
        if self._match(TokenType.IF_KW):
            return self._if_stmnt()
        
        if self._match(TokenType.WHILE_KW):
            self.token_history.append([])

            self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'while' keyword.")
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression inside of 'while' statement.")
            body = self._scope()
            
            start, end = self._statement_start_end()
            return While(start, end, self.token_history.pop(), expr, body)
        
        if self._match(TokenType.FOR_KW):
            self.token_history.append([])

            self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'for' keyword.")
            looper_type = self._templated("for statement")
            looper_name = self._consume(TokenType.IDENTIFIER, "Expected looper name after looper type in 'for' statement.")
            self._consume(TokenType.IN_KW, "Expected 'in' after looper name and type.")
            looped = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after looped expression in 'for' statement.")
            body = self._scope()

            start, end = self._statement_start_end()
            return For(start, end, self.token_history.pop(), (looper_type, looper_name), looped, body)
        
        return self._expression()
    
    def _if_stmnt(self) -> If:
        self.token_history.append([])

        self._consume(TokenType.LEFT_PAREN, "Expected '(' after keyword.")
        expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression inside of statement.")
        body = self._scope()

        following: Elif | Else | None = None
        if self._match(TokenType.ELIF_KW):
            following = self._elif_stmnt()
        elif self._match(TokenType.ELSE_KW):
            following = self._else_stmnt()

        start, end = self._statement_start_end()
        return If(start, end, self.token_history.pop(), expr, following, body)

    def _elif_stmnt(self) -> Elif:
        as_if = self._if_stmnt()
        return Elif(as_if.start_index, as_if.end_index, as_if.tokens, as_if.check, as_if.following, as_if.run)

    def _else_stmnt(self) -> Else:
        self.token_history.append([])
        body = self._scope()
        start, end = self._statement_start_end()
        return Else(start, end, self.token_history.pop(), body)
    
    def _templated(self, after: str) -> Templated:
        name = self._consume(TokenType.IDENTIFIER, f"Expected templated type (or plain identifier) after {after}.")
        return Templated(name, self._templated_list())

    def _templated_definition(self, after: str) -> Templated:
        name = self._consume(TokenType.IDENTIFIER, f"Expected templated type (or plain identifier) after {after}.")
        templates: list[Templated] = []
        if self._match(TokenType.LEFT_ANGLE):
            while True:
                templates.append(Templated(self._consume(TokenType.IDENTIFIER, "Expected identifier."), []))
                if self._match(TokenType.COMMA):
                    continue
                self._consume(TokenType.RIGHT_ANGLE, "Expected '>' or ',' after templated argument.")
                break
        return Templated(name, templates)
    
    def _templated_list(self) -> list[Templated]:
        out: list[Templated] = []

        if self._match(TokenType.LEFT_ANGLE):
            while True:
                out.append(self._templated("templated argument"))
                if self._match(TokenType.COMMA):
                    continue
                self._consume(TokenType.RIGHT_ANGLE, "Expected '>' or ',' after templated argument.")
                break
        
        return out
    
    def _param_definition(self) -> list[tuple[Templated, Token]]:
        out: list[tuple[Templated, Token]] = []
        if self._match(TokenType.RIGHT_PAREN):
            return out
        
        while True:
            out.append((self._templated("parameter definition argument"), self._consume(TokenType.IDENTIFIER, "Expected identifier after type.")))
            if self._match(TokenType.COMMA):
                continue
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' or ',' after parameter definition.")
            break

        return out
    
    def _statement_start_end(self) -> tuple[int, int]:
        first_token = self.token_history[-1][0]
        last_token = self.token_history[-1][-1]
        return (first_token.start_ind, last_token.start_ind + last_token.length)
    
    def _match(self, *tokens: TokenType) -> bool:
        if self._check(*tokens):
            self._advance()
            return True
        return False

    def _check(self, *tokens: TokenType) -> bool:
        for token in tokens:
            if token == self.current.token_type:
                return True
        return False
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self.current.token_type == token_type:
            self._advance()
            return self.current
        
        raise self._error_at_current(message)
    
    def _advance(self) -> None:
        self.previous = self.current

        while True:
            self.current = self.scanner.scan_token()
            if self.current.token_type != TokenType.ERROR:
                break
            
            self._error_at_current(self.current.raw) # Error message is stored in the token raw.
        
        for tokens in self.token_history:
            tokens.append(self.current)
    
    def _error_at_current(self, message: str) -> ParseException:
        return self._error_at(self.current, message)
    
    def _error(self, message: str) -> ParseException:
        if not self.previous:
            print("(please report) Error at beginning of file.")
            return ParseException()
        
        return self._error_at(self.previous, message)
    
    def _error_at(self, token: Token, message: str) -> ParseException:
        self.panic_mode = True
        print(f"[line {token.line}] error ", end="")
        
        if token.token_type == TokenType.EOF:
            print("at end of file: ", end="")
        elif token.token_type == TokenType.ERROR:
            pass
        else:
            print(f"at '{token.raw}': ", end="")

        print(f": {message}")
        self.had_error = True
        return ParseException()
