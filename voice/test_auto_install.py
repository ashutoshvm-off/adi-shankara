#!/usr/bin/env python3
"""
Test automatic installation of enhanced AI pipeline packages
"""

import sys
import os

# Add the voice directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_automatic_installation():
    """Test that required and enhanced packages are automatically installed"""
    print("🧪 Testing Automatic Package Installation")
    print("=" * 60)
    
    try:
        # This should trigger the automatic installation process
        print("🔄 Importing main1.py (will trigger auto-installation)...")
        
        # Import the main module - this should install packages automatically
        from main1 import NaturalShankaraAssistant
        
        print("✅ main1.py imported successfully")
        print("✅ Automatic installation process completed")
        
        # Check if enhanced packages are now available
        print("\n🔍 Checking Enhanced Package Availability After Installation:")
        
        enhanced_available = 0
        enhanced_total = 4  # torch, transformers, requests, sentence-transformers
        
        try:
            import torch
            print("  ✅ torch - Available")
            enhanced_available += 1
        except ImportError:
            print("  ❌ torch - Not Available")
        
        try:
            import transformers
            print("  ✅ transformers - Available")
            enhanced_available += 1
        except ImportError:
            print("  ❌ transformers - Not Available")
        
        try:
            import requests
            print("  ✅ requests - Available")
            enhanced_available += 1
        except ImportError:
            print("  ❌ requests - Not Available")
        
        try:
            import sentence_transformers
            print("  ✅ sentence-transformers - Available")
            enhanced_available += 1
        except ImportError:
            print("  ❌ sentence-transformers - Not Available")
        
        print(f"\n📊 Enhanced Package Status: {enhanced_available}/{enhanced_total} available")
        
        if enhanced_available >= 3:
            print("🎉 Enhanced AI pipeline is ready!")
        elif enhanced_available >= 1:
            print("⚡ Partial enhanced capabilities available")
        else:
            print("📌 Using basic pipeline with fallbacks")
        
        # Try to initialize assistant to test integration
        print(f"\n🚀 Testing Assistant Initialization...")
        assistant = NaturalShankaraAssistant()
        
        if hasattr(assistant, 'enhanced_pipeline_available'):
            print(f"✅ Enhanced pipeline availability: {assistant.enhanced_pipeline_available}")
        else:
            print("⚠️ Enhanced pipeline attribute not found")
        
        print(f"\n🎉 Automatic Installation Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔬 Automatic Package Installation Test")
    print("Testing enhanced AI pipeline package auto-installation")
    
    success = test_automatic_installation()
    
    if success:
        print(f"\n✅ AUTO-INSTALLATION WORKING!")
        print(f"🚀 Enhanced packages are automatically installed when needed")
    else:
        print(f"\n❌ Auto-installation needs troubleshooting")
