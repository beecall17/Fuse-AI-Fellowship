import os
import re
import json
import time
import logging
import psycopg2
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Setup logging directories
os.makedirs("logs", exist_ok=True)

# 1. SQL Generation Log
gen_logger = logging.getLogger("sql_generation")
gen_logger.setLevel(logging.INFO)
# Clear handlers if already present to avoid duplicate logging
if gen_logger.hasHandlers():
    gen_logger.handlers.clear()
gen_file_handler = logging.FileHandler("logs/sql_generation.log", encoding="utf-8")
gen_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
gen_file_handler.setFormatter(gen_formatter)
gen_logger.addHandler(gen_file_handler)

# 2. SQL Execution Log
exec_logger = logging.getLogger("sql_execution")
exec_logger.setLevel(logging.INFO)
if exec_logger.hasHandlers():
    exec_logger.handlers.clear()
exec_file_handler = logging.FileHandler("logs/sql_execution.log", encoding="utf-8")
exec_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
exec_file_handler.setFormatter(exec_formatter)
exec_logger.addHandler(exec_file_handler)

# Global Client configuration
API_KEY = os.environ.get("GROQ_API_KEY") or os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
if API_KEY:
    API_KEY = API_KEY.split('#')[0].strip()
BASE_URL = os.environ.get("GROQ_API_URL") or os.environ.get("GROK_API_URL") or "https://api.groq.com/openai/v1"
if BASE_URL:
    BASE_URL = BASE_URL.split('#')[0].strip()
MODEL = os.environ.get("GROQ_MODEL") or os.environ.get("GROK_MODEL") or "llama-3.3-70b-versatile"
if MODEL:
    model_env = MODEL.split('#')[0].strip()

# Initialize Client
client = None
if API_KEY and "your_groq" not in API_KEY and "your_xai" not in API_KEY:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def get_db_connection():
    """
    Returns a new synchronous PostgreSQL connection using env variables.
    """
    return psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB", "classicmodels"),
        user=os.environ.get("POSTGRES_USER", "app_user"),
        password=os.environ.get("POSTGRES_PASSWORD", "secure_password_123"),
        host=os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        port=os.environ.get("POSTGRES_PORT", "5433")
    )

def is_query_safe(sql: str) -> tuple[bool, str]:
    """
    Checks if a query contains only SELECT queries and blocks any DDL/DML.
    Returns (is_safe, error_reason).
    """
    cleaned_sql = sql.strip()
    upper_sql = cleaned_sql.upper()
    
    # Must start with SELECT or WITH
    if not (upper_sql.startswith("SELECT") or upper_sql.startswith("WITH")):
        return False, "Query must start with SELECT or WITH. Direct schema modifications are blocked."
        
    # Check for destructive/unauthorized words as whole words
    blocked_keywords = ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE", "REPLACE"]
    for keyword in blocked_keywords:
        if re.search(r'\b' + keyword + r'\b', upper_sql):
            return False, f"Unauthorized operation detected: '{keyword}' queries are strictly prohibited."
            
    return True, ""

