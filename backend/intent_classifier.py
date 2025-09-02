"""
Enhanced Intent Classifier - Phase 2
Expanded to 15 operations with simple parameter extraction
Maintains high reliability while adding advanced functionality
"""

import pandas as pd
import re
from typing import Dict, Any, Optional


# 15 Enhanced Operations - Phase 2 Implementation
ENHANCED_INTENTS = {
    # Phase 1 operations (preserved)
    "describe": "df.describe()",
    "show_data": "df.head(10)",
    "count": "len(df)",
    "columns": "list(df.columns)",
    "mean": "df.mean(numeric_only=True)",
    
    # Phase 2 additions - parameterized operations
    "filter": "df[df['{column}'] {operator} {value}]",
    "sort": "df.sort_values('{column}')",
    "group_mean": "df.groupby('{column}').mean(numeric_only=True)",
    "top_n": "df.nlargest({n}, '{column}')",
    "unique": "df['{column}'].unique()",
    "min_max": "df['{column}'].agg(['min', 'max'])",
    "correlation": "df.select_dtypes(include=['number']).corr()",
    "info": "df.info()",
    "null_count": "df.isnull().sum()",
    "value_counts": "df['{column}'].value_counts()"
}


def extract_parameters(query: str, columns: list) -> dict:
    """Extract basic parameters from natural language queries"""
    params = {}
    query_lower = query.lower()
    
    # Column detection - find first matching column
    for column in columns:
        if column.lower() in query_lower:
            params['column'] = column
            break
    
    # Number extraction for top_n operations
    numbers = re.findall(r'\d+', query)
    if numbers:
        params['n'] = int(numbers[0])
    
    # Operator detection for filtering
    if '>' in query:
        params['operator'] = '>'
        value_matches = re.findall(r'>\s*(\d+(?:\.\d+)?)', query)
        if value_matches:
            params['value'] = float(value_matches[0]) if '.' in value_matches[0] else int(value_matches[0])
    elif '<' in query:
        params['operator'] = '<'
        value_matches = re.findall(r'<\s*(\d+(?:\.\d+)?)', query)
        if value_matches:
            params['value'] = float(value_matches[0]) if '.' in value_matches[0] else int(value_matches[0])
    elif '=' in query or 'equal' in query_lower:
        params['operator'] = '=='
        # Extract quoted strings or numbers after equals
        value_matches = re.findall(r'=\s*["\']([^"\']+)["\']|=\s*(\d+(?:\.\d+)?)', query)
        if value_matches:
            for match in value_matches[0]:
                if match:
                    try:
                        params['value'] = float(match) if '.' in match else int(match)
                    except ValueError:
                        params['value'] = f"'{match}'"
                    break
    
    return params


def simple_intent_classifier(query: str, columns: list) -> str:
    """Enhanced intent classification with Phase 3 complex query detection"""
    query_lower = query.lower()
    
    # Phase 3: Check for complex queries that need LLM code generation (first priority)
    complex_keywords = [
        'calculate', 'compute', 'analysis', 'analyze', 'compare', 'find',
        'percentage', 'ratio', 'total', 'sum', 'aggregate',
        'customers', 'purchase', 'sales', 'revenue'
    ]
    
    if any(keyword in query_lower for keyword in complex_keywords):
        return "llm_generate"
    
    # Phase 1 operations (preserved for backward compatibility)
    if any(word in query_lower for word in ["describe", "summary", "statistics"]):
        return "describe"
    elif any(word in query_lower for word in ["count", "rows", "many", "number"]):
        return "count"
    elif any(word in query_lower for word in ["columns", "fields"]):
        return "columns"
    elif any(word in query_lower for word in ["average", "mean"]) and "group" not in query_lower:
        return "mean"
    
    # Phase 2 additions - more specific pattern matching
    elif any(word in query_lower for word in ["filter", "where"]) or any(op in query for op in ['>', '<', '=']):
        return "filter"
    elif any(word in query_lower for word in ["sort", "order"]):
        return "sort"
    elif any(word in query_lower for word in ["group", "groupby"]) and any(word in query_lower for word in ["mean", "average"]):
        return "group_mean"
    elif any(word in query_lower for word in ["top", "largest", "highest", "maximum"]):
        return "top_n"
    elif any(word in query_lower for word in ["unique", "distinct"]):
        return "unique"
    elif any(word in query_lower for word in ["min", "max", "minimum", "maximum"]) and "top" not in query_lower:
        return "min_max"
    elif any(word in query_lower for word in ["correlation", "corr", "correlate"]):
        return "correlation"
    elif any(word in query_lower for word in ["info", "information", "dtype", "types"]):
        return "info"
    elif any(word in query_lower for word in ["null", "missing", "nan"]):
        return "null_count"
    elif any(word in query_lower for word in ["value_counts", "frequency", "count values"]):
        return "value_counts"
    elif any(word in query_lower for word in ["show", "display", "see", "first"]):
        return "show_data"
    else:
        return "show_data"  # Safe default


def execute_intent(intent: str, df: pd.DataFrame, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Execute intent with parameter support for Phase 2 operations"""
    if params is None:
        params = {}
    
    if intent in ENHANCED_INTENTS:
        code = ENHANCED_INTENTS[intent]
        
        try:
            # Handle parameterized operations
            if '{' in code:  # Parameterized operation
                # Validate required parameters
                if 'column' in code and 'column' not in params:
                    return {"success": False, "error": f"Column name required for {intent} operation"}
                if '{n}' in code and 'n' not in params:
                    params['n'] = 5  # Default to top 5
                
                # Format the code with parameters
                try:
                    formatted_code = code.format(**params)
                except KeyError as e:
                    return {"success": False, "error": f"Missing parameter: {str(e)}"}
                
                # Execute formatted code
                result = eval(formatted_code)
            else:
                # Non-parameterized operation
                result = eval(code)
            
            return {"success": True, "result": result, "intent": intent, "params": params}
            
        except Exception as e:
            return {"success": False, "error": f"{intent} operation failed: {str(e)}"}
    else:
        available_ops = list(ENHANCED_INTENTS.keys())
        return {
            "success": False, 
            "error": f"Unknown operation '{intent}'. Available operations: {', '.join(available_ops)}"
        }


def get_available_operations() -> Dict[str, str]:
    """Get list of all 15 available operations for user reference"""
    return {
        # Phase 1 operations
        "describe": "Get statistical summary of the data",
        "show_data": "Display first 10 rows of data",
        "count": "Count total number of rows",
        "columns": "List all column names",
        "mean": "Calculate average values for numeric columns",
        
        # Phase 2 additions
        "filter": "Filter rows based on conditions (e.g., 'sales > 100')",
        "sort": "Sort data by column (e.g., 'sort by price')",
        "group_mean": "Group by column and calculate means (e.g., 'average sales by region')",
        "top_n": "Show top N records by column (e.g., 'top 5 customers')",
        "unique": "Show unique values in column (e.g., 'unique regions')",
        "min_max": "Show minimum and maximum values for column",
        "correlation": "Show correlation matrix for numeric columns",
        "info": "Show data types and non-null counts",
        "null_count": "Show count of missing values per column",
        "value_counts": "Show frequency count of values in column"
    }