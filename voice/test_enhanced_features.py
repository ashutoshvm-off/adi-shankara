#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced language detection and Wikipedia search features
of the Adi Shankara Assistant.
"""

import sys
import os

# Add the current directory to the path to import main1
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_language_detection_and_response():
    """Test the enhanced language detection and automatic response in detected language"""
    
    print("=" * 60)
    print("🧪 TESTING ENHANCED LANGUAGE DETECTION & RESPONSE")
    print("=" * 60)
    
    try:
        from main1 import NaturalShankaraAssistant
        
        # Initialize the assistant
        print("Initializing Adi Shankara Assistant...")
        assistant = NaturalShankaraAssistant()
        
        # Test cases for different languages
        test_queries = [
            # English queries
            ("Hello, who are you?", "English"),
            ("Tell me about Advaita Vedanta", "English"),
            ("What is Wikipedia's information about Albert Einstein?", "English"),
            
            # Malayalam queries
            ("നമസ്കാരം, നിങ്ങൾ ആരാണ്?", "Malayalam"),
            ("അദ്വൈതത്തെക്കുറിച്ച് പറയൂ", "Malayalam"),
            
            # Hindi queries (if translation works)
            ("नमस्ते, आप कौन हैं?", "Hindi"),
            ("अद्वैत वेदांत के बारे में बताइए", "Hindi"),
            
            # Wikipedia search queries
            ("Search Wikipedia for quantum physics", "English + Wikipedia"),
            ("Tell me about Mahatma Gandhi from Wikipedia", "English + Wikipedia"),
            ("What is neural networks in malayalam", "Malayalam + Wikipedia"),
        ]
        
        print("\n🔄 Testing different language inputs and responses...")
        print("-" * 60)
        
        for i, (query, test_type) in enumerate(test_queries):
            print(f"\n📝 Test {i+1}: {test_type}")
            print(f"🗣️ Input: {query}")
            
            try:
                # Get the response using the enhanced system
                response = assistant.get_wisdom_response(query)
                print(f"🤖 Response: {response[:200]}..." if len(response) > 200 else f"🤖 Response: {response}")
                print(f"🌐 Response Language: {assistant.current_response_language}")
                
            except Exception as e:
                print(f"❌ Error processing query: {e}")
            
            print("-" * 40)
        
        print("\n✅ Language detection and response testing completed!")
        
    except ImportError as e:
        print(f"❌ Failed to import assistant: {e}")
        print("Make sure main1.py is in the same directory.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_wikipedia_integration():
    """Test the enhanced Wikipedia search functionality"""
    
    print("\n" + "=" * 60)
    print("🧪 TESTING ENHANCED WIKIPEDIA INTEGRATION")
    print("=" * 60)
    
    try:
        from main1 import NaturalShankaraAssistant
        
        assistant = NaturalShankaraAssistant()
        
        # Wikipedia test queries
        wiki_queries = [
            "Tell me about artificial intelligence",
            "What is quantum computing?",
            "Search Wikipedia for Adi Shankara",
            "Find information about meditation",
            "Explain neural networks",
            "What does Wikipedia say about consciousness?",
        ]
        
        print("\n🔍 Testing Wikipedia search capabilities...")
        print("-" * 60)
        
        for i, query in enumerate(wiki_queries):
            print(f"\n📝 Wikipedia Test {i+1}")
            print(f"🔍 Query: {query}")
            
            try:
                response = assistant.handle_wikipedia_requests(query)
                if response:
                    print(f"📖 Response: {response[:300]}..." if len(response) > 300 else f"📖 Response: {response}")
                else:
                    print("ℹ️ No Wikipedia response triggered (query may be handled by other components)")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 40)
        
        print("\n✅ Wikipedia integration testing completed!")
        
    except Exception as e:
        print(f"❌ Error during Wikipedia testing: {e}")

def test_translation_features():
    """Test the translation capabilities"""
    
    print("\n" + "=" * 60)
    print("🧪 TESTING TRANSLATION FEATURES")
    print("=" * 60)
    
    try:
        from main1 import NaturalShankaraAssistant
        
        assistant = NaturalShankaraAssistant()
        
        # Translation test cases
        translation_tests = [
            ("Translate 'Hello world' to Hindi", "English to Hindi"),
            ("Say 'consciousness is everything' in Malayalam", "English to Malayalam"),
            ("Convert 'Advaita Vedanta' to Tamil", "English to Tamil"),
            ("What is artificial intelligence in Hindi", "Wikipedia + Translation"),
        ]
        
        print("\n🌐 Testing translation capabilities...")
        print("-" * 60)
        
        for i, (query, test_type) in enumerate(translation_tests):
            print(f"\n📝 Translation Test {i+1}: {test_type}")
            print(f"🔄 Query: {query}")
            
            try:
                response = assistant.handle_wikipedia_requests(query)
                if response:
                    print(f"🌐 Response: {response[:250]}..." if len(response) > 250 else f"🌐 Response: {response}")
                else:
                    # Try general response system
                    response = assistant.get_wisdom_response(query)
                    print(f"🤖 General Response: {response[:250]}..." if len(response) > 250 else f"🤖 General Response: {response}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 40)
        
        print("\n✅ Translation testing completed!")
        
    except Exception as e:
        print(f"❌ Error during translation testing: {e}")

def main():
    """Main test function"""
    
    print("🚀 ENHANCED ADI SHANKARA ASSISTANT - FEATURE TESTING")
    print("=" * 60)
    print("This script tests the enhanced features:")
    print("✨ Automatic language detection and response")
    print("📖 Enhanced Wikipedia search with human-like responses")
    print("🌐 Multi-language translation capabilities")
    print("🤖 Natural conversation flow")
    print("=" * 60)
    
    # Run all tests
    test_language_detection_and_response()
    test_wikipedia_integration()
    test_translation_features()
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS COMPLETED!")
    print("=" * 60)
    print("\n💡 Usage Tips:")
    print("- The assistant now automatically detects the language you speak/type")
    print("- It will respond in the same language you used")
    print("- Wikipedia searches are more natural and comprehensive")
    print("- You can ask for translations to any supported language")
    print("- All existing features are preserved and enhanced")
    print("\n🗣️ Try starting a conversation with: python main1.py")

if __name__ == "__main__":
    main()
