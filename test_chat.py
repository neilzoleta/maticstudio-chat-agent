#!/usr/bin/env python3
"""
Test script for MATIC Studio Chat Agent
"""

import requests
import json
import time

def test_chat_api():
    """Test the chat API endpoint"""
    
    # Test messages
    test_messages = [
        "What services does MATIC Studio offer?",
        "I need help with business process automation",
        "Can you help me schedule a consultation call?"
    ]
    
    print("🧪 Testing MATIC Studio Chat Agent API...")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: {message}")
        
        try:
            response = requests.post(
                'http://localhost:5001/api/chat',
                json={
                    'message': message,
                    'conversation_history': []
                },
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response'][:100]}...")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the Flask app is running on port 5001")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        time.sleep(1)  # Small delay between requests
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5001/health')
        if response.status_code == 200:
            data = response.json()
            print(f"💚 Health Check: {data}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 MATIC Studio Chat Agent Test Suite")
    print("Make sure the Flask app is running: python flask_app.py (port 5001)")
    print()
    
    # Test health endpoint first
    test_health_endpoint()
    
    # Test chat API
    test_chat_api() 