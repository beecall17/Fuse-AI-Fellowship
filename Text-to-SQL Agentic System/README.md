# Text-to-SQL Agentic System

A comprehensive, multi-phase agentic system that converts natural language questions into executable SQL queries. The system decomposes natural language into structured SQL components, generates safe PostgreSQL statements, and executes them against a live database with built-in verification and error recovery.

---

## 🎯 Overview

This project implements a **3-phase text-to-SQL pipeline**:

1. **Query Decomposition** (Task 2): Parse natural language questions into structured components (Intent, Tables, Columns, Filters, Joins)
2. **SQL Generation & Safety** (Task 3): Convert decomposed components into safe, executable PostgreSQL queries with DDL/DML prevention
3. **Execution & Verification** (Task 3): Execute queries against PostgreSQL with automatic error recovery and result caching

---

## 🌟 Key Features

- **Prompt Chaining Architecture**: Multi-step LLM pipeline with self-correction via Groq API (llama-3.3-70b)
- **Safety Enforcement**: Blocks destructive operations (DELETE, DROP, UPDATE, INSERT, ALTER, TRUNCATE) at the SQL parsing level
- **Incremental Caching**: Resume from interruptions with automatic progress persistence
- **Self-Correction Engine**: Catches syntax errors and automatically retries with debugging context
- **Dual Logging System**: Separate logs for generation traces and database execution metrics
- **Interactive Streamlit UI**: Real-time query builder with side-by-side reasoning and results visualization

---

## 📂 Project Structure

```
Text-to-SQL Agentic System/
├── fastapi_agent.py           # FastAPI REST endpoint for queries
├── query_decomposition.py      # Task 2: LLM-based query decomposition
├── sql_pipeline.py             # Task 3: SQL generation, verification & execution
├── run_pipeline.py             # Batch processor for all 50 questions
├── streamlit_app.py            # Interactive web dashboard
├── Dockerfile & docker-compose.yml  # Container orchestration
├── logs/                       # Generation & execution logs
└── Scripts/
    ├── seed.sql                # PostgreSQL schema
    ├── sql_questions.csv       # Input questions (50 samples)
    ├── query_decompositions.json   # Task 2 output
    └── query_executions.json      # Task 3 final results
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

### Run Batch Pipeline
```bash
python run_pipeline.py --limit 5  # Test with first 5 questions
```

### Launch Interactive Dashboard
```bash
streamlit run streamlit_app.py  # Opens at http://localhost:8501
```

### Docker Deployment
```bash
docker-compose up -d
```

---

## 📖 Documentation

For detailed task-specific information, refer to:
- **Task 2 Details**: See `Task_readme/Task2_README.md`
- **Task 3 Details**: See `Task_readme/Task3_README.md`
- **Project Journal**: See `Task_readme/JOURNAL.md` for updates and insights

---

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, FastAPI
- **LLM**: Groq API (llama-3.3-70b-versatile)
- **Database**: PostgreSQL
- **Frontend**: Streamlit
- **Deployment**: Docker & Docker Compose
- **Dependencies**: openai, psycopg2-binary, python-dotenv

