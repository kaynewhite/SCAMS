# Clearance System

## Overview
A modern Flask-based web application for managing student clearance requirements in an academic institution. The system allows administrators to post requirements and manage student clearances, while students can view their requirements and download clearance documents. The application supports role-based access control with separate dashboards for administrators and students, featuring a clean and modern design.

## User Preferences
- Preferred communication style: Simple, everyday language
- Design preference: Modern but simple interface
- Single admin user system with student registration capability

## System Users
### Admin User
- Username: ronronadmin
- Password: ronron1234
- Role: System Administrator with full access

### Student Users  
- Students register using their student number
- Password: Same as their student number
- Registration format: 022*-**** (e.g., 0221-1001)

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **Layout Structure**: Base template system with extending child templates for modular design
- **Multiple Templates**: Separate HTML files for login, register, admin dashboard, student dashboard
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
- **Schema Design**: Five main tables: users, requirements, student_requirements, clearances, and submitted_clearances
- **Data Relationships**: Foreign key relationships ensuring data integrity
- **Storage Location**: Local file-based SQLite database (clearance_system.db)
- **File Uploads**: Support for signature template image uploads with UUID naming

### Key Features
- **Requirements Management**: Admins can add/delete semester requirements
- **Student Tracking**: Real-time tracking of student completion status
- **Search & Filter**: Advanced filtering by student number, course, year, major, and section with improved UI
- **Clearance Processing**: Automated clearance submission when all requirements are completed
- **Downloadable Clearance**: Professional PDF clearance certificates with student info, completion date, and signature templates
- **File Upload**: Admin signature template upload functionality
- **Archive System**: Submitted clearances moved to separate table for easy management

### External Dependencies
- **Flask**: Web framework and template engine
- **SQLite3**: Database engine for data persistence
- **Werkzeug**: Security utilities for password hashing and authentication
- **ReportLab**: PDF generation for downloadable clearance certificates
- **Static Assets**: Organized CSS and JavaScript files in separate directories
- **File Upload Support**: Built-in support for signature template image uploads

### Recent Changes (September 2025)
- Restructured from single-page application to multi-template Flask application
- Simplified user system to single admin and student registration
- Added PDF download functionality for clearance certificates
- Implemented delete functionality for requirements and signature templates
- Created separate archive table for submitted clearances
- Enhanced search and filter interface with improved responsive design
- Added comprehensive error handling and user feedback
- Improved security with proper password hashing and session management
- Modern CSS grid layout for better organization and mobile responsiveness
- Removed dark mode feature for simplified interface
- Added undo submission functionality for individual students
- Implemented clear all requirements button with automatic submission reversion
- Enhanced student notification system with color-coded status messages
- Added bulk CSV download for all completed clearances
- Improved login interface with proper student number format guidance