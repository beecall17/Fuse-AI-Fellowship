# Fix script for Order schema field validator syntax

import re

def fix_order_schema():
    """Fix field validator syntax in order.py"""
    
    with open('app/schemas/order.py', 'r') as f:
        content = f.read()
    
    # Fix field validator syntax - add quotes around field names
    # Pattern: @field_validator('fieldName') -> @field_validator('fieldName')
    patterns = [
        (r"@field_validator\('([^']+)', '([^']+)'\)", lambda m: f"@field_validator('{m.group(1)}', '{m.group(2)}')"),
        (r"@field_validator\('([^']+)'\)", lambda m: f"@field_validator('{m.group(1)}')"),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    with open('app/schemas/order.py', 'w') as f:
        f.write(content)
    
    print("Fixed Order schema field validator syntax")

if __name__ == "__main__":
    fix_order_schema()
