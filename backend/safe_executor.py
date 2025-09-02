"""
Phase 3: Safe Code Execution - Secure pandas code execution
Minimal implementation with security constraints
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def safe_execute_code(code: str, df: pd.DataFrame) -> Dict[str, Any]:
    """Execute generated code with safety constraints - 30 lines max"""
    
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
        # Execute in restricted environment
        local_vars = {'df': df, 'pd': pd, 'np': np}
        exec(code, {}, local_vars)
        
        # Get result
        result = local_vars.get('result', 'Code executed successfully')
        
        return {'success': True, 'result': result}
        
    except Exception as e:
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