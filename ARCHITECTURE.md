# System Architecture Diagram

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER BROWSER                              │
│                       http://localhost:5000                         │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │                    UI Components                          │    │
│  │  • Chat Interface (Original)                              │    │
│  │  • GitHub Button (NEW) ────────────────────┐             │    │
│  │  • Repository Modal                        │             │    │
│  │  • Analysis Dashboard                      │             │    │
│  │  • Report Viewer                           │             │    │
│  └───────────────────────────────────────────┼────────────────┘    │
└────────────────────────────────────────────┼──────────────────────┘
                                              │
                    Click GitHub Button       │
                                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PYTHON FLASK SERVER (Port 5000)                        │
│                        app.py                                       │
│                                                                     │
│  Original Routes:                    GitHub Proxy Routes (NEW):    │
│  • GET  /             → index.html   • GET  /api/github/repos      │
│  • POST /chat         → search_chat  • POST /api/github/analyze    │
│  • GET  /messages                    • POST /api/github/qa         │
│  • POST /message                     • GET  /api/github/reports    │
│                                                                     │
│  ├─────────────────────┐            └─────────────┬──────────────┐ │
│  │   Chatbot Module    │                          │              │ │
│  │   (search_rag.py)   │                          │              │ │
│  └─────────────────────┘                          │              │ │
└────────────────────────────────────────────────────┼──────────────┘
                                                     │
                                 Proxy HTTP Requests │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│              NODE.JS EXPRESS SERVER (Port 3001)                     │
│                        server.js                                    │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Authentication Layer                       │  │
│  │  GET /auth/github          → Redirect to GitHub OAuth        │  │
│  │  GET /auth/github/callback → Exchange code for token         │  │
│  │  GET /auth/status          → Check if authenticated          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   Repository Operations                       │  │
│  │  GET /repos                → List user repositories           │  │
│  │  POST /analyze             → Analyze selected repository      │  │
│  │  GET /reports              → List all reports                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Analysis Engine                            │  │
│  │  • Fetch file tree (recursive)                                │  │
│  │  • Detect languages                                           │  │
│  │  • Parse dependencies (npm, pip, maven, go, ruby)             │  │
│  │  • Analyze commit history (90 days)                           │  │
│  │  • Calculate quality metrics                                  │  │
│  │  • Generate recommendations                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Report Generation                          │  │
│  │  GET /reports/:id/json     → JSON format                      │  │
│  │  GET /reports/:id/html     → HTML format                      │  │
│  │  GET /reports/:id/pdf      → PDF format (generated)           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      AI Q&A System                            │  │
│  │  POST /qa                  → Ask question about report        │  │
│  │  • Load report context                                        │  │
│  │  • Build prompt with code insights                            │  │
│  │  • Query DeepSeek API                                         │  │
│  │  • Return AI-generated answer                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────┬───────────────┬────────────────┬──────────────────────┘
             │               │                │
             ▼               ▼                ▼
┌──────────────────┐  ┌─────────────┐  ┌────────────────────┐
│   GitHub API     │  │ DeepSeek AI │  │   File System      │
│   (Octokit)      │  │     API     │  │  ./data/reports/   │
│                  │  │             │  │                    │
│ • List repos     │  │ • Chat      │  │ • {id}.json        │
│ • Get tree       │  │ • Context   │  │ • {id}.html        │
│ • Get content    │  │ • Analysis  │  │ • {id}.pdf         │
│ • List commits   │  │             │  │                    │
│ • Get issues     │  └─────────────┘  └────────────────────┘
└──────────────────┘
```

## Component Interaction Flow

### 1. GitHub Authentication Flow
```
User clicks GitHub button
    ↓
Open popup → http://localhost:3001/auth/github
    ↓
Redirect to → https://github.com/login/oauth/authorize
    ↓
User authorizes app
    ↓
GitHub redirects → http://localhost:3001/auth/github/callback?code=...
    ↓
Exchange code for access token
    ↓
Store token in session
    ↓
Display success message
    ↓
Close popup, reload repository list
```

### 2. Repository Analysis Flow
```
User selects repository
    ↓
POST /analyze { owner, repo }
    ↓
┌─────────────────────────────────┐
│ Parallel Data Fetching          │
│ • Repository metadata           │
│ • File tree (recursive)         │
│ • package.json                  │
│ • requirements.txt              │
│ • pom.xml                       │
│ • go.mod                        │
│ • Gemfile                       │
│ • Commit history (90d)          │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Analysis Engine Processing      │
│ • Count files by language       │
│ • Parse all dependencies        │
│ • Calculate quality metrics     │
│ • Detect issues                 │
│ • Generate recommendations      │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Report Generation               │
│ • Create JSON report            │
│ • Generate HTML view            │
│ • Save to disk                  │
└─────────────────────────────────┘
    ↓
Return report ID and summary
    ↓
Display report in UI
```

### 3. AI Q&A Flow
```
User asks question about codebase
    ↓
POST /qa { reportId, question }
    ↓
Load report from ./data/reports/{id}.json
    ↓
Build context prompt:
  • Repository info
  • File counts
  • Languages used
  • Dependencies
  • Issues detected
  • Recommendations
  • User's question
    ↓
POST to DeepSeek API
    ↓
Receive AI-generated answer
    ↓
