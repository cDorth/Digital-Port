# Overview

This is an advanced digital portfolio web application built with Flask that showcases projects and achievements with AI-powered features. The system includes a public portfolio area, admin dashboard, user authentication, and enhanced features like AI recommendations, interactive career timeline, skills comparator, and complete multilingual support (Portuguese/English) with instant language switching. The application uses PostgreSQL database and includes modern UI/UX with Bootstrap 5.

# User Preferences

Preferred communication style: Simple, everyday language.

# Recent Changes (Updated August 12, 2025)

- Enhanced "Let's Work Together" section with modern CTA design featuring:
  - Animated background with floating shapes and elements
  - Professional gradient design with glassmorphism effects
  - Interactive contact buttons with icons and hover animations
  - Trust indicators and feature highlights
  - Full responsive design for all devices

- Transformed featured projects section with:
  - Interactive project cards with hover zoom and shadow effects
  - Modern card design with gradient overlays
  - Enhanced project stats and tags display
  - Smooth animations and microinteractions
  - Professional typography and spacing

- Updated internationalization support:
  - Added new i18n keys for enhanced sections
  - Complete bilingual support (Portuguese/English) for new content
  - Instant language switching functionality

# System Architecture

## Frontend Architecture
The application uses a traditional server-side rendered architecture with Jinja2 templates. The frontend is built with Bootstrap 5 for responsive design and styling, Font Awesome for icons, and custom CSS for additional styling. JavaScript provides client-side enhancements like tooltips, auto-hiding alerts, and search form improvements.

## Backend Architecture
The backend follows the Flask framework pattern with a modular structure:

- **Application Factory Pattern**: The Flask app is configured in `app.py` with database initialization and login management
- **Blueprint Architecture**: Routes are organized in `routes.py` with clear separation between public, admin, and authentication endpoints
- **Model-View-Controller (MVC)**: Models are defined in `models.py`, views are handled through templates, and controllers are in the routes file
- **Form Handling**: WTForms integration provides form validation and CSRF protection through `forms.py`
- **File Management**: Utility functions in `utils.py` handle image uploads, resizing, and file operations

## Data Storage Solutions
The application uses SQLAlchemy ORM with Flask-SQLAlchemy for database operations. The database schema includes:

- **User Management**: User model with authentication support via Flask-Login, including language preferences
- **Content Management**: Project, Category, and Tag models with many-to-many relationships
- **Interaction Features**: Comment and Like models for user engagement
- **Portfolio Content**: AboutMe model for personal information display
- **Internationalization**: Complete bilingual support (Portuguese/English) with client-side switching and user preference storage

The database supports PostgreSQL through environment configuration with connection pooling and automatic reconnection features. User preferences including language settings are stored in the database for authenticated users.

## Authentication and Authorization
User authentication is handled through Flask-Login with session-based management. The system includes:

- **User Registration/Login**: Standard email/password authentication with password hashing using Werkzeug
- **Admin Authorization**: Role-based access control with admin flags for content management
- **Session Management**: Remember me functionality and secure session handling
- **CSRF Protection**: Built-in protection through Flask-WTF

## File Upload System
Image handling includes automatic resizing using Pillow, secure filename generation, and organized storage in the static uploads directory. The system supports common image formats with file size limitations.

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web framework for the application
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering

## Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design (via CDN)
- **Font Awesome 6**: Icon library (via CDN)
- **Pillow**: Python imaging library for image processing

## Database Integration
- **SQLAlchemy**: Database abstraction layer
- **PostgreSQL**: Primary database (configured via DATABASE_URL environment variable)

## Security and Utilities
- **Werkzeug**: Password hashing and security utilities
- **ProxyFix**: Middleware for handling reverse proxy headers

## Environment Configuration
The application relies on environment variables for:
- **SESSION_SECRET**: Flask session encryption key
- **DATABASE_URL**: Database connection string

## Development Dependencies
- **Python 3.x**: Runtime environment
- **Flask development server**: For local development and testing