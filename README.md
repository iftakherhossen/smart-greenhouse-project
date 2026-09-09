\# Smart Greenhouse



A three-tier Smart Greenhouse application developed as part of the course project.



The project is currently in the \*\*foundation / Phase 1\*\* stage. The goal of this phase is to establish a clean and runnable development environment consisting of:



\* Python / FastAPI backend

\* PostgreSQL database

\* Alembic database migration tooling

\* React + TypeScript frontend

\* React Router

\* Tailwind CSS v4

\* Docker-based PostgreSQL development environment



The actual greenhouse business functionality will be implemented in later phases.



\---



\## 1. Project Structure



```text

smart-greenhouse/

├── backend/

│   ├── .venv/

│   ├── pyproject.toml

│   ├── alembic.ini

│   ├── alembic/

│   │   └── versions/

│   │       └── 001\_baseline.py

│   └── src/

│       ├── main.py

│       ├── domain/

│       ├── application/

│       ├── infrastructure/

│       │   ├── settings.py

│       │   └── db.py

│       └── interfaces/

│           └── api/

│               └── health.py

│

├── frontend/

│   ├── src/

│   │   ├── App.tsx

│   │   ├── main.tsx

│   │   └── index.css

│   ├── package.json

│   ├── vite.config.ts

│   └── ...

│

├── .env

├── .env.example

├── .gitignore

├── docker-compose.yml

└── README.md

```



\---



\## 2. Prerequisites



Install the following software before starting the project:



\* Python 3.11 or newer

\* Node.js

\* npm

\* Docker Desktop

\* Git



Check the installed versions:



```powershell

python --version

node --version

npm --version

docker --version

git --version

```



\---



\## 3. First-Time Setup



Clone or obtain the project and enter the project directory:



```powershell

cd "C:\\Smart Greenhouse Project\\smart-greenhouse"

```



\### Environment variables



Create the real `.env` file from `.env.example`.



The development PostgreSQL container uses host port `5433` because port `5432` is already used by another PostgreSQL installation.



Example:



```env

POSTGRES\_USER=greenhouse

POSTGRES\_PASSWORD=greenhouse

POSTGRES\_DB=greenhouse

POSTGRES\_HOST=localhost

POSTGRES\_PORT=5433



DATABASE\_URL=postgresql+psycopg://greenhouse:greenhouse@localhost:5433/greenhouse



API\_HOST=0.0.0.0

API\_PORT=8000

CORS\_ORIGINS=http://localhost:5173

```



\---



\## 4. PostgreSQL



PostgreSQL runs inside Docker.



Start the database:



```powershell

docker compose up -d

```



Check the container:



```powershell

docker compose ps

```



The PostgreSQL container should show a healthy status.



The database is available from the host at:



```text

localhost:5433

```



Local development database:



```text

Database: greenhouse

User: greenhouse

Password: greenhouse

Host: localhost

Port: 5433

```



The database uses a Docker volume so that PostgreSQL data persists between container restarts.



\---



\## 5. Backend



The backend uses:



\* Python

\* FastAPI

\* Uvicorn

\* SQLAlchemy

\* Psycopg

\* Pydantic Settings

\* Scalar API documentation



\### Create and activate the virtual environment



From the `backend` directory:



```powershell

cd backend

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



Install the project dependencies:



```powershell

pip install -e .

```



\### Start the backend



From the `backend` directory:



```powershell

uvicorn src.main:app --reload --port 8000

```



The API runs at:



```text

http://localhost:8000

```



\---



\## 6. Alembic



Alembic is used for database migration management.



The current Phase 1 migration is an intentionally empty baseline migration.



Run the migrations with:



```powershell

cd backend

.\\.venv\\Scripts\\Activate.ps1

alembic upgrade head

```



Check the current migration:



```powershell

alembic current

```



The baseline migration does not create business tables yet.



At this stage the PostgreSQL database contains:



```text

alembic\_version

```



Business tables will be introduced in later phases.



\---



\## 7. Frontend



The frontend uses:



\* Vite

\* React

\* TypeScript

\* React Router

\* Tailwind CSS v4



Install dependencies:



```powershell

cd frontend

npm install

```



Start the development server:



```powershell

npm run dev

```



The frontend runs at:



```text

http://localhost:5173

```



\### Production build



To verify the frontend production build:



```powershell

npm run build

```



\---



\## 8. Daily Startup



The intended development workflow uses three terminals.



\### Terminal 1 — PostgreSQL



From the project root:



```powershell

docker compose up -d

```



Check the database:



```powershell

docker compose ps

```



\---



\### Terminal 2 — Backend



From the project root:



```powershell

cd backend

.\\.venv\\Scripts\\Activate.ps1

uvicorn src.main:app --reload --port 8000

```



\---



\### Terminal 3 — Frontend



From the project root:



```powershell

cd frontend

npm run dev

```



\---



\## 9. URLs



\### Frontend



```text

http://localhost:5173/

```



\### Backend



```text

http://localhost:8000/

```



\### Health check



```text

http://localhost:8000/health

```



Expected response:



```json

{

&#x20; "status": "ok",

&#x20; "db": "ok"

}

```



\### OpenAPI JSON



```text

http://localhost:8000/openapi.json

```



\### Scalar API documentation



```text

http://localhost:8000/scalar

```



The default FastAPI Swagger UI and ReDoc endpoints are intentionally disabled.



Therefore:



```text

http://localhost:8000/docs

```



and



```text

http://localhost:8000/redoc

```



are not available.



\---



\## 10. Phase Documentation



\### Phase 1 — Foundation



Phase 1 establishes the project foundation.



Completed:



\* Project structure

\* Environment configuration

\* Docker PostgreSQL

\* Database connection

\* FastAPI application

\* Health endpoint

\* Scalar API documentation

\* OpenAPI endpoint

\* Alembic initialization

\* Baseline migration

\* React + TypeScript frontend

\* React Router

\* Tailwind CSS v4

\* Initial Smart Greenhouse dashboard

\* Six frontend sections



Required frontend section IDs:



```text

sensors

config

automation

overview

controls

events

```



\### Phase 1 Non-Goals



The following features are intentionally \*\*not implemented yet\*\*:



```text

\- Devices table

\- Locations table

\- Sensors table

\- Actuators

\- Automation functionality

\- Authentication

\- WebSockets

\- Sensor API

\- Factory Method

\- Business entities

```



These belong to later phases of the project.



The purpose of Phase 1 is to establish a clean, runnable foundation before implementing the actual Smart Greenhouse domain functionality.



\---



\## Development Notes



The project uses a three-tier architecture:



```text

React + TypeScript

&#x20;       │

&#x20;       │ HTTP

&#x20;       ▼

FastAPI Backend

&#x20;       │

&#x20;       │ SQLAlchemy / Psycopg

&#x20;       ▼

PostgreSQL

```



Database schema changes should be managed through Alembic migrations rather than manual database modifications.



The project should remain focused on the current phase and avoid implementing features assigned to later phases prematurely.



