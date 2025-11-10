"""
GitHub API Integration for Repository Analysis
Fetches repository metadata, commits, contributors, and more
"""

import requests
import os
from datetime import datetime

# GitHub API configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')  # Optional: Add your GitHub token for higher rate limits
GITHUB_API_BASE = "https://api.github.com"

def parse_github_url(url):
    """
    Extract owner and repo name from GitHub URL
    
    Examples:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - github.com/owner/repo
    """
    url = url.strip().rstrip('/')
    
    # Remove protocol
    url = url.replace('https://', '').replace('http://', '')
    
    # Remove .git extension
    url = url.replace('.git', '')
    
    # Extract owner and repo
    parts = url.split('/')
    if len(parts) >= 3 and parts[0] == 'github.com':
        return parts[1], parts[2]
    elif len(parts) >= 2:
        return parts[0], parts[1]
    
    return None, None

def get_repo_info(owner, repo):
    """
    Get basic repository information
    
    Returns:
    {
        'name': str,
        'description': str,
        'stars': int,
        'forks': int,
        'language': str,
        'created_at': str,
        'updated_at': str,
        'open_issues': int,
        'size': int (KB),
        'topics': list,
        'license': str
    }
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'name': data.get('name', ''),
            'full_name': data.get('full_name', ''),
            'description': data.get('description', 'No description'),
            'stars': data.get('stargazers_count', 0),
            'forks': data.get('forks_count', 0),
            'watchers': data.get('watchers_count', 0),
            'language': data.get('language', 'Unknown'),
            'created_at': data.get('created_at', ''),
            'updated_at': data.get('updated_at', ''),
            'pushed_at': data.get('pushed_at', ''),
            'open_issues': data.get('open_issues_count', 0),
            'size': data.get('size', 0),
            'topics': data.get('topics', []),
            'license': data.get('license', {}).get('name', 'No license'),
            'homepage': data.get('homepage', ''),
            'default_branch': data.get('default_branch', 'main')
        }
    except requests.exceptions.RequestException as e:
        print(f"[GitHub API Error] Failed to fetch repo info: {e}")
        return None

def get_recent_commits(owner, repo, limit=10):
    """
    Get recent commits from the repository
    
    Returns: List of commits with:
    - sha: Commit hash
    - message: Commit message
    - author: Author name
    - date: Commit date
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
    params = {'per_page': limit}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        commits = []
        for commit in data:
            commits.append({
                'sha': commit.get('sha', '')[:7],
                'message': commit.get('commit', {}).get('message', '').split('\n')[0],
                'author': commit.get('commit', {}).get('author', {}).get('name', 'Unknown'),
                'date': commit.get('commit', {}).get('author', {}).get('date', ''),
                'url': commit.get('html_url', '')
            })
        
        return commits
    except requests.exceptions.RequestException as e:
        print(f"[GitHub API Error] Failed to fetch commits: {e}")
        return []

def get_contributors(owner, repo, limit=10):
    """
    Get top contributors to the repository
    
    Returns: List of contributors with:
    - login: GitHub username
    - contributions: Number of contributions
    - avatar_url: Profile picture URL
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contributors"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
    params = {'per_page': limit}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        contributors = []
        for contributor in data:
            contributors.append({
                'login': contributor.get('login', 'Unknown'),
                'contributions': contributor.get('contributions', 0),
                'avatar_url': contributor.get('avatar_url', ''),
                'profile_url': contributor.get('html_url', '')
            })
        
        return contributors
    except requests.exceptions.RequestException as e:
        print(f"[GitHub API Error] Failed to fetch contributors: {e}")
        return []

def get_languages(owner, repo):
    """
    Get programming languages used in the repository
    
    Returns: Dict of language: bytes
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[GitHub API Error] Failed to fetch languages: {e}")
        return {}

def analyze_github_repo(github_url_or_name):
    """
    Comprehensive GitHub repository analysis
    
    Args:
        github_url_or_name: Full GitHub URL or 'owner/repo' format
    
    Returns:
        Dict with complete repository analysis or None if failed
    """
    # Parse URL to get owner and repo
    if '/' in github_url_or_name:
        if 'github.com' in github_url_or_name:
            owner, repo = parse_github_url(github_url_or_name)
        else:
            parts = github_url_or_name.split('/')
            owner, repo = parts[0], parts[1] if len(parts) >= 2 else None
    else:
        print("[GitHub API Error] Invalid repository format. Use 'owner/repo' or full URL")
        return None
    
    if not owner or not repo:
        print("[GitHub API Error] Could not extract owner/repo from input")
        return None
    
    print(f"[GitHub API] Analyzing repository: {owner}/{repo}")
    
    # Fetch all data
    repo_info = get_repo_info(owner, repo)
    if not repo_info:
        return None
    
    commits = get_recent_commits(owner, repo, limit=10)
    contributors = get_contributors(owner, repo, limit=10)
    languages = get_languages(owner, repo)
    
    # Calculate language percentages
    total_bytes = sum(languages.values())
    language_percentages = {}
    if total_bytes > 0:
        for lang, bytes_count in languages.items():
            language_percentages[lang] = round((bytes_count / total_bytes) * 100, 1)
    
    return {
        'repository': repo_info,
        'recent_commits': commits,
        'top_contributors': contributors,
        'languages': language_percentages,
        'analysis_timestamp': datetime.now().isoformat()
    }

def format_github_analysis(analysis):
    """
    Format GitHub analysis into human-readable text
    
    Args:
        analysis: Dict from analyze_github_repo()
    
    Returns:
        Formatted string for AI context
    """
    if not analysis:
        return "Unable to fetch GitHub repository data."
    
    repo = analysis['repository']
    
    output = f"""
📦 **GitHub Repository Analysis**

**{repo['full_name']}**
{repo['description']}

⭐ Stars: {repo['stars']:,} | 🍴 Forks: {repo['forks']:,} | 👀 Watchers: {repo['watchers']:,}
🐛 Open Issues: {repo['open_issues']} | 📦 Size: {repo['size']:,} KB
🏷️ License: {repo['license']}
📅 Created: {repo['created_at'][:10]} | Last updated: {repo['updated_at'][:10]}

**Languages:**
"""
    
    for lang, percentage in analysis['languages'].items():
        output += f"  • {lang}: {percentage}%\n"
    
    output += "\n**Recent Commits:**\n"
    for commit in analysis['recent_commits'][:5]:
        output += f"  • [{commit['sha']}] {commit['message']} - {commit['author']} ({commit['date'][:10]})\n"
    
    output += "\n**Top Contributors:**\n"
    for contributor in analysis['top_contributors'][:5]:
        output += f"  • {contributor['login']}: {contributor['contributions']} contributions\n"
    
    return output

# Test function
if __name__ == "__main__":
    # Example: Analyze Flask repository
    analysis = analyze_github_repo("https://github.com/pallets/flask")
    if analysis:
        print(format_github_analysis(analysis))
