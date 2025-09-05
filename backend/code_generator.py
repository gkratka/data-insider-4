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
    
    prompt = f"""CRITICAL DATA REQUIREMENT: You MUST use the existing dataframe 'df' that contains the user's actual data.

STRICTLY FORBIDDEN:
- Creating new DataFrames with pd.DataFrame()
- Using sample/mock/fake data
- Importing pandas or numpy in generated code
- Any data fabrication or synthesis

REQUIRED APPROACH:
- Use only 'df' variable (pre-loaded with user data)
- Work with existing columns: {columns}
- Generate only the analysis logic, not data creation
- Reference actual column values from the provided sample
- ALWAYS print() the final result so users can see it

User query: "{query}"
Available columns: {columns}
Sample of actual data: {sample_data}

STRICT RULES:
- Return only executable Python code, no explanations
- Handle potential errors gracefully
- No file system operations
- No external network calls
- No import statements
- MUST end with print() statement to display result

Generate ONLY the pandas operation code using the pre-loaded 'df' variable:"""
    
    try:
        response = gemini_model.generate_content(prompt)
        code = response.text.strip()
        
        # Clean up the response - remove markdown formatting
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].strip()
        
        # Auto-wrap single expressions with print() if missing
        lines = code.strip().split('\n')
        if len(lines) == 1 and 'print(' not in code and not code.startswith('try:'):
            # Single expression - wrap with print
            code = f"print({code})"
            
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