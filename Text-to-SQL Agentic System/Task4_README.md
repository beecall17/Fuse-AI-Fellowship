# Task 4: FastAPI SQL Agent Service Documentation

This document describes the high-performance containerized REST API service built for the Text-to-SQL Agentic System. It has been integrated into the Docker Compose network and offers robust input guardrails, safety filters, up to 3 self-correction retry attempts, and natural language summarization.

---

## 🛠️ API Specification

### **POST `/agent/sql`**
Processes a natural language question and compiles it into a safe, executing SQL statement against the classicmodels database.

* **Request Format (JSON):**
  ```json
  {
    "question": "How many customers are from Germany?"
  }
  ```

* **Response Format (JSON):**
  ```json
  {
    "sql": "SELECT COUNT(\"customerNumber\") FROM customers WHERE \"country\" = 'Germany'",
    "result": 3,
    "summary": "There are 3 customers from Germany.",
    "status": "success"
  }
  ```

---

## 🛡️ Enterprise Guardrail Architecture

### 1. Relevance Intent Guardrail
Before submitting the question to LLM processing, the API runs the input through a preloaded schema classifier.
* **Database-Related Questions**: Continue directly to Prompt 1 (Decomposition).
* **Irrelevant/Chit-chat Questions** (e.g. *"What is the capital of France?"*): Blocked immediately with status `failure` and a helpful response suggesting valid topic queries (e.g. products, customers, order details, payments).
  * *Response summary output:* `"Cannot perform 'user input', instead use predefined our question or showing that. (Hint: ...)"`

### 2. Mutation Safety Guardrail (SELECT-only)
* Blocks mutating statements such as `DELETE`, `UPDATE`, `DROP`, `INSERT`, `CREATE` case-insensitively.
* Pre-generation: Analyzes the natural language question and returns `Cannot perform this operations, only SELECT is allowed.` if keywords are present.
* Post-generation: Passes the compiled SQL query through a syntax engine. If any mutation statements are generated, execution is blocked.

### 3. Automatic Self-Correction Retry (Up to 3 Max)
* If query execution fails at the database level (e.g., column ambiguity, syntax deviations), the API reads the exact PostgreSQL error traceback.
* Sends the error and failing SQL statement to the **Prompt 3 Self-Correction Agent**.
* Automatically retries the execution loop up to **3 times maximum**.
* Precise execution timings (`time.perf_counter()`), decomposition steps, and SQL generation logs are output directly to `logs/sql_generation.log` and `logs/sql_execution.log`.

### 4. Natural Language Summarizer
* Translates raw records and totals into a beautiful, human-sounding sentence (`"summary"` key) via a final Groq summarization prompt.

---

## 🚀 How to Run the Environment

All three services (PostgreSQL Database on port 5433, Streamlit on port 8501, and FastAPI on port 8000) run simultaneously in Docker.

```bash
# 1. Stop any existing base container setups
docker compose down -v

# 2. Build and start the unified environment
docker compose up --build -d
```

---

## 🧪 Running the Verification Test Suite

We have written a dedicated verification client to test all integration scenarios (valid queries, blocked deletions, blocked weather chit-chat, and ambiguous column auto-healing).

Run the test suite on the host machine:
```bash
python test_fastapi_agent.py
```

### Expected Output
```text
============================================================
         TESTING FASTAPI TEXT-TO-SQL REST ENDPOINT
============================================================

[*] TEST 1: Valid database query...
[+] Status:  success
[+] SQL:     SELECT COUNT("orderNumber") FROM orders
[+] Result:  326
[+] Summary: There is a total of 326 orders that have been placed.

[*] TEST 2: Mutation guardrail block...
[+] Status:  failure
[+] Result:  None
[+] Summary: Cannot perform this operations, only SELECT is allowed.
[+] Status: PASS (Safety validator successfully caught mutation statement)

[*] TEST 3: Irrelevant question guardrail block...
[+] Status:  failure
[+] Summary: Cannot perform "What is the weather like in New York today?", instead use predefined our question or showing that. (Hint: Our database is designed to...)
[+] Status: PASS (Successfully caught irrelevant database question)

[*] TEST 4: Self-correction retry of ambiguous columns...
[+] Status:  success
[+] SQL:     SELECT "customers"."customerNumber", SUM("amount") FROM "customers" ...
[+] Result (capped to 5 shown): [{'customerNumber': 455, 'sum': 70378.65}, ...]
[+] Summary: The database contains total payment information for 98 customers...
[+] Status: PASS (Successfully self-corrected and executed!)

============================================================
```
