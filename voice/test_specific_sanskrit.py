#!/usr/bin/env python3
"""
Direct test for the specific Sanskrit query 'कः त्वम्?'
"""

from main1 import NaturalShankaraAssistant

def test_specific_sanskrit_query():
    """Test the specific Sanskrit query that was failing"""
    print("🕉️ Testing Specific Sanskrit Query: कः त्वम्?")
    print("=" * 50)
    
    assistant = NaturalShankaraAssistant()
    
    # Test the specific query
    query = "कः त्वम्?"
    print(f"📝 Sanskrit Query: {query}")
    print("🔄 Processing...")
    
    try:
        response = assistant.get_wisdom_response(query)
        print(f"🕉️ Response: {response}")
    except Exception as e:
        print(f"⚠️ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_sanskrit_query()
