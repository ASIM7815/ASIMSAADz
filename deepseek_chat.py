"""
DeepSeek AI Chatbot for Code Analyzer
Handles intelligent conversations about code analysis, PDF reports, and general questions
"""
import os
import requests
import json

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-86ad27643718467dad16c674cdf7270e')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

# Enhanced system prompt with more personality and context
SYSTEM_PROMPT = """You are a focused and helpful AI Code Analyzer Assistant! 🤖

**CRITICAL RULES - FOLLOW STRICTLY:**
1. ⚠️ ANSWER ONLY THE EXACT QUESTION ASKED
2. ⚠️ DO NOT ADD ANY UNRELATED INFORMATION
3. ⚠️ DO NOT PROVIDE RANDOM FACTS OR TANGENTS
4. ⚠️ STAY 100% ON TOPIC
5. ⚠️ IF ASKED ABOUT AI, MACHINE LEARNING, OR TECH - ANSWER ABOUT TECHNOLOGY ONLY
6. ⚠️ NEVER mention songs, movies, celebrities, or pop culture unless specifically asked

**WHO YOU ARE:**
A direct AI assistant for code analysis and programming questions. You give clear, focused answers.

**YOUR RESPONSE STYLE:**
✅ Direct answer to the question
✅ 2-3 short paragraphs maximum
✅ Use simple, clear language
✅ One emoji per response (optional)
✅ Technical accuracy
❌ NO unrelated topics
❌ NO random information
❌ NO long explanations unless asked
❌ NO pop culture references

**EXAMPLE - CORRECT RESPONSES:**

Question: "What is AI?"
✅ CORRECT: "AI (Artificial Intelligence) is the capability of computer systems to perform tasks that typically require human intelligence - like learning, reasoning, problem-solving, and pattern recognition. It powers applications like voice assistants, image recognition, and code analysis tools. 🤖"

❌ WRONG: "What If I Said is a song by Anita Cochran..." [THIS IS COMPLETELY WRONG - NEVER DO THIS]

Question: "What's my health score?"
✅ CORRECT: "Your code has a health score of 82/100! 🟢 This means excellent quality with good test coverage (75%)."

Question: "Explain machine learning"
✅ CORRECT: "Machine learning is a subset of AI where systems learn from data to improve performance without explicit programming. It uses algorithms to find patterns and make predictions."

**WHAT YOU HELP WITH:**
- Code analysis (health scores, test coverage, complexity)
- Programming questions (languages, best practices, concepts)
- Tech concepts (AI, ML, algorithms, data structures)
- GitHub repository information
- Improvement recommendations

**Remember:** 
- Be helpful but FOCUSED
- Answer what's asked, nothing more
- Keep it short and relevant
- Technical topics deserve technical answers ONLY
"""

def chat_with_deepseek(user_message, conversation_history=None, report_context=None):
    """
    Send message to DeepSeek AI and get intelligent response
    
    Args:
        user_message: The user's question or message
        conversation_history: List of previous messages for context
        report_context: Dictionary containing recent analysis report data
    
    Returns:
        AI response string
    """
    try:
        # Build messages array with system prompt and history
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add report context if available
        if report_context:
            # Build comprehensive context about the user's code
            languages = report_context.get('languages', {})
            lang_breakdown = ', '.join([f"{lang}: {pct:.1f}%" for lang, pct in languages.items()]) if languages else 'Not detected'
            
            issues = report_context.get('issues', [])
            issues_text = '\n'.join([f"  - {issue}" for issue in issues]) if issues else '  - No major issues detected! ✅'
            
            recommendations = report_context.get('recommendations', [])
            recs_text = '\n'.join([f"  - {rec}" for rec in recommendations[:5]]) if recommendations else '  - Keep up the great work!'
            
            # Top directories
            top_dirs = report_context.get('topDirectories', [])
            dirs_text = ', '.join([f"{d['name']} ({d['count']} files)" for d in top_dirs[:5]]) if top_dirs else 'Not analyzed'
            
            # Dependencies breakdown
            deps = report_context.get('dependencies', {})
            npm_deps = len(deps.get('npm', {}).get('dependencies', {}))
            pip_deps = len(deps.get('pip', {}))
            deps_text = []
            if npm_deps > 0:
                deps_text.append(f"NPM: {npm_deps}")
            if pip_deps > 0:
                deps_text.append(f"Python: {pip_deps}")
            deps_summary = ', '.join(deps_text) if deps_text else 'None detected'
            
            context_message = f"""
**📊 USER'S UPLOADED CODE REPORT - MEMORIZE THIS INFORMATION:**

🏷️ **Project Details:**
  - Name: {report_context.get('projectName', 'Unknown')}
  - Total Files: {report_context.get('totalFiles', 0)}
  - Generated: {report_context.get('generatedAt', 'Recently')}

💻 **Languages Used:**
  - {lang_breakdown}
  - Total Languages: {len(languages)}

📈 **Quality Metrics:**
  - Health Score: {report_context.get('qualityScore', 'N/A')}/100
  - Test Coverage: {report_context.get('testCoverage', 0):.1f}%
  - Status: {"Excellent 🟢" if report_context.get('qualityScore', 0) >= 80 else "Good 🟡" if report_context.get('qualityScore', 0) >= 60 else "Needs Work 🔴"}

📦 **Dependencies:**
  - Total: {report_context.get('totalDependencies', 0)}
  - Breakdown: {deps_summary}

📁 **Top Directories:**
  - {dirs_text}

⚠️ **Issues Found ({len(issues)}):**
{issues_text}

💡 **Recommendations:**
{recs_text}

**IMPORTANT INSTRUCTIONS:**
- When user asks about "my code", "my project", "my report", or "the analysis", refer to THIS data
- Give specific answers using the exact numbers and details above
- Don't ask for GitHub repos when user wants info about THEIR uploaded code
- Be conversational and reference specific metrics naturally
- If user asks general questions about their code, explain the metrics in friendly terms
"""
            messages.append({"role": "system", "content": context_message})
        
        # Add conversation history if provided (last 8 messages for better context)
        if conversation_history:
            messages.extend(conversation_history[-8:])
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Call DeepSeek API
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'deepseek-chat',
            'messages': messages,
            'temperature': 0.3,  # Very low = highly focused, deterministic responses
            'max_tokens': 500,  # Shorter responses
            'top_p': 0.85,  # More focused sampling
            'frequency_penalty': 0.7,  # Strongly avoid repetition
            'presence_penalty': 0.8,   # Strongly stay on topic
            'stream': False
        }
        
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=35
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            return ai_response
        else:
            print(f"DeepSeek API Error: {response.status_code} - {response.text}")
            return fallback_response(user_message)
            
    except requests.exceptions.Timeout:
        print("DeepSeek API timeout")
        return "⏱️ Hmm, I'm thinking a bit slowly right now! Could you ask me again? I promise I'll be quicker! 😅"
    
    except Exception as e:
        print(f"DeepSeek AI Error: {str(e)}")
        return fallback_response(user_message)


