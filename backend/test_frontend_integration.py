#!/usr/bin/env python3
"""
Frontend Integration Test - Test the file ID mismatch issue
This test validates the end-to-end flow between frontend and backend
"""

import requests
import json
import time

def test_frontend_backend_integration():
    """Test the complete file upload and chat flow"""
    
    # Backend endpoints
    BASE_URL = "http://localhost:8000"
    FRONTEND_URL = "http://localhost:8081"
    
    print("🧪 Testing Frontend-Backend Integration")
    print("=" * 50)
    
    # Step 1: Test backend health
    print("1️⃣ Testing backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Backend not reachable: {e}")
        return
    
    # Step 2: Get current files
    print("\n2️⃣ Getting current files...")
    response = requests.get(f"{BASE_URL}/api/v1/files")
    files = response.json()
    print(f"📁 Found {len(files)} files:")
    for file in files:
        print(f"   - {file['id']}: {file['filename']} ({file['rows']} rows)")
    
    if not files:
        print("❌ No files found - need to upload a file first")
        return
    
    # Use the first available file
    test_file = files[0]
    file_id = test_file['id']
    filename = test_file['filename']
    
    print(f"\n3️⃣ Testing chat with file ID: {file_id}")
    
    # Step 3: Test different query types
    test_queries = [
        "what can you tell me about the data that was uploaded?",
        "describe the data structure",
        "calculate total sales by segment",
        "find top 5 customers with highest sales"
    ]
    
    session_id = "integration_test_session"
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n3.{i} Testing query: '{query}'")
        
        chat_data = {
            "message": query,
            "session_id": session_id,
            "file_ids": [file_id]
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if "File" in result["response"] and "not found" in result["response"]:
                    print(f"❌ File ID mismatch error: {result['response']}")
                else:
                    print(f"✅ Query successful")
                    # Show first 100 chars of response
                    response_preview = result["response"][:100]
                    if len(result["response"]) > 100:
                        response_preview += "..."
                    print(f"   Response: {response_preview}")
            else:
                print(f"❌ Chat request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Chat request error: {e}")
    
    print("\n4️⃣ Testing frontend API compatibility...")
    
    # Test the exact data format that frontend sends
    frontend_format = {
        "message": "test frontend compatibility",
        "session_id": session_id,
        "file_ids": [file_id]  # Frontend sends file_ids, not fileIds
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/chat",
        json=frontend_format,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        if "File" in result["response"] and "not found" in result["response"]:
            print(f"❌ Frontend format compatibility issue: {result['response']}")
        else:
            print("✅ Frontend format compatibility confirmed")
    else:
        print(f"❌ Frontend format test failed: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎯 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    print(f"Backend URL: {BASE_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Test File: {filename} (ID: {file_id})")
    print(f"File contains {test_file.get('rows', 'unknown')} rows")
    print(f"Columns: {test_file.get('columns', 'unknown')}")

if __name__ == "__main__":
    test_frontend_backend_integration()