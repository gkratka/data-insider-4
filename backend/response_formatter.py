"""
Natural Language Response Formatter
Converts technical results into user-friendly conversational responses
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, Optional


def format_natural_response(query: str, result: Any, execution_details: Dict = None) -> str:
    """
    Convert technical results into natural language responses
    Hide implementation details and present user-friendly answers
    """
    
    # Handle different result types
    if isinstance(result, (int, float)):
        return format_numeric_response(query, result)
    elif isinstance(result, pd.Series):
        return format_series_response(query, result)
    elif isinstance(result, pd.DataFrame):
        return format_dataframe_response(query, result)
    elif isinstance(result, str):
        return format_text_response(query, result)
    else:
        return f"I found the answer: {str(result)}"


def format_numeric_response(query: str, result: float) -> str:
    """Format numeric results with context from the query"""
    
    # Detect query type and provide contextual response
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['average', 'mean']):
        if 'sales' in query_lower:
            return f"The average sales amount is **{result:,.2f}**"
        elif 'price' in query_lower:
            return f"The average price is **{result:,.2f}**"
        else:
            return f"The average value is **{result:,.2f}**"
    
    elif any(word in query_lower for word in ['total', 'sum']):
        if 'sales' in query_lower:
            return f"The total sales amount is **${result:,.2f}**"
        elif 'revenue' in query_lower:
            return f"The total revenue is **${result:,.2f}**"
        else:
            return f"The total is **{result:,.2f}**"
    
    elif any(word in query_lower for word in ['count', 'how many']):
        return f"I found **{int(result)}** records matching your criteria"
    
    elif any(word in query_lower for word in ['max', 'maximum', 'highest']):
        return f"The highest value is **{result:,.2f}**"
    
    elif any(word in query_lower for word in ['min', 'minimum', 'lowest']):
        return f"The lowest value is **{result:,.2f}**"
    
    else:
        return f"The result is **{result:,.2f}**"


def format_series_response(query: str, result: pd.Series) -> str:
    """Format Series results into readable format"""
    
    query_lower = query.lower()
    
    # Handle groupby results
    if len(result) <= 10:  # Show all if reasonable size
        formatted_items = []
        for idx, value in result.items():
            if isinstance(value, (int, float)):
                formatted_items.append(f"• **{idx}**: {value:,.2f}")
            else:
                formatted_items.append(f"• **{idx}**: {value}")
        
        if 'segment' in query_lower or 'group' in query_lower:
            return f"Here's the breakdown by category:\n\n" + "\n".join(formatted_items)
        else:
            return f"Here are the results:\n\n" + "\n".join(formatted_items)
    
    else:  # Summarize if too many results
        total = result.sum() if result.dtype in ['int64', 'float64'] else len(result)
        top_3 = result.nlargest(3) if result.dtype in ['int64', 'float64'] else result.head(3)
        
        response = f"I found results for {len(result)} categories. Here are the top 3:\n\n"
        for idx, value in top_3.items():
            response += f"• **{idx}**: {value:,.2f}\n"
        
        if result.dtype in ['int64', 'float64']:
            response += f"\n📊 **Total across all categories**: {total:,.2f}"
        
        return response


def format_dataframe_response(query: str, result: pd.DataFrame) -> str:
    """Format DataFrame results into readable tables"""
    
    query_lower = query.lower()
    
    if len(result) == 0:
        return "No records found matching your criteria."
    
    # Limit display size for readability
    display_rows = min(len(result), 5)
    display_df = result.head(display_rows)
    
    if 'top' in query_lower and 'customer' in query_lower:
        response = f"Here are the top {display_rows} customers:\n\n"
    elif 'find' in query_lower:
        response = f"I found {len(result)} matching records. Here are the first {display_rows}:\n\n"
    else:
        response = f"Here are the results ({len(result)} total records):\n\n"
    
    # Format as a simple table
    response += format_dataframe_table(display_df)
    
    if len(result) > display_rows:
        response += f"\n\n📋 *Showing {display_rows} of {len(result)} total records*"
    
    return response


def format_dataframe_table(df: pd.DataFrame) -> str:
    """Format a small DataFrame as a readable table"""
    
    if df.empty:
        return "No data to display"
    
    # Get column widths
    col_widths = {}
    for col in df.columns:
        col_widths[col] = max(len(str(col)), df[col].astype(str).str.len().max())
    
    # Build table header
    header_parts = []
    separator_parts = []
    
    for col in df.columns:
        width = min(col_widths[col], 20)  # Limit column width
        header_parts.append(f"{str(col):<{width}}")
        separator_parts.append("-" * width)
    
    table = "```\n"
    table += " | ".join(header_parts) + "\n"
    table += "-|-".join(separator_parts) + "\n"
    
    # Build table rows
    for _, row in df.iterrows():
        row_parts = []
        for col in df.columns:
            width = min(col_widths[col], 20)
            value = str(row[col])
            if len(value) > 20:
                value = value[:17] + "..."
            row_parts.append(f"{value:<{width}}")
        table += " | ".join(row_parts) + "\n"
    
    table += "```"
    return table


def format_text_response(query: str, result: str) -> str:
    """Format text results"""
    return f"Here's what I found: {result}"


def generate_conversational_intro(query: str) -> str:
    """Generate a conversational introduction based on the query"""
    
    query_lower = query.lower()
    
    if 'average' in query_lower:
        return "Let me calculate the average for you..."
    elif 'total' in query_lower:
        return "I'll sum that up for you..."
    elif 'find' in query_lower:
        return "Searching through your data..."
    elif 'top' in query_lower:
        return "Let me find the top results..."
    else:
        return "Analyzing your data..."


# Phase 2 ML-Specific Response Formatting Functions

def format_regression_response(query: str, ml_result: dict) -> str:
    """Format regression analysis in user-friendly language"""
    r2 = ml_result.get('r_squared', 0)
    slope = ml_result.get('slope', 0)
    p_value = ml_result.get('p_value', 1)
    intercept = ml_result.get('intercept', 0)
    equation = ml_result.get('equation', f'y = {slope:.4f}x + {intercept:.4f}')
    
    response = f"**📈 Linear Regression Analysis**\n\n"
    
    if ml_result.get('is_significant', False):
        response += f"I found a **statistically significant relationship** between your variables.\n\n"
        response += f"🎯 **Key Findings**:\n"
        response += f"• **Equation**: `{equation}`\n"
        response += f"• For every 1 unit increase in the independent variable, the dependent variable changes by **{slope:.2f}**\n"
        response += f"• This model explains **{r2*100:.1f}%** of the variance in your data\n"
        response += f"• The relationship is statistically significant (p = {p_value:.4f})\n\n"
        
        if r2 > 0.7:
            response += f"✅ **Strong relationship** - This model is quite reliable for predictions\n"
        elif r2 > 0.5:
            response += f"⚠️ **Moderate relationship** - Use predictions with some caution\n"
        else:
            response += f"⚠️ **Weak relationship** - Other factors likely influence the outcome\n"
    else:
        response += f"📊 **Analysis Results**:\n"
        response += f"• The relationship appears **not statistically significant** (p = {p_value:.4f})\n"
        response += f"• Model explains only **{r2*100:.1f}%** of the variance\n"
        response += f"• Consider other variables that might influence the outcome\n"
    
    return response


def format_correlation_response(query: str, corr_result: Any) -> str:
    """Format correlation analysis with clear explanations"""
    
    if isinstance(corr_result, pd.DataFrame):
        # Correlation matrix
        response = "**🔗 Correlation Analysis**\n\n"
        
        # Find strongest correlations (excluding diagonal)
        strong_correlations = []
        for i in range(len(corr_result.columns)):
            for j in range(i+1, len(corr_result.columns)):
                col1, col2 = corr_result.columns[i], corr_result.columns[j]
                corr_value = corr_result.iloc[i, j]
                if abs(corr_value) > 0.5:  # Strong correlation threshold
                    strong_correlations.append((col1, col2, corr_value))
        
        if strong_correlations:
            response += "🎯 **Strong Relationships Found**:\n"
            for col1, col2, corr_val in sorted(strong_correlations, key=lambda x: abs(x[2]), reverse=True):
                strength = "very strong" if abs(corr_val) > 0.8 else "strong"
                direction = "positive" if corr_val > 0 else "negative"
                response += f"• **{col1}** and **{col2}**: {strength} {direction} correlation ({corr_val:.3f})\n"
        else:
            response += "📊 **Analysis Results**: No strong correlations found (all correlations < 0.5)\n"
            
        response += f"\n💡 **Interpretation**: Correlations closer to ±1.0 indicate stronger linear relationships"
        
    else:
        # Single correlation value
        response = f"**🔗 Correlation Result**: {corr_result:.3f}\n\n"
        abs_corr = abs(corr_result)
        
        if abs_corr > 0.8:
            strength = "very strong"
        elif abs_corr > 0.6:
            strength = "strong"
        elif abs_corr > 0.4:
            strength = "moderate"
        elif abs_corr > 0.2:
            strength = "weak"
        else:
            strength = "very weak"
            
        direction = "positive" if corr_result > 0 else "negative"
        response += f"This indicates a **{strength} {direction}** linear relationship between the variables."
    
    return response


def format_prediction_response(query: str, prediction_result: dict) -> str:
    """Format prediction results with confidence indicators"""
    
    prediction_value = prediction_result.get('prediction')
    confidence = prediction_result.get('confidence_level', 0)
    model_type = prediction_result.get('model_type', 'unknown')
    
    response = f"**🔮 Prediction Analysis**\n\n"
    
    if prediction_value is not None:
        response += f"🎯 **Predicted Value**: **{prediction_value:.2f}**\n\n"
        
        if confidence > 0:
            response += f"📊 **Model Performance**:\n"
            response += f"• Model Type: {model_type.replace('_', ' ').title()}\n"
            response += f"• Confidence Level: **{confidence*100:.1f}%**\n\n"
            
            if confidence > 0.8:
                response += f"✅ **High Confidence** - This prediction is quite reliable based on your data\n"
            elif confidence > 0.6:
                response += f"⚠️ **Moderate Confidence** - Consider this prediction as an estimate\n"
            else:
                response += f"⚠️ **Low Confidence** - Use this prediction with caution, consider gathering more data\n"
    else:
        response += f"❌ Unable to generate reliable prediction with current data\n"
        response += f"💡 **Suggestions**: Try with more data points or check for missing values\n"
    
    return response


def format_forecast_response(query: str, forecast_result: dict) -> str:
    """Format time series forecasting results"""
    
    forecast_values = forecast_result.get('forecast_values', [])
    trend = forecast_result.get('trend', 'stable')
    periods = forecast_result.get('periods', len(forecast_values))
    
    response = f"**📈 Time Series Forecast**\n\n"
    
    if forecast_values:
        response += f"🎯 **Forecast for next {periods} periods**:\n"
        
        for i, value in enumerate(forecast_values[:5], 1):  # Show first 5
            response += f"• Period {i}: **{value:.2f}**\n"
        
        if len(forecast_values) > 5:
            response += f"• ... and {len(forecast_values)-5} more periods\n"
        
        response += f"\n📊 **Trend Analysis**: The data shows a **{trend}** trend\n"
        
        if trend == 'increasing':
            response += f"📈 Values are expected to continue growing over time\n"
        elif trend == 'decreasing':
            response += f"📉 Values are expected to continue declining over time\n"
        else:
            response += f"➡️ Values are expected to remain relatively stable\n"
    else:
        response += f"❌ Unable to generate forecast with current data\n"
        response += f"💡 **Suggestions**: Ensure you have time-series data with sufficient historical points\n"
    
    return response