# EduNexus

EduNexus is an academic intelligence layer for a university ERP. It combines role-scoped academic records, deterministic validation, retrieval grounded in institutional documents, and human-confirmed faculty operations. It does not replace the underlying ERP.

## Architecture

- `frontend/`: React 19 and Vite student, faculty, and admin workspaces.
- `backend/app/`: FastAPI, SQLAlchemy models, JWT authentication, academic APIs, and workflow services.
- `agents/`: LangGraph intent router for academic knowledge, university policy, student success, and faculty attendance intelligence.
- `rag/`: curriculum and institutional source documents, ingestion, retrieval, and the existing Chroma store.
- `ml/`: a reproducible synthetic Student Success evaluation demonstration.
- `docs/evaluation/`: generated evaluation evidence; synthetic ML results are clearly labeled.

Academic writes follow interpretation or data entry → server-side validation → explicit confirmation → PostgreSQL transaction → audit entry. LLM output never writes academic records directly.

## Local setup

1. Configure `backend/.env` with `DATABASE_URL`, `JWT_SECRET`, and (when needed) `GEMINI_API_KEY`. Optional mail settings are `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, and `SMTP_FROM`.
2. From `backend/`, run `python -m alembic upgrade head` to apply schema migrations.
3. Create an admin with `EDUNEXUS_ADMIN_USERNAME`, `EDUNEXUS_ADMIN_EMAIL`, and `EDUNEXUS_ADMIN_PASSWORD` set in the environment, then run `python scripts/create_admin.py`. The command does not print or store the supplied password in source control.
4. Start the API from `backend/` with `uvicorn app.main:app --reload`.
5. From `frontend/`, run `npm install` once, then `npm run dev`.

Student and faculty seeded prototype accounts and source records are managed by `backend/scripts/seed.py`. Keep the provided database and source documents intact when refreshing the frontend.

## Verification

From the repository root, run `python -m unittest discover -s backend/tests -v`. Run `python scripts/evaluate_agents.py` for measured router cases and latency, and `python ml/student_success_evaluation.py` for the synthetic ML experiment. Build the frontend from `frontend/` with `npm run build`.

See [Evaluation I evidence](docs/EVALUATION_I.md) for metrics interpretation and limitations. Database/API integration checks require the configured PostgreSQL service. SMTP status is `NOT_CONFIGURED`, `SENT`, or `FAILED`; an email issue does not roll back a saved mentor request.
