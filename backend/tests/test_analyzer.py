import sys
import os
# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from analyzer import classify_item, analyze_activity_data, generate_personality_archetype, get_simulated_historical_data

def test_classify_item():
    # Test Programming and Technology
    assert classify_item("Learn Python Coding for Beginners", "", [], None) == "Programming & Technology"
    assert classify_item("Rust Programming Language Deep Dive", "", [], None) == "Programming & Technology"
    
    # Test Gaming
    assert classify_item("Minecraft 1.20 Playthrough Part 1", "", [], "20") == "Gaming"
    
    # Test Music
    assert classify_item("Relaxing Acoustic Guitar Instrumental", "", [], "10") == "Music"
    
    # Test Finance
    assert classify_item("How to Buy Index Funds and Build Wealth", "", [], None) == "Finance & Business"
    
    # Test Education
    assert classify_item("Crash Course World History Episode 12", "", [], "27") == "Education"

def test_analyze_activity_data():
    items = [
        {"title": "Intro to Coding in Python", "description": "", "tags": [], "youtube_category_id": "28", "type": "like"},
        {"title": "How to Build a Startup SaaS", "description": "", "tags": [], "youtube_category_id": None, "type": "like"},
        {"title": "lofi beats to study to", "description": "", "tags": [], "youtube_category_id": "10", "type": "subscription"},
        {"title": "Minecraft Speedrun", "description": "", "tags": [], "youtube_category_id": "20", "type": "subscription"},
        {"title": "Neuroscience and Huberman focus tips", "description": "", "tags": [], "youtube_category_id": None, "type": "like"}
    ]
    
    results = analyze_activity_data(items, 'mock')
    assert results is not None
    assert 'distribution' in results
    assert 'metrics' in results
    
    dist = results['distribution']
    metrics = results['metrics']
    
    # Check that categories exist
    assert dist['Programming & Technology'] > 0
    assert dist['Finance & Business'] > 0
    assert dist['Music'] > 0
    assert dist['Gaming'] > 0
    assert dist['Self-Improvement'] > 0
    
    # Check counts
    assert metrics['item_count'] == 5
    assert metrics['liked_count'] == 3
    assert metrics['sub_count'] == 2
    
    # Learning categories are Programming (20%), Finance (20%), Self-Improvement (20%) -> 60%
    # Entertainment are Music (20%), Gaming (20%) -> 40%
    assert metrics['learning_ratio'] == 60.0
    assert metrics['entertainment_ratio'] == 40.0
    assert metrics['productivity_score'] > 50  # Positive productivity weight

def test_generate_personality_archetype():
    dist = {
        'Programming & Technology': 40.0,
        'Science & Engineering': 30.0,
        'Music': 30.0
    }
    metrics = {'learning_ratio': 70.0}
    
    archetype, desc = generate_personality_archetype(dist, metrics)
    assert archetype == "The Architect Genius"
    assert "logical and intellectual" in desc

def test_simulated_historical_data():
    current_dist = {
        'Programming & Technology': 50.0,
        'Gaming': 30.0,
        'Music': 20.0
    }
    
    past_data = get_simulated_historical_data(current_dist, 42)
    past_dist = past_data['distribution']
    
    # Total past percentage must sum to 100%
    assert round(sum(past_dist.values())) == 100
    
    # Check that shifts occur but are relatively close
    assert past_dist['Programming & Technology'] > 30
    assert past_dist['Gaming'] > 15
