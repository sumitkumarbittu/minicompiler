from .lexer import TokenType, Token, Lexer
from .ast import *
from .util import Diagnostic, Severity

class Parser:
    def __init__(self, tokens: list[Token], file_path: str, diag_engine):
        self.tokens = tokens
        self.pos = 0
        self.file_path = file_path
        self.diag = diag_engine

    def peek(self, offset=0) -> Token:
        if self.pos + offset >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos + offset]

    def consume(self):
        t = self.peek()
        self.pos += 1
        return t

    def match(self, type: TokenType) -> bool:
        if self.peek().type == type:
            self.consume()
            return True
        return False

    def expect(self, type: TokenType, msg: str) -> Token:
        if self.peek().type == type:
            return self.consume()
        self._error(msg, self.peek())
        return self.tokens[-1] # fallback

    def parse(self) -> Module:
        funcs = []
        top_level_stmts = []
        
        while self.peek().type != TokenType.EOF:
            if self.peek().type == TokenType.NEWLINE:
                self.consume()
                continue
            
            if self.peek().type == TokenType.DEF:
                funcs.append(self.parse_function())
            else:
                # Top level statement
                stmt = self.parse_stmt()
                if stmt:
                    top_level_stmts.append(stmt)

        # Synthesize main if we have top-level code
        if top_level_stmts:
             main_func = FunctionDef(name="main", args=[], body=top_level_stmts, token=None)
             funcs.append(main_func)

        return Module(functions=funcs)

    def parse_function(self) -> FunctionDef:
        start_tok = self.expect(TokenType.DEF, "Expected 'def'")
        name_tok = self.expect(TokenType.IDENTIFIER, "Expected function name")
        self.expect(TokenType.LPAREN, "Expected '('")
        
        args = []
        if self.peek().type != TokenType.RPAREN:
            t = self.expect(TokenType.IDENTIFIER, "Expected argument name")
            args.append(t.value)
            while self.match(TokenType.COMMA):
                t = self.expect(TokenType.IDENTIFIER, "Expected argument name")
                args.append(t.value)
        
        self.expect(TokenType.RPAREN, "Expected ')'")
        self.expect(TokenType.COLON, "Expected ':'")
        self.expect(TokenType.NEWLINE, "Expected newline after def")
        
        body = self.parse_block()
        return FunctionDef(token=start_tok, name=name_tok.value, args=args, body=body)

    def parse_block(self) -> List[Stmt]:
        self.expect(TokenType.INDENT, "Expected indentation block")
        stmts = []
        while self.peek().type != TokenType.DEDENT and self.peek().type != TokenType.EOF:
            s = self.parse_stmt()
            if s:
                stmts.append(s)
        self.expect(TokenType.DEDENT, "Expected dedent")
        return stmts

    def parse_stmt(self) -> Optional[Stmt]:
        t = self.peek()
        
        if self.match(TokenType.IF):
            cond = self.parse_expr()
            self.expect(TokenType.COLON, "Expected ':'")
            self.expect(TokenType.NEWLINE, "Expected newline")
            then_block = self.parse_block()
            else_block = []
            if self.match(TokenType.ELSE):
                self.expect(TokenType.COLON, "Expected ':'")
                self.expect(TokenType.NEWLINE, "Expected newline")
                else_block = self.parse_block()
            return IfStmt(token=t, cond=cond, then_block=then_block, else_block=else_block)
            
        elif self.match(TokenType.WHILE):
            cond = self.parse_expr()
            self.expect(TokenType.COLON, "Expected ':'")
            self.expect(TokenType.NEWLINE, "Expected newline")
            body = self.parse_block()
            return WhileStmt(token=t, cond=cond, body=body)
            
        elif self.match(TokenType.RETURN):
            val = self.parse_expr()
            self.expect(TokenType.NEWLINE, "Expected newline")
            return ReturnStmt(token=t, value=val)
            
        elif t.type == TokenType.IDENTIFIER:
            # Check if assignment (x =) or call (x())
            if self.peek(1).type == TokenType.EQ:
                name_tok = self.consume()
                self.consume() # eat =
                val = self.parse_expr()
                self.expect(TokenType.NEWLINE, "Expected newline")
                return AssignStmt(token=t, name=name_tok.value, value=val)
            else:
                 # Must be expr stmt
                expr = self.parse_expr()
                self.expect(TokenType.NEWLINE, "Expected newline")
                if not isinstance(expr, CallExpr):
                     self._error("Statement must be assignment or call", t)
                return ExprStmt(token=t, expr=expr)
                
        elif t.type == TokenType.PRINT:
            # Special case for print which is statement-like in behavior but parse as CallExpr inside ExprStmt
            expr = self.parse_expr()
            self.expect(TokenType.NEWLINE, "Expected newline")
            return ExprStmt(token=t, expr=expr)
            
        elif t.type == TokenType.NEWLINE:
            self.consume()
            return None # Empty stmt
            
        else:
            self._error(f"Unexpected token {t.type}", t)
            self.consume()
            return None

    def parse_expr(self) -> Expr:
        return self.parse_compare()

    def parse_compare(self) -> Expr:
        lhs = self.parse_add_sub()
        if self.peek().type in [TokenType.EQEQ, TokenType.NEQ, TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE]:
            op_tok = self.consume()
            rhs = self.parse_add_sub()
            op_map = {
                TokenType.EQEQ: "==", TokenType.NEQ: "!=", 
                TokenType.LT: "<", TokenType.LTE: "<=",
                TokenType.GT: ">", TokenType.GTE: ">="
            }
            return BinOp(token=op_tok, left=lhs, right=rhs, op=op_map[op_tok.type])
        return lhs

    def parse_add_sub(self) -> Expr:
        lhs = self.parse_term()
        while self.peek().type in [TokenType.PLUS, TokenType.MINUS]:
            op_tok = self.consume()
            rhs = self.parse_term()
            op_char = "+" if op_tok.type == TokenType.PLUS else "-"
            lhs = BinOp(token=op_tok, left=lhs, right=rhs, op=op_char)
        return lhs

    def parse_term(self) -> Expr:
        lhs = self.parse_factor()
        while self.peek().type in [TokenType.STAR, TokenType.SLASH]:
            op_tok = self.consume()
            rhs = self.parse_factor()
            op_char = "*" if op_tok.type == TokenType.STAR else "/"
            lhs = BinOp(token=op_tok, left=lhs, right=rhs, op=op_char)
        return lhs

    def parse_factor(self) -> Expr:
        t = self.peek()
        if t.type == TokenType.INTEGER:
            self.consume()
            return NumLit(token=t, value=int(t.value))
        elif t.type == TokenType.IDENTIFIER:
            self.consume()
            if self.peek().type == TokenType.LPAREN:
                return self.parse_call(t.value)
            return VarExpr(token=t, name=t.value)
        elif t.type == TokenType.PRINT:
            self.consume()
            return self.parse_call("print")
        elif t.type == TokenType.LPAREN:
            self.consume()
            e = self.parse_expr()
            self.expect(TokenType.RPAREN, "Expected ')'")
            return e
        else:
            self._error(f"Unexpected token in expression: {t.value}", t)
            self.consume()
            return NumLit(token=t, value=0)

    def parse_call(self, name: str) -> CallExpr:
        self.expect(TokenType.LPAREN, "Expected '('")
        args = []
        if self.peek().type != TokenType.RPAREN:
            args.append(self.parse_expr())
            while self.match(TokenType.COMMA):
                args.append(self.parse_expr())
        self.expect(TokenType.RPAREN, "Expected ')'")
        return CallExpr(token=None, callee=name, args=args)

    def _error(self, msg, token):
        self.diag.report(Diagnostic(Severity.ERROR, self.file_path, token.line, token.col, msg))
