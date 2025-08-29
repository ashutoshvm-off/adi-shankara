#!/usr/bin/env python3
"""
Test script for Sanskrit input/output functionality in the Adi Shankara Assistant
"""

from main1 import NaturalShankaraAssistant
import time

def test_sanskrit_functionality():
    """Test various Sanskrit input and output scenarios"""
    print("🕉️ Testing Sanskrit Support in Adi Shankara Assistant")
    print("=" * 60)
    
    # Initialize the assistant
    assistant = NaturalShankaraAssistant()
    
    print("\n1. Testing Sanskrit Language Request (English input)")
    test_queries = [
        "tell me about yourself in Sanskrit",
        "explain Advaita in Sanskrit",
        "what is Brahman in Sanskrit language",
        "speak in Sanskrit",
        "reply in Sanskrit"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("🔄 Processing...")
        response = assistant.get_wisdom_response(query)
        print(f"🕉️ Response: {response}")
        print("-" * 40)
        time.sleep(1)
    
    print("\n2. Testing Sanskrit Script Input (Devanagari)")
    sanskrit_queries = [
        "नमस्ते",  # Namaste
        "कः त्वम्?",  # Who are you?
        "अद्वैतं किम्?",  # What is Advaita?
        "ब्रह्म सत्यम्",  # Brahman is truth
        "आत्मा ब्रह्म",  # Atman is Brahman
    ]
    
    for query in sanskrit_queries:
        print(f"\n📝 Sanskrit Query: {query}")
        print("🔄 Processing...")
        try:
            response = assistant.get_wisdom_response(query)
            print(f"🕉️ Response: {response}")
        except Exception as e:
            print(f"⚠️ Error: {e}")
        print("-" * 40)
        time.sleep(1)
    
    print("\n3. Testing Mixed Language Conversation")
    mixed_queries = [
        "Who are you?",
        "in Sanskrit please",
        "what is maya?",
        "explain in Sanskrit",
        "switch to English",
        "tell me about consciousness"
    ]
    
    for query in mixed_queries:
        print(f"\n📝 Mixed Query: {query}")
        print("🔄 Processing...")
        response = assistant.get_wisdom_response(query)
        print(f"💬 Response: {response}")
        print("-" * 40)
        time.sleep(1)
    
    print("\n4. Testing Sanskrit Philosophical Terms")
    term_queries = [
        "explain the mahavakyas in Sanskrit",
        "what is Om in Sanskrit",
        "describe moksha in Sanskrit",
        "tell me about consciousness in Sanskrit terms"
    ]
    
    for query in term_queries:
        print(f"\n📝 Term Query: {query}")
        print("🔄 Processing...")
        response = assistant.get_wisdom_response(query)
        print(f"🕉️ Response: {response}")
        print("-" * 40)
        time.sleep(1)
    
    print("\n✅ Sanskrit functionality testing completed!")
    print("🕉️ Sanskrit support includes:")
    print("   • Detection of Sanskrit script (Devanagari)")
    print("   • Translation from Sanskrit to English for processing")
    print("   • Enhanced responses with Sanskrit terms and explanations")
    print("   • Sanskrit mode activation via voice commands")
    print("   • Philosophical term explanations in Sanskrit")
    print("   • Sanskrit-Malayalam-English terminology mapping")

def quick_test():
    """Quick test of basic Sanskrit functionality"""
    print("🚀 Quick Sanskrit Test")
    print("=" * 30)
    
    assistant = NaturalShankaraAssistant()
    
    # Test basic Sanskrit request
    print("\n📝 Testing: 'Who are you in Sanskrit?'")
    response = assistant.get_wisdom_response("Who are you in Sanskrit?")
    print(f"🕉️ Response: {response}")
    
    # Test Sanskrit script
    print("\n📝 Testing Sanskrit script: 'नमस्ते'")
    response = assistant.get_wisdom_response("नमस्ते")
    print(f"🕉️ Response: {response}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        test_sanskrit_functionality()
