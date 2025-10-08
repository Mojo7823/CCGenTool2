# CCGenTool2 Server Contribution Guide

## Runtime and External Modules
- **FastAPI** (`fastapi.FastAPI`, `fastapi.Depends`, `fastapi.UploadFile`, `fastapi.File`, `fastapi.HTTPException`) powers the HTTP API surface that the Vue client calls.
- **SQLAlchemy** (`sqlalchemy.create_engine`, `sqlalchemy.orm.Session`, ORM models) provides persistence, with optional PostgreSQL or SQLite backends.
- **Pydantic v2** (`pydantic.BaseModel`, `pydantic.Field`, `pydantic.ConfigDict`) defines request/response schemas with alias support for `class` fields.
- **python-docx** (`docx.Document` et al.) generates DOCX previews for cover pages, SFR/SAR sections, and ST introduction bundles.
- **lxml** (`lxml.etree`, `lxml.html`) parses Common Criteria XML and sanitises HTML previews.
- **Other helpers**: `tempfile`, `uuid`, `pathlib.Path`, and `asynccontextmanager` manage filesystem lifecycles for uploads and previews.

## Workflow Integration Requirements
The backend must keep the following product rules intact because the Vue app and `/final-preview` rely on them to decide completion status and to render compiled documents:
1. **HTML-first output** – every module endpoint that returns preview data (cover, SFR, SAR, ST introduction sections, etc.) must ultimately persist and return HTML fragments. The `/final-preview` step concatenates those fragments, so avoid returning plain text or other formats.
2. **Shared WYSIWYG contract** – rich-text capable endpoints must accept and return the shared JSON structure produced by the TipTap-based editor (table sizing, text formatting, and orientation flags are embedded in the HTML and must not be stripped server-side).
3. **JSON persistence for save/load** – whenever you introduce new storage endpoints, make sure the request/response bodies are JSON serialisations that match the session service expectations from the web client.
4. **Section status reporting** – the `/final-preview` `Section Status` API depends on each module exposing whether required form fields are filled. Extend response payloads with the appropriate `Completed`/`Missing` flags whenever new modules are added so the status screen stays accurate.
5. **Workflow completeness** – endpoints should not silently accept partially filled data. Validate required payload fields and raise `HTTPException(status_code=422, detail=...)` when the workflow rules would otherwise be violated.

## Module Map and Function Responsibilities
### `app/database.py`
- Configures the SQLAlchemy `engine` depending on `DATABASE_URL` (SQLite special casing) and exposes `SessionLocal` and declarative `Base`.
- `get_db()` yields a request-scoped SQLAlchemy session that API endpoints depend upon.

### `app/models.py`
- Declares ORM tables:
  - `Component` for generic XML component rows.
  - `ComponentFamilyBase` mixin underpinning specific FA*/FP*/AC* tables (e.g. `FauDb`, `FcoDb`, `AcoDb`, `AdvDb`).
  - `ElementListDb` captures coloured XML element lists.

### `app/schemas.py`
- Mirrors the ORM with Pydantic models:
  - `ComponentBase`/`ComponentCreate`/`ComponentUpdate`/`ComponentOut` manage generic component payloads.
  - `ComponentFamilyBase`/`ComponentFamilyCreate`/`ComponentFamilyUpdate`/`ComponentFamilyOut` handle family-specific tables using the alias `class_field`.
  - `ElementListBase` + derivatives represent coloured element storage.
  - `XmlParseResponse` & `XmlImportResponse` describe parser outcomes consumed by `/xml` routes.

### `app/xml_parser_service.py`
- `XmlNode` builds a navigable tree with `add_child()` and `to_dict()` used by preview endpoints.
- `XmlParserService`
  - Maintains `functional_table_mappings` and `assurance_table_mappings` that translate XML class IDs into ORM models.
  - `parse_xml_file()` creates the `XmlNode` tree and extracts component dictionaries.
  - `import_to_database()` orchestrates parsing, delegates to `_insert_component_to_table()`, collects failures, imports coloured element lists via `_extract_element_lists()` and `_insert_element_list_to_db()`, and commits.
  - Helper methods `_get_table_class_for_class_id()`, `_get_table_name_for_class_id()`, `_normalize_text()`, `_parse_component_element()`, etc. (defined deeper in the file) normalise XML values before persistence.
