"""
Phase 3: Safe Code Execution - Secure pandas code execution
Minimal implementation with security constraints
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def validate_no_data_fabrication(code: str) -> bool:
    """Validate that generated code does not create synthetic data"""
    forbidden_patterns = [
        'pd.DataFrame(',
        'pandas.DataFrame(',
        'import pandas',
        'import numpy',
        '.DataFrame(',
        'pd.Series(',
        'pandas.Series('
    ]
    
    # Check for forbidden patterns
    for pattern in forbidden_patterns:
        if pattern in code:
            return False
    
    # Ensure 'df' variable is used (must reference user data)
    if 'df' not in code and 'result' not in code:
        return False
        
    return True


def safe_execute_code(code: str, df: pd.DataFrame) -> Dict[str, Any]:
    """Execute generated code with safety constraints - 30 lines max"""
    
    # First validate that code doesn't create synthetic data
    if not validate_no_data_fabrication(code):
        return {
            'success': False,
            'error': 'Generated code attempted to create synthetic data instead of using your uploaded dataset.'
        }
    
    # Validate code safety - allow pandas/numpy imports but block dangerous ones
    forbidden_patterns = [
        'open(', 'file', 'os.', 'sys.', 'subprocess',
        'eval(', 'exec(', '__', 'globals', 'locals'
    ]
    
    # Allow pandas/numpy imports but block other imports
    if 'import' in code:
        import_lines = [line.strip() for line in code.split('\n') if 'import' in line]
        allowed_imports = ['pandas', 'numpy', 'np', 'pd']
        
        for import_line in import_lines:
            if not any(allowed in import_line for allowed in allowed_imports):
                return {
                    'success': False,
                    'error': f'Forbidden import: {import_line}'
                }
    
    # Check for remaining forbidden patterns
    for pattern in forbidden_patterns:
        if pattern in code:
            return {
                'success': False, 
                'error': f'Code contains forbidden operation: {pattern}'
            }
    
    try:
        # Execute in restricted environment and capture output
        import io
        import sys
        
        # Capture stdout
        old_stdout = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            local_vars = {'df': df, 'pd': pd, 'np': np}
            exec(code, {}, local_vars)
        finally:
            # Always restore stdout
            sys.stdout = old_stdout
        
        # Get result (either from print output or result variable)
        output_text = captured_output.getvalue().strip()
        variable_result = local_vars.get('result')
        
        if output_text:
            result = output_text
        elif variable_result is not None:
            result = variable_result
        else:
            result = 'Code executed successfully'
        
        return {'success': True, 'result': result}
        
    except Exception as e:
        # Ensure stdout is restored even on exception
        import sys
        if 'old_stdout' in locals():
            sys.stdout = old_stdout
        return {'success': False, 'error': str(e)}


def format_execution_result(result: Any) -> str:
    """Format result for user display - 10 lines max"""
    if isinstance(result, pd.DataFrame):
        return result.to_string()
    elif isinstance(result, pd.Series):
        return result.to_string()
    elif isinstance(result, (list, dict)):
        return str(result)
    else:
        return str(result)