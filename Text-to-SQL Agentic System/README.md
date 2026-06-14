# Text-to-SQL Agentic System

A comprehensive, multi-phase agentic system that converts natural language questions into executable SQL queries. The system decomposes natural language into structured SQL components, generates safe SQL with mutation prevention, and includes a production-ready FastAPI REST service with enterprise guardrails.

---

## 🎯 Overview

This project implements a **4-phase text-to-SQL pipeline**:

1. **Query Decomposition** (Task 2): Parse natural language questions into structured components (Intent, Tables, Columns, Filters, Joins)
2. **SQL Generation & Safety** (Task 3): Convert decomposed components into safe, executable PostgreSQL queries with DDL/DML prevention
3. **Execution & Verification** (Task 3): Execute queries against PostgreSQL with automatic error recovery and result caching
4. **FastAPI REST Service** (Task 4): Production-ready HTTP endpoint with enterprise guardrails (relevance checking, mutation safety, auto-correction, summarization)

---

## 🌟 Key Features

- **Prompt Chaining Architecture**: Multi-step LLM pipeline with self-correction via Groq API (llama-3.3-70b)
- **Safety Enforcement**: Blocks destructive operations (DELETE, DROP, UPDATE, INSERT, ALTER, TRUNCATE) at the SQL parsing level
- **Incremental Caching**: Resume from interruptions with automatic progress persistence
- **Self-Correction Engine**: Catches syntax errors and automatically retries with debugging context (up to 3 attempts)
- **Dual Logging System**: Separate logs for generation traces and database execution metrics
- **Interactive Streamlit UI**: Real-time query builder with side-by-side reasoning and results visualization
- **Enterprise Guardrails**: Relevance filtering, mutation safety, automatic query correction, and natural language summarization
- **Containerized Deployment**: Docker & Docker Compose for seamless multi-service orchestration (PostgreSQL, Streamlit, FastAPI)

---

## 📂 Project Structure

```
Text-to-SQL Agentic System/
├── fastapi_agent.py           # Task 4: FastAPI REST endpoint with guardrails
├── query_decomposition.py      # Task 2: LLM-based query decomposition
├── sql_pipeline.py             # Task 3: SQL generation, verification & execution
├── run_pipeline.py             # Batch processor for all 50 questions
├── streamlit_app.py            # Interactive web dashboard
├── Dockerfile & docker-compose.yml  # Container orchestration
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── logs/                       # Generation & execution logs
│   ├── sql_generation.log      # Task 2-3 decomposition & SQL traces
│   └── sql_execution.log       # Task 3 database execution metrics
├── tests/                      # Test suite
│   └── test_fastapi_agent.py   # Verification tests for Task 4
├── Scripts/                    # Helper scripts
│   ├── seed.sql                # PostgreSQL schema initialization
│   ├── sql_questions.csv       # Input questions (50 samples)
│   ├── query_decompositions.json   # Task 2 output
│   └── query_executions.json       # Task 3 final results
└── Task_readme/                # Detailed task documentation
    ├── Task2_README.md         # Query Decomposition details
    ├── Task3_README.md         # SQL Generation & Execution details
    ├── Task4_README.md         # FastAPI Service & Guardrails details
    └── JOURNAL.md              # Development updates and insights
```

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Configure Environment
```bash
cp .env.example .env
# Edit .env with your Groq API key and PostgreSQL credentials
```

### Run Batch Pipeline (Tasks 2-3)
```bash
python run_pipeline.py --limit 5  # Test with first 5 questions
```

### Launch Interactive Dashboard (Task 2-3)
```bash
streamlit run streamlit_app.py  # Opens at http://localhost:8501
```

### Start FastAPI Service (Task 4)
```bash
# Option 1: Docker (Recommended - all services together)
docker-compose up -d

# Option 2: Direct Python
python fastapi_agent.py  # Runs on http://localhost:8000
```

### Test FastAPI Endpoint
```bash
# Run verification test suite
python tests/test_fastapi_agent.py

# Or test manually with curl:
curl -X POST http://localhost:8000/agent/sql \
  -H "Content-Type: application/json" \
  -d '{"question": "How many customers are from Germany?"}'
```

---

## 📖 Documentation

For detailed task-specific information, refer to:
- **Task 2 Details**: See `Task_readme/Task2_README.md` - Query decomposition pipeline
- **Task 3 Details**: See `Task_readme/Task3_README.md` - SQL generation, safety, and execution
- **Task 4 Details**: See `Task_readme/Task4_README.md` - FastAPI service and enterprise guardrails
- **Project Journal**: See `Task_readme/JOURNAL.md` - Development updates and insights

---

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, FastAPI, Streamlit
- **LLM**: Groq API (llama-3.3-70b-versatile)
- **Database**: PostgreSQL (psycopg2-binary)
- **Frontend**: Streamlit web dashboard
- **Deployment**: Docker & Docker Compose
- **Dependencies**: openai, pydantic, python-dotenv, uvicorn

---

## 🔒 Security & Guardrails

The FastAPI service (Task 4) implements four layers of protection:

1. **Relevance Intent Guardrail**: Filters out non-database questions (chit-chat, weather, etc.)
2. **Mutation Safety Guardrail**: Blocks DELETE, UPDATE, DROP, INSERT, ALTER, TRUNCATE statements
3. **Automatic Self-Correction**: Retries up to 3 times on SQL execution errors with debugging context
4. **Natural Language Summarizer**: Translates raw results into human-readable summaries

See `Task_readme/Task4_README.md` for detailed architecture and testing instructions.

---

## 📊 Expected Results

When running the full pipeline on 50 test questions:
- **Task 2**: Produces structured query decompositions (intent, tables, columns, filters, joins)
- **Task 3**: Generates safe SQL and executes against PostgreSQL with >95% success rate
- **Task 4**: Serves HTTP requests with guardrails, guardrails + auto-correction achieving near-perfect safety

---

## 🐳 Docker Deployment

All services (PostgreSQL on port 5433, Streamlit on port 8501, FastAPI on port 8000) run simultaneously:

```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f fastapi_agent

# Stop services
docker-compose down -v
```
