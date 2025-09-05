"""
Simplified LLM Backend - Phase 1 Foundation-First Approach
No Redis, no complex databases, no over-engineering
Maximum reliability with minimal dependencies
"""

import os
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv

# Simple local imports - no complex engines
from simple_file_manager import SimpleFileManager
from intent_classifier import simple_intent_classifier, execute_intent, get_available_operations, extract_parameters
from code_generator import generate_pandas_code
from safe_executor import safe_execute_code, format_execution_result
from response_formatter import format_natural_response

# Phase 4: System Reliability imports
from data_quality_validator import validate_data_quality
from error_recovery_enhancer import handle_analysis_error, attempt_graceful_fallback

# Load environment variables
load_dotenv()

app = FastAPI(title="Data Intelligence Platform - Foundation-First")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Simple in-memory sessions - No Redis dependency
sessions = {}
file_manager = SimpleFileManager()

# Initialize Gemini client
gemini_model = None
try:
    import google.generativeai as genai
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        gemini_model = genai.GenerativeModel(model_name)
        print("✅ Gemini API connected successfully")
    else:
        print("⚠️ GOOGLE_API_KEY not found - using mock responses")
except ImportError:
    print("⚠️ google-generativeai not installed - using mock responses")


# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: str
    file_ids: Optional[List[str]] = []


class ChatResponse(BaseModel):
    response: str
    session_id: str


# Simple session management - No Redis dependency
def get_session(session_id: str) -> Dict:
    """Simple session retrieval with automatic initialization"""
    if session_id not in sessions:
        sessions[session_id] = {
            'messages': [], 
            'files': []
        }
    return sessions[session_id]


async def get_gemini_response(query: str, context: str = "") -> str:
    """Get response from Gemini or return mock response"""
    if not gemini_model:
        return f"🤖 Mock Response: I would analyze '{query}' but need GOOGLE_API_KEY"
    
    try:
        prompt = f"{context}\n\nUser query: {query}"
        response = gemini_model.generate_content(prompt)
        return response.text if response.text else "No response received"
    except Exception as e:
        return f"Error: {str(e)}"


