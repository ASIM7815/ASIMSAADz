// Code Upload and Analysis JavaScript
// Handles local folder upload and code analysis

// Allowed code file extensions
const CODE_EXTENSIONS = [
    '.js', '.jsx', '.ts', '.tsx',           // JavaScript/TypeScript
    '.py', '.pyw',                          // Python
    '.java',                                // Java
    '.cpp', '.c', '.h', '.hpp', '.cc',     // C/C++
    '.cs',                                  // C#
    '.go',                                  // Go
    '.rs',                                  // Rust
    '.rb',                                  // Ruby
    '.php',                                 // PHP
    '.swift',                               // Swift
    '.kt', '.kts',                          // Kotlin
    '.scala',                               // Scala
    '.html', '.htm',                        // HTML
    '.css', '.scss', '.sass', '.less',     // CSS
    '.json', '.xml', '.yaml', '.yml',      // Config
    '.md', '.txt',                          // Documentation
    '.sh', '.bash', '.bat', '.ps1',        // Scripts
    '.sql',                                 // SQL
    '.r',                                   // R
    '.dart',                                // Dart
    '.lua',                                 // Lua
    '.vue'                                  // Vue
];

let uploadedFiles = [];
let analysisInProgress = false;

// Initialize upload functionality
document.addEventListener('DOMContentLoaded', () => {
    const addBtn = document.getElementById('addBtn');
    const folderInput = document.getElementById('folderInput');

    // Click + button to trigger folder upload
    addBtn.addEventListener('click', () => {
        if (analysisInProgress) {
            alert('⚠️ Analysis in progress. Please wait...');
            return;
        }
        folderInput.click();
    });

    // Handle folder selection
    folderInput.addEventListener('change', handleFolderUpload);
});

/**
 * Handle folder upload
 */
async function handleFolderUpload(event) {
    const files = Array.from(event.target.files);
    
    if (files.length === 0) {
        return;
    }

    // Filter only code files
    uploadedFiles = files.filter(file => {
        const ext = getFileExtension(file.name);
        return CODE_EXTENSIONS.includes(ext);
    });

    if (uploadedFiles.length === 0) {
        addBotMessage('❌ No code files found in the selected folder. Please upload a folder containing code files.');
        return;
    }

    addBotMessage(`📁 Found ${uploadedFiles.length} code files. Starting analysis...`);
    
    // Start analysis
    await analyzeUploadedCode();
}

/**
 * Analyze uploaded code files
 */
async function analyzeUploadedCode() {
    analysisInProgress = true;
    
    try {
        // Show progress
        addBotMessage('🔍 Scanning files and analyzing code structure...');

        // Process files and extract information
        const analysis = await processFiles(uploadedFiles);

        // Send to backend for detailed analysis
        addBotMessage('🤖 Generating detailed report with AI insights...');
        
        const response = await fetch('/analyze-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(analysis)
        });

        if (!response.ok) {
            throw new Error('Analysis failed');
        }

        const result = await response.json();
        
        // Display report in chat
        displayAnalysisReport(result);
        
        // Ask if user wants PDF
        setTimeout(() => {
            addBotMessage('📄 Would you like to download this report as PDF? (Type "yes" or "download pdf")');
            // Store report ID for PDF download
            window.currentReportId = result.reportId;
        }, 1000);

    } catch (error) {
        console.error('Analysis error:', error);
        addBotMessage('❌ Analysis failed: ' + error.message);
    } finally {
        analysisInProgress = false;
        // Reset file input
        document.getElementById('folderInput').value = '';
    }
}

/**
 * Process uploaded files and extract analysis data
 */
async function processFiles(files) {
    const analysis = {
        projectName: extractProjectName(files),
        totalFiles: files.length,
        files: [],
        languages: {},
        directories: {},
        filesSummary: []
    };

    for (const file of files) {
        const ext = getFileExtension(file.name);
        const lang = mapExtensionToLanguage(ext);
        const relativePath = file.webkitRelativePath || file.name;
        const dir = getDirectoryName(relativePath);

        // Count languages
        analysis.languages[lang] = (analysis.languages[lang] || 0) + 1;

        // Count directories
        analysis.directories[dir] = (analysis.directories[dir] || 0) + 1;

        // Read file content for dependency detection
        const content = await readFileContent(file);
        
        analysis.filesSummary.push({
            path: relativePath,
            name: file.name,
            size: file.size,
            language: lang,
            extension: ext,
            hasContent: content.length > 0
        });

        // Detect dependencies from specific files
        if (file.name === 'package.json' || 
            file.name === 'requirements.txt' || 
            file.name === 'pom.xml' ||
            file.name === 'go.mod' ||
            file.name === 'Gemfile') {
            analysis[file.name] = content;
        }
    }

    return analysis;
}

