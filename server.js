require('dotenv').config();
const express = require('express');
const session = require('express-session');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const fse = require('fs-extra');
const crypto = require('crypto');
const { Octokit } = require('@octokit/rest');
const PDFDocument = require('pdfkit');
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');

const app = express();

// Middleware
app.use(cors({
  origin: 'http://localhost:5000',
  credentials: true
}));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(session({
  secret: process.env.SESSION_SECRET || crypto.randomBytes(32).toString('hex'),
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: false, // Set to true in production with HTTPS
    httpOnly: true,
    maxAge: 24 * 60 * 60 * 1000 // 24 hours
  }
}));

const PORT = process.env.PORT || 3001;
const BASE_URL = process.env.BASE_URL || `http://localhost:${PORT}`;
const REPORT_DIR = process.env.REPORT_DIR || path.join(process.cwd(), 'data', 'reports');
const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY;
const DEEPSEEK_API_URL = process.env.DEEPSEEK_API_URL || 'https://api.deepseek.com/v1/chat/completions';
const DEEPSEEK_MODEL = process.env.DEEPSEEK_MODEL || 'deepseek-chat';

// Ensure report directory exists
fse.ensureDirSync(REPORT_DIR);

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Middleware to check if user is authenticated with GitHub
 */
function requireAuth(req, res, next) {
  if (!req.session || !req.session.ghToken) {
    return res.status(401).json({ error: 'Not authenticated with GitHub' });
  }
  next();
}

/**
 * Create Octokit instance from session token
 */
function octokitFromSession(req) {
  return new Octokit({
    auth: req.session.ghToken,
    userAgent: 'Codebase-Explorer-Agent/1.0'
  });
}

/**
 * Map file extension to programming language
 */
function mapExtToLanguage(filename) {
  const ext = path.extname(filename).toLowerCase();
  const map = {
    '.js': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript', '.jsx': 'JavaScript',
    '.py': 'Python', '.java': 'Java', '.rb': 'Ruby', '.php': 'PHP', '.go': 'Go',
    '.cs': 'C#', '.cpp': 'C++', '.c': 'C', '.h': 'C/C++', '.hpp': 'C++', '.rs': 'Rust',
    '.kt': 'Kotlin', '.swift': 'Swift', '.m': 'Objective-C', '.scala': 'Scala',
    '.sh': 'Shell', '.bash': 'Bash', '.yml': 'YAML', '.yaml': 'YAML',
    '.json': 'JSON', '.xml': 'XML', '.md': 'Markdown', '.html': 'HTML',
    '.css': 'CSS', '.scss': 'SCSS', '.sass': 'Sass', '.vue': 'Vue',
    '.sql': 'SQL', '.r': 'R', '.dart': 'Dart', '.lua': 'Lua'
  };
  return map[ext] || (ext ? ext.replace('.', '').toUpperCase() : 'Other');
}

/**
 * Fetch file content from GitHub
 */
async function fetchContent(octokit, owner, repo, ref, filepath) {
  try {
    const { data } = await octokit.repos.getContent({
      owner,
      repo,
      path: filepath,
      ref
    });
    if (Array.isArray(data) || !data.content) return null;
    const buff = Buffer.from(data.content, data.encoding || 'base64');
    return buff.toString('utf8');
  } catch (err) {
    console.log(`Could not fetch ${filepath}:`, err.message);
    return null;
  }
}

/**
 * Parse dependency files and extract package information
 */
