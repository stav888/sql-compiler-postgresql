import { NextRequest, NextResponse } from 'next/server';
import { SqlCompiler, ValidationError, GenerationError } from '@sql-compiler/core';
import { z } from 'zod';
import { rateLimit } from '@/lib/rate-limit';
import { getSchemaForCompilation } from '@/lib/schema-helper';

// Request validation schema
const CompileRequestSchema = z.object({
  prompt: z.string().min(1).max(1000),
  schemaName: z.string().optional().default('default'),
});

export async function POST(request: NextRequest) {
  try {
    // Rate limiting
    const rateLimitResult = await rateLimit(request);
    if (!rateLimitResult.success) {
      return NextResponse.json(
        { error: 'Too many requests. Please try again later.' },
        { status: 429 }
      );
    }

    // Validate request body
    const body = await request.json();
    const { prompt, schemaName } = CompileRequestSchema.parse(body);

    // Get OpenAI API key (server-only)
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      console.error('OPENAI_API_KEY not configured');
      return NextResponse.json(
        { error: 'Service configuration error' },
        { status: 500 }
      );
    }

    // Initialize SQL compiler
    const compiler = new SqlCompiler(apiKey);
    
    // Get the database schema
    const schema = getSchemaForCompilation(schemaName);

    // Compile SQL
    const result = await compiler.compileSql(prompt, schema);

    // Log for monitoring (hash the prompt for privacy)
    console.log('SQL compilation request:', {
      promptLength: prompt.length,
      schemaName,
      isValid: result.isValid,
      hasWarnings: result.warnings.length > 0,
      timestamp: new Date().toISOString(),
    });

    return NextResponse.json({
      success: true,
      sql: result.sql,
      explanation: result.explanation,
      isValid: result.isValid,
      warnings: result.warnings,
    });

  } catch (error) {
    console.error('SQL compilation error:', error);

    if (error instanceof ValidationError) {
      return NextResponse.json(
        { error: error.message },
        { status: 400 }
      );
    }

    if (error instanceof GenerationError) {
      return NextResponse.json(
        { error: 'Failed to generate SQL. Please try rephrasing your request.' },
        { status: 422 }
      );
    }

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request format', details: error.issues },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}