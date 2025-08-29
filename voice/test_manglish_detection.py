#!/usr/bin/env python3
"""
Test script for Manglish detection in the Shankara Assistant
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main1 import NaturalShankaraAssistant

def test_manglish_detection():
    """Test the Manglish detection functionality"""
    print("🧪 Testing Manglish Detection System\n")
    
    # Initialize assistant
    assistant = NaturalShankaraAssistant()
    
    # Test cases
    test_inputs = [
        "sugamano",  # The problematic case
        "are you good",  # English that might be misclassified
        "namaste",
        "thangal aar",
        "enthanu parayunnathu",
        "tang Ganpati parivar",  # Your original problematic input
        "ningal evideya",
        "adi shankara about parayu",
        "hello how are you",  # English control
        "what is vedanta",  # English control
        "namaskaram guruji",
        "shankar acharya enthanu upadeshichu",
        "engane aan moksha labhikkan",
        "malayalam il parayu"
    ]
    
    print("Testing Manglish Detection:")
    print("=" * 50)
    
    for test_input in test_inputs:
        print(f"\n📝 Input: '{test_input}'")
        
        # Test contains_manglish
        has_manglish = assistant.contains_manglish(test_input)
        print(f"   🔍 Manglish detected: {has_manglish}")
        
        # Test detect_manglish_patterns
        has_patterns, patterns = assistant.detect_manglish_patterns(test_input)
        print(f"   🎯 Patterns found: {has_patterns}")
        if patterns:
            print(f"   📋 Pattern details: {patterns}")
        
        # Test language detection
        try:
            processed_text, detected_lang = assistant.detect_language_and_translate(test_input)
            print(f"   🌐 Detected language: {detected_lang}")
            print(f"   🔄 Processed text: '{processed_text}'")
        except Exception as e:
            print(f"   ⚠️ Language detection error: {e}")
        
        print("-" * 30)

def test_response_generation():
    """Test response generation for Manglish inputs"""
    print("\n\n🎭 Testing Response Generation\n")
    
    assistant = NaturalShankaraAssistant()
    
    manglish_inputs = [
        "namaste",
        "thangal aar",
        "tang pati parayu",
        "adi shankara enthanu upadeshichu"
    ]
    
    print("Testing Response Generation:")
    print("=" * 50)
    
    for test_input in manglish_inputs:
        print(f"\n📝 Input: '{test_input}'")
        
        try:
            response = assistant.respond_in_malayalam(test_input)
            if response:
                print(f"   🗨️ Malayalam Response: {response[:100]}...")
            else:
                print("   ❌ No Malayalam response generated")
        except Exception as e:
            print(f"   ⚠️ Response generation error: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_manglish_detection()
    test_response_generation()
    print("\n✅ Testing completed!")
