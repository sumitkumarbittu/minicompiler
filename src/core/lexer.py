from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional
import re
from .util import Diagnostic, Severity

class TokenType(Enum):
    # Control
    EOF = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    
    # Keywords
    DEF = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    RETURN = auto()
    
    # Builtins/Identifiers/Literals
    IDENTIFIER = auto()
    INTEGER = auto()
    PRINT = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQ = auto()      # =
    EQEQ = auto()    # ==
    NEQ = auto()     # !=
    LT = auto()      # <
    LTE = auto()     # <=
    GT = auto()      # >
    GTE = auto()     # >=
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    COLON = auto()
    COMMA = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    col: int
    
    def __str__(self):
        return f"Token({self.type.name}, '{self.value}', {self.line}:{self.col})"

class Lexer:
    def __init__(self, source: str, file_path: str, diag_engine):
        self.source = source
        self.file_path = file_path
        self.diag = diag_engine
        
        self.pos = 0
        self.line = 1
        self.col = 1
        self.indent_stack = [0]  # Stack of indent levels (spaces)
        self.tokens = []
        
        # Keywords map
        self.keywords = {
            'def': TokenType.DEF,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'return': TokenType.RETURN,
            'print': TokenType.PRINT # Treated as keyword-ish for v1
        }

    def tokenize(self) -> list[Token]:
        length = len(self.source)
        
        # Start of line handling
        is_start_of_line = True
        
        while self.pos < length:
            ch = self.source[self.pos]
            
            # Handle indentation at start of line
            if is_start_of_line:
                if ch == ' ':
                    # Count spaces
                    spaces = 0
                    temp_pos = self.pos
                    while temp_pos < length and self.source[temp_pos] == ' ':
                        spaces += 1
                        temp_pos += 1
                    
                    if temp_pos < length and self.source[temp_pos] == '\n':
                        # Empty line with spaces, ignore
                        self.pos = temp_pos + 1
                        self.line += 1
                        self.col = 1
                        continue
                    elif temp_pos < length and self.source[temp_pos] == '#':
                         # Comment line, ignore
                        self._skip_comment()
                        continue
                    
                    # Real code follows
                    self.pos = temp_pos
                    self.col += spaces
                    
                    current_indent = self.indent_stack[-1]
                    if spaces > current_indent:
                        self.indent_stack.append(spaces)
                        self.tokens.append(Token(TokenType.INDENT, "", self.line, 1))
                    elif spaces < current_indent:
                        while spaces < self.indent_stack[-1]:
                            self.indent_stack.pop()
                            self.tokens.append(Token(TokenType.DEDENT, "", self.line, 1))
                        if spaces != self.indent_stack[-1]:
                            self._error(f"Unindent does not match any outer indentation level")
                
                elif ch == '\n':
                    self.pos += 1
                    self.line += 1
                    self.col = 1
                    continue
                elif ch == '#':
                    self._skip_comment()
                    continue
                else:
                    # No spaces, check for dedent to 0
                    if self.indent_stack[-1] > 0:
                        while self.indent_stack[-1] > 0:
                            self.indent_stack.pop()
                            self.tokens.append(Token(TokenType.DEDENT, "", self.line, 1))
            
            is_start_of_line = False
            
            # Re-check char as we might have advanced
            if self.pos >= length: break
            ch = self.source[self.pos]
            
            if ch.isspace():
                if ch == '\n':
                    self.tokens.append(Token(TokenType.NEWLINE, "\n", self.line, self.col))
                    self.pos += 1
                    self.line += 1
                    self.col = 1
                    is_start_of_line = True
                    continue
                else:
                    self.pos += 1
                    self.col += 1
                    continue
            
            if ch == '#':
                self._skip_comment()
                # If comment ends with newline, next loop handles newline
                continue
                
            if ch.isalpha() or ch == '_':
                self._lex_identifier()
                continue
            
            if ch.isdigit():
                self._lex_number()
                continue
                
            # Operators
            if self._match("=="): self._add(TokenType.EQEQ, "=="); continue
            if self._match("!="): self._add(TokenType.NEQ, "!="); continue
            if self._match("<="): self._add(TokenType.LTE, "<="); continue
            if self._match(">="): self._add(TokenType.GTE, ">="); continue
            
            if ch == '+': self._add(TokenType.PLUS, "+")
            elif ch == '-': self._add(TokenType.MINUS, "-")
            elif ch == '*': self._add(TokenType.STAR, "*")
            elif ch == '/': self._add(TokenType.SLASH, "/")
            elif ch == '=': self._add(TokenType.EQ, "=")
            elif ch == '<': self._add(TokenType.LT, "<")
            elif ch == '>': self._add(TokenType.GT, ">")
            elif ch == '(': self._add(TokenType.LPAREN, "(")
            elif ch == ')': self._add(TokenType.RPAREN, ")")
            elif ch == ':': self._add(TokenType.COLON, ":")
            elif ch == ',': self._add(TokenType.COMMA, ",")
            else:
                self._error(f"Unexpected character '{ch}'")
                self.pos += 1
                self.col += 1

        # End of file cleanup
        if self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
             self.tokens.append(Token(TokenType.NEWLINE, "\n", self.line, self.col))
             
        while self.indent_stack[-1] > 0:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, "", self.line, self.col))
            
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.col))
        return self.tokens

    def _skip_comment(self):
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self.pos += 1

    def _match(self, s):
        if self.source.startswith(s, self.pos):
            return True
        return False

    def _add(self, type, val):
        self.tokens.append(Token(type, val, self.line, self.col))
        self.pos += len(val)
        self.col += len(val)

    def _lex_identifier(self):
        start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self.pos += 1
        text = self.source[start:self.pos]
        
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.tokens.append(Token(token_type, text, self.line, self.col - (self.pos - start)))
        self.col += (self.pos - start)

    def _lex_number(self):
        start = self.pos
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self.pos += 1
        text = self.source[start:self.pos]
        self.tokens.append(Token(TokenType.INTEGER, text, self.line, self.col - (self.pos - start)))
        self.col += (self.pos - start)

    def _error(self, msg):
        self.diag.report(Diagnostic(Severity.ERROR, self.file_path, self.line, self.col, msg))
