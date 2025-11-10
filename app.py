from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from chatbot import chat
from search_rag import search_chat
from deepseek_chat import chat_with_deepseek
from github_api import analyze_github_repo, format_github_analysis
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
    """Handle chat requests with DeepSeek AI and report context"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        chat_id = data.get('chat_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        print(f"[CHAT] User asked: {user_message}")
        
        # Get conversation history for context
        conversation_history = []
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sender, message FROM messages 
                WHERE chat_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 8
            ''', (chat_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to DeepSeek format (reverse order for chronological)
            for sender, message in reversed(rows):
                role = "user" if sender == "user" else "assistant"
                conversation_history.append({"role": role, "content": message})
        except:
            pass  # Continue without history if DB fails
        
        # Get recent report context if available
        report_context = None
        if hasattr(app, 'reports') and app.reports:
            # Get the most recent report
            latest_report_id = list(app.reports.keys())[-1]
            report_context = app.reports[latest_report_id]
            print(f"[📊 REPORT] Using uploaded code context: {report_context.get('projectName', 'Unknown')}")
        
        # Smart routing: Determine which API(s) to use
        message_lower = user_message.lower()
        
        # Check if question is about code/report analysis (prioritize user's own code)
        code_keywords = ['report', 'analysis', 'my code', 'my project', 'my file', 'health score', 'complexity', 
                        'summary', 'explain', 'improve', 'fix', 'test', 'coverage', 'issue', 'recommendation',
                        'how many', 'what language', 'dependencies', 'quality']
        is_code_question = any(keyword in message_lower for keyword in code_keywords)
        
        # Check if it's a tech/programming question (should use DeepSeek, NOT search)
        tech_keywords = ['ai', 'artificial intelligence', 'machine learning', 'programming', 'python', 'javascript', 
                        'code', 'software', 'algorithm', 'data structure', 'api', 'framework', 'library',
                        'what is ai', 'what is ml', 'what is python', 'explain ai']
        is_tech_question = any(keyword in message_lower for keyword in tech_keywords)
        
        # Check if question needs internet search (ONLY for non-tech general knowledge, current events)
        # Exclude tech questions from search
        search_keywords = ['latest news', 'today news', 'current events', 'trending news', 
                          'who is', 'when did', 'where is', 'what happened']
        needs_search = any(keyword in message_lower for keyword in search_keywords) and not is_tech_question
        
        # Check if explicitly asking about GitHub repo (must have URL or clear repo reference)
        github_keywords = ['github.com', 'repository', 'repo']
        has_github_url = 'github.com' in user_message or '/' in user_message
        needs_github = any(keyword in message_lower for keyword in github_keywords) and has_github_url
        
        # Extract GitHub URL if present in message
        github_context = None
        if needs_github and ('github.com' in user_message or '/' in user_message):
            # Try to extract GitHub URL or owner/repo
            import re
            github_pattern = r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)|([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)'
            match = re.search(github_pattern, user_message)
            if match:
                repo_identifier = match.group(1) or match.group(2)
                print(f"[🐙 GITHUB] Fetching data for: {repo_identifier}")
                github_analysis = analyze_github_repo(repo_identifier)
                if github_analysis:
                    github_context = format_github_analysis(github_analysis)
        
        # Get AI response based on question type
        # PRIORITY 1: User's uploaded code (if they have report context and asking code questions)
        if report_context and is_code_question and not needs_github:
            # User asking about THEIR code - use report context
            print("[🧠 AI + 📊 REPORT] Using DeepSeek AI with YOUR uploaded code context...")
            bot_response = chat_with_deepseek(user_message, conversation_history, report_context)
        
        # PRIORITY 2: General knowledge search (not code-related)
        elif needs_search and not is_code_question:
            # General knowledge - use DuckDuckGo
            print("[🔍 INTERNET] Using DuckDuckGo for general knowledge...")
            bot_response = search_chat(user_message)
        
        # PRIORITY 3: GitHub repository analysis (explicit GitHub URL provided)
        elif needs_github and github_context:
            # GitHub-specific query with data - use DeepSeek + GitHub context
            print("[🐙 GITHUB + AI] Using GitHub API + DeepSeek...")
            enhanced_message = f"{user_message}\n\n{github_context}"
            bot_response = chat_with_deepseek(enhanced_message, conversation_history, report_context)
        
        # PRIORITY 4: GitHub query without URL - ask for clarification
        elif needs_github and not github_context:
            # GitHub query but no URL found
            if report_context:
                # User has uploaded code - maybe they want info about THEIR code?
                print("[🧠 AI + 📊] User mentioned GitHub but has uploaded code - using their report...")
                clarification = f"\n\n💡 *Note: I see you mentioned GitHub, but you have code uploaded. I'll tell you about YOUR project. If you want to analyze a GitHub repository, please provide the URL like: `https://github.com/owner/repo`*"
                bot_response = chat_with_deepseek(user_message, conversation_history, report_context) + clarification
            else:
                # No uploaded code - need GitHub URL
                print("[🐙 GITHUB] GitHub query detected but no repo URL...")
                bot_response = "I can help analyze GitHub repositories! 🐙\n\nPlease provide a GitHub repository URL or use the format `owner/repo`.\n\nExample:\n- `analyze https://github.com/pallets/flask`\n- `tell me about microsoft/vscode`"
        
        # PRIORITY 5: Default - general chat with DeepSeek (use report context if available)
        else:
            # Code analysis or general chat - use DeepSeek AI
            if report_context:
                print("[🧠 AI + 📊 REPORT] Using DeepSeek AI with YOUR code context...")
            else:
                print("[🧠 AI] Using DeepSeek AI...")
            bot_response = chat_with_deepseek(user_message, conversation_history, report_context)
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        })
    
    except Exception as e:
        print(f"[ERROR] Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': "Oops! I had a hiccup. Can you try asking again? 😅",
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
        
        print(f"[✅ REPORT SAVED] AI will now remember this code: {project_name} ({total_files} files)")
        
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
            'aiContextSaved': True,  # Signal to frontend that AI has the context
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
    """Generate and download next-level AI Code Intelligence Report PDF"""
    try:
        from flask import send_file
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.graphics.shapes import Drawing, Rect, String
        from reportlab.graphics.charts.piecharts import Pie
        from reportlab.graphics.charts.barcharts import VerticalBarChart
        from reportlab.graphics import renderPDF
        import io
        
        # Get report from app storage
        if not hasattr(app, 'reports') or report_id not in app.reports:
            return jsonify({'error': 'Report not found'}), 404
        
        report = app.reports[report_id]
        
        # Create PDF in memory with A4 size
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=40, leftMargin=40,
                              topMargin=40, bottomMargin=40)
        story = []
        
        # Custom styles with modern fonts and colors
        styles = getSampleStyleSheet()
        
        # Title Page Style - Futuristic gradient-like effect
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=32,
            textColor=colors.HexColor('#6366f1'),  # Indigo
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=38
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#818cf8'),  # Light indigo
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        heading_style = ParagraphStyle(
            'ModernHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#4f46e5'),  # Deep indigo
            spaceAfter=18,
            spaceBefore=24,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#818cf8'),
            borderWidth=0,
            borderPadding=0,
            leftIndent=0,
            leading=20
        )
        
        body_style = ParagraphStyle(
            'ModernBody',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1e293b'),  # Dark slate
            spaceAfter=10,
            spaceBefore=2,
            leading=14,
            fontName='Helvetica'
        )
        
        # ============================================================
        # TITLE PAGE - Beautiful gradient-inspired design
        # ============================================================
        
        story.append(Spacer(1, 1.2*inch))
        
        # Main Title with emoji-like icons
        story.append(Paragraph(
            "🤖 AI CODEBASE<br/>INTELLIGENCE REPORT",
            title_style
        ))
        
        story.append(Spacer(1, 0.4*inch))
        
        # Project name in elegant box
        project_box_data = [[Paragraph(f"<b>{report['projectName']}</b>", subtitle_style)]]
        project_box = Table(project_box_data, colWidths=[5*inch])
        project_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
            ('BORDER', (0, 0), (-1, -1), 2, colors.HexColor('#6366f1')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('ROUNDEDCORNERS', [10, 10, 10, 10]),
        ]))
        story.append(project_box)
        
        story.append(Spacer(1, 0.6*inch))
        
        # Metadata in clean format
        from datetime import datetime
        gen_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        metadata = [
            ["📅 Generated:", gen_time],
            ["🔑 Analysis ID:", f"#{report_id[:8].upper()}"],
            ["📊 Report Version:", "AI Code Analyzer v2.0"]
        ]
        
        meta_table = Table(metadata, colWidths=[1.5*inch, 3.5*inch])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1e293b')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(meta_table)
        
        story.append(Spacer(1, 1*inch))
        
        # Health Score - Big dopamine hit!
        health_score = report['qualityScore']
        health_emoji = "🟢" if health_score >= 80 else "🟡" if health_score >= 60 else "🟠" if health_score >= 40 else "🔴"
        health_text = "Excellent" if health_score >= 80 else "Good" if health_score >= 60 else "Fair" if health_score >= 40 else "Needs Attention"
        
        story.append(Paragraph(
            f"{health_emoji} <b>CODEBASE HEALTH SCORE</b>",
            heading_style
        ))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Score box with clean design
        score_style = ParagraphStyle(
            'ScoreStyle',
            parent=styles['Normal'],
            fontSize=48,
            textColor=colors.HexColor('#6366f1'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=58
        )
        
        score_data = [[Paragraph(f"<b>{health_score}/100</b>", score_style)]]
        score_table = Table(score_data, colWidths=[5*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdf4') if health_score >= 70 else colors.HexColor('#fef3c7')),
            ('BORDER', (0, 0), (-1, -1), 3, colors.HexColor('#22c55e') if health_score >= 70 else colors.HexColor('#f59e0b')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 30),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 30),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        story.append(score_table)
        
        story.append(Spacer(1, 0.35*inch))
        
        # Status text with proper spacing - no background
        status_style = ParagraphStyle(
            'StatusText',
            parent=styles['Normal'],
            fontSize=13,
            textColor=colors.HexColor('#475569'),
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=18
        )
        
        story.append(Paragraph(
            f"<i>Status: <b>{health_text}</b></i>",
            status_style
        ))
        story.append(Paragraph(
            f"<i>Stable and {('Maintainable' if health_score >= 70 else 'Improvable')}</i>",
            status_style
        ))
        
        story.append(PageBreak())
        
        # ============================================================
        # EXECUTIVE SUMMARY
        # ============================================================
        
        story.append(Paragraph("📋 EXECUTIVE SUMMARY", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        summary_data = [
            ["📁 Total Files", str(report['totalFiles'])],
            ["💻 Languages Detected", str(report['languageCount'])],
            ["📦 Dependencies", str(report['totalDependencies'])],
            ["🧪 Test Coverage", f"{report.get('testCoverage', 0):.1f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.8*inch, 2.2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#faf5ff')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e7ff')),
            ('TOPPADDING', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(summary_table)
        
        story.append(Spacer(1, 0.5*inch))
        
        # ============================================================
        # LANGUAGE BREAKDOWN with PIE CHART
        # ============================================================
        
        story.append(Paragraph("💻 LANGUAGE DISTRIBUTION", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Create pie chart with better spacing
        if report['languages']:
            drawing = Drawing(450, 250)
            pie = Pie()
            pie.x = 100
            pie.y = 30
            pie.width = 150
            pie.height = 150
            
            # Prepare data
            lang_items = sorted(report['languages'].items(), key=lambda x: x[1], reverse=True)[:6]
            pie.data = [count for _, count in lang_items]
            pie.labels = []  # Remove labels from pie to avoid overlap
            
            # Beautiful color palette
            pie.slices.strokeWidth = 1
            pie.slices.strokeColor = colors.white
            color_palette = [
                colors.HexColor('#6366f1'), colors.HexColor('#8b5cf6'),
                colors.HexColor('#ec4899'), colors.HexColor('#f59e0b'),
                colors.HexColor('#10b981'), colors.HexColor('#3b82f6'),
            ]
            for i, color in enumerate(color_palette[:len(pie.data)]):
                pie.slices[i].fillColor = color
            
            # Add legend with proper spacing
            from reportlab.graphics.charts.legends import Legend
            legend = Legend()
            legend.x = 280
            legend.y = 100
            legend.dx = 8
            legend.dy = 8
            legend.fontName = 'Helvetica'
            legend.fontSize = 10
            legend.columnMaximum = 6
            legend.alignment = 'right'
            legend.colorNamePairs = [(color_palette[i], lang_items[i][0]) for i in range(len(lang_items))]
            
            drawing.add(pie)
            drawing.add(legend)
            story.append(drawing)
        
        story.append(Spacer(1, 0.4*inch))
        
        # Language table with percentages
        total_files = report['totalFiles']
        lang_table_data = [['Language', 'Files', 'Percentage']]
        for lang, count in sorted(report['languages'].items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / total_files * 100) if total_files > 0 else 0
            lang_table_data.append([lang, str(count), f"{percentage:.1f}%"])
        
        lang_table = Table(lang_table_data, colWidths=[2.2*inch, 1.4*inch, 1.4*inch])
        lang_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
        ]))
        story.append(lang_table)
        
        story.append(PageBreak())
        
        # ============================================================
        # TOP DIRECTORIES BAR CHART
        # ============================================================
        
        if report.get('topDirectories'):
            story.append(Paragraph("📂 TOP DIRECTORIES BY FILE COUNT", heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            top_dirs = report['topDirectories'][:8]
            dir_data = [['Directory', 'Files']]
            for d in top_dirs:
                dir_data.append([d['name'][:30], str(d['count'])])
            
            dir_table = Table(dir_data, colWidths=[3.5*inch, 1.5*inch])
            dir_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd6fe')),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f3ff')]),
            ]))
            story.append(dir_table)
            story.append(Spacer(1, 0.4*inch))
        
        # ============================================================
        # QUALITY METRICS DASHBOARD
        # ============================================================
        
        story.append(Paragraph("📊 QUALITY METRICS DASHBOARD", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        test_coverage = report.get('testCoverage', 0)
        test_emoji = "✅" if test_coverage >= 70 else "⚠️" if test_coverage >= 40 else "❌"
        
        quality_metrics = [
            [f"🧪 Test Coverage", f"{test_emoji} {test_coverage:.1f}%"],
            ["📄 Documentation", "✅ README Present" if report['qualityScore'] >= 70 else "⚠️ Needs Improvement"],
            ["📦 Dependencies", f"{'✅' if report['totalDependencies'] < 50 else '⚠️'} {report['totalDependencies']} packages"],
            ["⚙️ Code Quality", f"{'🟢' if health_score >= 80 else '🟡' if health_score >= 60 else '🟠'} {health_text}"],
        ]
        
        quality_table = Table(quality_metrics, colWidths=[2.8*inch, 2.2*inch])
        quality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdf4')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bbf7d0')),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(quality_table)
        
        story.append(Spacer(1, 0.5*inch))
        
        # ============================================================
        # WARNINGS & ISSUES - Red bordered boxes
        # ============================================================
        
        if report.get('issues'):
            story.append(Paragraph("⚠️ DETECTED ISSUES & WARNINGS", heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            for issue in report['issues']:
                issue_data = [[Paragraph(f"⚠️ {issue}", body_style)]]
                issue_box = Table(issue_data, colWidths=[5*inch])
                issue_box.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef2f2')),
                    ('BORDER', (0, 0), (-1, -1), 2, colors.HexColor('#ef4444')),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 12),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ]))
                story.append(issue_box)
                story.append(Spacer(1, 0.15*inch))
        
        story.append(PageBreak())
        
        # ============================================================
        # AI RECOMMENDATIONS - Friendly and human-like
        # ============================================================
        
        story.append(Paragraph("🤖 AI-POWERED RECOMMENDATIONS", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Conversational intro
        intro_text = f"Based on my analysis of <b>{report['projectName']}</b>, I've identified key areas where your codebase can improve. Here's my personalized advice:"
        story.append(Paragraph(intro_text, body_style))
        story.append(Spacer(1, 0.2*inch))
        
        for i, rec in enumerate(report.get('recommendations', []), 1):
            rec_data = [[Paragraph(f"<b>{i}.</b> {rec}", body_style)]]
            rec_box = Table(rec_data, colWidths=[5*inch])
            rec_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
                ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor('#3b82f6')),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ]))
            story.append(rec_box)
            story.append(Spacer(1, 0.15*inch))
        
        story.append(Spacer(1, 0.3*inch))
        
        # ============================================================
        # CONFIDENCE & SATISFACTION METER
        # ============================================================
        
        story.append(Paragraph("✨ OVERALL ASSESSMENT", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        confidence_text = f"Your codebase demonstrates <b>{health_text.lower()}</b> practices with a health score of <b>{health_score}/100</b>. "
        
        if health_score >= 80:
            confidence_text += "This is an excellent foundation! Your code is well-structured and maintainable. Keep up the great work! 🎉"
        elif health_score >= 60:
            confidence_text += "You're on the right track! Focus on the recommendations above to reach excellence. 🚀"
        else:
            confidence_text += "There's room for improvement. Follow the AI recommendations to strengthen your codebase. 💪"
        
        story.append(Paragraph(confidence_text, body_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Visual confidence bar
        confidence_bar_data = [["AI CONFIDENCE LEVEL", f"{health_score}% Confident"]]
        confidence_bar = Table(confidence_bar_data, colWidths=[2.5*inch, 2.5*inch])
        confidence_bar.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#6366f1')),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#22c55e') if health_score >= 70 else colors.HexColor('#f59e0b')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(confidence_bar)
        
        story.append(Spacer(1, 1*inch))
        
        # ============================================================
        # FOOTER - Professional and clean
        # ============================================================
        
        footer_text = f"<i>Generated by AI Code Analyzer v2.0 | {gen_time} | Analysis ID: #{report_id[:8].upper()}</i>"
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER
        )
        story.append(Paragraph(footer_text, footer_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'AI-Code-Intelligence-{report["projectName"]}.pdf',
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
    # Get port from environment variable (Render sets PORT automatically)
    port = int(os.getenv('PORT', 5000))
    # Check if running in production
    is_production = os.getenv('RENDER', False)
    
    if not is_production:
        print("="*60)
        print("Starting AI Chat & Repository Explorer Server...")
        print("✓ Internet Search AI (DuckDuckGo)")
        print("✓ GitHub Repository Analysis")
        print("✓ AI-Powered Code Insights")
        print("="*60)
        print("\nOpen http://localhost:5000 in your browser")
        print(f"Node.js backend: {NODE_BACKEND_URL}\n")
    
    # Use debug mode only in development
    app.run(debug=not is_production, host='0.0.0.0', port=port)
