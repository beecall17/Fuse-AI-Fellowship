import os
import json
import time
import argparse
from query_decomposition import parse_schema
from sql_pipeline import run_full_pipeline, gen_logger, exec_logger

def main():
    parser = argparse.ArgumentParser(description="SQL Pipeline Runner: Decomposition, Generation, & Execution")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of questions to process")
    parser.add_argument("--force", action="store_true", help="Force overwrite of existing executions")
    args = parser.parse_args()

    print("=" * 60)
    print("        TEXT-TO-SQL PIPELINE EXECUTION ENGINE")
    print("=" * 60)

    # Resolve paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(base_dir, "Scripts", "seed.sql")
    if not os.path.exists(sql_path):
        sql_path = os.path.join(base_dir, "scripts", "seed.sql")
        
    decomp_path = os.path.join(base_dir, "Scripts", "query_decompositions.json")
    if not os.path.exists(decomp_path):
        decomp_path = os.path.join(base_dir, "scripts", "query_decompositions.json")
        
    output_path = os.path.join(base_dir, "Scripts", "query_executions.json")

    # 1. Parse Schema
    print(f"[*] Parsing database schema from: {sql_path}")
    try:
        schema = parse_schema(sql_path)
        print(f"[+] Loaded {len(schema)} tables for schema context.")
    except Exception as e:
        print(f"[!] Schema parse error: {e}")
        return

    # Convert schema to description
    schema_desc_lines = []
    for table_name, cols in schema.items():
        schema_desc_lines.append(f"Table '{table_name}': {', '.join(cols)}")
    schema_desc = "\n".join(schema_desc_lines)

    # 2. Load Decompositions
    print(f"[*] Loading decompositions from: {decomp_path}")
    if not os.path.exists(decomp_path):
        print(f"[!] Warning: decompositions cache file not found at {decomp_path}")
        print("[*] The system will dynamically decompose all questions.")
        decompositions = []
    else:
        try:
            with open(decomp_path, 'r', encoding='utf-8') as f:
                decompositions = json.load(f)
            print(f"[+] Loaded {len(decompositions)} decompositions.")
        except Exception as e:
            print(f"[!] Error reading decompositions file: {e}")
            decompositions = []

    # 3. Load Existing Executions for Caching / Resuming
    existing_executions = []
    processed_questions = set()
    if os.path.exists(output_path) and not args.force:
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_executions = json.load(f)
                processed_questions = {d['question'] for d in existing_executions if 'question' in d}
                print(f"[+] Loaded {len(existing_executions)} existing executions from cache.")
        except Exception as e:
            print(f"[!] Error reading executions cache: {e}. Starting fresh.")
            existing_executions = []

    # 4. Limit if specified
    if args.limit:
        decompositions = decompositions[:args.limit]
        print(f"[*] Limited pipeline to first {args.limit} queries.")

    results = list(existing_executions)
    newly_processed = 0
    skipped = 0

    print("\n[*] Starting Batch Pipeline Execution...")
    for idx, item in enumerate(decompositions, 1):
        question = item.get("question")
        if not question:
            continue
            
        if question in processed_questions and not args.force:
            print(f"[{idx}/{len(decompositions)}] Skipped: '{question}' (already executed)")
            skipped += 1
            continue

        print(f"[{idx}/{len(decompositions)}] Processing: '{question}'")
        
        # Call full pipeline (dynamic re-decomposition is built-in if intent or tables are faulty)
        output = run_full_pipeline(question, item, schema_desc)
        
        # If question was already in results, update it; otherwise append
        existing_index = next((i for i, r in enumerate(results) if r['question'] == question), None)
        if existing_index is not None:
            results[existing_index] = output
        else:
            results.append(output)
            
        newly_processed += 1
        
        print(f"  -> Casing: {output['status'].upper()}")
        print(f"  -> Generated SQL: {output['sql']}")
        print(f"  -> Total Row Count: {output['total_row_count']}")
        if "error" in output and output["error"]:
            print(f"  -> [!] Error: {output['error']}")
            
        # Incremental Save
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"  [!] Failed to save execution progress: {e}")

        # Rate limit prevention sleep
        time.sleep(0.8)

    print("\n" + "=" * 60)
    print("                  PIPELINE RUN COMPLETE")
    print("=" * 60)
    print(f"[+] Total questions: {len(decompositions)}")
    print(f"[+] Newly executed:  {newly_processed}")
    print(f"[+] Skipped cache:   {skipped}")
    print(f"[+] Saved output to: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
