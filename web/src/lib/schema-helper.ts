import { Schema } from '@sql-compiler/core';

// Schema helper to provide database schema for compilation
export function getSchemaForCompilation(schemaName: string = 'default'): Schema {
  // In a real application, this would fetch the schema from the database
  // For demo purposes, we'll return a predefined schema that matches our Drizzle schema
  
  if (schemaName === 'default') {
    return {
      tables: [
        {
          name: 'users',
          columns: [
            { name: 'id', type: 'integer', nullable: false, primaryKey: true },
            { name: 'name', type: 'varchar(100)', nullable: false, primaryKey: false },
            { name: 'email', type: 'varchar(255)', nullable: false, primaryKey: false },
            { name: 'role', type: 'varchar(50)', nullable: true, primaryKey: false },
            { name: 'created_at', type: 'timestamp', nullable: true, primaryKey: false },
            { name: 'updated_at', type: 'timestamp', nullable: true, primaryKey: false },
          ],
        },
        {
          name: 'products',
          columns: [
            { name: 'id', type: 'integer', nullable: false, primaryKey: true },
            { name: 'name', type: 'varchar(200)', nullable: false, primaryKey: false },
            { name: 'description', type: 'text', nullable: true, primaryKey: false },
            { name: 'price', type: 'integer', nullable: false, primaryKey: false },
            { name: 'category', type: 'varchar(100)', nullable: true, primaryKey: false },
            { name: 'in_stock', type: 'boolean', nullable: true, primaryKey: false },
            { name: 'created_at', type: 'timestamp', nullable: true, primaryKey: false },
          ],
        },
        {
          name: 'orders',
          columns: [
            { name: 'id', type: 'integer', nullable: false, primaryKey: true },
            { name: 'user_id', type: 'integer', nullable: false, primaryKey: false, foreignKey: 'users(id)' },
            { name: 'product_id', type: 'integer', nullable: false, primaryKey: false, foreignKey: 'products(id)' },
            { name: 'quantity', type: 'integer', nullable: false, primaryKey: false },
            { name: 'total_amount', type: 'integer', nullable: false, primaryKey: false },
            { name: 'status', type: 'varchar(50)', nullable: true, primaryKey: false },
            { name: 'created_at', type: 'timestamp', nullable: true, primaryKey: false },
          ],
        },
      ],
    };
  }
  
  throw new Error(`Unknown schema: ${schemaName}`);
}