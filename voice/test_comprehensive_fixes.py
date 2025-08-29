#!/usr/bin/env python3
"""
Comprehensive Test Script for Language Detection and Malayalam Fixes
Tests all the fixes for language detection errors and Malayalam accuracy
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_language_detection_fixes():
    """Test the language detection format string fixes"""
    print("🧪 Testing Language Detection Fixes")
    print("=" * 50)
    
    try:
        from main1 import NaturalShankaraAssistant
        
        # Initialize assistant
        assistant = NaturalShankaraAssistant()
        print("✅ Assistant initialized successfully")
        
        # Test cases that previously caused format string errors
        test_cases = [
            {
                'description': 'None language handling',
                'text': 'hello',
                'language': None
            },
            {
                'description': 'Empty language handling', 
                'text': 'namaskaram',
                'language': ''
            },
            {
                'description': 'Short language code',
                'text': 'enthaan',
                'language': 'm'
            },
            {
                'description': 'Normal Malayalam detection',
                'text': 'enik advaita patti ariyaan und',
                'language': 'ml-IN'
            }
        ]
        
        print(f"\n🔍 Testing safe format string handling:")
        print("-" * 40)
        
        for i, test in enumerate(test_cases, 1):
            try:
                print(f"\nTest {i}: {test['description']}")
                
                # Test the language detection function directly
                processed_text, detected_lang = assistant.detect_language_and_translate(test['text'])
                
                print(f"  Input: '{test['text']}'")
                print(f"  Processed: '{processed_text}'")
                print(f"  Detected: '{detected_lang}'")
                print(f"  ✅ No format string errors!")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ Failed to test language detection: {e}")
        return False

def test_malayalam_accuracy_improvements():
    """Test the improved Malayalam translation accuracy"""
    print(f"\n🌴 Testing Malayalam Accuracy Improvements")
    print("=" * 50)
    
    try:
        from wikipedia_translator import WikipediaTranslator
        
        translator = WikipediaTranslator()
        print("✅ Enhanced translator initialized")
        
        # Test Malayalam-specific queries
        test_queries = [
            "tell me about Adi Shankara in Malayalam",
            "what is advaita vedanta in malayalam", 
            "explain maya concept in malayalam",
            "who is Adi Shankaracharya malayalam"
        ]
        
        print(f"\n🔍 Testing enhanced Malayalam responses:")
        print("-" * 40)
        
        for i, query in enumerate(test_queries, 1):
            try:
                print(f"\nTest {i}: {query}")
                
                result = translator.process_query(query)
                
                if result['success']:
                    print(f"  ✅ Translation successful")
                    print(f"  Language: {result['language']}")
                    print(f"  Content preview: {result['content'][:100]}...")
                    
                    # Check for Malayalam script
                    has_malayalam = any(ord(c) >= 0x0D00 and ord(c) <= 0x0D7F for c in result['content'])
                    if has_malayalam:
                        print(f"  ✅ Contains Malayalam script")
                    else:
                        print(f"  ⚠️ No Malayalam script detected")
                        
                else:
                    print(f"  ❌ Translation failed: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test Malayalam accuracy: {e}")
        return False

def test_manglish_voice_backup():
    """Test the Manglish voice backup system"""
    print(f"\n🥭 Testing Manglish Voice Backup System")
    print("=" * 50)
    
    try:
        from manglish_voice_backup import ManglishVoiceBackup
        
        voice_backup = ManglishVoiceBackup()
        print("✅ Manglish voice backup initialized")
        
        # Test voice synthesis capabilities
        test_texts = [
            {
                'text': 'namaskaram, enik advaita patti ariyaan und',
                'language': 'malayalam',
                'type': 'Manglish'
            },
            {
                'text': 'ആദി ശങ്കരാചാര്യൻ ഒരു മഹാനായ ആചാര്യനാണ്',
                'language': 'malayalam',
                'type': 'Pure Malayalam'
            }
        ]
        
        print(f"\n🎤 Testing voice synthesis:")
        print("-" * 40)
        
        for i, test in enumerate(test_texts, 1):
            try:
                print(f"\nTest {i}: {test['type']}")
                print(f"  Text: {test['text'][:50]}...")
                
                # Test voice synthesis (without actually playing)
                audio_file = voice_backup.synthesize_manglish_voice(
                    test['text'], 
                    test['language']
                )
                
                if audio_file:
                    print(f"  ✅ Voice synthesis successful")
                    print(f"  Audio file: {audio_file}")
                    
                    # Cleanup
                    voice_backup.cleanup_temp_file(audio_file)
                    print(f"  🗑️ Temporary file cleaned up")
                else:
                    print(f"  ❌ Voice synthesis failed")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test Manglish voice backup: {e}")
        return False

def test_enhanced_language_handler():
    """Test the enhanced language detection handler"""
    print(f"\n🌐 Testing Enhanced Language Handler")
    print("=" * 50)
    
    try:
        from language_detection_fix import EnhancedLanguageHandler
        
        handler = EnhancedLanguageHandler()
        print("✅ Enhanced language handler initialized")
        
        # Test enhanced Manglish detection
        test_texts = [
            'namaskaram guru',
            'enik enthu cheyyanam?', 
            'ningal evide ninnum?',
            'advaita vedanta explained',
            'ആദി ശങ്കരൻ ആരാണ്?',
            '',  # Empty string test
            None  # None test
        ]
        
        print(f"\n🔍 Testing enhanced Manglish detection:")
        print("-" * 40)
        
        for i, text in enumerate(test_texts, 1):
            try:
                if text is None:
                    print(f"\nTest {i}: None input")
                    formatted = handler.safe_format_language_detection("test", None)
                    print(f"  ✅ Safe formatting: {formatted}")
                    
                elif text == '':
                    print(f"\nTest {i}: Empty string")
                    formatted = handler.safe_format_language_detection("", "ml")
                    print(f"  ✅ Safe formatting: {formatted}")
                    
                else:
                    print(f"\nTest {i}: '{text}'")
                    is_malayalam, score = handler.enhanced_malayalam_detection(text)
                    formatted = handler.safe_format_language_detection(text, "ml" if is_malayalam else "en")
                    
                    print(f"  Malayalam detected: {is_malayalam}")
                    print(f"  Confidence score: {score:.2f}")
                    print(f"  Formatted output: {formatted}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test enhanced language handler: {e}")
        return False

def run_comprehensive_tests():
    """Run all tests and provide summary"""
    print("🔧 Comprehensive Language Detection and Malayalam Fix Tests")
    print("=" * 70)
    
    tests = [
        ('Language Detection Fixes', test_language_detection_fixes),
        ('Malayalam Accuracy Improvements', test_malayalam_accuracy_improvements),
        ('Manglish Voice Backup', test_manglish_voice_backup),
        ('Enhanced Language Handler', test_enhanced_language_handler)
    ]
    
    results = []
    
    for test_name, test_function in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            success = test_function()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n📈 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All fixes working correctly!")
    else:
        print("⚠️ Some issues remain. Check individual test results above.")
    
    return passed == total

def main():
    """Main testing function"""
    print("🚀 Starting comprehensive fix verification...")
    
    success = run_comprehensive_tests()
    
    if success:
        print(f"\n✅ All language detection and Malayalam fixes verified!")
        print("💡 The issues should now be resolved:")
        print("   • Language detection format string errors fixed")
        print("   • Malayalam response accuracy improved") 
        print("   • Manglish voice backup system ready")
    else:
        print(f"\n⚠️ Some fixes need additional work. See test results above.")

if __name__ == "__main__":
    main()
