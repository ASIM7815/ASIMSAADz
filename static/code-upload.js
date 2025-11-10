// Code Upload and Analysis JavaScript
// Handles local folder upload and code analysis

// Allowed code file extensions - comprehensive list
const CODE_EXTENSIONS = [
    // JavaScript/TypeScript
    '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
    
    // Python
    '.py', '.pyw', '.pyx', '.pyi',
    
    // Java/JVM
    '.java', '.class', '.jar', '.gradle', '.kt', '.kts', '.scala', '.groovy',
    
    // C/C++
    '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx', '.hh',
    
    // C#/.NET
    '.cs', '.vb', '.fs', '.fsx',
    
    // Go
    '.go', '.mod', '.sum',
    
    // Rust
    '.rs', '.toml',
    
    // Ruby
    '.rb', '.rake', '.gemspec',
    
    // PHP
    '.php', '.phtml', '.php3', '.php4', '.php5', '.phps',
    
    // Swift/Objective-C
    '.swift', '.m', '.mm',
    
    // Web Development
    '.html', '.htm', '.xhtml', '.shtml',
    '.css', '.scss', '.sass', '.less', '.styl',
    '.vue', '.svelte',
    
    // Configuration & Data
    '.json', '.json5', '.jsonc',
    '.xml', '.xaml', '.xsd', '.xsl', '.xslt',
    '.yaml', '.yml',
    '.toml', '.ini', '.cfg', '.conf',
    '.env', '.properties',
    
    // Documentation
    '.md', '.markdown', '.rst', '.txt', '.text',
    '.adoc', '.asciidoc',
    
    // Shell/Scripts
    '.sh', '.bash', '.zsh', '.fish',
    '.bat', '.cmd', '.ps1', '.psm1',
    
    // Database
    '.sql', '.mysql', '.pgsql', '.sqlite',
    
    // Other Languages
    '.r', '.R', '.rmd',                    // R
    '.dart',                               // Dart
    '.lua',                                // Lua
    '.pl', '.pm', '.t',                    // Perl
    '.ex', '.exs', '.eex',                 // Elixir
    '.erl', '.hrl',                        // Erlang
    '.clj', '.cljs', '.cljc', '.edn',     // Clojure
    '.lisp', '.lsp', '.cl',               // Lisp
    '.hs', '.lhs',                         // Haskell
    '.ml', '.mli',                         // OCaml
    '.nim',                                // Nim
    '.cr',                                 // Crystal
    '.v', '.vh', '.sv', '.svh',           // Verilog/SystemVerilog
    '.vhd', '.vhdl',                       // VHDL
    '.asm', '.s',                          // Assembly
    '.f', '.f90', '.f95', '.for',         // Fortran
    '.pas', '.pp',                         // Pascal
    '.d',                                  // D
    '.jl',                                 // Julia
    '.sol',                                // Solidity
    '.proto',                              // Protocol Buffers
    '.graphql', '.gql',                    // GraphQL
    '.tf', '.tfvars',                      // Terraform
    
    // Build & Config Files
    '.dockerfile', '.dockerignore',
    '.makefile', '.mk',
    '.cmake',
    '.gradle',
    '.maven',
    '.npmrc', '.yarnrc',
    '.eslintrc', '.prettierrc',
    '.babelrc',
    '.gitignore', '.gitattributes',
    
    // Misc
    '.tex',                                // LaTeX
    '.bib',                                // BibTeX
    '.log'                                 // Logs
];

