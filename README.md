FormForge API
<h2>Introduction</h2>
FormForge API is the backend service powering the FormForge application, a dynamic form builder with a powerful rule engine. This API is responsible for managing form schemas, handling user submissions, and providing data for analytics and integrations.

Built with Python and FastAPI, the project follows the principles of Clean Architecture to ensure a high degree of maintainability, testability, and separation of concerns.

Technology Stack
Framework: FastAPI

Database: PostgreSQL

ORM: SQLAlchemy

Database Migrations: Alembic

Dependency Management: Poetry

Data Validation: Pydantic

Prerequisites
Before you begin, ensure you have the following installed on your local machine:

Python 3.11+

Poetry

A running instance of PostgreSQL

Local Development Setup
Follow these steps to get the development environment running.

1. Clone the Repository
git clone <your-repository-url>
cd FormForge-API

2. Configure Environment Variables
Create a .env file in the root of the project by copying the example file.

cp .env.example .env

Open the newly created .env file and update the DATABASE_URL with your PostgreSQL connection details.

DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database_name>

3. Install Dependencies
Poetry will create a virtual environment and install all necessary packages from the pyproject.toml file.

poetry install

4. Set up the Database
Ensure your PostgreSQL server is running and that the database specified in your .env file exists. The user must have permissions to create tables and schemas.

5. Run Database Migrations
This command will apply all existing migrations and create the necessary tables in your database.

poetry run alembic upgrade head

Running the Application
To start the FastAPI development server, run the following command. The --reload flag enables hot-reloading on code changes.

poetry run uvicorn app.main:app --reload
