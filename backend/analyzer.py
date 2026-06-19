import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Define keyword lists for categorization
KEYWORDS = {
    'Programming & Technology': [
        'python', 'javascript', 'rust', 'c++', 'java', 'programming', 'coding', 'web dev', 'software', 
        'developer', 'react', 'git', 'ai', 'machine learning', 'llm', 'framework', 'database', 'aws', 
        'docker', 'kubernetes', 'tech stack', 'neural network', 'github', 'vscode', 'api', 'backend', 
        'frontend', 'algorithm', 'data structures', 'coder', 'hackathon', 'linux'
    ],
    'Science & Engineering': [
        'physics', 'math', 'calculus', 'chemistry', 'biology', 'quantum', 'engineering', 'robotics', 
        'space', 'astronomy', 'nasa', 'electronics', 'hardware', 'mechanical', 'aerospace', 'science',
        'veritasium', 'vsauce', 'curious', 'cosmos', 'universe', 'black hole', 'evolution'
    ],
    'Education': [
        'course', 'tutorial', 'learn', 'how to', 'explained', 'history', 'lecture', 'academy', 
        'crash course', 'ted', 'documentary', 'khan academy', 'syllabus', 'college', 'school',
        'curriculum', 'lesson', 'study', 'expert', 'guide', 'class'
    ],
    'Gaming': [
        'gameplay', 'gaming', 'twitch', 'ps5', 'xbox', 'nintendo', 'playthrough', 'let\'s play', 
        'speedrun', 'minecraft', 'fortnite', 'roblox', 'esports', 'valheim', 'elden ring', 'gta', 
        'cyberpunk', 'streamer', 'ign', 'retro gaming', 'playstation', 'console'
    ],
    'Finance & Business': [
        'stocks', 'crypto', 'investing', 'bitcoin', 'finance', 'market', 'dividend', 'wealth', 
        'startup', 'saas', 'marketing', 'economics', 'real estate', 'portfolio', 'passive income',
        'side hustle', 'trading', 'etf', 'personal finance', 'business', 'entrepreneur', 'invest',
        'fund', 'funds', 'capital'
    ],
    'Movies & Entertainment': [
        'movie', 'film', 'trailer', 'netflix', 'comedy', 'funny', 'skit', 'vlog', 'anime', 'series', 
        'review', 'marvel', 'hollywood', 'cinema', 'actor', 'directors cut', 'show', 'reaction',
        'podcast', 'parody', 'memes'
    ],
    'Music': [
        'song', 'music', 'album', 'lofi', 'playlist', 'remix', 'instrumental', 'guitar', 'piano', 
        'singing', 'concert', 'beat', 'cover', 'official audio', 'spotify', 'lyrics', 'live session'
    ],
    'Sports': [
        'football', 'basketball', 'soccer', 'nfl', 'nba', 'sports', 'workout', 'highlights', 
        'ufc', 'mma', 'gym', 'fitness', 'bodybuilding', 'tennis', 'cricket', 'baseball', 'olympics',
        'athlete', 'training session', 'calisthenics'
    ],
    'News': [
        'news', 'politics', 'current events', 'election', 'cnn', 'bbc', 'report', 'world news', 
        'journalist', 'press conference', 'breaking news', 'conflict', 'senate', 'prime minister'
    ],
    'Self-Improvement': [
        'productivity', 'motivation', 'mindset', 'habits', 'routines', 'discipline', 'meditation', 
        'focus', 'mental health', 'huberman', 'success', 'minimalism', 'growth', 'stoic', 'confidence',
        'time management', 'biohacking', 'sleep'
    ],
    'Vlogs & Lifestyle': [
        'vlog', 'vlogs', 'lifestyle', 'travel vlog', 'daily vlog', 'routine', 'blogs', 'blogging', 
        'day in the life', 'unboxing', 'challenge', 'hauls', 'shopping haul', 'skincare', 'morning routine',
        'night routine', 'grwm', 'traveling', 'vlogger'
    ]
}

