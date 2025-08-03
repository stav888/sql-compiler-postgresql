'use client';

import { SqlPlayground } from '@/components/SqlPlayground';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-4">
            PostgreSQL SQL Compiler
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Transform natural language into optimized PostgreSQL queries using AI. 
            Simply describe what data you need, and get production-ready SQL with explanations.
          </p>
        </div>

        {/* Main Content */}
        <SqlPlayground />

        {/* Features */}
        <div className="mt-16 grid md:grid-cols-3 gap-8">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">
              🚀 AI-Powered
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Advanced AI understands your natural language queries and generates optimized PostgreSQL code.
            </p>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">
              🔒 Secure
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Built with security in mind - read-only queries, rate limiting, and proper input validation.
            </p>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">
              ⚡ Fast
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Edge-optimized deployment with sub-second response times and connection pooling.
            </p>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center text-gray-500 dark:text-gray-400">
          <p>Built with Next.js, PostgreSQL, and OpenAI • Deployed on Vercel</p>
        </footer>
      </div>
    </div>
  );
}
