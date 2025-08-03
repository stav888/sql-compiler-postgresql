'use client';

import { useState } from 'react';

interface CompilationResult {
  success: boolean;
  sql?: string;
  explanation?: string;
  isValid?: boolean;
  warnings?: string[];
  error?: string;
}

export function SqlPlayground() {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState<CompilationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const response = await fetch('/api/compile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      const data = await response.json();
      setResult(data);
    } catch {
      setResult({
        success: false,
        error: 'Network error. Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const examples = [
    'Show me all users who have placed orders in the last 30 days',
    'Find the top 5 products by total sales amount',
    'Get average order value by user role',
    'List products that are out of stock',
  ];

  const handleExampleClick = (example: string) => {
    setPrompt(example);
    setResult(null);
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Input Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
        <form onSubmit={handleSubmit}>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Describe your query in natural language:
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., Show me all users who placed orders in the last month"
            className="w-full p-4 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            rows={4}
            disabled={isLoading}
          />
          
          <div className="flex justify-between items-center mt-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {prompt.length}/1000 characters
            </div>
            <button
              type="submit"
              disabled={!prompt.trim() || isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-medium transition-colors"
            >
              {isLoading ? 'Generating...' : 'Generate SQL'}
            </button>
          </div>
        </form>
      </div>

      {/* Examples */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Try these examples:
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {examples.map((example, index) => (
            <button
              key={index}
              onClick={() => handleExampleClick(example)}
              className="text-left p-3 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg text-sm text-gray-700 dark:text-gray-300 transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* Database Schema */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Available Tables:
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">users</h4>
            <ul className="text-gray-600 dark:text-gray-300 space-y-1">
              <li>• id (integer, PK)</li>
              <li>• name (varchar)</li>
              <li>• email (varchar)</li>
              <li>• role (varchar)</li>
              <li>• created_at (timestamp)</li>
            </ul>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">products</h4>
            <ul className="text-gray-600 dark:text-gray-300 space-y-1">
              <li>• id (integer, PK)</li>
              <li>• name (varchar)</li>
              <li>• description (text)</li>
              <li>• price (integer)</li>
              <li>• category (varchar)</li>
              <li>• in_stock (boolean)</li>
            </ul>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">orders</h4>
            <ul className="text-gray-600 dark:text-gray-300 space-y-1">
              <li>• id (integer, PK)</li>
              <li>• user_id (integer, FK)</li>
              <li>• product_id (integer, FK)</li>
              <li>• quantity (integer)</li>
              <li>• total_amount (integer)</li>
              <li>• status (varchar)</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          {result.success ? (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Generated SQL
                </h3>
                <div className="flex items-center space-x-2">
                  {result.isValid ? (
                    <span className="text-green-600 dark:text-green-400 text-sm">✓ Valid</span>
                  ) : (
                    <span className="text-red-600 dark:text-red-400 text-sm">⚠ Issues found</span>
                  )}
                </div>
              </div>
              
              <div className="bg-gray-900 rounded-lg p-4 mb-4">
                <pre className="text-green-400 font-mono text-sm overflow-x-auto">
                  {result.sql}
                </pre>
              </div>

              {result.explanation && (
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Explanation:</h4>
                  <p className="text-gray-700 dark:text-gray-300">{result.explanation}</p>
                </div>
              )}

              {result.warnings && result.warnings.length > 0 && (
                <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                  <h4 className="font-semibold text-yellow-800 dark:text-yellow-300 mb-2">Warnings:</h4>
                  <ul className="text-yellow-700 dark:text-yellow-300 space-y-1">
                    {result.warnings.map((warning, index) => (
                      <li key={index}>• {warning}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-red-600 dark:text-red-400 mb-2">
                ❌ Error
              </div>
              <p className="text-gray-700 dark:text-gray-300">
                {result.error || 'Failed to generate SQL'}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}