# YouTube official category ID mapping
YT_CATEGORY_MAPPING = {
    '10': 'Music',
    '15': 'Other',          # Pets & Animals
    '17': 'Sports',
    '19': 'Other',          # Travel & Events
    '20': 'Gaming',
    '22': 'Vlogs & Lifestyle', # People & Blogs
    '23': 'Movies & Entertainment', # Comedy
    '24': 'Movies & Entertainment', # Entertainment
    '25': 'News',
    '26': 'Self-Improvement',      # Howto & Style
    '27': 'Education',
    '28': 'Science & Engineering', # Science & Technology
    '30': 'Movies & Entertainment', # Movies
    '44': 'Movies & Entertainment'  # Trailers
}

def classify_item(title, description="", tags=None, yt_category_id=None):
    """
    Heuristically classifies a video/channel into one of our 11 target categories.
    """
    if tags is None:
        tags = []
        
    text_content = f"{title} {description} {' '.join(tags)}".lower()
    
    # Initialize category scores
    scores = {cat: 0 for cat in KEYWORDS.keys()}
    
    # 1. Check tags & text for exact keyword matches
    for category, kw_list in KEYWORDS.items():
        for kw in kw_list:
            if kw in text_content:
                # Give higher weight to matches in title
                if kw in title.lower():
                    scores[category] += 3
                else:
                    scores[category] += 1
                    
    # 2. Check official YouTube Category ID mapping
    if yt_category_id and yt_category_id in YT_CATEGORY_MAPPING:
        yt_cat = YT_CATEGORY_MAPPING[yt_category_id]
        if yt_cat in scores:
            scores[yt_cat] += 5
            # Special logic: Category 28 (Science & Technology) could be Programming & Technology too
            if yt_category_id == '28':
                # Check tech keywords
                tech_hits = any(kw in text_content for kw in KEYWORDS['Programming & Technology'])
                if tech_hits:
                    scores['Programming & Technology'] += 6
                else:
                    scores['Science & Engineering'] += 5
                    
    # Find the category with highest score
    max_cat = max(scores, key=scores.get)
    
    # If no keywords matched and no YouTube category ID matches, classify as Other
    if scores[max_cat] == 0 and (not yt_category_id or yt_category_id not in YT_CATEGORY_MAPPING):
        return 'Other'
        
    return max_cat

def analyze_activity_data(items, data_source='api'):
    """
    Analyzes a list of YouTube items (subscriptions and/or likes), calculates distributions
    and metrics using Pandas.
    """
    if not items:
        return None
        
    # Classify all items
    classified_items = []
    for item in items:
        cat = classify_item(
            title=item.get('title', ''),
            description=item.get('description', ''),
            tags=item.get('tags', []),
            yt_category_id=item.get('youtube_category_id')
        )
        classified_items.append({
            'title': item.get('title'),
            'category': cat,
            'type': item.get('type', 'activity')
        })
        
    df = pd.DataFrame(classified_items)
    
    # Calculate distribution
    counts = df['category'].value_counts()
    total = len(df)
    
    distribution = {}
    all_categories = list(KEYWORDS.keys()) + ['Other']
    for cat in all_categories:
        distribution[cat] = float(np.round((counts.get(cat, 0) / total) * 100, 1))
        
    # Sort distribution by percentage descending
    sorted_dist = dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))
    
    # Compute scores
    learning_cats = ['Programming & Technology', 'Science & Engineering', 'Education', 'Finance & Business', 'Self-Improvement']
    entertainment_cats = ['Gaming', 'Movies & Entertainment', 'Music', 'Sports', 'Vlogs & Lifestyle']
    
    learning_score = sum(sorted_dist.get(c, 0) for c in learning_cats)
    entertainment_score = sum(sorted_dist.get(c, 0) for c in entertainment_cats)
    
    # Normalize scores out of 100 (in case 'Other' or 'News' dominates)
    total_le = learning_score + entertainment_score
    if total_le > 0:
        learning_ratio = (learning_score / total_le) * 100
        entertainment_ratio = (entertainment_score / total_le) * 100
    else:
        learning_ratio = 50.0
        entertainment_ratio = 50.0
        
    # Productivity score: based heavily on Learning content vs Entertainment content, with News being neutral
    # Self-Improvement, Programming, and Education give highest productivity weight
    productivity_weight = (
        sorted_dist.get('Programming & Technology', 0) * 1.0 +
        sorted_dist.get('Self-Improvement', 0) * 1.2 +
        sorted_dist.get('Education', 0) * 0.9 +
        sorted_dist.get('Science & Engineering', 0) * 0.8 +
        sorted_dist.get('Finance & Business', 0) * 1.0 -
        sorted_dist.get('Gaming', 0) * 0.8 -
        sorted_dist.get('Movies & Entertainment', 0) * 0.6
    )
    
    # Normalize productivity score to range 20 - 98
    productivity_score = int(np.clip(50 + (productivity_weight * 1.2), 20, 98))
    
    # Determine top topics / keywords
    top_categories = [cat for cat, pct in sorted_dist.items() if pct > 0][:3]
    
    metrics = {
        'learning_ratio': float(np.round(learning_ratio, 1)),
        'entertainment_ratio': float(np.round(entertainment_ratio, 1)),
        'productivity_score': productivity_score,
        'top_categories': top_categories,
        'item_count': total,
        'liked_count': sum(1 for item in items if item.get('type') == 'like'),
        'sub_count': sum(1 for item in items if item.get('type') == 'subscription')
    }
    
    return {
        'distribution': sorted_dist,
        'metrics': metrics
    }