function parseDependencies(files) {
  const out = { npm: {}, pip: {}, maven: [], golang: {}, other: {} };

  // Parse package.json (Node.js)
  if (files.packageJson) {
    try {
      const pj = JSON.parse(files.packageJson);
      out.npm = {
        dependencies: pj.dependencies || {},
        devDependencies: pj.devDependencies || {},
        name: pj.name,
        version: pj.version
      };
    } catch (e) {
      console.log('Error parsing package.json:', e.message);
    }
  }

  // Parse requirements.txt (Python)
  if (files.requirementsTxt) {
    const deps = {};
    files.requirementsTxt.split(/\r?\n/).forEach(line => {
      const t = line.trim();
      if (!t || t.startsWith('#')) return;
      const match = t.match(/^([a-zA-Z0-9\-_]+)([>=<~!]=?.*)?$/);
      if (match) {
        deps[match[1]] = match[2] ? match[2].trim() : 'latest';
      }
    });
    out.pip = deps;
  }

  // Parse pom.xml (Java Maven)
  if (files.pomXml) {
    const depMatches = [...files.pomXml.matchAll(
      /<dependency>[\s\S]*?<groupId>(.*?)<\/groupId>[\s\S]*?<artifactId>(.*?)<\/artifactId>[\s\S]*?(?:<version>(.*?)<\/version>)?[\s\S]*?<\/dependency>/g
    )];
    out.maven = depMatches.map(m => ({
      groupId: m[1],
      artifactId: m[2],
      version: m[3] || 'latest'
    }));
  }

  // Parse go.mod (Golang)
  if (files.goMod) {
    const deps = {};
    files.goMod.split(/\r?\n/).forEach(line => {
      const m = line.trim().match(/^([A-Za-z0-9._\-\/]+)\s+v?([0-9][^\s]+)$/);
      if (m) deps[m[1]] = m[2];
    });
    out.golang = deps;
  }

  // Parse Gemfile (Ruby)
  if (files.gemfile) {
    const deps = {};
    files.gemfile.split(/\r?\n/).forEach(line => {
      const m = line.trim().match(/gem\s+['"]([^'"]+)['"]/);
      if (m) deps[m[1]] = 'latest';
    });
    out.other.ruby = deps;
  }

  return out;
}

/**
 * Summarize languages used in the repository
 */
function summarizeLanguages(tree) {
  const langCounts = {};
  const langSizes = {};

  for (const node of tree) {
    if (node.type !== 'blob') continue;
    const lang = mapExtToLanguage(node.path);
    langCounts[lang] = (langCounts[lang] || 0) + 1;
    langSizes[lang] = (langSizes[lang] || 0) + (node.size || 0);
  }

  return { counts: langCounts, sizes: langSizes };
}

/**
 * Summarize top directories by file count
 */
function summarizeTopDirs(tree, topN = 10) {
  const counts = {};
  for (const node of tree) {
    if (node.type !== 'blob') continue;
    const dir = path.dirname(node.path).split('/')[0] || '.';
    counts[dir] = (counts[dir] || 0) + 1;
  }
  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, topN)
    .map(([name, count]) => ({ name, count }));
}

/**
 * Fetch recent commit activity
 */
async function fetchRecentCommits(octokit, owner, repo, defaultBranch) {
  try {
    const since = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString();
    const commits = [];
    let page = 1;

    // Fetch up to 300 commits (3 pages)
    while (page <= 3) {
      const { data } = await octokit.repos.listCommits({
        owner,
        repo,
        sha: defaultBranch,
        since,
        per_page: 100,
        page
      });
      commits.push(...data);
      if (data.length < 100) break;
      page++;
    }

    const uniqueAuthors = new Set(
      commits.map(c => c.author?.login || c.commit?.author?.email).filter(Boolean)
    );
    const lastCommitDate = commits[0]?.commit?.author?.date || null;

    return {
      totalLast90Days: commits.length,
      uniqueAuthors: uniqueAuthors.size,
      lastCommitDate,
      recentCommits: commits.slice(0, 10).map(c => ({
        sha: c.sha.substring(0, 7),
        message: c.commit?.message?.split('\n')[0] || '',
        author: c.author?.login || c.commit?.author?.name || 'Unknown',
        date: c.commit?.author?.date
      }))
    };
  } catch (err) {
    console.log('Error fetching commits:', err.message);
    return {
      totalLast90Days: 0,
      uniqueAuthors: 0,
      lastCommitDate: null,
      recentCommits: []
    };
  }
}

/**
 * Analyze code quality indicators
 */
