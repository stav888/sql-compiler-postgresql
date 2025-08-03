"""
Semantic Analyzer for SQL statements.
Performs type checking, symbol table management, and constraint validation.
"""

from typing import List, Dict, Any, Optional, Set
from ..ast.nodes import *


class SemanticError(Exception):
    """Exception raised for semantic analysis errors."""
    
    def __init__(self, message: str, node: Optional[ASTNode] = None):
        self.message = message
        self.node = node
        super().__init__(message)


class SymbolTable:
    """Symbol table for managing table and column information."""
    
    def __init__(self):
        self.tables: Dict[str, Dict[str, Any]] = {}
        self.aliases: Dict[str, str] = {}  # alias -> table_name
        self.functions: Dict[str, Dict[str, Any]] = {}
        self.scopes: List[Dict[str, Any]] = [{}]  # Stack of scopes for subqueries
    
    def add_table(self, name: str, columns: List[str], alias: Optional[str] = None):
        """Add a table to the symbol table."""
        self.tables[name] = {
            "columns": columns,
            "alias": alias
        }
        if alias:
            self.aliases[alias] = name
    
    def add_function(self, name: str, return_type: str, arg_types: List[str]):
        """Add a function to the symbol table."""
        self.functions[name.lower()] = {
            "return_type": return_type,
            "arg_types": arg_types
        }
    
    def get_table(self, name: str) -> Optional[Dict[str, Any]]:
        """Get table information by name or alias."""
        if name in self.tables:
            return self.tables[name]
        elif name in self.aliases:
            return self.tables[self.aliases[name]]
        return None
    
    def has_column(self, table: str, column: str) -> bool:
        """Check if a table has a specific column."""
        table_info = self.get_table(table)
        if table_info:
            return column in table_info["columns"]
        return False
    
    def get_column_type(self, table: str, column: str) -> Optional[str]:
        """Get the type of a column (simplified for now)."""
        if self.has_column(table, column):
            return "unknown"  # In a real implementation, this would return actual types
        return None
    
    def push_scope(self):
        """Push a new scope for subquery analysis."""
        self.scopes.append({})
    
    def pop_scope(self):
        """Pop the current scope."""
        if len(self.scopes) > 1:
            self.scopes.pop()
    
    def add_to_scope(self, name: str, info: Dict[str, Any]):
        """Add a symbol to the current scope."""
        self.scopes[-1][name] = info
    
    def lookup_in_scope(self, name: str) -> Optional[Dict[str, Any]]:
        """Look up a symbol in the current scope stack."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None


class SemanticAnalyzer:
    """
    Semantic analyzer for SQL statements.
    Performs type checking, symbol resolution, and validation.
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self._init_builtin_functions()
    
    def _init_builtin_functions(self):
        """Initialize built-in PostgreSQL functions."""
        # String functions
        self.symbol_table.add_function("length", "integer", ["text"])
        self.symbol_table.add_function("upper", "text", ["text"])
        self.symbol_table.add_function("lower", "text", ["text"])
        self.symbol_table.add_function("substring", "text", ["text", "integer", "integer"])
        
        # Numeric functions
        self.symbol_table.add_function("abs", "numeric", ["numeric"])
        self.symbol_table.add_function("ceil", "integer", ["numeric"])
        self.symbol_table.add_function("floor", "integer", ["numeric"])
        self.symbol_table.add_function("round", "numeric", ["numeric", "integer"])
        
        # Aggregate functions
        self.symbol_table.add_function("count", "bigint", ["any"])
        self.symbol_table.add_function("sum", "numeric", ["numeric"])
        self.symbol_table.add_function("avg", "numeric", ["numeric"])
        self.symbol_table.add_function("min", "any", ["any"])
        self.symbol_table.add_function("max", "any", ["any"])
        
        # Date/time functions
        self.symbol_table.add_function("now", "timestamp", [])
        self.symbol_table.add_function("current_date", "date", [])
        self.symbol_table.add_function("current_time", "time", [])
        
        # JSON functions (PostgreSQL-specific)
        self.symbol_table.add_function("json_extract_path", "json", ["json", "text"])
        self.symbol_table.add_function("jsonb_extract_path", "jsonb", ["jsonb", "text"])
    
    def analyze(self, statements: List[Statement]) -> Dict[str, Any]:
        """
        Analyze a list of SQL statements.
        
        Returns:
            Dictionary containing analysis results
        """
        self.errors = []
        self.warnings = []
        
        analysis_result = {
            "tables_used": set(),
            "columns_accessed": set(),
            "functions_called": set(),
            "join_types": set(),
            "complexity_score": 0,
            "optimization_suggestions": [],
            "errors": [],
            "warnings": []
        }
        
        for statement in statements:
            try:
                self._analyze_statement(statement, analysis_result)
            except SemanticError as e:
                self.errors.append(str(e))
        
        analysis_result["errors"] = self.errors
        analysis_result["warnings"] = self.warnings
        analysis_result["tables_used"] = list(analysis_result["tables_used"])
        analysis_result["columns_accessed"] = list(analysis_result["columns_accessed"])
        analysis_result["functions_called"] = list(analysis_result["functions_called"])
        analysis_result["join_types"] = list(analysis_result["join_types"])
        
        return analysis_result
    
    def _analyze_statement(self, statement: Statement, result: Dict[str, Any]):
        """Analyze a single statement."""
        if isinstance(statement, SelectStatement):
            self._analyze_select_statement(statement, result)
        elif isinstance(statement, InsertStatement):
            self._analyze_insert_statement(statement, result)
        elif isinstance(statement, UpdateStatement):
            self._analyze_update_statement(statement, result)
        elif isinstance(statement, DeleteStatement):
            self._analyze_delete_statement(statement, result)
        elif isinstance(statement, CreateTableStatement):
            self._analyze_create_table_statement(statement, result)
    
    def _analyze_select_statement(self, stmt: SelectStatement, result: Dict[str, Any]):
        """Analyze a SELECT statement."""
        # Analyze WITH clause (CTEs)
        if stmt.with_clause:
            self._analyze_with_clause(stmt.with_clause, result)
        
        # Analyze FROM clause first to build symbol table
        if stmt.from_clause:
            self._analyze_from_clause(stmt.from_clause, result)
        
        # Analyze SELECT list
        for expr in stmt.select_list:
            self._analyze_expression(expr, result)
        
        # Analyze WHERE clause
        if stmt.where_clause:
            self._analyze_expression(stmt.where_clause, result)
        
        # Analyze GROUP BY
        for expr in stmt.group_by:
            self._analyze_expression(expr, result)
        
        # Analyze HAVING clause
        if stmt.having_clause:
            self._analyze_expression(stmt.having_clause, result)
        
        # Analyze ORDER BY
        for order_item in stmt.order_by:
            self._analyze_expression(order_item.expression, result)
        
        # Analyze LIMIT and OFFSET
        if stmt.limit_clause:
            self._analyze_expression(stmt.limit_clause, result)
        if stmt.offset_clause:
            self._analyze_expression(stmt.offset_clause, result)
        
        # Update complexity score
        result["complexity_score"] += self._calculate_select_complexity(stmt)
        
        # Generate optimization suggestions
        self._suggest_select_optimizations(stmt, result)
    
    def _analyze_with_clause(self, with_clause: WithClause, result: Dict[str, Any]):
        """Analyze WITH clause (CTEs)."""
        for cte in with_clause.ctes:
            # Analyze the CTE query
            self.symbol_table.push_scope()
            self._analyze_select_statement(cte.query, result)
            self.symbol_table.pop_scope()
            
            # Add CTE to symbol table as a temporary table
            columns = cte.columns if cte.columns else ["*"]  # Simplified
            self.symbol_table.add_table(cte.name, columns)
    
    def _analyze_from_clause(self, from_clause: Expression, result: Dict[str, Any]):
        """Analyze FROM clause."""
        if isinstance(from_clause, TableReference):
            result["tables_used"].add(from_clause.name)
            # In a real implementation, we'd look up table schema from database
            # For now, assume some common columns
            common_columns = ["id", "name", "created_at", "updated_at"]
            self.symbol_table.add_table(from_clause.name, common_columns, from_clause.alias)
        
        elif isinstance(from_clause, Join):
            result["join_types"].add(from_clause.join_type)
            self._analyze_from_clause(from_clause.left, result)
            self._analyze_from_clause(from_clause.right, result)
            
            if from_clause.condition:
                self._analyze_expression(from_clause.condition, result)
        
        elif isinstance(from_clause, Subquery):
            self.symbol_table.push_scope()
            self._analyze_select_statement(from_clause.query, result)
            self.symbol_table.pop_scope()
    
    def _analyze_expression(self, expr: Expression, result: Dict[str, Any]):
        """Analyze an expression."""
        if isinstance(expr, ColumnReference):
            if expr.table:
                result["columns_accessed"].add(f"{expr.table}.{expr.column}")
                if not self.symbol_table.has_column(expr.table, expr.column):
                    self.warnings.append(f"Column {expr.table}.{expr.column} not found in table schema")
            else:
                result["columns_accessed"].add(expr.column)
        
        elif isinstance(expr, FunctionCall):
            result["functions_called"].add(expr.name)
            func_info = self.symbol_table.functions.get(expr.name.lower())
            if not func_info:
                self.warnings.append(f"Unknown function: {expr.name}")
            elif len(expr.arguments) < len(func_info["arg_types"]):
                self.errors.append(f"Function {expr.name} expects {len(func_info['arg_types'])} arguments, got {len(expr.arguments)}")
            
            for arg in expr.arguments:
                self._analyze_expression(arg, result)
        
        elif isinstance(expr, BinaryOperation):
            self._analyze_expression(expr.left, result)
            self._analyze_expression(expr.right, result)
            self._validate_binary_operation(expr)
        
        elif isinstance(expr, UnaryOperation):
            self._analyze_expression(expr.operand, result)
        
        elif isinstance(expr, CaseExpression):
            if expr.expression:
                self._analyze_expression(expr.expression, result)
            for when_expr, then_expr in expr.when_clauses:
                self._analyze_expression(when_expr, result)
                self._analyze_expression(then_expr, result)
            if expr.else_clause:
                self._analyze_expression(expr.else_clause, result)
        
        elif isinstance(expr, ArrayExpression):
            for element in expr.elements:
                self._analyze_expression(element, result)
        
        elif isinstance(expr, Subquery):
            self.symbol_table.push_scope()
            self._analyze_select_statement(expr.query, result)
            self.symbol_table.pop_scope()
    
    def _analyze_insert_statement(self, stmt: InsertStatement, result: Dict[str, Any]):
        """Analyze an INSERT statement."""
        result["tables_used"].add(stmt.table.name)
        
        if stmt.values:
            for row in stmt.values:
                for expr in row:
                    self._analyze_expression(expr, result)
        
        if stmt.select_query:
            self._analyze_select_statement(stmt.select_query, result)
    
    def _analyze_update_statement(self, stmt: UpdateStatement, result: Dict[str, Any]):
        """Analyze an UPDATE statement."""
        result["tables_used"].add(stmt.table.name)
        
        for column, expr in stmt.set_clauses:
            result["columns_accessed"].add(f"{stmt.table.name}.{column}")
            self._analyze_expression(expr, result)
        
        if stmt.where_clause:
            self._analyze_expression(stmt.where_clause, result)
    
    def _analyze_delete_statement(self, stmt: DeleteStatement, result: Dict[str, Any]):
        """Analyze a DELETE statement."""
        result["tables_used"].add(stmt.table.name)
        
        if stmt.where_clause:
            self._analyze_expression(stmt.where_clause, result)
    
    def _analyze_create_table_statement(self, stmt: CreateTableStatement, result: Dict[str, Any]):
        """Analyze a CREATE TABLE statement."""
        columns = [col.name for col in stmt.columns]
        self.symbol_table.add_table(stmt.table_name, columns)
        result["tables_used"].add(stmt.table_name)
    
    def _validate_binary_operation(self, expr: BinaryOperation):
        """Validate binary operations for type compatibility."""
        # Simplified type checking - in a real implementation, this would be more sophisticated
        arithmetic_ops = ['+', '-', '*', '/', '%']
        comparison_ops = ['=', '!=', '<>', '<', '<=', '>', '>=']
        logical_ops = ['AND', 'OR']
        
        if expr.operator in arithmetic_ops:
            # Both operands should be numeric
            pass  # Simplified - would check actual types
        elif expr.operator in comparison_ops:
            # Operands should be comparable
            pass  # Simplified - would check type compatibility
        elif expr.operator in logical_ops:
            # Both operands should be boolean
            pass  # Simplified - would check boolean types
    
    def _calculate_select_complexity(self, stmt: SelectStatement) -> int:
        """Calculate complexity score for a SELECT statement."""
        score = 1  # Base score
        
        # Add complexity for each clause
        if stmt.from_clause:
            score += 1
        if stmt.where_clause:
            score += 2
        if stmt.group_by:
            score += len(stmt.group_by)
        if stmt.having_clause:
            score += 2
        if stmt.order_by:
            score += len(stmt.order_by)
        if stmt.with_clause:
            score += len(stmt.with_clause.ctes) * 3
        
        # Add complexity for joins
        if stmt.from_clause and isinstance(stmt.from_clause, Join):
            score += self._count_joins(stmt.from_clause) * 2
        
        return score
    
    def _count_joins(self, expr: Expression) -> int:
        """Count the number of joins in an expression."""
        if isinstance(expr, Join):
            return 1 + self._count_joins(expr.left) + self._count_joins(expr.right)
        return 0
    
    def _suggest_select_optimizations(self, stmt: SelectStatement, result: Dict[str, Any]):
        """Generate optimization suggestions for SELECT statements."""
        suggestions = result["optimization_suggestions"]
        
        # Suggest adding LIMIT for potentially large result sets
        if not stmt.limit_clause and not stmt.group_by:
            suggestions.append("Consider adding LIMIT clause to prevent large result sets")
        
        # Suggest indexes for WHERE clause columns
        if stmt.where_clause and isinstance(stmt.where_clause, BinaryOperation):
            if isinstance(stmt.where_clause.left, ColumnReference):
                suggestions.append(f"Consider adding index on {stmt.where_clause.left.column}")
        
        # Suggest avoiding SELECT *
        for expr in stmt.select_list:
            if isinstance(expr, Identifier) and expr.name == "*":
                suggestions.append("Consider specifying column names instead of SELECT *")
        
        # Suggest using INNER JOIN instead of WHERE for joins
        if stmt.where_clause and stmt.from_clause:
            suggestions.append("Consider using explicit JOIN syntax instead of WHERE clause joins")