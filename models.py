from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(300))
    video_path = db.Column(db.String(300))
    property_type = db.Column(db.String(100))  # apartment, house, commercial
    price = db.Column(db.String(100))
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    featured = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Property {self.title}>'

class AdminSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_token = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
