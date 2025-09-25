import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, LargeBinary
from database import db

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
    
    # Optimized file storage - removed LargeBinary for performance
    video_filename = db.Column(db.String(255))
    video_content_type = db.Column(db.String(100))
    
    def has_video_data(self):
        """Check if this instance has video file available"""
        return (self.video_path and os.path.exists(self.video_path)) or self.video_filename
    
    def has_video_file(self):
        """Check if this instance has video file stored locally"""
        return self.video_path is not None and os.path.exists(self.video_path) if self.video_path else False
    
    def __repr__(self):
        return f'<Property {self.title}>'

class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)  # Keep for backward compatibility
    is_primary = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optimized file storage - removed LargeBinary for performance
    image_filename = db.Column(db.String(255))
    image_content_type = db.Column(db.String(100))
    
    def has_image_data(self):
        """Check if this instance has image file available"""
        return (self.image_path and os.path.exists(self.image_path)) or self.image_filename
    
    def has_image_file(self):
        """Check if this instance has image file stored locally (backward compatibility)"""
        return self.image_path is not None and os.path.exists(self.image_path) if self.image_path else False
    
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
    
    # Optimized file storage - removed LargeBinary for performance
    image_filename = db.Column(db.String(255))
    image_content_type = db.Column(db.String(100))
    video_filename = db.Column(db.String(255))
    video_content_type = db.Column(db.String(100))
    
    def has_image_data(self):
        """Check if this instance has image file available"""
        return (self.image_path and os.path.exists(self.image_path)) or self.image_filename
    
    def has_video_data(self):
        """Check if this instance has video file available"""
        return (self.video_path and os.path.exists(self.video_path)) or self.video_filename
    
    def has_image_file(self):
        """Check if this instance has image file stored locally (backward compatibility)"""
        return self.image_path is not None and os.path.exists(self.image_path) if self.image_path else False
    
    def has_video_file(self):
        """Check if this instance has video file stored locally (backward compatibility)"""
        return self.video_path is not None and os.path.exists(self.video_path) if self.video_path else False
    
    def __repr__(self):
        return f'<Post {self.title}>'


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    interest = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ContactMessage {self.name}>'

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, default='admin')
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Admin {self.username}>'

class AdminSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_token = db.Column(db.String(100), unique=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    admin = db.relationship('Admin', backref=db.backref('sessions', lazy=True))
