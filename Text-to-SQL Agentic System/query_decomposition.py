import os
import re
import csv
import json
import time
import argparse
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def parse_schema(sql_file_path):
    """
    Parses seed.sql and returns a dictionary of {table_name: [column_names]}.
    """
    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"SQL file not found at {sql_file_path}")
        
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove single line comments
    content = re.sub(r'--.*', '', content)
    # Remove block comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Find all CREATE TABLE statements
    create_table_regex = re.compile(
        r'CREATE\s+TABLE\s+(\w+)\s*\((.*?)\);', 
        re.DOTALL | re.IGNORECASE
    )
    
    schema = {}
    for match in create_table_regex.finditer(content):
        table_name = match.group(1)
        columns_def = match.group(2)
        
        columns = []
        # Parse column lines
        col_lines = [line.strip() for line in columns_def.split('\n') if line.strip()]
        for line in col_lines:
            upper_line = line.upper()
            # Ignore lines declaring constraints
            if any(upper_line.startswith(keyword) for keyword in ['PRIMARY KEY', 'FOREIGN KEY', 'CONSTRAINT', 'UNIQUE', 'CHECK']):
                continue
                
            match_col = re.match(r'^(?:"([^"]+)"|([a-zA-Z_]\w*))\s+([A-Za-z0-9_(), ]+)', line)
            if match_col:
                col_name = match_col.group(1) or match_col.group(2)
                if col_name.upper() not in ('PRIMARY', 'FOREIGN', 'KEY', 'CONSTRAINT', 'UNIQUE', 'CHECK'):
                    columns.append(col_name)
                    
        schema[table_name] = columns
    return schema

def load_questions(csv_file_path):
    """
    Reads the questions from a CSV file.
    Assumes a header row exists and contains a column named 'question'.
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"Questions CSV file not found at {csv_file_path}")
        
    questions = []
    with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'question' in row and row['question'].strip():
                questions.append(row['question'].strip())
            elif len(row) > 0:
                # Fallback if header doesn't match perfectly
                first_val = list(row.values())[0]
                if first_val and first_val.strip():
                    questions.append(first_val.strip())
    return questions

def get_decomposition(client, model, question, schema_desc):
    """
    Calls the Grok API using OpenAI-compatible SDK and returns the structured JSON decomposition.
    """
    system_prompt = f"""You are an expert SQL Query Decomposition Assistant. Your task is to analyze natural language questions and decompose them into structured SQL components based ONLY on the provided database schema.

Database Schema (Tables and Columns):
{schema_desc}

Decomposition Guidelines:
1. Intent: Define what the question is asking in a short, descriptive phrase (e.g. "Count total customers", "Retrieve all product details").
2. Tables: Identify the tables involved. They MUST exist in the schema. Represent as a string (if single table) or a list of strings (if multiple tables).
3. Columns: Identify the specific columns needed. They MUST exist in the tables identified. Represent as a string (if single column) or a list of strings (if multiple columns).
4. Filters: Specify any conditions or filters implied by the question (e.g., "country = 'USA'", "buyPrice > 100"). If no filters exist, use "None".
5. Joins: Identify any joins required between tables. Specify the join condition if applicable (e.g., "employees.officeCode = offices.officeCode"). If no joins are needed, use "None".

Example:
Question: How many customers are from the USA?
Output JSON format:
{{
  "Intent": "Count total customers",
  "Tables": "customers",
  "Columns": "customerNumber",
  "Filters": "country = 'USA'",
  "Joins": "None"
}}

Another Example:
Question: Get employees and their office cities
Output JSON format:
{{
  "Intent": "Retrieve employee names along with their office cities",
  "Tables": ["employees", "offices"],
  "Columns": ["firstName", "lastName", "city"],
  "Filters": "None",
  "Joins": "employees.officeCode = offices.officeCode"
}}

