# SQL Compiler for PostgreSQL

A comprehensive SQL compiler that can parse, analyze, and compile SQL statements for PostgreSQL. The compiler includes lexical analysis, parsing, semantic analysis, and code generation with optimization capabilities.

## Features

### Core Components

- **Lexical Analyzer (Lexer)**: Tokenizes SQL input into keywords, identifiers, operators, literals, etc.
- **Parser**: Builds an Abstract Syntax Tree (AST) from tokens using recursive descent parsing
- **Semantic Analyzer**: Performs type checking, symbol table management, and constraint validation
- **Code Generator**: Generates optimized PostgreSQL-compatible SQL with optimization techniques
- **Error Handling**: Comprehensive error reporting with line numbers and context

### PostgreSQL-Specific Support

- PostgreSQL keywords and syntax (ILIKE, ARRAY, JSONB, etc.)
- JSON/JSONB operators (`->`, `->>`, `#>`, `@>`, `?`, etc.)
- Array literals and operations
- Common Table Expressions (CTEs) with RECURSIVE support
- Window functions with OVER clauses
- PostgreSQL data types (SERIAL, TIMESTAMPTZ, UUID, etc.)
- Advanced features like LATERAL joins

### SQL Statement Support

- **SELECT**: Basic and complex queries with JOINs, subqueries, CTEs, window functions
- **INSERT**: Single and multi-row inserts, INSERT FROM SELECT
- **UPDATE**: Single table updates with WHERE clauses
- **DELETE**: Single table deletes with WHERE clauses
- **CREATE TABLE**: Table creation with column definitions and constraints

## Installation

Clone the repository:

```bash
git clone https://github.com/stav888/sql-compiler-postgresql.git
cd sql-compiler-postgresql
```

## Usage

### Command Line Interface

```bash
# Compile a SQL file
python -m src.main examples/simple_select.sql --output optimized.sql

# Run in interactive mode
python -m src.main --interactive

# Analyze and explain a query
python -m src.main examples/complex_query.sql --analyze --explain

# Target specific PostgreSQL version
python -m src.main input.sql --target postgresql-13 --verbose

# Output results in JSON format
python -m src.main input.sql --json
```

### Interactive Mode

```bash
python -m src.main --interactive
```

```
SQL Compiler for PostgreSQL - Interactive Mode
Type 'exit' or 'quit' to exit, 'help' for help

sql> SELECT id, name FROM users WHERE active = TRUE;
✓ Compilation successful

Optimized SQL:
SELECT id, name FROM users WHERE active = TRUE

sql> \analyze
sql> SELECT COUNT(*) FROM orders;
✓ Compilation successful

Optimized SQL:
SELECT COUNT(*) FROM orders

Semantic Analysis:
{
  "tables_used": ["orders"],
  "functions_called": ["count"],
  "complexity_score": 3
}
```

### Programmatic Usage

```python
from src.main import SQLCompiler

compiler = SQLCompiler(target_version="postgresql-14")

# Compile SQL
result = compiler.compile_sql(
    "SELECT id, name FROM users WHERE active = TRUE",
    analyze=True
)

if result["success"]:
    print("Optimized SQL:", result["optimized_sql"])
    print("Semantic Info:", result["semantic_info"])
else:
    print("Errors:", result["errors"])
```

## Examples

### Simple SELECT Query

```sql
SELECT id, name, email, created_at
FROM users
WHERE active = TRUE
  AND created_at > '2023-01-01'
ORDER BY created_at DESC
LIMIT 100;
```

### Complex Query with CTEs and JOINs

```sql
WITH recent_orders AS (
    SELECT 
        user_id,
        COUNT(*) as order_count,
        SUM(total_amount) as total_spent
    FROM orders 
    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
    HAVING COUNT(*) > 5
)
SELECT 
    u.name,
    u.email,
    ro.order_count,
    ro.total_spent
FROM users u
INNER JOIN recent_orders ro ON u.id = ro.user_id
WHERE u.active = TRUE
ORDER BY ro.total_spent DESC;
```

### PostgreSQL-Specific Features

```sql
SELECT 
    id,
    name,
    metadata -> 'profile' ->> 'age' as age,
    tags @> ARRAY['vip'] as is_vip,
    ARRAY[email, phone] as contact_methods,
    ROW_NUMBER() OVER (
        PARTITION BY status 
        ORDER BY created_at DESC
    ) as status_rank
FROM users 
WHERE metadata ? 'profile'
  AND tags && ARRAY['active', 'verified'];
```

## Project Structure

```
sql-compiler-postgresql/
├── src/
│   ├── lexer/
│   │   ├── __init__.py
│   │   └── lexer.py          # SQL tokenization
│   ├── parser/
│   │   ├── __init__.py
│   │   └── parser.py         # AST parsing
│   ├── ast/
│   │   ├── __init__.py
│   │   └── nodes.py          # AST node definitions
│   ├── semantic/
│   │   ├── __init__.py
│   │   └── analyzer.py       # Semantic analysis
│   ├── codegen/
│   │   ├── __init__.py
│   │   └── generator.py      # Code generation
│   └── main.py               # CLI interface
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   └── test_integration.py
├── examples/
│   ├── simple_select.sql
│   ├── complex_query.sql
│   ├── postgresql_features.sql
│   ├── window_functions.sql
│   └── schema.sql
└── README.md
```

## Architecture

### Lexical Analysis

The lexer tokenizes SQL input into a stream of tokens, handling:
- PostgreSQL keywords and identifiers
- String and numeric literals
- Operators (including PostgreSQL-specific ones like `->`, `->>`)
- Comments (single-line `--` and multi-line `/* */`)
- Punctuation and delimiters

### Parsing

The parser uses recursive descent parsing to build an AST from tokens:
- Handles operator precedence correctly
- Supports all major SQL constructs
- Provides detailed error reporting with line/column information
- Extensible design for adding new SQL features

### Semantic Analysis

The semantic analyzer performs:
- Symbol table management for tables, columns, and functions
- Type checking and validation
- Scope resolution for aliases and subqueries
- Query complexity analysis
- Optimization suggestions

### Code Generation

The code generator produces optimized SQL:
- Maintains PostgreSQL compatibility
- Applies basic optimizations
- Configurable for different PostgreSQL versions
- Clean, readable output formatting

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Run specific test categories:

```bash
# Test lexer
python -m pytest tests/test_lexer.py -v

# Test parser
python -m pytest tests/test_parser.py -v

# Integration tests
python -m pytest tests/test_integration.py -v
```

## Error Handling

The compiler provides comprehensive error reporting:

```bash
$ python -m src.main examples/invalid.sql
✗ Failed to compile examples/invalid.sql
  Parser error: Line 1, Column 8: Expected FROM keyword
```

## Supported PostgreSQL Versions

- PostgreSQL 12+
- PostgreSQL 13
- PostgreSQL 14 (default)
- PostgreSQL 15

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Roadmap

- [ ] Advanced query optimization techniques
- [ ] Support for stored procedures and functions
- [ ] Query execution plan analysis
- [ ] Integration with PostgreSQL system catalogs
- [ ] Performance benchmarking tools
- [ ] Additional PostgreSQL-specific features