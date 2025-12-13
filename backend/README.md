# KidRide Flask Backend Skeleton

## Quickstart (local venv)
1. `python -m venv .venv && .venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux).
2. `pip install -r requirements.txt`.
3. Copy `env.example` to `.env` and adjust values (Firebase credentials path, database URL, CORS origins).
4. `flask run --app app --debug` (or `flask run --app app --host=0.0.0.0 --port=5000`).

## Quickstart (Docker)
- `docker compose up --build`
- API available at `http://localhost:5000`.

## Notable endpoints
- `GET /health` — service heartbeat.
- `GET /api/v1/ping` — simple ping.
- `GET /api/v1/users/me` — returns current user (requires Firebase ID token as `Authorization: Bearer <token>`; honors `AUTH_DEV_BYPASS=true`).
- `POST /api/v1/kids` — create a kid record for the current user/household. JSON body: `first_name` (required), `dob` (ISO `YYYY-MM-DD`, optional), `gender` (optional), `household_id` (optional, falls back to user's household).
- `GET /api/v1/kids` — list kids for the caller's household (or `household_id` query param); auth required.
- `POST /api/v1/households` — create household and attach caller. Body: `name` (required), `address`, `location`.
- `GET /api/v1/households/me` — fetch caller's household (requires user to be linked).

## Structure
- `app.py` — Flask app creation, CORS, DB init, health routes.
- `config.py` — environment-driven settings (SQLite dev default, Postgres ready).
- `models/` — SQLAlchemy models seeded from ERD (Household, User, Kid, Vehicle).
- `routes/` — blueprints for auth and user endpoints.
- `middleware/firebase_auth.py` — Firebase JWT guard with optional dev bypass.
- `services/` — `user_service` placeholder for DB-backed lookups/creation.
- `services/` — `kid_service` creates and lists kid records.
- `utils/` — helpers for JSON responses and bearer token parsing.

## Notes
- Client apps should authenticate with Firebase client SDK, then send the ID token to protected routes. Server-side verification is stubbed in middleware and will work once Firebase Admin credentials are supplied.
- Database migrations are not included yet; add Alembic when schemas firm up.
