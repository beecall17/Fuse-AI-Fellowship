import os
import re
import json
import time
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# Import core structures from our pipeline
from sql_pipeline import (
    run_full_pipeline,
    execute_query,
    is_query_safe,
    generate_sql_query,
    fix_sql_query,
    decompose_question,
    client,
    MODEL,
    gen_logger,
    exec_logger
)
from query_decomposition import parse_schema

# Load env variables
load_dotenv()

# Initialize FastAPI App
app = FastAPI(
    title="Text-to-SQL FastAPI Agent Service",
    description="REST API for structured text-to-SQL decomposition, execution, self-correction, and natural language summary.",
    version="1.0.0"
)

# Request schema
class SQLAgentRequest(BaseModel):
    question: str

# Response schema
class SQLAgentResponse(BaseModel):
    sql: str | None
    result: list | dict | int | None
    summary: str
    status: str

# Resolve database schema paths
base_dir = os.path.dirname(os.path.abspath(__file__))
sql_path = os.path.join(base_dir, "Scripts", "seed.sql")
if not os.path.exists(sql_path):
    sql_path = os.path.join(base_dir, "scripts", "seed.sql")

# Preload schema constraints
try:
    schema = parse_schema(sql_path)
    schema_desc_lines = []
    for table, cols in schema.items():
        schema_desc_lines.append(f"Table '{table}': {', '.join(cols)}")
    schema_desc = "\n".join(schema_desc_lines)
except Exception as e:
    schema = {}
    schema_desc = ""

def check_database_relevance(question: str) -> tuple[bool, str]:
    """
    Guardrail: Checks if the input question relates to the preloaded database schema.
    """
    if not client:
        return True, ""
        
    prompt = f"""You are a Database Intent Guardrail. Your sole task is to analyze if a user's natural language question is relevant to the provided database schema tables and columns.

Database Schema (Tables and Columns):
{schema_desc}

User Input: "{question}"

Instructions:
1. Determine if the question asks for information that can be answered using the tables and columns in the schema (e.g. products, customers, order details, employees, payments).
2. If it is relevant, respond ONLY with "RELEVANT".
3. If it is completely unrelated to the database (e.g. chit-chat, math, coding, weather, general history), respond with "IRRELEVANT" followed by a short, helpful explanation of what our database can do.

Response format:
RELEVANT
OR
IRRELEVANT: [Short explanation of what questions to ask based on tables]
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a database guardrail assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        res = response.choices[0].message.content.strip()
        if res.upper().startswith("RELEVANT"):
            return True, ""
        
        if ":" in res:
            reason = res.split(":", 1)[1].strip()
        else:
            reason = res
        return False, reason
    except Exception as e:
        # Fallback to true in case of API failure so processing can proceed
        return True, ""

def generate_summary(question: str, result_rows: list, total_count: int) -> str:
    """
    Generates a high-quality natural language summary of the returned rows based on the original question.
    """
    if not client:
        return f"Successfully executed query. Returned {total_count} records."
        
    sample_data = json.dumps(result_rows[:10], indent=2)
    
    prompt = f"""You are a Data Summary Specialist.
Your task is to write a single-sentence, professional, and natural-sounding summary of the database query results that directly answers the user's question.

User Question: "{question}"
Total Records Found: {total_count}
Sample Records (First 10):
{sample_data}

Instructions:
1. Provide a single direct sentence answering the question (e.g. "There are 42 shipped orders from customers in USA.").
2. Keep it natural, factual, and strictly aligned with the sample data and total row count.
3. Respond ONLY with the sentence. Do not include introductory phrases or explanations.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a professional database summary generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Retrieved {total_count} rows from the database successfully."

