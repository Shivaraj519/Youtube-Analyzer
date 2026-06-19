from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(128), unique=True, nullable=True)
    email = db.Column(db.String(128), unique=True, nullable=True)
    name = db.Column(db.String(128), nullable=False)
    picture = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'google_id': self.google_id,
            'email': self.email,
            'name': self.name,
            'picture': self.picture,
            'created_at': self.created_at.isoformat()
        }

class Analysis(db.Model):
    __tablename__ = 'analyses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    run_date = db.Column(db.DateTime, default=datetime.utcnow)
    category_distribution = db.Column(db.Text, nullable=False)  # JSON string
    metrics = db.Column(db.Text, nullable=False)  # JSON string
    personality_report = db.Column(db.Text, nullable=False)
    insights = db.Column(db.Text, nullable=False)  # JSON string (list of structured weekly/monthly observations)
    data_source = db.Column(db.String(32), default='api') # 'api', 'mock', 'takeout'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'run_date': self.run_date.isoformat(),
            'category_distribution': json.loads(self.category_distribution),
            'metrics': json.loads(self.metrics),
            'personality_report': self.personality_report,
            'insights': json.loads(self.insights),
            'data_source': self.data_source
        }
