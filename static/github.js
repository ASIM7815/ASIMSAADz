// GitHub Repository Explorer JavaScript
// Handles GitHub authentication, repository selection, and analysis display

const NODE_BACKEND_URL = 'http://localhost:3001';
let currentReportId = null;

// Initialize GitHub functionality
document.addEventListener('DOMContentLoaded', () => {
    const githubBtn = document.getElementById('githubBtn');
    const modal = document.getElementById('githubModal');
    const closeModal = document.getElementById('closeModal');

    // Open GitHub modal
    githubBtn.addEventListener('click', openGitHubModal);
    
    // Close modal
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close modal on outside click
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Listen for auth success from popup
    window.addEventListener('message', (event) => {
        if (event.data.type === 'github_auth_success') {
            console.log('GitHub auth successful!');
            loadRepositoryList();
        }
    });

    // Check if already authenticated
    checkGitHubAuth();
});

/**
 * Check GitHub authentication status
 */
async function checkGitHubAuth() {
    try {
        const response = await fetch(`${NODE_BACKEND_URL}/auth/status`, {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.authenticated) {
            console.log('✓ GitHub authenticated:', data.user.login);
            updateGitHubButton(true, data.user);
        }
    } catch (error) {
        console.log('GitHub backend not available or not authenticated');
    }
}

/**
 * Update GitHub button appearance based on auth status
 */
function updateGitHubButton(authenticated, user = null) {
    const githubBtn = document.getElementById('githubBtn');
    
    if (authenticated && user) {
        githubBtn.title = `GitHub: ${user.login}`;
        githubBtn.style.background = 'linear-gradient(135deg, #2ecc71, #27ae60)';
    }
}

/**
 * Open GitHub modal
 */
async function openGitHubModal() {
    const modal = document.getElementById('githubModal');
    const modalBody = document.getElementById('modalBody');
    
    modal.style.display = 'flex';
    modalBody.innerHTML = '<div class="loading">Checking backend availability...</div>';

    try {
        const response = await fetch(`${NODE_BACKEND_URL}/health`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Backend not responding');
        }

        // Backend is available, check authentication
        const authResponse = await fetch(`${NODE_BACKEND_URL}/auth/status`, {
            credentials: 'include'
        });
        const data = await authResponse.json();

        if (data.authenticated) {
            loadRepositoryList();
        } else {
            showGitHubLogin();
        }
    } catch (error) {
        modalBody.innerHTML = `
            <div class="backend-info">
                <h3>⚙️ GitHub Repository Explorer</h3>
                <p>To use the GitHub analysis feature, you need to start the Node.js backend server.</p>
                
                <div class="setup-steps">
                    <h4>Quick Setup:</h4>
                    <div class="step-item">
                        <strong>1.</strong> Open a new terminal in the project folder
                    </div>
                    <div class="step-item">
                        <strong>2.</strong> Install dependencies:
                        <pre>npm install</pre>
                    </div>
                    <div class="step-item">
                        <strong>3.</strong> Start the backend:
                        <pre>node server.js</pre>
                    </div>
                    <div class="step-item">
                        <strong>4.</strong> Click the GitHub button again
                    </div>
                </div>

                <div class="feature-info">
                    <h4>✨ What You'll Get:</h4>
                    <ul>
                        <li>📊 Complete repository analysis</li>
                        <li>💻 Language and dependency detection</li>
                        <li>📈 Code quality metrics</li>
                        <li>📄 PDF report generation</li>
                        <li>🤖 AI-powered code insights</li>
                    </ul>
                </div>

                <p class="note">📖 See <strong>COMPLETE_SETUP_GUIDE.md</strong> for detailed instructions</p>
            </div>
        `;
    }
}

/**
 * Show GitHub login button
 */
function showGitHubLogin() {
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
        <div class="auth-section">
            <h3>🔐 Connect to GitHub</h3>
            <p>Sign in with your GitHub account to analyze your repositories</p>
            <button class="github-login-btn" onclick="loginWithGitHub()">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                Sign in with GitHub
            </button>
            <p class="note">We only request read-only access to your repositories</p>
        </div>
    `;
}

/**
 * Initiate GitHub OAuth login
 */
function loginWithGitHub() {
    const authUrl = `${NODE_BACKEND_URL}/auth/github`;
    const popup = window.open(authUrl, 'GitHubAuth', 'width=600,height=700');
    
    // Check if popup is closed
    const checkPopup = setInterval(() => {
        if (popup.closed) {
            clearInterval(checkPopup);
            setTimeout(() => {
                checkGitHubAuth().then(() => {
                    loadRepositoryList();
                });
            }, 500);
        }
    }, 1000);
}

/**
 * Load and display repository list
 */
async function loadRepositoryList() {
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = '<div class="loading">Loading repositories...</div>';

    try {
        const response = await fetch(`${NODE_BACKEND_URL}/repos`, {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to fetch repositories');
        }

        const data = await response.json();
        displayRepositories(data.repos);
    } catch (error) {
        modalBody.innerHTML = `
            <div class="error-message">
                <h3>⚠️ Error Loading Repositories</h3>
                <p>${error.message}</p>
                <button onclick="loadRepositoryList()">Retry</button>
            </div>
        `;
    }
}

/**
 * Display repository list
 */
function displayRepositories(repos) {
    const modalBody = document.getElementById('modalBody');
    
    if (!repos || repos.length === 0) {
        modalBody.innerHTML = `
            <div class="no-repos">
                <h3>No repositories found</h3>
                <p>Create a repository on GitHub to get started</p>
            </div>
        `;
        return;
    }

    const repoHTML = repos.map(repo => `
        <div class="repo-item" onclick='analyzeRepository("${repo.owner}", "${repo.name}")'>
            <div class="repo-info">
                <h4>${repo.fullName}</h4>
                <p>${repo.description || 'No description'}</p>
                <div class="repo-meta">
                    ${repo.language ? `<span class="badge">${repo.language}</span>` : ''}
                    <span>⭐ ${repo.stars || 0}</span>
                    <span>🔱 ${repo.forks || 0}</span>
                    ${repo.private ? '<span class="badge private">Private</span>' : ''}
                </div>
            </div>
            <div class="repo-action">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M9 18l6-6-6-6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
        </div>
    `).join('');

    modalBody.innerHTML = `
        <div class="repo-list-header">
            <h3>Select a Repository to Analyze</h3>
            <input type="text" id="repoSearch" placeholder="Search repositories..." class="search-input">
        </div>
        <div class="repo-list" id="repoList">
            ${repoHTML}
        </div>
    `;

    // Add search functionality
    document.getElementById('repoSearch').addEventListener('input', (e) => {
        const search = e.target.value.toLowerCase();
        const items = document.querySelectorAll('.repo-item');
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(search) ? 'flex' : 'none';
        });
    });
}

/**
 * Analyze selected repository
 */
async function analyzeRepository(owner, repo) {
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
        <div class="analyzing">
            <div class="spinner"></div>
            <h3>🔍 Analyzing ${owner}/${repo}</h3>
            <p>This may take a moment...</p>
            <div class="progress-steps">
                <div class="step active">Fetching repository data</div>
                <div class="step">Analyzing file structure</div>
                <div class="step">Parsing dependencies</div>
                <div class="step">Checking commit history</div>
                <div class="step">Generating report</div>
            </div>
        </div>
    `;

    try {
        const response = await fetch(`${NODE_BACKEND_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ owner, repo })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.details || error.error || 'Analysis failed');
        }

        const data = await response.json();
        currentReportId = data.reportId;
        displayReport(data.reportId);
    } catch (error) {
        modalBody.innerHTML = `
            <div class="error-message">
                <h3>⚠️ Analysis Failed</h3>
                <p>${error.message}</p>
                <button onclick="loadRepositoryList()">Back to Repositories</button>
            </div>
        `;
    }
}

/**
 * Display analysis report
 */
async function displayReport(reportId) {
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = '<div class="loading">Loading report...</div>';

    try {
        const response = await fetch(`${NODE_BACKEND_URL}/reports/${reportId}/json`, {
            credentials: 'include'
        });
        const report = await response.json();

        const totalDeps = 
            Object.keys(report.dependencies?.npm?.dependencies || {}).length +
            Object.keys(report.dependencies?.npm?.devDependencies || {}).length +
            Object.keys(report.dependencies?.pip || {}).length;

        const languageCharts = Object.entries(report.files.languages.counts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([lang, count]) => {
                const percent = (count / report.files.total * 100).toFixed(1);
                return `
                    <div class="lang-bar">
                        <span class="lang-name">${lang}</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${percent}%"></div>
                        </div>
                        <span class="lang-count">${count}</span>
                    </div>
                `;
            }).join('');

        modalBody.innerHTML = `
            <div class="report-view">
                <div class="report-header">
                    <h2>📊 ${report.repo.fullName}</h2>
                    <div class="report-actions">
                        <button onclick="downloadReport('${reportId}', 'pdf')" class="action-btn">
                            📄 Download PDF
                        </button>
                        <button onclick="downloadReport('${reportId}', 'html')" class="action-btn">
                            🌐 View HTML
                        </button>
                        <button onclick="loadRepositoryList()" class="action-btn">
                            ← Back
                        </button>
                    </div>
                </div>

                <div class="report-grid">
                    <div class="stat-card">
                        <div class="stat-value">${report.files.total.toLocaleString()}</div>
                        <div class="stat-label">Total Files</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${Object.keys(report.files.languages.counts).length}</div>
                        <div class="stat-label">Languages</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${totalDeps}</div>
                        <div class="stat-label">Dependencies</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${report.activity.commits90d}</div>
                        <div class="stat-label">Commits (90d)</div>
                    </div>
                </div>

                <div class="report-section">
                    <h3>💻 Language Breakdown</h3>
                    ${languageCharts}
                </div>

                <div class="report-section">
                    <h3>📁 Top Directories</h3>
                    <div class="dir-list">
                        ${report.files.topDirs.slice(0, 10).map(d => 
                            `<div class="dir-item"><strong>${d.name}</strong>: ${d.count} files</div>`
                        ).join('')}
                    </div>
                </div>

                ${report.quality.issues.length > 0 ? `
                <div class="report-section">
                    <h3>⚠️ Issues Detected</h3>
                    <div class="issue-list">
                        ${report.quality.issues.map(i => `<div class="issue-item">⚠ ${i}</div>`).join('')}
                    </div>
                </div>
                ` : ''}

                <div class="report-section">
                    <h3>✅ Recommendations</h3>
                    <div class="rec-list">
                        ${report.quality.recommendations.map(r => `<div class="rec-item">✓ ${r}</div>`).join('')}
                    </div>
                </div>

                <div class="report-section">
                    <h3>💬 Ask Questions About This Codebase</h3>
                    <div class="qa-section">
                        <input type="text" id="qaInput" placeholder="e.g., What are the main security concerns?" class="qa-input">
                        <button onclick="askQuestion('${reportId}')" class="qa-btn">Ask AI</button>
                    </div>
                    <div id="qaResponse" class="qa-response"></div>
                </div>
            </div>
        `;
    } catch (error) {
        modalBody.innerHTML = `
            <div class="error-message">
                <h3>⚠️ Error Loading Report</h3>
                <p>${error.message}</p>
                <button onclick="loadRepositoryList()">Back to Repositories</button>
            </div>
        `;
    }
}

/**
 * Download report
 */
function downloadReport(reportId, format) {
    const url = `${NODE_BACKEND_URL}/reports/${reportId}/${format}`;
    
    if (format === 'html') {
        window.open(url, '_blank');
    } else {
        const link = document.createElement('a');
        link.href = url;
        link.download = `report-${reportId}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

/**
 * Ask AI question about the report
 */
async function askQuestion(reportId) {
    const input = document.getElementById('qaInput');
    const question = input.value.trim();
    const responseDiv = document.getElementById('qaResponse');

    if (!question) {
        responseDiv.innerHTML = '<div class="error">Please enter a question</div>';
        return;
    }

    responseDiv.innerHTML = '<div class="loading">AI is thinking...</div>';

    try {
        const response = await fetch(`${NODE_BACKEND_URL}/qa`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ reportId, question })
        });

        if (!response.ok) {
            throw new Error('Failed to get AI response');
        }

        const data = await response.json();
        responseDiv.innerHTML = `
            <div class="qa-answer">
                <strong>Q: ${data.question}</strong>
                <p>${data.answer}</p>
            </div>
        `;
        input.value = '';
    } catch (error) {
        responseDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
}
