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
            response = f"File '{request.file_ids[0]}' not found. Please upload a file first."
        else:
            df = file_data['df']
            
            # Phase 2/3: Enhanced intent classification with parameter extraction
            intent = simple_intent_classifier(request.message, df.columns.tolist())
            
            if intent == "llm_generate":
                # Phase 3: LLM code generation for complex queries
                sample_data = df.head(3).to_dict()
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
                    formatted_result = format_execution_result(execution_result["result"])
                    response = f"Generated Code:\n{generated_code}\n\nResult:\n{formatted_result}"
                else:
                    print(f"❌ Execution error: {execution_result['error']}")
                    response = f"Code Generation Error: {execution_result['error']}"
            else:
                # Phase 1/2: Standard intent operations
                params = extract_parameters(request.message, df.columns.tolist())
                result = execute_intent(intent, df, params)
                
                if result["success"]:
                    # Format result for user
                    if isinstance(result["result"], pd.DataFrame):
                        response = f"Result ({intent}):\n{result['result'].to_string()}"
                    elif isinstance(result["result"], pd.Series):
                        response = f"Result ({intent}):\n{result['result'].to_string()}"
                    else:
                        response = f"Result ({intent}): {result['result']}"
                else:
                    response = f"Error: {result['error']}"
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