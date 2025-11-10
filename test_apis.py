"""
Test script for API integrations
Tests DeepSeek AI, GitHub API, and DuckDuckGo Search
"""

print("🧪 Testing AI Code Analyzer API Integrations...\n")

# Test 1: DeepSeek AI
print("1️⃣ Testing DeepSeek AI...")
try:
    from deepseek_chat import chat_with_deepseek
    
    # Test basic conversation
    response = chat_with_deepseek(
        "Hello! What can you help me with?",
        [],
        None
    )
    
    if response and len(response) > 20:
        print("✅ DeepSeek AI working!")
        print(f"   Sample response: {response[:100]}...")
    else:
        print("⚠️ DeepSeek AI response seems short")
        
except Exception as e:
    print(f"❌ DeepSeek AI error: {e}")

print()

# Test 2: GitHub API
print("2️⃣ Testing GitHub API...")
try:
    from github_api import analyze_github_repo, format_github_analysis
    
    # Test with a small repo
    analysis = analyze_github_repo("octocat/Hello-World")
    
    if analysis and analysis.get('repository'):
        repo = analysis['repository']
        print("✅ GitHub API working!")
        print(f"   Repo: {repo['full_name']}")
        print(f"   Stars: {repo['stars']}")
        print(f"   Language: {repo['language']}")
    else:
        print("⚠️ GitHub API returned no data")
        
except Exception as e:
    print(f"❌ GitHub API error: {e}")

print()

# Test 3: DuckDuckGo Search
print("3️⃣ Testing DuckDuckGo Search...")
try:
    from search_rag import search_chat
    
    # Test search
    response = search_chat("Python programming language")
    
    if response and len(response) > 20:
        print("✅ DuckDuckGo Search working!")
        print(f"   Sample response: {response[:100]}...")
    else:
        print("⚠️ DuckDuckGo response seems short")
        
except Exception as e:
    print(f"❌ DuckDuckGo error: {e}")

print()
print("=" * 60)
print("🎉 API Integration Test Complete!")
print("=" * 60)
