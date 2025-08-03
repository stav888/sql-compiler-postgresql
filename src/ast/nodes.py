"""
Abstract Syntax Tree (AST) nodes for SQL statements.
Represents the structure of parsed SQL queries.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from dataclasses import dataclass


class ASTNode(ABC):
    """Base class for all AST nodes."""
    
    @abstractmethod
    def accept(self, visitor):
        """Accept a visitor for the visitor pattern."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the node to a dictionary representation."""
        pass


@dataclass
class Position:
    """Position information for AST nodes."""
    line: int
    column: int


class Expression(ASTNode):
    """Base class for all expressions."""
    
    def __init__(self, position: Optional[Position] = None):
        self.position = position


class Statement(ASTNode):
    """Base class for all SQL statements."""
    
    def __init__(self, position: Optional[Position] = None):
        self.position = position


# Expressions

class Identifier(Expression):
    """Represents an identifier (table name, column name, etc.)."""
    
    def __init__(self, name: str, position: Optional[Position] = None):
        super().__init__(position)
        self.name = name
    
    def accept(self, visitor):
        return visitor.visit_identifier(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Identifier",
            "name": self.name
        }
    
    def __str__(self):
        return self.name


class Literal(Expression):
    """Base class for literal values."""
    
    def __init__(self, value: Any, position: Optional[Position] = None):
        super().__init__(position)
        self.value = value


class StringLiteral(Literal):
    """String literal expression."""
    
    def accept(self, visitor):
        return visitor.visit_string_literal(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "StringLiteral",
            "value": self.value
        }
    
    def __str__(self):
        return f"'{self.value}'"


class NumberLiteral(Literal):
    """Numeric literal expression."""
    
    def accept(self, visitor):
        return visitor.visit_number_literal(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "NumberLiteral",
            "value": self.value
        }
    
    def __str__(self):
        return str(self.value)


class BooleanLiteral(Literal):
    """Boolean literal expression."""
    
    def accept(self, visitor):
        return visitor.visit_boolean_literal(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "BooleanLiteral",
            "value": self.value
        }
    
    def __str__(self):
        return "TRUE" if self.value else "FALSE"


class NullLiteral(Literal):
    """NULL literal expression."""
    
    def __init__(self, position: Optional[Position] = None):
        super().__init__(None, position)
    
    def accept(self, visitor):
        return visitor.visit_null_literal(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "NullLiteral",
            "value": None
        }
    
    def __str__(self):
        return "NULL"


class BinaryOperation(Expression):
    """Binary operation expression (e.g., a + b, a AND b)."""
    
    def __init__(self, left: Expression, operator: str, right: Expression, 
                 position: Optional[Position] = None):
        super().__init__(position)
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_binary_operation(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "BinaryOperation",
            "left": self.left.to_dict(),
            "operator": self.operator,
            "right": self.right.to_dict()
        }
    
    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"


class UnaryOperation(Expression):
    """Unary operation expression (e.g., NOT condition, -value)."""
    
    def __init__(self, operator: str, operand: Expression, 
                 position: Optional[Position] = None):
        super().__init__(position)
        self.operator = operator
        self.operand = operand
    
    def accept(self, visitor):
        return visitor.visit_unary_operation(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "UnaryOperation",
            "operator": self.operator,
            "operand": self.operand.to_dict()
        }
    
    def __str__(self):
        return f"{self.operator} {self.operand}"


class FunctionCall(Expression):
    """Function call expression."""
    
    def __init__(self, name: str, arguments: List[Expression], 
                 position: Optional[Position] = None):
        super().__init__(position)
        self.name = name
        self.arguments = arguments
    
    def accept(self, visitor):
        return visitor.visit_function_call(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "FunctionCall",
            "name": self.name,
            "arguments": [arg.to_dict() for arg in self.arguments]
        }
    
    def __str__(self):
        args = ", ".join(str(arg) for arg in self.arguments)
        return f"{self.name}({args})"


