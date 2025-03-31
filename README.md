# Course Management System

## Project Description

The Course Management System is a comprehensive web-based application designed to streamline and automate the academic course management process at universities. This system serves as a bridge between students, professors, and administrative staff, providing a centralized platform for course-related operations.

### What Does It Do?

The system provides a robust set of features including:

- **User Authentication & Authorization**
  - Secure login system for students, professors, and administrators
  - Role-based access control
  - Session management for secure operations

- **Course Management**
  - Course creation and modification
  - Enrollment processing
  - Prerequisites tracking and validation
  - Course capacity management
  - Course schedule management

- **Student Features**
  - Course registration and enrollment
  - View enrolled courses
  - Track academic progress
  - Interactive dashboard
  - Prerequisites verification

- **Professor Features**
  - Course creation and management
  - Student enrollment oversight
  - Course materials management
  - Course schedule management

### Why This Tech Stack?

Our technology stack has been carefully chosen to provide a robust, scalable, and maintainable solution:

#### Backend
- **Flask Framework (Python)**
  - Lightweight and flexible
  - Easy to extend
  - Great for RESTful APIs
  - Extensive middleware support
  - Simple integration with SQLAlchemy

- **SQLAlchemy ORM**
  - Object-Relational Mapping for intuitive database operations
  - Database agnostic
  - Powerful query building
  - Transaction management
  - Connection pooling

- **MySQL Database**
  - Robust and reliable
  - ACID compliance
  - Excellent performance for complex queries
  - Strong data integrity
  - Wide community support

#### Frontend
- **HTML5**
  - Semantic markup
  - Modern web standards
  - Cross-browser compatibility

- **CSS3**
  - Responsive design
  - Modern styling capabilities
  - CSS Grid and Flexbox for layouts

- **JavaScript**
  - Dynamic user interface
  - Real-time form validation
  - AJAX for asynchronous operations
  - Enhanced user experience

#### Authentication & Security
- **Flask-Login**
  - Session management
  - User authentication
  - Remember me functionality
  - Login required decorators

- **Flask-Session**
  - Server-side session management
  - Secure session data storage
  - Configurable session lifetime

### Architecture Overview

The application follows a Model-View-Controller (MVC) architecture:

```
├── Models (SQLAlchemy Models)
│   ├── Student
│   ├── Professor
│   ├── Course
│   └── Enrollment
│
├── Views (Flask Templates)
│   ├── Authentication
│   ├── Course Management
│   └── User Dashboard
│
└── Controllers (Flask Routes)
    ├── Authentication
    ├── Course Operations
    └── User Management
```

### Database Design

The system utilizes a relational database with the following core tables:
- Students
- Professors
- Courses
- Enrollments
- Prerequisites
- Departments

Each table is carefully designed with appropriate foreign key relationships and constraints to maintain data integrity.

## System Overview

This system allows for efficient management of university courses, including:
- Student registration and authentication
- Course enrollment and management
- Prerequisites tracking
- Professor information management
- Interactive dashboard for enrolled courses

## Technical Stack

- **Backend Framework**: Flask (Python web framework)
- **Database**: MySQL
- **ORM**: SQLAlchemy (Object-Relational Mapping)
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login
- **Session Management**: Flask-Session

## Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- pip (Python package installer)
- Git (for version control)

## Database Setup

The system uses a MySQL database for data storage. You'll need to:

1. Have MySQL Server 8.0 or higher installed
2. Configure your database connection in `.env` file
3. Initialize the database schema

## Setup Instructions

1. **Clone the Repository**:
```bash
git clone <repository-url>
cd Project
```

2. **Create and Activate Virtual Environment**:

For Windows:
```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
.\env\Scripts\activate
```

For Linux/Mac:
```bash
# Create virtual environment
python3 -m venv env

# Activate virtual environment
source env/bin/activate
```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and update the database configuration:
     ```
     DB_HOST=localhost
     DB_USER=your_username
     DB_PASSWORD=your_password
     DB_NAME=course_management
     ```

5. **Create the Database**:

Connect to MySQL and run:
```sql
CREATE DATABASE course_management;
```

6. **Initialize the Database**:
```bash
# Initialize database schema
python main.py --init-db

# Optional: Load test data
python main.py --load-test-data
```

## Running the Application

1. **Ensure Virtual Environment is Active**:
   - Look for `(env)` at the start of your command prompt
   - If not active, run the activation command from Step 2 of Setup

2. **Start the Application**:
```bash
# Normal mode
python main.py

# With debug enabled
python main.py --debug
```

3. **Access the Application**:
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - Default admin credentials (if using test data):
     - Username: admin
     - Password: admin123

## Development Features

1. **Debug Mode**:
```bash
python main.py --debug
```

2. **Database Operations**:
```bash
# Reset database
python main.py --reset-db

# Load test data
python main.py --load-test-data
```

## Understanding the ORM (Object-Relational Mapping)

This project uses SQLAlchemy ORM, which provides these benefits:
- Write Python code instead of SQL queries
- Automatic handling of database connections
- Object-oriented approach to database operations
- Built-in security features

Example of ORM usage in our code:
```python
# Instead of writing SQL like:
# SELECT * FROM courses WHERE professor_id = 1;

# We write Python code:
courses = Course.query.filter_by(professor_id=1).all()
```

## Project Structure

```
Project/
├── web/                    # Web application package
│   ├── routes/            # URL route definitions
│   │   ├── __init__.py
│   │   ├── auth_routes.py    # Authentication routes
│   │   ├── course_routes.py  # Course management routes
│   │   └── professor_routes.py # Professor management routes
│   ├── templates/         # HTML templates
│   ├── static/           # Static files (CSS, JS, images)
│   ├── models.py         # Database models using SQLAlchemy ORM
│   └── app.py           # Flask application initialization
├── sql_connection.py     # Database connection management
├── schema.sql           # Database schema definition
├── test_data.sql       # Sample data for testing
├── requirements.txt    # Python package dependencies
├── .env               # Environment variables (private)
├── .env.example      # Example environment variables
└── README.md        # This documentation
```

## Support

For additional help:
1. Check the comments in the code
2. Review the SQL schema in `schema.sql`
3. Examine the test data in `test_data.sql`
4. Contact the development team

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is used for educational purposes at Montclair State University. 