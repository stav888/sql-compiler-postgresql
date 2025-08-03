import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';

if (!process.env.DATABASE_URL) {
  throw new Error('DATABASE_URL environment variable is required');
}

// Create connection pool with security settings
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 10000,
  // Security settings
  statement_timeout: 5000, // 5 second timeout
  query_timeout: 5000,
});

// Configure security on each new connection
pool.on('connect', (client) => {
  // Set read-only mode and timeout for safety
  client.query('SET default_transaction_read_only = true');
  client.query('SET statement_timeout = 5000');
});

export const db = drizzle(pool);
export { pool };