class CaseExpression(Expression):
    """CASE expression."""
    
    def __init__(self, expression: Optional[Expression], when_clauses: List[tuple], 
                 else_clause: Optional[Expression], position: Optional[Position] = None):
        super().__init__(position)
        self.expression = expression  # Optional expression after CASE
        self.when_clauses = when_clauses  # List of (condition, result) tuples
        self.else_clause = else_clause
    
    def accept(self, visitor):
        return visitor.visit_case_expression(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "CaseExpression",
            "expression": self.expression.to_dict() if self.expression else None,
            "when_clauses": [(when.to_dict(), then.to_dict()) for when, then in self.when_clauses],
            "else_clause": self.else_clause.to_dict() if self.else_clause else None
        }


class ArrayExpression(Expression):
    """PostgreSQL array expression."""
    
    def __init__(self, elements: List[Expression], position: Optional[Position] = None):
        super().__init__(position)
        self.elements = elements
    
    def accept(self, visitor):
        return visitor.visit_array_expression(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ArrayExpression",
            "elements": [elem.to_dict() for elem in self.elements]
        }
    
    def __str__(self):
        elements = ", ".join(str(elem) for elem in self.elements)
        return f"ARRAY[{elements}]"


class JSONExpression(Expression):
    """PostgreSQL JSON expression."""
    
    def __init__(self, object_expr: Expression, path_expr: Expression, 
                 operator: str, position: Optional[Position] = None):
        super().__init__(position)
        self.object_expr = object_expr
        self.path_expr = path_expr
        self.operator = operator  # ->, ->>, #>, etc.
    
    def accept(self, visitor):
        return visitor.visit_json_expression(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "JSONExpression",
            "object": self.object_expr.to_dict(),
            "path": self.path_expr.to_dict(),
            "operator": self.operator
        }


# Column and table references

class ColumnReference(Expression):
    """Reference to a table column."""
    
    def __init__(self, table: Optional[str], column: str, 
                 position: Optional[Position] = None):
        super().__init__(position)
        self.table = table
        self.column = column
    
    def accept(self, visitor):
        return visitor.visit_column_reference(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ColumnReference",
            "table": self.table,
            "column": self.column
        }
    
    def __str__(self):
        if self.table:
            return f"{self.table}.{self.column}"
        return self.column


class TableReference(Expression):
    """Reference to a table."""
    
    def __init__(self, name: str, alias: Optional[str] = None, 
                 position: Optional[Position] = None):
        super().__init__(position)
        self.name = name
        self.alias = alias
    
    def accept(self, visitor):
        return visitor.visit_table_reference(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "TableReference",
            "name": self.name,
            "alias": self.alias
        }
    
    def __str__(self):
        if self.alias:
            return f"{self.name} AS {self.alias}"
        return self.name


# Subqueries

class Subquery(Expression):
    """Subquery expression."""
    
    def __init__(self, query: 'SelectStatement', position: Optional[Position] = None):
        super().__init__(position)
        self.query = query
    
    def accept(self, visitor):
        return visitor.visit_subquery(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Subquery",
            "query": self.query.to_dict()
        }


# Window functions

class WindowFunction(Expression):
    """Window function expression."""
    
    def __init__(self, function: FunctionCall, over_clause: 'OverClause', 
                 position: Optional[Position] = None):
        super().__init__(position)
        self.function = function
        self.over_clause = over_clause
    
    def accept(self, visitor):
        return visitor.visit_window_function(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "WindowFunction",
            "function": self.function.to_dict(),
            "over_clause": self.over_clause.to_dict()
        }


class OverClause(ASTNode):
    """OVER clause for window functions."""
    
    def __init__(self, partition_by: Optional[List[Expression]] = None,
                 order_by: Optional[List['OrderByItem']] = None,
                 frame: Optional['WindowFrame'] = None,
                 position: Optional[Position] = None):
        self.partition_by = partition_by or []
        self.order_by = order_by or []
        self.frame = frame
        self.position = position
    
    def accept(self, visitor):
        return visitor.visit_over_clause(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "OverClause",
            "partition_by": [expr.to_dict() for expr in self.partition_by],
            "order_by": [item.to_dict() for item in self.order_by],
            "frame": self.frame.to_dict() if self.frame else None
        }


