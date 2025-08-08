#!/usr/bin/env python3
"""
Enhanced Wikipedia-to-Language Demo
Demonstrates the powerful Wikipedia retrieval and translation system
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_wikipedia_to_language():
    """Demonstrate Wikipedia content retrieval and translation to any language"""
    
    print("🌍 WIKIPEDIA TO ANY LANGUAGE CONVERTER")
    print("=" * 60)
    print("This demo shows how to get Wikipedia content in any language!")
    print("=" * 60)
    
    try:
        from wikipedia_translator import WikipediaTranslator
        
        # Initialize the translator
        translator = WikipediaTranslator()
        
        # Demo queries - various topics in different languages
        demo_queries = [
            # Technology topics
            "Tell me about artificial intelligence in Hindi",
            "What is quantum computing in Malayalam", 
            "Explain machine learning in Tamil",
            "Search for neural networks in Spanish",
            
            # Science topics
            "Albert Einstein in French",
            "Quantum physics in German",
            "DNA in Italian",
            "Climate change in Portuguese",
            
            # Philosophy & Culture
            "Buddhism in Japanese",
            "Yoga in Russian",
            "Meditation in Chinese",
            "Consciousness in Arabic",
            
            # Historical figures
            "Mahatma Gandhi in Bengali",
            "Leonardo da Vinci in Telugu",
            "Isaac Newton in Kannada",
            "Marie Curie in Gujarati",
        ]
        
        print("\n🔄 Processing Wikipedia content in multiple languages...")
        print("-" * 60)
        
        for i, query in enumerate(demo_queries):
            print(f"\n📝 Demo {i+1}: {query}")
            print("🔍 Processing...")
            
            try:
                result = translator.process_query(query)
                
                if result['success']:
                    print(f"✅ Success!")
                    print(f"📰 Title: {result['title']}")
                    print(f"🌐 Language: {result['language'].title()}")
                    print(f"📖 Content Preview: {result['content'][:150]}...")
                    print(f"🔗 Source: {result.get('url', 'N/A')}")
                else:
                    print(f"❌ Failed: {result['message']}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 40)
        
        print("\n✅ Demo completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure wikipedia_translator.py is in the same directory.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def interactive_wikipedia_translator():
    """Interactive mode for user to test Wikipedia translation"""
    
    print("\n🎮 INTERACTIVE WIKIPEDIA TRANSLATOR")
    print("=" * 60)
    print("Ask for any Wikipedia topic in any language!")
    print("Examples:")
    print("  - 'Tell me about space exploration in Hindi'")
    print("  - 'What is photosynthesis in Malayalam'")
    print("  - 'Explain gravity in Spanish'")
    print("Type 'quit' to exit.")
    print("-" * 60)
    
    try:
        from wikipedia_translator import WikipediaTranslator
        translator = WikipediaTranslator()
        
        while True:
            try:
                query = input("\n🗣️ Your request: ").strip()
                
                if not query:
                    continue
                    
                if query.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Thanks for using the Wikipedia translator!")
                    break
                
                print("🔍 Searching and translating...")
                result = translator.process_query(query)
                
                if result['success']:
                    print(f"\n📰 Title: {result['title']}")
                    print(f"🌐 Language: {result['language'].title()}")
                    print(f"📄 Detail Level: {result['detail_level'].title()}")
                    print(f"\n📖 Content:\n{result['content']}")
                    print(f"\n🔗 Wikipedia URL: {result.get('url', 'N/A')}")
                else:
                    print(f"\n❌ {result['message']}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Setup error: {e}")

def test_language_coverage():
    """Test the language coverage and translation quality"""
    
    print("\n🌏 LANGUAGE COVERAGE TEST")
    print("=" * 60)
    
    try:
        from wikipedia_translator import WikipediaTranslator
        translator = WikipediaTranslator()
        
        # Test a simple topic in multiple languages
        topic = "artificial intelligence"
        test_languages = [
            'hindi', 'malayalam', 'tamil', 'telugu', 'kannada',
            'marathi', 'gujarati', 'bengali', 'spanish', 'french',
            'german', 'italian', 'portuguese', 'russian', 'chinese',
            'japanese', 'korean', 'arabic'
        ]
        
        print(f"Testing topic: '{topic}' in {len(test_languages)} languages")
        print("-" * 60)
        
        successful = 0
        for i, lang in enumerate(test_languages):
            try:
                query = f"tell me about {topic} in {lang}"
                result = translator.process_query(query)
                
                if result['success']:
                    print(f"✅ {lang.title()}: Success")
                    successful += 1
                else:
                    print(f"❌ {lang.title()}: Failed")
                    
            except Exception as e:
                print(f"⚠️ {lang.title()}: Error - {e}")
        
        print(f"\n📊 Results: {successful}/{len(test_languages)} languages successful")
        print(f"🎯 Success rate: {(successful/len(test_languages)*100):.1f}%")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

def integration_demo():
    """Show how to integrate with the main assistant"""
    
    print("\n🔗 INTEGRATION WITH MAIN ASSISTANT")
    print("=" * 60)
    print("Showing how the enhanced Wikipedia translator integrates with Adi Shankara Assistant")
    print("-" * 60)
    
    try:
        # Test queries that would work with the main assistant
        integration_queries = [
            "Tell me about consciousness in Malayalam",
            "What is meditation in Hindi",
            "Explain Advaita Vedanta in Tamil",
            "Search Wikipedia for yoga in Spanish",
            "Who was Adi Shankara in French"
        ]
        
        print("These queries would work seamlessly with the main assistant:")
        for i, query in enumerate(integration_queries):
            print(f"{i+1}. {query}")
        
        print(f"\n💡 The assistant now:")
        print("✨ Automatically detects the language you want")
        print("📖 Searches Wikipedia intelligently")
        print("🌐 Translates content accurately")
        print("🤖 Responds naturally as Adi Shankara")
        print("🎯 Preserves all original features")
        
        print(f"\n🗣️ To use: python main1.py")
        print("Then just ask naturally in any language!")
        
    except Exception as e:
        print(f"❌ Integration demo error: {e}")

def main():
    """Main demo function"""
    
    print("🚀 ENHANCED WIKIPEDIA-TO-ANY-LANGUAGE SYSTEM")
    print("=" * 70)
    print("Comprehensive demonstration of Wikipedia content retrieval and translation")
    print("=" * 70)
    
    try:
        # Run all demos
        demo_wikipedia_to_language()
        test_language_coverage()
        integration_demo()
        
        # Offer interactive mode
        print("\n" + "=" * 70)
        response = input("🎮 Would you like to try the interactive mode? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            interactive_wikipedia_translator()
        
        print("\n🎉 All demos completed!")
        print("=" * 70)
        print("💡 Key Features Demonstrated:")
        print("🌍 Multi-language Wikipedia content retrieval")
        print("🔄 Intelligent topic extraction from natural queries")
        print("🌐 High-quality translation to 18+ languages")
        print("📖 Adjustable detail levels (brief, summary, detailed)")
        print("🤖 Natural integration with conversational AI")
        print("✨ Error handling and fallback mechanisms")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Thanks for testing!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    main()
