#!/usr/bin/env python3
"""
Debug script to test full Malayalam response flow
"""

import sys
import os

# Add the current directory to the path so we can import main1
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main1 import NaturalShankaraAssistant

def test_full_malayalam_flow():
    """Test the full Malayalam response flow"""
    print("🔍 Testing Full Malayalam Response Flow")
    print("=" * 50)
    
    # Initialize the assistant
    assistant = NaturalShankaraAssistant()
    
    query = "Can you speak in Malayalam?"
    print(f"\nTesting query: '{query}'")
    
    print(f"Malayalam mode before: {assistant.malayalam_mode}")
    
    # Test the direct method first
    print("\n1. Testing respond_in_malayalam directly:")
    malayalam_response = assistant.respond_in_malayalam(query)
    print(f"  Malayalam mode after direct call: {assistant.malayalam_mode}")
    print(f"  Direct response: {malayalam_response is not None}")
    if malayalam_response:
        print(f"  Response: {malayalam_response[:100]}...")
    
    # Reset Malayalam mode
    assistant.malayalam_mode = False
    
    # Test the full response flow
    print("\n2. Testing get_wisdom_response:")
    full_response = assistant.get_wisdom_response(query)
    print(f"  Malayalam mode after full response: {assistant.malayalam_mode}")
    print(f"  Full response: {full_response[:100]}...")
    
    # Test the second query behavior
    print("\n3. Testing follow-up query in Malayalam mode:")
    second_query = "Who are you?"
    print(f"Second query: '{second_query}'")
    print(f"Malayalam mode before second query: {assistant.malayalam_mode}")
    
    second_response = assistant.get_wisdom_response(second_query)
    print(f"Malayalam mode after second query: {assistant.malayalam_mode}")
    print(f"Second response: {second_response[:100]}...")

if __name__ == "__main__":
    test_full_malayalam_flow()