def get_simulated_historical_data(current_dist, user_id=None):
    """
    Creates a simulated database entry from 30 days ago to show historical trends,
    emerging interests, and comparisons.
    """
    # Shift current categories by a randomized -4% to +4% and re-normalize to 100%
    np.random.seed(user_id or 42)
    categories = list(current_dist.keys())
    shifts = np.random.uniform(-4.0, 4.0, len(categories))
    
    past_dist = {}
    for i, cat in enumerate(categories):
        past_dist[cat] = max(0.0, current_dist[cat] + shifts[i])
        
    total_past = sum(past_dist.values())
    if total_past > 0:
        for cat in past_dist:
            past_dist[cat] = float(np.round((past_dist[cat] / total_past) * 100, 1))
            
    # Calculate past scores
    learning_cats = ['Programming & Technology', 'Science & Engineering', 'Education', 'Finance & Business', 'Self-Improvement']
    learning_score = sum(past_dist.get(c, 0) for c in learning_cats)
    ent_cats = ['Gaming', 'Movies & Entertainment', 'Music', 'Sports']
    ent_score = sum(past_dist.get(c, 0) for c in ent_cats)
    
    total_le = learning_score + ent_score
    learning_ratio = (learning_score / total_le) * 100 if total_le > 0 else 50.0
    
    productivity_weight = (
        past_dist.get('Programming & Technology', 0) * 1.0 +
        past_dist.get('Self-Improvement', 0) * 1.2 +
        past_dist.get('Education', 0) * 0.9 +
        past_dist.get('Science & Engineering', 0) * 0.8 +
        past_dist.get('Finance & Business', 0) * 1.0 -
        past_dist.get('Gaming', 0) * 0.8 -
        past_dist.get('Movies & Entertainment', 0) * 0.6
    )
    productivity_score = int(np.clip(50 + (productivity_weight * 1.2), 20, 98))
    
    return {
        'distribution': past_dist,
        'metrics': {
            'learning_ratio': float(np.round(learning_ratio, 1)),
            'entertainment_ratio': float(np.round(100 - learning_ratio, 1)),
            'productivity_score': productivity_score,
            'top_categories': [c for c, p in sorted(past_dist.items(), key=lambda x: x[1], reverse=True)[:3]]
        }
    }

