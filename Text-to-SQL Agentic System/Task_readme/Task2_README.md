# SQL Query Decomposition System

A highly optimized and robust Python automation system that parses natural language questions and decomposes them into structured SQL components (Intent, Tables, Columns, Filters, and Joins) utilizing the **Groq API** and schema information from a PostgreSQL database seed file.

---

## 🌟 Key Features

- **Automated Schema Parsing:** Dynamically parses the database schema (tables and columns) directly from your `seed.sql` script, ensuring alignment with downstream operations.
- **Groq Integration:** Employs the `openai` SDK mapped to Groq's API base (`https://api.groq.com/openai/v1`) using standard high-speed models like `llama-3.3-70b-versatile` or `gemma2-9b-it`.
- **Incremental Processing & Persistence:** Saves progress continuously to `query_decompositions.json`. If a run is interrupted or rate-limited, it automatically resumes where it left off, avoiding redundant API costs.
- **Robust Rate-Limit & Error Recovery:** Gracefully handles rate limits and API interruptions with exponential backoff retry mechanisms.
- **Inline Comment Sanitizer:** Safely strips any trailing comments in your `.env` file (e.g. `# from console.groq.com`) to prevent authentication anomalies.
- **Clean Command Line Flags:** 
  - `--limit N`: Restrict processing to the first `N` questions (ideal for rapid dry-runs).
  - `--force`: Reprocess all questions and overwrite previous entries in the output file.

---

## 📂 Project Structure

```text
Text-to-SQL Agentic System/
├── .env                         # Local environment settings (Groq API key)
├── .env.example                 # Template for environment settings
├── query_decomposition.py       # Main automation script
├── README.md                    # Project documentation
└── Scripts/
    ├── seed.sql                 # PostgreSQL database seed & schema definition
    ├── sql_questions.csv        # List of natural language questions to analyze
    └── query_decompositions.json # Generated structured decomposition output
```

---

## 🛠️ Setup & Configuration

### 1. Prerequisites
Ensure you have Python 3.8+ installed along with the required libraries:
```bash
pip install openai python-dotenv
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your Groq API key:
```bash
cp .env.example .env
```

Open `.env` and enter your credentials:
```ini
# Groq API Configuration
GROQ_API_KEY=gsk_your_real_groq_api_key_here
GROQ_API_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## 🚀 Usage

### 🚀 Running the Full System
To run query decomposition against all 50 questions in the CSV file:
```bash
python query_decomposition.py
```

### 🧪 Run a Quick Dry Run (Limit 3 Questions)
To process only the first 3 questions to verify API keys and correct output parsing:
```bash
python query_decomposition.py --limit 3
```

### 🔄 Force Re-processing
If you want to bypass the incremental cache and re-query the Groq API for all questions:
```bash
python query_decomposition.py --force
```

---

## 📊 Structured Output Format

The decompositions are written directly to `Scripts/query_decompositions.json` in a beautifully formatted JSON structure.

### Output JSON Example

```json
[
  {
    "question": "How many customers are from the USA?",
    "Intent": "Count total customers",
    "Tables": "customers",
    "Columns": "customerNumber",
    "Filters": "country = 'USA'",
    "Joins": "None"
  },
  {
    "question": "Get employees and their office cities",
    "Intent": "Retrieve employee names along with their office cities",
    "Tables": [
      "employees",
      "offices"
    ],
    "Columns": [
      "firstName",
      "lastName",
      "city"
    ],
    "Filters": "None",
    "Joins": "employees.officeCode = offices.officeCode"
  }
]
```

---

## 🛡️ Premium Implementation Features

- **Strict Schema Enforcement:** Decomposed table names and column names are cross-referenced with the parsed DB schema, preventing hallucinations.
- **Fail-safe Fallback:** If Groq returns invalid JSON or experiences API issues, the system automatically falls back to clean, predictable default state markers (e.g., `"None"`) and notes the error in the console.
- **Double-quote and Case Sanitizer:** Correctly extracts quoted identifiers (e.g., `"productLine"`) from SQL tables.