class WindowFrame(ASTNode):
    """Window frame specification."""
    
    def __init__(self, frame_type: str, start_bound: str, end_bound: Optional[str] = None,
                 position: Optional[Position] = None):
        self.frame_type = frame_type  # ROWS, RANGE, GROUPS
        self.start_bound = start_bound
        self.end_bound = end_bound
        self.position = position
    
    def accept(self, visitor):
        return visitor.visit_window_frame(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "WindowFrame",
            "frame_type": self.frame_type,
            "start_bound": self.start_bound,
            "end_bound": self.end_bound
        }


# Statements

class SelectStatement(Statement):
    """SELECT statement."""
    
    def __init__(self, select_list: List[Expression], from_clause: Optional[Expression] = None,
                 where_clause: Optional[Expression] = None, group_by: Optional[List[Expression]] = None,
                 having_clause: Optional[Expression] = None, order_by: Optional[List['OrderByItem']] = None,
                 limit_clause: Optional[Expression] = None, offset_clause: Optional[Expression] = None,
                 distinct: bool = False, with_clause: Optional['WithClause'] = None,
                 position: Optional[Position] = None):
        super().__init__(position)
        self.select_list = select_list
        self.from_clause = from_clause
        self.where_clause = where_clause
        self.group_by = group_by or []
        self.having_clause = having_clause
        self.order_by = order_by or []
        self.limit_clause = limit_clause
        self.offset_clause = offset_clause
        self.distinct = distinct
        self.with_clause = with_clause
    
    def accept(self, visitor):
        return visitor.visit_select_statement(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "SelectStatement",
            "distinct": self.distinct,
            "with_clause": self.with_clause.to_dict() if self.with_clause else None,
            "select_list": [expr.to_dict() for expr in self.select_list],
            "from_clause": self.from_clause.to_dict() if self.from_clause else None,
            "where_clause": self.where_clause.to_dict() if self.where_clause else None,
            "group_by": [expr.to_dict() for expr in self.group_by],
            "having_clause": self.having_clause.to_dict() if self.having_clause else None,
            "order_by": [item.to_dict() for item in self.order_by],
            "limit_clause": self.limit_clause.to_dict() if self.limit_clause else None,
            "offset_clause": self.offset_clause.to_dict() if self.offset_clause else None
        }


class InsertStatement(Statement):
    """INSERT statement."""
    
    def __init__(self, table: TableReference, columns: Optional[List[str]] = None,
                 values: Optional[List[List[Expression]]] = None,
                 select_query: Optional[SelectStatement] = None,
                 position: Optional[Position] = None):
        super().__init__(position)
        self.table = table
        self.columns = columns or []
        self.values = values or []
        self.select_query = select_query
    
    def accept(self, visitor):
        return visitor.visit_insert_statement(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "InsertStatement",
            "table": self.table.to_dict(),
            "columns": self.columns,
            "values": [[expr.to_dict() for expr in row] for row in self.values],
            "select_query": self.select_query.to_dict() if self.select_query else None
        }


class UpdateStatement(Statement):
    """UPDATE statement."""
    
    def __init__(self, table: TableReference, set_clauses: List[tuple],
                 where_clause: Optional[Expression] = None,
                 position: Optional[Position] = None):
        super().__init__(position)
        self.table = table
        self.set_clauses = set_clauses  # List of (column, value) tuples
        self.where_clause = where_clause
    
    def accept(self, visitor):
        return visitor.visit_update_statement(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "UpdateStatement",
            "table": self.table.to_dict(),
            "set_clauses": [(col, val.to_dict()) for col, val in self.set_clauses],
            "where_clause": self.where_clause.to_dict() if self.where_clause else None
        }


class DeleteStatement(Statement):
    """DELETE statement."""
    
    def __init__(self, table: TableReference, where_clause: Optional[Expression] = None,
                 position: Optional[Position] = None):
        super().__init__(position)
        self.table = table
        self.where_clause = where_clause
    
    def accept(self, visitor):
        return visitor.visit_delete_statement(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "DeleteStatement",
            "table": self.table.to_dict(),
            "where_clause": self.where_clause.to_dict() if self.where_clause else None
        }


