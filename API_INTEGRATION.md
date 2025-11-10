# 🤝 AI API Integration Guide

## Overview
Your AI Code Analyzer now intelligently combines **three powerful APIs** to provide comprehensive answers:

1. **🧠 DeepSeek AI** - Code analysis & intelligent conversations
2. **🐙 GitHub API** - Repository metadata & analysis  
3. **🔍 DuckDuckGo** - General knowledge & current events

---

## 🎯 How It Works

### Smart Question Routing
The system automatically detects what type of question you're asking and uses the best API:

#### 1️⃣ DeepSeek AI (Code & General Chat)
**Triggers when:**
- Asking about your uploaded code report
- Questions about programming concepts
- Code explanations, bugs, complexity
- General conversation

**Examples:**
```
✅ "Can you give me a summary of my report?"
✅ "Explain the health score"
✅ "What files have high complexity?"
✅ "How can I improve my code?"
✅ "What is a design pattern?"
```

**What you get:**
- Personalized responses with emojis 😊
- Context-aware answers based on your report
- Friendly, conversational AI
- Code explanations and suggestions

---

#### 2️⃣ GitHub API (Repository Analysis)
**Triggers when:**
- Message contains GitHub URLs
- Keywords: repository, repo, github, commits, contributors, stars, forks

**Examples:**
```
✅ "Analyze https://github.com/pallets/flask"
✅ "Tell me about microsoft/vscode"
✅ "Show me contributors for tensorflow/tensorflow"
✅ "What languages are used in facebook/react"
```

**What you get:**
- ⭐ Stars, forks, watchers count
- 📝 Repository description
- 🏷️ Programming languages & percentages
- 👥 Top contributors
- 📅 Recent commits (last 10)
- 🐛 Open issues count
- 📦 Repository size & license

**Response format:**
```
📦 GitHub Repository Analysis

owner/repository-name
Description of the repository

⭐ Stars: 50,000 | 🍴 Forks: 10,000 | 👀 Watchers: 2,000
🐛 Open Issues: 150 | 📦 Size: 5,000 KB
🏷️ License: MIT License
📅 Created: 2015-04-01 | Last updated: 2024-01-15

Languages:
  • Python: 65.3%
  • JavaScript: 25.1%
  • HTML: 9.6%

Recent Commits:
  • [abc1234] Fix bug in authentication - John Doe (2024-01-14)
  • [def5678] Add new feature - Jane Smith (2024-01-13)
  ...

Top Contributors:
  • john_doe: 1,250 contributions
  • jane_smith: 850 contributions
  ...
```

---

#### 3️⃣ DuckDuckGo Search (General Knowledge)
**Triggers when:**
- Keywords: who is, what is, latest, news, today, current, trending
- Questions about people, places, events
- NOT code-related questions

**Examples:**
```
✅ "Who is Abdul Kalam?"
✅ "What is the latest news in AI?"
✅ "When did Python 3.12 release?"
✅ "What are trending technologies today?"
✅ "Where is Silicon Valley?"
```

**What you get:**
- Real-time internet search results
- Current information & news
- Biographical info about people
- Up-to-date tech trends

---

## 🚀 Usage Examples

### Scenario 1: Analyzing Your Code
```
You: "Upload code folder" → [Uploads Python project]
AI: "📊 Analysis complete! Your project has 25 files..."

You: "Give me a summary of my report"
🧠 DeepSeek AI responds with personalized insights about YOUR code
```

### Scenario 2: Learning About Repositories
```
You: "Analyze https://github.com/django/django"
🐙 GitHub API fetches:
  - 75K stars, 30K forks
  - Python 98.2%, HTML 1.8%
  - 2,100 contributors
  - Recent commits & updates

🧠 DeepSeek AI explains the data in conversational style
```

### Scenario 3: General Knowledge
```
You: "Who is Guido van Rossum?"
🔍 DuckDuckGo searches the internet
AI: "Guido van Rossum is the creator of Python programming language..."
```

### Scenario 4: Mixed Queries
```
You: "Compare my code health score to React's repository"
🧠 DeepSeek analyzes YOUR report
🐙 GitHub API fetches React repository data
AI: Combines both to give you a comprehensive comparison
```

---

## 🎨 System Architecture

```
User Question
     |
     v
Smart Router (app.py)
     |
     +---> Keywords Detection
     |
     +---> API Selection:
           |
           +---> 🧠 DeepSeek AI
           |     - Code questions
           |     - Report analysis
           |     - General chat
           |
           +---> 🐙 GitHub API
           |     - Repository queries
           |     - Contributor info
           |     - Commit history
           |
           +---> 🔍 DuckDuckGo
                 - General knowledge
                 - Current events
                 - People/places
```

---

## 📊 API Features Comparison

| Feature | DeepSeek AI | GitHub API | DuckDuckGo |
|---------|-------------|------------|------------|
| Code Analysis | ✅ | ❌ | ❌ |
| Report Understanding | ✅ | ❌ | ❌ |
| Repository Data | ❌ | ✅ | ❌ |
| Commit History | ❌ | ✅ | ❌ |
| Contributors | ❌ | ✅ | ❌ |
| General Knowledge | ⚠️ | ❌ | ✅ |
| Current Events | ❌ | ❌ | ✅ |
| Biographical Info | ❌ | ❌ | ✅ |
| Conversational | ✅ | ❌ | ❌ |
| Context Memory | ✅ | ❌ | ❌ |

