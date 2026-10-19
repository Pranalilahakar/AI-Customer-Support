# AI Customer Support & Ticket Management System

An AI-assisted customer support platform for creating and managing support tickets, organizing customer requests, and helping support teams respond more efficiently.

**Live Demo:** [Open the application](https://ai-customer-support-4vjv-e8mva44ba-pranalilahakars-projects.vercel.app/)

**Backend API:** [FastAPI service](https://ai-customer-support-swart-alpha.vercel.app/)

**API Documentation:** [Explore the API with Swagger UI](https://ai-customer-support-swart-alpha.vercel.app/docs)

**GitHub Repository:** [AI-Customer-Support](https://github.com/Pranalilahakar/AI-Customer-Support)

---

## Overview

The AI Customer Support & Ticket Management System is a full-stack web application that combines a React frontend, FastAPI backend, PostgreSQL database, and machine-learning-assisted ticket categorization.

Customers can register, log in, create support tickets, and track their requests. Support agents can work with tickets, while administrators have access to role-specific functionality according to the application's authorization rules.

The application also includes AI-assisted ticket summaries, suggested replies, knowledge-base search, and explainable priority recommendations.

The project demonstrates full-stack development, REST API design, database integration, authentication, role-based access control, machine learning, automated testing, Docker-based local development, and cloud deployment.

## Live Application

| Component | URL |
|---|---|
| Frontend | [Open the live application](https://ai-customer-support-4vjv-e8mva44ba-pranalilahakars-projects.vercel.app/) |
| Backend API | [Open API](https://ai-customer-support-swart-alpha.vercel.app/) |
| API health check | [Check backend health](https://ai-customer-support-swart-alpha.vercel.app/health) |
| Interactive API documentation | [Open Swagger UI](https://ai-customer-support-swart-alpha.vercel.app/docs) |
| Source code | [View repository](https://github.com/Pranalilahakar/AI-Customer-Support) |

The frontend and backend are deployed separately. The backend connects to the hosted PostgreSQL database on Supabase.

> **Note:** Use the production domain shown in your Vercel project settings if your frontend's deployment URL changes.

## Features

- **User authentication:** Account registration and login using password hashing and JWT authentication.
- **Role-based access control:** Customer, agent, and administrator roles.
- **Ticket management:** Create, view, and track customer support tickets.
- **Ticket workflow:** Support-team ticket handling, assignment, and status management where permitted by the user's role.
- **AI ticket categorization:** Machine-learning predictions based on ticket text.
- **Ticket summaries:** Concise summaries to help support staff understand issues.
- **Suggested replies:** Draft responses for agents to review and edit.
- **Knowledge-base search:** Keyword-based retrieval of relevant support guidance.
- **Priority recommendations:** Explainable, rule-based suggestions to help identify important tickets.
- **Persistent storage:** PostgreSQL database integration.
- **REST API:** FastAPI endpoints for application functionality.
- **Interactive frontend:** React and Vite.
- **API documentation:** Interactive Swagger UI.
- **Automated testing:** Backend tests using pytest.
- **Docker support:** Docker Compose for local development.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Database | PostgreSQL, Supabase |
| ORM | SQLAlchemy |
| Authentication | JWT, password hashing |
| Machine learning | scikit-learn, TF-IDF, Logistic Regression, joblib |
| AI-assisted workflows | Python-based summaries, suggested replies, keyword retrieval, priority rules |
| Testing | pytest, FastAPI TestClient |
| Local containers | Docker, Docker Compose |
| Cloud deployment | Vercel |
| Version control | Git, GitHub |

## Architecture

```text
                  Customer / Agent / Admin
                            |
                            v
                     React Frontend
                       (Vercel)
                            |
                       HTTP / API
                            |
                            v
                     FastAPI Backend
                       (Vercel)
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
        Authentication   Ticket       AI-Assisted
        and Authorization Services     Services
              |             |             |
              +-------------+-------------+
                            |
                            v
                    PostgreSQL Database
                       (Supabase)
```

The frontend communicates with the backend through HTTP requests. The backend handles authentication, authorization, ticket operations, and AI-assisted features. Supabase provides hosted PostgreSQL persistence.

## User Roles

### Customer
- Register and log in.
- Create support tickets.
- View and track tickets available to their account.
- Use customer-facing functionality provided by the application.

### Support Agent
- Access permitted support tickets.
- Work with ticket status and assignment functionality where available.
- Use AI-assisted summaries and suggested replies to help with support responses.

### Administrator
- Access administrator-specific functionality permitted by the application.
- Manage or inspect resources according to the implemented permissions.

**Security note:** Public registration should create customer accounts only. Agent and administrator roles should be assigned through a trusted administrative process, not selected freely during public registration.

## AI Features and Limitations

### 1. Ticket category prediction

A scikit-learn text-classification pipeline predicts one of four ticket categories:

- `account_access`
- `billing`
- `general_inquiry`
- `technical_issue`

The classifier uses TF-IDF text features and Logistic Regression.

### 2. Ticket summaries

The application produces concise summaries of ticket information and comments to help support staff understand the issue more quickly.

### 3. Suggested replies

The application provides draft reply suggestions based on ticket information and comments. Agents should review and edit suggestions before sending responses.

### 4. Knowledge-base search

The knowledge-search feature retrieves relevant sections from local Markdown support-guidance files using keyword matching.

This is a lightweight retrieval implementation, **not a full LLM-powered Retrieval-Augmented Generation (RAG) system**. The included support guidance is demonstration content and should not be treated as verified company policy.

### 5. Priority recommendations

Rule-based logic recommends a ticket priority and provides an explanation based on ticket content and configured rules.

These recommendations assist human decision-making. They should not be treated as definitive assessments.

### Model evaluation

The previously recorded classifier evaluation used 48 examples: 36 training examples and 12 holdout test examples. The recorded holdout accuracy was **91.7% (11 of 12 examples)**.

This is an initial prototype result, not evidence of production-level model reliability. The dataset and holdout set are small, so the result may not generalize to real-world customer support data.

If maintained in the repository, the detailed evaluation report is available at `docs/ml-evaluation.md`.

## Local Development with Docker

The deployed application is available online. You can also run the project locally for development and testing.

### Prerequisites

Install:

- Git
- Docker Desktop with Docker Compose
- Python 3.12 and Node.js 22, or compatible supported versions, if developing outside Docker

### 1. Clone the repository

```powershell
git clone https://github.com/Pranalilahakar/AI-Customer-Support.git
cd AI-Customer-Support
```

### 2. Configure environment variables

Create the environment files expected by your local Docker Compose and backend configuration.

Example root `.env`:

```dotenv
DB_USER=your_database_user
DB_PASSWORD=your_strong_database_password
DB_NAME=customer_support_db
```

Example `backend/.env`:

```dotenv
DB_USER=your_database_user
DB_PASSWORD=your_strong_database_password
DB_HOST=db
DB_PORT=5432
DB_NAME=customer_support_db
JWT_SECRET=your_long_random_secret
```

Replace all example values with your own local credentials. These examples are for local development, not production configuration.

**Security:** Never commit real passwords, JWT secrets, production database credentials, or `.env` files to GitHub. Configure production secrets through the hosting platform's environment-variable settings.

### 3. Start the services

```powershell
docker compose up --build -d
```

Check service status:

```powershell
docker compose ps
```

### 4. Initialize database tables when needed

For a new local database, initialize the SQLAlchemy tables using the project's model definitions:

```powershell
docker compose exec backend python -c "from app.db.base import Base; from app.db.database import engine; from app.models.user import User; from app.models.ticket import Ticket; from app.models.comment import TicketComment; Base.metadata.create_all(bind=engine); print('Database tables initialized')"
```

Run this only when the database needs initialization and the backend can connect successfully. This development approach does not replace a versioned migration system such as Alembic.

### 5. Open the local application

| Service | URL |
|---|---|
| Frontend | [http://localhost:8080](http://localhost:8080) |
| Backend API | [http://localhost:8000](http://localhost:8000) |
| API documentation | [http://localhost:8000/docs](http://localhost:8000/docs) |

The local URLs depend on the port mappings in your Docker Compose configuration.

### 6. Stop the services

```powershell
docker compose down
```

This stops the containers without intentionally deleting the named database volume.

**Warning:** `docker compose down -v` removes associated named volumes and can permanently delete your local database data. Do not run it if you need to preserve that data.

## Running Backend Tests

From the repository root, run:

```powershell
python -m pytest .\backend\tests -q
```

The previously recorded local test run completed with:

```text
36 passed, 1 warning
```

This is a historical test result; run the tests again to verify the current code.

The test configuration may require a dedicated PostgreSQL test database and appropriate connection settings. Test fixtures can create or drop tables and modify test records, so **never point tests at the production database or a database containing important personal data**.

## Building the Frontend

From the repository root:

```powershell
npm --prefix .\frontend ci
npm --prefix .\frontend run build
```

The production frontend assets are generated in `frontend/dist/`.

## Deployment Configuration

The current deployment uses Vercel for the frontend and backend, with Supabase PostgreSQL for persistent storage.

### Frontend environment variable

Configure the following variable in the frontend Vercel project:

```dotenv
VITE_API_URL=https://ai-customer-support-swart-alpha.vercel.app
```

The frontend uses this value to communicate with the deployed API.

### Backend environment variables

Configure the required database and authentication settings in the backend Vercel project's environment variables:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
JWT_SECRET
FRONTEND_ORIGIN
```

Use the actual Supabase connection details and a strong, private JWT secret. Set `FRONTEND_ORIGIN` to the exact production frontend origin.

Do not put real values for database passwords or JWT secrets in this README or commit them to the repository.

### Deployment checks

After deployment:

1. Open the frontend and verify that the application loads.
2. Visit the backend health endpoint.
3. Register or log in with a test account.
4. Create a test ticket and verify that it persists.
5. Verify customer, agent, and administrator permissions using separate accounts.
6. Test AI-assisted functionality through the deployed application.
7. Review deployment logs if an API request fails.

## Project Structure

```text
AI-Customer-Support/
├── .github/
│   └── workflows/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── models/
│   │   │   ├── assist.py
│   │   │   ├── knowledge.py
│   │   │   ├── priority.py
│   │   │   ├── predictor.py
│   │   └── api/
│   │   ├── db/
│   │   ├── models/
│   │   └── main.py
│   ├── data/
│   │   ├── knowledge_base/
│   │   └── ticket_categories.csv
│   ├── tests/
│   ├── index.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── package-lock.json
├── docs/
├── compose.yaml
├── .dockerignore
├── .gitignore
└── README.md
```

This is an overview of the expected organization. Confirm the actual files in the repository before relying on optional directories or files shown here.

## Key Learning Outcomes

- Building REST APIs using FastAPI and Python.
- Designing relational database models with SQLAlchemy.
- Implementing JWT authentication and role-based authorization.
- Connecting a React frontend to a backend API.
- Integrating a machine-learning text classifier.
- Evaluating a classifier and documenting its limitations.
- Developing AI-assisted support workflows.
- Using PostgreSQL for persistent data storage.
- Containerizing services with Docker Compose.
- Writing and running automated backend tests.
- Deploying a full-stack application to cloud services.
- Managing project code with Git and GitHub.

## Future Improvements

- Expand the training dataset with more representative support tickets.
- Improve model evaluation with cross-validation and larger test datasets.
- Add database migrations using Alembic.
- Expand automated CI and end-to-end testing.
- Improve production logging, monitoring, and error handling.
- Strengthen security testing and deployment hardening.
- Add ticket analytics and support-team reporting.
- Consider semantic search and an LLM-powered RAG system using approved knowledge sources.

## Author

**Pranali Lahakar**

GitHub: [Pranalilahakar](https://github.com/Pranalilahakar)

## License

No license has been specified. Add a license file if you intend to define how others may use, modify, and distribute this project.
