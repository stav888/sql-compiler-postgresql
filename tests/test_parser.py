"""
Tests for the SQL parser.
"""

import unittest
from src.lexer.lexer import SQLLexer
from src.parser.parser import SQLParser, parse_sql
from src.ast.nodes import *


class TestSQLParser(unittest.TestCase):
    
    def test_simple_select(self):
        sql = "SELECT id, name FROM users"
        statements = parse_sql(sql)
        
        self.assertEqual(len(statements), 1)
        stmt = statements[0]
        self.assertIsInstance(stmt, SelectStatement)
        self.assertEqual(len(stmt.select_list), 2)
        self.assertIsInstance(stmt.from_clause, TableReference)
        self.assertEqual(stmt.from_clause.name, "users")
    
    def test_select_with_where(self):
        sql = "SELECT * FROM users WHERE id = 1"
        statements = parse_sql(sql)
        
        stmt = statements[0]
        self.assertIsInstance(stmt, SelectStatement)
        self.assertIsNotNone(stmt.where_clause)
        self.assertIsInstance(stmt.where_clause, BinaryOperation)
    
    def test_select_with_join(self):
        sql = "SELECT u.name, p.title FROM users u JOIN posts p ON u.id = p.user_id"
        statements = parse_sql(sql)
        
        stmt = statements[0]
        self.assertIsInstance(stmt, SelectStatement)
        self.assertIsInstance(stmt.from_clause, Join)
        self.assertEqual(stmt.from_clause.join_type, "INNER")
    
    def test_insert_statement(self):
        sql = "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')"
        statements = parse_sql(sql)
        
        stmt = statements[0]
        self.assertIsInstance(stmt, InsertStatement)
        self.assertEqual(stmt.table.name, "users")
        self.assertEqual(len(stmt.columns), 2)
        self.assertEqual(len(stmt.values), 1)
        self.assertEqual(len(stmt.values[0]), 2)
    
    def test_update_statement(self):
        sql = "UPDATE users SET name = 'John Doe' WHERE id = 1"
        statements = parse_sql(sql)
        
        stmt = statements[0]
        self.assertIsInstance(stmt, UpdateStatement)
        self.assertEqual(stmt.table.name, "users")
        self.assertEqual(len(stmt.set_clauses), 1)
        self.assertIsNotNone(stmt.where_clause)
    
    def test_delete_statement(self):
        sql = "DELETE FROM users WHERE id = 1"
        statements = parse_sql(sql)
        
        stmt = statements[0]
        self.assertIsInstance(stmt, DeleteStatement)
        self.assertEqual(stmt.table.name, "users")
        self.assertIsNotNone(stmt.where_clause)
    
    def test_create_table_statement(self):
        sql = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email TEXT UNIQUE
        )
        """
        statements = parse_sql(sql)
        
        stmt = statements[0]
        self.assertIsInstance(stmt, CreateTableStatement)
        self.assertEqual(stmt.table_name, "users")
        self.assertEqual(len(stmt.columns), 3)
    
    def test_function_call(self):
        sql = "SELECT COUNT(*), MAX(age) FROM users"
        statements = parse_sql(sql)
        
        stmt = statements[0]
        self.assertEqual(len(stmt.select_list), 2)
        self.assertIsInstance(stmt.select_list[0], FunctionCall)
        self.assertIsInstance(stmt.select_list[1], FunctionCall)
    
    def test_case_expression(self):
        sql = """
        SELECT CASE 
            WHEN age < 18 THEN 'Minor'
            WHEN age >= 18 THEN 'Adult'
            ELSE 'Unknown'
        END FROM users
        """
        statements = parse_sql(sql)
        
        stmt = statements[0]
        self.assertIsInstance(stmt.select_list[0], CaseExpression)
        case_expr = stmt.select_list[0]
        self.assertEqual(len(case_expr.when_clauses), 2)
        self.assertIsNotNone(case_expr.else_clause)
    
    def test_with_clause(self):
        sql = """
        WITH recent_users AS (
            SELECT * FROM users WHERE created_at > '2023-01-01'
        )
        SELECT * FROM recent_users
        """
        statements = parse_sql(sql)
        
        stmt = statements[0]
        self.assertIsInstance(stmt, SelectStatement)
        self.assertIsNotNone(stmt.with_clause)
        self.assertEqual(len(stmt.with_clause.ctes), 1)


if __name__ == '__main__':
    unittest.main()