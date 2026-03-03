# DevPulse Dashboard UI

Real-time API monitoring, AI-powered code generation, and compatibility analysis dashboard.

## Features

- **Dashboard Stats**: Real-time overview of API health metrics
- **Health Monitor**: Live status of 15 monitored APIs with latency tracking
- **AI Code Generator**: Generate production-ready Python integration code using Groq AI
- **Compatibility Checker**: Analyze API compatibility using graph-based pathfinding
- **Documentation Search**: AI-powered documentation search and Q&A

## Tech Stack

- **Framework**: Next.js 16 with App Router
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **API Client**: Async fetch with proper error handling

## Quick Start

### Prerequisites

- Node.js 18+ 
- DevPulse Backend running on port 8000

### Installation

```bash
# Install dependencies
npm install

# Configure environment (optional - defaults to localhost:8000)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## Project Structure

```
src/
├── app/
│   ├── layout.tsx          # Root layout with dark theme
│   ├── page.tsx            # Main dashboard page
│   └── globals.css         # Global styles
├── components/
│   ├── DashboardStats.tsx      # Stats overview cards
│   ├── HealthMonitor.tsx       # API health grid
│   ├── CodeGenerator.tsx       # AI code generation UI
│   ├── CompatibilityChecker.tsx # API compatibility tool
│   └── DocsSearch.tsx          # Documentation search
└── lib/
    └── api.ts              # API client with TypeScript types
```

## API Endpoints Used

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Get health status of all APIs |
| `/api/dashboard` | GET | Get dashboard statistics |
| `/api/compatibility` | GET | Check API compatibility |
| `/api/generate` | POST | Generate integration code |
| `/api/docs` | POST | Search documentation |

## Development

```bash
npm run dev     # Start development server
npm run build   # Build for production
npm start       # Start production server
npm run lint    # Lint code
```

## Deploy on Vercel

```bash
npx vercel
```

Check out the [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