def generate_sql_query(question: str, decomposition: dict, schema_desc: str) -> str:
    """
    Prompt 2: SQL Query Generation based on structured decomposition.
    """
    if not client:
        raise ValueError("LLM client not initialized. Please configure API keys.")
        
    prompt = f"""You are an expert PostgreSQL Query Generator.
Your task is to take a natural language question, its structured query decomposition, and the database schema, and generate a valid, highly-optimized PostgreSQL SELECT query.

Database Schema (Tables and Columns):
{schema_desc}

Structured Decomposition:
- Intent: {decomposition.get('Intent', 'None')}
- Tables involved: {decomposition.get('Tables', 'None')}
- Columns needed: {decomposition.get('Columns', 'None')}
- Filters/Conditions: {decomposition.get('Filters', 'None')}
- Joins needed: {decomposition.get('Joins', 'None')}

PostgreSQL Case Sensitivity Rule (CRITICAL):
PostgreSQL treats all table and column names as case-insensitive (lowercase) unless they are enclosed in double quotes.
For any mixed-case table or column names (such as "productLine", "productCode", "quantityInStock", "buyPrice", "MSRP", "customerNumber", "contactLastName", "contactFirstName", "salesRepEmployeeNumber", "creditLimit", "checkNumber", "paymentDate", "orderNumber", "orderDate", "requiredDate", "shippedDate", "quantityOrdered", "priceEach", "orderLineNumber"), you MUST enclose them in double quotes (e.g. \"productLine\") in the SELECT, JOIN, WHERE, GROUP BY, or ORDER BY statements. Regular lowercase names do not need quotes.

Example:
If columns needed are productCode and buyPrice from products, the SQL must look like:
SELECT "productCode", "buyPrice" FROM products;

Only SELECT statements are allowed.
Do not explain the code. Respond ONLY with the SQL query wrapped in a ```sql markdown block.
"""

    gen_logger.info(f"Generating SQL for question: '{question}' using model '{MODEL}'")
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a professional PostgreSQL specialist who writes precise SQL statements enclosed in ```sql blocks."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    
    raw_content = response.choices[0].message.content.strip()
    
    # Extract SQL from markdown block
    match = re.search(r"```sql\s*(.*?)\s*```", raw_content, re.DOTALL | re.IGNORECASE)
    if match:
        sql = match.group(1).strip()
    else:
        match_plain = re.search(r"```\s*(.*?)\s*```", raw_content, re.DOTALL)
        if match_plain:
            sql = match_plain.group(1).strip()
        else:
            sql = raw_content.strip()
            
    # Remove trailing semicolons for consistency
    if sql.endswith(";"):
        sql = sql[:-1].strip()
        
    gen_logger.info(f"Generated SQL: {sql}")
    return sql

def fix_sql_query(question: str, decomposition: dict, failed_sql: str, error_message: str, schema_desc: str) -> str:
    """
    Prompt 3: Fix SQL Query Errors (Self-Correction Retry).
    """
    if not client:
        raise ValueError("LLM client not initialized.")
        
    prompt = f"""You are a professional PostgreSQL debug engineer.
A generated SQL query has failed to execute due to a database-level runtime error.
Your task is to fix the query surgically so that it executes successfully against the database schema.

Database Schema:
{schema_desc}

Original Question: {question}
Decomposition:
- Intent: {decomposition.get('Intent', 'None')}
- Tables: {decomposition.get('Tables', 'None')}
- Columns: {decomposition.get('Columns', 'None')}
- Filters: {decomposition.get('Filters', 'None')}
- Joins: {decomposition.get('Joins', 'None')}

Failed SQL Query:
{failed_sql}

Database Error Message:
{error_message}

PostgreSQL Case Sensitivity Rule (CRITICAL):
PostgreSQL treats all table and column names as case-insensitive unless they are enclosed in double quotes.
For mixed-case identifiers (like "productLine", "productCode", "quantityOrdered", "priceEach", "customerNumber", etc.), you MUST enclose them in double quotes (e.g. \"productLine\") in the SELECT, JOIN, WHERE, GROUP BY, or ORDER BY statements.

Only SELECT statements are allowed.
Do not explain the fix. Respond ONLY with the corrected SQL query wrapped in a ```sql markdown block.
"""

    gen_logger.warning(f"Failed SQL detected: {failed_sql} | Error: {error_message}. Attempting self-correction.")
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a professional PostgreSQL debug engineer who writes precise corrected SQL statements enclosed in ```sql blocks."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    
    raw_content = response.choices[0].message.content.strip()
    
    match = re.search(r"```sql\s*(.*?)\s*```", raw_content, re.DOTALL | re.IGNORECASE)
    if match:
        sql = match.group(1).strip()
    else:
        match_plain = re.search(r"```\s*(.*?)\s*```", raw_content, re.DOTALL)
        if match_plain:
            sql = match_plain.group(1).strip()
        else:
            sql = raw_content.strip()
            
    if sql.endswith(";"):
        sql = sql[:-1].strip()
        
    gen_logger.info(f"Self-Corrected SQL: {sql}")
    return sql

def execute_query(sql: str) -> dict:
    """
    Executes a SELECT query against PostgreSQL.
    Logs execution results, handles safety checks, caps result list to first 10,
    and returns a structured dict of the query status.
    """
    exec_logger.info(f"Attempting execution of SQL: {sql}")
    
    # 1. Safety Check
    is_safe, reason = is_query_safe(sql)
    if not is_safe:
        err_msg = f"Safety Block: {reason}"
        exec_logger.error(err_msg)
        return {
            "status": "failure",
            "result": [],
            "total_row_count": 0,
            "error": err_msg
        }
        
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(sql)
        
        # Fetch columns from cursor description
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        total_rows = len(rows)
        
        # Convert rows into dictionary mappings for a highly-premium structured output
        results_dicts = []
        for row in rows[:10]:
            row_dict = {}
            for col_idx, col_name in enumerate(columns):
                val = row[col_idx]
                # Convert dates/decimals to strings to prevent JSON serialization errors
                if hasattr(val, 'isoformat'): # date/time
                    val = val.isoformat()
                elif hasattr(val, 'to_eng_string') or type(val).__name__ == 'Decimal': # Decimal
                    val = float(val)
                row_dict[col_name] = val
            results_dicts.append(row_dict)
            
        exec_logger.info(f"Execution Successful. Status: SUCCESS | Total Rows: {total_rows}")
        
        return {
            "status": "success",
            "result": results_dicts,
            "total_row_count": total_rows,
            "error": None
        }
        
    except Exception as e:
        err_msg = str(e)
        exec_logger.error(f"Execution Failed. Error: {err_msg}")
        return {
            "status": "failure",
            "result": [],
            "total_row_count": 0,
            "error": err_msg
        }
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def decompose_question(question: str, schema_desc: str) -> dict:
    """
    Prompt 1: Dynamically decomposes a natural language question.
    Used if cached decomposition is missing or contains errors.
    """
    if not client:
        raise ValueError("LLM client not initialized.")
        
    system_prompt = f"""You are an expert SQL Query Decomposition Assistant. Your task is to analyze natural language questions and decompose them into structured SQL components based ONLY on the provided database schema.

