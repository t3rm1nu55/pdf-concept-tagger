"""
Quick test script for experimentation backend
"""

import requests
import json
import base64

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{API_URL}/health")
    print("Health:", response.json())

def test_prompt_experiment():
    """Test prompt experimentation"""
    data = {
        "prompt": "Extract all dates from this text: The project started on 2024-01-15 and will complete on 2024-06-30. The meeting is scheduled for 2024-03-20.",
        "model": "gpt-4-turbo-preview",
        "provider": "openai",
        "temperature": 0.1
    }
    
    response = requests.post(f"{API_URL}/api/v1/prompts/experiment", json=data)
    print("\nPrompt Experiment Result:")
    print(json.dumps(response.json(), indent=2))

def test_models():
    """Test model switching"""
    response = requests.get(f"{API_URL}/api/v1/models")
    print("\nAvailable Models:")
    print(json.dumps(response.json(), indent=2))

def test_switch_model():
    """Test switching model"""
    data = {
        "provider": "openai",
        "model": "gpt-4-turbo-preview"
    }
    response = requests.post(f"{API_URL}/api/v1/models/switch", json=data)
    print("\nSwitch Model Result:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("🧪 Testing Experimentation Backend\n")
    
    try:
        test_health()
        test_models()
        test_prompt_experiment()
        print("\n✅ All tests passed!")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python server.py")
    except Exception as e:
        print(f"❌ Error: {e}")
