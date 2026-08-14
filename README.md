# EduNexus — Agentic AI Academic Decision-Support System

EduNexus is an agentic AI academic decision-support platform built on top of a college ERP. Traditional ERPs store attendance, marks, and records but never reason over them. EduNexus closes that gap: it detects at-risk students before results confirm it, matches students to faculty mentors by actual research/interest overlap, answers placement and academic queries through a site-wide grounded RAG chatbot, and generates predictive institutional reports automatically — all while keeping every actual approval and decision in human (faculty/admin) hands.

---

## 🌟 Key Features

1. **Agent 1 — Student Success Scanner**: Evaluates attendance (<75%), internal marks trend drops (>15%), and unsubmitted assignments via deterministic rule pre-filters, then invokes Gemini 2.5 Flash for personalized risk narratives and action plans.
2. **Agent 2 — Mentor Discovery Engine**: Performs ChromaDB vector similarity search over faculty research interests and bios, checks live availability toggles, and synthesizes 2-sentence match rationales.
3. **Agent 3 — Placement & Academic Policy RAG Assistant**: Multi-document grounded RAG assistant (placement guides, interview question banks, academic attendance policies, assignment submission rules). Accessible site-wide.
4. **Agent 4 — Executive Admin Analytics & Predictions**: Multi-year moving-average placement rate and salary package forecasts with executive Gemini narratives and disclaimers.
5. **Role-Based Access Control (RBAC)**: Student, Faculty, and Admin dashboards with JWT authentication and server-side department-scoped messaging guards.
6. **Dark/Light Theme**: Rich purple & indigo aesthetics with persistent Dark/Light mode context and zero unhandled errors.

---

## 🛠 Tech Stack

- **Frontend**: React + Vite + TailwindCSS + Lucide Icons + Recharts
- **Backend**: FastAPI (Python), SQLAlchemy ORM, SQLite / PostgreSQL
- **Vector DB**: ChromaDB (local persistent vector store)
- **AI / Agent Framework**: LangGraph StateGraph, Gemini 2.5 Flash LLM
- **Scheduler**: APScheduler for background daily risk scans

---

## 🚀 Quickstart Guide

### 1. Backend Setup & Seed
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Generate synthetic ERP database
python database/seed/generate_seed.py

# Seed ChromaDB vector store
python database/seed/seed_vector_store.py

# Start FastAPI backend server
python -m uvicorn app.main:app --reload --app-dir backend
```
The FastAPI backend will run at `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The React frontend will launch at `http://localhost:5173`.

---

## 🔑 Demo Login Accounts

| Role | Email | Password |
|---|---|---|
| **Student** | `student@educamp.edu` | `password123` |
| **Faculty** | `faculty@educamp.edu` | `password123` |
| **Admin** | `admin@educamp.edu` | `password123` |
