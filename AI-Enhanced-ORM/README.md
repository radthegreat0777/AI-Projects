# AI-Powered Natural Language Database Agent with Human-in-the-Loop DML Approval

A **FastAPI** backend that combines SQLAlchemy async ORM with an AI-powered natural language database agent — allowing users to query and mutate a PostgreSQL database using plain English, with a built-in human-in-the-loop approval workflow for DML operations.

---

## Features

- **Async REST API** — built with FastAPI and SQLAlchemy 2.0 async engine
- **AI Database Agent** — powered by LangChain + GPT-3.5-turbo; translates natural language into SQL queries
- **Conversational Memory** — agent retains conversation context via LangGraph's `PostgresSaver` checkpointer
- **Human-in-the-Loop DML** — AI proposes INSERT/UPDATE/DELETE statements; a human must explicitly approve before execution
- **Gradio Chat UI** — browser-based conversational interface mounted at `/agent/ui`
- **Repository Pattern** — clean separation of database access logic for `User` and `Invoice` entities
- **Pydantic Validation** — all request and response bodies are fully validated

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL (via `asyncpg`) |
| AI / LLM | LangChain, LangGraph, OpenAI GPT-3.5-turbo |
| Agent Memory | LangGraph `PostgresSaver` |
| Chat UI | Gradio |
| Validation | Pydantic v2 |
| Config | python-dotenv |

---

## Project Structure

```
.
├── main.py                  # FastAPI app entry point; mounts routers and Gradio UI
├── database_config.py       # Async SQLAlchemy engine and session factory
├── db_models.py             # ORM models: User, Invoice, PendingRequest
├── resp_models.py           # Pydantic request/response schemas
├── db_agent.py              # LangChain agent, DML proposal & approval logic
├── agent_routes.py          # API routes for natural language queries and DML workflow
├── user_routes.py           # CRUD routes for User entities
├── user_repository.py       # DB access layer for User
├── invoice_route.py         # Routes for Invoice creation
├── invoice_repository.py    # DB access layer for Invoice
└── requirements.txt         # Python dependencies
```

---

## Database Schema

### `users`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | Primary Key, Indexed |
| `name` | String(255) | Not Null |
| `email` | String(255) | Unique, Not Null |

### `invoices`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | Primary Key, Indexed |
| `user_id` | Integer | Not Null (FK to users) |
| `amount` | Float | — |
| `description` | String(255) | Not Null |
| `created_at` | DateTime | Server default `now()` |

### `pending_requests`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | String(36) | Primary Key (UUID) |
| `query` | String(1000) | Natural language query |
| `sql` | Text | AI-generated SQL |
| `status` | String(20) | `pending` / `approved` / `rejected` |
| `created_at` | DateTime | Server default `now()` |

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL running locally
- DBeaver (to Check Database Processes) 
- An OpenAI API key

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/ai-enhanced-orm.git
cd ai-enhanced-orm

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
```

Update the database connection strings in `database_config.py` and `db_agent.py` to match your PostgreSQL credentials:

```python
# database_config.py
DATABASE_URL = "postgresql+asyncpg://YOUR_USER:YOUR_PASSWORD@localhost:5432/YOUR_DB"

# db_agent.py
DB_URL = "postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/YOUR_DB"
```

### Running the App

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

Gradio chat UI: `http://localhost:8000/agent/ui`

---

## API Reference

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/` | Create a new user |
| `GET` | `/users/` | List all users (paginated) |
| `GET` | `/users/{user_id}` | Get a user by ID |

### Invoices

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/invoices/` | Create a new invoice |

### Database Agent

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/agent/query` | Query the database with natural language |
| `POST` | `/agent/dml/propose` | AI proposes a DML SQL statement for review |
| `POST` | `/agent/dml/approve` | Approve or reject a pending DML statement |

---

## Human-in-the-Loop DML Workflow

This project implements a safe pattern for AI-driven data mutations:

```
1. User sends a natural language request  →  POST /agent/dml/propose
2. AI generates the SQL and saves it with status "pending"
3. API returns the proposed SQL + an approval_id
4. Human reviews the SQL
5. Human approves or rejects  →  POST /agent/dml/approve
6. If approved, SQL is executed; status updated to "approved"
7. If rejected, no changes are made; status updated to "rejected"
```

This ensures **no DML statement is ever executed without human review**, regardless of what the AI generates.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key (required) |

---

## Notes & Known Issues

- The `user_routes.py` `create_user` endpoint has a missing `await` on `repo.get_user_by_email()` — this should be awaited to correctly check for duplicate emails.
- The `agent_routes.py` `approve_dml` route is missing the leading `/` in the path (`"dml/approve"` should be `"/dml/approve"`).
- `database_config.py` uses a hardcoded connection string — move credentials to environment variables before deploying.
- The agent is restricted to **SELECT only** queries. DML goes through the separate proposal/approval flow.

---

## Future Improvements

- Add authentication (e.g., JWT) to protect agent and admin routes
- Migrate hardcoded DB credentials to environment variables
- Add MCP (Model Context Protocol) server integration
- Write unit and integration tests
- Create a Frontend UI to modify this project to a complete application

---

