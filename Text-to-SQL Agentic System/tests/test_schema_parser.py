import re
import os
import json

def parse_schema(sql_file_path):
    if not os.path.exists(sql_file_path):
        print(f"Error: SQL file not found at {sql_file_path}")
        return None
        
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
        # Find column names. We match words in double quotes at the start of a line/section,
        # or alphanumeric column names, followed by their type declaration.
        # We explicitly exclude SQL keywords that define constraints.
        col_lines = [line.strip() for line in columns_def.split('\n') if line.strip()]
        
        for line in col_lines:
            # Check for column definition, typically starting with "columnName" or columnName
            # Example: "productLine" VARCHAR(50) PRIMARY KEY,
            # We want to match either "name" or name as the first token
            # Ignore constraint lines like PRIMARY KEY, FOREIGN KEY, CONSTRAINT, etc.
            upper_line = line.upper()
            if any(upper_line.startswith(keyword) for keyword in ['PRIMARY KEY', 'FOREIGN KEY', 'CONSTRAINT', 'UNIQUE', 'CHECK']):
                continue
                
            match_col = re.match(r'^(?:"([^"]+)"|([a-zA-Z_]\w*))\s+([A-Za-z0-9_(), ]+)', line)
            if match_col:
                col_name = match_col.group(1) or match_col.group(2)
                if col_name.upper() not in ('PRIMARY', 'FOREIGN', 'KEY', 'CONSTRAINT', 'UNIQUE', 'CHECK'):
                    columns.append(col_name)
                    
        schema[table_name] = columns
    return schema

if __name__ == "__main__":
    # Test path
    path = os.path.join("Scripts", "seed.sql")
    if not os.path.exists(path):
        # Fallback to Task 3 path
        path = os.path.join("scripts", "seed.sql")
        
    print(f"Parsing schema from {path}...")
    schema = parse_schema(path)
    if schema:
        print("\nSuccessfully Parsed Schema:")
        print(json.dumps(schema, indent=2))
    else:
        print("Failed to parse schema.")