# API Routes
@app.get("/")
async def root():
    return {
        "message": "Data Intelligence Platform - Foundation-First Phase 1",
        "gemini_available": gemini_model is not None,
        "available_operations": get_available_operations()
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "phase": 1}


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Simplified chat endpoint with direct execution"""
    session = get_session(request.session_id)
    
    # Add user message to session
    session['messages'].append({
        'role': 'user',
        'content': request.message,
        'timestamp': datetime.now()
    })
    
    # Process query based on whether files are available
    if request.file_ids and request.file_ids[0]:
        file_data = file_manager.get_file(request.file_ids[0])
        
        if not file_data:
            # Auto-recovery: Try to find the most recent available file
            available_files = file_manager.list_files()
            if available_files:
                # Use the most recent file (highest ID number)
                latest_file_id = max(available_files.keys(), key=lambda x: int(x.split('_')[1]))
                file_data = file_manager.get_file(latest_file_id)
                print(f"🔄 Auto-recovery: Using latest file {latest_file_id} instead of invalid {request.file_ids[0]}")
                # Continue processing with the recovered file - don't return early
            else:
                response = f"File '{request.file_ids[0]}' not found. Please upload a file first."
                # Add AI response to session and return early
                session['messages'].append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now()
                })
                return ChatResponse(response=response, session_id=request.session_id)
        
        if file_data:  # Process the file (either original or auto-recovered)
            df = file_data['df']
            
            # Phase 4: Data Quality Validation - Pre-analysis checks
            intent = simple_intent_classifier(request.message, df.columns.tolist())
            
            # Add intent validation logging
            print(f"🔍 Pipeline Routing - Intent: '{intent}' for query: '{request.message}'")
            
            # Validate ML intent routing
            if intent.startswith('ml_'):
                print(f"✅ ML Intent Detected - Routing to MLPredictor: {intent}")
            elif intent == 'llm_generate' and any(word in request.message.lower() for word in ['regression', 'predict', 'model']):
                print(f"⚠️ WARNING: ML-like query routed to LLM generation instead of MLPredictor")
                print(f"   Query: '{request.message}'")
                print(f"   Intent: '{intent}'")
                print(f"   Consider reviewing intent classification patterns")
            
            # Perform data quality validation for ML and statistical operations
            if intent.startswith('ml_') or intent in ['regression', 'correlation']:
                try:
                    quality_result = validate_data_quality(df, intent)
                    
                    # Check for critical data quality issues
                    if not quality_result['is_valid']:
                        # Critical issues found - provide quality report instead of analysis
                        quality_message = f"🔍 **Data Quality Assessment**\n\n"
                        quality_message += f"❌ **Issues Found**:\n"
                        for issue in quality_result['issues']:
                            quality_message += f"• {issue}\n"
                        
                        if quality_result['warnings']:
                            quality_message += f"\n⚠️ **Warnings**:\n"
                            for warning in quality_result['warnings']:
                                quality_message += f"• {warning}\n"
                        
                        if quality_result['recommendations']:
                            quality_message += f"\n💡 **Recommendations**:\n"
                            for rec in quality_result['recommendations']:
                                quality_message += f"• {rec}\n"
                        
                        # Add quality score
                        quality_message += f"\n📊 **Data Quality Score**: {quality_result['quality_score']:.1f}/100"
                        
                        response = quality_message
                        
                        # Add AI response to session and return early
                        session['messages'].append({
                            'role': 'assistant',
                            'content': response,
                            'timestamp': datetime.now()
                        })
                        return ChatResponse(response=response, session_id=request.session_id)
                    
                    # Quality warnings - include in analysis but warn user
                    elif quality_result['warnings']:
                        print(f"⚠️ Data quality warnings for {intent}: {len(quality_result['warnings'])} warnings")
                        
                except Exception as quality_error:
                    print(f"⚠️ Data quality validation failed: {str(quality_error)}")
                    # Continue with analysis despite validation failure
            
            # Phase 2/3: Enhanced intent classification with parameter extraction (continued)
            
            if intent == "llm_generate":
                # Phase 3: LLM code generation for complex queries
                # Enhanced sample data context - Phase 1 Priority 3
                sample_data = {
                    'row_count': len(df),
                    'columns': df.columns.tolist(),
                    'dtypes': df.dtypes.to_dict(),
                    'sample_rows': df.head(3).to_dict('records'),
                    'null_counts': df.isnull().sum().to_dict(),
                    'numeric_columns': df.select_dtypes(include=['number']).columns.tolist()
                }
                generated_code = generate_pandas_code(
                    request.message, 
                    df.columns.tolist(), 
                    sample_data, 
                    gemini_model
                )
                
                # Log the generated code for debugging
                print(f"🔍 Generated code: {generated_code}")
                
                # Execute the generated code safely
                execution_result = safe_execute_code(generated_code, df)
                
                if execution_result["success"]:
                    # Format as natural language response - hide technical details
                    response = format_natural_response(request.message, execution_result["result"])
                else:
                    print(f"❌ Execution error: {execution_result['error']}")
                    
                    # Phase 4: Enhanced error recovery for LLM-generated code
                    try:
                        error_context = Exception(execution_result['error'])
                        recovery_result = handle_analysis_error(error_context, request.message, 'llm_generate', df)
                        
                        # Create enhanced error response
                        error_response = f"🔧 **Analysis Issue Detected**\n\n"
                        error_response += f"{recovery_result['user_friendly_message']}\n\n"
                        
                        if recovery_result['fallback_suggestions']:
                            error_response += f"💡 **Try These Instead**:\n"
                            for suggestion in recovery_result['fallback_suggestions'][:3]:
                                error_response += f"• {suggestion}\n"
                        
                        if recovery_result['query_reformulations']:
                            error_response += f"\n🔄 **Alternative Queries**:\n"
                            for reform in recovery_result['query_reformulations'][:2]:
                                error_response += f"• \"{reform}\"\n"
                        
                        response = error_response
                        
                        # Attempt graceful fallback if possible
                        if recovery_result.get('can_retry_with_fallback', False):
                            try:
                                fallback_result = attempt_graceful_fallback('llm_generate', df, request.message)
                                if fallback_result.get('fallback_successful', False):
                                    response += f"\n\n📊 **Here's a simpler analysis instead**:\n"
                                    response += f"{fallback_result['fallback_message']}\n\n"
                                    response += format_natural_response(request.message, fallback_result['result'])
                            except Exception as fallback_error:
                                print(f"⚠️ Fallback also failed: {str(fallback_error)}")
                    
                    except Exception as recovery_error:
                        print(f"⚠️ Error recovery failed: {str(recovery_error)}")
                        response = "I encountered an issue processing your request. Could you try rephrasing your question or check if the column names are correct?"
            else:
                # Phase 1/2/3: Standard and ML intent operations
                params = extract_parameters(request.message, df.columns.tolist())
                
                # Enhanced error context for ML operations
                if intent.startswith('ml_'):
                    try:
                        result = execute_intent(intent, df, params)
                        
                        if not result["success"]:
                            print(f"❌ ML Operation Failed:")
                            print(f"   Intent: {intent}")
                            print(f"   Query: {request.message}")
                            print(f"   Error: {result.get('error', 'Unknown error')}")
                            print(f"   Parameters: {params}")
                            
                    except Exception as e:
                        print(f"❌ ML Pipeline Exception:")
                        print(f"   Intent: {intent}")
                        print(f"   Query: {request.message}")
                        print(f"   Exception: {str(e)}")
                        result = {"success": False, "error": f"ML pipeline error: {str(e)}"}
                else:
                    # Standard operations
                    result = execute_intent(intent, df, params)
                
                if result["success"]:
                    # Phase 3: Check if this is an ML analysis result
                    if result.get("ml_analysis", False):
                        # Import ML-specific response formatting functions
                        from response_formatter import (
                            format_regression_response, 
                            format_correlation_response,
                            format_prediction_response
                        )
                        
                        ml_result = result["result"]
                        model_type = ml_result.get("model_type", "")
                        
                        # Use specialized ML formatting based on model type
                        if "regression" in model_type:
                            response = format_regression_response(request.message, ml_result)
                        elif "correlation" in model_type:
                            response = format_correlation_response(request.message, ml_result)
                        elif "prediction" in model_type:
                            response = format_prediction_response(request.message, ml_result)
                        else:
                            # Fallback to regression formatting for statistical analysis
                            response = format_regression_response(request.message, ml_result)
                        
                        # Add recommendations if available
                        if hasattr(ml_result, 'get') and 'recommendations' in ml_result:
                            response += f"\n\n💡 **Recommendations**:\n"
                            for rec in ml_result['recommendations']:
                                response += f"• {rec}\n"
                    else:
                        # Phase 1/2: Standard response formatting
                        response = format_natural_response(request.message, result["result"])
                else:
                    # Phase 4: Enhanced error recovery for ML and standard operations
                    try:
                        error_context = Exception(result.get("error", "Unknown error occurred"))
                        recovery_result = handle_analysis_error(error_context, request.message, intent, df)
                        
                        # Create enhanced error response
                        error_response = f"🔧 **Analysis Issue Detected**\n\n"
                        error_response += f"{recovery_result['user_friendly_message']}\n\n"
                        
                        if recovery_result['actionable_steps']:
                            error_response += f"🛠️ **What You Can Do**:\n"
                            for step in recovery_result['actionable_steps'][:4]:
                                error_response += f"• {step}\n"
                        
                        if recovery_result['fallback_suggestions']:
                            error_response += f"\n💡 **Try These Instead**:\n"
                            for suggestion in recovery_result['fallback_suggestions'][:3]:
                                error_response += f"• {suggestion}\n"
                        
                        response = error_response
                        
                        # Attempt graceful fallback if possible
                        if recovery_result.get('can_retry_with_fallback', False):
                            try:
                                fallback_result = attempt_graceful_fallback(intent, df, request.message)
                                if fallback_result.get('fallback_successful', False):
                                    response += f"\n\n📊 **Here's a simpler analysis instead**:\n"
                                    response += f"{fallback_result['fallback_message']}\n\n"
                                    response += format_natural_response(request.message, fallback_result['result'])
                            except Exception as fallback_error:
                                print(f"⚠️ Fallback failed: {str(fallback_error)}")
                        
                    except Exception as recovery_error:
                        print(f"⚠️ Error recovery failed: {str(recovery_error)}")
                        response = "I encountered an issue processing your request. Could you try rephrasing your question or check if the column names are correct?"
    else:
        available_ops = ", ".join(list(get_available_operations().keys())[:10]) + "..."
        response = f"Please upload a file first. I can help with: {available_ops}"
    
    # Add AI response to session
    session['messages'].append({
        'role': 'assistant',
        'content': response,
        'timestamp': datetime.now()
    })
    
    return ChatResponse(response=response, session_id=request.session_id)


@app.post("/api/v1/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file with simple processing"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        # Read file content
        content = await file.read()
        
        # Save file to disk
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Load into pandas based on file type
        file_ext = file.filename.lower().split('.')[-1]
        
        if file_ext == 'csv':
            df = pd.read_csv(file_path)
        elif file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use CSV or Excel.")
        
        # Store in file manager with simple ID
        file_id = file_manager.store_file(file.filename, str(file_path), df)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "size": len(content),
            "rows": len(df),
            "columns": list(df.columns),
            "message": f"File uploaded successfully as {file_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")


@app.get("/api/v1/files")
async def list_files():
    """List uploaded files"""
    files_info = file_manager.list_files()
    return [
        {
            "id": file_id,
            "filename": info["filename"],
            "rows": info["rows"],
            "columns": info["columns"]
        }
        for file_id, info in files_info.items()
    ]


@app.delete("/api/v1/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file"""
    success = file_manager.delete_file(file_id)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": f"File {file_id} deleted successfully"}


@app.get("/api/v1/operations")
async def get_operations():
    """Get available operations"""
    return get_available_operations()


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Phase 1: Foundation-First Implementation")
    print("📋 Available operations:", list(get_available_operations().keys()))
    uvicorn.run(app, host="0.0.0.0", port=8000)