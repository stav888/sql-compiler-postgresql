"""
Integration tests for the SQL compiler.
"""

import unittest
import json
from src.main import SQLCompiler


class TestSQLCompiler(unittest.TestCase):
    
    def setUp(self):
        self.compiler = SQLCompiler()
    
    def test_simple_query_compilation(self):
        sql = "SELECT id, name FROM users WHERE active = TRUE"
        result = self.compiler.compile_sql(sql)
        
        self.assertTrue(result["success"])
        self.assertGreater(len(result["tokens"]), 0)
        self.assertGreater(len(result["ast"]), 0)
        self.assertIsNotNone(result["optimized_sql"])
    
    def test_complex_query_compilation(self):
        sql = """
        WITH recent_orders AS (
            SELECT user_id, COUNT(*) as order_count
            FROM orders 
            WHERE created_at > '2023-01-01'
            GROUP BY user_id
        )
        SELECT u.name, u.email, ro.order_count
        FROM users u
        LEFT JOIN recent_orders ro ON u.id = ro.user_id
        WHERE u.active = TRUE
        ORDER BY ro.order_count DESC
        LIMIT 10
        """
        result = self.compiler.compile_sql(sql, analyze=True)
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["semantic_info"])
        self.assertIn("users", result["semantic_info"]["tables_used"])
        self.assertIn("orders", result["semantic_info"]["tables_used"])
    
    def test_insert_compilation(self):
        sql = "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')"
        result = self.compiler.compile_sql(sql)
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["optimized_sql"])
    
    def test_error_handling(self):
        sql = "INVALID SQL STATEMENT"
        result = self.compiler.compile_sql(sql)
        
        self.assertFalse(result["success"])
        self.assertGreater(len(result["errors"]), 0)
    
    def test_postgresql_specific_features(self):
        sql = """
        SELECT 
            data -> 'key' as json_field,
            ARRAY[1, 2, 3] as array_field,
            name ILIKE '%john%' as case_insensitive_match
        FROM users
        """
        result = self.compiler.compile_sql(sql)
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["optimized_sql"])


if __name__ == '__main__':
    unittest.main()