def fallback_response(user_message):
    """Enhanced fallback responses when API fails"""
    message_lower = user_message.lower()
    
    # Report explanation
    if any(word in message_lower for word in ['report', 'explain', 'analysis', 'results', 'pdf']):
        return """📊 **Your Code Analysis Report Explained!**

Great question! Let me break down what each metric means:

**🟢 Health Score (0-100)**
Think of this as your code's overall grade! 
- 80-100: Excellent! Your code is top-notch! 🎉
- 60-79: Good! Some room for improvement
- 40-59: Fair - needs attention
- 0-39: Critical issues detected

**🧪 Test Coverage (%)**
Shows how much of your code is tested:
- 70%+: Great coverage!
- 40-69%: Add more tests
- <40%: Needs significant testing

**💻 Languages & Files**
Shows all programming languages detected and file counts

**📦 Dependencies**
External libraries your project uses (npm, pip, etc.)

**⚠️ Issues & Recommendations**
Smart suggestions to improve your code quality!

Want me to explain anything specific? 😊"""
    
    # What is AI
    elif 'what is ai' in message_lower or 'artificial intelligence' in message_lower:
        return """🤖 **What is AI (Artificial Intelligence)?**

Great question! Let me explain in simple terms:

**AI** is technology that makes computers "think" and learn like humans! 🧠

**What AI Can Do:**
✨ **Learn** from data and experiences
🔍 **Recognize** patterns (like detecting code issues!)
💬 **Understand** language (that's me talking to you!)
🎯 **Make decisions** based on information
🚀 **Solve problems** automatically

**How I Use AI:**
- 📊 Analyze your code structure
- 🔎 Detect bugs and issues
- 💡 Generate smart recommendations
- 📈 Calculate quality scores
- 🎨 Create beautiful reports

Think of me as your coding buddy who never sleeps and loves reviewing code! 😊

Want to see AI in action? Upload your code and I'll analyze it instantly! 🚀"""
    
    # General capabilities
    elif any(word in message_lower for word in ['what can you', 'help', 'do', 'capabilities']):
        return """🎯 **What I Can Do For You!**

Hey there! I'm your AI-powered code analyzer, and I'm here to help! Here's what makes me special:

**📊 Code Analysis**
- Scan 100+ programming languages instantly
- Python, JavaScript, Java, C++, Go, Rust, and many more!
- Count files, detect patterns, measure quality

**🎨 Beautiful Reports**
- Generate stunning PDF reports with charts
- Color-coded health scores
- Language distribution pie charts
- Professional design that impresses!

**💬 Smart Conversations** (That's us right now!)
- Answer programming questions
- Explain your code metrics
- Provide best practices
- Help troubleshoot issues

**🚀 Quick & Easy**
1. Click the **+** button
2. Upload your code folder
3. Get instant analysis!
4. Download beautiful PDF report

Try asking me: "What does health score mean?" or "How do I improve my code?" 😊"""
    
    # How to use
    elif any(word in message_lower for word in ['how', 'use', 'upload', 'start']):
        return """📚 **How to Use Me - Super Easy!**

Let me guide you through it! 👇

**Step 1: Upload Your Code** 📁
- Click the **+** button (next to where you type)
- Select your project folder
- I accept ALL code files (.py, .js, .java, .html, .css, etc.)
- ❌ No images/videos please!

**Step 2: Watch the Magic** ✨
- I'll scan your files in seconds
- Detect all programming languages
- Calculate quality score
- Find issues and opportunities

**Step 3: Get Your Report** 📄
- See instant results in chat
- Type **"yes"** when I ask
- Download beautiful PDF report
- Share with your team!

**Then Ask Me Anything!** 💬
- "Explain my report"
- "How do I improve?"
- "What's test coverage?"
- "Best practices for Python?"

Ready? Click that **+** button and let's analyze some code! 🚀"""
    
    # Default friendly response
    else:
        return """👋 Hey! I'm your friendly AI Code Analyzer!

I'm here to help you understand and improve your code! 😊

**Quick Help:**
- 📊 "Explain my report" - Understand your analysis
- 🔍 "What is [term]?" - Learn programming concepts  
- 💡 "How do I improve?" - Get actionable tips
- 📁 Click **+** button - Upload and analyze code!

What would you like to know? I'm all ears! 🎧✨"""


# Main chat function for compatibility
def chat(user_message):
    """Main chat interface - uses DeepSeek AI"""
    return chat_with_deepseek(user_message)
