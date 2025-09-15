# CCGenTool 2

Common Criteria Generation Tool 2 for Security Target Documents

## CCGenTool2 — Vue.js + FastAPI + Postgres

This scaffolds a simple full‑stack app with a dashboard UI and a Postgres‑backed CRUD for a "components" table.

### What’s included
- Backend: FastAPI, SQLAlchemy, psycopg2, health endpoint, CRUD for components
- Frontend: Vue 3 + Vite with navbar, sidebar (accordion) and pages
	- Home
	- Database → Query Data, Modify Data (CRUD)
- Docker Compose for Postgres and API

### Data model (components)
- id (int, PK)
- class (string, required) → stored as class_name in DB
- family (string)
- component (string)
- component_name (string)
- element (string)
- element_item (string)

### Endpoints
- GET /health → DB status and latency
- GET /components?q=... → list/filter
- POST /components → create
- GET /components/{id} → read
- PUT /components/{id} → update
- DELETE /components/{id} → delete

### Quick start (Docker)

#### Option 1: Using convenience scripts (Recommended)
- **Fresh installation** (clean install, removes all data):
	```bash
	./fresh_run.sh
	```
- **Regular startup** (normal startup, preserves data):
	```bash
	./regular_run.sh
	```

#### Option 2: Manual setup
1. Start Postgres + API
	 - In repo root:
	 ```bash
	 docker compose up -d --build
	 ```
	 API: http://localhost:8000

2. Start Frontend (first time)
	 ```bash
	 cd web
	 cp .env.example .env
	 npm install
	 npm run dev
	 ```
	 UI: http://localhost:5173

#### Initial data setup
1. Navigate to **XML Parser** in the sidebar
2. Upload `/oldparser/cc.xml` to populate the database with Common Criteria components
3. Test the **Security Functional Requirements** feature

### Dev without Docker
- Backend
	```bash
	cd server
	python -m venv .venv && source .venv/bin/activate
	pip install -r requirements.txt
	export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/appdb"
	python run.py
	```
- Frontend
	```bash
	cd web
	cp .env.example .env
	npm install
	npm run dev
	```

### Notes
- Navbar shows DB status (ok/degraded) with latency.
- Sidebar contains Home and Database; Database expands to Query Data and Modify Data.