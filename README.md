# AI Customer Support & Ticket Management System

An AI-powered customer support application that helps customers create and track support tickets while enabling support teams to manage, categorize, prioritize, and respond to requests efficiently.

## Overview

The **AI Customer Support & Ticket Management System** combines a React frontend, FastAPI backend, PostgreSQL database, and machine-learning-based ticket categorization in one application.

The project demonstrates REST API development, database integration, authentication, role-based authorization, AI-assisted support workflows, automated testing, and Docker-based deployment.

In addition to ticket category prediction, the application provides ticket summaries, suggested reply drafts, knowledge-base search, and explainable priority recommendations.

## Features

- **User authentication:** Register and log in using password hashing and JWT authentication.
- **Role-based access control:** Apply different permissions for customers, support agents, and administrators.
- **Ticket management:** Create, view, track, and manage customer support tickets.
- **Ticket assignment and status management:** Support ticket workflows for the support team.
- **AI ticket categorization:** Predict a suitable category from ticket text using a trained machine-learning classifier.
- **Ticket summaries:** Generate concise summaries of ticket information and comments.
- **Suggested replies:** Provide draft responses to help agents respond to customer requests.
- **Knowledge-base search:** Retrieve relevant sections from local support guidance using keyword-based matching.
- **Priority recommendations:** Provide explainable priority suggestions using rules and ticket content, with human review required.
- **PostgreSQL persistence:** Store application data in a relational database.
- **REST API:** Expose backend functionality through FastAPI.
- **Interactive frontend:** Provide a React-based user interface.
- **Docker support:** Run the frontend, backend, and database using Docker Compose.
- **API documentation:** Explore available endpoints through FastAPI's Swagger UI.
- **Automated tests:** Test backend functionality with pytest.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy |
| Authentication | JWT, password hashing |
| Machine Learning | scikit-learn, TF-IDF, Logistic Regression, joblib |
| AI-assisted workflows | Python-based summaries, reply templates, keyword-based knowledge retrieval, rule-based priority recommendations |
| API Testing | pytest, FastAPI TestClient |
| Frontend Build | npm, Vite |
| Deployment | Docker, Docker Compose, Nginx |
| Version Control | Git, GitHub |
| CI | GitHub Actions workflow, if configured in `.github/workflows/ci.yml` |

## Architecture

```text
                  Customer / Support Agent / Admin
                              |
                              v
                       React Frontend
                        (Nginx server)
                              |
                          HTTP / API
                              |
                              v
                        FastAPI Backend
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
       Authentication    Ticket Services   AI Services
             |                |                |
             +----------------+----------------+
                              |
                              v
                          PostgreSQL

AI Services:
- Ticket category prediction
- Ticket summaries
- Suggested reply drafts
- Knowledge-base search
- Explainable priority recommendations
```

The React frontend communicates with the FastAPI backend over HTTP. The backend handles authentication, authorization, ticket operations, and AI-assisted workflows. PostgreSQL stores application data, while the category classifier and support guidance provide additional assistance to the support team.

## AI Features and Limitations

### 1. Ticket category prediction

The project uses a scikit-learn text-classification pipeline to recommend one of four categories:

- `account_access`
- `billing`
- `general_inquiry`
- `technical_issue`

The model uses text features generated through TF-IDF and a Logistic Regression classifier.

The model is intended to assist categorization, not replace human judgment.

### 2. Ticket summaries

The application provides a concise summary of ticket information and comments to help support staff understand the issue more quickly.

### 3. Suggested replies

The application generates draft reply suggestions based on ticket information and comments. These are suggestions for an agent to review and edit, not automatically sent messages.

### 4. Knowledge-base search

The knowledge-search feature searches local Markdown support-guidance files and ranks relevant sections using keyword overlap.

This is a lightweight retrieval implementation. It is **not a full LLM-powered Retrieval-Augmented Generation (RAG) system** and does not independently verify whether retrieved guidance represents official company policy.

The included support guidance is demonstration content, not an official policy document.

### 5. Priority recommendations

The application uses explainable keyword-based rules to recommend a ticket priority and provide a reason for the recommendation.

The recommendation does not automatically change the ticket's stored priority. A human should review the result before taking action.

### Model evaluation

The current classifier was evaluated using a small dataset of 48 examples, with 36 training examples and 12 holdout test examples.

The recorded holdout accuracy was **91.7% (11 of 12 examples)**. This is an initial prototype result, not evidence of production-level reliability. The small dataset and holdout set limit how confidently the metrics can be generalized.

The detailed evaluation report is intended to be maintained at `docs/ml-evaluation.md`.

## Prerequisites

To run the complete application with Docker, install:

- Docker Desktop with Docker Compose
- Git
- A terminal such as PowerShell

For local development and testing, also install Python 3.12 and Node.js 22 or a compatible supported version.

## Run with Docker

### 1. Clone the repository

```bash
git clone https://github.com/Pranalilahakar/AI-Customer-Support.git
cd AI-Customer-Support
```

### 2. Configure environment variables

Create a root `.env` file for the database settings referenced by Docker Compose:

