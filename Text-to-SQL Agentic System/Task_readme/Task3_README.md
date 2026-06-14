# Text-to-SQL Agentic System (Decomposition, Generation & Verification)

This workspace contains a multi-phase **Text-to-SQL Agentic System** that parses natural language questions, extracts schema constraints, generates safe and mixed-case corrected PostgreSQL SELECT queries via the **Groq API**, and validates and executes them live against a Dockerized database.

---

## 🌟 Key Features

- **Prompt Chaining Pipeline**:
  - **Prompt 1 (Decomposition)**: Decomposes natural language queries into Intent, Tables, Columns, Filters, and Joins.
  - **Prompt 2 (Generation)**: Translates decomposition components into optimized PostgreSQL-compatible SELECT statements (safeguarding mixed-case variables with proper double quotes).
  - **Prompt 3 (Self-Correction Retry)**: Captures database-level syntax or catalog errors and dynamically debugs the SQL for a single automatic retry.
- **Safety Verification Gate**: Parses and blocks any destructive DDL/DML queries (e.g., `DELETE`, `DROP`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`) case-insensitively, strictly enforcing read-only SELECT behaviors.
- **Incremental Cache Recovery**: Persists batch executions. If interrupted, the system automatically checks cache files to resume progress and re-decomposes only invalid/failed outputs.
- **Dynamic Dual Logger**:
  - `logs/sql_generation.log`: Contains detailed generation traces, Groq prompts, and self-correction debugging logic.
  - `logs/sql_execution.log`: Details connection logs, safety validations, raw PostgreSQL operations, and timing metrics.
- **Interactive Streamlit Web Interface**: Provides an elegant, responsive side-by-side layout. Users can select pre-loaded questions or query the database in real-time, viewing live pipeline reasoning, safety metrics, and console logs side-by-side with records tables.

---

## 📂 System File Map

```text
Text-to-SQL Agentic System/
├── .env                       # API credentials & PostgreSQL connection keys
├── .env.example               # Template environment configuration
├── query_decomposition.py     # Task 2: Question decomposition & caching
├── sql_pipeline.py            # Task 3: SQL Gen, Safe verification, Self-correction, and DB execution
├── run_pipeline.py            # Task 3: Batch runner for all 50 questions
├── streamlit_app.py           # Task 3: Streamlit UI with side-by-side logs and reasoning
├── README.md                  # Master documentation (Task 2 & 3)
├── Task2_README.md            # Original Task 2 README
├── JOURNAL.md                 # Project updates, challenges, and insights
├── logs/
│   ├── sql_generation.log     # Detailed LLM generation traces
│   └── sql_execution.log      # Raw database query execution metrics
└── Scripts/
    ├── seed.sql               # PostgreSQL seed schemas
    ├── sql_questions.csv      # Natural language questions list
    ├── query_decompositions.json # Structured caching file for Task 2
    └── query_executions.json     # Final output with query, results, and row count
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.8+ installed along with the required libraries:
```bash
pip install streamlit pandas psycopg2-binary openai python-dotenv
```

### 2. Set Up Environment Variables
Configure your credentials in `.env` in the root directory:
```ini
# Groq API Configuration
GROQ_API_KEY=gsk_your_real_groq_api_key_here
GROQ_API_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.3-70b-versatile

# PostgreSQL Database Configuration
POSTGRES_DB=classicmodels
POSTGRES_USER=app_user
POSTGRES_PASSWORD=secure_password_123
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
```

---

## 🚀 Execution & Usage

### 🚀 1. Run the Batch Pipeline (All 50 Questions)
To process all 50 questions, generate their safe SQL queries, run them against PostgreSQL, and save them to `Scripts/query_executions.json`:
```bash
python run_pipeline.py
```
*Supports the following arguments:*
- `--limit N`: Limit pipeline to the first `N` questions (ideal for rapid tests).
- `--force`: Ignore caching/resuming and overwrite all previous executions.

### 🖥️ 2. Launch the Streamlit Web Server
To launch the interactive dashboard for natural language questions, dynamic reasoning visualizers, and data grid rendering:
```bash
streamlit run streamlit_app.py
```
This launches a web page at `http://localhost:8501`.

---

## 📊 Output Schema (`query_executions.json`)

The final structured JSON file `Scripts/query_executions.json` follows this structured schema:

```json
[
  {
    "question": "Show all orders placed by customers in Germany",
    "decompose": {
      "Intent": "Retrieve orders for customers in Germany",
      "Tables": ["orders", "customers"],
      "Columns": ["orderNumber", "orderDate", "status", "country"],
      "Filters": "country = 'Germany'",
      "Joins": "orders.customerNumber = customers.customerNumber"
    },
    "sql": "SELECT o.\"orderNumber\", o.\"orderDate\", o.\"status\", c.\"country\" FROM orders o JOIN customers c ON o.\"customerNumber\" = c.\"customerNumber\" WHERE c.\"country\" = 'Germany'",
    "total_row_count": 7,
    "result": [
      {
        "orderNumber": 10165,
        "orderDate": "2003-10-22",
        "status": "Shipped",
        "country": "Germany"
      }
      // Capped to first 10 rows for payload efficiency...
    ],
    "status": "success"
  }
]
```
