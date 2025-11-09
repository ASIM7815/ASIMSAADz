from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from chatbot import chat
from search_rag import search_chat
import sqlite3
from datetime import datetime
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
CORS(app)  # Enable CORS for frontend-backend communication

# Node.js backend URL for GitHub analysis
NODE_BACKEND_URL = os.getenv('NODE_BACKEND_URL', 'http://localhost:3001')

# Database initialization
def init_db():
    """Initialize SQLite database with messages table"""
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully")

# Initialize database on startup
init_db()

@app.route('/')
def home():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/messages', methods=['GET'])
def get_messages():
    """Get all messages for a specific chat_id"""
    try:
        chat_id = request.args.get('chat_id')
        
        if not chat_id:
            return jsonify({'error': 'No chat_id provided'}), 400
        
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, chat_id, sender, message, timestamp 
            FROM messages 
            WHERE chat_id = ? 
            ORDER BY timestamp ASC
        ''', (chat_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'chat_id': row[1],
                'sender': row[2],
                'message': row[3],
                'timestamp': row[4]
            })
        
        conn.close()
        return jsonify({'messages': messages, 'status': 'success'})
    
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/message', methods=['POST'])
def save_message():
    """Save a message to the database"""
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        sender = data.get('sender')
        message = data.get('message')
        
        if not all([chat_id, sender, message]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (chat_id, sender, message) 
            VALUES (?, ?, ?)
        ''', (chat_id, sender, message))
        conn.commit()
        
        message_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'id': message_id,
            'status': 'success',
            'message': 'Message saved successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete all messages for a specific chat_id"""
    try:
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM messages WHERE chat_id = ?', (chat_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'Deleted {deleted_count} messages',
            'deleted_count': deleted_count
        })
    
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/chats', methods=['DELETE'])
def delete_all_chats():
    """Delete all messages from all chats"""
    try:
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM messages')
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'Deleted all {deleted_count} messages',
            'deleted_count': deleted_count
        })
    
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Handle chat requests from frontend"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get response from internet search
        bot_response = search_chat(user_message)
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/analyze-code', methods=['POST'])
def analyze_code():
    """Analyze uploaded code files"""
    try:
        data = request.get_json()
        
        # Extract analysis data
        project_name = data.get('projectName', 'Untitled Project')
        total_files = data.get('totalFiles', 0)
        languages = data.get('languages', {})
        directories = data.get('directories', {})
        files_summary = data.get('filesSummary', [])
        
        # Parse dependencies
        dependencies = {
            'npm': {},
            'pip': {},
            'maven': [],
            'golang': {},
            'ruby': {}
        }
        
        # Parse package.json if present
        if 'package.json' in data:
            try:
                import json
                pkg = json.loads(data['package.json'])
                dependencies['npm'] = {
                    'dependencies': pkg.get('dependencies', {}),
                    'devDependencies': pkg.get('devDependencies', {})
                }
            except:
                pass
        
        # Parse requirements.txt if present
        if 'requirements.txt' in data:
            pip_deps = {}
            for line in data['requirements.txt'].split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('==')
                    if parts:
                        pip_deps[parts[0].strip()] = parts[1].strip() if len(parts) > 1 else 'latest'
            dependencies['pip'] = pip_deps
        
        # Count total dependencies
        total_deps = (
            len(dependencies['npm'].get('dependencies', {})) +
            len(dependencies['npm'].get('devDependencies', {})) +
            len(dependencies['pip'])
        )
        
        # Analyze code quality
        issues = []
        recommendations = []
        quality_score = 100
        
        # Check for issues
        if total_files > 5000:
            issues.append('Very large codebase with ' + str(total_files) + ' files')
            recommendations.append('Consider modularizing into smaller packages')
            quality_score -= 10
        
        # Check for test files
        test_files = sum(1 for f in files_summary if 'test' in f['path'].lower() or 'spec' in f['path'].lower())
        test_coverage = (test_files / total_files * 100) if total_files > 0 else 0
        
        if test_coverage < 10:
            issues.append(f'Low test coverage detected ({test_coverage:.1f}%)')
            recommendations.append('Add more unit and integration tests')
            quality_score -= 15
        
        # Check dependencies
        if len(dependencies['npm'].get('dependencies', {})) > 100:
            issues.append('High number of npm dependencies')
            recommendations.append('Review and remove unused dependencies')
            quality_score -= 10
        
        # Check for documentation
        has_readme = any(f['name'].lower() == 'readme.md' for f in files_summary)
        if not has_readme:
            issues.append('No README.md file found')
            recommendations.append('Add comprehensive project documentation')
            quality_score -= 10
        
        # Add general recommendations
        recommendations.append('Enable code linting (ESLint, Pylint, etc.)')
        recommendations.append('Set up continuous integration (CI/CD)')
        recommendations.append('Use version control (Git) if not already')
        recommendations.append('Add code comments for complex logic')
        
        # Prepare top directories
        top_dirs = sorted(
            [{'name': k, 'count': v} for k, v in directories.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]
        
        # Generate unique report ID
        import uuid
        report_id = str(uuid.uuid4())
        
        # Store report for PDF generation
        report_data = {
            'id': report_id,
            'projectName': project_name,
            'totalFiles': total_files,
            'languages': languages,
            'languageCount': len(languages),
            'topDirectories': top_dirs,
            'totalDependencies': total_deps,
            'dependencies': dependencies,
            'issues': issues,
            'recommendations': recommendations,
            'qualityScore': max(0, quality_score),
            'testCoverage': test_coverage,
            'generatedAt': datetime.now().isoformat()
        }
        
        # Save report to global dict for PDF generation (temporary storage)
        if not hasattr(app, 'reports'):
            app.reports = {}
        app.reports[report_id] = report_data
        
        return jsonify({
            'reportId': report_id,
            'projectName': project_name,
            'totalFiles': total_files,
            'languages': languages,
            'languageCount': len(languages),
            'topDirectories': top_dirs,
            'totalDependencies': total_deps,
            'issues': issues,
            'recommendations': recommendations,
            'qualityScore': max(0, quality_score),
            'status': 'success'
        })
    
    except Exception as e:
        print("Analysis error:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/download-report/<report_id>')
def download_report(report_id):
    """Generate and download PDF report"""
    try:
        from flask import send_file
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch
        import io
        
        # Get report from app storage
        if not hasattr(app, 'reports') or report_id not in app.reports:
            return jsonify({'error': 'Report not found'}), 404
        
        report = app.reports[report_id]
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>Code Analysis Report</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Project info
        story.append(Paragraph(f"<b>Project:</b> {report['projectName']}", styles['Normal']))
        story.append(Paragraph(f"<b>Total Files:</b> {report['totalFiles']}", styles['Normal']))
        story.append(Paragraph(f"<b>Languages:</b> {report['languageCount']}", styles['Normal']))
        story.append(Paragraph(f"<b>Dependencies:</b> {report['totalDependencies']}", styles['Normal']))
        story.append(Paragraph(f"<b>Quality Score:</b> {report['qualityScore']}/100", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Language breakdown
        story.append(Paragraph("<b>Language Breakdown:</b>", styles['Heading2']))
        lang_data = [['Language', 'Files']]
        for lang, count in sorted(report['languages'].items(), key=lambda x: x[1], reverse=True)[:10]:
            lang_data.append([lang, str(count)])
        
        lang_table = Table(lang_data)
        lang_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(lang_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Issues
        if report['issues']:
            story.append(Paragraph("<b>Issues Detected:</b>", styles['Heading2']))
            for issue in report['issues']:
                story.append(Paragraph(f"• {issue}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Recommendations
        story.append(Paragraph("<b>Recommendations:</b>", styles['Heading2']))
        for rec in report['recommendations']:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Paragraph(f"<i>Generated: {report['generatedAt']}</i>", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'code-analysis-{report["projectName"]}.pdf',
            mimetype='application/pdf'
        )
    
    except Exception as e:
        print("PDF generation error:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# GITHUB REPOSITORY ANALYSIS PROXY ENDPOINTS
# ============================================================================

@app.route('/api/github/auth/status', methods=['GET'])
def github_auth_status():
    """Check GitHub authentication status via Node.js backend"""
    try:
        response = requests.get(f'{NODE_BACKEND_URL}/auth/status', timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': 'Backend service unavailable', 'details': str(e)}), 503

@app.route('/api/github/repos', methods=['GET'])
def github_repos():
    """Get user's GitHub repositories"""
    try:
        # Forward cookies/session to maintain authentication
        response = requests.get(
            f'{NODE_BACKEND_URL}/repos',
            cookies=request.cookies,
            timeout=10
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to fetch repositories', 'details': str(e)}), 503

@app.route('/api/github/analyze', methods=['POST'])
def github_analyze():
    """Analyze a GitHub repository"""
    try:
        data = request.get_json()
        response = requests.post(
            f'{NODE_BACKEND_URL}/analyze',
            json=data,
            cookies=request.cookies,
            timeout=120  # Analysis can take time
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': 'Analysis failed', 'details': str(e)}), 503

@app.route('/api/github/reports', methods=['GET'])
def github_reports():
    """Get list of all reports"""
    try:
        response = requests.get(f'{NODE_BACKEND_URL}/reports', timeout=10)
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to fetch reports', 'details': str(e)}), 503

@app.route('/api/github/reports/<report_id>/json', methods=['GET'])
def github_report_json(report_id):
    """Get report as JSON"""
    try:
        response = requests.get(f'{NODE_BACKEND_URL}/reports/{report_id}/json', timeout=10)
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to fetch report', 'details': str(e)}), 503

@app.route('/api/github/qa', methods=['POST'])
def github_qa():
    """Ask questions about a repository analysis"""
    try:
        data = request.get_json()
        response = requests.post(
            f'{NODE_BACKEND_URL}/qa',
            json=data,
            cookies=request.cookies,
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': 'Q&A request failed', 'details': str(e)}), 503

if __name__ == '__main__':
    print("="*60)
    print("Starting AI Chat & Repository Explorer Server...")
    print("✓ Internet Search AI (DuckDuckGo)")
    print("✓ GitHub Repository Analysis")
    print("✓ AI-Powered Code Insights")
    print("="*60)
    print("\nOpen http://localhost:5000 in your browser")
    print(f"Node.js backend: {NODE_BACKEND_URL}\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
