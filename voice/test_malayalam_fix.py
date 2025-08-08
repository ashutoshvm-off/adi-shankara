#!/usr/bin/env python3
"""
Test script for the fixed Malayalam translation functionality
"""

import sys
import os

# Add the current directory to the path so we can import main1
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main1 import NaturalShankaraAssistant

def test_malayalam_translation_fix():
    """Test the fixed Malayalam translation functionality"""
    print("🧪 Testing Fixed Malayalam Translation")
    print("=" * 60)
    
    # Initialize the assistant
    try:
        assistant = NaturalShankaraAssistant()
        print("✅ Assistant initialized successfully")
        print(f"📚 Loaded {len(assistant.qa_pairs)} Q&A pairs from knowledge base")
    except Exception as e:
        print(f"❌ Failed to initialize assistant: {e}")
        return
    
    # Test specific cases that were failing
    test_cases = [
        {
            "description": "Identity question with Malayalam request",
            "query": "tell me about yourself in malayalam",
            "expected_language": "malayalam"
        },
        {
            "description": "Direct Malayalam identity question",
            "query": "who are you malayalam",
            "expected_language": "malayalam"
        },
        {
            "description": "Advaita question in Malayalam", 
            "query": "what is advaita vedanta in malayalam",
            "expected_language": "malayalam"
        },
        {
            "description": "Maya concept in Malayalam",
            "query": "explain maya in malayalam",
            "expected_language": "malayalam"
        },
        {
            "description": "Birth/origin in Malayalam",
            "query": "where were you born in malayalam",
            "expected_language": "malayalam"
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test {i}/{total_tests}: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        print("-" * 50)
        
        try:
            # Reset Malayalam mode for each test
            assistant.malayalam_mode = False
            
            # Get response
            response = assistant.get_wisdom_response(test_case['query'])
            
            if response:
                print(f"✅ Response received ({len(response)} characters)")
                print(f"🔤 Sample: {response[:200]}...")
                
                # Check if response contains Malayalam script
                if any(ord(char) >= 0x0D00 and ord(char) <= 0x0D7F for char in response):
                    print("✅ Contains Malayalam script")
                    successful_tests += 1
                else:
                    print("❌ No Malayalam script found")
                    print(f"Full response: {response}")
                
                print(f"🌐 Malayalam mode active: {assistant.malayalam_mode}")
                
            else:
                print("❌ No response received")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 50)
    
    # Test continuous Malayalam conversation
    print(f"\n🔄 Testing continuous Malayalam conversation...")
    print("-" * 50)
    
    try:
        # Activate Malayalam mode first
        assistant.malayalam_mode = True
        
        follow_up_questions = [
            "what is moksha?",
            "tell me about brahman",
            "where did you travel?"
        ]
        
        for i, question in enumerate(follow_up_questions, 1):
            print(f"\nFollow-up {i}: '{question}'")
            response = assistant.get_wisdom_response(question)
            
            if response and any(ord(char) >= 0x0D00 and ord(char) <= 0x0D7F for char in response):
                print(f"✅ Malayalam response: {response[:100]}...")
                successful_tests += 0.5  # Partial credit for follow-ups
            else:
                print(f"❌ Non-Malayalam response: {response[:100]}...")
    
    except Exception as e:
        print(f"❌ Continuous conversation error: {e}")
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"✅ Successful: {successful_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - successful_tests}/{total_tests}")
    print(f"📈 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests >= total_tests * 0.8:
        print("🎉 Malayalam translation fix is working well!")
    else:
        print("⚠️ Malayalam translation still needs improvement")

def test_json_knowledge_base():
    """Test that the JSON knowledge base is working"""
    print("\n🗂️ Testing JSON Knowledge Base")
    print("=" * 40)
    
    try:
        assistant = NaturalShankaraAssistant()
        
        # Test that we have Q&A pairs loaded
        if assistant.qa_pairs:
            print(f"✅ Loaded {len(assistant.qa_pairs)} Q&A pairs from JSON")
            
            # Show a sample
            for i, (question, answer) in enumerate(assistant.qa_pairs[:3]):
                print(f"\n📝 Sample {i+1}:")
                print(f"Q: {question}")
                print(f"A: {answer[:100]}...")
        else:
            print("❌ No Q&A pairs loaded")
            
    except Exception as e:
        print(f"❌ JSON knowledge base error: {e}")

def test_human_like_interaction():
    """Test that the model responds naturally and only to questions asked"""
    print("\n🤖 Testing Human-like Interaction")
    print("=" * 40)
    
    try:
        assistant = NaturalShankaraAssistant()
        
        # Test questions that should get specific answers
        specific_tests = [
            ("Who are you?", "identity"),
            ("What is Advaita Vedanta?", "philosophy"),
            ("Where were you born?", "birthplace"),
            ("What is maya?", "maya concept")
        ]
        
        for question, expected_topic in specific_tests:
            print(f"\n❓ Question: {question}")
            response = assistant.get_wisdom_response(question)
            print(f"💬 Response: {response[:150]}...")
            
            # Check if response is relevant to the topic
            if expected_topic.lower() in response.lower():
                print(f"✅ Response contains expected topic: {expected_topic}")
            else:
                print(f"⚠️ Response may not address the specific question about {expected_topic}")
    
    except Exception as e:
        print(f"❌ Human-like interaction test error: {e}")

if __name__ == "__main__":
    try:
        test_json_knowledge_base()
        test_malayalam_translation_fix()
        test_human_like_interaction()
        
        print("\n" + "="*60)
        print("🏁 All tests completed!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
