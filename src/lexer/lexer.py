"""
SQL Lexer - Tokenizes SQL input into tokens for parsing.
Supports PostgreSQL-specific syntax and keywords.
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Iterator


class TokenType(Enum):
    # Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    
    # Keywords (PostgreSQL-specific and standard SQL)
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    TABLE = "TABLE"
    INDEX = "INDEX"
    DROP = "DROP"
    ALTER = "ALTER"
    INTO = "INTO"
    VALUES = "VALUES"
    SET = "SET"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    NULL = "NULL"
    TRUE = "TRUE"
    FALSE = "FALSE"
    AS = "AS"
    DISTINCT = "DISTINCT"
    ORDER = "ORDER"
    BY = "BY"
    GROUP = "GROUP"
    HAVING = "HAVING"
    LIMIT = "LIMIT"
    OFFSET = "OFFSET"
    JOIN = "JOIN"
    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    FULL = "FULL"
    OUTER = "OUTER"
    ON = "ON"
    USING = "USING"
    UNION = "UNION"
    INTERSECT = "INTERSECT"
    EXCEPT = "EXCEPT"
    ALL = "ALL"
    ANY = "ANY"
    SOME = "SOME"
    EXISTS = "EXISTS"
    IN = "IN"
    BETWEEN = "BETWEEN"
    LIKE = "LIKE"
    ILIKE = "ILIKE"  # PostgreSQL-specific
    SIMILAR = "SIMILAR"
    CASE = "CASE"
    WHEN = "WHEN"
    THEN = "THEN"
    ELSE = "ELSE"
    END = "END"
    WITH = "WITH"  # For CTEs
    RECURSIVE = "RECURSIVE"
    WINDOW = "WINDOW"  # For window functions
    OVER = "OVER"
    PARTITION = "PARTITION"
    ARRAY = "ARRAY"  # PostgreSQL arrays
    JSONB = "JSONB"  # PostgreSQL JSON
    JSON = "JSON"
    
    # Data types
    INTEGER = "INTEGER"
    BIGINT = "BIGINT"
    SMALLINT = "SMALLINT"
    DECIMAL = "DECIMAL"
    NUMERIC = "NUMERIC"
    REAL = "REAL"
    DOUBLE = "DOUBLE"
    PRECISION = "PRECISION"
    VARCHAR = "VARCHAR"
    CHAR = "CHAR"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    TIME = "TIME"
    TIMESTAMP = "TIMESTAMP"
    TIMESTAMPTZ = "TIMESTAMPTZ"  # PostgreSQL-specific
    INTERVAL = "INTERVAL"
    UUID = "UUID"  # PostgreSQL-specific
    LATERAL = "LATERAL"  # PostgreSQL-specific
    
    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS_THAN = "LESS_THAN"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_THAN = "GREATER_THAN"
    GREATER_EQUAL = "GREATER_EQUAL"
    CONCAT = "CONCAT"  # ||
    CAST = "CAST"  # ::
    ARROW = "ARROW"  # -> for JSON
    DOUBLE_ARROW = "DOUBLE_ARROW"  # ->> for JSON
    HASH = "HASH"  # # for JSON path
    QUESTION = "QUESTION"  # ? for JSON
    
    # Punctuation
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    DOT = "DOT"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    
    # Special
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    position: int


class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Line {line}, Column {column}: {message}")


class SQLLexer:
    """
    SQL Lexer for PostgreSQL-compatible SQL statements.
    Tokenizes input text into a stream of tokens for parsing.
    """
    
    # PostgreSQL keywords (case-insensitive)
    KEYWORDS = {
        'SELECT': TokenType.SELECT,
        'FROM': TokenType.FROM,
        'WHERE': TokenType.WHERE,
        'INSERT': TokenType.INSERT,
        'UPDATE': TokenType.UPDATE,
        'DELETE': TokenType.DELETE,
        'CREATE': TokenType.CREATE,
        'TABLE': TokenType.TABLE,
        'INDEX': TokenType.INDEX,
        'DROP': TokenType.DROP,
        'ALTER': TokenType.ALTER,
        'INTO': TokenType.INTO,
        'VALUES': TokenType.VALUES,
        'SET': TokenType.SET,
        'AND': TokenType.AND,
        'OR': TokenType.OR,
        'NOT': TokenType.NOT,
        'NULL': TokenType.NULL,
        'TRUE': TokenType.TRUE,
        'FALSE': TokenType.FALSE,
        'AS': TokenType.AS,
        'DISTINCT': TokenType.DISTINCT,
        'ORDER': TokenType.ORDER,
        'BY': TokenType.BY,
        'GROUP': TokenType.GROUP,
        'HAVING': TokenType.HAVING,
        'LIMIT': TokenType.LIMIT,
        'OFFSET': TokenType.OFFSET,
        'JOIN': TokenType.JOIN,
        'INNER': TokenType.INNER,
        'LEFT': TokenType.LEFT,
        'RIGHT': TokenType.RIGHT,
        'FULL': TokenType.FULL,
        'OUTER': TokenType.OUTER,
        'ON': TokenType.ON,
        'USING': TokenType.USING,
        'UNION': TokenType.UNION,
        'INTERSECT': TokenType.INTERSECT,
        'EXCEPT': TokenType.EXCEPT,
        'ALL': TokenType.ALL,
        'ANY': TokenType.ANY,
        'SOME': TokenType.SOME,
        'EXISTS': TokenType.EXISTS,
        'IN': TokenType.IN,
        'BETWEEN': TokenType.BETWEEN,
        'LIKE': TokenType.LIKE,
        'ILIKE': TokenType.ILIKE,
        'SIMILAR': TokenType.SIMILAR,
        'CASE': TokenType.CASE,
        'WHEN': TokenType.WHEN,
        'THEN': TokenType.THEN,
        'ELSE': TokenType.ELSE,
        'END': TokenType.END,
        'WITH': TokenType.WITH,
        'RECURSIVE': TokenType.RECURSIVE,
        'WINDOW': TokenType.WINDOW,
        'OVER': TokenType.OVER,
        'PARTITION': TokenType.PARTITION,
        'ARRAY': TokenType.ARRAY,
        'JSONB': TokenType.JSONB,
        'JSON': TokenType.JSON,
        'INTEGER': TokenType.INTEGER,
        'BIGINT': TokenType.BIGINT,
        'SMALLINT': TokenType.SMALLINT,
        'DECIMAL': TokenType.DECIMAL,
        'NUMERIC': TokenType.NUMERIC,
        'REAL': TokenType.REAL,
        'DOUBLE': TokenType.DOUBLE,
        'PRECISION': TokenType.PRECISION,
        'VARCHAR': TokenType.VARCHAR,
        'CHAR': TokenType.CHAR,
        'TEXT': TokenType.TEXT,
        'BOOLEAN': TokenType.BOOLEAN,
        'DATE': TokenType.DATE,
        'TIME': TokenType.TIME,
        'TIMESTAMP': TokenType.TIMESTAMP,
        'TIMESTAMPTZ': TokenType.TIMESTAMPTZ,
        'INTERVAL': TokenType.INTERVAL,
        'UUID': TokenType.UUID,
        'LATERAL': TokenType.LATERAL,
    }
    
    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        """Get the current character at position."""
        if self.position >= len(self.text):
            return None
        return self.text[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek at character at current position + offset."""
        pos = self.position + offset
        if pos >= len(self.text):
            return None
        return self.text[pos]
    
    def advance(self) -> None:
        """Move to the next character."""
        if self.position < len(self.text):
            if self.text[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def skip_whitespace(self) -> None:
        """Skip whitespace characters except newlines."""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def read_string(self, quote_char: str) -> str:
        """Read a string literal."""
        value = ""
        self.advance()  # Skip opening quote
        
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char():
                    # Handle escape sequences
                    escape_map = {
                        'n': '\n',
                        't': '\t',
                        'r': '\r',
                        '\\': '\\',
                        "'": "'",
                        '"': '"'
                    }
                    value += escape_map.get(self.current_char(), self.current_char())
                    self.advance()
            else:
                value += self.current_char()
                self.advance()
        
        if not self.current_char():
            raise LexerError("Unterminated string literal", self.line, self.column)
        
        self.advance()  # Skip closing quote
        return value
    
    def read_number(self) -> str:
        """Read a numeric literal."""
        value = ""
        has_dot = False
        
        while (self.current_char() and 
               (self.current_char().isdigit() or 
                (self.current_char() == '.' and not has_dot))):
            if self.current_char() == '.':
                has_dot = True
            value += self.current_char()
            self.advance()
        
        # Handle scientific notation
        if self.current_char() and self.current_char().lower() == 'e':
            value += self.current_char()
            self.advance()
            if self.current_char() and self.current_char() in '+-':
                value += self.current_char()
                self.advance()
            while self.current_char() and self.current_char().isdigit():
                value += self.current_char()
                self.advance()
        
        return value
    
    def read_identifier(self) -> str:
        """Read an identifier or keyword."""
        value = ""
        
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() in '_$')):
            value += self.current_char()
            self.advance()
        
        return value
    
    def read_comment(self) -> str:
        """Read a comment (-- or /* */)."""
        if self.current_char() == '-' and self.peek_char() == '-':
            # Single line comment
            value = ""
            while self.current_char() and self.current_char() != '\n':
                value += self.current_char()
                self.advance()
            return value
        elif self.current_char() == '/' and self.peek_char() == '*':
            # Multi-line comment
            value = ""
            self.advance()  # Skip /
            self.advance()  # Skip *
            
            while self.current_char():
                if self.current_char() == '*' and self.peek_char() == '/':
                    value += "*/"
                    self.advance()
                    self.advance()
                    break
                value += self.current_char()
                self.advance()
            
            return "/*" + value
        
        return ""
    
    def tokenize(self) -> List[Token]:
        """Tokenize the input text."""
        self.tokens = []
        
        while self.current_char():
            start_line = self.line
            start_column = self.column
            start_position = self.position
            
            char = self.current_char()
            
            # Skip whitespace
            if char in ' \t\r':
                self.skip_whitespace()
                continue
            
            # Newlines
            elif char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, char, start_line, start_column, start_position))
                self.advance()
            
            # Comments
            elif char == '-' and self.peek_char() == '-':
                comment = self.read_comment()
                self.tokens.append(Token(TokenType.COMMENT, comment, start_line, start_column, start_position))
            
            elif char == '/' and self.peek_char() == '*':
                comment = self.read_comment()
                self.tokens.append(Token(TokenType.COMMENT, comment, start_line, start_column, start_position))
            
            # String literals
            elif char in ("'", '"'):
                value = self.read_string(char)
                self.tokens.append(Token(TokenType.STRING, value, start_line, start_column, start_position))
            
            # Numbers
            elif char.isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, start_line, start_column, start_position))
            
            # Identifiers and keywords
            elif char.isalpha() or char == '_':
                value = self.read_identifier()
                token_type = self.KEYWORDS.get(value.upper(), TokenType.IDENTIFIER)
                self.tokens.append(Token(token_type, value, start_line, start_column, start_position))
            
            # Operators and punctuation
            elif char == ';':
                self.tokens.append(Token(TokenType.SEMICOLON, char, start_line, start_column, start_position))
                self.advance()
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, char, start_line, start_column, start_position))
                self.advance()
            elif char == '.':
                self.tokens.append(Token(TokenType.DOT, char, start_line, start_column, start_position))
                self.advance()
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, char, start_line, start_column, start_position))
                self.advance()
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, char, start_line, start_column, start_position))
                self.advance()
            elif char == '[':
                self.tokens.append(Token(TokenType.LBRACKET, char, start_line, start_column, start_position))
                self.advance()
            elif char == ']':
                self.tokens.append(Token(TokenType.RBRACKET, char, start_line, start_column, start_position))
                self.advance()
            elif char == '{':
                self.tokens.append(Token(TokenType.LBRACE, char, start_line, start_column, start_position))
                self.advance()
            elif char == '}':
                self.tokens.append(Token(TokenType.RBRACE, char, start_line, start_column, start_position))
                self.advance()
            elif char == '+':
                self.tokens.append(Token(TokenType.PLUS, char, start_line, start_column, start_position))
                self.advance()
            elif char == '-':
                if self.peek_char() == '>':
                    if self.peek_char(2) == '>':
                        self.tokens.append(Token(TokenType.DOUBLE_ARROW, '->>', start_line, start_column, start_position))
                        self.advance()
                        self.advance()
                        self.advance()
                    else:
                        self.tokens.append(Token(TokenType.ARROW, '->', start_line, start_column, start_position))
                        self.advance()
                        self.advance()
                else:
                    self.tokens.append(Token(TokenType.MINUS, char, start_line, start_column, start_position))
                    self.advance()
            elif char == '*':
                self.tokens.append(Token(TokenType.MULTIPLY, char, start_line, start_column, start_position))
                self.advance()
            elif char == '/':
                self.tokens.append(Token(TokenType.DIVIDE, char, start_line, start_column, start_position))
                self.advance()
            elif char == '%':
                self.tokens.append(Token(TokenType.MODULO, char, start_line, start_column, start_position))
                self.advance()
            elif char == '=':
                self.tokens.append(Token(TokenType.EQUAL, char, start_line, start_column, start_position))
                self.advance()
            elif char == '!':
                if self.peek_char() == '=':
                    self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', start_line, start_column, start_position))
                    self.advance()
                    self.advance()
                else:
                    raise LexerError(f"Unexpected character: {char}", self.line, self.column)
            elif char == '<':
                if self.peek_char() == '=':
                    self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', start_line, start_column, start_position))
                    self.advance()
                    self.advance()
                elif self.peek_char() == '>':
                    self.tokens.append(Token(TokenType.NOT_EQUAL, '<>', start_line, start_column, start_position))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.LESS_THAN, char, start_line, start_column, start_position))
                    self.advance()
            elif char == '>':
                if self.peek_char() == '=':
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', start_line, start_column, start_position))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.GREATER_THAN, char, start_line, start_column, start_position))
                    self.advance()
            elif char == '|':
                if self.peek_char() == '|':
                    self.tokens.append(Token(TokenType.CONCAT, '||', start_line, start_column, start_position))
                    self.advance()
                    self.advance()
                else:
                    raise LexerError(f"Unexpected character: {char}", self.line, self.column)
            elif char == ':':
                if self.peek_char() == ':':
                    self.tokens.append(Token(TokenType.CAST, '::', start_line, start_column, start_position))
                    self.advance()
                    self.advance()
                else:
                    raise LexerError(f"Unexpected character: {char}", self.line, self.column)
            elif char == '#':
                self.tokens.append(Token(TokenType.HASH, char, start_line, start_column, start_position))
                self.advance()
            elif char == '?':
                self.tokens.append(Token(TokenType.QUESTION, char, start_line, start_column, start_position))
                self.advance()
            else:
                raise LexerError(f"Unexpected character: {char}", self.line, self.column)
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column, self.position))
        return self.tokens
    
    def get_tokens(self, include_whitespace: bool = False, include_comments: bool = False) -> List[Token]:
        """Get tokens, optionally filtering out whitespace and comments."""
        if not self.tokens:
            self.tokenize()
        
        filtered_tokens = []
        for token in self.tokens:
            if not include_whitespace and token.type == TokenType.NEWLINE:
                continue
            if not include_comments and token.type == TokenType.COMMENT:
                continue
            filtered_tokens.append(token)
        
        return filtered_tokens