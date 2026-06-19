import os
import json
import logging
from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import requests
from datetime import datetime, timedelta

from config import Config
from database import db, User, Analysis
from youtube_service import get_user_subscriptions, get_user_liked_videos
from analyzer import analyze_activity_data, get_simulated_historical_data, generate_ai_report

# Enable HTTP for OAuth development locally
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
app.config.from_object(Config)

# Enable CORS for frontend requests, adding any environment-configured frontend url
allowed_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
frontend_url = os.environ.get('FRONTEND_URL')
if frontend_url:
    allowed_origins.append(frontend_url.rstrip('/'))

CORS(app, supports_credentials=True, origins=allowed_origins)

# Initialize DB
db.init_app(app)

with app.app_context():
    db.create_all()

# Helper: Get Google OAuth Flow
def get_google_flow():
    client_config = {
        "web": {
            "client_id": app.config['GOOGLE_CLIENT_ID'],
            "project_id": "youtube-personality-analyzer",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
            "redirect_uris": [app.config['GOOGLE_REDIRECT_URI']]
        }
    }
    return Flow.from_client_config(
        client_config,
        scopes=[
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/youtube.readonly',
            'openid'
        ]
    )

# --- Authentication Routes ---

@app.route('/api/auth/status', methods=['GET'])
def get_auth_status():
    """
    Returns if Google OAuth is configured on the backend.
    """
    return jsonify({
        'oauth_configured': Config.is_oauth_configured()
    })

@app.route('/api/auth/login', methods=['GET'])
def login():
    """
    Initiates Google OAuth Flow.
    """
    if not Config.is_oauth_configured():
        return jsonify({
            'error': 'Google OAuth credentials are not configured on this server. Please use Demo Mode.'
        }), 400
        
    flow = get_google_flow()
    flow.redirect_uri = Config.GOOGLE_REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account'
    )
    session['oauth_state'] = state
    return jsonify({'url': authorization_url})

@app.route('/api/auth/callback', methods=['GET'])
def callback():
    """
    Handles Google OAuth redirect callback.
    """
    if not Config.is_oauth_configured():
        frontend_url = os.environ.get('FRONTEND_URL')
        if frontend_url:
            return redirect(f"{frontend_url.rstrip('/')}/?error=not_configured")
        return redirect(f"{request.scheme}://{request.host}/?error=not_configured")
        
    state = session.get('oauth_state')
    
    flow = get_google_flow()
    flow.redirect_uri = Config.GOOGLE_REDIRECT_URI
    flow.fetch_token(authorization_response=request.url)
    
    credentials = flow.credentials
    session['oauth_credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    # Retrieve user info from Google APIs
    user_info_service = build_user_info_service(credentials)
    user_info = user_info_service.get().execute()
    
    google_id = user_info.get('id')
    email = user_info.get('email')
    name = user_info.get('name')
    picture = user_info.get('picture')
    
    # Save or update User in DB
    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture
        )
        db.session.add(user)
    else:
        user.name = name
        user.picture = picture
        user.email = email
        
    db.session.commit()
    session['user_id'] = user.id
    
    # Redirect back to the frontend dashboard
    frontend_url = os.environ.get('FRONTEND_URL')
    if frontend_url:
        return redirect(f"{frontend_url.rstrip('/')}/dashboard")
    return redirect(f"{request.scheme}://{request.host}/dashboard")

def build_user_info_service(credentials):
    from googleapiclient.discovery import build
    return build('oauth2', 'v2', credentials=credentials).userinfo()