---

## 🔑 Configuration

### DeepSeek API
- **File:** `deepseek_chat.py`
- **API Key:** `sk-86ad27643718467dad16c674cdf7270e`
- **Endpoint:** `https://api.deepseek.com/v1/chat/completions`
- **Features:** 
  - Conversation memory (last 8 messages)
  - Report context awareness
  - Friendly personality with emojis

### GitHub API
- **File:** `github_api.py`
- **Endpoint:** `https://api.github.com`
- **Rate Limit:** 60 requests/hour (unauthenticated)
- **Optional:** Set `GITHUB_TOKEN` environment variable for 5,000 requests/hour
- **Functions:**
  - `get_repo_info()` - Basic repository data
  - `get_recent_commits()` - Last 10 commits
  - `get_contributors()` - Top contributors
  - `get_languages()` - Language breakdown

### DuckDuckGo Search
- **File:** `search_rag.py`
- **Library:** `duckduckgo-search`
- **No API Key Required** - Free and unlimited
- **Features:**
  - Real-time internet search
  - Safe search enabled
  - Instant answers

---

## 🛠️ Technical Details

### Conversation Memory
DeepSeek AI remembers your last 8 messages for context-aware responses:
```python
conversation_history = [
    {"role": "user", "content": "Upload code"},
    {"role": "assistant", "content": "Analysis complete..."},
    {"role": "user", "content": "Explain health score"},
    ...
]
```

### Report Context
When you upload code, the analysis is stored and passed to AI:
```python
report_context = {
    'project_name': 'MyProject',
    'health_score': 85,
    'total_files': 25,
    'languages': {'Python': 80, 'JavaScript': 20},
    'dependencies': {...}
}
```

### Error Handling
- **API Failures:** Graceful fallback responses
- **Rate Limits:** Clear error messages
- **Network Issues:** Retry logic with timeouts

---

## 💡 Pro Tips

1. **Be Specific:** More specific questions get better answers
   - ❌ "Tell me about code"
   - ✅ "Explain why my health score is 75"

2. **Use Keywords:** Trigger the right API
   - For GitHub: Include "github.com" or "repository"
   - For Search: Use "who is", "what is", "latest"
   - For Code: Mention "report", "analysis", "my code"

3. **Combine Context:** Ask follow-up questions
   ```
   You: "Analyze https://github.com/django/django"
   AI: [Shows repository data]
   You: "How does my code compare?"
   AI: [Compares YOUR report to Django's stats]
   ```

4. **Upload First:** For best results, upload code before asking questions
   - AI will have full context about YOUR project
   - Can reference specific files, functions, metrics

---

## 🎯 What Each API is Best For

### 🧠 DeepSeek AI - Your Code Mentor
- Understanding your report
- Explaining complexity scores
- Suggesting improvements
- Answering programming questions
- Friendly conversation about code

### 🐙 GitHub API - Repository Explorer
- Comparing projects
- Finding popular repositories
- Checking contributor activity
- Language distribution analysis
- Monitoring commit frequency

### 🔍 DuckDuckGo - Knowledge Base
- Learning about people in tech
- Finding latest news
- Understanding concepts
- Historical information
- Current events & trends

---

## 📈 Future Enhancements

Coming soon:
- [ ] GitHub authentication for higher rate limits
- [ ] Cached repository data for faster responses
- [ ] Multi-repository comparison
- [ ] Trend analysis over time
- [ ] Integration with more code analysis tools

---

## 🐛 Troubleshooting

**AI not responding?**
- Check internet connection
- Verify DeepSeek API key is valid
- Look for error messages in terminal

**GitHub data not showing?**
- Verify repository URL is correct
- Check rate limit (60 requests/hour)
- Use format: `owner/repo` or full URL

**Search not working?**
- DuckDuckGo may be temporarily unavailable
- Try rephrasing your question
- Use more specific keywords

---

## 📝 Example Conversation Flow

```
User: [Uploads Python project with 30 files]

AI: "📊 Code Analysis Complete!
    - 30 files analyzed
    - Health Score: 82/100
    - Python 85%, JavaScript 15%"

User: "Give me a summary"
[🧠 DeepSeek AI with report context]
AI: "Your project looks great! 😊 Health score of 82 shows 
    solid code quality. You have 5 files with high complexity..."

User: "Compare it to Flask"
[🧠 DeepSeek suggests specificity]
AI: "I'd love to help! Could you share the Flask repository URL?"

User: "https://github.com/pallets/flask"
[🐙 GitHub API fetches data + 🧠 DeepSeek analyzes]
AI: "📦 Flask Repository:
    ⭐ 65K stars | 🍴 16K forks
    Python 99.8%
    
    Compared to your project:
    - Both are Python-heavy ✅
    - Flask has 15+ contributors vs your solo work
    - Your complexity score (4.2) is better than Flask's (5.8)"

User: "Who created Flask?"
[🔍 DuckDuckGo searches]
AI: "Flask was created by Armin Ronacher in 2010..."

User: "Thanks! Any tips to improve my code?"
[🧠 DeepSeek with report context]
AI: "Based on your report, here are 3 tips:
    1. Reduce complexity in auth.py (score: 8.1)
    2. Add documentation to 5 files missing docstrings
    3. Consider breaking down large functions in utils.py"
```

---

**🎉 Enjoy your intelligent AI assistant with three powerful APIs working together!**
