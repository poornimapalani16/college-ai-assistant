# College AI Assistant — O.P. Jindal Global University (JGU)

An enterprise-style RAG assistant for students, parents, faculty, and admin staff,
built to the PRD: **FastAPI + LangChain + LangGraph + ChromaDB + Sentence-Transformers +
Gemini** on the backend, **React** on the frontend, deployable to **Render**.

## What's here

```
backend/    FastAPI RAG API (ingestion, ChromaDB, LangGraph pipeline, admin endpoints)
frontend/   React app: Module 1 (landing page) + Module 2/3 (chat widget + admin panel)
data/       Extracted JGU Student Handbook text used to seed the knowledge base
render.yaml Render blueprint for both services
```

## The 3 modules from the PRD

1. **Landing page** — `frontend/src/components/LandingPage.jsx` — one page representing
   the JGU website (hero, schools, quick links, campus life, footer).
2. **User touches the assistant & asks a question** — the floating "Ask JGU Assistant"
   button opens `ChatWidget.jsx`, where the user picks a role (student/parent/faculty)
   and types a question.
3. **The chatbot answers** — `ChatWidget.jsx` calls `POST /api/chat`, which runs the
   LangGraph pipeline in `backend/app/rag_graph.py`: rewrite the query using chat
   history → retrieve top-k chunks from ChromaDB → ask Gemini to answer **only** from
   those chunks → return the answer **with cited source documents/pages**.

There's also a 4th, PRD-required piece: **Admin: upload / delete / re-index documents**,
at `frontend/#admin` (`AdminPanel.jsx`) calling the `/api/admin/*` endpoints.

## Data source

`data/jgu_handbook_extract.txt` contains real text pulled from the official
[JGU Student Handbook 2024-25](https://jgu.edu.in/storage/1/Student-Handbook.pdf)
(university overview, leadership, academic calendar, all 8 schools' admissions/fees,
public holidays). It's a ~42-page front-matter extract of the 350+ page handbook —
see the note at the bottom of that file for what a production ingest should add
(attendance rules, exam regulations, hostel/library policy, full fee schedules,
faculty directory, etc). **Drop the full PDF into `backend/data/` and re-run
`seed_documents.py`** to index everything.

## Run it locally

### 1. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: set GEMINI_API_KEY (https://aistudio.google.com/apikey) and ADMIN_API_KEY

python seed_documents.py                 # indexes everything in backend/data/
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the interactive API docs.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. Set `VITE_API_BASE_URL=http://localhost:8000` in a
`frontend/.env` file if you don't want the default.

Admin panel: `http://localhost:5173/#admin` (enter the `ADMIN_API_KEY` from your backend `.env`).

## Deploy to Render

`render.yaml` defines both services (backend web service + frontend static site) as a
Render **Blueprint**. In the Render dashboard: New → Blueprint → point at this repo.
You'll be prompted to fill in `GEMINI_API_KEY` and `ADMIN_API_KEY` (marked `sync: false`
so they're entered securely rather than committed). After first deploy, run
`python seed_documents.py` via a Render **Job** (or SSH) to populate the vector store,
or upload documents through the `#admin` panel once both services are live.

## Notes on the architecture

- **Why LangGraph, not just a LangChain chain?** The graph (`rewrite_query → retrieve →
  generate_answer`) lets follow-up questions ("what about for postgrad?") resolve
  correctly using conversation memory, and makes it easy to add nodes later
  (e.g., a "grade documents" relevance-filter node, or role-based routing).
- **Why Sentence-Transformers locally instead of a hosted embeddings API?** Keeps
  embedding cost at $0 and avoids sending every chunk of student data to a third
  party; only the final generation call goes to Gemini.
- **Session memory** is in-process (`SESSION_STORE` dict) for this reference build —
  swap it for Redis/Postgres before running multiple backend instances.
- **Security**: admin endpoints require an `X-Admin-Key` header; put real auth
  (SSO / JWT tied to staff accounts) in front of this before production use with
  real student data.
