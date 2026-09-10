# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Damien is UC Berkeley's course evaluations administration tool ("OEC, reimagined"). Department admins assign evaluation forms and types to course sections each term, confirm the results, and Damien exports the confirmed data as CSVs (via SFTP, with S3 as a fallback/archive) for ingestion by the Blue course evaluation system. Course/instructor/student data is sourced from a Postgres mirror of SIS data (schema `unholy_loch`, refreshed via `dblink`).

## Commands

```bash
# Run all tests and linters in parallel
tox -p

# Run pytest only
tox -e test

# Run a specific test file or directory
tox -e test -- tests/test_models/test_foo.py
tox -e test -- tests/test_externals/

# Python linter (Ruff)
tox -e lint-py

# Lint specific Python files
tox -e lint-py -- scripts/foo.py

# Vue/TS linter (ESLint)
tox -e lint-vue

# Auto-fix Vue/TS lint errors
tox -e lint-vue-fix

# Build Vue frontend
tox -e build-vue  # or: npm run build-vue

# Run Vue dev server (port 8080)
npm run serve-vue

# Run Flask backend (port 5000)
python application.py

# Initialize DB schema
export FLASK_APP=application.py
flask initdb

# Interactive console with Flask app context
python -i consoler.py
```

## Architecture

### Backend (Flask + PostgreSQL)

The Flask app is in `damien/` and follows a layered architecture:

- **`damien/api/`** — REST controllers (one per resource). All routes are `/api/*`.
- **`damien/merged/`** — Business logic that aggregates models/externals: `section.py` (course section view combining SIS + evaluation data), `user_session.py` (Flask-Login user wrapper).
- **`damien/externals/`** — Raw integrations: `s3.py`, `sftp.py` (evaluation exports), `b_connected.py` (SMTP via UC Berkeley's bConnected On-Premise relay).
- **`damien/models/`** — SQLAlchemy models. `department.py` and `evaluation.py` are central; `department_form.py`/`evaluation_type.py` define the form+type combinations that can be assigned to a section's evaluation; `export.py` tracks export job status/history.
- **`damien/jobs/refresh_unholy_loch.py`** — The one background job: refreshes the `unholy_loch` SIS mirror. Scheduled via APScheduler (cron config in `SCHEDULE_LOCH_REFRESH`) and also triggerable by admins via `/api/job/refresh_unholy_loch`.
- **`damien/lib/`** — Pure utilities: `berkeley.py` (term ID/date calculations), `queries.py` (raw SQL against `unholy_loch`), `exporter.py` (builds and uploads the Blue export CSVs), `cache.py` (JSON section/department cache), `http.py`, `util.py`.
- **`config/`** — Layered config: `default.py` → `{DAMIEN_ENV}.py` → `{DAMIEN_LOCAL_CONFIGS}/{DAMIEN_ENV}-local.py`. Sensitive values go in the local file (outside the repo). `DAMIEN_ENV` defaults to `development`.

### Frontend (Vue 3 + TypeScript)

SPA using Vue 3, Vuetify 3, Pinia, and vue-router. Source lives in `src/`.

- **`src/views/`** — Page-level components. `StatusBoard.vue` is the admin overview; `Department.vue` is where department admins assign forms/types and confirm evaluations. `TheMonastery.vue`/`Megiddo.vue`/`NannysRoom.vue` are gated Easter eggs (`EASTER_EGG_MONASTERY`/`EASTER_EGG_NANNYSROOM` config).
- **`src/stores/`** — Pinia stores: `context.ts` (current user/session/term), `department/`, `list-management-session.ts`.
- **`src/api/`** — Axios API client wrappers.
- **`src/router.ts`** — Route guards call `requiresAdmin` or `requiresDepartmentMembership` from `src/auth.ts`.

In development, Vue runs at `http://localhost:8080` (via `npm run serve-vue`) and Flask at port 5000. Flask returns CORS headers in development mode (see `damien/routes.py`) to allow cross-origin requests. In production/staging, Flask serves `dist/static/index.html` for all non-API routes.

### Key patterns

**DB commits** — Always call `std_commit()` (from `damien/__init__.py`) instead of `db.session.commit()`. In test mode, `std_commit()` only flushes; it never actually commits, keeping test transactions isolated. Pass `allow_test_environment=True` for the rare case a test needs a real commit (e.g., to make data visible to a later, separately-committed request).

**Test fixtures** — External service calls are replaced by fixtures under `fixtures/` when `DAMIEN_ENV == 'test'` (`FIXTURES_PATH` config), and S3 interactions are mocked with `moto` (see `tests/util.py`'s `mock_s3_bucket`). The `skip_when_pytest` decorator (from `damien/__init__.py`) is used to stub out functions entirely under test.

**Caching** — Section/department JSON is cached via `damien/lib/cache.py`, backed by the `JsonCache` model and Flask-Cache (`CACHE_TYPE = 'FileSystemCache'`).

**Evaluation exports** — `damien/lib/exporter.py` builds the full set of CSVs (`courses`, `course_instructors`, `course_students`, `course_supervisors`, `students`, `instructors`, `supervisors`, hierarchy files, etc.) for a term and uploads them via SFTP (falling back to S3 on failure, if `ALLOW_S3_UPLOAD_ON_PUBLISH_FAILURE`). Several files carry forward only the immediately preceding term's rows from the last successful export (rather than the full past-export contents) to keep file size bounded; course/term identity is inferred from `COURSE_ID` prefixes like `2022-B` (see `term_code_for_sis_id`/`term_ids_range` in `damien/lib/berkeley.py`).

**Authentication** — CAS (UC Berkeley) in production, via the `cas` package (`damien/api/auth_controller.py`). Development uses `DEVELOPER_AUTH_ENABLED = True` + `DEVELOPER_AUTH_PASSWORD` for the `/api/auth/dev_auth_login` bypass. Tests use the `fake_auth` pytest fixture.

### E2E tests (Mrs. Baylock)

Selenium-based browser tests live in `mrsbaylock/` (the counterpart to Xena in the sibling `diablo` project). Run interactively via `./mrsbaylock/mrsbaylock.sh`, which prompts for browser (Chrome/Firefox), headless mode, test filter, and credentials. Requires chromedriver or geckodriver installed separately.