/**
 * Read file content
 */
function readFileContent(file) {
    return new Promise((resolve, reject) => {
        // Only read text files under 1MB
        if (file.size > 1024 * 1024) {
            resolve(''); // Skip large files
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = () => resolve('');
        reader.readAsText(file);
    });
}

/**
 * Display analysis report in chat
 */
function displayAnalysisReport(report) {
    let message = `
📊 <strong>Code Analysis Report</strong>
━━━━━━━━━━━━━━━━━━━━━━━━

<strong>📁 Project:</strong> ${report.projectName}
<strong>📝 Total Files:</strong> ${report.totalFiles}
<strong>💻 Languages:</strong> ${report.languageCount}
<strong>📦 Dependencies:</strong> ${report.totalDependencies}

<strong>🔍 Language Breakdown:</strong>
${formatLanguages(report.languages)}

<strong>📂 Top Directories:</strong>
${formatDirectories(report.topDirectories)}

<strong>⚠️ Issues Found:</strong>
${report.issues.length > 0 ? report.issues.map(i => `  • ${i}`).join('\n') : '  ✓ No major issues detected'}

<strong>✅ Recommendations:</strong>
${report.recommendations.map(r => `  • ${r}`).join('\n')}

<strong>📈 Code Quality Score:</strong> ${report.qualityScore}/100

━━━━━━━━━━━━━━━━━━━━━━━━
<em>Report generated at ${new Date().toLocaleString()}</em>
    `.trim();

    addBotMessage(message);
}

/**
 * Format languages for display
 */
function formatLanguages(languages) {
    return Object.entries(languages)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([lang, count]) => `  • ${lang}: ${count} files`)
        .join('\n');
}

/**
 * Format directories for display
 */
function formatDirectories(directories) {
    return directories
        .slice(0, 5)
        .map(d => `  • ${d.name}: ${d.count} files`)
        .join('\n');
}

/**
 * Utility functions
 */
function getFileExtension(filename) {
    const match = filename.match(/\.[^.]+$/);
    return match ? match[0].toLowerCase() : '';
}

function mapExtensionToLanguage(ext) {
    const map = {
        '.js': 'JavaScript', '.jsx': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript',
        '.py': 'Python', '.pyw': 'Python',
        '.java': 'Java',
        '.cpp': 'C++', '.cc': 'C++', '.c': 'C', '.h': 'C/C++', '.hpp': 'C++',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin', '.kts': 'Kotlin',
        '.scala': 'Scala',
        '.html': 'HTML', '.htm': 'HTML',
        '.css': 'CSS', '.scss': 'SCSS', '.sass': 'Sass', '.less': 'Less',
        '.json': 'JSON',
        '.xml': 'XML',
        '.yaml': 'YAML', '.yml': 'YAML',
        '.md': 'Markdown',
        '.txt': 'Text',
        '.sh': 'Shell', '.bash': 'Bash', '.bat': 'Batch', '.ps1': 'PowerShell',
        '.sql': 'SQL',
        '.r': 'R',
        '.dart': 'Dart',
        '.lua': 'Lua',
        '.vue': 'Vue'
    };
    return map[ext] || 'Other';
}

function getDirectoryName(path) {
    const parts = path.split('/');
    return parts.length > 1 ? parts[0] : '.';
}

function extractProjectName(files) {
    if (files.length > 0 && files[0].webkitRelativePath) {
        return files[0].webkitRelativePath.split('/')[0];
    }
    return 'Uploaded Project';
}

/**
 * Add bot message to chat
 */
function addBotMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.innerHTML = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    chatMessages.classList.add('active');
}

/**
 * Handle PDF download request
 */
window.handlePDFDownload = function() {
    if (window.currentReportId) {
        addBotMessage('📥 Generating PDF report...');
        
        // Trigger PDF download
        const link = document.createElement('a');
        link.href = `/download-report/${window.currentReportId}`;
        link.download = `code-analysis-${window.currentReportId}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        setTimeout(() => {
            addBotMessage('✅ PDF report downloaded successfully!');
        }, 1000);
        
        window.currentReportId = null;
    }
};

// Intercept chat messages for PDF download request
const originalSendMessage = window.sendMessage;
if (typeof originalSendMessage === 'function') {
    window.sendMessage = function() {
        const userInput = document.getElementById('userInput');
        const message = userInput.value.trim().toLowerCase();
        
        // Check if user wants to download PDF
        if ((message === 'yes' || message.includes('download') || message.includes('pdf')) && window.currentReportId) {
            userInput.value = '';
            addUserMessage(message);
            handlePDFDownload();
            return;
        }
        
        // Otherwise, proceed with normal chat
        originalSendMessage();
    };
}

function addUserMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
