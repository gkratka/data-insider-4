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
    """Enhanced intent classification with Phase 3 ML-specific detection and debug logging"""
    query_lower = query.lower()
    
    # Add debug logging at start of function
    print(f"🎯 Intent Classification - Query: '{query}'")
    
    # Phase 3: Check for dedicated ML operations (highest priority)
    
    # Ridge regression detection
    if any(word in query_lower for word in ['ridge regression', 'regularized regression', 'regularization']):
        intent = "ml_ridge_regression"
        print(f"🎯 Intent Classified: {intent} (Ridge regression pattern matched)")
        return intent
    
    # Polynomial regression detection
    if any(word in query_lower for word in ['polynomial regression', 'quadratic', 'cubic', 'polynomial']):
        intent = "ml_polynomial_regression"
        print(f"🎯 Intent Classified: {intent} (Polynomial regression pattern matched)")
        return intent
    
    # Enhanced linear regression detection patterns
    linear_regression_patterns = [
        'linear regression', 'regression analysis', 'regression model',
        'analyze relationship', 'relationship.*regression', 'regression.*relationship', 
        'statistical relationship', 'linear relationship'
    ]
    
    # Prediction patterns that should use MLPredictor
    prediction_patterns = [
        r'predict .* based on', r'forecast .* using', r'estimate .* from',
        r'model .* relationship', r'analyze .* relationship.*regression'
    ]
    
    # Check for direct pattern matches
    if any(pattern in query_lower for pattern in linear_regression_patterns):
        intent = "ml_linear_regression"
        print(f"🎯 Intent Classified: {intent} (Linear regression direct pattern matched)")
        return intent
    
    # Check for regex prediction patterns
    if any(re.search(pattern, query_lower) for pattern in prediction_patterns):
        intent = "ml_linear_regression"
        print(f"🎯 Intent Classified: {intent} (Prediction regex pattern matched)")
        return intent
    
    # Enhanced combination logic
    if (any(word in query_lower for word in ['regression', 'linear', 'predict']) and 
        any(word in query_lower for word in ['analysis', 'model', 'relationship', 'based on'])):
        intent = "ml_linear_regression"
        print(f"🎯 Intent Classified: {intent} (Enhanced combination logic matched)")
        return intent
    
    # Statistical analysis detection (for ML predictor)
    if any(combo in query_lower for combo in ['statistical analysis', 'statistical significance', 'p-value', 'confidence interval']):
        intent = "ml_statistical_analysis"
        print(f"🎯 Intent Classified: {intent} (Statistical analysis pattern matched)")
        return intent
    
    # Phase 2/3: Check for complex queries that need LLM code generation (second priority)
    complex_keywords = [
        # Existing Phase 1 keywords
        'calculate', 'compute', 'compare', 'find',
        'percentage', 'ratio', 'total', 'sum', 'aggregate',
        
        # Phase 2 addition: Prediction-specific keywords (but not ML-specific)
        # Note: 'analyze', 'relationship', 'model', 'fit' removed to prevent 
        # conflicts with ML intent detection (should trigger ML intents, not LLM generation)
        'predict', 'forecast', 'trend', 'future', 'estimate', 
        'project', 'extrapolate', 'dependent', 'independent', 
        'variable', 'slope', 'coefficient', 'r-squared', 'train',
        
        # Business domain keywords
        'customers', 'purchase', 'sales', 'revenue'
    ]
    
    # Add logging for fallback to complex keywords
    if any(keyword in query_lower for keyword in complex_keywords):
        intent = "llm_generate"
        matched_keywords = [kw for kw in complex_keywords if kw in query_lower]
        print(f"🎯 Intent Classified: {intent} (complex keywords matched: {matched_keywords})")
        return intent
    
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
    """Execute intent with parameter support for Phase 2 operations and Phase 3 ML operations"""
    if params is None:
        params = {}
    
    # Phase 3: Handle dedicated ML operations
    if intent.startswith("ml_"):
        try:
            from ml_predictor import MLPredictor
            ml_predictor = MLPredictor()
            
            # Detect columns for regression analysis
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if len(numeric_cols) < 2:
                return {
                    "success": False, 
                    "error": "Need at least 2 numeric columns for ML analysis"
                }
            
            # Use first two numeric columns as default (can be enhanced with parameter extraction)
            x_col = numeric_cols[0] if 'x_column' not in params else params['x_column']
            y_col = numeric_cols[1] if 'y_column' not in params else params['y_column']
            
            # Ensure we don't use the same column for both
            if x_col == y_col and len(numeric_cols) > 1:
                y_col = numeric_cols[1] if x_col == numeric_cols[0] else numeric_cols[0]
            
            # Execute specific ML operation
            if intent == "ml_linear_regression":
                result = ml_predictor.linear_regression_analysis(df, x_col, y_col)
            elif intent == "ml_polynomial_regression":
                degree = params.get('degree', 2)
                result = ml_predictor.polynomial_regression_analysis(df, x_col, y_col, degree)
            elif intent == "ml_ridge_regression":
                alpha = params.get('alpha', 1.0)
                result = ml_predictor.ridge_regression_analysis(df, x_col, y_col, alpha)
            elif intent == "ml_statistical_analysis":
                # Default to linear regression for statistical analysis
                result = ml_predictor.linear_regression_analysis(df, x_col, y_col)
            else:
                return {"success": False, "error": f"Unknown ML operation: {intent}"}
            
            if result.get('success', False):
                # Add column information to result
                result['columns_used'] = {'x_column': x_col, 'y_column': y_col}
                result['intent'] = intent
                return {"success": True, "result": result, "intent": intent, "ml_analysis": True}
            else:
                return {"success": False, "error": result.get('error', 'ML analysis failed')}
                
        except ImportError:
            return {"success": False, "error": "ML Predictor module not available"}
        except Exception as e:
            return {"success": False, "error": f"ML analysis failed: {str(e)}"}
    
    # Phase 1/2: Handle standard operations
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


