# Course Management System

A web-based course management system built with Flask and SQLAlchemy.

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- pip (Python package installer)

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd Project
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv env
.\env\Scripts\activate

# Linux/Mac
python3 -m venv env
source env/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the database credentials and other variables in `.env`

5. Create the database:
```sql
CREATE DATABASE course_management;
```

6. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Running the Application

1. Make sure your virtual environment is activated

2. Run the Flask application:
```bash
flask run
```

3. Access the application at `http://localhost:5000`

## Project Structure

```
Project/
├── web/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── course_routes.py
│   │   └── professor_routes.py
│   ├── templates/
│   ├── static/
│   ├── models.py
│   ├── config.py
│   └── app.py
├── requirements.txt
├── .env
└── README.md
```

## Features

- Student authentication (login/register)
- Course listing and search
- Course enrollment and withdrawal
- Prerequisites viewing
- Professor information
- Dashboard for enrolled courses

## Development

To run the application in development mode:
```bash
flask run --debug
```

## Testing

To run tests:
```bash
flask test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 