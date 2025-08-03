import OpenAI from 'openai';
import { Schema, SqlCompilationResult, GenerationError, ValidationError } from './types.js';

export class SqlCompiler {
  private openai: OpenAI;
  
  constructor(apiKey: string) {
    if (!apiKey) {
      throw new ValidationError('OpenAI API key is required');
    }
    
    this.openai = new OpenAI({
      apiKey,
    });
  }

  /**
   * Compiles a user prompt into PostgreSQL SQL
   */
  async compileSql(userPrompt: string, schema: Schema): Promise<SqlCompilationResult> {
    try {
      // Validate inputs
      if (!userPrompt?.trim()) {
        throw new ValidationError('User prompt cannot be empty');
      }

      // Build schema context for the AI
      const schemaContext = this.buildSchemaContext(schema);
      
      // Create the AI prompt
      const systemPrompt = `You are an expert PostgreSQL SQL generator. Given a database schema and user request, generate a valid PostgreSQL query.

Database Schema:
${schemaContext}

Rules:
1. Only use tables and columns that exist in the schema
2. Use proper PostgreSQL syntax and functions
3. Include proper JOINs when accessing multiple tables
4. Use parameterized queries when applicable
5. Optimize for performance
6. Return only the SQL query without explanations or markdown formatting

Respond with just the SQL query.`;

      const response = await this.openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        max_tokens: 500,
        temperature: 0.1,
      });

      const generatedSql = response.choices[0]?.message?.content?.trim();
      
      if (!generatedSql) {
        throw new GenerationError('Failed to generate SQL from prompt');
      }

      // Basic validation
      const validation = this.validateSql(generatedSql, schema);
      
      // Generate explanation
      const explanation = await this.generateExplanation(generatedSql, userPrompt);

      return {
        sql: generatedSql,
        explanation,
        isValid: validation.isValid,
        warnings: validation.warnings,
      };

    } catch (error) {
      if (error instanceof ValidationError || error instanceof GenerationError) {
        throw error;
      }
      
      throw new GenerationError(`SQL compilation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Builds a human-readable schema context for the AI
   */
  private buildSchemaContext(schema: Schema): string {
    return schema.tables.map(table => {
      const columns = table.columns.map(col => {
        const attributes = [];
        if (col.primaryKey) attributes.push('PRIMARY KEY');
        if (!col.nullable) attributes.push('NOT NULL');
        if (col.foreignKey) attributes.push(`REFERENCES ${col.foreignKey}`);
        
        return `  ${col.name} ${col.type}${attributes.length ? ' ' + attributes.join(' ') : ''}`;
      }).join('\n');
      
      return `Table: ${table.name}\n${columns}`;
    }).join('\n\n');
  }

  /**
   * Basic SQL validation
   */
  private validateSql(sql: string, schema: Schema): { isValid: boolean; warnings: string[] } {
    const warnings: string[] = [];
    let isValid = true;

    // Check for dangerous keywords
    const dangerousKeywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE'];
    const upperSql = sql.toUpperCase();
    
    for (const keyword of dangerousKeywords) {
      if (upperSql.includes(keyword)) {
        warnings.push(`Contains potentially dangerous keyword: ${keyword}`);
        if (['DROP', 'TRUNCATE', 'ALTER', 'CREATE'].includes(keyword)) {
          isValid = false;
        }
      }
    }

    // Check for table existence
    const tableNames = schema.tables.map(t => t.name.toLowerCase());
    const sqlWords = sql.toLowerCase().split(/\s+/);
    
    for (const word of sqlWords) {
      // Simple heuristic to find table references
      if (word.match(/^[a-z_][a-z0-9_]*$/) && !['select', 'from', 'where', 'and', 'or', 'in', 'on', 'as'].includes(word)) {
        if (tableNames.includes(word) === false && word.length > 2) {
          // This might be a table name that doesn't exist
          // warnings.push(`Possible reference to unknown table: ${word}`);
        }
      }
    }

    return { isValid, warnings };
  }

  /**
   * Generate an explanation for the SQL query
   */
  private async generateExplanation(sql: string, userPrompt: string): Promise<string> {
    try {
      const response = await this.openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [
          {
            role: 'system',
            content: 'You are a database expert. Explain the given SQL query in simple terms, focusing on what data it retrieves and how.'
          },
          {
            role: 'user',
            content: `User asked: "${userPrompt}"\n\nGenerated SQL:\n${sql}\n\nPlease explain what this query does:`
          }
        ],
        max_tokens: 200,
        temperature: 0.3,
      });

      return response.choices[0]?.message?.content?.trim() || 'No explanation available';
    } catch (error) {
      return 'Explanation generation failed';
    }
  }
}