#!/usr/bin/env python3
"""
Test script to install and verify Coqui TTS after Visual C++ Build Tools installation
"""

import subprocess
import sys
import os

def test_coqui_installation():
    """Test if Coqui TTS can be installed and imported"""
    
    print("🔧 Testing Coqui TTS installation...")
    print("=" * 50)
    
    # Get the Python executable path
    python_exe = sys.executable
    print(f"Using Python: {python_exe}")
    
    try:
        # Try to install TTS
        print("\n📦 Installing Coqui TTS...")
        result = subprocess.run([
            python_exe, "-m", "pip", "install", "TTS", "torch", "torchaudio"
        ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        if result.returncode == 0:
            print("✅ Coqui TTS installation completed!")
        else:
            print("❌ Installation failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Installation timed out (took more than 10 minutes)")
        return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False
    
    # Test import
    try:
        print("\n🧪 Testing TTS import...")
        from TTS.api import TTS
        print("✅ TTS import successful!")
        
        # Test model loading
        print("\n🤖 Testing model loading...")
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
        print("✅ Model loading successful!")
        
        print("\n🎉 Coqui TTS is ready to use!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

if __name__ == "__main__":
    success = test_coqui_installation()
    if success:
        print("\n🚀 You can now use premium Coqui TTS voices!")
        print("Run your main voice assistant to enjoy high-quality speech synthesis.")
    else:
        print("\n⚠️  Coqui TTS installation failed.")
        print("Please check that Visual C++ Build Tools are properly installed.")
        print("You can still use Edge TTS and other voice engines.")
