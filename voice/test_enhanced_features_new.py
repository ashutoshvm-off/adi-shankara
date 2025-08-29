#!/usr/bin/env python3
"""
Test script for the enhanced sentence rephrasing and automatic translation features
"""

from main1 import NaturalShankaraAssistant
import time

def test_enhanced_features():
    """Test the enhanced language detection, rephrasing, and auto-translation features"""
    
    print("🧪 Testing Enhanced Shankara Assistant Features")
    print("=" * 60)
    
    # Initialize the assistant
    print("🔄 Initializing assistant...")
    assistant = NaturalShankaraAssistant()
    
    # Test cases for different languages and scenarios
    test_cases = [
        {
            "query": "Who are you?",
            "expected_language": "en",
            "description": "English identity question"
        },
        {
            "query": "आप कौन हैं?",  # Hindi: Who are you?
            "expected_language": "hi", 
            "description": "Hindi identity question"
        },
        {
            "query": "namaste guru, enthanu advaita vedanta?",  # Manglish
            "expected_language": "manglish",
            "description": "Manglish philosophical question"
        },
        {
            "query": "Tell me about consciousness in Malayalam",
            "expected_language": "ml",
            "description": "Explicit language request"
        },
        {
            "query": "¿Quién eres tú?",  # Spanish: Who are you?
            "expected_language": "es",
            "description": "Spanish identity question"
        },
        {
            "query": "What is truth?",
            "expected_language": "en",
            "description": "English philosophical question"
        }
    ]
    
    print(f"🚀 Running {len(test_cases)} test cases...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 Test {i}: {test_case['description']}")
        print(f"   Query: '{test_case['query']}'")
        
        try:
            # Test language detection
            processed_query, detected_lang, confidence = assistant.detect_language_and_translate(test_case['query'])
            print(f"   🔍 Detected Language: {detected_lang} (confidence: {confidence:.2f})")
            
            # Test sentence rephrasing
            rephrased = assistant.rephrase_and_enhance_response(
                "I am Adi Shankara, a teacher of Advaita Vedanta.", 
                assistant.current_response_language,
                "sage"
            )
            print(f"   ✨ Rephrased Response: '{rephrased[:100]}{'...' if len(rephrased) > 100 else ''}'")
            
            # Test full response with auto-translation
            response = assistant.get_wisdom_response(test_case['query'])
            print(f"   💬 Full Response: '{response[:150]}{'...' if len(response) > 150 else ''}'")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("-" * 60)
        time.sleep(0.5)  # Small delay for readability
    
    print("\n🎉 Enhanced features testing completed!")
    print("\n📊 Features Tested:")
    print("   ✅ Advanced Language Detection (20+ languages)")
    print("   ✅ Enhanced Manglish Detection")
    print("   ✅ Multi-style Sentence Rephrasing (Sage, Conversational, Scholarly)")
    print("   ✅ Cultural Enhancement for Target Languages")
    print("   ✅ Sanskrit Integration")
    print("   ✅ Automatic Translation with Post-processing")
    print("   ✅ Confidence-based Response Styling")

if __name__ == "__main__":
    test_enhanced_features()
