#!/usr/bin/env python3
"""
Test script to verify Malayalam conversation functionality
"""

import sys
import os

# Add the current directory to the path so we can import main1
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main1 import NaturalShankaraAssistant

def test_malayalam_conversation():
    """Test Malayalam conversation mode functionality"""
    print("🧪 Testing Malayalam Conversation Mode")
    print("=" * 50)
    
    # Initialize the assistant
    print("Initializing Adi Shankara assistant...")
    assistant = NaturalShankaraAssistant()
    
    print(f"Initial Malayalam mode: {assistant.malayalam_mode}")
    
    # Test Malayalam mode activation
    test_queries = [
        "Can you speak in Malayalam?",
        "നമസ്കാരം! എങ്ങനെയുണ്ട്?",
        "Who are you?",
        "Tell me about Advaita Vedanta",
        "What is Maya?",
        "Where were you born?",
        "Thank you",
        "Switch to English please"
    ]
    
    print("\n🎭 Testing Malayalam Mode Activation and Responses:")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: '{query}' ---")
        
        # Get response
        response = assistant.get_wisdom_response(query)
        
        # Check if Malayalam mode was activated/deactivated
        print(f"Malayalam mode after query: {assistant.malayalam_mode}")
        print(f"Response: {response[:100]}{'...' if len(response) > 100 else ''}")
        
        # Test the voice output (optional)
        test_voice = input(f"Test voice for this response? (y/n): ").lower().strip()
        if test_voice == 'y':
            try:
                assistant.speak_with_enhanced_quality(response, pause_before=0.5, pause_after=1.0)
            except Exception as e:
                print(f"Voice test failed: {e}")
        
        print("-" * 30)
    
    print("\n✅ Malayalam conversation test completed!")
    print("\nExpected behavior:")
    print("1. Malayalam mode should activate when requesting Malayalam")
    print("2. All subsequent responses should be in Malayalam")
    print("3. Should switch back to English when requested")
    print("4. Malayalam voice synthesis should work with Google TTS")

def test_malayalam_starters():
    """Test Malayalam conversation starters"""
    print("\n🎭 Testing Malayalam Conversation Starters:")
    
    assistant = NaturalShankaraAssistant()
    
    # Activate Malayalam mode
    assistant.malayalam_mode = True
    
    print("Malayalam conversation starters:")
    for i, starter in enumerate(assistant.malayalam_conversation_starters, 1):
        print(f"{i}. {starter[:80]}{'...' if len(starter) > 80 else ''}")
    
    # Test a conversation starter
    import random
    test_starter = random.choice(assistant.malayalam_conversation_starters)
    print(f"\nTesting random Malayalam starter:")
    print(f"Selected: {test_starter}")
    
    test_voice = input("Test voice for this starter? (y/n): ").lower().strip()
    if test_voice == 'y':
        try:
            assistant.speak_with_enhanced_quality(test_starter, pause_before=0.5, pause_after=1.0)
        except Exception as e:
            print(f"Voice test failed: {e}")

if __name__ == "__main__":
    try:
        test_malayalam_conversation()
        test_malayalam_starters()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
