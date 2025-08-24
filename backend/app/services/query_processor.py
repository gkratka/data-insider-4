import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import pandas as pd

from app.services.claude_service import claude_client
from app.services.data_processing_service import data_processing_engine
from app.models.file import UploadedFile


logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    """Types of data analysis intents"""
    FILTER = "filter"
    AGGREGATE = "aggregate" 
    SORT = "sort"
    SUMMARIZE = "summarize"
    VISUALIZE = "visualize"
    JOIN = "join"
    STATISTICS = "statistics"
    UNKNOWN = "unknown"


class EntityType(Enum):
    """Types of entities in queries"""
    TABLE = "table"
    COLUMN = "column"
    VALUE = "value"
    OPERATION = "operation"
    CONDITION = "condition"


class NaturalLanguageProcessor:
    """Process natural language queries into data operations"""
    
    def __init__(self):
        self.intent_keywords = {
            QueryIntent.FILTER: ["filter", "where", "show me", "find", "select", "get"],
            QueryIntent.AGGREGATE: ["sum", "count", "average", "mean", "total", "group by", "aggregate"],
            QueryIntent.SORT: ["sort", "order", "arrange", "rank"],
            QueryIntent.SUMMARIZE: ["summary", "describe", "overview", "statistics", "stats"],
            QueryIntent.VISUALIZE: ["plot", "chart", "graph", "visualize", "show"],
            QueryIntent.JOIN: ["join", "merge", "combine", "relate"],
            QueryIntent.STATISTICS: ["correlation", "regression", "analysis", "trend", "pattern"]
        }
        
        self.operation_mapping = {
            "equals": ["equals", "is", "=", "=="],
            "greater_than": ["greater than", "more than", "above", ">"],
            "less_than": ["less than", "below", "under", "<"],
            "contains": ["contains", "includes", "has", "with"],
            "not_equals": ["not", "isn't", "not equal", "!="],
            "is_null": ["null", "empty", "missing", "blank"],
            "not_null": ["not null", "not empty", "has value"]
        }
    
    def classify_intent(self, query: str) -> QueryIntent:
        """
        Classify the intent of a natural language query
        
        Args:
            query: Natural language query
            
        Returns:
            Classified intent
        """
        query_lower = query.lower()
        
        # Count matches for each intent
        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            intent_scores[intent] = score
        
        # Return intent with highest score
        if max(intent_scores.values()) > 0:
            return max(intent_scores, key=intent_scores.get)
        else:
            return QueryIntent.UNKNOWN
    
    def extract_entities(self, query: str, available_columns: List[str]) -> Dict[str, List[str]]:
        """
        Extract entities (columns, values, operations) from query
        
        Args:
            query: Natural language query
            available_columns: List of column names in the dataset
            
        Returns:
            Dict of extracted entities by type
        """
        entities = {
            'columns': [],
            'values': [],
            'operations': [],
            'conditions': []
        }
        
        query_lower = query.lower()
        
        # Extract column names
        for col in available_columns:
            col_variations = [col.lower(), col.replace('_', ' ').lower()]
            for variation in col_variations:
                if variation in query_lower:
                    entities['columns'].append(col)
                    break
        
        # Extract operations
        for operation, keywords in self.operation_mapping.items():
            if any(keyword in query_lower for keyword in keywords):
                entities['operations'].append(operation)
        
        # Extract numeric values
        numeric_pattern = r'\b\d+\.?\d*\b'
        numeric_matches = re.findall(numeric_pattern, query)
        entities['values'].extend(numeric_matches)
        
        # Extract quoted values
        quoted_pattern = r'["\']([^"\']+)["\']'
        quoted_matches = re.findall(quoted_pattern, query)
        entities['values'].extend(quoted_matches)
        
        return entities
    
    async def generate_pandas_code(
        self, 
        query: str, 
        intent: QueryIntent, 
        entities: Dict[str, List[str]],
        data_summary: Dict[str, Any]
    ) -> str:
        """
        Generate pandas code for the query using Claude
        
        Args:
            query: Original natural language query
            intent: Classified intent
            entities: Extracted entities
            data_summary: Summary of the dataset
            
        Returns:
            Generated pandas code
        """
        system_prompt = """You are an expert Python data analyst. Generate pandas code to answer natural language queries about datasets. 

Requirements:
- Use only pandas operations
- Assume the DataFrame is named 'df'
- Return only the pandas code, no explanations
- Handle errors gracefully
- Use efficient operations for large datasets
- For aggregations, use groupby when appropriate
- For filtering, use boolean indexing
- For sorting, use sort_values()

The dataset information and query will be provided."""
        
        user_prompt = f"""
Dataset Information:
- Columns: {list(data_summary.get('columns', []))}
- Column types: {data_summary.get('dtypes', {})}
- Shape: {data_summary.get('shape', [])}

Query Intent: {intent.value}
Extracted Entities:
- Columns: {entities.get('columns', [])}
- Operations: {entities.get('operations', [])}
- Values: {entities.get('values', [])}

Natural Language Query: "{query}"

Generate pandas code to answer this query:
"""
        
        try:
            messages = [
                {'role': 'user', 'content': user_prompt}
            ]
            
            response = await claude_client.create_completion(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=1000,
                temperature=0.1
            )
            
            # Extract code from response
            code = self._extract_code_from_response(response['content'])
            return code
            
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            return self._generate_fallback_code(intent, entities)
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract pandas code from Claude's response"""
        # Look for code blocks
        code_block_pattern = r'```(?:python)?\s*(.*?)```'
        matches = re.findall(code_block_pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # If no code blocks, look for lines starting with df.
        lines = response.split('\n')
        code_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('df.') or line.startswith('result =') or 'df[' in line:
                code_lines.append(line)
        
        return '\n'.join(code_lines) if code_lines else response.strip()
    
    def _generate_fallback_code(self, intent: QueryIntent, entities: Dict[str, List[str]]) -> str:
        """Generate basic fallback code when Claude fails"""
        columns = entities.get('columns', [])
        operations = entities.get('operations', [])
        values = entities.get('values', [])
        
        if intent == QueryIntent.FILTER and columns and values:
            col = columns[0]
            val = values[0]
            if 'greater_than' in operations:
                return f"result = df[df['{col}'] > {val}]"
            elif 'less_than' in operations:
                return f"result = df[df['{col}'] < {val}]"
            else:
                return f"result = df[df['{col}'] == '{val}']"
        
        elif intent == QueryIntent.AGGREGATE and columns:
            col = columns[0]
            return f"result = df.groupby('{col}').size().reset_index(name='count')"
        
        elif intent == QueryIntent.SORT and columns:
            col = columns[0]
            return f"result = df.sort_values(by='{col}')"
        
        elif intent == QueryIntent.SUMMARIZE:
            return "result = df.describe()"
        
        else:
            return "result = df.head(10)"
    
    async def execute_generated_code(
        self, 
        code: str, 
        df: pd.DataFrame
    ) -> Tuple[bool, Any, str]:
        """
        Safely execute generated pandas code
        
        Args:
            code: Generated pandas code
            df: DataFrame to operate on
            
        Returns:
            Tuple of (success, result, error_message)
        """
        try:
            # Create safe execution environment
            safe_globals = {
                'df': df,
                'pd': pd,
                'np': __import__('numpy')
            }
            
            safe_locals = {}
            
            # Execute the code
            exec(code, safe_globals, safe_locals)
            
            # Get result
            if 'result' in safe_locals:
                result = safe_locals['result']
            else:
                # If no result variable, assume last line is the result
                lines = code.strip().split('\n')
                if lines:
                    last_line = lines[-1]
                    if not last_line.startswith('result ='):
                        exec(f"result = {last_line}", safe_globals, safe_locals)
                        result = safe_locals['result']
                    else:
                        result = df  # fallback
                else:
                    result = df
            
            return True, result, ""
            
        except Exception as e:
            logger.error(f"Code execution error: {str(e)}")
            return False, None, str(e)
    
    def generate_explanation(
        self, 
        query: str, 
        intent: QueryIntent, 
        code: str, 
        result_summary: str
    ) -> str:
        """
        Generate human-readable explanation of the analysis
        
        Args:
            query: Original query
            intent: Classified intent
            code: Generated code
            result_summary: Summary of results
            
        Returns:
            Human-readable explanation
        """
        explanations = {
            QueryIntent.FILTER: f"I filtered the data based on your criteria: '{query}'. {result_summary}",
            QueryIntent.AGGREGATE: f"I performed aggregation on the data: '{query}'. {result_summary}",
            QueryIntent.SORT: f"I sorted the data as requested: '{query}'. {result_summary}",
            QueryIntent.SUMMARIZE: f"Here's a summary of your data: {result_summary}",
            QueryIntent.VISUALIZE: f"I prepared the data for visualization: '{query}'. {result_summary}",
            QueryIntent.STATISTICS: f"I calculated the requested statistics: '{query}'. {result_summary}"
        }
        
        return explanations.get(intent, f"I processed your query: '{query}'. {result_summary}")


class QueryProcessor:
    """Main query processing service"""
    
    def __init__(self):
        self.nlp = NaturalLanguageProcessor()
    
    async def process_query(
        self,
        query: str,
        file_record: UploadedFile,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a natural language query against a data file
        
        Args:
            query: Natural language query
            file_record: Database record of the file to query
            session_id: Optional session ID for context
            
        Returns:
            Dict with query results and metadata
        """
        try:
            # Load data
            df = await data_processing_engine.load_file_data(file_record)
            data_summary = data_processing_engine.get_data_summary(df)
            
            # Process query
            intent = self.nlp.classify_intent(query)
            entities = self.nlp.extract_entities(query, data_summary['columns'])
            
            # Generate pandas code
            code = await self.nlp.generate_pandas_code(
                query, intent, entities, data_summary
            )
            
            # Execute code
            success, result, error = await self.nlp.execute_generated_code(code, df)
            
            if not success:
                return {
                    'success': False,
                    'error': f"Query execution failed: {error}",
                    'intent': intent.value,
                    'generated_code': code
                }
            
            # Process results
            if isinstance(result, pd.DataFrame):
                result_data = result.head(100).to_dict('records')
                result_summary = f"Found {len(result)} rows"
                columns = [{'name': col, 'type': str(result[col].dtype)} for col in result.columns]
            else:
                result_data = [{'result': str(result)}]
                result_summary = f"Result: {str(result)}"
                columns = [{'name': 'result', 'type': 'object'}]
            
            # Generate explanation
            explanation = self.nlp.generate_explanation(
                query, intent, code, result_summary
            )
            
            return {
                'success': True,
                'intent': intent.value,
                'entities': entities,
                'generated_code': code,
                'result_data': result_data,
                'columns': columns,
                'total_rows': len(result) if isinstance(result, pd.DataFrame) else 1,
                'explanation': explanation,
                'result_summary': result_summary
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return {
                'success': False,
                'error': f"Query processing failed: {str(e)}",
                'intent': 'unknown'
            }


# Global instance
query_processor = QueryProcessor()