```dotenv
DB_USER=your_database_user
DB_PASSWORD=your_strong_database_password
DB_NAME=customer_support_db
```

Create `backend/.env` with the database settings and backend authentication configuration:

```dotenv
DB_USER=your_database_user
DB_PASSWORD=your_strong_database_password
DB_HOST=db
DB_PORT=5432
DB_NAME=customer_support_db
JWT_SECRET=your_long_random_secret
```

Replace the example values with your own. Use a strong, unique JWT secret and secure database credentials.

**Security:** Never commit real passwords, JWT secrets, `.env` files, or other sensitive credentials to GitHub. The repository's `.gitignore` is configured to ignore environment files.

### 3. Build and start the services

```powershell
docker compose up --build -d
```

Check the service status:

```powershell
docker compose ps
```

Wait until PostgreSQL is healthy before initializing the database.

### 4. Initialize the database tables

For a new database, initialize the SQLAlchemy tables using:

```powershell
docker compose exec backend python -c "from app.db.base import Base; from app.db.database import engine; from app.models.user import User; from app.models.ticket import Ticket; from app.models.comment import TicketComment; Base.metadata.create_all(bind=engine); print('Database tables initialized')"
```

This creates tables for the imported models. Run it after the database is healthy and the backend can connect to PostgreSQL.

This is a development initialization approach, not a substitute for a versioned database migration system. Database migrations with Alembic remain a useful future improvement.

### 5. Open the application

| Service | URL |
|---|---|
| Frontend | http://localhost:8080 |
| Backend API documentation | http://localhost:8000/docs |

Register an account, log in, create a support ticket, and explore the ticket-management and AI-assisted features available to your account role.

### 6. Stop the services

```powershell
docker compose down
```

This stops and removes the containers while preserving the named PostgreSQL volume.

To remove the containers and permanently delete the Docker database volume, `docker compose down -v` can be used. **Do not use this command if you need to retain your database data.**

## Run Backend Tests

Activate the project's Python virtual environment and run the tests from the repository root:

```powershell
python -m pytest .\backend\tests -q
```

The latest recorded local test run completed successfully:

```text
36 passed, 1 warning
```

The warning concerns the Starlette/httpx test-client compatibility deprecation. It should be reviewed as part of dependency maintenance.

### Database requirements for tests

The test configuration uses a dedicated PostgreSQL database named `customer_support_test_db`. The database must be available, and the test environment must have the correct connection settings before running the tests.

**Important:** The test fixtures create and drop tables and delete test records. Configure the tests to use only the dedicated test database, never a database containing production or personal data.

## Build the Frontend

From the repository root:

```powershell
npm --prefix .\frontend ci
npm --prefix .\frontend run build
```

The build creates production assets in `frontend/dist/`.

The latest recorded frontend production build completed successfully with Vite.

## API Documentation

When the backend is running, open:

http://localhost:8000/docs

FastAPI's interactive Swagger UI allows you to inspect available routes, review request and response schemas, and test supported API requests.

Access to individual endpoints depends on the endpoint's authentication and authorization requirements.

## Project Structure

```text
AI-Customer-Support/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── models/
│   │   │   ├── assist.py
│   │   │   ├── knowledge.py
│   │   │   ├── priority.py
│   │   │   ├── predictor.py
│   │   │   └── train_classifier.py
│   │   ├── api/
│   │   ├── db/
│   │   ├── models/
│   │   └── main.py
│   ├── data/
│   │   ├── knowledge_base/
│   │   └── ticket_categories.csv
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── docs/
│   └── ml-evaluation.md
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── package-lock.json
├── .dockerignore
├── .gitignore
├── compose.yaml
└── README.md
```

The structure above describes the intended project organization. Some documentation and CI files may need to be created before all listed paths exist in the repository.

## Key Learning Outcomes

- Building REST APIs with FastAPI and Python.
- Designing relational database models with SQLAlchemy.
- Implementing JWT authentication and role-based authorization.
- Integrating a machine-learning text classifier into an application.
- Evaluating a classification model and documenting its limitations.
- Building ticket summaries and suggested reply drafts.
- Implementing keyword-based knowledge retrieval and explainable priority rules.
- Developing a React frontend that communicates with backend APIs.
- Containerizing a multi-service application with Docker Compose.
- Testing backend functionality with pytest.
- Managing source code and version history with Git and GitHub.
- Preparing automated backend and frontend checks with CI.

## Future Enhancements

- Expand the training dataset with more representative, correctly labelled support tickets.
- Improve evaluation using cross-validation and a larger holdout dataset.
- Add database migrations with Alembic.
- Expand automated CI checks and maintain dependency versions.
- Add stronger logging, monitoring, and production deployment hardening.
- Improve ticket analytics and support-team reporting.
- Consider semantic retrieval and an LLM-based RAG architecture using approved knowledge sources.
- Deploy the application to a cloud hosting platform.
- Add additional security testing and end-to-end frontend/API tests.

## Author

**Pranali Lahakar**

GitHub: https://github.com/Pranalilahakar

## License

No license has been specified yet. Add a license if you intend to define permissions for others to use, modify, and distribute this project.
