#!/usr/bin/env python3
"""
Debug script to test Malayalam mode activation
"""

import sys
import os

# Add the current directory to the path so we can import main1
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main1 import NaturalShankaraAssistant

def test_malayalam_detection():
    """Test Malayalam trigger detection"""
    print("🔍 Testing Malayalam Trigger Detection")
    print("=" * 50)
    
    # Initialize the assistant
    assistant = NaturalShankaraAssistant()
    
    test_queries = [
        "Can you speak in Malayalam?",
        "speak in malayalam",
        "malayalam",
        "reply in malayalam"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        
        # Check the triggers manually
        query_lower = query.lower()
        malayalam_triggers = [
            'malayalam', 'malayalam language', 'reply in malayalam', 'speak in malayalam',
            'continue in malayalam', 'continue speaking in malayalam', 'speak malayalam',
            'tell in malayalam', 'explain in malayalam', 'say in malayalam'
        ]
        
        print(f"Query lower: '{query_lower}'")
        
        triggered = any(trigger in query_lower for trigger in malayalam_triggers)
        print(f"Should trigger Malayalam: {triggered}")
        
        if triggered:
            for trigger in malayalam_triggers:
                if trigger in query_lower:
                    print(f"  - Matched trigger: '{trigger}'")
        
        # Test the actual method
        print(f"Malayalam mode before: {assistant.malayalam_mode}")
        response = assistant.respond_in_malayalam(query)
        print(f"Malayalam mode after: {assistant.malayalam_mode}")
        print(f"Response received: {response is not None}")
        if response:
            print(f"Response: {response[:100]}...")
        
        print("-" * 30)
        
        # Reset for next test
        assistant.malayalam_mode = False

if __name__ == "__main__":
    test_malayalam_detection()
