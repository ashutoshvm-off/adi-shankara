#!/usr/bin/env python3
"""
Specific test for IndicTrans2 translation functionality
"""

import sys
import os

# Add the voice directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_indictrans2_translation():
    """Test IndicTrans2 translation with trust_remote_code=True"""
    print("🧪 Testing IndicTrans2 Translation Engine")
    print("=" * 50)
    
    try:
        # Import the assistant
        from main1 import NaturalShankaraAssistant
        
        print("✅ Assistant imported successfully")
        
        # Initialize assistant
        assistant = NaturalShankaraAssistant()
        print("✅ Assistant initialized")
        
        # Check if enhanced pipeline is available
        if hasattr(assistant, 'enhanced_tts_manager') and assistant.enhanced_tts_manager.indictrans2_engine:
            print("✅ IndicTrans2 engine found")
            
            # Test translations
            test_cases = [
                ("Hello, how are you?", "ml", "English to Malayalam"),
                ("I am fine, thank you", "hi", "English to Hindi"),
                ("What is the meaning of life?", "ta", "English to Tamil"),
                ("The soul and Brahman are one", "ml", "Philosophical concept to Malayalam"),
                ("Knowledge is power", "hi", "English to Hindi")
            ]
            
            print(f"\n🔄 Testing {len(test_cases)} translation cases...")
            
            successful_translations = 0
            failed_translations = 0
            
            for text, target_lang, description in test_cases:
                print(f"\n📝 Test: {description}")
                print(f"   Input: '{text}'")
                print(f"   Target: {target_lang}")
                
                try:
                    translated = assistant.enhanced_tts_manager.indictrans2_engine.translate(text, target_lang)
                    
                    if translated and translated.strip() and translated != text:
                        print(f"   ✅ Output: '{translated}'")
                        successful_translations += 1
                    else:
                        print(f"   ⚠️ Output: '{translated}' (empty or unchanged)")
                        failed_translations += 1
                        
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    failed_translations += 1
            
            print(f"\n📊 Translation Test Summary:")
            print(f"   ✅ Successful: {successful_translations}/{len(test_cases)}")
            print(f"   ❌ Failed: {failed_translations}/{len(test_cases)}")
            
            if successful_translations > 0:
                print(f"   🎉 IndicTrans2 is working!")
                return True
            else:
                print(f"   ⚠️ IndicTrans2 needs troubleshooting")
                return False
                
        else:
            print("❌ IndicTrans2 engine not available")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_translation():
    """Test fallback translation with Google Translate"""
    print("\n" + "=" * 50)
    print("🔄 Testing Fallback Translation (Google Translate)")
    print("=" * 50)
    
    try:
        from main1 import NaturalShankaraAssistant
        
        assistant = NaturalShankaraAssistant()
        
        # Test enhanced translation method which includes fallbacks
        test_text = "The eternal consciousness is one with all beings"
        target_lang = "ml"
        
        print(f"📝 Testing enhanced translation pipeline...")
        print(f"   Input: '{test_text}'")
        print(f"   Target: {target_lang}")
        
        if hasattr(assistant, 'translate_with_enhanced_pipeline'):
            translated = assistant.translate_with_enhanced_pipeline(test_text, target_lang, "en")
            print(f"   ✅ Output: '{translated}'")
            return True
        else:
            print("❌ Enhanced translation method not found")
            return False
            
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔬 IndicTrans2 Translation Test Suite")
    print("Testing enhanced translation pipeline with trust_remote_code=True")
    
    # Run tests
    success1 = test_indictrans2_translation()
    success2 = test_fallback_translation()
    
    if success1:
        print(f"\n🎉 IndicTrans2 WORKING SUCCESSFULLY!")
        print(f"✅ Enhanced translation pipeline is operational")
    elif success2:
        print(f"\n⚠️ IndicTrans2 not working, but fallback translation is operational")
        print(f"✅ Translation functionality is available via Google Translate")
    else:
        print(f"\n❌ Translation functionality needs troubleshooting")