Ensure that all returned table and column names exactly match the casing and spelling in the schema.
You must respond with a raw JSON block only. Do not wrap in markdown block (like ```json), and do not include any explanatory text before or after the JSON.
"""

    max_retries = 3
    base_delay = 2
    for attempt in range(max_retries):
        try:
            # We use a standard chat completion call
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Decompose the following question:\n{question}"}
                ],
                temperature=0.0
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up potential markdown wrapper from model response
            if content.startswith("```"):
                content = re.sub(r'^```(?:json)?\n', '', content)
                content = re.sub(r'\n```$', '', content)
            content = content.strip()
            
            # Parse the JSON
            decomposition = json.loads(content)
            
            # Validate required keys
            required_keys = ["Intent", "Tables", "Columns", "Filters", "Joins"]
            for key in required_keys:
                if key not in decomposition:
                    decomposition[key] = "None"
                    
            return decomposition
            
        except json.JSONDecodeError as je:
            print(f"  [Attempt {attempt+1}/{max_retries}] JSON parse error. Retrying... Output was: {content[:100]}")
            time.sleep(base_delay * (attempt + 1))
        except Exception as e:
            print(f"  [Attempt {attempt+1}/{max_retries}] API error: {e}. Retrying...")
            time.sleep(base_delay * (attempt + 1))
            
    # Return placeholder on failure
    return {
        "Intent": "Error decomposing question",
        "Tables": "None",
        "Columns": "None",
        "Filters": "None",
        "Joins": "None",
        "Error": "Failed to get response from API"
    }

def main():
    parser = argparse.ArgumentParser(description="SQL Query Decomposition System using Groq API")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of questions to process")
    parser.add_argument("--force", action="store_true", help="Force overwrite of existing decompositions")
    args = parser.parse_args()

    print("=" * 60)
    print("        SQL QUERY DECOMPOSITION SYSTEM (GROQ)")
    print("=" * 60)

    # Resolve paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(base_dir, "Scripts", "seed.sql")
    if not os.path.exists(sql_path):
        sql_path = os.path.join(base_dir, "scripts", "seed.sql")
        
    csv_path = os.path.join(base_dir, "Scripts", "sql_questions.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(base_dir, "scripts", "sql_questions.csv")
        
    output_path = os.path.join(base_dir, "Scripts", "query_decompositions.json")
    
    # 1. Parse Schema
    print(f"[*] Parsing database schema from: {sql_path}")
    try:
        schema = parse_schema(sql_path)
        print(f"[+] Loaded {len(schema)} tables: {', '.join(schema.keys())}")
    except Exception as e:
        print(f"[!] Schema parse error: {e}")
        return

    # Convert schema to structured format for prompt
    schema_desc_lines = []
    for table_name, cols in schema.items():
        schema_desc_lines.append(f"Table '{table_name}': {', '.join(cols)}")
    schema_desc = "\n".join(schema_desc_lines)

    # 2. Load Questions
    print(f"[*] Loading questions from: {csv_path}")
    try:
        questions = load_questions(csv_path)
        print(f"[+] Loaded {len(questions)} questions.")
    except Exception as e:
        print(f"[!] Questions load error: {e}")
        return

    if args.limit:
        questions = questions[:args.limit]
        print(f"[*] Limited execution to first {args.limit} questions.")

    # 3. Setup API Client
    api_key = (
        os.environ.get("GROQ_API_KEY") or 
        os.environ.get("GROK_API_KEY") or 
        os.environ.get("XAI_API_KEY")
    )
    
    # Sanitize inline comments if present in the environment value
    if api_key:
        api_key = api_key.split('#')[0].strip()
        
    is_placeholder = not api_key or any(p in api_key for p in ["your_groq", "your_xai", "placeholder"])
    if is_placeholder:
        print("[!] Warning: GROQ_API_KEY/GROK_API_KEY is not set or has placeholder value in .env")
        print("[*] Please update the .env file with your valid API key.")
        import sys
        if sys.stdin.isatty():
            api_key = input("Enter your API Key (or press Enter to exit): ").strip()
            if not api_key:
                print("[*] Exiting.")
                return
        else:
            print("[!] Running in a non-interactive shell. Cannot prompt for key. Please write the key to .env.")
            print("[*] Exiting.")
            return

    base_url = os.environ.get("GROQ_API_URL") or os.environ.get("GROK_API_URL") or "https://api.groq.com/openai/v1"
    model = os.environ.get("GROQ_MODEL") or os.environ.get("GROK_MODEL") or "llama-3.3-70b-versatile"
    
    if base_url:
        base_url = base_url.split('#')[0].strip()
    if model:
        model = model.split('#')[0].strip()
    
    print(f"[*] Initializing client using model: '{model}'")
    print(f"[*] API Base URL: {base_url}")
    client = OpenAI(api_key=api_key, base_url=base_url)

    # 4. Load Existing Decompositions for Incremental Save/Update
    existing_decompositions = []
    processed_questions = set()
    
    if os.path.exists(output_path) and not args.force:
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_decompositions = json.load(f)
                processed_questions = {d['question'] for d in existing_decompositions if 'question' in d}
                print(f"[+] Loaded {len(existing_decompositions)} existing decompositions from {output_path}")
        except Exception as e:
            print(f"[!] Error reading existing JSON output: {e}. Starting fresh.")
            existing_decompositions = []

    # 5. Process Questions
    results = list(existing_decompositions)
    success_count = 0
    skipped_count = 0

    print("\n[*] Starting Decomposition Loop...")
    for idx, question in enumerate(questions, 1):
        if question in processed_questions and not args.force:
            print(f"[{idx}/{len(questions)}] Skipped: '{question}' (already processed)")
            skipped_count += 1
            continue

        print(f"[{idx}/{len(questions)}] Processing: '{question}'")
        
        # Call Grok
        decomposition = get_decomposition(client, model, question, schema_desc)
        
        # Format the item
        result_item = {
            "question": question,
            "Intent": decomposition.get("Intent", "None"),
            "Tables": decomposition.get("Tables", "None"),
            "Columns": decomposition.get("Columns", "None"),
            "Filters": decomposition.get("Filters", "None"),
            "Joins": decomposition.get("Joins", "None")
        }
        
        # If the question was already in results, update it; otherwise append
        existing_index = next((i for i, r in enumerate(results) if r['question'] == question), None)
        if existing_index is not None:
            results[existing_index] = result_item
        else:
            results.append(result_item)
            
        success_count += 1
        
        # Print info
        print(f"  -> Intent: {result_item['Intent']}")
        print(f"  -> Tables: {result_item['Tables']}")
        print(f"  -> Columns: {result_item['Columns']}")
        print(f"  -> Filters: {result_item['Filters']}")
        print(f"  -> Joins: {result_item['Joins']}")
        
        # Save incrementally
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"  [!] Failed to save progress to JSON: {e}")

        # Sleep to avoid hitting rate limits
        time.sleep(0.8)

    print("\n" + "=" * 60)
    print("                  DECOMPOSITION COMPLETE")
    print("=" * 60)
    print(f"[+] Total questions: {len(questions)}")
    print(f"[+] Newly processed: {success_count}")
    print(f"[+] Skipped:         {skipped_count}")
    print(f"[+] Output saved to: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
