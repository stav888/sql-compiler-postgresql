"""
Code Generator for optimized PostgreSQL SQL.
Generates optimized SQL code from AST.
"""

from typing import List, Dict, Any, Optional
from ..ast.nodes import *


class CodeGenerator:
    """
    Code generator for PostgreSQL SQL.
    Generates optimized SQL code from AST nodes.
    """
    
    def __init__(self, target_version: str = "postgresql-14"):
        self.target_version = target_version
        self.indent_level = 0
        self.optimization_enabled = True
    
    def generate(self, statements: List[Statement]) -> str:
        """Generate SQL code from a list of statements."""
        sql_parts = []
        
        for statement in statements:
            sql = self._generate_statement(statement)
            if sql:
                sql_parts.append(sql)
        
        return ";\n\n".join(sql_parts) + ";"
    
    def _generate_statement(self, statement: Statement) -> str:
        """Generate SQL for a single statement."""
        if isinstance(statement, SelectStatement):
            return self._generate_select_statement(statement)
        elif isinstance(statement, InsertStatement):
            return self._generate_insert_statement(statement)
        elif isinstance(statement, UpdateStatement):
            return self._generate_update_statement(statement)
        elif isinstance(statement, DeleteStatement):
            return self._generate_delete_statement(statement)
        elif isinstance(statement, CreateTableStatement):
            return self._generate_create_table_statement(statement)
        else:
            return ""
    
    def _generate_select_statement(self, stmt: SelectStatement) -> str:
        """Generate SQL for a SELECT statement."""
        parts = []
        
        # WITH clause
        if stmt.with_clause:
            parts.append(self._generate_with_clause(stmt.with_clause))
        
        # SELECT clause
        select_part = "SELECT"
        if stmt.distinct:
            select_part += " DISTINCT"
        
        select_list = ", ".join(self._generate_expression(expr) for expr in stmt.select_list)
        parts.append(f"{select_part} {select_list}")
        
        # FROM clause
        if stmt.from_clause:
            from_sql = self._generate_expression(stmt.from_clause)
            parts.append(f"FROM {from_sql}")
        
        # WHERE clause
        if stmt.where_clause:
            where_sql = self._generate_expression(stmt.where_clause)
            parts.append(f"WHERE {where_sql}")
        
        # GROUP BY clause
        if stmt.group_by:
            group_by_list = ", ".join(self._generate_expression(expr) for expr in stmt.group_by)
            parts.append(f"GROUP BY {group_by_list}")
        
        # HAVING clause
        if stmt.having_clause:
            having_sql = self._generate_expression(stmt.having_clause)
            parts.append(f"HAVING {having_sql}")
        
        # ORDER BY clause
        if stmt.order_by:
            order_by_list = ", ".join(self._generate_order_by_item(item) for item in stmt.order_by)
            parts.append(f"ORDER BY {order_by_list}")
        
        # LIMIT clause
        if stmt.limit_clause:
            limit_sql = self._generate_expression(stmt.limit_clause)
            parts.append(f"LIMIT {limit_sql}")
        
        # OFFSET clause
        if stmt.offset_clause:
            offset_sql = self._generate_expression(stmt.offset_clause)
            parts.append(f"OFFSET {offset_sql}")
        
        return "\n".join(parts)
    
    def _generate_with_clause(self, with_clause: WithClause) -> str:
        """Generate SQL for WITH clause."""
        parts = ["WITH"]
        
        if with_clause.recursive:
            parts[0] += " RECURSIVE"
        
        cte_parts = []
        for cte in with_clause.ctes:
            cte_sql = self._generate_cte(cte)
            cte_parts.append(cte_sql)
        
        parts.append(", ".join(cte_parts))
        return " ".join(parts)
    
    def _generate_cte(self, cte: CommonTableExpression) -> str:
        """Generate SQL for a CTE."""
        parts = [cte.name]
        
        if cte.columns:
            columns = ", ".join(cte.columns)
            parts.append(f"({columns})")
        
        parts.append("AS")
        query_sql = self._generate_select_statement(cte.query)
        parts.append(f"({query_sql})")
        
        return " ".join(parts)
    
    def _generate_insert_statement(self, stmt: InsertStatement) -> str:
        """Generate SQL for INSERT statement."""
        parts = ["INSERT INTO", stmt.table.name]
        
        if stmt.columns:
            columns = ", ".join(stmt.columns)
            parts.append(f"({columns})")
        
        if stmt.values:
            values_parts = []
            for row in stmt.values:
                row_values = ", ".join(self._generate_expression(expr) for expr in row)
                values_parts.append(f"({row_values})")
            parts.append("VALUES")
            parts.append(", ".join(values_parts))
        elif stmt.select_query:
            select_sql = self._generate_select_statement(stmt.select_query)
            parts.append(select_sql)
        
        return " ".join(parts)
    
    def _generate_update_statement(self, stmt: UpdateStatement) -> str:
        """Generate SQL for UPDATE statement."""
        parts = ["UPDATE", stmt.table.name, "SET"]
        
        set_parts = []
        for column, expr in stmt.set_clauses:
            expr_sql = self._generate_expression(expr)
            set_parts.append(f"{column} = {expr_sql}")
        
        parts.append(", ".join(set_parts))
        
        if stmt.where_clause:
            where_sql = self._generate_expression(stmt.where_clause)
            parts.append(f"WHERE {where_sql}")
        
        return " ".join(parts)
    
    def _generate_delete_statement(self, stmt: DeleteStatement) -> str:
        """Generate SQL for DELETE statement."""
        parts = ["DELETE FROM", stmt.table.name]
        
        if stmt.where_clause:
            where_sql = self._generate_expression(stmt.where_clause)
            parts.append(f"WHERE {where_sql}")
        
        return " ".join(parts)
    
    def _generate_create_table_statement(self, stmt: CreateTableStatement) -> str:
        """Generate SQL for CREATE TABLE statement."""
        parts = ["CREATE TABLE", stmt.table_name, "("]
        
        column_parts = []
        for col in stmt.columns:
            col_sql = self._generate_column_definition(col)
            column_parts.append(col_sql)
        
        if stmt.constraints:
            for constraint in stmt.constraints:
                constraint_sql = self._generate_table_constraint(constraint)
                column_parts.append(constraint_sql)
        
        parts.append(",\n    ".join(column_parts))
        parts.append(")")
        
        return " ".join(parts[:2]) + " " + parts[2] + "\n    " + parts[3] + "\n" + parts[4]
    
    def _generate_column_definition(self, col: ColumnDefinition) -> str:
        """Generate SQL for column definition."""
        parts = [col.name, col.data_type]
        
        if col.constraints:
            parts.extend(col.constraints)
        
        return " ".join(parts)
    
    def _generate_table_constraint(self, constraint: TableConstraint) -> str:
        """Generate SQL for table constraint."""
        parts = []
        
        if constraint.name:
            parts.append(f"CONSTRAINT {constraint.name}")
        
        if constraint.constraint_type == "PRIMARY KEY":
            columns = ", ".join(constraint.columns)
            parts.append(f"PRIMARY KEY ({columns})")
        elif constraint.constraint_type == "FOREIGN KEY":
            columns = ", ".join(constraint.columns)
            ref_columns = ", ".join(constraint.reference_columns)
            parts.append(f"FOREIGN KEY ({columns}) REFERENCES {constraint.reference_table} ({ref_columns})")
        elif constraint.constraint_type == "UNIQUE":
            columns = ", ".join(constraint.columns)
            parts.append(f"UNIQUE ({columns})")
        
        return " ".join(parts)
    
    def _generate_order_by_item(self, item: OrderByItem) -> str:
        """Generate SQL for ORDER BY item."""
        parts = [self._generate_expression(item.expression)]
        
        if item.direction != "ASC":
            parts.append(item.direction)
        
        if item.nulls:
            parts.append(f"NULLS {item.nulls}")
        
        return " ".join(parts)
    
    def _generate_expression(self, expr: Expression) -> str:
        """Generate SQL for an expression."""
        if isinstance(expr, Identifier):
            return expr.name
        
        elif isinstance(expr, StringLiteral):
            # Escape single quotes
            escaped = expr.value.replace("'", "''")
            return f"'{escaped}'"
        
        elif isinstance(expr, NumberLiteral):
            return str(expr.value)
        
        elif isinstance(expr, BooleanLiteral):
            return "TRUE" if expr.value else "FALSE"
        
        elif isinstance(expr, NullLiteral):
            return "NULL"
        
        elif isinstance(expr, ColumnReference):
            if expr.table:
                return f"{expr.table}.{expr.column}"
            return expr.column
        
        elif isinstance(expr, TableReference):
            parts = [expr.name]
            if expr.alias:
                parts.extend(["AS", expr.alias])
            return " ".join(parts)
        
        elif isinstance(expr, BinaryOperation):
            left = self._generate_expression(expr.left)
            right = self._generate_expression(expr.right)
            
            # Add parentheses for clarity in complex expressions
            if isinstance(expr.left, BinaryOperation):
                left = f"({left})"
            if isinstance(expr.right, BinaryOperation):
                right = f"({right})"
            
            return f"{left} {expr.operator} {right}"
        
        elif isinstance(expr, UnaryOperation):
            operand = self._generate_expression(expr.operand)
            if isinstance(expr.operand, BinaryOperation):
                operand = f"({operand})"
            return f"{expr.operator} {operand}"
        
        elif isinstance(expr, FunctionCall):
            args = ", ".join(self._generate_expression(arg) for arg in expr.arguments)
            return f"{expr.name}({args})"
        
        elif isinstance(expr, CaseExpression):
            parts = ["CASE"]
            
            if expr.expression:
                parts.append(self._generate_expression(expr.expression))
            
            for when_expr, then_expr in expr.when_clauses:
                when_sql = self._generate_expression(when_expr)
                then_sql = self._generate_expression(then_expr)
                parts.append(f"WHEN {when_sql} THEN {then_sql}")
            
            if expr.else_clause:
                else_sql = self._generate_expression(expr.else_clause)
                parts.append(f"ELSE {else_sql}")
            
            parts.append("END")
            return " ".join(parts)
        
        elif isinstance(expr, ArrayExpression):
            elements = ", ".join(self._generate_expression(elem) for elem in expr.elements)
            return f"ARRAY[{elements}]"
        
        elif isinstance(expr, JSONExpression):
            obj_sql = self._generate_expression(expr.object_expr)
            path_sql = self._generate_expression(expr.path_expr)
            return f"{obj_sql} {expr.operator} {path_sql}"
        
        elif isinstance(expr, Subquery):
            query_sql = self._generate_select_statement(expr.query)
            return f"({query_sql})"
        
        elif isinstance(expr, Join):
            left_sql = self._generate_expression(expr.left)
            right_sql = self._generate_expression(expr.right)
            
            parts = [left_sql, f"{expr.join_type} JOIN", right_sql]
            
            if expr.condition:
                condition_sql = self._generate_expression(expr.condition)
                parts.append(f"ON {condition_sql}")
            elif expr.using_columns:
                columns = ", ".join(expr.using_columns)
                parts.append(f"USING ({columns})")
            
            return " ".join(parts)
        
        elif isinstance(expr, WindowFunction):
            func_sql = self._generate_expression(expr.function)
            over_sql = self._generate_over_clause(expr.over_clause)
            return f"{func_sql} {over_sql}"
        
        else:
            return str(expr)
    
    def _generate_over_clause(self, over_clause: OverClause) -> str:
        """Generate SQL for OVER clause."""
        parts = ["OVER ("]
        
        clause_parts = []
        
        if over_clause.partition_by:
            partition_list = ", ".join(self._generate_expression(expr) for expr in over_clause.partition_by)
            clause_parts.append(f"PARTITION BY {partition_list}")
        
        if over_clause.order_by:
            order_list = ", ".join(self._generate_order_by_item(item) for item in over_clause.order_by)
            clause_parts.append(f"ORDER BY {order_list}")
        
        if over_clause.frame:
            frame_sql = self._generate_window_frame(over_clause.frame)
            clause_parts.append(frame_sql)
        
        parts.append(" ".join(clause_parts))
        parts.append(")")
        
        return "".join(parts)
    
    def _generate_window_frame(self, frame: WindowFrame) -> str:
        """Generate SQL for window frame."""
        parts = [frame.frame_type]  # ROWS, RANGE, GROUPS
        
        if frame.end_bound:
            parts.append(f"BETWEEN {frame.start_bound} AND {frame.end_bound}")
        else:
            parts.append(frame.start_bound)
        
        return " ".join(parts)
    
    def _optimize_query(self, sql: str) -> str:
        """Apply basic query optimizations."""
        if not self.optimization_enabled:
            return sql
        
        # Basic optimizations (in a real implementation, these would be more sophisticated)
        optimizations = [
            self._optimize_redundant_parentheses,
            self._optimize_constant_folding,
            self._optimize_predicate_pushdown
        ]
        
        for optimization in optimizations:
            sql = optimization(sql)
        
        return sql
    
    def _optimize_redundant_parentheses(self, sql: str) -> str:
        """Remove redundant parentheses."""
        # Simplified implementation
        return sql
    
    def _optimize_constant_folding(self, sql: str) -> str:
        """Fold constant expressions."""
        # Simplified implementation
        return sql
    
    def _optimize_predicate_pushdown(self, sql: str) -> str:
        """Push predicates down to reduce intermediate results."""
        # Simplified implementation
        return sql