function analyzeCodeQuality(tree, dependencies) {
  const issues = [];
  const recommendations = [];

  // Check repository size
  const totalFiles = tree.filter(n => n.type === 'blob').length;
  if (totalFiles > 5000) {
    issues.push('Very large repository with ' + totalFiles + ' files');
    recommendations.push('Consider modularizing into smaller services or packages');
  }

  // Check for test files
  const testFiles = tree.filter(n =>
    n.path.includes('test') || n.path.includes('spec') || n.path.includes('__tests__')
  ).length;
  const testCoverage = totalFiles > 0 ? (testFiles / totalFiles * 100).toFixed(1) : 0;
  if (testCoverage < 10) {
    issues.push('Low test coverage detected');
    recommendations.push('Add more unit and integration tests');
  }

  // Check dependency counts
  const npmDepCount = Object.keys(dependencies.npm?.dependencies || {}).length;
  const npmDevDepCount = Object.keys(dependencies.npm?.devDependencies || {}).length;
  if (npmDepCount > 100) {
    issues.push('High number of npm dependencies (' + npmDepCount + ')');
    recommendations.push('Review and remove unused dependencies');
  }

  // Check for documentation
  const hasReadme = tree.some(n => n.path.toLowerCase() === 'readme.md');
  const hasContributing = tree.some(n => n.path.toLowerCase() === 'contributing.md');
  if (!hasReadme) {
    issues.push('Missing README.md file');
    recommendations.push('Add comprehensive documentation');
  }

  // Check for configuration files
  const hasCI = tree.some(n =>
    n.path.includes('.github/workflows') ||
    n.path.includes('.gitlab-ci') ||
    n.path.includes('jenkins')
  );
  if (!hasCI) {
    recommendations.push('Set up CI/CD pipeline for automated testing');
  }

  return {
    issues,
    recommendations,
    metrics: {
      totalFiles,
      testFiles,
      testCoveragePercent: parseFloat(testCoverage),
      hasReadme,
      hasContributing,
      hasCI
    }
  };
}

/**
 * Generate HTML report
 */
