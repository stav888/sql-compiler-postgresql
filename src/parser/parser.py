"""
SQL Parser - Parses tokens into an Abstract Syntax Tree (AST).
Implements a recursive descent parser for PostgreSQL SQL statements.
"""

from typing import List, Optional, Union, Any
from ..lexer.lexer import Token, TokenType, SQLLexer
from ..ast.nodes import *


class ParseError(Exception):
    """Exception raised when parsing fails."""
    
    def __init__(self, message: str, token: Optional[Token] = None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f"Line {token.line}, Column {token.column}: {message}")
        else:
            super().__init__(message)


class SQLParser:
    """
    SQL Parser for PostgreSQL-compatible SQL statements.
    Parses tokens into an Abstract Syntax Tree (AST).
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else None
    
    def current(self) -> Optional[Token]:
        """Get the current token."""
        return self.current_token
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """Peek at a token at current position + offset."""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def advance(self) -> Token:
        """Move to the next token and return the previous one."""
        prev_token = self.current_token
        if self.position < len(self.tokens) - 1:
            self.position += 1
            self.current_token = self.tokens[self.position]
        return prev_token
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        if not self.current_token:
            return False
        return self.current_token.type in token_types
    
    def consume(self, token_type: TokenType, message: str = None) -> Token:
        """Consume a token of the given type or raise an error."""
        if not self.current_token:
            raise ParseError(message or f"Expected {token_type.value}, got EOF")
        
        if self.current_token.type != token_type:
            raise ParseError(
                message or f"Expected {token_type.value}, got {self.current_token.type.value}",
                self.current_token
            )
        
        return self.advance()
    
    def parse(self) -> List[Statement]:
        """Parse tokens into a list of SQL statements."""
        statements = []
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            # Skip newlines at statement level
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            
            # Consume optional semicolon
            if self.match(TokenType.SEMICOLON):
                self.advance()
        
        return statements
    
    def parse_statement(self) -> Optional[Statement]:
        """Parse a single SQL statement."""
        if not self.current_token:
            return None
        
        if self.match(TokenType.SELECT):
            return self.parse_select_statement()
        elif self.match(TokenType.WITH):
            return self.parse_select_statement()  # WITH clause can start a SELECT
        elif self.match(TokenType.INSERT):
            return self.parse_insert_statement()
        elif self.match(TokenType.UPDATE):
            return self.parse_update_statement()
        elif self.match(TokenType.DELETE):
            return self.parse_delete_statement()
        elif self.match(TokenType.CREATE):
            return self.parse_create_statement()
        else:
            raise ParseError(f"Unexpected token: {self.current_token.value}", self.current_token)
    
    def parse_select_statement(self) -> SelectStatement:
        """Parse a SELECT statement."""
        position = Position(self.current_token.line, self.current_token.column) if self.current_token else None
        
        # Parse optional WITH clause
        with_clause = None
        if self.match(TokenType.WITH):
            with_clause = self.parse_with_clause()
        
        # Parse SELECT
        self.consume(TokenType.SELECT, "Expected SELECT keyword")
        
        # Parse optional DISTINCT
        distinct = False
        if self.match(TokenType.DISTINCT):
            distinct = True
            self.advance()
        
        # Parse select list
        select_list = self.parse_select_list()
        
        # Parse optional FROM clause
        from_clause = None
        if self.match(TokenType.FROM):
            self.advance()
            from_clause = self.parse_from_clause()
        
        # Parse optional WHERE clause
        where_clause = None
        if self.match(TokenType.WHERE):
            self.advance()
            where_clause = self.parse_expression()
        
        # Parse optional GROUP BY clause
        group_by = []
        if self.match(TokenType.GROUP):
            self.advance()
            self.consume(TokenType.BY, "Expected BY after GROUP")
            group_by = self.parse_expression_list()
        
        # Parse optional HAVING clause
        having_clause = None
        if self.match(TokenType.HAVING):
            self.advance()
            having_clause = self.parse_expression()
        
        # Parse optional ORDER BY clause
        order_by = []
        if self.match(TokenType.ORDER):
            self.advance()
            self.consume(TokenType.BY, "Expected BY after ORDER")
            order_by = self.parse_order_by_list()
        
        # Parse optional LIMIT clause
        limit_clause = None
        if self.match(TokenType.LIMIT):
            self.advance()
            limit_clause = self.parse_expression()
        
        # Parse optional OFFSET clause
        offset_clause = None
        if self.match(TokenType.OFFSET):
            self.advance()
            offset_clause = self.parse_expression()
        
        return SelectStatement(
            select_list=select_list,
            from_clause=from_clause,
            where_clause=where_clause,
            group_by=group_by,
            having_clause=having_clause,
            order_by=order_by,
            limit_clause=limit_clause,
            offset_clause=offset_clause,
            distinct=distinct,
            with_clause=with_clause,
            position=position
        )
    
    def parse_with_clause(self) -> WithClause:
        """Parse a WITH clause (CTE)."""
        position = Position(self.current_token.line, self.current_token.column) if self.current_token else None
        
        self.consume(TokenType.WITH, "Expected WITH keyword")
        
        # Parse optional RECURSIVE
        recursive = False
        if self.match(TokenType.RECURSIVE):
            recursive = True
            self.advance()
        
        # Parse CTE list
        ctes = []
        ctes.append(self.parse_cte())
        
        while self.match(TokenType.COMMA):
            self.advance()
            ctes.append(self.parse_cte())
        
        return WithClause(ctes=ctes, recursive=recursive, position=position)
    
    def parse_cte(self) -> CommonTableExpression:
        """Parse a Common Table Expression."""
        position = Position(self.current_token.line, self.current_token.column) if self.current_token else None
        
        # Parse CTE name
        name_token = self.consume(TokenType.IDENTIFIER, "Expected CTE name")
        name = name_token.value
        
        # Parse optional column list
        columns = []
        if self.match(TokenType.LPAREN):
            self.advance()
            columns.append(self.consume(TokenType.IDENTIFIER, "Expected column name").value)
            
            while self.match(TokenType.COMMA):
                self.advance()
                columns.append(self.consume(TokenType.IDENTIFIER, "Expected column name").value)
            
            self.consume(TokenType.RPAREN, "Expected closing parenthesis")
        
        # Parse AS
        self.consume(TokenType.AS, "Expected AS keyword")
        
        # Parse query
        self.consume(TokenType.LPAREN, "Expected opening parenthesis")
        query = self.parse_select_statement()
        self.consume(TokenType.RPAREN, "Expected closing parenthesis")
        
        return CommonTableExpression(name=name, query=query, columns=columns, position=position)
    
    def parse_select_list(self) -> List[Expression]:
        """Parse the SELECT list."""
        expressions = []
        expressions.append(self.parse_select_item())
        
        while self.match(TokenType.COMMA):
            self.advance()
            expressions.append(self.parse_select_item())
        
        return expressions
    
    def parse_select_item(self) -> Expression:
        """Parse a single item in the SELECT list."""
        expr = self.parse_expression()
        
        # Parse optional alias
        if self.match(TokenType.AS):
            self.advance()
            alias_token = self.consume(TokenType.IDENTIFIER, "Expected alias name")
            # For now, we'll just return the expression
            # In a more complete implementation, we'd create an AliasExpression
            return expr
        elif self.match(TokenType.IDENTIFIER):
            # Implicit alias
            alias_token = self.advance()
            return expr
        
        return expr
    
    def parse_from_clause(self) -> Expression:
        """Parse the FROM clause."""
        return self.parse_table_expression()
    
    def parse_table_expression(self) -> Expression:
        """Parse a table expression (can include joins)."""
        left = self.parse_table_reference()
        
        # Parse joins
        while self.match(TokenType.JOIN, TokenType.INNER, TokenType.LEFT, TokenType.RIGHT, TokenType.FULL):
            join_type = "INNER"  # default
            
            if self.match(TokenType.INNER):
                self.advance()
                self.consume(TokenType.JOIN, "Expected JOIN after INNER")
            elif self.match(TokenType.LEFT):
                join_type = "LEFT"
                self.advance()
                if self.match(TokenType.OUTER):
                    self.advance()
                self.consume(TokenType.JOIN, "Expected JOIN after LEFT")
            elif self.match(TokenType.RIGHT):
                join_type = "RIGHT"
                self.advance()
                if self.match(TokenType.OUTER):
                    self.advance()
                self.consume(TokenType.JOIN, "Expected JOIN after RIGHT")
            elif self.match(TokenType.FULL):
                join_type = "FULL"
                self.advance()
                if self.match(TokenType.OUTER):
                    self.advance()
                self.consume(TokenType.JOIN, "Expected JOIN after FULL")
            elif self.match(TokenType.JOIN):
                self.advance()
            
            right = self.parse_table_reference()
            
            # Parse join condition
            condition = None
            using_columns = []
            
            if self.match(TokenType.ON):
                self.advance()
                condition = self.parse_expression()
            elif self.match(TokenType.USING):
                self.advance()
                self.consume(TokenType.LPAREN, "Expected opening parenthesis")
                using_columns.append(self.consume(TokenType.IDENTIFIER, "Expected column name").value)
                
                while self.match(TokenType.COMMA):
                    self.advance()
                    using_columns.append(self.consume(TokenType.IDENTIFIER, "Expected column name").value)
                
                self.consume(TokenType.RPAREN, "Expected closing parenthesis")
            
            left = Join(
                join_type=join_type,
                left=left,
                right=right,
                condition=condition,
                using_columns=using_columns
            )
        
        return left
    
    def parse_table_reference(self) -> Expression:
        """Parse a table reference."""
        # Check for LATERAL
        is_lateral = False
        if self.match(TokenType.LATERAL):
            is_lateral = True
            self.advance()
        
        if self.match(TokenType.LPAREN):
            # Subquery
            self.advance()
            subquery = self.parse_select_statement()
            self.consume(TokenType.RPAREN, "Expected closing parenthesis")
            
            # Parse optional alias
            alias = None
            if self.match(TokenType.AS):
                self.advance()
                alias = self.consume(TokenType.IDENTIFIER, "Expected table alias").value
            elif self.match(TokenType.IDENTIFIER):
                alias = self.advance().value
            
            subquery_expr = Subquery(query=subquery)
            # In a full implementation, we'd have a LATERAL wrapper node
            return subquery_expr
        else:
            # Table name
            table_token = self.consume(TokenType.IDENTIFIER, "Expected table name")
            table_name = table_token.value
            
            # Parse optional alias
            alias = None
            if self.match(TokenType.AS):
                self.advance()
                alias = self.consume(TokenType.IDENTIFIER, "Expected table alias").value
            elif self.match(TokenType.IDENTIFIER):
                alias = self.advance().value
            
            return TableReference(name=table_name, alias=alias)
    
    def parse_expression_list(self) -> List[Expression]:
        """Parse a comma-separated list of expressions."""
        expressions = []
        expressions.append(self.parse_expression())
        
        while self.match(TokenType.COMMA):
            self.advance()
            expressions.append(self.parse_expression())
        
        return expressions
    
    def parse_order_by_list(self) -> List[OrderByItem]:
        """Parse ORDER BY list."""
        items = []
        items.append(self.parse_order_by_item())
        
        while self.match(TokenType.COMMA):
            self.advance()
            items.append(self.parse_order_by_item())
        
        return items
    
    def parse_order_by_item(self) -> OrderByItem:
        """Parse a single ORDER BY item."""
        expression = self.parse_expression()
        
        direction = "ASC"
        if self.match(TokenType.IDENTIFIER):
            if self.current_token.value.upper() in ("ASC", "DESC"):
                direction = self.advance().value.upper()
        
        nulls = None
        if self.match(TokenType.IDENTIFIER) and self.current_token.value.upper() == "NULLS":
            self.advance()
            if self.match(TokenType.IDENTIFIER) and self.current_token.value.upper() in ("FIRST", "LAST"):
                nulls = self.advance().value.upper()
        
        return OrderByItem(expression=expression, direction=direction, nulls=nulls)
    
    def parse_expression(self) -> Expression:
        """Parse an expression (with operator precedence)."""
        return self.parse_or_expression()
    
    def parse_or_expression(self) -> Expression:
        """Parse OR expressions."""
        left = self.parse_and_expression()
        
        while self.match(TokenType.OR):
            operator = self.advance().value
            right = self.parse_and_expression()
            left = BinaryOperation(left=left, operator=operator, right=right)
        
        return left
    
    def parse_and_expression(self) -> Expression:
        """Parse AND expressions."""
        left = self.parse_equality_expression()
        
        while self.match(TokenType.AND):
            operator = self.advance().value
            right = self.parse_equality_expression()
            left = BinaryOperation(left=left, operator=operator, right=right)
        
        return left
    
    def parse_equality_expression(self) -> Expression:
        """Parse equality expressions."""
        left = self.parse_relational_expression()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.advance().value
            right = self.parse_relational_expression()
            left = BinaryOperation(left=left, operator=operator, right=right)
        
        return left
    
    def parse_relational_expression(self) -> Expression:
        """Parse relational expressions."""
        left = self.parse_additive_expression()
        
        while (self.match(TokenType.LESS_THAN, TokenType.LESS_EQUAL, 
                         TokenType.GREATER_THAN, TokenType.GREATER_EQUAL,
                         TokenType.LIKE, TokenType.ILIKE, TokenType.IN)):
            operator = self.advance().value
            right = self.parse_additive_expression()
            left = BinaryOperation(left=left, operator=operator, right=right)
        
        return left
    
    def parse_additive_expression(self) -> Expression:
        """Parse additive expressions."""
        left = self.parse_multiplicative_expression()
        
        while self.match(TokenType.PLUS, TokenType.MINUS, TokenType.CONCAT):
            operator = self.advance().value
            right = self.parse_multiplicative_expression()
            left = BinaryOperation(left=left, operator=operator, right=right)
        
        return left
    
    def parse_multiplicative_expression(self) -> Expression:
        """Parse multiplicative expressions."""
        left = self.parse_json_expression()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.advance().value
            right = self.parse_json_expression()
            left = BinaryOperation(left=left, operator=operator, right=right)
        
        return left
    
    def parse_json_expression(self) -> Expression:
        """Parse JSON expressions (PostgreSQL-specific)."""
        left = self.parse_unary_expression()
        
        while self.match(TokenType.ARROW, TokenType.DOUBLE_ARROW, TokenType.HASH):
            operator = self.advance().value
            right = self.parse_unary_expression()
            left = BinaryOperation(left=left, operator=operator, right=right)
        
        return left
    
    def parse_unary_expression(self) -> Expression:
        """Parse unary expressions."""
        if self.match(TokenType.NOT, TokenType.MINUS, TokenType.PLUS):
            operator = self.advance().value
            operand = self.parse_unary_expression()
            return UnaryOperation(operator=operator, operand=operand)
        
        return self.parse_primary_expression()
    
    def parse_primary_expression(self) -> Expression:
        """Parse primary expressions."""
        if self.match(TokenType.NUMBER):
            value = self.advance().value
            # Try to convert to appropriate numeric type
            if '.' in value or 'e' in value.lower():
                return NumberLiteral(float(value))
            else:
                return NumberLiteral(int(value))
        
        elif self.match(TokenType.STRING):
            value = self.advance().value
            return StringLiteral(value)
        
        elif self.match(TokenType.TRUE):
            self.advance()
            return BooleanLiteral(True)
        
        elif self.match(TokenType.FALSE):
            self.advance()
            return BooleanLiteral(False)
        
        elif self.match(TokenType.NULL):
            self.advance()
            return NullLiteral()
        
        elif self.match(TokenType.IDENTIFIER):
            identifier = self.advance().value
            
            # Handle special PostgreSQL functions/keywords that act like identifiers
            if identifier.upper() in ('CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'NOW'):
                # These can be called with or without parentheses
                if self.match(TokenType.LPAREN):
                    self.advance()
                    arguments = []
                    if not self.match(TokenType.RPAREN):
                        arguments = self.parse_expression_list()
                    self.consume(TokenType.RPAREN, "Expected closing parenthesis")
                    return FunctionCall(name=identifier, arguments=arguments)
                else:
                    return FunctionCall(name=identifier, arguments=[])
            
            # Check for function call
            elif self.match(TokenType.LPAREN):
                self.advance()
                
                # Parse arguments
                arguments = []
                if not self.match(TokenType.RPAREN):
                    # Handle special case of * in function calls like COUNT(*)
                    if self.match(TokenType.MULTIPLY):
                        star_token = self.advance()
                        arguments.append(Identifier(name="*"))
                    else:
                        arguments = self.parse_expression_list()
                
                self.consume(TokenType.RPAREN, "Expected closing parenthesis")
                
                return FunctionCall(name=identifier, arguments=arguments)
            
            # Check for column reference
            elif self.match(TokenType.DOT):
                self.advance()
                column = self.consume(TokenType.IDENTIFIER, "Expected column name").value
                return ColumnReference(table=identifier, column=column)
            
            # Simple identifier
            else:
                return Identifier(name=identifier)
        
        elif self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected closing parenthesis")
            return expr
        
        elif self.match(TokenType.CASE):
            return self.parse_case_expression()
        
        elif self.match(TokenType.ARRAY):
            return self.parse_array_expression()
        
        elif self.match(TokenType.INTERVAL):
            # Handle INTERVAL expressions
            self.advance()
            interval_value = self.consume(TokenType.STRING, "Expected interval value").value
            return StringLiteral(f"INTERVAL '{interval_value}'")
        
        elif self.match(TokenType.MULTIPLY):
            # Handle * as a special identifier (for SELECT *)
            self.advance()
            return Identifier(name="*")
        
        else:
            raise ParseError(f"Unexpected token: {self.current_token.value}", self.current_token)
    
    def parse_case_expression(self) -> CaseExpression:
        """Parse a CASE expression."""
        position = Position(self.current_token.line, self.current_token.column) if self.current_token else None
        
        self.consume(TokenType.CASE, "Expected CASE keyword")
        
        # Parse optional expression after CASE
        case_expr = None
        if not self.match(TokenType.WHEN):
            case_expr = self.parse_expression()
        
        # Parse WHEN clauses
        when_clauses = []
        while self.match(TokenType.WHEN):
            self.advance()
            when_expr = self.parse_expression()
            self.consume(TokenType.THEN, "Expected THEN keyword")
            then_expr = self.parse_expression()
            when_clauses.append((when_expr, then_expr))
        
        # Parse optional ELSE clause
        else_clause = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_clause = self.parse_expression()
        
        self.consume(TokenType.END, "Expected END keyword")
        
        return CaseExpression(
            expression=case_expr,
            when_clauses=when_clauses,
            else_clause=else_clause,
            position=position
        )
    
    def parse_array_expression(self) -> ArrayExpression:
        """Parse a PostgreSQL array expression."""
        position = Position(self.current_token.line, self.current_token.column) if self.current_token else None
        
        self.consume(TokenType.ARRAY, "Expected ARRAY keyword")
        self.consume(TokenType.LBRACKET, "Expected opening bracket")
        
        elements = []
        if not self.match(TokenType.RBRACKET):
            elements = self.parse_expression_list()
        
        self.consume(TokenType.RBRACKET, "Expected closing bracket")
        
        return ArrayExpression(elements=elements, position=position)
    
    def parse_insert_statement(self) -> InsertStatement:
        """Parse an INSERT statement."""
        position = Position(self.current_token.line, self.current_token.column) if self.current_token else None
        
        self.consume(TokenType.INSERT, "Expected INSERT keyword")
        self.consume(TokenType.INTO, "Expected INTO keyword")
        
        # Parse table reference
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name").value
        table = TableReference(name=table_name)
        
        # Parse optional column list
        columns = []
        if self.match(TokenType.LPAREN):
            self.advance()
            columns.append(self.consume(TokenType.IDENTIFIER, "Expected column name").value)
            
            while self.match(TokenType.COMMA):
                self.advance()
                columns.append(self.consume(TokenType.IDENTIFIER, "Expected column name").value)
            
            self.consume(TokenType.RPAREN, "Expected closing parenthesis")
        
        # Parse VALUES or SELECT
        if self.match(TokenType.VALUES):
            self.advance()
            values = []
            
            # Parse value lists
            self.consume(TokenType.LPAREN, "Expected opening parenthesis")
            row = self.parse_expression_list()
            values.append(row)
            self.consume(TokenType.RPAREN, "Expected closing parenthesis")
            
            while self.match(TokenType.COMMA):
                self.advance()
                self.consume(TokenType.LPAREN, "Expected opening parenthesis")
                row = self.parse_expression_list()
                values.append(row)
                self.consume(TokenType.RPAREN, "Expected closing parenthesis")
            
            return InsertStatement(table=table, columns=columns, values=values, position=position)
        
        elif self.match(TokenType.SELECT):
            select_query = self.parse_select_statement()
            return InsertStatement(table=table, columns=columns, select_query=select_query, position=position)
        
        else:
            raise ParseError("Expected VALUES or SELECT after INSERT INTO", self.current_token)
    
    def parse_update_statement(self) -> UpdateStatement:
        """Parse an UPDATE statement."""
        position = Position(self.current_token.line, self.current_token.column) if self.current_token else None
        
        self.consume(TokenType.UPDATE, "Expected UPDATE keyword")
        
        # Parse table reference
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name").value
        table = TableReference(name=table_name)
        
        # Parse SET clause
        self.consume(TokenType.SET, "Expected SET keyword")
        set_clauses = []
        
        column = self.consume(TokenType.IDENTIFIER, "Expected column name").value
        self.consume(TokenType.EQUAL, "Expected = after column name")
        value = self.parse_expression()
        set_clauses.append((column, value))
        
        while self.match(TokenType.COMMA):
            self.advance()
            column = self.consume(TokenType.IDENTIFIER, "Expected column name").value
            self.consume(TokenType.EQUAL, "Expected = after column name")
            value = self.parse_expression()
            set_clauses.append((column, value))
        
        # Parse optional WHERE clause
        where_clause = None
        if self.match(TokenType.WHERE):
            self.advance()
            where_clause = self.parse_expression()
        
        return UpdateStatement(table=table, set_clauses=set_clauses, where_clause=where_clause, position=position)
    
    def parse_delete_statement(self) -> DeleteStatement:
        """Parse a DELETE statement."""
        position = Position(self.current_token.line, self.current_token.column) if self.current_token else None
        
        self.consume(TokenType.DELETE, "Expected DELETE keyword")
        self.consume(TokenType.FROM, "Expected FROM keyword")
        
        # Parse table reference
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name").value
        table = TableReference(name=table_name)
        
        # Parse optional WHERE clause
        where_clause = None
        if self.match(TokenType.WHERE):
            self.advance()
            where_clause = self.parse_expression()
        
        return DeleteStatement(table=table, where_clause=where_clause, position=position)
    
    def parse_create_statement(self) -> Statement:
        """Parse a CREATE statement."""
        self.consume(TokenType.CREATE, "Expected CREATE keyword")
        
        if self.match(TokenType.TABLE):
            return self.parse_create_table_statement()
        else:
            raise ParseError("Only CREATE TABLE is currently supported", self.current_token)
    
    def parse_create_table_statement(self) -> CreateTableStatement:
        """Parse a CREATE TABLE statement."""
        position = Position(self.current_token.line, self.current_token.column) if self.current_token else None
        
        self.consume(TokenType.TABLE, "Expected TABLE keyword")
        
        # Parse table name
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name").value
        
        # Parse column definitions
        self.consume(TokenType.LPAREN, "Expected opening parenthesis")
        
        columns = []
        columns.append(self.parse_column_definition())
        
        while self.match(TokenType.COMMA):
            self.advance()
            # Check if we have a table constraint instead of column definition
            if self.match(TokenType.IDENTIFIER) and self.peek() and self.peek().type == TokenType.IDENTIFIER:
                # This might be a column definition
                columns.append(self.parse_column_definition())
            else:
                # This might be a table constraint - for now, just parse as column
                columns.append(self.parse_column_definition())
        
        self.consume(TokenType.RPAREN, "Expected closing parenthesis")
        
        return CreateTableStatement(table_name=table_name, columns=columns, position=position)
    
    def parse_column_definition(self) -> ColumnDefinition:
        """Parse a column definition."""
        position = Position(self.current_token.line, self.current_token.column) if self.current_token else None
        
        # Parse column name
        column_name = self.consume(TokenType.IDENTIFIER, "Expected column name").value
        
        # Parse data type
        if self.match(TokenType.INTEGER, TokenType.BIGINT, TokenType.SMALLINT, 
                     TokenType.VARCHAR, TokenType.CHAR, TokenType.TEXT, 
                     TokenType.BOOLEAN, TokenType.DATE, TokenType.TIME, 
                     TokenType.TIMESTAMP, TokenType.TIMESTAMPTZ):
            data_type = self.advance().value
        else:
            data_type = self.consume(TokenType.IDENTIFIER, "Expected data type").value
        
        # Handle parameterized types like VARCHAR(255)
        if self.match(TokenType.LPAREN):
            self.advance()
            param = self.consume(TokenType.NUMBER, "Expected type parameter").value
            data_type += f"({param})"
            self.consume(TokenType.RPAREN, "Expected closing parenthesis")
        
        # Parse optional constraints
        constraints = []
        while (self.match(TokenType.IDENTIFIER) and 
               self.current_token.value.upper() in ("NOT", "PRIMARY", "UNIQUE", "DEFAULT", "CHECK") and
               not self.match(TokenType.COMMA, TokenType.RPAREN)):
            constraint = self.current_token.value.upper()
            if constraint == "NOT":
                self.advance()
                if self.match(TokenType.NULL):
                    self.advance()
                    constraints.append("NOT NULL")
                else:
                    raise ParseError("Expected NULL after NOT", self.current_token)
            elif constraint == "PRIMARY":
                self.advance()
                if self.match(TokenType.IDENTIFIER) and self.current_token.value.upper() == "KEY":
                    self.advance()
                    constraints.append("PRIMARY KEY")
                else:
                    raise ParseError("Expected KEY after PRIMARY", self.current_token)
            else:
                constraints.append(constraint)
                self.advance()
        
        return ColumnDefinition(name=column_name, data_type=data_type, constraints=constraints, position=position)


def parse_sql(sql: str) -> List[Statement]:
    """Parse SQL string into AST statements."""
    lexer = SQLLexer(sql)
    tokens = lexer.get_tokens()
    parser = SQLParser(tokens)
    return parser.parse()