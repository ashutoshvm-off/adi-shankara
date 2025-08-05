#!/usr/bin/env python3
"""
Test Wikipedia Search and Translation Functionality
Test the enhanced Wikipedia retrieval and language translation features
"""

import os
import sys

# Add the voice directory to the path
voice_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, voice_dir)

try:
    from main1 import NaturalShankaraAssistant
except ImportError as e:
    print(f"❌ Could not import main1: {e}")
    sys.exit(1)

def test_wikipedia_search_and_translation():
    """Test various Wikipedia search and translation scenarios"""
    print("🧪 Testing Wikipedia Search and Translation Features")
    print("=" * 60)
    
    # Initialize the assistant
    try:
        assistant = NaturalShankaraAssistant()
        print("✅ Assistant initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize assistant: {e}")
        return False
    
    # Test cases for Wikipedia search and translation
    test_cases = [
        # Basic Wikipedia searches
        {
            "query": "search wikipedia for quantum physics",
            "description": "Basic Wikipedia search"
        },
        {
            "query": "what does wikipedia say about meditation",
            "description": "Wikipedia search with natural language"
        },
        {
            "query": "tell me about Mahatma Gandhi",
            "description": "Information request"
        },
        
        # Wikipedia search with translation
        {
            "query": "search wikipedia for yoga in hindi",
            "description": "Wikipedia search with Hindi translation"
        },
        {
            "query": "tell me about Buddhism in malayalam",
            "description": "Wikipedia search with Malayalam translation"
        },
        {
            "query": "what is artificial intelligence in tamil",
            "description": "Wikipedia search with Tamil translation"
        },
        
        # Translation of content
        {
            "query": "translate 'consciousness is the foundation of all existence' to sanskrit",
            "description": "Direct translation request"
        },
        {
            "query": "say 'the Self is eternal and blissful' in hindi",
            "description": "Translation with natural language"
        },
        
        # Complex queries
        {
            "query": "search wikipedia for Indian philosophy in spanish",
            "description": "Complex search with Spanish translation"
        },
        {
            "query": "find information about climate change in french",
            "description": "Search with French translation"
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}/{total_tests}: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        print("-" * 40)
        
        try:
            # Get response from assistant
            response = assistant.get_wisdom_response(test_case['query'])
            
            if response:
                print(f"✅ Response received:")
                print(f"{response[:200]}..." if len(response) > 200 else response)
                successful_tests += 1
            else:
                print("❌ No response received")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"✅ Successful: {successful_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - successful_tests}/{total_tests}")
    print(f"📈 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    return successful_tests == total_tests

def test_language_detection():
    """Test language detection and mapping"""
    print("\n🌐 Testing Language Detection and Mapping")
    print("=" * 50)
    
    try:
        assistant = NaturalShankaraAssistant()
        
        # Test language extraction
        test_queries = [
            "translate this to hindi",
            "say something in malayalam", 
            "tell me about yoga in tamil",
            "search for meditation in sanskrit",
            "what is consciousness in spanish"
        ]
        
        for query in test_queries:
            language = assistant.extract_target_language(query)
            print(f"Query: '{query}' → Language: {language}")
        
        # Test topic extraction
        print("\n🔍 Testing Topic Extraction")
        topic_queries = [
            "search wikipedia for quantum mechanics",
            "what is artificial intelligence",
            "tell me about climate change",
            "find information about yoga"
        ]
        
        for query in topic_queries:
            topic = assistant.extract_search_topic(query, "search wikipedia for")
            if not topic:
                # Try other triggers
                for trigger in ["what is", "tell me about", "find information about"]:
                    if trigger in query.lower():
                        topic = assistant.extract_search_topic(query, trigger)
                        break
            print(f"Query: '{query}' → Topic: {topic}")
            
    except Exception as e:
        print(f"❌ Language detection test failed: {e}")

def test_translation_functionality():
    """Test the translation functionality specifically"""
    print("\n🔤 Testing Translation Functionality")
    print("=" * 40)
    
    try:
        assistant = NaturalShankaraAssistant()
        
        # Test basic translation
        test_text = "Consciousness is the foundation of all existence"
        target_languages = ["hindi", "malayalam", "spanish", "french"]
        
        for lang in target_languages:
            try:
                translated = assistant.translate_to_language(test_text, lang)
                print(f"\n{lang.title()}:")
                print(f"Original: {test_text}")
                print(f"Translated: {translated}")
            except Exception as e:
                print(f"❌ Translation to {lang} failed: {e}")
                
    except Exception as e:
        print(f"❌ Translation test failed: {e}")

def main():
    """Main test function"""
    print("🔬 Wikipedia Search and Translation Test Suite")
    print("=" * 60)
    
    # Run all tests
    try:
        # Test 1: Language detection
        test_language_detection()
        
        # Test 2: Translation functionality  
        test_translation_functionality()
        
        # Test 3: Full Wikipedia search and translation
        success = test_wikipedia_search_and_translation()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 All tests completed! Wikipedia search and translation features are working.")
        else:
            print("⚠️  Some tests had issues. Check the output above for details.")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    main()
