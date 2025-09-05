"""
Phase 3 Testing - Smart Code Generation Validation
Test all Phase 3 success criteria with minimal code
"""

import requests
import json
import time
from pathlib import Path


def test_phase_3():
    """Test Phase 3: Smart Code Generation - validate all success criteria"""
    
    base_url = "http://localhost:8000"
    
    # Upload test file first
    print("🔧 Uploading test data...")
    with open("/Users/gkratka/Documents/data-modeling-4/backend/test_data.csv", "rb") as f:
        files = {"file": ("test_data.csv", f, "text/csv")}
        upload_response = requests.post(f"{base_url}/api/v1/files/upload", files=files)
        file_id = upload_response.json()["file_id"]
        print(f"✅ File uploaded as {file_id}")
    
    # Phase 3 Success Criteria Tests
    test_cases = [
        {
            "query": "calculate total salary for all employees",
            "criteria": "Complex queries with calculate keyword",
            "expected_intent": "llm_generate"
        },
        {
            "query": "find the top 5 customers by total purchase amount", 
            "criteria": "Top N with complex analysis",
            "expected_intent": "llm_generate"
        },
        {
            "query": "compute the percentage of employees in each department",
            "criteria": "Percentage calculation",
            "expected_intent": "llm_generate"
        },
        {
            "query": "analyze salary by region and department",
            "criteria": "Multi-dimensional analysis", 
            "expected_intent": "llm_generate"
        }
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for i, test in enumerate(test_cases):
        print(f"\n🧪 Test {i+1}/{total_tests}: {test['criteria']}")
        print(f"Query: '{test['query']}'")
        
        start_time = time.time()
        
        # Send chat request
        chat_response = requests.post(
            f"{base_url}/api/v1/chat",
            json={
                "message": test["query"],
                "session_id": "phase3_test",
                "file_ids": [file_id]
            }
        )
        
        response_time = time.time() - start_time
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()["response"]
            
            # Check if LLM code generation was triggered
            if "Generated Code:" in response_data:
                print("✅ LLM code generation triggered")
                
                # Check if code was generated
                if "result = " in response_data or "df." in response_data:
                    print("✅ Valid pandas code generated")
                    
                    # Check if execution was successful  
                    if "Result:" in response_data and "Error:" not in response_data:
                        print("✅ Code executed successfully")
                        success_count += 1
                        
                        # Check response time (target: < 5 seconds)
                        if response_time < 5.0:
                            print(f"✅ Response time: {response_time:.2f}s (target: <5s)")
                        else:
                            print(f"⚠️ Response time: {response_time:.2f}s (target: <5s)")
                    else:
                        print("❌ Code execution failed")
                        print(f"Response: {response_data}")
                else:
                    print("❌ Invalid pandas code generated")
            else:
                print("❌ LLM code generation not triggered")
                print(f"Response: {response_data}")
        else:
            print(f"❌ Request failed: {chat_response.status_code}")
    
    # Calculate success rate
    success_rate = (success_count / total_tests) * 100
    print(f"\n📊 Phase 3 Results:")
    print(f"✅ Success Rate: {success_rate}% (target: 80%+)")
    print(f"✅ Tests Passed: {success_count}/{total_tests}")
    
    # Validate success criteria
    if success_rate >= 80:
        print("🎉 Phase 3 SUCCESS: All criteria met!")
        return True
    else:
        print("❌ Phase 3 FAILED: Success rate below 80%")
        return False


if __name__ == "__main__":
    test_phase_3()