# CCGenTool 2

Common Criteria Generation Tool 2 for Security Target documents.

## Features

- **XML parsing** – upload a Common Criteria XML file and parse it via `/xml/parse`.
- **Database import** – `/xml/import` parses and stores components into Postgres tables grouped by family.
- **Database browser** – the Query Data page lists all functional and assurance tables. Selecting a table displays its rows.
- **CRUD API** – `/components` endpoints provide create, read, update and delete operations.

## Project structure

- `oldparser/` – original scripts and sample `cc_2022.xml`.
- `server/` – FastAPI backend (see `app/main.py`).
- `web/` – Vue 3 frontend (Vite based).
- `docker-compose.yml` – optional Postgres + API stack.

## API overview

- `GET /health` – database status and latency.
- `GET/POST/PUT/DELETE /components` – CRUD operations.
- `POST /xml/parse` – parse an uploaded XML file.
- `POST /xml/import` – parse and insert components into Postgres.
- `GET /families` – list available family tables.
- `GET /families/{table}` – query rows from a specific family table.

## Getting started

### Using Docker

```bash
docker compose up -d --build
```

API available at <http://localhost:8000>.

Frontend:

```bash
cd web
npm install
npm run dev
```

Open <http://localhost:5173> in a browser.

### Manual setup

Backend:

```bash
cd server
pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/appdb"
python run.py
```

Frontend:

```bash
cd web
npm install
npm run dev
```

## Notes

- The Query Data view lists all tables and lets you search each one.
- After importing XML data, rows become visible in their respective family tables and via the `/components` CRUD endpoints.