- This service is consumed by FastAPI endpoints (`/xml/parse`, `/xml/import`) and the CLI importer.

### `app/main.py`
- Lifecycle:
  - `lifespan()` ensures tables exist on startup.
  - Directory helpers (`get_user_upload_dir()`, `_get_preview_docx_dir()`, `get_user_docx_dir()`) standardise per-user storage.
- Cover/ST document helpers:
  - `_resolve_uploaded_image_path()`, `_format_cover_date()`, `_build_cover_document()`, `_append_html_to_document()`, `_build_html_preview_document()`, `_build_st_intro_combined_document()` convert stored data and HTML fragments into DOCX files using `python-docx`.
  - Styling utilities (`_px_to_points()`, `_parse_margin_left()`, `_parse_color()`, `_collect_inline_styles()`, `_merge_styles()`, `_append_inline_content()`, `_append_block_element()`) interpret inline styles when rendering HTML previews.
- Dependency helpers:
  - `get_family_table_model()` maps requested table names to ORM classes using `XmlParserService` tables.
- REST endpoints (dependency injection via `Depends(get_db)`):
  - `/health` (`health`) issues a lightweight `SELECT 1` and returns latency.
  - CRUD for `/components` (`list_components`, `create_component`, `get_component`, `update_component`, `delete_component`).
  - XML ingestion (`parse_xml_file`, `import_xml_to_database`) delegates to `XmlParserService`.
  - Family lookups (`list_family_tables`, `list_family_components`, `count_family_components`, `create_family_component`, `update_family_component`, `delete_family_component`).
  - Element list retrieval/formatting (`list_element_lists`, `get_formatted_element_list`).
  - Formatted family exports (`get_formatted_family_elements`).
  - Upload & preview management (`upload_cover_image`, `generate_cover_preview`, `generate_sfr_preview`, `generate_sar_preview`, `generate_st_intro_preview`).
  - Cleanup endpoints for each preview namespace to delete user-specific temp files.
- Static assets from `/cover/uploads` and `/cover/docx` are served using `StaticFiles` (see mounting logic near the top of the file).

### `app/__init__.py`
- Marks the directory as a Python package.

### `run.py`
- CLI entry point for local dev using `uvicorn.run("app.main:app")` with autoreload.

### `import_cc_data.py`
- Batch importer utilising `XmlParserService` without FastAPI:
  - `clear_tables()` bulk-deletes ORM rows using SQLAlchemy `delete`.
  - `import_xml()` manages session lifecycle, optional reset, and prints summary metrics returned from the service.
  - `default_xml_path()`, `parse_args()`, and `main()` wire the CLI flags.
- Shares ORM models and parser with `app/main.py`, so keep interfaces aligned.

## Cross-Module Relationships
- FastAPI endpoints and the CLI importer both instantiate `XmlParserService` to keep XML parsing logic centralised.
- Request handlers accept/return Pydantic models from `schemas.py`, which directly map to SQLAlchemy ORM entities defined in `models.py`.
- Upload/preview helpers write files into directories derived from environment variables; cleanup endpoints must delete from the same locations to avoid orphaned files.
- Data consumed by the Vue client must preserve the HTML/JSON contracts outlined above so that saving/loading, previews, and `/final-preview` status calculations remain consistent.

## Testing Expectations
1. Start dependencies (e.g. PostgreSQL) as directed in the repository root instructions, or fall back to SQLite for isolated checks.
2. Launch the API with `uvicorn app.main:app --reload` (or `python run.py`).
3. Run the Vue client and execute your change-specific user flows.
4. Validate XML import paths by uploading `oldparser/cc.xml` through the web UI so that new endpoints see realistic data.
5. Use Playwright-driven browser flows (see the `web/AGENTS.md` instructions) to exercise API mutations that rely on stateful interactions.
6. Capture evidence (logs, screenshots) demonstrating that HTML fragments persist correctly and that `/final-preview` reflects updated section statuses when applicable.

Lastly, please test all your implementation, using your own tool like playwright, and take screenshot as your aid in debugging and for evidence.