def analyze_prediction_context(query: str, df: pd.DataFrame) -> dict:
    """
    Phase 2: Comprehensive query context analysis for ML operation selection
    
    Features:
    - Numeric column pairs detection for regression
    - Time series pattern identification
    - Categorical analysis for grouping vs continuous variables
    - Data sufficiency checking for analysis requirements
    """
    query_lower = query.lower()
    context = {'type': 'general'}
    
    # Column type analysis
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    # Check for datetime patterns in column names even if not datetime type
    potential_date_cols = [col for col in df.columns if any(word in col.lower() 
                          for word in ['date', 'time', 'year', 'month', 'day'])]
    all_date_cols = list(set(datetime_cols + potential_date_cols))
    
    context.update({
        'numeric_columns': numeric_cols,
        'categorical_columns': categorical_cols,
        'datetime_columns': all_date_cols,
        'total_rows': len(df),
        'sufficient_data_regression': len(df) >= 10,
        'sufficient_data_ml': len(df) >= 30,
        'data_quality': 'good' if df.isnull().sum().sum() / (len(df) * len(df.columns)) < 0.1 else 'poor'
    })
    
    # Prediction scenario detection
    prediction_indicators = ['predict', 'forecast', 'estimate', 'project', 'model']
    if any(indicator in query_lower for indicator in prediction_indicators):
        context['type'] = 'prediction'
        
        # Look for target variable mentions in query
        target_column = None
        for col in numeric_cols:
            if col.lower() in query_lower:
                target_column = col
                break
        
        if target_column:
            context.update({
                'target_column': target_column,
                'feature_columns': [c for c in numeric_cols if c != target_column],
                'prediction_type': 'regression' if target_column in numeric_cols else 'classification'
            })
        
        # Time series forecasting detection
        if any(word in query_lower for word in ['trend', 'future', 'forecast', 'time']) and all_date_cols:
            context.update({
                'analysis_type': 'time_series',
                'time_column': all_date_cols[0],
                'suitable_for_forecasting': len(df) >= 20
            })
    
    # Correlation analysis detection
    elif 'correlation' in query_lower or 'relationship' in query_lower:
        context['type'] = 'correlation'
        if len(numeric_cols) >= 2:
            context.update({
                'analysis_type': 'correlation_matrix',
                'suitable_pairs': [(numeric_cols[i], numeric_cols[j]) 
                                 for i in range(len(numeric_cols)) 
                                 for j in range(i+1, len(numeric_cols))]
            })
    
    # Regression analysis detection
    elif any(word in query_lower for word in ['regression', 'linear', 'dependent', 'independent']):
        context['type'] = 'regression'
        if len(numeric_cols) >= 2:
            context.update({
                'analysis_type': 'linear_regression',
                'potential_target_features': numeric_cols,
                'regression_ready': len(df) >= 10 and len(numeric_cols) >= 2
            })
    
    # Grouping analysis detection
    elif any(word in query_lower for word in ['group', 'category', 'segment']) and categorical_cols:
        context['type'] = 'grouping'
        context.update({
            'analysis_type': 'grouped_analysis',
            'grouping_columns': categorical_cols,
            'numeric_for_grouping': numeric_cols
        })
    
    # Data quality assessment
    if context['data_quality'] == 'poor':
        context['recommendations'] = [
            'Consider data cleaning before analysis',
            'Check for missing values that might affect results',
            'Verify data types are correctly assigned'
        ]
    
    return context


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