from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(300))  # Main image for backward compatibility
    video_path = db.Column(db.String(300))
    property_type = db.Column(db.String(100))  # apartment, house, commercial
    price = db.Column(db.String(100))
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    featured = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Property {self.title}>'

class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    property = db.relationship('Property', backref=db.backref('images', lazy=True, order_by='PropertyImage.order_index', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<PropertyImage {self.image_path}>'

class ChatbotConversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    message = db.Column(db.Text)
    bot_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatbotConversation {self.name}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    image_path = db.Column(db.String(300))
    video_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    featured = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Post {self.title}>'


class AdminSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_token = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
