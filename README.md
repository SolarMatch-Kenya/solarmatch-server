# SolarMatch Server

This is the backend for the SolarMatch application. SolarMatch-KE is an AI-Powered Solar Suitability and Adoption Platform.
We help homeowners, businesses, and communities transition to clean energy through data-driven insights.

We are empowering Kenya to go solar — one rooftop at a time.

It provides a RESTful API to support the frontend application, handling user authentication, data processing, and interactions with the database and AI services.

## Features

- **RESTful API:** A well-structured API for all frontend operations.
- **User Management:** Secure user registration, login, and profile management.
- **Data Analysis:** Processes and analyzes data to provide solar suitability scores and other insights.
- **AI Integration:** Connects with Google's Gemini API to power the "Sunny" chatbot.
- **Database Management:** Uses SQLAlchemy and Alembic for database operations and migrations.
- **Installer Management:** Functionality for solar installers to manage their profiles and connect with homeowners.

## Tech Stack

- **Flask:** A lightweight WSGI web application framework in Python.
- **Flask-RESTful:** An extension for Flask that adds support for quickly building REST APIs.
- **SQLAlchemy:** A SQL toolkit and Object-Relational Mapper (ORM) for Python.
- **Alembic:** A lightweight database migration tool for usage with the SQLAlchemy.
- **Flask-JWT-Extended:** An extension for Flask that adds support for JWTs.
- **Flask-Bcrypt:** A Flask extension for hashing passwords with Bcrypt.
- **Gunicorn:** A Python WSGI HTTP Server for UNIX.
- **PostgreSQL/SQLite:** Relational databases for data storage.
- **Google Gemini API:** For generative AI capabilities.
- **Cloudinary:** For cloud-based image and video management.

## Getting Started

### Prerequisites

- Python 3.8+ and pip installed on your machine.
- A PostgreSQL or SQLite database.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SolarMatch-Kenya/solarmatch-server.git
   ```
2. Navigate to the server directory:
   ```bash
   cd solarmatch/solarmatch-server
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
4. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env` file and add the necessary environment variables.
### Running the Application

To start the development server, run:

```bash
flask run
```

The API will be available at `http://127.0.0.1:5000`.

## API Endpoints

The API provides the following main endpoints:

- `/auth`: User authentication (login, registration).
- `/users`: User profile management.
- `/analysis`: Solar analysis and suitability scores.
- `/installers`: Installer profiles and marketplace.
- `/ai`: AI-powered chatbot.

For a detailed list of all endpoints, please refer to the source code in the `routes` directory.

## Database

The application uses SQLAlchemy as an ORM and Alembic for database migrations. To apply the latest migrations, run:

```bash
flask db upgrade
```

To create a new migration, run:

```bash
flask db migrate -m "Your migration message"
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## Authors

- [James Kariuki](https://github.com/chiznox6)
- [Patricia Njuguna](https://github.com/Ms-Njuguna)
- [Ayub Karanja](https://github.com/AyubFoks)

## License

This project is licensed under the [MIT License](https://mit-license.org/).