class CreateTableStatement(Statement):
    """CREATE TABLE statement."""
    
    def __init__(self, table_name: str, columns: List['ColumnDefinition'],
                 constraints: Optional[List['TableConstraint']] = None,
                 position: Optional[Position] = None):
        super().__init__(position)
        self.table_name = table_name
        self.columns = columns
        self.constraints = constraints or []
    
    def accept(self, visitor):
        return visitor.visit_create_table_statement(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "CreateTableStatement",
            "table_name": self.table_name,
            "columns": [col.to_dict() for col in self.columns],
            "constraints": [constraint.to_dict() for constraint in self.constraints]
        }


# Auxiliary classes

class OrderByItem(ASTNode):
    """ORDER BY item."""
    
    def __init__(self, expression: Expression, direction: str = "ASC",
                 nulls: Optional[str] = None, position: Optional[Position] = None):
        self.expression = expression
        self.direction = direction  # ASC or DESC
        self.nulls = nulls  # FIRST or LAST
        self.position = position
    
    def accept(self, visitor):
        return visitor.visit_order_by_item(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "OrderByItem",
            "expression": self.expression.to_dict(),
            "direction": self.direction,
            "nulls": self.nulls
        }


class WithClause(ASTNode):
    """WITH clause for CTEs."""
    
    def __init__(self, ctes: List['CommonTableExpression'], recursive: bool = False,
                 position: Optional[Position] = None):
        self.ctes = ctes
        self.recursive = recursive
        self.position = position
    
    def accept(self, visitor):
        return visitor.visit_with_clause(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "WithClause",
            "recursive": self.recursive,
            "ctes": [cte.to_dict() for cte in self.ctes]
        }


class CommonTableExpression(ASTNode):
    """Common Table Expression (CTE)."""
    
    def __init__(self, name: str, query: SelectStatement, 
                 columns: Optional[List[str]] = None,
                 position: Optional[Position] = None):
        self.name = name
        self.query = query
        self.columns = columns or []
        self.position = position
    
    def accept(self, visitor):
        return visitor.visit_cte(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "CommonTableExpression",
            "name": self.name,
            "columns": self.columns,
            "query": self.query.to_dict()
        }


class Join(ASTNode):
    """JOIN clause."""
    
    def __init__(self, join_type: str, left: Expression, right: Expression,
                 condition: Optional[Expression] = None,
                 using_columns: Optional[List[str]] = None,
                 position: Optional[Position] = None):
        self.join_type = join_type  # INNER, LEFT, RIGHT, FULL, etc.
        self.left = left
        self.right = right
        self.condition = condition  # ON condition
        self.using_columns = using_columns or []  # USING columns
        self.position = position
    
    def accept(self, visitor):
        return visitor.visit_join(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Join",
            "join_type": self.join_type,
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
            "condition": self.condition.to_dict() if self.condition else None,
            "using_columns": self.using_columns
        }


class ColumnDefinition(ASTNode):
    """Column definition for CREATE TABLE."""
    
    def __init__(self, name: str, data_type: str, constraints: Optional[List[str]] = None,
                 position: Optional[Position] = None):
        self.name = name
        self.data_type = data_type
        self.constraints = constraints or []
        self.position = position
    
    def accept(self, visitor):
        return visitor.visit_column_definition(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ColumnDefinition",
            "name": self.name,
            "data_type": self.data_type,
            "constraints": self.constraints
        }


class TableConstraint(ASTNode):
    """Table constraint for CREATE TABLE."""
    
    def __init__(self, constraint_type: str, name: Optional[str] = None,
                 columns: Optional[List[str]] = None, reference_table: Optional[str] = None,
                 reference_columns: Optional[List[str]] = None,
                 position: Optional[Position] = None):
        self.constraint_type = constraint_type  # PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK
        self.name = name
        self.columns = columns or []
        self.reference_table = reference_table
        self.reference_columns = reference_columns or []
        self.position = position
    
    def accept(self, visitor):
        return visitor.visit_table_constraint(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "TableConstraint",
            "constraint_type": self.constraint_type,
            "name": self.name,
            "columns": self.columns,
            "reference_table": self.reference_table,
            "reference_columns": self.reference_columns
        }