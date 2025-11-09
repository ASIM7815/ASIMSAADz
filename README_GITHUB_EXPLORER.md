# 🤖 AI-Powered Codebase & Repository Explorer Agent

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Node](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen.svg)
![Python](https://img.shields.io/badge/python-%3E%3D3.8-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Analyze any GitHub repository with AI-powered insights in seconds!**

[Features](#-features) • [Quick Start](#-quick-start) • [Setup](#-installation) • [Documentation](#-documentation)

</div>

---

## 🌟 Features

### 🔍 **Intelligent Repository Analysis**
- **Deep Code Scanning**: Analyzes entire repository structure, file types, and organization
- **Language Detection**: Automatically identifies all programming languages used
- **Dependency Mapping**: Parses npm, pip, Maven, Go modules, and Ruby gems
- **Commit History Analysis**: Tracks activity over the last 90 days

### 📊 **Comprehensive Reports**
- **Visual Dashboards**: Beautiful stats cards with language breakdowns
- **Quality Metrics**: Code coverage, documentation, and CI/CD detection
- **Issue Detection**: Automatically identifies potential problems
- **Smart Recommendations**: Actionable suggestions for improvement

### 🤖 **AI-Powered Insights**
- **DeepSeek Integration**: Ask questions about your codebase
- **Natural Language Q&A**: Get explanations in plain English
- **Architectural Advice**: Receive guidance on code structure
- **Security Analysis**: Identify potential vulnerabilities

### 📄 **Export Options**
- **PDF Reports**: Professional formatted documents
- **HTML Views**: Interactive web-based reports
- **JSON Data**: Machine-readable analysis results

### 🎨 **Modern UI/UX**
- **Glassmorphic Design**: Beautiful futuristic interface
- **Responsive Layout**: Works on desktop and mobile
- **Real-time Updates**: Live progress indicators
- **Smooth Animations**: Polished user experience

---

## 🎯 Use Cases

### For **Individual Developers**
- 📈 Understand unfamiliar codebases quickly
- 🔧 Identify areas needing refactoring
- 📚 Generate documentation automatically
- 🎓 Learn from well-structured projects

### For **Development Teams**
- 👥 Onboard new team members faster
- 📊 Track project health metrics
- 🔄 Monitor dependency updates
- 🏆 Maintain code quality standards

### For **Engineering Managers**
- 📋 Get project status at a glance
- 📉 Identify technical debt
- 🎯 Prioritize maintenance tasks
- 💼 Generate reports for stakeholders

---

## ⚡ Quick Start

### One-Command Startup

```powershell
cd c:\ASIMSAADz
start.bat
```

This will:
1. ✅ Check prerequisites
2. ✅ Install dependencies (if needed)
3. ✅ Start both servers
4. ✅ Open your browser automatically

### Manual Startup

**Terminal 1 - Backend:**
```powershell
node server.js
```

**Terminal 2 - Frontend:**
```powershell
python app.py
```

Then open: **http://localhost:5000**

---

## 📦 Installation

### Prerequisites

- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (3.8+)
- [Git](https://git-scm.com/)
- GitHub account

### Setup Steps

#### 1️⃣ Install Dependencies

```powershell
npm install
pip install flask flask-cors requests
```

#### 2️⃣ Create GitHub OAuth App

1. Go to [GitHub Settings → Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in:
   - **Application name**: Codebase Explorer
   - **Homepage URL**: `http://localhost:3001`
   - **Callback URL**: `http://localhost:3001/auth/github/callback`
4. Save **Client ID** and **Client Secret**

#### 3️⃣ Configure Environment

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your credentials:

```env
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
SESSION_SECRET=random_secret_key
DEEPSEEK_API_KEY=sk-86ad27643718467dad16c674cdf7270e
```

#### 4️⃣ Run the Application

```powershell
start.bat
```

Or manually start both servers as shown above.

---

## 📖 Documentation

### 📚 Available Guides

- **[COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)** - Comprehensive setup instructions
- **[QUICKSTART.md](./QUICKSTART.md)** - Get started in 5 minutes
- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Original setup documentation

### 🔗 API Documentation

#### Node.js Backend (Port 3001)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/auth/github` | GET | Start OAuth flow |
| `/auth/status` | GET | Check authentication |
| `/repos` | GET | List repositories |
| `/analyze` | POST | Analyze repository |
| `/reports/:id/json` | GET | Get report (JSON) |
| `/reports/:id/html` | GET | Get report (HTML) |
| `/reports/:id/pdf` | GET | Download PDF |
| `/qa` | POST | Ask AI question |

#### Python Frontend (Port 5000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main interface |
| `/chat` | POST | AI chat (DuckDuckGo) |
| `/api/github/*` | ALL | Proxy to Node backend |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Browser (Port 5000)                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  React-like UI with GitHub Integration Button   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│            Python Flask Server (Port 5000)              │
│  • Serves HTML/CSS/JS                                   │
│  • Handles chat requests                                │
│  • Proxies GitHub requests to Node.js                   │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│           Node.js Express Server (Port 3001)            │
│  • GitHub OAuth authentication                          │
│  • Repository data fetching                             │
│  • Code analysis engine                                 │
│  • PDF report generation                                │
│  • DeepSeek AI integration                              │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ├──────────────┬────────────────┐
                  ▼              ▼                ▼
          ┌─────────────┐  ┌──────────┐  ┌────────────┐
          │  GitHub API │  │ DeepSeek │  │ File System│
          │             │  │   API    │  │  (Reports) │
          └─────────────┘  └──────────┘  └────────────┘
```

---

## 🎨 Screenshots

### Main Interface
- Beautiful glassmorphic design with animated orb
- Chat interface with AI capabilities
- GitHub integration button in header

### Repository Selection
- List of all your GitHub repositories
- Search and filter functionality
- Repository metadata (stars, forks, language)

### Analysis Report
- Comprehensive statistics dashboard
- Language breakdown with visual charts
- Dependency information
- Code quality metrics
- AI-powered Q&A section

---

## 🛠️ Technology Stack

### Backend
- **Node.js** - Runtime environment
- **Express** - Web framework
- **Octokit** - GitHub API client
- **PDFKit** - PDF generation
- **Axios** - HTTP client

### Frontend
- **Python Flask** - Web server
- **Vanilla JavaScript** - No frameworks needed
- **CSS3** - Modern styling with animations
- **HTML5** - Semantic markup

### APIs & Services
- **GitHub REST API** - Repository data
- **DeepSeek AI** - Natural language processing
- **DuckDuckGo** - Web search (chat feature)

---

## 🔒 Security

- ✅ OAuth 2.0 authentication
- ✅ Session-based security
- ✅ Environment variable protection
- ✅ Read-only repository access
- ✅ No credentials stored in code
- ✅ Secure token handling

### Best Practices

1. Never commit `.env` file
2. Rotate OAuth secrets regularly
3. Use HTTPS in production
4. Implement rate limiting
5. Validate all user inputs

---

## 🐛 Troubleshooting

### Common Issues

**Problem**: Backend service unavailable  
**Solution**: Ensure Node.js server is running on port 3001

**Problem**: GitHub OAuth not configured  
**Solution**: Check `.env` file has valid credentials

**Problem**: Port already in use  
**Solution**: Kill existing process or change port in `.env`

**Problem**: AI Q&A not working  
**Solution**: Verify `DEEPSEEK_API_KEY` is correct

### Getting Help

1. Check [COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)
2. Review console errors in browser (F12)
3. Check terminal output for errors
4. Verify all environment variables are set

---

## 📈 Roadmap

### Planned Features

- [ ] Support for GitLab and Bitbucket
- [ ] Scheduled automatic re-analysis
- [ ] Webhook integration for real-time updates
- [ ] Team collaboration features
- [ ] Custom report templates
- [ ] Integration with Jira/Trello
- [ ] Code complexity metrics
- [ ] Security vulnerability scanning
- [ ] Multi-language AI support
- [ ] Docker containerization

---

## 🤝 Contributing

While this is a personal project, suggestions are welcome! Feel free to:

1. Report bugs or issues
2. Suggest new features
3. Improve documentation
4. Share your use cases

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **GitHub** - For the comprehensive REST API
- **DeepSeek** - For powerful AI capabilities
- **Node.js & Python communities** - For excellent tools and libraries
- **All contributors** - Thank you for your support!

---

## 📞 Support

For questions or support:

- 📧 Check documentation files
- 🐛 Review troubleshooting section
- 💬 Examine console logs
- 🔍 Search existing issues

---

<div align="center">

**Made with ❤️ by AI Assistant**

**⭐ Star this project if you find it useful!**

[Back to Top](#-ai-powered-codebase--repository-explorer-agent)

</div>
