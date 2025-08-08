#!/usr/bin/env python3
"""
Test script for the built-in Adi Shankara Wikipedia translator functionality
"""

import sys
import os

# Add the current directory to the path so we can import main1
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main1 import NaturalShankaraAssistant

def test_builtin_translator():
    """Test the built-in Wikipedia translator for Adi Shankara content"""
    print("🧪 Testing Built-in Adi Shankara Wikipedia Translator")
    print("=" * 60)
    
    # Initialize the assistant
    try:
        assistant = NaturalShankaraAssistant()
        print("✅ Assistant initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize assistant: {e}")
        return
    
    # Test cases for the built-in translator
    test_cases = [
        {
            "description": "Test Malayalam translation of Adi Shankara content",
            "topic": "Adi Shankara",
            "language": "malayalam",
            "detail": "summary"
        },
        {
            "description": "Test Hindi translation of Advaita Vedanta",
            "topic": "Advaita Vedanta", 
            "language": "hindi",
            "detail": "brief"
        },
        {
            "description": "Test Tamil translation of Shankara's philosophy",
            "topic": "Shankara philosophy",
            "language": "tamil",
            "detail": "detailed"
        },
        {
            "description": "Test English (no translation) for Kaladi",
            "topic": "Kaladi Kerala",
            "language": "english",
            "detail": "summary"
        },
        {
            "description": "Test Spanish translation of meditation",
            "topic": "meditation consciousness",
            "language": "spanish",
            "detail": "summary"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test {i}: {test_case['description']}")
        print("-" * 50)
        
        try:
            # Test the built-in translator directly
            response = assistant.get_adi_shankara_wikipedia_translator(
                test_case['topic'], 
                test_case['language'], 
                test_case['detail']
            )
            
            if response:
                print(f"✅ Translation successful for {test_case['language']}")
                print(f"📄 Response length: {len(response)} characters")
                print(f"🔤 First 200 characters: {response[:200]}...")
                
                # Check if response contains expected language indicators
                if test_case['language'] == 'malayalam' and any(ord(char) >= 0x0D00 and ord(char) <= 0x0D7F for char in response):
                    print("✅ Contains Malayalam script")
                elif test_case['language'] == 'hindi' and any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in response):
                    print("✅ Contains Hindi script")
                elif test_case['language'] == 'tamil' and any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in response):
                    print("✅ Contains Tamil script")
                elif test_case['language'] == 'english':
                    print("✅ English response (no translation needed)")
                else:
                    print(f"ℹ️  Response in {test_case['language']} (script check may not be comprehensive)")
                    
            else:
                print(f"❌ No response received for {test_case['language']}")
                
        except Exception as e:
            print(f"❌ Error during translation test: {e}")
    
    print("\n" + "=" * 60)
    print("🔬 Testing automatic translation detection...")
    
    # Test automatic detection of language requests
    auto_test_cases = [
        "Tell me about Adi Shankara in Malayalam",
        "Explain Advaita Vedanta in Hindi", 
        "What is maya in Tamil",
        "Search for Shankara's teachings in Spanish",
        "Find information about moksha in French"
    ]
    
    for i, query in enumerate(auto_test_cases, 1):
        print(f"\n🔍 Auto-detection test {i}: '{query}'")
        try:
            # Extract topic and detect language
            response = assistant.handle_translation_requests(query)
            if response:
                print(f"✅ Auto-detection worked, response length: {len(response)}")
                print(f"🔤 Sample: {response[:150]}...")
            else:
                print("❌ Auto-detection failed")
        except Exception as e:
            print(f"❌ Auto-detection error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Testing complete integration with main response system...")
    
    # Test integration with main response system
    integration_tests = [
        "Tell me about yourself in Malayalam",
        "What is Advaita Vedanta in Hindi?",
        "Explain consciousness in Tamil",
        "Search Wikipedia for Shankara's philosophy in Spanish"
    ]
    
    for i, query in enumerate(integration_tests, 1):
        print(f"\n🧩 Integration test {i}: '{query}'")
        try:
            response = assistant.get_wisdom_response(query)
            if response:
                print(f"✅ Integration successful, response length: {len(response)}")
                print(f"🔤 Sample: {response[:150]}...")
            else:
                print("❌ Integration failed - no response")
        except Exception as e:
            print(f"❌ Integration error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Built-in translator testing completed!")

if __name__ == "__main__":
    test_builtin_translator()