@app.post("/agent/sql", response_model=SQLAgentResponse)
async def process_sql_agent(request: SQLAgentRequest):
    question = request.question.strip()
    
    # 1. Guardrail - DDL/DML mutation keyword block
    forbidden = ["DELETE", "DROP", "UPDATE", "INSERT", "TRUNCATE", "ALTER", "CREATE", "GRANT", "REVOKE"]
    q_upper = question.upper()
    for keyword in forbidden:
        if re.search(r'\b' + keyword + r'\b', q_upper):
            return SQLAgentResponse(
                sql=None,
                result=None,
                summary="Cannot perform this operations, only SELECT is allowed.",
                status="failure"
            )
            
    # 2. Guardrail - Database relevance verification
    is_relevant, fallback_reason = check_database_relevance(question)
    if not is_relevant:
        return SQLAgentResponse(
            sql=None,
            result=None,
            summary=f"Cannot perform \"{question}\", instead use predefined our question or showing that. (Hint: {fallback_reason})",
            status="failure"
        )

    # 3. Prompt 1 - Structured Decomposition
    try:
        decomposition = decompose_question(question, schema_desc)
        # Log decomposition step
        gen_logger.info(f"FastAPI Decomposition Step: {json.dumps(decomposition)}")
    except Exception as e:
        gen_logger.error(f"FastAPI Decomposition failed: {e}")
        return SQLAgentResponse(
            sql=None,
            result=None,
            summary="Failed to decompose natural language question into schema coordinates.",
            status="failure"
        )
        
    # 4. Prompt 2 - SQL Query Generation
    try:
        sql = generate_sql_query(question, decomposition, schema_desc)
        # Log generation step
        gen_logger.info(f"FastAPI Generated SQL: {sql}")
    except Exception as e:
        gen_logger.error(f"FastAPI SQL Generation failed: {e}")
        return SQLAgentResponse(
            sql=None,
            result=None,
            summary="Failed to generate SQL query from decomposition steps.",
            status="failure"
        )

    # 5. Safe Query Validation Gate
    is_safe, reason = is_query_safe(sql)
    if not is_safe:
        return SQLAgentResponse(
            sql=sql,
            result=None,
            summary=f"Cannot perform this operations, only SELECT is allowed. (Reason: {reason})",
            status="failure"
        )

    # 6. Database Execution Loop with Prompt 3 Self-Correction Retry (Up to 3 times maximum)
    max_attempts = 3
    attempt = 1
    current_sql = sql
    exec_result = None
    execution_time = 0.0
    
    while attempt <= max_attempts:
        start_time = time.perf_counter()
        exec_result = execute_query(current_sql)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        # Log execution details and timings
        exec_logger.info(
            f"FastAPI Query Execution - Attempt {attempt} | Time: {execution_time:.4f}s | "
            f"Status: {exec_result['status']} | SQL: {current_sql}"
        )
        
        if exec_result["status"] == "success":
            break
            
        # Self-correction (Prompt 3 retry)
        error_msg = exec_result["error"]
        if attempt < max_attempts:
            gen_logger.warning(f"FastAPI Attempt {attempt} failed: {error_msg}. Fixing query...")
            try:
                current_sql = fix_sql_query(question, decomposition, current_sql, error_msg, schema_desc)
                attempt += 1
            except Exception as e:
                gen_logger.error(f"FastAPI Self-correction exception: {e}")
                break
        else:
            break

    # 7. Fallback if all attempts fail
    if exec_result["status"] == "failure":
        return SQLAgentResponse(
            sql=current_sql,
            result=None,
            summary=f"All {max_attempts} execution attempts failed. Database Error: {exec_result.get('error')}",
            status="failure"
        )

    # 8. Success Formatting (Cap to first 10 rows)
    rows = exec_result["result"]
    total_count = exec_result["total_row_count"]
    
    # Generate Natural Language Summary via LLM
    summary = generate_summary(question, rows, total_count)
    
    # If the question was a simple scalar count (e.g. "Total number of customers"), return the number directly
    if total_count == 1 and len(rows) == 1:
        # Check if the single row has a single column containing a numeric count
        row_dict = rows[0]
        if len(row_dict) == 1:
            val = list(row_dict.values())[0]
            if isinstance(val, (int, float)):
                return SQLAgentResponse(
                    sql=current_sql,
                    result=val,
                    summary=summary,
                    status="success"
                )

    return SQLAgentResponse(
        sql=current_sql,
        result=rows,  # Capped to 10 rows in execute_query
        summary=summary,
        status="success"
    )
