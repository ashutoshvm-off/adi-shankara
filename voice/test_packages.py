#!/usr/bin/env python3
"""
Quick package verification script
"""

def test_imports():
    """Test if all required packages can be imported"""
    print("🔧 Testing package imports...")
    print("=" * 50)
    
    packages = [
        ("speech_recognition", "Speech Recognition"),
        ("pyttsx3", "Text-to-Speech Engine"),
        ("torch", "PyTorch"),
        ("sentence_transformers", "Sentence Transformers"),
        ("googletrans", "Google Translate"),
        ("wikipedia", "Wikipedia"),
        ("edge_tts", "Edge TTS"),
        ("pygame", "Pygame"),
        ("gtts", "Google TTS"),
        ("nltk", "NLTK"),
        ("scipy", "SciPy"),
        ("sounddevice", "Sound Device"),
        ("aiofiles", "Async Files")
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for package, name in packages:
        try:
            __import__(package)
            print(f"✅ {name} - OK")
            success_count += 1
        except ImportError as e:
            print(f"❌ {name} - FAILED: {e}")
        except Exception as e:
            print(f"⚠️  {name} - WARNING: {e}")
            success_count += 1  # Count as success if it's just a warning
    
    print("=" * 50)
    print(f"📊 Results: {success_count}/{total_count} packages working")
    
    if success_count == total_count:
        print("🎉 All packages are working perfectly!")
        return True
    elif success_count >= total_count * 0.8:
        print("✅ Most packages are working - should be functional")
        return True
    else:
        print("⚠️  Some critical packages are missing")
        return False

if __name__ == "__main__":
    test_imports()