@app.route('/api/auth/demo', methods=['POST'])
def login_demo():
    """
    Logs in with a simulated Demo User profile.
    """
    demo_email = "demo.user@personality-analyzer.local"
    user = User.query.filter_by(email=demo_email).first()
    
    if not user:
        user = User(
            google_id="demo-google-id-12345",
            email=demo_email,
            name="Alex Mercer (Demo)",
            picture="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&h=150&q=80"
        )
        db.session.add(user)
        db.session.commit()
        
    session['user_id'] = user.id
    # Store flag in session to identify demo credentials
    session['is_demo'] = True
    
    return jsonify(user.to_dict())

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    """
    Returns current user info.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify(user.to_dict())

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """
    Clears session tokens.
    """
    session.clear()
    return jsonify({'success': True})

# --- YouTube Data & Analysis Routes ---

def get_mock_youtube_data():
    """
    Returns a rich dataset of simulated YouTube subscriptions and liked videos.
    """
    mock_items = []
    
    # Subscriptions (Coding, Self-Improvement, Science, Finance, Gaming)
    subs = [
        ("freeCodeCamp.org", "Learn to code for free. Tutorials on Python, React, JavaScript, SQL, AWS, and Git.", "Education"),
        ("3Blue1Brown", "Visual mathematical explanations. Topics include Calculus, Linear Algebra, Neural Networks.", "Science & Engineering"),
        ("Ali Abdaal", "Productivity tips, study habits, time management, and book reviews.", "Self-Improvement"),
        ("The B1M", "World's best architecture and mega-projects engineering documentary channel.", "Science & Engineering"),
        ("Lofi Girl", "Relaxing music beats for coding, studying, and sleeping.", "Music"),
        ("Fireship", "High-speed coding tutorials, technology updates, and web developer reviews.", "Programming & Technology"),
        ("Lex Fridman Podcast", "Conversations with AI researchers, scientists, tech leaders, and philosophers.", "Education"),
        ("Graham Stephan", "Personal finance, stock market, real estate, and passive income strategies.", "Finance & Business"),
        ("Linus Tech Tips", "Hardware reviews, computer builds, gaming rigs, and tech news.", "Programming & Technology"),
        ("Andrew Huberman (Huberman Lab)", "Neuroscience, focus protocols, sleep habits, and physiological performance.", "Self-Improvement"),
        ("Gamer's Nexus", "Deep-dives into computer hardware, GPUS, thermal testing, and gaming tech.", "Gaming"),
        ("Veritasium", "Engaging videos on physics, quantum mechanics, history of science, and engineering.", "Science & Engineering"),
        ("TED-Ed", "Short animated documentaries explaining riddle math, historical figures, and philosophy.", "Education"),
        ("Warren Buffett Archive", "Interviews and shareholder letters discussing investing strategies, equities, and inflation.", "Finance & Business")
    ]
    
    for title, desc, yt_cat in subs:
        mock_items.append({
            'title': title,
            'description': desc,
            'youtube_category_id': '27' if yt_cat == 'Education' else '28',
            'tags': [yt_cat.lower()],
            'type': 'subscription'
        })
        
    # Liked Videos
    likes = [
        ("Learn Python - Full Course for Beginners [Tutorial]", "Complete Python program course with exercises.", "Programming & Technology", ['python', 'coding']),
        ("Why 60% of Developers Fail Coding Interviews", "How data structures and algorithms trip up tech interviews.", "Programming & Technology", ['coding', 'algorithms']),
        ("Building a Full-Stack React App in 20 Minutes", "Quick setup guide using Vite, Tailwind, and Node backend.", "Programming & Technology", ['react', 'web dev']),
        ("How to Start Investing in 2026 (Step-by-Step)", "Easy ETF, stock market, and index fund portfolio guide.", "Finance & Business", ['investing', 'stocks']),
        ("The Science of Brain Focus & Concentration", "Huberman Lab podcast clip on dopamine and ADHD protocols.", "Self-Improvement", ['focus', 'neuroscience']),
        ("Is This the Fastest AI Coding Assistant Ever?", "Reviewing a new AI text editor designed for developers.", "Programming & Technology", ['ai', 'coding']),
        ("Understanding Quantum Physics in 10 Minutes", "Animated visualization of the double slit experiment.", "Science & Engineering", ['physics', 'quantum']),
        ("How I Read 100 Books a Year (Actionable Rules)", "Time-blocking, audiobooks, and active note-taking.", "Self-Improvement", ['productivity', 'books']),
        ("Elden Ring - Speedrun World Record in 45m", "Watch an optimized playthrough of the GOTY gaming title.", "Gaming", ['gaming', 'elden ring']),
        ("MacBook Pro M4 Review: The Developer's Dream?", "M4 Apple Silicon compilation testing compilation times.", "Programming & Technology", ['tech', 'macbook']),
        ("lofi hip hop radio - beats to relax/study to", "Ongoing stream of soft beats for study states.", "Music", ['lofi', 'music']),
        ("How the Federal Reserve Controls the US Dollar", "Economics explained, inflation, interest rates, and GDP.", "Finance & Business", ['economics', 'money']),
        ("SpaceX Starship Launches Next-Gen Flight Test", "Engineering live stream of super heavy booster recovery.", "Science & Engineering", ['space', 'engineering']),
        ("React Router v7 Tutorial: Complete Guide", "Dynamic frontend navigation, layouts, and data loaders.", "Programming & Technology", ['react', 'router']),
        ("Designing my Dream Home Office Setup", "Productive, minimalistic desk setups with custom lighting.", "Self-Improvement", ['minimalism', 'workspace']),
        ("The Insane Engineering of the Burj Khalifa", "Structural challenges, wind buffering, and high-altitude concrete pumping.", "Science & Engineering", ['engineering', 'building']),
        ("Is AI Actually Replacing Software Engineers?", "Analyzing LLM code generation and the future of coding.", "Programming & Technology", ['ai', 'software']),
        ("The Ultimate Gym Routine for Desk Workers", "Correcting posture, active stretches, and full body hypertrophy.", "Sports", ['gym', 'workout']),
        ("Figma to Code - 5x Faster Workflows", "Converting UI mockups directly into JSX tailwind formats.", "Programming & Technology", ['figma', 'design']),
        ("Why I Sold My Startup for $10M at 25", "Building SaaS products, cold email campaigns, and exit strategies.", "Finance & Business", ['saas', 'startup']),
        ("Building a Physics Engine in Vanilla JavaScript", "Coding canvas collisions, gravity forces, and inertia vectors.", "Programming & Technology", ['javascript', 'physics']),
        ("A Day in the Life of a Google Tech Lead", "Software engineering routines, daily standups, and code review.", "Programming & Technology", ['google', 'tech lead'])
    ]
    
    for title, desc, category, tags in likes:
        mock_items.append({
            'title': title,
            'description': desc,
            'youtube_category_id': '28' if category in ['Programming & Technology', 'Science & Engineering'] else '27',
            'tags': tags,
            'type': 'like'
        })
        
    return mock_items

@app.route('/api/youtube/analyze', methods=['POST'])
def analyze():
    """
    Fetches user's YouTube activity data (or uses mock data if Demo User),
    performs categorization, metrics computation, and AI generation, then saves to SQLite.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    is_demo = session.get('is_demo', False)
    
    items = []
    data_source = 'api'
    
    if is_demo or not Config.is_oauth_configured():
        logger.info(f"Running simulation analysis for user: {user.name}")
        items = get_mock_youtube_data()
        data_source = 'mock'
    else:
        # Fetch live data using OAuth
        credentials_dict = session.get('oauth_credentials')
        if not credentials_dict:
            return jsonify({'error': 'OAuth credentials missing from session. Please login again.'}), 401
            
        credentials = Credentials(**credentials_dict)
        logger.info(f"Fetching YouTube data via API for user: {user.name}")
        
        # Pull subs & likes
        subs = get_user_subscriptions(credentials, max_results=50)
        likes = get_user_liked_videos(credentials, max_results=50)
        items = subs + likes
        data_source = 'api'
        
        if not items:
            # Fallback to mock data with a warning if API returned nothing
            logger.warning("YouTube API returned zero items. Falling back to mock data.")
            items = get_mock_youtube_data()
            data_source = 'mock'
            
    # Perform Pandas / NumPy analysis
    analysis_results = analyze_activity_data(items, data_source)
    if not analysis_results:
        return jsonify({'error': 'Failed to analyze YouTube data'}), 500
        
    dist = analysis_results['distribution']
    metrics = analysis_results['metrics']
    
    # Generate AI insights report
    api_key = app.config['GEMINI_API_KEY']
    ai_report = generate_ai_report(dist, metrics, data_source, api_key)
    
    # Save the analysis result in Database
    analysis = Analysis(
        user_id=user.id,
        category_distribution=json.dumps(dist),
        metrics=json.dumps(metrics),
        personality_report=json.dumps(ai_report),
        insights=json.dumps(ai_report.get('weekly_insights', [])),
        data_source=data_source
    )
    
    db.session.add(analysis)
    db.session.commit()
    
    return jsonify(analysis.to_dict())