Database Schema (Tables and Columns):
{schema_desc}

Decomposition Guidelines:
1. Intent: Define what the question is asking in a short, descriptive phrase (e.g. "Count total customers", "Retrieve all product details").
2. Tables: Identify the tables involved. They MUST exist in the schema. Represent as a string (if single table) or a list of strings (if multiple tables).
3. Columns: Identify the specific columns needed. They MUST exist in the tables identified. Represent as a string (if single column) or a list of strings (if multiple columns).
4. Filters: Specify any conditions or filters implied by the question (e.g., "country = 'USA'", "buyPrice > 100"). If no filters exist, use "None".
5. Joins: Identify any joins required between tables. Specify the join condition if applicable (e.g., "employees.officeCode = offices.officeCode"). If no joins are needed, use "None".

You must respond with a raw JSON block only matching this schema. Do not wrap in markdown block (like ```json), and do not include any explanatory text.
"""

    gen_logger.info(f"Dynamically decomposing question: '{question}'")
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Decompose the following question:\n{question}"}
        ],
        temperature=0.0
    )
    
    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        content = re.sub(r'^```(?:json)?\n', '', content)
        content = re.sub(r'\n```$', '', content)
    content = content.strip()
    
    decomposition = json.loads(content)
    
    # Standardize keys to camelCase / PascalCase matching the requirements case-insensitively
    std_decomposition = {}
    for key, val in decomposition.items():
        lower_key = key.lower()
        if lower_key == "intent":
            std_decomposition["Intent"] = val
        elif lower_key == "tables":
            std_decomposition["Tables"] = val
        elif lower_key == "columns":
            std_decomposition["Columns"] = val
        elif lower_key == "filters":
            std_decomposition["Filters"] = val
        elif lower_key == "joins":
            std_decomposition["Joins"] = val
        else:
            std_decomposition[key] = val
            
    # Validate required keys
    required_keys = ["Intent", "Tables", "Columns", "Filters", "Joins"]
    for key in required_keys:
        if key not in std_decomposition:
            std_decomposition[key] = "None"
            
    return std_decomposition

def run_full_pipeline(question: str, decomposition: dict, schema_desc: str) -> dict:
    """
    Coordinates SQL Generation, execution safety check, database execution, and error self-correction.
    Maximum retry limit: 1 retry.
    """
    # Step 0: Ensure valid decomposition (dynamically re-decompose if needed)
    needs_decomposition = (
        not decomposition or 
        decomposition.get("Intent") == "Error decomposing question" or
        decomposition.get("Tables") == "None"
    )
    
    if needs_decomposition:
        try:
            decomposition = decompose_question(question, schema_desc)
            gen_logger.info(f"Successfully re-decomposed question dynamically: {decomposition}")
        except Exception as e:
            gen_logger.error(f"Failed dynamic decomposition for '{question}': {e}")
            if not decomposition:
                decomposition = {
                    "Intent": "Error decomposing question",
                    "Tables": "None",
                    "Columns": "None",
                    "Filters": "None",
                    "Joins": "None"
                }

    # Step 1: Generate SQL
    try:
        sql = generate_sql_query(question, decomposition, schema_desc)
    except Exception as e:
        gen_logger.error(f"SQL Generation exception: {e}")
        return {
            "question": question,
            "decompose": decomposition,
            "sql": None,
            "total_row_count": 0,
            "result": [],
            "status": "failure",
            "error": f"SQL Generation Failed: {e}"
        }
        
    # Step 2: Execute SQL
    exec_result = execute_query(sql)
    
    # Step 3: Self-Correction Loop (if failed, max 1 retry)
    if exec_result["status"] == "failure" and not exec_result["error"].startswith("Safety Block"):
        error_msg = exec_result["error"]
        
        # Self-correction (Prompt 3)
        try:
            corrected_sql = fix_sql_query(question, decomposition, sql, error_msg, schema_desc)
            # Retry execution once
            exec_result = execute_query(corrected_sql)
            sql = corrected_sql
        except Exception as e:
            gen_logger.error(f"Self-correction exception: {e}")
            exec_result = {
                "status": "failure",
                "result": [],
                "total_row_count": 0,
                "error": f"Self-correction failed: {e}"
            }
            
    # Construct final unified structured response matching user requirements
    final_output = {
        "question": question,
        "decompose": decomposition,
        "sql": sql,
        "total_row_count": exec_result["total_row_count"],
        "result": exec_result["result"],
        "status": exec_result["status"]
    }
    
    if exec_result["error"]:
        final_output["error"] = exec_result["error"]
        
    return final_output
