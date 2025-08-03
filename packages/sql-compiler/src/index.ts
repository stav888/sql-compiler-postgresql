export * from './types.js';
export * from './compiler.js';

// Convenience export for the main function
import { SqlCompiler } from './compiler.js';
export { SqlCompiler };

// Create a simple factory function
export function createSqlCompiler(apiKey: string) {
  return new SqlCompiler(apiKey);
}

// Export a convenience function that matches the problem statement signature
export async function compileSql(userPrompt: string, schema: any, apiKey: string) {
  const compiler = new SqlCompiler(apiKey);
  return compiler.compileSql(userPrompt, schema);
}