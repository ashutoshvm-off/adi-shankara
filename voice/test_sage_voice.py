

#!/usr/bin/env python3
"""
Test script to verify the Adi Shankara voice assistant sounds like a male sage
"""

import sys
import os

# Add the current directory to the path so we can import main1
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main1 import NaturalShankaraAssistant

def test_sage_voice():
    """Test the voice configuration for Adi Shankara"""
    print("🧪 Testing Adi Shankara's Sage Voice Configuration")
    print("=" * 60)
    
    # Initialize the assistant
    print("Initializing Adi Shankara assistant...")
    assistant = NaturalShankaraAssistant()
    
    # Test sentences that should sound wise and contemplative
    test_phrases = [
        "I am Adi Shankara, and I teach the truth of Advaita Vedanta.",
        "The Self that you truly are is the same consciousness that appears as all existence.",
        "Through understanding maya, one transcends the illusion of separateness and realizes Brahman.",
        "My dear friend, moksha is not something to be achieved, but your very nature to be recognized.",
        "In the depths of meditation, the seeker discovers that the sought and the seeker are one."
    ]
    
    print("\n🎭 Testing sage-like voice delivery...")
    print("Listen carefully to ensure the voice sounds masculine, wise, and contemplative.\n")
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"Test {i}/5: Testing philosophical delivery...")
        print(f"Speaking: \"{phrase[:50]}...\"")
        
        try:
            # Test the enhanced speech function
            assistant.speak_with_enhanced_quality(phrase, pause_before=0.5, pause_after=1.0)
            
            input("Press Enter to continue to next test...")
            
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user.")
            break
        except Exception as e:
            print(f"❌ Error during test {i}: {e}")
            continue
    
    print("\n✅ Voice testing complete!")
    print("\nExpected characteristics:")
    print("  • Masculine, mature male voice")
    print("  • Slower, contemplative speech rate")
    print("  • Clear pronunciation of Sanskrit terms")
    print("  • Thoughtful pauses between concepts")
    print("  • Authoritative but gentle tone")
    
    # Test the text enhancement function
    print("\n🔧 Testing text enhancement for speech...")
    sample_text = "The ultimate truth is that Atman and Brahman are one. This is the essence of Advaita Vedanta, my dear friend."
    enhanced = assistant.enhance_text_for_speech(sample_text)
    print(f"Original: {sample_text}")
    print(f"Enhanced: {enhanced}")

if __name__ == "__main__":
    try:
        test_sage_voice()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
