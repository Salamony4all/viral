# 🎬 Viral Engine Frontend

A beautiful, interactive React dashboard for the Zero-API Viral Engine multi-agent TikTok content creation system.

## ✨ Features

### 🎯 Input Section
- Enter any topic (e.g., "productivity hack for students")
- One-click generation of complete viral campaigns
- Real-time progress indicator

### 🎬 Video Preview
- TikTok-native 9:16 aspect ratio
- Built-in video player
- Metadata display (duration, title)

### 📝 Script Editor
- Main script display in 3-column format [Time | Visual | Audio]
- Multiple script variations for A/B testing
- Auto-generated captions list

### 💰 Monetization Dashboard
- Earnings projection ($X - $Y range)
- Recommended affiliate products
- Revenue per product
- Direct affiliate links

### 💭 Brainstorm Chat
- Real-time chat with AI agents
- Ask for ideas and suggestions
- Personalized responses from each agent
- Full conversation history

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install Node.js 18+
node --version

# Verify npm
npm --version
```

### 2. Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
```

### 3. Start Development Server
```bash
npm run dev
```

Opens automatically at `http://localhost:3000`

### 4. Make Sure Backend is Running
```bash
# In another terminal, from the viral_engine directory
python api.py
```

## 📁 Project Structure

```
frontend/
│
├── src/
│   ├── components/
│   │   ├── ChatBox.tsx          # Agent brainstorming interface
│   │   ├── ChatBox.css
│   │   ├── VideoPreview.tsx     # TikTok-style video player
│   │   ├── VideoPreview.css
│   │   ├── ScriptDisplay.tsx    # Script + variations display
│   │   ├── ScriptDisplay.css
│   │   ├── MonetizationBrief.tsx # Earnings strategy
│   │   └── MonetizationBrief.css
│   │
│   ├── pages/
│   │   ├── Dashboard.tsx        # Main dashboard page
│   │   └── Dashboard.css
│   │
│   ├── services/
│   │   └── agentService.ts      # API calls to backend
│   │
│   ├── types/
│   │   └── index.ts             # TypeScript definitions
│   │
│   ├── App.tsx
│   ├── App.css
│   ├── main.tsx
│   ├── index.css
│   └── vite-env.d.ts
│
├── public/
│   └── index.html               # HTML entry point
│
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── .env.example
├── .gitignore
└── README.md
```

## 🎨 Components Deep Dive

### ChatBox Component
**Purpose**: Interactive chat for brainstorming with agents

**Props**:
```typescript
{
  agent: string;           // e.g., "Narrative Architect"
  onSendMessage: (msg: string) => Promise<void>;
  isLoading?: boolean;
}
```

**Features**:
- Message history with timestamps
- User/assistant message distinction
- Loading states
- Disabled state during generation
- Keyboard shortcuts (Enter to send)

### VideoPreview Component
**Purpose**: Display generated video in TikTok format

**Props**:
```typescript
{
  src?: string;            // Video file path/URL
  title?: string;          // Video title
  duration?: number;       // Duration in milliseconds
}
```

**Features**:
- 9:16 aspect ratio (TikTok native)
- Play/pause controls
- Hover overlay with play button
- Placeholder when no video

### ScriptDisplay Component
**Purpose**: Show generated script with variations and captions

**Props**:
```typescript
{
  script?: string;         // Main script
  variations?: string[];   // Alternative versions
  captions?: string[];     // Caption list
}
```

**Features**:
- Syntax-highlighted script
- Variation cards with version number
- Caption list with numbering
- Collapsible sections

### MonetizationBrief Component
**Purpose**: Display monetization strategy and earnings

**Props**:
```typescript
{
  brief?: string;
  products?: Array<{
    name: string;
    affiliate_link?: string;
    estimated_revenue?: number;
  }>;
  earnings_projection?: {
    low: number;
    high: number;
    currency: string;
  };
}
```

**Features**:
- Earnings range display
- Product cards with links
- Revenue estimates
- Clickable affiliate links

## 🔗 API Integration

### Service: agentService.ts

```typescript
// Generate complete campaign
await agentService.generateCampaign("topic");

// Brainstorm with agent
await agentService.brainstormWithAgent("Agent Name", "prompt");

// Get pipeline status
await agentService.getPipelineStatus();

// Get recent results
await agentService.getRecentResults();

// Save for later
await agentService.saveGeneration(id, notes);
```

## 🎯 User Workflow

1. **Input Topic**
   - User enters topic in the input field
   - Click "Generate Campaign"

2. **Processing**
   - Shows loading spinner
   - Agents run in sequence (Alpha → Beta → Gamma → Delta)
   - Progress indicator updates

3. **Results**
   - Video preview displays generated TikTok
   - Script tab shows main script + variations
   - Monetization tab shows strategy
   - Chat tab enables brainstorming

4. **Refinement** (Optional)
   - Use chat to brainstorm improvements
   - Re-generate if needed
   - Save results for later

## 🎨 Design System

### Colors
- Primary: `#667eea` (Purple)
- Secondary: `#764ba2` (Dark Purple)
- Accent: `#f5576c` (Red)
- Background: `#f8f9fa` (Light Gray)
- Text: `#333` (Dark)

### Typography
- Headers: -apple-system font stack
- Code: Monaco/Menlo monospace
- Size: 16px base

### Spacing
- 8px, 12px, 16px, 20px units
- Consistent padding/margins

### Shadows
- Small: `0 2px 8px rgba(0,0,0,0.1)`
- Medium: `0 8px 20px rgba(0,0,0,0.1)`

### Animations
- Fade in: `0.3s ease-in`
- Transform: `translateY(-2px)` on hover
- Spin: `1s linear infinite` for loaders

## 📱 Responsive Design

- **Desktop** (>768px): Full layout
- **Tablet** (481px-768px): Adjusted spacing
- **Mobile** (<480px): Stacked layout
- Mobile-first approach

## 🔧 Development

### Environment Variables
```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENV=development
```

### Build
```bash
npm run build
```

Output: `dist/` directory ready for deployment

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
```

## 🚀 Deployment

### Build Optimized Version
```bash
npm run build
```

### Serve Locally
```bash
npm run preview
```

### Deploy to Web
1. Build: `npm run build`
2. Upload `dist/` folder to:
   - Vercel
   - Netlify
   - GitHub Pages
   - Your web server

### Docker (Optional)
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 🐛 Troubleshooting

### Issue: "Cannot connect to API"
**Solution**: 
- Ensure backend is running: `python api.py`
- Check backend is on `localhost:8000`
- Verify CORS is enabled

### Issue: "Blank screen"
**Solution**:
- Open browser DevTools (F12)
- Check console for errors
- Verify `npm install` completed
- Try clearing browser cache

### Issue: "Port 3000 already in use"
**Solution**:
```bash
npm run dev -- --port 3001
```

### Issue: Module errors
**Solution**:
```bash
rm -rf node_modules
npm install
```

## 📚 Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [Vite Guide](https://vitejs.dev)
- [Lucide Icons](https://lucide.dev)
- [Axios HTTP Client](https://axios-http.com)

## 🎯 Next Steps

1. ✅ Start frontend: `npm run dev`
2. ✅ Start backend: `python api.py`
3. ✅ Open http://localhost:3000
4. ✅ Enter a topic
5. ✅ Generate viral content!

## 📝 License

Part of the Zero-API Viral Engine project.

---

**Made with ❤️ for viral content creators**
