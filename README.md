# SolarMatch Server

## Project Overview

The SolarMatch server is the backend component of the SolarMatch platform, an AI-powered application for solar suitability analysis and adoption. It provides a robust RESTful API that serves as the backbone for the frontend client, handling business logic, data persistence, and integration with third-party services.

## Features

- **RESTful API:** A comprehensive and well-structured API for all frontend operations.
- **User Management:** Secure user authentication, authorization, and profile management using JWT.
- **Data Analysis:** Asynchronous processing and analysis of geospatial data to generate solar suitability scores and related insights.
- **AI Integration:** Seamless integration with Google's Gemini API to power the "Sunny" conversational AI assistant.
- **Database Management:** Employs SQLAlchemy ORM and Alembic for database schema management and migrations.
- **Installer Marketplace:** Functionality for solar installation companies to manage their service profiles and connect with potential customers.

## Tech Stack

- **Framework:** Flask
- **API:** Flask-RESTful
- **ORM:** SQLAlchemy
- **Database Migrations:** Alembic
- **Authentication:** Flask-JWT-Extended
- **Password Hashing:** Flask-Bcrypt
- **WSGI Server:** Gunicorn
- **Database:** PostgreSQL (production), SQLite (development)
- **AI:** Google Gemini API
- **Cloud Services:** Cloudinary for media management

## Project Structure

```
/solarmatch-server
├── app.py              # Flask application factory and entry point
├── config.py           # Application configuration settings
├── requirements.txt    # Python package dependencies
├── wsgi.py             # WSGI entry point for Gunicorn
├── .env.example        # Example environment variables
├── instance/           # Instance-specific data (e.g., SQLite DB)
│   └── solarmatch.db
├── models/             # SQLAlchemy data models
│   ├── __init__.py
│   ├── user.py
│   ├── analysis.py
│   └── ...
├── routes/             # API route definitions
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── admin_routes.py
│   └── ...
├── sevices/           # Business logic and external service integrations
│   └── gemini_service.py
├── tasks/              # Celery task definitions for background processing
│   └── ...
├── migrations/         # Alembic database migration scripts
│   └── ...
└── utils/              # Utility functions and helpers
    └── ...
```

## Installation and Setup

### Prerequisites

- Python 3.8+
- PostgreSQL or SQLite

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/SolarMatch-Kenya/solarmatch-server.git
    cd solarmatch/solarmatch-server
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Create a `.env` file based on `.env.example` and populate it with the necessary credentials and configuration parameters.

## Running the Application

To start the development server, execute:

```bash
flask run
```

The API will be accessible at `http://127.0.0.1:5000`. For production deployments, use the Gunicorn WSGI server:

```bash
gunicorn wsgi:app
```

## Database Migrations

The application utilizes Alembic for managing database schema migrations.

-   **To apply migrations:**
    ```bash
    flask db upgrade
    ```

-   **To generate a new migration:**
    ```bash
    flask db migrate -m "Descriptive migration message"
    ```

## API Endpoints

The API is organized into modular blueprints within the `routes` directory. Key endpoints include:

-   `/auth`: User authentication (login, registration, token refresh)
-   `/users`: User profile and data management
-   `/analysis`: Solar analysis report generation and retrieval
-   `/installers`: Installer profile and service management
-   `/ai`: Conversational AI endpoints

For a comprehensive list of all available routes and their specifications, please refer to the source code in the `routes` directory.

## Contributing

Contributions are welcome. Please adhere to the existing code style and submit pull requests for any enhancements or bug fixes.
## Authors

- [James Kariuki](https://github.com/chiznox6)
- [Patricia Njuguna](https://github.com/Ms-Njuguna)
- [Ayub Karanja](https://github.com/AyubFoks)

## License

This project is licensed under the [MIT License](https://mit-license.org/).