// Blocked extensions (media files, executables, archives)
const BLOCKED_EXTENSIONS = [
    // Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp', '.tiff', '.psd', '.raw',
    
    // Videos
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.mpeg', '.mpg', '.3gp',
    
    // Audio
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus',
    
    // Archives
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso',
    
    // Executables
    '.exe', '.dll', '.so', '.dylib', '.bin', '.app', '.dmg', '.msi',
    
    // Documents (non-code)
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
    
    // Fonts
    '.ttf', '.otf', '.woff', '.woff2', '.eot'
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

    // Filter files - allow code files, block media/executables
    uploadedFiles = files.filter(file => {
        const ext = getFileExtension(file.name).toLowerCase();
        
        // Block media and executable files explicitly
        if (BLOCKED_EXTENSIONS.includes(ext)) {
            return false;
        }
        
        // Allow code files
        if (CODE_EXTENSIONS.includes(ext)) {
            return true;
        }
        
        // Allow files without extension (like Makefile, Dockerfile)
        if (ext === '' && !file.name.includes('.')) {
            return true;
        }
        
        return false;
    });

    const blockedCount = files.length - uploadedFiles.length;

    if (uploadedFiles.length === 0) {
        addBotMessage('❌ No code files found in the selected folder. Please upload a folder containing programming files.');
        if (blockedCount > 0) {
            addBotMessage(`ℹ️ ${blockedCount} non-code files were filtered out (images, videos, executables, etc.)`);
        }
        return;
    }

    addBotMessage(`📁 Found ${uploadedFiles.length} code files. Starting analysis...`);
    
    if (blockedCount > 0) {
        addBotMessage(`ℹ️ Filtered out ${blockedCount} non-code files (images, videos, etc.)`);
    }
    
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
        // JavaScript/TypeScript
        '.js': 'JavaScript', '.jsx': 'JavaScript', '.mjs': 'JavaScript', '.cjs': 'JavaScript',
        '.ts': 'TypeScript', '.tsx': 'TypeScript',
        
        // Python
        '.py': 'Python', '.pyw': 'Python', '.pyx': 'Python', '.pyi': 'Python',
        
        // Java/JVM
        '.java': 'Java', '.class': 'Java', '.jar': 'Java',
        '.kt': 'Kotlin', '.kts': 'Kotlin',
        '.scala': 'Scala',
        '.groovy': 'Groovy', '.gradle': 'Gradle',
        
        // C/C++
        '.c': 'C', '.h': 'C/C++',
        '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++', '.hpp': 'C++', '.hxx': 'C++',
        
        // C#/.NET
        '.cs': 'C#', '.vb': 'Visual Basic', '.fs': 'F#',
        
        // Go
        '.go': 'Go', '.mod': 'Go Module', '.sum': 'Go',
        
        // Rust
        '.rs': 'Rust', '.toml': 'TOML',
        
        // Ruby
        '.rb': 'Ruby', '.rake': 'Ruby', '.gemspec': 'Ruby',
        
        // PHP
        '.php': 'PHP', '.phtml': 'PHP',
        
        // Swift/Objective-C
        '.swift': 'Swift', '.m': 'Objective-C', '.mm': 'Objective-C++',
        
        // Web
        '.html': 'HTML', '.htm': 'HTML', '.xhtml': 'XHTML',
        '.css': 'CSS', '.scss': 'SCSS', '.sass': 'Sass', '.less': 'Less',
        '.vue': 'Vue', '.svelte': 'Svelte',
        
        // Config & Data
        '.json': 'JSON', '.json5': 'JSON5', '.jsonc': 'JSON',
        '.xml': 'XML', '.xaml': 'XAML',
        '.yaml': 'YAML', '.yml': 'YAML',
        '.ini': 'INI', '.cfg': 'Config', '.conf': 'Config',
        '.env': 'Environment',
        
        // Documentation
        '.md': 'Markdown', '.markdown': 'Markdown',
        '.rst': 'reStructuredText', '.txt': 'Text',
        
        // Shell/Scripts
        '.sh': 'Shell', '.bash': 'Bash', '.zsh': 'Zsh',
        '.bat': 'Batch', '.cmd': 'Batch', '.ps1': 'PowerShell',
        
        // Database
        '.sql': 'SQL', '.mysql': 'MySQL', '.pgsql': 'PostgreSQL',
        
        // Other Languages
        '.r': 'R', '.R': 'R',
        '.dart': 'Dart',
        '.lua': 'Lua',
        '.pl': 'Perl', '.pm': 'Perl',
        '.ex': 'Elixir', '.exs': 'Elixir',
        '.erl': 'Erlang',
        '.clj': 'Clojure', '.cljs': 'ClojureScript',
        '.lisp': 'Lisp', '.cl': 'Common Lisp',
        '.hs': 'Haskell',
        '.ml': 'OCaml',
        '.nim': 'Nim',
        '.cr': 'Crystal',
        '.v': 'Verilog', '.sv': 'SystemVerilog',
        '.vhd': 'VHDL', '.vhdl': 'VHDL',
        '.asm': 'Assembly', '.s': 'Assembly',
        '.f': 'Fortran', '.f90': 'Fortran',
        '.pas': 'Pascal',
        '.d': 'D',
        '.jl': 'Julia',
        '.sol': 'Solidity',
        '.proto': 'Protocol Buffers',
        '.graphql': 'GraphQL', '.gql': 'GraphQL',
        '.tf': 'Terraform', '.tfvars': 'Terraform',
        '.dockerfile': 'Docker',
        '.makefile': 'Makefile', '.mk': 'Makefile',
        '.cmake': 'CMake',
        '.tex': 'LaTeX'
    };
    return map[ext.toLowerCase()] || 'Other';
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
