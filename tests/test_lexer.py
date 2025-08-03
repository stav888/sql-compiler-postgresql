"""
Tests for the SQL lexer.
"""

import unittest
from src.lexer.lexer import SQLLexer, TokenType, LexerError


class TestSQLLexer(unittest.TestCase):
    
    def test_simple_select(self):
        sql = "SELECT id, name FROM users"
        lexer = SQLLexer(sql)
        tokens = lexer.get_tokens()
        
        expected_types = [
            TokenType.SELECT, TokenType.IDENTIFIER, TokenType.COMMA,
            TokenType.IDENTIFIER, TokenType.FROM, TokenType.IDENTIFIER,
            TokenType.EOF
        ]
        
        actual_types = [token.type for token in tokens]
        self.assertEqual(actual_types, expected_types)
    
    def test_string_literals(self):
        sql = "SELECT 'hello', \"world\""
        lexer = SQLLexer(sql)
        tokens = lexer.get_tokens()
        
        string_tokens = [token for token in tokens if token.type == TokenType.STRING]
        self.assertEqual(len(string_tokens), 2)
        self.assertEqual(string_tokens[0].value, "hello")
        self.assertEqual(string_tokens[1].value, "world")
    
    def test_numbers(self):
        sql = "SELECT 42, 3.14, 1.5e10"
        lexer = SQLLexer(sql)
        tokens = lexer.get_tokens()
        
        number_tokens = [token for token in tokens if token.type == TokenType.NUMBER]
        self.assertEqual(len(number_tokens), 3)
        self.assertEqual(number_tokens[0].value, "42")
        self.assertEqual(number_tokens[1].value, "3.14")
        self.assertEqual(number_tokens[2].value, "1.5e10")
    
    def test_keywords(self):
        sql = "SELECT DISTINCT name FROM users WHERE active = TRUE"
        lexer = SQLLexer(sql)
        tokens = lexer.get_tokens()
        
        keyword_tokens = [token for token in tokens if token.type in [
            TokenType.SELECT, TokenType.DISTINCT, TokenType.FROM,
            TokenType.WHERE, TokenType.TRUE
        ]]
        self.assertEqual(len(keyword_tokens), 5)
    
    def test_operators(self):
        sql = "SELECT a + b, c * d, e <= f"
        lexer = SQLLexer(sql)
        tokens = lexer.get_tokens()
        
        operator_tokens = [token for token in tokens if token.type in [
            TokenType.PLUS, TokenType.MULTIPLY, TokenType.LESS_EQUAL
        ]]
        self.assertEqual(len(operator_tokens), 3)
    
    def test_postgresql_operators(self):
        sql = "SELECT data -> 'key', json ->> 'field'"
        lexer = SQLLexer(sql)
        tokens = lexer.get_tokens()
        
        arrow_tokens = [token for token in tokens if token.type in [
            TokenType.ARROW, TokenType.DOUBLE_ARROW
        ]]
        self.assertEqual(len(arrow_tokens), 2)
    
    def test_comments(self):
        sql = """
        -- Single line comment
        SELECT id /* Multi-line
        comment */ FROM users
        """
        lexer = SQLLexer(sql)
        tokens = lexer.get_tokens(include_comments=True)
        
        comment_tokens = [token for token in tokens if token.type == TokenType.COMMENT]
        self.assertEqual(len(comment_tokens), 2)
    
    def test_error_handling(self):
        sql = "SELECT @ FROM users"
        lexer = SQLLexer(sql)
        
        with self.assertRaises(LexerError):
            lexer.get_tokens()


if __name__ == '__main__':
    unittest.main()