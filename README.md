# PostgreSQL SQL Compiler Website

A public-facing website for transforming natural language into optimized PostgreSQL queries using AI.

## 🚀 Features

- **AI-Powered SQL Generation**: Convert natural language to PostgreSQL queries
- **Secure Architecture**: Server-only AI processing with rate limiting
- **Real-time Validation**: Instant SQL validation and warnings
- **Production Ready**: Built for deployment on Vercel with Neon PostgreSQL

## 🏗️ Architecture

```
Browser  ⇄  Next.js (SSR)  ⇄  API Routes  ⇄  SQL Compiler  ⇄  PostgreSQL
                                    ↘
                                     OpenAI GPT
```

## 📦 Project Structure

```
├── packages/sql-compiler/     # Core SQL compilation logic
│   ├── src/
│   │   ├── compiler.ts       # Main SqlCompiler class
│   │   ├── types.ts          # TypeScript interfaces
│   │   └── index.ts          # Package exports
│   └── package.json
├── web/                      # Next.js web application
│   ├── src/
│   │   ├── app/
│   │   │   ├── api/compile/  # SQL compilation API
│   │   │   ├── page.tsx      # Landing page
│   │   │   └── layout.tsx    # App layout
│   │   ├── components/
│   │   │   └── SqlPlayground.tsx  # Main UI component
│   │   └── lib/
│   │       ├── rate-limit.ts      # Rate limiting
│   │       └── schema-helper.ts   # Database schema
│   └── package.json
└── package.json              # Root workspace config
```

## 🛠️ Development Setup

1. **Clone and install dependencies**:
   ```bash
   git clone <repository>
   cd sql-compiler-postgresql
   npm install
   ```

2. **Build the SQL compiler package**:
   ```bash
   cd packages/sql-compiler
   npm run build
   ```

3. **Configure environment variables**:
   ```bash
   cd web
   cp .env.example .env.local
   # Edit .env.local with your OpenAI API key and database URL
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```

## 🔐 Environment Variables

Create `web/.env.local` with:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here

# Database (optional for demo)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Rate limiting
RATE_LIMIT_MAX=30
RATE_LIMIT_WINDOW=60000
```

## 🚀 Deployment

### Vercel (Recommended)

1. **Push to GitHub**
2. **Connect to Vercel**
3. **Set environment variables in Vercel dashboard**
4. **Deploy**

### Manual Deployment

```bash
# Build all packages
npm run build

# Deploy to your preferred platform
```

## 🔒 Security Features

- ✅ Server-only AI processing (no API keys in browser)
- ✅ Rate limiting (30 requests/minute per IP)
- ✅ Input validation and sanitization
- ✅ SQL injection prevention
- ✅ Read-only database queries only
- ✅ Request timeout protection

## 📊 Database Schema

The demo includes a sample e-commerce schema:

- **users** (id, name, email, role, created_at)
- **products** (id, name, description, price, category, in_stock)
- **orders** (id, user_id, product_id, quantity, total_amount, status)

## 🧪 Example Queries

Try these natural language queries:

- "Show me all users who have placed orders in the last 30 days"
- "Find the top 5 products by total sales amount"
- "Get average order value by user role"
- "List products that are out of stock"

## 🛡️ Production Checklist

- [ ] Set up PostgreSQL with Row-Level Security (RLS)
- [ ] Configure connection pooling (PgBouncer recommended)
- [ ] Set up proper database indexes
- [ ] Enable query logging and monitoring
- [ ] Configure backup strategy
- [ ] Set up error reporting (Sentry, etc.)
- [ ] Implement proper logging and analytics

## 📝 License

MIT