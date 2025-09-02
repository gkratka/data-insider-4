"""
Phase 3: Smart Code Generation - LLM-generated pandas code
Minimal implementation with safety constraints
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import google.generativeai as genai
import os


def generate_pandas_code(query: str, columns: list, sample_data: dict, gemini_model=None) -> str:
    """Generate pandas code using LLM with safety constraints - 30 lines max"""
    
    if not gemini_model:
        return "# Error: Gemini model not available"
    
    prompt = f"""Generate pandas code for: "{query}"

Available columns: {columns}
Sample data (first 3 rows): {sample_data}

STRICT RULES:
- Use variable name 'df' for the dataframe
- Only use pandas and numpy operations
- Return only executable Python code, no explanations
- Handle potential errors gracefully
- No file system operations
- No external network calls
- No import statements

Example format:
result = df.groupby('category').sum()"""
    
    try:
        response = gemini_model.generate_content(prompt)
        code = response.text.strip()
        
        # Clean up the response - remove markdown formatting
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].strip()
            
        return code
    except Exception as e:
        return f"# Error generating code: {str(e)}"


def is_complex_query(query: str) -> bool:
    """Detect if query needs LLM code generation - 8 lines"""
    complex_keywords = [
        'calculate', 'compute', 'analysis', 'compare', 'find',
        'percentage', 'ratio', 'total', 'sum', 'aggregate',
        'customers', 'purchase', 'sales', 'revenue'
    ]
    
    return any(keyword in query.lower() for keyword in complex_keywords)