@app.route('/api/youtube/upload', methods=['POST'])
def upload_takeout():
    """
    Allows users to upload a watch-history.json from Google Takeout.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    try:
        data = json.load(file)
        if not isinstance(data, list):
            return jsonify({'error': 'Invalid format. Google Takeout watch history must be a JSON array.'}), 400
            
        items = []
        # Parse Google Takeout watch history elements
        # Example takeout item: { "header": "YouTube", "title": "Watched Python Tutorial", "titleUrl": "...", "time": "2026-06-19..." }
        for entry in data[:300]: # limit to top 300 for execution performance
            title = entry.get('title', '')
            if title.startswith("Watched "):
                title = title[8:]
                
            # Takeout files contain channel details as subtitles
            subtitles = entry.get('subtitles', [])
            description = subtitles[0].get('name', '') if subtitles else ''
            
            items.append({
                'title': title,
                'description': description,
                'youtube_category_id': None,
                'tags': [],
                'type': 'takeout_watch'
            })
            
        if not items:
            return jsonify({'error': 'Could not parse any watch history items from the file.'}), 400
            
        # Run categorization and statistics
        analysis_results = analyze_activity_data(items, 'takeout')
        dist = analysis_results['distribution']
        metrics = analysis_results['metrics']
        
        # Generate AI report
        api_key = app.config['GEMINI_API_KEY']
        ai_report = generate_ai_report(dist, metrics, 'takeout', api_key)
        
        # Save to DB
        analysis = Analysis(
            user_id=user.id,
            category_distribution=json.dumps(dist),
            metrics=json.dumps(metrics),
            personality_report=json.dumps(ai_report),
            insights=json.dumps(ai_report.get('weekly_insights', [])),
            data_source='takeout'
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        return jsonify(analysis.to_dict())
    except Exception as e:
        logger.error(f"Error parsing Google Takeout file: {str(e)}")
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 400

@app.route('/api/analytics/history', methods=['GET'])
def get_history():
    """
    Retrieves historical analysis reports for current user.
    If only one report exists, automatically generates a simulated previous month
    report to demonstrate trend features immediately.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
        
    analyses = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.run_date.desc()).all()
    
    if not analyses:
        return jsonify([])
        
    # If the user only has 1 analysis, generate a simulated previous month to enable the Comparison tab features
    if len(analyses) == 1:
        current = analyses[0]
        current_dist = json.loads(current.category_distribution)
        
        past_data = get_simulated_historical_data(current_dist, user_id)
        past_dist = past_data['distribution']
        past_metrics = past_data['metrics']
        
        # Save historical report dated 30 days ago
        past_report = generate_ai_report(past_dist, past_metrics, current.data_source, app.config['GEMINI_API_KEY'])
        past_analysis = Analysis(
            user_id=user_id,
            run_date=datetime.utcnow() - timedelta(days=30),
            category_distribution=json.dumps(past_dist),
            metrics=json.dumps(past_metrics),
            personality_report=json.dumps(past_report),
            insights=json.dumps(past_report.get('weekly_insights', [])),
            data_source=current.data_source
        )
        db.session.add(past_analysis)
        db.session.commit()
        
        # Re-fetch
        analyses = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.run_date.desc()).all()
        
    return jsonify([a.to_dict() for a in analyses])

# Catch-all route to serve React frontend SPA static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
        
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)

