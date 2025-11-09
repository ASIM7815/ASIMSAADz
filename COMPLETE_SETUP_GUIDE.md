# 🚀 Codebase & Repository Explorer Agent - Complete Setup Guide

## 📋 Overview

The **Codebase & Repository Explorer Agent** is an AI-powered system that helps developers understand and analyze their software projects. It connects to GitHub, scans repositories, analyzes code structure, dependencies, and generates detailed reports with actionable insights.

### Key Features

✅ **GitHub OAuth Integration** - Secure authentication with your GitHub account  
✅ **Automated Repository Analysis** - Scans file structure, languages, and dependencies  
✅ **Smart Insights** - Detects issues, code quality metrics, and provides recommendations  
✅ **PDF Report Generation** - Download professional analysis reports  
✅ **AI-Powered Q&A** - Ask questions about your codebase using DeepSeek AI  
✅ **Beautiful UI** - Futuristic glassmorphic interface with real-time updates  

---

## 🛠️ Prerequisites

Before you begin, ensure you have:

1. **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
2. **Python** (3.8 or higher) - [Download here](https://www.python.org/)
3. **Git** - [Download here](https://git-scm.com/)
4. **GitHub Account** - [Sign up here](https://github.com/)
5. **DeepSeek API Key** - Already provided: `sk-86ad27643718467dad16c674cdf7270e`

---

## 📦 Installation Steps

### Step 1: Install Node.js Dependencies

Open PowerShell in the `c:\ASIMSAADz` directory and run:

```powershell
cd c:\ASIMSAADz
npm install
```

This will install:
- Express (Web server)
- Octokit (GitHub API client)
- PDFKit (PDF generation)
- Axios (HTTP requests)
- Other dependencies

### Step 2: Install Python Dependencies

Make sure your Python environment has the required packages:

```powershell
pip install flask flask-cors requests
```

### Step 3: Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **"New OAuth App"**
3. Fill in the details:
   - **Application name**: `Codebase Explorer Agent`
   - **Homepage URL**: `http://localhost:3001`
   - **Authorization callback URL**: `http://localhost:3001/auth/github/callback`
4. Click **"Register application"**
5. Copy the **Client ID** and generate a **Client Secret**

### Step 4: Configure Environment Variables

Create a `.env` file in `c:\ASIMSAADz`:

```powershell
Copy-Item .env.example .env
```

Edit the `.env` file and add your GitHub credentials:

```env
# Server Configuration
PORT=3001
BASE_URL=http://localhost:3001
SESSION_SECRET=your-random-secret-key-here-change-this

# GitHub OAuth App Credentials
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
GITHUB_SCOPE=repo,read:user

# DeepSeek API Configuration
DEEPSEEK_API_KEY=sk-86ad27643718467dad16c674cdf7270e
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat

# Report Storage
REPORT_DIR=./data/reports
```

**Important**: Replace `your_github_client_id_here` and `your_github_client_secret_here` with your actual GitHub OAuth credentials.

---

## 🚀 Running the Application

You need to run **TWO** servers simultaneously:

### Terminal 1: Start Node.js Backend (Port 3001)

```powershell
cd c:\ASIMSAADz
node server.js
```

You should see:

```
╔════════════════════════════════════════════════════════════╗
║   Codebase & Repository Explorer Agent                    ║
╚════════════════════════════════════════════════════════════╝

🚀 Server running on: http://localhost:3001
📊 Report storage: ./data/reports
🔐 GitHub OAuth: Configured
🤖 DeepSeek API: Configured
```

### Terminal 2: Start Python Flask Frontend (Port 5000)

Open a **new** PowerShell window:

```powershell
cd c:\ASIMSAADz
python app.py
```

You should see:

```
============================================================
Starting AI Chat & Repository Explorer Server...
✓ Internet Search AI (DuckDuckGo)
✓ GitHub Repository Analysis
✓ AI-Powered Code Insights
============================================================

Open http://localhost:5000 in your browser
Node.js backend: http://localhost:3001
```

---

## 🌐 Using the Application

### 1. Access the Application

Open your web browser and go to: **http://localhost:5000**

### 2. Connect to GitHub

1. Click the **GitHub button** (top-right corner with GitHub logo)
2. Click **"Sign in with GitHub"**
3. Authorize the app in the popup window
4. Wait for authentication to complete

### 3. Select a Repository

1. After authentication, you'll see your repository list
2. Use the search bar to find a specific repository
3. Click on any repository to start analysis

### 4. View Analysis Report

The system will:
- Fetch all files from the repository
- Analyze file structure and languages
- Parse dependencies (npm, pip, maven, go, etc.)
- Check commit history (last 90 days)
- Detect code quality issues
- Generate recommendations

You'll see:
- **Total files** count
- **Languages** breakdown with percentages
- **Dependencies** summary
- **Top directories** by file count
- **Issues** detected (if any)
- **Recommendations** for improvement
- **Recent commits** activity

### 5. Download Reports

Choose from:
- **📄 PDF Download** - Professional formatted report
- **🌐 HTML View** - Interactive web version

### 6. Ask AI Questions

In the report view:
1. Type your question in the Q&A section
2. Examples:
   - "What are the main security concerns?"
   - "How can I improve code quality?"
   - "What dependencies should I update?"
3. Click **"Ask AI"**
4. Get instant insights powered by DeepSeek

---

## 📂 Project Structure

```
c:\ASIMSAADz\
│
├── server.js              # Node.js backend (GitHub API, analysis, PDF)
├── app.py                 # Flask frontend server
├── package.json           # Node.js dependencies
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (DO NOT COMMIT)
├── .env.example           # Example environment file
├── github.json            # Sample GitHub API response
│
├── static/
│   ├── script.js          # Main frontend JavaScript
│   ├── github.js          # GitHub integration JavaScript
│   └── style.css          # Styles with GitHub UI
│
├── templates/
│   └── index.html         # Main HTML template
│
├── data/
│   └── reports/           # Generated analysis reports (JSON, HTML, PDF)
│
└── chat.db                # SQLite database for chat history
```

---

## 🔧 Troubleshooting

### Problem: "Backend service unavailable"

**Solution**: Make sure the Node.js server is running on port 3001:
```powershell
node server.js
```

### Problem: "GitHub OAuth not configured"

**Solution**: Check your `.env` file has valid `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`

### Problem: "Cannot connect to GitHub"

**Solution**: 
1. Check your internet connection
2. Verify GitHub OAuth app callback URL: `http://localhost:3001/auth/github/callback`
3. Ensure you're using HTTP (not HTTPS) for localhost

### Problem: "AI Q&A not working"

**Solution**: Verify `DEEPSEEK_API_KEY` in `.env` file is correct

### Problem: Port already in use

**Solution**: Kill the process using the port:
```powershell
# For port 3001
netstat -ano | findstr :3001
taskkill /PID <PID_NUMBER> /F

# For port 5000
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

---

## 🔐 Security Best Practices

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Keep your GitHub token secure** - Don't share it publicly
3. **Rotate secrets regularly** - Update OAuth secrets periodically
4. **Use environment variables** - Never hardcode API keys in code
5. **Review OAuth permissions** - Only request necessary scopes

---

## 🎯 Features Explained

### 1. Repository Analysis Engine

The system performs comprehensive analysis:

- **File Tree Scanning**: Recursively fetches all files using GitHub Git Tree API
- **Language Detection**: Maps file extensions to programming languages
- **Dependency Parsing**: Reads package.json, requirements.txt, pom.xml, go.mod, Gemfile
- **Commit History**: Analyzes last 90 days of activity
- **Code Quality Metrics**: Checks test coverage, documentation, CI/CD setup

### 2. Smart Issue Detection

Automatically identifies:
- ⚠️ Very large repositories (>5000 files)
- ⚠️ Low test coverage (<10%)
- ⚠️ High dependency counts (>100 npm packages)
- ⚠️ Missing README or documentation
- ⚠️ No CI/CD configuration

### 3. Actionable Recommendations

Provides specific suggestions:
- ✅ Add more unit and integration tests
- ✅ Review and remove unused dependencies
- ✅ Set up CI/CD pipeline
- ✅ Improve documentation
- ✅ Consider modularization for large codebases

### 4. AI-Powered Insights

Uses DeepSeek API to:
- Answer questions about your codebase
- Provide architectural recommendations
- Suggest refactoring opportunities
- Explain complex dependencies
- Identify security concerns

---

## 📊 Report Storage

All reports are saved in `c:\ASIMSAADz\data\reports\` with:

- **JSON format**: Machine-readable data (`{reportId}.json`)
- **HTML format**: Human-readable web page (`{reportId}.html`)
- **PDF format**: Generated on-demand (`{reportId}.pdf`)

Reports persist across sessions and can be accessed later via the API.

---

## 🌟 Advanced Usage

### Running in Production

For production deployment:

1. Use HTTPS with valid SSL certificate
2. Set `SESSION_SECRET` to a strong random value
3. Configure `BASE_URL` to your domain
4. Use a production-grade database (PostgreSQL)
5. Set `NODE_ENV=production`
6. Enable rate limiting and security headers

### API Endpoints Reference

#### Node.js Backend (Port 3001)

- `GET /health` - Health check
- `GET /auth/github` - Start OAuth flow
- `GET /auth/github/callback` - OAuth callback
- `GET /auth/status` - Check auth status
- `POST /auth/logout` - Logout
- `GET /repos` - List repositories
- `POST /analyze` - Analyze repository
- `GET /reports` - List all reports
- `GET /reports/:id/json` - Get report (JSON)
- `GET /reports/:id/html` - Get report (HTML)
- `GET /reports/:id/pdf` - Download report (PDF)
- `POST /qa` - Ask AI question

#### Python Frontend (Port 5000)

- `GET /` - Main page
- `POST /chat` - AI chat (DuckDuckGo search)
- `GET /api/github/*` - Proxy to Node.js backend

---

## 🤝 Contributing

This is a custom implementation for your AI assistant. Feel free to extend it with:

- Additional language support (Rust, Kotlin, Swift)
- More dependency parsers
- Integration with GitLab, Bitbucket
- Scheduled re-analysis
- Webhook support for automatic updates
- Team collaboration features
- Custom report templates

---

## 📝 License

This project is for educational and personal use. Make sure to comply with:
- GitHub API Terms of Service
- DeepSeek API Terms
- Any third-party library licenses

---

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all environment variables are set correctly
3. Ensure both servers are running
4. Check browser console for JavaScript errors
5. Review Node.js and Python terminal output

---

## 🎉 Congratulations!

You now have a fully functional **Codebase & Repository Explorer Agent**! 

Start analyzing your repositories and gain valuable insights into your projects. Happy coding! 🚀

---

**Created by**: Your AI Assistant  
**Date**: November 2025  
**Version**: 1.0.0