def generate_personality_archetype(distribution, metrics):
    """
    Deduce personality archetype based on dominant categories.
    """
    sorted_cats = list(distribution.keys())
    primary = sorted_cats[0]
    secondary = sorted_cats[1] if len(sorted_cats) > 1 else 'Other'
    
    # Archetype decisions
    if primary == 'Programming & Technology':
        if secondary in ['Science & Engineering', 'Education']:
            return "The Architect Genius", "A highly logical and intellectual builder focused on solving complex engineering puzzles."
        elif secondary in ['Finance & Business', 'Self-Improvement']:
            return "The Tech Entrepreneur", "A modern builder focused on leveraging automation and software to create business value."
        else:
            return "The Digital Craftsman", "A practical programmer who enjoys crafting clean code and experimenting with tech stacks."
            
    elif primary == 'Education':
        if secondary in ['Science & Engineering', 'Programming & Technology']:
            return "The Analytical Scholar", "An insatiable learner driven by understanding the fundamental equations and codes of life."
        else:
            return "The Lifelong Learner", "Curious and well-rounded, searching for deep documentaries and intellectual explanations."
            
    elif primary == 'Gaming':
        if secondary in ['Programming & Technology', 'Science & Engineering']:
            return "The Virtual Engineer", "Combines analytical thinking with interactive digital gameplay, exploring game mechanics."
        else:
            return "The Interactive Explorer", "Finds relaxation, community, and strategy within immersive video game worlds."
            
    elif primary == 'Finance & Business':
        if secondary in ['Self-Improvement', 'Programming & Technology']:
            return "The Wealth Optimizer", "A goal-driven individual interested in productivity hacks, coding tools, and asset allocation."
        else:
            return "The Venture Strategist", "Keeps a sharp eye on financial indicators, stock models, and macroeconomic changes."
            
    elif primary == 'Self-Improvement':
        if secondary in ['Education', 'Sports']:
            return "The Peak Optimizer", "Fascinated by neuroscience, physical fitness, and daily habits to maximize cognitive performance."
        else:
            return "The Mindful Achiever", "Focused on mental fortitude, stoicism, and actionable steps to improve personal growth."
            
    elif primary in ['Movies & Entertainment', 'Music']:
        if metrics['learning_ratio'] > 40:
            return "The Creative Thinker", "Appreciates artistic design and musical beats while balancing it with insightful learning."
        else:
            return "The Culture Connoisseur", "Seeks entertainment, storytelling, and musical composition as primary forms of digital output."
            
    else:
        # Default fallback
        if metrics['learning_ratio'] > 50:
            return "The Balanced Explorer", "Balances diverse interests across engineering, coding, and general knowledge updates."
        else:
            return "The Relaxed Generalist", "Utilizes YouTube for a wide mix of pop culture, news updates, and leisure activities."

