# 🚀 Frontend Setup Guide

## Prerequisites

- Node.js 18+ and npm
- React 18
- TypeScript 5

## Installation

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Setup

Create `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENV=development
```

### 3. Development Server

Start the React development server:

```bash
npm run dev
```

The app will open at `http://localhost:3000`

## Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable React components
│   │   ├── ChatBox.tsx       # Agent brainstorming interface
│   │   ├── VideoPreview.tsx  # Video player component
│   │   ├── ScriptDisplay.tsx # Script & variations display
│   │   └── MonetizationBrief.tsx # Earnings & products
│   ├── pages/           # Full page components
│   │   └── Dashboard.tsx      # Main dashboard
│   ├── services/        # API services
│   │   └── agentService.ts   # Calls to backend API
│   ├── types/           # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
│   └── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Components

### ChatBox
Interactive chat for brainstorming with agents
- Real-time messaging
- Agent selection
- Auto-scroll to latest message

### VideoPreview
TikTok-style video player (9:16 aspect ratio)
- Video playback controls
- Duration display
- Metadata

### ScriptDisplay
Three-column script format
- Main script view
- Script variations for A/B testing
- Auto-generated captions

### MonetizationBrief
Monetization strategy dashboard
- Earnings projection range
- Recommended affiliate products
- Revenue per product

## API Integration

The frontend communicates with the FastAPI backend:

```
Frontend (React) → http://localhost:3000
Backend (FastAPI) → http://localhost:8000/api
```

Key endpoints:
- `POST /api/generate` - Start content generation
- `POST /api/brainstorm` - Chat with agents
- `GET /api/status` - Check generation progress
- `GET /api/results` - Get previous generations

## Features

✅ Topic input with auto-complete suggestions
✅ Real-time generation progress
✅ Multi-tab content viewer (Video, Script, Monetization, Chat)
✅ Agent brainstorming chat
✅ Responsive mobile design
✅ Beautiful gradient UI
✅ Error handling with user feedback

## Troubleshooting

### Port 3000 already in use
```bash
# Use a different port
npm run dev -- --port 3001
```

### API connection failed
- Make sure backend is running: `python api.py`
- Check backend is on `http://localhost:8000`
- Verify CORS is enabled in api.py

### Module not found errors
```bash
npm install
npm run type-check
```

## Next Steps

1. Start the backend API: `python api.py`
2. Start the frontend: `npm run dev`
3. Open http://localhost:3000
4. Enter a topic and generate your first viral video!
