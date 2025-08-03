import { z } from 'zod';

// Schema validation
export const ColumnSchema = z.object({
  name: z.string(),
  type: z.string(),
  nullable: z.boolean().default(false),
  primaryKey: z.boolean().default(false),
  foreignKey: z.string().optional(),
});

export const TableSchema = z.object({
  name: z.string(),
  columns: z.array(ColumnSchema),
});

export const DatabaseSchema = z.object({
  tables: z.array(TableSchema),
});

export type Column = z.infer<typeof ColumnSchema>;
export type Table = z.infer<typeof TableSchema>;
export type Schema = z.infer<typeof DatabaseSchema>;

// SQL compilation result
export interface SqlCompilationResult {
  sql: string;
  explanation: string;
  isValid: boolean;
  warnings: string[];
}

// Error types
export class SqlCompilerError extends Error {
  constructor(message: string, public code: string) {
    super(message);
    this.name = 'SqlCompilerError';
  }
}

export class ValidationError extends SqlCompilerError {
  constructor(message: string) {
    super(message, 'VALIDATION_ERROR');
  }
}

export class GenerationError extends SqlCompilerError {
  constructor(message: string) {
    super(message, 'GENERATION_ERROR');
  }
}