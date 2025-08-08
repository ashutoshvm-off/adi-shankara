#!/usr/bin/env python3
"""
Enhanced Integration for Main Assistant
Integrates the powerful Wikipedia-to-language translator with the main Adi Shankara Assistant
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def enhance_main_assistant():
    """Add enhanced Wikipedia translation capabilities to the main assistant"""
    
    try:
        from main1 import NaturalShankaraAssistant
        from wikipedia_translator import WikipediaTranslator
        
        # Create enhanced assistant class
        class EnhancedShankaraAssistant(NaturalShankaraAssistant):
            """Enhanced version with powerful Wikipedia translation"""
            
            def __init__(self, qa_file="shankaracharya_qa.txt"):
                super().__init__(qa_file)
                # Add the Wikipedia translator
                self.wiki_translator = WikipediaTranslator()
                print("🌍 Enhanced Wikipedia translator loaded!")
            
            def enhanced_wikipedia_search(self, query):
                """Use the enhanced Wikipedia translator for better results"""
                try:
                    result = self.wiki_translator.process_query(query)
                    
                    if result['success']:
                        # Create natural response as Adi Shankara
                        intro_phrases = [
                            f"I have explored the vast repository of knowledge and found this wisdom about '{result['topic']}'",
                            f"Through my inquiry into the accumulated learning of humanity, I can share this about '{result['topic']}'",
                            f"From the great storehouse of human understanding, here is what I discovered about '{result['topic']}'",
                            f"My search through the extensive collection of knowledge reveals this about '{result['topic']}'",
                        ]
                        
                        import random
                        intro = random.choice(intro_phrases)
                        
                        # Add language note if translated
                        if result['language'] != 'english':
                            language_note = f" (shared in {result['language'].title()})"
                            intro += language_note
                        
                        response = f"{intro}:\n\n{result['content']}"
                        
                        # Add engaging closing
                        closings = [
                            "\n\nI hope this knowledge serves your understanding well! What other mysteries would you like to explore?",
                            "\n\nMay this wisdom be helpful to you! Is there anything else you wish to discover?",
                            "\n\nI trust this information brings clarity to your inquiry. What other questions arise in your mind?",
                        ]
                        
                        response += random.choice(closings)
                        return response
                    else:
                        return f"My friend, I searched diligently but couldn't find comprehensive information about '{result.get('topic', 'that topic')}' in the great repository of knowledge. Perhaps you could try a different way of asking, or inquire about a related subject?"
                
                except Exception as e:
                    return f"I encountered some difficulty in my search for knowledge. The path to understanding sometimes has obstacles. Please try asking in a different way, my friend."
            
            def handle_wikipedia_requests(self, query):
                """Enhanced Wikipedia handling using the new translator"""
                query_lower = query.lower().strip()
                
                # Check if this is a Wikipedia/information request
                wikipedia_indicators = [
                    "tell me about", "what is", "who is", "explain", "search for",
                    "find information", "look up", "wikipedia", "information about",
                    "details about", "learn about", "in hindi", "in malayalam", 
                    "in tamil", "in telugu", "in kannada", "in spanish", "in french",
                    "translate", "convert to"
                ]
                
                if any(indicator in query_lower for indicator in wikipedia_indicators):
                    # Use enhanced Wikipedia search
                    return self.enhanced_wikipedia_search(query)
                
                # Fall back to original method if not a clear Wikipedia request
                return super().handle_wikipedia_requests(query)
        
        return EnhancedShankaraAssistant
    
    except ImportError as e:
        print(f"❌ Could not enhance assistant: {e}")
        print("Make sure both main1.py and wikipedia_translator.py are available.")
        return None
    except Exception as e:
        print(f"❌ Enhancement error: {e}")
        return None

def test_enhanced_assistant():
    """Test the enhanced assistant with various queries"""
    
    print("🧪 TESTING ENHANCED ASSISTANT")
    print("=" * 50)
    
    try:
        EnhancedAssistant = enhance_main_assistant()
        if not EnhancedAssistant:
            return
        
        # Create assistant instance
        assistant = EnhancedAssistant()
        
        # Test queries
        test_queries = [
            "Tell me about machine learning in Hindi",
            "What is quantum physics in Malayalam",
            "Explain photosynthesis in Tamil", 
            "Who was Albert Einstein in Spanish",
            "Search for meditation",
            "What is consciousness",
        ]
        
        print("\n🔄 Testing enhanced capabilities...")
        print("-" * 50)
        
        for i, query in enumerate(test_queries):
            print(f"\n📝 Test {i+1}: {query}")
            try:
                response = assistant.get_wisdom_response(query)
                print(f"🤖 Response: {response[:200]}...")
                print(f"🌐 Language: {assistant.current_response_language}")
            except Exception as e:
                print(f"❌ Error: {e}")
            print("-" * 30)
        
        print("\n✅ Enhanced assistant testing completed!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

def run_enhanced_assistant():
    """Run the enhanced assistant interactively"""
    
    print("🚀 ENHANCED ADI SHANKARA ASSISTANT")
    print("=" * 50)
    print("Now with powerful Wikipedia translation to any language!")
    print("=" * 50)
    
    try:
        EnhancedAssistant = enhance_main_assistant()
        if not EnhancedAssistant:
            return
        
        assistant = EnhancedAssistant()
        
        print("\n🎯 Ready! Try these examples:")
        print("• 'Tell me about artificial intelligence in Hindi'")
        print("• 'What is quantum computing in Malayalam'")
        print("• 'Explain meditation in Spanish'")
        print("• 'Who was Leonardo da Vinci in French'")
        print("\nType 'quit' to exit.")
        print("-" * 50)
        
        while True:
            try:
                query = input("\n🗣️ You: ").strip()
                
                if not query:
                    continue
                    
                if query.lower() in ['quit', 'exit', 'bye']:
                    print("\n🙏 It has been a pleasure sharing knowledge with you! Until we meet again in the pursuit of truth.")
                    break
                
                response = assistant.get_wisdom_response(query)
                print(f"\n🤖 Adi Shankara: {response}")
                
            except KeyboardInterrupt:
                print("\n\n🙏 Peace be with you, my friend! Our conversation was enlightening.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Runtime error: {e}")

def main():
    """Main function"""
    
    print("🌟 ENHANCED ADI SHANKARA ASSISTANT WITH WIKIPEDIA TRANSLATOR")
    print("=" * 70)
    print("Combining spiritual wisdom with global knowledge in any language!")
    print("=" * 70)
    
    print("\nChoose an option:")
    print("1. Test enhanced capabilities")
    print("2. Run interactive enhanced assistant")
    print("3. Both (test first, then interactive)")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            test_enhanced_assistant()
        elif choice == "2":
            run_enhanced_assistant()
        elif choice == "3":
            test_enhanced_assistant()
            print("\n" + "="*50)
            input("Press Enter to continue to interactive mode...")
            run_enhanced_assistant()
        else:
            print("Invalid choice. Running test mode...")
            test_enhanced_assistant()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
