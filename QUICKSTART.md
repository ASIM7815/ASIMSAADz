# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```powershell
cd c:\ASIMSAADz
npm install
```

### Step 2: Setup GitHub OAuth

1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Set callback URL: `http://localhost:3001/auth/github/callback`
4. Copy Client ID and Secret

### Step 3: Configure .env

Copy `.env.example` to `.env` and fill in:
- `GITHUB_CLIENT_ID` - Your GitHub Client ID
- `GITHUB_CLIENT_SECRET` - Your GitHub Client Secret
- `SESSION_SECRET` - Any random string
- `DEEPSEEK_API_KEY` - Already set: `sk-86ad27643718467dad16c674cdf7270e`

### Step 4: Run Both Servers

**Terminal 1 (Node.js Backend):**
```powershell
node server.js
```

**Terminal 2 (Python Frontend):**
```powershell
python app.py
```

### Step 5: Open Browser

Go to: http://localhost:5000

Click the GitHub button → Sign in → Select a repository → View analysis!

---

## 📖 Full Documentation

See [COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md) for detailed instructions.

## 🔑 Key Features

- ✅ GitHub OAuth login
- ✅ Repository analysis (files, languages, dependencies)
- ✅ Code quality insights
- ✅ PDF report generation
- ✅ AI-powered Q&A (DeepSeek)

## 🛠️ Tech Stack

- **Backend**: Node.js + Express
- **Frontend**: Python Flask + Vanilla JS
- **APIs**: GitHub REST API, DeepSeek AI
- **Styling**: Custom CSS with glassmorphism

## 📞 Need Help?

Check the troubleshooting section in the complete guide!
