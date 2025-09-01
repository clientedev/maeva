# Maeva Investimentos Imobiliários

## Overview

Maeva Investimentos Imobiliários is a luxury real estate website for a São Paulo-based real estate consultancy specializing in medium to high-end properties. The platform serves as a digital showcase for property listings, company information, and client engagement tools. The website features a sophisticated black and gold design theme to convey luxury and exclusivity, with Portuguese language content targeting the Brazilian market.

The application provides a public-facing website for potential clients to browse properties and contact the company, along with an administrative interface for managing property listings through file uploads and content management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask for server-side rendering
- **UI Framework**: Bootstrap 5.3.0 for responsive design and component styling
- **Design System**: Custom CSS with luxury color scheme (black, gold, white) using CSS custom properties
- **Typography**: Google Fonts integration (Playfair Display for headings, Inter for body text)
- **Icons**: Font Awesome 6.4.0 for consistent iconography
- **JavaScript**: Vanilla ES6+ with modular function organization for interactive features

### Backend Architecture
- **Web Framework**: Flask with SQLAlchemy ORM for database operations
- **Application Structure**: Single-file application entry point with modular separation of concerns
- **Route Organization**: Dedicated routes module handling all URL endpoints and request processing
- **Model Layer**: SQLAlchemy models with declarative base for database schema definition
- **Session Management**: Flask sessions with configurable secret key and ProxyFix middleware

### Authentication & Authorization
- **Admin Access**: Simple password-based authentication system without user registration
- **Session Management**: Custom AdminSession model with token-based session tracking
- **Session Expiration**: 2-hour expiration window for administrative sessions
- **Security**: Hard-coded admin password (4731v8) with session token generation using UUID4

### File Management System
- **Upload Strategy**: Local file storage in dedicated uploads directory
- **File Validation**: Extension-based filtering for images and videos (png, jpg, jpeg, gif, mp4, avi, mov)
- **Size Limits**: 16MB maximum file upload size
- **File Security**: Werkzeug secure_filename implementation for safe file handling
- **Static File Serving**: Flask static file serving for uploaded content

### Database Design
- **Property Model**: Core entity storing listing information including title, description, media paths, pricing, and location data
- **AdminSession Model**: Authentication tracking with session tokens and expiration timestamps
- **Schema Strategy**: SQLAlchemy with automatic table creation and model relationships
- **Database Flexibility**: Environment-configurable database URL with SQLite default for development

## External Dependencies

### Database Systems
- **SQLite**: Default development database with file-based storage
- **PostgreSQL**: Production-ready option via DATABASE_URL environment variable
- **Connection Management**: SQLAlchemy connection pooling with 300-second recycle time and pre-ping health checks

### CDN & External Resources
- **Bootstrap CDN**: CSS framework delivery via jsDelivr CDN
- **Font Awesome CDN**: Icon library via CloudFlare CDN
- **Google Fonts API**: Custom typography loading for Playfair Display and Inter fonts
- **Pixabay**: Image hosting service for placeholder and stock photography

### Communication Platforms
- **WhatsApp Business**: Primary customer communication channel with click-to-chat integration
- **Instagram**: Social media presence (@Roseaventura) for marketing and portfolio display
- **LinkedIn**: Professional networking platform (Rose Ventura) for business connections

### Development & Deployment
- **Werkzeug**: WSGI utilities and development server with proxy fix middleware
- **Flask Extensions**: SQLAlchemy integration for ORM functionality
- **Python Environment**: Configurable host and port settings with debug mode support

### Third-Party Integrations
- **Social Sharing**: Native web sharing APIs for property listings
- **Contact Forms**: Direct integration with WhatsApp web interface for lead generation
- **Media Display**: Responsive image and video galleries with modal overlays