def generate_ai_report(distribution, metrics, data_source='api', api_key=None):
    """
    Generates a full-text report, strengths, recommendations, and insights.
    If Gemini API key is configured, uses Live AI models. Otherwise, falls back to local NLP template generator.
    """
    sorted_cats = [(k, v) for k, v in distribution.items() if v > 0]
    
    # Basic info formatting
    top_cat_str = ", ".join([f"{c} ({p}%)" for c, p in sorted_cats[:3]])
    learning_ratio = metrics['learning_ratio']
    ent_ratio = metrics['entertainment_ratio']
    productivity = metrics['productivity_score']
    
    archetype, archetype_desc = generate_personality_archetype(distribution, metrics)
    
    # 1. Try Live Gemini API
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            You are a senior behavioral psychologist and data analyst specializing in digital footprints.
            Analyze the following YouTube viewing metrics to write a premium "YouTube Digital Personality Report":
            
            - Top Categories: {top_cat_str}
            - All Categories: {json.dumps(distribution)}
            - Learning vs Entertainment Ratio: {learning_ratio}% Learning / {ent_ratio}% Entertainment
            - Productivity Score: {productivity}/100
            - Deduced Archetype: {archetype} - {archetype_desc}
            
            Your response must be in JSON format matching this schema:
            {{
                "report_text": "A detailed 3-paragraph summary of their personality, interests, and learning habits. Use engaging, premium language.",
                "strengths": [
                    "A list of 3-4 strengths indicated by this pattern"
                ],
                "learning_areas": [
                    "A list of 3-4 potential growth areas or recommendations to optimize their learning"
                ],
                "weekly_insights": [
                    "Insight 1: A brief sentence summarizing a specific trend based on categories",
                    "Insight 2: Another insight about their productivity habits",
                    "Insight 3: An observation about their balance"
                ]
            }}
            
            Format the output strictly as a parseable JSON object. Do not include markdown code block syntax (like ```json) in your raw response. Just return the JSON object.
            """
            response = model.generate_content(prompt)
            # Clean up response text if markdown fence exists
            resp_text = response.text.strip()
            if resp_text.startswith("```"):
                lines = resp_text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                resp_text = "\n".join(lines).strip()
                
            data = json.loads(resp_text)
            # Add archetype details
            data['archetype'] = archetype
            data['archetype_description'] = archetype_desc
            return data
        except Exception as e:
            logger.error(f"Gemini API generation failed, falling back to local model: {str(e)}")
            
    # 2. Local Fallback Generator
    # Generate report text using templates
    sorted_cats_list = list(distribution.keys())
    primary = sorted_cats_list[0]
    secondary = sorted_cats_list[1] if len(sorted_cats_list) > 1 else 'Other'
    
    report_p1 = (
        f"Based on your digital profile, you are characterized as **{archetype}**. "
        f"You primarily consume {primary.lower()} content (representing {distribution[primary]}% of your activity), "
        f"balanced by interests in {secondary.lower()} ({distribution.get(secondary, 0)}%). "
        f"Your viewing habits suggest a profile highly matching {archetype_desc.lower()}"
    )
    
    if learning_ratio >= 60:
        report_p2 = (
            f"Your viewing ratio indicates a growth-oriented mindset, with educational content representing {learning_ratio}% of your overall activity. "
            f"You actively utilize digital video as a medium for skill acquisition, self-study, and cognitive development. "
            f"Your focus on practical topics (like programming, finance, or science) acts as a powerful lever for career development and problem-solving skills."
        )
    elif learning_ratio >= 40:
        report_p2 = (
            f"Your profile maintains a balanced allocation of {learning_ratio}% learning and {ent_ratio}% entertainment content. "
            f"You utilize YouTube as a dual-purpose tool: extracting practical insights to build skills, while reserving sufficient bandwidth for relaxation, music, or gameplay. "
            f"This moderation supports healthy long-term retention without cognitive fatigue."
        )
    else:
        report_p2 = (
            f"Your current YouTube footprint leans primarily toward leisure and entertainment, which accounts for {ent_ratio}% of your viewing. "
            f"While video serves as a great tool for stress relief, comedy, and creative inspiration, "
            f"there is an opportunity to re-balance your queue toward skill-building categories (like coding, personal finance, or self-improvement) to boost your productivity score of {productivity}."
        )
        
    report_p3 = (
        f"Your overall productivity rating is {productivity}/100. By optimizing your subscriptions, "
        f"focusing on structured tutorials, and minimizing mindless scrolling in gaming or entertainment feeds, "
        f"you can convert your watch time into a structured personal university. "
        f"Your emerging interests point toward potential growth in self-improvement and technical skillsets."
    )
    
    report_text = f"{report_p1}\n\n{report_p2}\n\n{report_p3}"
    
    # Establish strengths based on top categories
    strengths_pool = {
        'Programming & Technology': [
            "Strong logical thinking and algorithmic problem-solving capacity",
            "High tech-literacy and adaptation to modern software and AI advancements",
            "Active builder mindset focused on developer tools and automation"
        ],
        'Science & Engineering': [
            "Deep scientific curiosity and interest in fundamental mechanics",
            "Intellectual endurance to grasp complex physics, math, or space concepts",
            "Analytical approach to dissecting how the physical world works"
        ],
        'Education': [
            "Active commitment to lifelong learning and intellectual expansion",
            "Broad general knowledge spanning history, science, and documentary resources",
            "Disciplined consumer of long-form, information-rich videos"
        ],
        'Finance & Business': [
            "Strong fiscal consciousness and focus on wealth optimization",
            "Interest in macroeconomic trends, startups, and product design",
            "Strategic investor mindset focused on portfolio building"
        ],
        'Self-Improvement': [
            "High self-awareness and active dedication to mental/physical well-being",
            "Focus on neurochemistry, time management, and peak habits",
            "Action-oriented mindset striving for personal optimization"
        ],
        'Gaming': [
            "Quick cognitive reaction time and tactical game-theory mindset",
            "Appreciation for immersive digital stories, designs, and communities"
        ],
        'Movies & Entertainment': [
            "High cultural intelligence and appreciation for storytelling",
            "Creative approach to entertainment and comedy skits"
        ],
        'Music': [
            "Strong audio-sensory appreciation and creative focus",
            "Ability to utilize soundscapes (like lofi) to set studying or working states"
        ],
        'Sports': [
            "Active fitness focus, athletic inspiration, and kinesthetic knowledge",
            "Competitive drive and appreciation for team synergy and strategy"
        ],
        'News': [
            "Strong awareness of global current events, politics, and macro affairs",
            "Active civic interest and media tracking"
        ],
        'Vlogs & Lifestyle': [
            "Interest in daily human experiences, lifestyle trends, and visual storytelling",
            "Appreciation for personal authenticity, routines, and content creation formats"
        ]
    }
    
    # Fetch strengths based on top 2 categories
    strengths = []
    if primary in strengths_pool:
        strengths.extend(strengths_pool[primary][:2])
    if secondary in strengths_pool:
        strengths.extend(strengths_pool[secondary][:2])
        
    # Ensure fallback strengths if list is empty
    if len(strengths) < 3:
        strengths = [
            "Balanced curiosity across multiple distinct YouTube topics",
            "Strong digital literacy and custom content curation habits",
            "Use of video formats for combined learning and stress reduction"
        ]
        
    # Define suggestions for learning areas
    learning_pool = {
        'Programming & Technology': [
            "Complement coding videos with hands-on Github repository building to avoid 'tutorial hell'",
            "Include more self-improvement or communication content to balance technical hard skills",
        ],
        'Gaming': [
            "Set explicit daily app limits on gaming streams to allocate time for active skill building",
            "Transition passive game viewing into creative development, like game-dev or graphics design"
        ],
        'Movies & Entertainment': [
            "Introduce structured learning (e.g. 20 minutes of programming/math) before watching comedy/vlogs",
            "Use documentary formats to bridge the gap between pure entertainment and educational topics"
        ],
        'Finance & Business': [
            "Verify video investment suggestions against actual SEC files or financial reports to prevent hype traps",
            "Balance finance content with self-study in science, engineering, or technology"
        ],
        'Self-Improvement': [
            "Reduce productivity-optimization videos and prioritize active execution of your goals",
            "Incorporate light coding or math tutorials to build hard logical skills alongside soft motivation"
        ],
        'Vlogs & Lifestyle': [
            "Balance casual lifestyle streams with structured study/educational playlists",
            "Limit passive viewing of daily logs and translate suggestions into actionable lifestyle practices"
        ]
    }
    
    learning_areas = []
    if primary in learning_pool:
        learning_areas.extend(learning_pool[primary])
    if secondary in learning_pool:
        learning_areas.extend(learning_pool[secondary])
        
    # Standard recommendations
    learning_areas.append("Set a weekly 'Learning Hour' target for technical and educational channels")
    learning_areas.append("Export lists of watched tutorials to compile personal reference cheat-sheets")
    
    # Crop to max 4 items
    learning_areas = learning_areas[:4]
    
    # Weekly Insights
    weekly_insights = [
        f"Your focus on {primary} remains high this week, consolidating it as your dominant digital interest.",
        f"Productivity rating is currently sitting at {productivity}/100, which is { 'above' if productivity > 65 else 'below' } optimal thresholds.",
        f"A minor uptick in {secondary} indicates a developing shift in your interest profile."
    ]
    
    return {
        'archetype': archetype,
        'archetype_description': archetype_desc,
        'report_text': report_text,
        'strengths': strengths,
        'learning_areas': learning_areas,
        'weekly_insights': weekly_insights
    }