Return and display answer in UI
```

## Technology Stack Map

```
┌────────────────────────────────────────────────────────────┐
│                      Frontend Layer                        │
│  • HTML5 (templates/index.html)                            │
│  • CSS3 (static/style.css) - Glassmorphic design           │
│  • Vanilla JavaScript (static/script.js, static/github.js) │
│  • No frameworks - Pure web standards                      │
└────────────────────────────────────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────────┐
│                  Python Application Layer                  │
│  • Flask 3.0 - Web framework                               │
│  • Flask-CORS - Cross-origin support                       │
│  • Requests - HTTP client                                  │
│  • SQLite3 - Chat database                                 │
└────────────────────────────────────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────────┐
│                  Node.js Application Layer                 │
│  • Express 4.19 - Web framework                            │
│  • Express-Session - Session management                    │
│  • Octokit/rest 20.0 - GitHub API client                   │
│  • PDFKit 0.14 - PDF generation                            │
│  • Axios 1.6 - HTTP client                                 │
│  • UUID 9.0 - Unique ID generation                         │
│  • FS-Extra 11.2 - File operations                         │
└────────────────────────────────────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────────┐
│                    External Services                       │
│  • GitHub REST API v3                                      │
│  • DeepSeek Chat API                                       │
│  • DuckDuckGo Search (for chat feature)                    │
└────────────────────────────────────────────────────────────┘
```

## Data Models

### Session Data
```javascript
{
  ghToken: "gho_xxxxxxxxxxxx",  // GitHub access token
  ghUser: {
    login: "username",
    name: "Full Name",
    avatar: "https://..."
  },
  oauthState: "random_string"    // CSRF protection
}
```

### Report Structure
```javascript
{
  id: "uuid-v4",
  generatedAt: "2025-11-10T...",
  repo: {
    owner: "username",
    name: "repo-name",
    fullName: "username/repo-name",
    defaultBranch: "main",
    visibility: "public|private",
    description: "...",
    url: "https://github.com/...",
    stars: 123,
    forks: 45
  },
  files: {
    total: 1234,
    languages: {
      counts: { "JavaScript": 500, "Python": 300, ... },
      sizes: { "JavaScript": 2048000, ... }
    },
    topDirs: [
      { name: "src", count: 450 },
      { name: "tests", count: 200 }
    ]
  },
  dependencies: {
    npm: {
      dependencies: { "express": "^4.19.2", ... },
      devDependencies: { "nodemon": "^3.1.0", ... }
    },
    pip: { "flask": "3.0.0", ... },
    maven: [...],
    golang: {...}
  },
  activity: {
    openIssues: 12,
    commits90d: 156,
    authors90d: 8,
    lastCommitDate: "2025-11-09T...",
    recentCommits: [...]
  },
  quality: {
    issues: ["High dependency count", ...],
    recommendations: ["Add CI/CD", ...],
    metrics: {
      totalFiles: 1234,
      testFiles: 123,
      testCoveragePercent: 10.0,
      hasReadme: true,
      hasCI: false
    }
  }
}
```

## Security Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Security Layers                         │
│                                                            │
│  1. Environment Variables (.env)                           │
│     • GitHub OAuth credentials                             │
│     • DeepSeek API key                                     │
│     • Session secret                                       │
│     • Never committed to git                               │
│                                                            │
│  2. OAuth 2.0 Flow                                         │
│     • State parameter (CSRF protection)                    │
│     • Short-lived authorization code                       │
│     • Secure token exchange                                │
│     • Read-only scope (repo, read:user)                    │
│                                                            │
│  3. Session Management                                     │
│     • HTTPOnly cookies                                     │
│     • Secure flag (production)                             │
│     • 24-hour expiration                                   │
│     • Random session IDs                                   │
│                                                            │
│  4. API Security                                           │
│     • requireAuth middleware                               │
│     • Token validation                                     │
│     • Rate limiting (GitHub API)                           │
│     • Input validation                                     │
│                                                            │
│  5. CORS Configuration                                     │
│     • Restricted origins                                   │
│     • Credentials support                                  │
│     • Preflight handling                                   │
└────────────────────────────────────────────────────────────┘
```

## File Organization

```
c:\ASIMSAADz\
│
├── 🔧 Configuration
│   ├── .env              (Environment variables - SECRET)
│   ├── .env.example      (Template)
│   ├── .gitignore        (Protects sensitive files)
│   ├── package.json      (Node.js config)
│   └── requirements.txt  (Python config)
│
├── 🖥️ Backend
│   ├── server.js         (Node.js - GitHub, Analysis, AI)
│   └── app.py            (Flask - Web server, Proxy)
│
├── 🎨 Frontend
│   ├── templates/
│   │   └── index.html    (Main UI template)
│   └── static/
│       ├── script.js     (Chat functionality)
│       ├── github.js     (GitHub integration)
│       └── style.css     (Styles + GitHub UI)
│
├── 💾 Data
│   ├── chat.db           (SQLite - Chat history)
│   └── reports/
│       ├── {uuid}.json   (Report data)
│       ├── {uuid}.html   (Web view)
│       └── {uuid}.pdf    (PDF export)
│
├── 📚 Documentation
│   ├── COMPLETE_SETUP_GUIDE.md     (Full setup)
│   ├── QUICKSTART.md               (5-minute start)
│   ├── README_GITHUB_EXPLORER.md   (Project README)
│   ├── IMPLEMENTATION_SUMMARY.md   (What was built)
│   └── ARCHITECTURE.md             (This file)
│
└── 🚀 Utilities
    └── start.bat         (Windows startup script)
```

---

This architecture enables:
- 🔄 Scalability through microservices
- 🔐 Security through OAuth and sessions
- 🎯 Modularity with clear separation of concerns
- 📊 Rich analytics through GitHub API
- 🤖 AI insights through DeepSeek
- 📄 Multiple export formats
- ⚡ Fast analysis through parallel processing
