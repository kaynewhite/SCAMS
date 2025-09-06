# Clearance System

## Overview
A modern Flask-based web application for managing student clearance requirements in an academic institution. The system allows administrators to post requirements and manage student clearances, while students can view their requirements and print clearance documents. The application supports role-based access control with separate dashboards for administrators and students, featuring a clean and modern design.

## User Preferences
- Preferred communication style: Simple, everyday language
- Design preference: Modern but simple interface
- Multiple user support: 2 student users and 3 admin users

## Demo Users
### Admin Users (3)
- admin1, admin2, admin3 (password: admin123)

### Student Users (2)  
- 0221-1001 (John Doe, IT Year 3 WMAD Section A, password: student123)
- 0222-1002 (Jane Smith, CS Year 2 Section B, password: student123)

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **Layout Structure**: Base template system with extending child templates for modular design
- **Multiple Templates**: Separate HTML files for login, register, admin dashboard, and student dashboard
- **Styling**: Modern CSS with CSS variables for consistent theming, separate CSS files for each section
- **Client-Side Logic**: JavaScript with AJAX for dynamic interactions and real-time updates
- **Responsive Design**: Mobile-first responsive design with modern UI components

### Backend Architecture
- **Framework**: Flask web framework with session-based authentication
- **Architecture Pattern**: MVC pattern with route handlers, template rendering, and RESTful API endpoints
- **Authentication**: Session-based authentication with password hashing using Werkzeug security
- **User Management**: Role-based access control supporting admin and student user types
- **API Endpoints**: Comprehensive RESTful API for requirements, student management, and clearance processing

### Data Storage
- **Database**: SQLite database with proper relational design
- **Schema Design**: Four main tables: users, requirements, student_requirements, and clearances
- **Data Relationships**: Foreign key relationships ensuring data integrity
- **Storage Location**: Local file-based SQLite database (clearance_system.db)
- **File Uploads**: Support for signature template image uploads

### Key Features
- **Requirements Management**: Admins can add/view semester requirements
- **Student Tracking**: Real-time tracking of student completion status
- **Search & Filter**: Advanced filtering by student number, course, year, major, and section
- **Clearance Processing**: Automated clearance submission when all requirements are completed
- **Printable Clearance**: Professional clearance certificates with signature templates
- **File Upload**: Admin signature template upload functionality

### External Dependencies
- **Flask**: Web framework and template engine
- **SQLite3**: Database engine for data persistence
- **Werkzeug**: Security utilities for password hashing and authentication
- **Static Assets**: Organized CSS and JavaScript files in separate directories
- **File Upload Support**: Built-in support for signature template image uploads

### Recent Changes (September 2025)
- Restructured from single-page application to multi-template Flask application
- Added modern CSS design with improved user experience
- Implemented comprehensive RESTful API endpoints
- Added database-backed user management with predefined demo users
- Enhanced admin dashboard with tabbed interface
- Improved student dashboard with real-time requirement tracking
- Added signature template upload functionality for clearance documents