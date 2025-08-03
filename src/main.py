#!/usr/bin/env python3
"""
SQL Compiler for PostgreSQL
Main entry point for the SQL compiler CLI.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Optional

from .lexer.lexer import SQLLexer, LexerError
from .parser.parser import SQLParser, ParseError, parse_sql
from .ast.nodes import Statement
from .semantic.analyzer import SemanticAnalyzer, SemanticError
from .codegen.generator import CodeGenerator


class SQLCompiler:
    """Main SQL Compiler class."""
    
    def __init__(self, target_version: str = "postgresql-14"):
        self.target_version = target_version
        self.semantic_analyzer = SemanticAnalyzer()
        self.code_generator = CodeGenerator(target_version)
    
    def compile_sql(self, sql: str, analyze: bool = False, explain: bool = False) -> dict:
        """
        Compile SQL statement and return results.
        
        Args:
            sql: SQL statement to compile
            analyze: Whether to perform semantic analysis
            explain: Whether to generate execution plan explanation
            
        Returns:
            Dictionary containing compilation results
        """
        result = {
            "success": False,
            "tokens": [],
            "ast": [],
            "semantic_info": None,
            "optimized_sql": None,
            "errors": []
        }
        
        try:
            # Lexical analysis
            lexer = SQLLexer(sql)
            tokens = lexer.get_tokens()
            result["tokens"] = [
                {
                    "type": token.type.value,
                    "value": token.value,
                    "line": token.line,
                    "column": token.column
                }
                for token in tokens
            ]
            
            # Parsing
            parser = SQLParser(tokens)
            statements = parser.parse()
            result["ast"] = [stmt.to_dict() for stmt in statements]
            
            if analyze and statements:
                # Semantic analysis
                try:
                    semantic_info = self.semantic_analyzer.analyze(statements)
                    result["semantic_info"] = semantic_info
                except SemanticError as e:
                    result["errors"].append(f"Semantic error: {e}")
                    return result
            
            # Code generation
            if statements:
                optimized_sql = self.code_generator.generate(statements)
                result["optimized_sql"] = optimized_sql
            
            result["success"] = True
            
        except LexerError as e:
            result["errors"].append(f"Lexer error: {e}")
        except ParseError as e:
            result["errors"].append(f"Parser error: {e}")
        except Exception as e:
            result["errors"].append(f"Unexpected error: {e}")
        
        return result
    
    def compile_file(self, file_path: Path, output_path: Optional[Path] = None,
                    analyze: bool = False, explain: bool = False) -> dict:
        """
        Compile SQL file and optionally save optimized output.
        
        Args:
            file_path: Path to input SQL file
            output_path: Optional path to save optimized SQL
            analyze: Whether to perform semantic analysis
            explain: Whether to generate execution plan explanation
            
        Returns:
            Dictionary containing compilation results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql = f.read()
        except FileNotFoundError:
            return {
                "success": False,
                "errors": [f"File not found: {file_path}"]
            }
        except Exception as e:
            return {
                "success": False,
                "errors": [f"Error reading file: {e}"]
            }
        
        result = self.compile_sql(sql, analyze, explain)
        
        # Save optimized SQL if requested and compilation was successful
        if output_path and result["success"] and result["optimized_sql"]:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result["optimized_sql"])
                result["output_file"] = str(output_path)
            except Exception as e:
                result["errors"].append(f"Error writing output file: {e}")
        
        return result


def interactive_mode():
    """Run the compiler in interactive mode."""
    compiler = SQLCompiler()
    
    print("SQL Compiler for PostgreSQL - Interactive Mode")
    print("Type 'exit' or 'quit' to exit, 'help' for help")
    print()
    
    while True:
        try:
            sql = input("sql> ").strip()
            
            if sql.lower() in ('exit', 'quit'):
                break
            elif sql.lower() == 'help':
                print("Commands:")
                print("  exit, quit     - Exit the interactive mode")
                print("  help           - Show this help message")
                print("  \\analyze       - Toggle semantic analysis")
                print("  \\explain       - Toggle execution plan explanation")
                print("  <SQL>          - Compile SQL statement")
                print()
                continue
            elif not sql:
                continue
            
            # Handle special commands
            analyze = False
            explain = False
            if sql.startswith('\\'):
                if sql == '\\analyze':
                    analyze = True
                    continue
                elif sql == '\\explain':
                    explain = True
                    continue
            
            result = compiler.compile_sql(sql, analyze, explain)
            
            if result["success"]:
                print("✓ Compilation successful")
                if result["optimized_sql"]:
                    print("\nOptimized SQL:")
                    print(result["optimized_sql"])
                if result["semantic_info"]:
                    print("\nSemantic Analysis:")
                    print(json.dumps(result["semantic_info"], indent=2))
            else:
                print("✗ Compilation failed")
                for error in result["errors"]:
                    print(f"  {error}")
            
            print()
            
        except KeyboardInterrupt:
            print("\nUse 'exit' or 'quit' to exit")
            continue
        except EOFError:
            break
    
    print("Goodbye!")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="SQL Compiler for PostgreSQL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compile a SQL file
  python -m src.main input.sql --output optimized.sql
  
  # Run in interactive mode
  python -m src.main --interactive
  
  # Analyze and explain a query
  python -m src.main query.sql --analyze --explain
  
  # Target specific PostgreSQL version
  python -m src.main input.sql --target postgresql-13
        """
    )
    
    parser.add_argument('input_file', nargs='?', type=Path,
                       help='Input SQL file to compile')
    parser.add_argument('-o', '--output', type=Path,
                       help='Output file for optimized SQL')
    parser.add_argument('-t', '--target', default='postgresql-14',
                       choices=['postgresql-12', 'postgresql-13', 'postgresql-14', 'postgresql-15'],
                       help='Target PostgreSQL version')
    parser.add_argument('-a', '--analyze', action='store_true',
                       help='Perform semantic analysis')
    parser.add_argument('-e', '--explain', action='store_true',
                       help='Generate execution plan explanation')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('-j', '--json', action='store_true',
                       help='Output results in JSON format')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Require input file for non-interactive mode
    if not args.input_file:
        parser.error("Input file is required unless running in interactive mode")
    
    # Initialize compiler
    compiler = SQLCompiler(target_version=args.target)
    
    # Compile file
    result = compiler.compile_file(
        file_path=args.input_file,
        output_path=args.output,
        analyze=args.analyze,
        explain=args.explain
    )
    
    # Output results
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            print(f"✓ Successfully compiled {args.input_file}")
            
            if args.verbose:
                print(f"\nTokens: {len(result['tokens'])}")
                print(f"AST nodes: {len(result['ast'])}")
                
                if result["semantic_info"]:
                    print("\nSemantic Analysis:")
                    print(json.dumps(result["semantic_info"], indent=2))
            
            if result["optimized_sql"]:
                if not args.output:
                    print("\nOptimized SQL:")
                    print(result["optimized_sql"])
                else:
                    print(f"Optimized SQL written to {args.output}")
        else:
            print(f"✗ Failed to compile {args.input_file}")
            for error in result["errors"]:
                print(f"  {error}")
            sys.exit(1)


if __name__ == "__main__":
    main()