function buildHtmlSummary(report) {
  const npmDeps = Object.keys(report.dependencies?.npm?.dependencies || {}).length;
  const npmDevDeps = Object.keys(report.dependencies?.npm?.devDependencies || {}).length;
  const pipDeps = Object.keys(report.dependencies?.pip || {}).length;
  const mavenDeps = Array.isArray(report.dependencies?.maven) ? report.dependencies.maven.length : 0;
  const totalDeps = npmDeps + npmDevDeps + pipDeps + mavenDeps;

  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${report.repo.fullName} - Codebase Analysis Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 20px rgba(0,0,0,0.08); }
        h1 { color: #2c3e50; font-size: 2.5em; margin-bottom: 10px; }
        h2 { color: #34495e; font-size: 1.8em; margin: 30px 0 15px; border-bottom: 3px solid #3498db; padding-bottom: 8px; }
        h3 { color: #555; margin: 20px 0 10px; }
        .meta { color: #7f8c8d; margin-bottom: 30px; font-size: 0.95em; }
        .meta strong { color: #2c3e50; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .card:hover { transform: translateY(-5px); }
        .card-title { font-size: 0.85em; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; }
        .card-value { font-size: 2.5em; font-weight: bold; margin-top: 10px; }
        .list { list-style: none; padding: 0; }
        .list li {
            padding: 12px;
            margin: 8px 0;
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }
        .issue { border-left-color: #e74c3c; background: #fee; }
        .recommendation { border-left-color: #2ecc71; background: #efe; }
        .lang-bar {
            display: flex;
            align-items: center;
            margin: 8px 0;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        .lang-name { min-width: 120px; font-weight: 600; color: #555; }
        .lang-progress {
            flex: 1;
            height: 24px;
            background: #e0e0e0;
            border-radius: 12px;
            overflow: hidden;
            margin: 0 15px;
        }
        .lang-fill {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            display: flex;
            align-items: center;
            padding-left: 10px;
            color: white;
            font-size: 0.85em;
            font-weight: bold;
        }
        .commit { padding: 10px; margin: 8px 0; background: #f8f9fa; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 0.9em; }
        .commit-sha { color: #3498db; font-weight: bold; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #ecf0f1; text-align: center; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Codebase Analysis Report</h1>
        <div class="meta">
            <strong>Repository:</strong> ${report.repo.fullName} | 
            <strong>Branch:</strong> ${report.repo.defaultBranch} | 
            <strong>Generated:</strong> ${new Date(report.generatedAt).toLocaleString()}
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-title">Total Files</div>
                <div class="card-value">${report.files.total.toLocaleString()}</div>
            </div>
            <div class="card">
                <div class="card-title">Languages</div>
                <div class="card-value">${Object.keys(report.files.languages.counts).length}</div>
            </div>
            <div class="card">
                <div class="card-title">Dependencies</div>
                <div class="card-value">${totalDeps}</div>
            </div>
            <div class="card">
                <div class="card-title">Open Issues</div>
                <div class="card-value">${report.activity.openIssues}</div>
            </div>
            <div class="card">
                <div class="card-title">Commits (90d)</div>
                <div class="card-value">${report.activity.commits90d}</div>
            </div>
            <div class="card">
                <div class="card-title">Contributors (90d)</div>
                <div class="card-value">${report.activity.authors90d}</div>
            </div>
        </div>

        <h2>📁 Top Directories</h2>
        <ul class="list">
            ${report.files.topDirs.map(d => `<li><strong>${d.name}</strong>: ${d.count} files</li>`).join('')}
        </ul>

        <h2>💻 Language Breakdown</h2>
        ${Object.entries(report.files.languages.counts)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 10)
          .map(([lang, count]) => {
            const percent = (count / report.files.total * 100).toFixed(1);
            return `
            <div class="lang-bar">
                <div class="lang-name">${lang}</div>
                <div class="lang-progress">
                    <div class="lang-fill" style="width: ${percent}%">${percent}%</div>
                </div>
                <div>${count} files</div>
            </div>`;
          }).join('')}

        <h2>📦 Dependencies</h2>
        ${npmDeps > 0 ? `<h3>NPM (${npmDeps} production + ${npmDevDeps} dev)</h3>` : ''}
        ${pipDeps > 0 ? `<h3>Python (${pipDeps} packages)</h3>` : ''}
        ${mavenDeps > 0 ? `<h3>Maven (${mavenDeps} artifacts)</h3>` : ''}

        <h2>⚠️ Issues Detected</h2>
        <ul class="list">
            ${report.quality.issues.length > 0 
              ? report.quality.issues.map(i => `<li class="issue">${i}</li>`).join('')
              : '<li>No major issues detected</li>'}
        </ul>

        <h2>✅ Recommendations</h2>
        <ul class="list">
            ${report.quality.recommendations.map(r => `<li class="recommendation">${r}</li>`).join('')}
        </ul>

        <h2>📝 Recent Commits</h2>
        ${report.activity.recentCommits.map(c => `
            <div class="commit">
                <span class="commit-sha">${c.sha}</span> - ${c.message}<br>
                <small>by ${c.author} on ${new Date(c.date).toLocaleDateString()}</small>
            </div>
        `).join('')}

        <div class="footer">
            <p>Generated by <strong>Codebase & Repository Explorer Agent</strong></p>
            <p>Powered by AI • Report ID: ${report.id}</p>
        </div>
    </div>
</body>
</html>`;
}

/**
 * Generate PDF report
 */
async function writePdfFromReport(report, outPath) {
  const doc = new PDFDocument({ size: 'A4', margin: 50 });
  
  return new Promise((resolve, reject) => {
    const stream = fs.createWriteStream(outPath);
    doc.pipe(stream);

    // Header
    doc.fontSize(24).fillColor('#2c3e50').text('Codebase Analysis Report', { underline: true });
    doc.moveDown(0.5);
    doc.fontSize(12).fillColor('#555')
       .text(`Repository: ${report.repo.fullName}`)
       .text(`Branch: ${report.repo.defaultBranch}`)
       .text(`Generated: ${new Date(report.generatedAt).toLocaleString()}`);
    doc.moveDown(1);

    // Summary Section
    doc.fontSize(16).fillColor('#2c3e50').text('Summary', { underline: true });
    doc.moveDown(0.3);
    doc.fontSize(11).fillColor('#333')
       .text(`Total Files: ${report.files.total}`)
       .text(`Languages: ${Object.keys(report.files.languages.counts).length}`)
       .text(`Open Issues: ${report.activity.openIssues}`)
       .text(`Commits (90 days): ${report.activity.commits90d}`)
       .text(`Active Contributors: ${report.activity.authors90d}`);
    doc.moveDown(1);

    // Top Directories
    doc.fontSize(16).fillColor('#2c3e50').text('Top Directories', { underline: true });
    doc.moveDown(0.3);
    doc.fontSize(11).fillColor('#333');
    report.files.topDirs.slice(0, 10).forEach(d => {
      doc.text(`• ${d.name}: ${d.count} files`);
    });
    doc.moveDown(1);

    // Languages
    doc.fontSize(16).fillColor('#2c3e50').text('Language Breakdown', { underline: true });
    doc.moveDown(0.3);
    doc.fontSize(11).fillColor('#333');
    Object.entries(report.files.languages.counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .forEach(([lang, count]) => {
        const percent = (count / report.files.total * 100).toFixed(1);
        doc.text(`• ${lang}: ${count} files (${percent}%)`);
      });
    doc.moveDown(1);

    // Issues
    if (report.quality.issues.length > 0) {
      doc.fontSize(16).fillColor('#e74c3c').text('Issues Detected', { underline: true });
      doc.moveDown(0.3);
      doc.fontSize(11).fillColor('#333');
      report.quality.issues.forEach(issue => {
        doc.text(`⚠ ${issue}`);
      });
      doc.moveDown(1);
    }

    // Recommendations
    doc.fontSize(16).fillColor('#2ecc71').text('Recommendations', { underline: true });
    doc.moveDown(0.3);
    doc.fontSize(11).fillColor('#333');
    report.quality.recommendations.forEach(rec => {
      doc.text(`✓ ${rec}`);
    });
    doc.moveDown(1);

    // Footer
    doc.fontSize(9).fillColor('#7f8c8d')
       .text(`Report ID: ${report.id}`, 50, doc.page.height - 50, { align: 'center' });

    doc.end();
    stream.on('finish', resolve);
    stream.on('error', reject);
  });
}

// ============================================================================
// API ROUTES
// ============================================================================

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'Codebase Repository Explorer Agent',
    version: '1.0.0',
    authenticated: !!req.session?.ghToken
  });
});

/**
 * Start GitHub OAuth flow
 */
app.get('/auth/github', (req, res) => {
  const clientId = process.env.GITHUB_CLIENT_ID;
  if (!clientId) {
    return res.status(500).json({ error: 'GitHub OAuth not configured' });
  }

  const state = crypto.randomBytes(16).toString('hex');
  req.session.oauthState = state;

  const scope = encodeURIComponent(process.env.GITHUB_SCOPE || 'repo,read:user');
  const redirectUri = encodeURIComponent(`${BASE_URL}/auth/github/callback`);
  const authorizeUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}&state=${state}`;

  res.redirect(authorizeUrl);
});

/**
 * GitHub OAuth callback
 */
app.get('/auth/github/callback', async (req, res) => {
  const { code, state } = req.query;

  if (!code || state !== req.session.oauthState) {
    return res.status(400).send('<h1>Invalid OAuth state</h1><p>Please try again.</p>');
  }

  try {
    const tokenResponse = await axios.post(
      'https://github.com/login/oauth/access_token',
      {
        client_id: process.env.GITHUB_CLIENT_ID,
        client_secret: process.env.GITHUB_CLIENT_SECRET,
        code,
        redirect_uri: `${BASE_URL}/auth/github/callback`,
        state
      },
      {
        headers: { Accept: 'application/json' }
      }
    );

    const { access_token, error } = tokenResponse.data;

    if (error || !access_token) {
      return res.status(401).send('<h1>OAuth Failed</h1><p>' + (error || 'No access token received') + '</p>');
    }

    req.session.ghToken = access_token;

    // Get user info
    const octokit = new Octokit({ auth: access_token });
    const { data: user } = await octokit.users.getAuthenticated();
    req.session.ghUser = {
      login: user.login,
      name: user.name,
      avatar: user.avatar_url
    };

    res.send(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>GitHub Connected</title>
        <style>
          body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
          .box { text-align: center; background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px); }
          h1 { margin: 0 0 20px 0; }
          button { background: white; color: #667eea; border: none; padding: 12px 30px; font-size: 16px; border-radius: 8px; cursor: pointer; margin-top: 20px; }
          button:hover { transform: scale(1.05); }
        </style>
      </head>
      <body>
        <div class="box">
          <h1>✅ GitHub Connected!</h1>
          <p>Welcome, <strong>${user.login}</strong></p>
          <button onclick="window.close()">Close this window</button>
          <script>
            setTimeout(() => {
              window.opener?.postMessage({ type: 'github_auth_success', user: '${user.login}' }, '*');
              window.close();
            }, 2000);
          </script>
        </div>
      </body>
      </html>
    `);
  } catch (err) {
    console.error('OAuth error:', err);
    res.status(500).send('<h1>OAuth Error</h1><p>' + err.message + '</p>');
  }
});

/**
 * Check authentication status
 */
app.get('/auth/status', (req, res) => {
  if (req.session?.ghToken && req.session?.ghUser) {
    res.json({
      authenticated: true,
      user: req.session.ghUser
    });
  } else {
    res.json({ authenticated: false });
  }
});

/**
 * Logout
 */
app.post('/auth/logout', (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: 'Logout failed' });
    }
    res.json({ success: true });
  });
});

/**
 * List user repositories
 */
app.get('/repos', requireAuth, async (req, res) => {
  try {
    const octokit = octokitFromSession(req);
    const repos = [];
    let page = 1;

    // Fetch up to 500 repos (5 pages)
    while (page <= 5) {
      const { data } = await octokit.repos.listForAuthenticatedUser({
        per_page: 100,
        page,
        sort: 'updated',
        direction: 'desc'
      });

      repos.push(...data.map(r => ({
        name: r.name,
        fullName: r.full_name,
        owner: r.owner.login,
        private: r.private,
        defaultBranch: r.default_branch,
        description: r.description,
        url: r.html_url,
        language: r.language,
        stars: r.stargazers_count,
        forks: r.forks_count,
        updatedAt: r.updated_at
      })));

      if (data.length < 100) break;
      page++;
    }

    res.json({ repos, count: repos.length });
  } catch (err) {
    console.error('Error fetching repos:', err);
    res.status(500).json({ error: 'Failed to fetch repositories', details: err.message });
  }
});

/**
 * Analyze a repository
 */
app.post('/analyze', requireAuth, async (req, res) => {
  const { owner, repo, ref } = req.body;

  if (!owner || !repo) {
    return res.status(400).json({ error: 'owner and repo are required' });
  }

  console.log(`Starting analysis for ${owner}/${repo}...`);

  try {
    const octokit = octokitFromSession(req);

    // Get repository info
    const { data: repoInfo } = await octokit.repos.get({ owner, repo });
    const defaultBranch = ref || repoInfo.default_branch || 'main';

    console.log(`Fetching file tree for branch: ${defaultBranch}...`);

    // Get recursive file tree
    const { data: treeData } = await octokit.git.getTree({
      owner,
      repo,
      tree_sha: defaultBranch,
      recursive: 'true'
    });

    const allNodes = treeData.tree || [];
    const files = allNodes.filter(n => n.type === 'blob');

    console.log(`Found ${files.length} files. Analyzing structure...`);

    // Analyze languages and structure
    const languageData = summarizeLanguages(files);
    const topDirs = summarizeTopDirs(files, 15);

    console.log('Fetching dependency files...');

    // Fetch dependency files
    const manifests = {
      packageJson: await fetchContent(octokit, owner, repo, defaultBranch, 'package.json'),
      requirementsTxt: await fetchContent(octokit, owner, repo, defaultBranch, 'requirements.txt'),
      pomXml: await fetchContent(octokit, owner, repo, defaultBranch, 'pom.xml'),
      goMod: await fetchContent(octokit, owner, repo, defaultBranch, 'go.mod'),
      gemfile: await fetchContent(octokit, owner, repo, defaultBranch, 'Gemfile')
    };

    const dependencies = parseDependencies(manifests);

    console.log('Fetching commit activity...');

    // Get commit activity
    const commitData = await fetchRecentCommits(octokit, owner, repo, defaultBranch);

    console.log('Analyzing code quality...');

    // Analyze code quality
    const quality = analyzeCodeQuality(allNodes, dependencies);

    // Build report
    const report = {
      id: uuidv4(),
      generatedAt: new Date().toISOString(),
      repo: {
        owner,
        name: repo,
        fullName: `${owner}/${repo}`,
        defaultBranch,
        visibility: repoInfo.private ? 'private' : 'public',
        description: repoInfo.description || '',
        url: repoInfo.html_url,
        stars: repoInfo.stargazers_count,
        forks: repoInfo.forks_count,
        createdAt: repoInfo.created_at,
        updatedAt: repoInfo.updated_at
      },
      files: {
        total: files.length,
        languages: languageData,
        topDirs
      },
      dependencies,
      activity: {
        openIssues: repoInfo.open_issues_count || 0,
        commits90d: commitData.totalLast90Days,
        authors90d: commitData.uniqueAuthors,
        lastCommitDate: commitData.lastCommitDate,
        recentCommits: commitData.recentCommits
      },
      quality,
      source: {
        mode: 'github-api',
        analyzedBy: req.session.ghUser?.login
      }
    };

    console.log('Saving report...');

    // Save report
    const jsonPath = path.join(REPORT_DIR, `${report.id}.json`);
    const htmlPath = path.join(REPORT_DIR, `${report.id}.html`);

    await fse.writeJson(jsonPath, report, { spaces: 2 });
    await fse.writeFile(htmlPath, buildHtmlSummary(report), 'utf8');

    console.log(`✓ Analysis complete! Report ID: ${report.id}`);

    res.json({
      success: true,
      reportId: report.id,
      summary: {
        totalFiles: report.files.total,
        languages: Object.keys(report.files.languages.counts).length,
        dependencies: Object.keys(dependencies.npm?.dependencies || {}).length,
        openIssues: report.activity.openIssues,
        commits90d: report.activity.commits90d
      },
      downloadUrls: {
        json: `/reports/${report.id}/json`,
        html: `/reports/${report.id}/html`,
        pdf: `/reports/${report.id}/pdf`
      }
    });
  } catch (err) {
    console.error('Analysis error:', err);
    res.status(500).json({
      error: 'Analysis failed',
      details: err.message,
      stack: process.env.NODE_ENV === 'development' ? err.stack : undefined
    });
  }
});

/**
 * Get report (JSON)
 */
app.get('/reports/:id/json', async (req, res) => {
  try {
    const reportPath = path.join(REPORT_DIR, `${req.params.id}.json`);
    if (!fs.existsSync(reportPath)) {
      return res.status(404).json({ error: 'Report not found' });
    }
    const report = await fse.readJson(reportPath);
    res.json(report);
  } catch (err) {
    res.status(500).json({ error: 'Failed to load report' });
  }
});

/**
 * Get report (HTML)
 */
app.get('/reports/:id/html', async (req, res) => {
  try {
    const htmlPath = path.join(REPORT_DIR, `${req.params.id}.html`);
    if (!fs.existsSync(htmlPath)) {
      return res.status(404).send('<h1>Report not found</h1>');
    }
    const html = await fse.readFile(htmlPath, 'utf8');
    res.setHeader('Content-Type', 'text/html');
    res.send(html);
  } catch (err) {
    res.status(500).send('<h1>Error loading report</h1>');
  }
});

/**
 * Generate and download PDF report
 */
app.get('/reports/:id/pdf', async (req, res) => {
  try {
    const jsonPath = path.join(REPORT_DIR, `${req.params.id}.json`);
    const pdfPath = path.join(REPORT_DIR, `${req.params.id}.pdf`);

    if (!fs.existsSync(jsonPath)) {
      return res.status(404).json({ error: 'Report not found' });
    }

    // Check if PDF already exists
    if (!fs.existsSync(pdfPath)) {
      console.log('Generating PDF...');
      const report = await fse.readJson(jsonPath);
      await writePdfFromReport(report, pdfPath);
    }

    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename="${req.params.id}.pdf"`);
    fs.createReadStream(pdfPath).pipe(res);
  } catch (err) {
    console.error('PDF generation error:', err);
    res.status(500).json({ error: 'Failed to generate PDF', details: err.message });
  }
});

/**
 * List all reports
 */
app.get('/reports', async (req, res) => {
  try {
    const files = await fse.readdir(REPORT_DIR);
    const jsonFiles = files.filter(f => f.endsWith('.json'));

    const reports = await Promise.all(
      jsonFiles.map(async (file) => {
        const data = await fse.readJson(path.join(REPORT_DIR, file));
        return {
          id: data.id,
          repo: data.repo.fullName,
          generatedAt: data.generatedAt,
          files: data.files.total,
          languages: Object.keys(data.files.languages.counts).length
        };
      })
    );

    res.json({ reports: reports.sort((a, b) => new Date(b.generatedAt) - new Date(a.generatedAt)) });
  } catch (err) {
    res.status(500).json({ error: 'Failed to list reports' });
  }
});

/**
 * Ask questions about a report using DeepSeek API
 */
app.post('/qa', requireAuth, async (req, res) => {
  const { reportId, question } = req.body;

  if (!reportId || !question) {
    return res.status(400).json({ error: 'reportId and question are required' });
  }

  if (!DEEPSEEK_API_KEY) {
    return res.status(500).json({ error: 'DeepSeek API key not configured' });
  }

  try {
    // Load report
    const reportPath = path.join(REPORT_DIR, `${reportId}.json`);
    if (!fs.existsSync(reportPath)) {
      return res.status(404).json({ error: 'Report not found' });
    }

    const report = await fse.readJson(reportPath);

    // Build context for LLM
    const context = `
You are an AI assistant helping developers understand their codebase analysis report.

Repository: ${report.repo.fullName}
Total Files: ${report.files.total}
Languages: ${Object.entries(report.files.languages.counts).map(([k,v]) => `${k} (${v})`).join(', ')}
Dependencies: ${JSON.stringify(report.dependencies, null, 2)}
Issues: ${report.quality.issues.join('; ')}
Recommendations: ${report.quality.recommendations.join('; ')}
Recent Activity: ${report.activity.commits90d} commits in last 90 days by ${report.activity.authors90d} contributors

Based on this codebase analysis, answer the following question:
${question}
`;

    console.log('Calling DeepSeek API...');

    // Call DeepSeek API
    const response = await axios.post(
      DEEPSEEK_API_URL,
      {
        model: DEEPSEEK_MODEL,
        messages: [
          {
            role: 'system',
            content: 'You are an expert software engineer and code analyst. Provide clear, actionable insights about codebases.'
          },
          {
            role: 'user',
            content: context
          }
        ],
        temperature: 0.7,
        max_tokens: 1000
      },
      {
        headers: {
          'Authorization': `Bearer ${DEEPSEEK_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const answer = response.data.choices[0]?.message?.content || 'No response generated';

    res.json({
      question,
      answer,
      reportId,
      timestamp: new Date().toISOString()
    });
  } catch (err) {
    console.error('DeepSeek API error:', err.response?.data || err.message);
    res.status(500).json({
      error: 'Failed to get answer from AI',
      details: err.response?.data?.error?.message || err.message
    });
  }
});

// ============================================================================
// START SERVER
// ============================================================================

app.listen(PORT, () => {
  console.log('');
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║   Codebase & Repository Explorer Agent                    ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  console.log('');
  console.log(`🚀 Server running on: ${BASE_URL}`);
  console.log(`📊 Report storage: ${REPORT_DIR}`);
  console.log(`🔐 GitHub OAuth: ${process.env.GITHUB_CLIENT_ID ? 'Configured' : 'NOT CONFIGURED'}`);
  console.log(`🤖 DeepSeek API: ${DEEPSEEK_API_KEY ? 'Configured' : 'NOT CONFIGURED'}`);
  console.log('');
  console.log('Available endpoints:');
  console.log('  GET  /health');
  console.log('  GET  /auth/github');
  console.log('  GET  /auth/status');
  console.log('  GET  /repos');
  console.log('  POST /analyze');
  console.log('  GET  /reports');
  console.log('  GET  /reports/:id/json');
  console.log('  GET  /reports/:id/html');
  console.log('  GET  /reports/:id/pdf');
  console.log('  POST /qa');
  console.log('');
});
