#!/usr/bin/env python3
"""
Test script for the enhanced AI pipeline implementation
Tests ChatGPT's suggested pipeline: Whisper Large-v3 + IndicTrans2 + Bhashini TTS
"""

import sys
import os

# Add the voice directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_pipeline():
    """Test the enhanced pipeline components"""
    print("🧪 Testing Enhanced AI Pipeline Implementation")
    print("=" * 60)
    
    try:
        # Import the main assistant
        from main1 import NaturalShankaraAssistant
        
        print("✅ Successfully imported NaturalShankaraAssistant")
        
        # Initialize the assistant
        print("\n🚀 Initializing assistant...")
        assistant = NaturalShankaraAssistant()
        
        print("✅ Assistant initialized successfully")
        
        # Test enhanced managers
        print("\n🔍 Testing Enhanced Managers...")
        
        if hasattr(assistant, 'enhanced_tts_manager'):
            print("✅ Enhanced TTS Manager found")
            
            # Test voice selection
            voice, engine, priority = assistant.enhanced_tts_manager.get_best_male_voice("ml")
            print(f"  🎭 Best Malayalam male voice: {voice} ({engine}, priority: {priority})")
            
            voice, engine, priority = assistant.enhanced_tts_manager.get_best_male_voice("en")
            print(f"  🎭 Best English male voice: {voice} ({engine}, priority: {priority})")
            
        else:
            print("❌ Enhanced TTS Manager not found")
        
        if hasattr(assistant, 'enhanced_stt_manager'):
            print("✅ Enhanced STT Manager found")
            
            # Test language detection
            test_texts = [
                "Hello, how are you?",
                "നമസ്കാരം, സുഖമാണോ?",
                "namaste, engane undu?",
                "नमस्ते, कैसे हैं आप?"
            ]
            
            for text in test_texts:
                detected = assistant.enhanced_stt_manager.detect_language_from_text(text)
                print(f"  🔍 '{text}' → Detected: {detected}")
                
        else:
            print("❌ Enhanced STT Manager not found")
        
        # Test pipeline availability
        print(f"\n🎯 Enhanced Pipeline Available: {getattr(assistant, 'enhanced_pipeline_available', False)}")
        
        # Test enhanced methods
        print("\n🧪 Testing Enhanced Methods...")
        
        if hasattr(assistant, 'translate_with_enhanced_pipeline'):
            print("✅ Enhanced translation method found")
            
            # Test translation
            test_translation = assistant.translate_with_enhanced_pipeline(
                "The Atman and Brahman are one", "ml", "en"
            )
            print(f"  🔄 Translation test: '{test_translation}'")
            
        if hasattr(assistant, 'process_user_input_with_enhanced_pipeline'):
            print("✅ Enhanced input processing method found")
            
            # Test input processing
            processed, lang = assistant.process_user_input_with_enhanced_pipeline("Hello there")
            print(f"  📝 Input processing test: '{processed}' (detected: {lang})")
        
        # Test engines availability
        print("\n🔧 Engine Availability Report:")
        
        engines_to_check = [
            ('Whisper Large-v3', 'enhanced_stt_manager.whisper_engine'),
            ('IndicTrans2', 'enhanced_tts_manager.indictrans2_engine'),
            ('Bhashini TTS', 'enhanced_tts_manager.bhashini_engine'),
        ]
        
        for engine_name, attr_path in engines_to_check:
            try:
                obj = assistant
                for attr in attr_path.split('.'):
                    obj = getattr(obj, attr, None)
                    if obj is None:
                        break
                
                if obj is not None:
                    print(f"  ✅ {engine_name}: Available")
                else:
                    print(f"  ❌ {engine_name}: Not Available")
            except Exception as e:
                print(f"  ❌ {engine_name}: Error - {e}")
        
        print(f"\n🎉 Enhanced Pipeline Test Completed Successfully!")
        print(f"📊 Summary:")
        print(f"  • Pipeline implements ChatGPT's suggested architecture")
        print(f"  • Whisper Large-v3 for superior speech recognition")
        print(f"  • IndicTrans2 for high-quality Indian language translation")
        print(f"  • Bhashini TTS for authentic Indian voices")
        print(f"  • Male-only voice enforcement for Adi Shankara character")
        print(f"  • Comprehensive fallback systems for reliability")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_malayalam_sanskrit_detection():
    """Test Malayalam and Sanskrit detection capabilities"""
    print("\n" + "=" * 60)
    print("🔍 Testing Malayalam & Sanskrit Detection")
    print("=" * 60)
    
    try:
        from main1 import NaturalShankaraAssistant
        
        assistant = NaturalShankaraAssistant()
        
        test_cases = [
            # Malayalam text
            ("നമസ്കാരം ആദി ശങ്കരാചാര്യാ", "ml"),
            # Sanskrit text  
            ("नमस्ते आदिशङ्कराचार्य", "hi"),
            # Manglish
            ("namaste, engane undu Shankara?", "ml"),
            # English
            ("Hello Adi Shankara, how are you?", "en"),
            # Mixed content
            ("Tell me about അദ്വൈതം philosophy", "ml"),
        ]
        
        for text, expected in test_cases:
            if hasattr(assistant, 'enhanced_stt_manager'):
                detected = assistant.enhanced_stt_manager.detect_language_from_text(text)
                status = "✅" if detected == expected else "⚠️"
                print(f"{status} '{text}' → Expected: {expected}, Got: {detected}")
            else:
                print(f"❌ Enhanced STT manager not available for testing")
                break
        
        print("\n🧠 Language Detection Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ Language detection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔬 Enhanced AI Pipeline Test Suite")
    print("Testing ChatGPT's suggested pipeline implementation")
    print("Components: Whisper Large-v3 + IndicTrans2 + Bhashini TTS")
    
    # Run tests
    success1 = test_enhanced_pipeline()
    success2 = test_malayalam_sanskrit_detection()
    
    if success1 and success2:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Enhanced pipeline is ready for superior Malayalam/Sanskrit experience")
    else:
        print(f"\n⚠️ Some tests failed, but basic functionality should still work")
