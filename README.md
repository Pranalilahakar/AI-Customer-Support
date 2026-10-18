# AI Customer Support & Ticket Management System

An AI-powered customer support application that helps customers create and track support tickets while enabling support teams to manage, categorize, and prioritize requests.

## Overview

The **AI Customer Support & Ticket Management System** combines a React frontend, FastAPI backend, PostgreSQL database, and machine-learning-based ticket category prediction in one application.

The project demonstrates REST API development, database integration, authentication, role-based access, AI integration, and Docker-based deployment.

## Features

- **User authentication:** Register and log in securely using password hashing and JWT authentication.
- **Ticket management:** Create, view, and track customer support tickets.
- **Role-based access:** Separate customer and support-related permissions.
- **AI ticket categorization:** Predict a suitable category from ticket text.
- **Ticket persistence:** Store application data in PostgreSQL.
- **REST API:** Provide backend endpoints through FastAPI.
- **Interactive frontend:** React-based user interface for interacting with the support system.
- **Containerization:** Run the frontend, backend, and database with Docker Compose.
- **API documentation:** Explore available endpoints through FastAPI's Swagger UI.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT, password hashing |
| Machine Learning | scikit-learn, joblib |
| API Testing | pytest, FastAPI TestClient |
| Deployment | Docker, Docker Compose, Nginx |
| Version Control | Git, GitHub |

## Architecture

```text
                Customer / Support Agent
                          |
                          v
                React Frontend
                  (Nginx server)
                          |
                     HTTP / API
                          |
                          v
                   FastAPI Backend
                    /     |     \
                   /      |      \
             Authentication |  AI Category
                   |        |   Prediction
                   v        v
                  PostgreSQL
```

The frontend communicates with the FastAPI backend through HTTP requests. The backend handles authentication, ticket operations, and AI category prediction, while PostgreSQL stores application data.

## Run with Docker

### Prerequisites

- Docker Desktop installed and running
- Git
- A terminal such as PowerShell

### 1. Clone the repository

```bash
git clone https://github.com/Pranalilahakar/AI-Customer-Support.git
cd AI-Customer-Support
```

### 2. Configure environment variables

Create a root `.env` file containing the database settings used by Docker Compose:

```dotenv
DB_USER=your_database_user
DB_PASSWORD=your_strong_database_password
DB_NAME=customer_support_db
```

Create `backend/.env` with the same database credentials and the additional backend settings:

```dotenv
DB_USER=your_database_user
DB_PASSWORD=your_strong_database_password
DB_HOST=db
DB_PORT=5432
DB_NAME=customer_support_db
JWT_SECRET=your_long_random_secret
```

Replace all example values with your own. Never commit real passwords, JWT secrets, or environment files to GitHub.

### 3. Build and start the services

```bash
docker compose up --build -d
```

Check the running containers:

```bash
docker compose ps
```

### 4. Initialize the database tables

For a new database, initialize the SQLAlchemy tables using:

```bash
docker compose exec backend python -c "from app.db.base import Base; from app.db.database import engine; from app.models.user import User; from app.models.ticket import Ticket; from app.models.comment import TicketComment; Base.metadata.create_all(bind=engine); print('Database tables initialized')"
```

This creates the tables defined by the imported models. Run it after the database is healthy and the backend can connect to PostgreSQL.

### 5. Open the application

| Service | URL |
|---|---|
| Frontend | http://localhost:8080 |
| Backend API documentation | http://localhost:8000/docs |

Register a customer account, log in, create a support ticket, and test the ticket categorization feature.

### Stop the services

```bash
docker compose down
```

This stops and removes the containers but preserves the named PostgreSQL volume.

To remove containers **and permanently delete the Docker database volume**, Docker's `down -v` command can be used. Do not use it if you need to retain your data.

## Run Tests

Activate your Python virtual environment and run the backend tests:

```bash
python -m pytest
```

The project has previously passed **25 backend tests** in the development environment.

Build the frontend:

```bash
cd frontend
npm run build
```

## API Documentation

FastAPI provides interactive API documentation when the backend is running:

http://localhost:8000/docs

Use the documentation to inspect available routes and test supported API requests.

## Project Structure

```text
AI-Customer-Support/
├── backend/
│   ├── app/
│   │   ├── db/
│   │   ├── models/
│   │   ├── routes/
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── .dockerignore
├── compose.yaml
└── README.md
```

## Key Learning Outcomes

- Building REST APIs with FastAPI and Python
- Designing relational database models with SQLAlchemy
- Implementing JWT authentication and role-based authorization
- Integrating machine-learning predictions into an application
- Developing a React frontend that communicates with backend APIs
- Containerizing a multi-service application with Docker Compose
- Testing backend functionality with pytest
- Managing source code and version history with Git and GitHub

## Future Enhancements

- Add database migrations with Alembic.
- Add automated CI/CD workflows using GitHub Actions.
- Deploy the application to a cloud hosting platform.
- Add automated API integration tests.
- Improve ticket analytics and support-team reporting.
- Add monitoring, logging, and production deployment hardening.

## Author

**Pranali Lahakar**

GitHub: [Pranalilahakar](https://github.com/Pranalilahakar)

## License

No license has been specified yet. Add a license if you intend to define permissions for others to use, modify, and distribute this project.
