#!/usr/bin/env python3
"""
Test script to verify Coqui TTS is disabled and other TTS models work
"""

import sys
import os

# Add the current directory to the path so we can import main1
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main1 import NaturalShankaraAssistant

def test_tts_models():
    """Test that Coqui TTS is disabled and other models work"""
    print("🧪 Testing TTS Configuration - Coqui TTS Should Be Disabled")
    print("=" * 65)
    
    # Initialize the assistant
    print("Initializing Adi Shankara assistant...")
    assistant = NaturalShankaraAssistant()
    
    # Check if Coqui TTS is properly disabled
    print(f"\n🔧 Coqui TTS Status: {'DISABLED ✅' if not hasattr(assistant, 'coqui_tts') or assistant.coqui_tts is None else 'ENABLED ❌'}")
    
    # Test voice hierarchy
    test_phrase = "Namaste! I am Adi Shankara. Testing voice without Coqui TTS."
    
    print("\n🎭 Testing TTS Model Hierarchy:")
    print("1. Coqui TTS: DISABLED (skipped)")
    print("2. Edge TTS: Should be tried first")
    print("3. Pyttsx3: Should be tried second")
    print("4. Google TTS: Should be tried as fallback")
    
    print(f"\n🗣️ Testing with phrase: \"{test_phrase}\"")
    print("Listen to confirm it uses Edge TTS, pyttsx3, or Google TTS (but NOT Coqui TTS)")
    
    try:
        assistant.speak_with_enhanced_quality(test_phrase, pause_before=0.5, pause_after=1.0)
        print("✅ Voice test completed successfully!")
    except Exception as e:
        print(f"❌ Voice test failed: {e}")
    
    # Show which TTS libraries are available
    print(f"\n📊 TTS Library Status:")
    try:
        from main1 import EDGE_TTS_AVAILABLE, PYTTSX3_AVAILABLE, GTTS_AVAILABLE, COQUI_TTS_AVAILABLE
        print(f"  • Edge TTS: {'Available ✅' if EDGE_TTS_AVAILABLE else 'Not Available ❌'}")
        print(f"  • Pyttsx3: {'Available ✅' if PYTTSX3_AVAILABLE else 'Not Available ❌'}")
        print(f"  • Google TTS: {'Available ✅' if GTTS_AVAILABLE else 'Not Available ❌'}")
        print(f"  • Coqui TTS: {'DISABLED ✅' if not COQUI_TTS_AVAILABLE else 'STILL ENABLED ❌'}")
    except ImportError as e:
        print(f"Could not check TTS status: {e}")
    
    print(f"\n🎯 Expected Behavior:")
    print("  • No Coqui TTS processing or loading")
    print("  • Faster startup (no Coqui model loading)")
    print("  • Voice uses Edge TTS (best), pyttsx3 (medium), or Google TTS (fallback)")
    print("  • Masculine voice selection still works")
    print("  • Sage-like delivery still works")

if __name__ == "__main__":
    try:
        test_tts_models()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
