#!/usr/bin/env python3
"""
Test Script for Premium Pipeline Integration
Tests each component of the ChatGPT-suggested pipeline individually and together
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# Add the voice directory to path so we can import from main1
voice_dir = Path(__file__).parent
sys.path.insert(0, str(voice_dir))

try:
    from main1 import *
    print("✅ Successfully imported from main1.py")
except ImportError as e:
    print(f"❌ Failed to import from main1.py: {e}")
    sys.exit(1)

class PremiumPipelineTester:
    """Test each component of the premium pipeline"""
    
    def __init__(self):
        self.results = {
            'whisper_test': False,
            'indictrans2_test': False,
            'bhashini_test': False,
            'pipeline_test': False
        }
    
    def test_whisper_engine(self):
        """Test Whisper Large-v3 speech recognition"""
        print("\n🎤 Testing Whisper Large-v3 Engine")
        print("=" * 50)
        
        try:
            whisper_engine = WhisperEngine()
            
            # Test if model can be initialized
            success = whisper_engine.initialize_model()
            
            if success:
                print("✅ Whisper Large-v3 model loaded successfully")
                print(f"   Device: {whisper_engine.device}")
                print(f"   Model: {whisper_engine.model_name}")
                
                # Test with sample text (we can't test audio without a file)
                print("   Note: Audio transcription test requires audio file")
                self.results['whisper_test'] = True
                return True
            else:
                print("❌ Whisper model failed to load")
                return False
                
        except Exception as e:
            print(f"❌ Whisper test failed: {e}")
            return False
    
    def test_indictrans2_engine(self):
        """Test IndicTrans2 translation engine"""
        print("\n🔄 Testing IndicTrans2 Translation Engine")
        print("=" * 50)
        
        try:
            translator = IndicTrans2Engine()
            
            # Test Malayalam translation
            test_texts = [
                ("Hello, how are you?", "ml"),
                ("What is the nature of reality?", "ml"),
                ("Peace and blessings", "ml")
            ]
            
            for text, target_lang in test_texts:
                print(f"\nTesting: '{text}' → {target_lang}")
                
                translated = translator.translate(text, target_lang)
                
                if translated:
                    print(f"✅ Translation: {translated}")
                else:
                    print("❌ Translation failed")
                    return False
            
            # Test reverse translation
            print(f"\nTesting reverse translation...")
            malayalam_text = "നമസ്കാരം"
            english_result = translator.reverse_translate(malayalam_text, "ml")
            
            if english_result:
                print(f"✅ Reverse translation: {malayalam_text} → {english_result}")
            else:
                print("⚠️ Reverse translation failed (using fallback)")
            
            self.results['indictrans2_test'] = True
            return True
            
        except Exception as e:
            print(f"❌ IndicTrans2 test failed: {e}")
            return False
    
    def test_bhashini_engine(self):
        """Test Bhashini TTS engine"""
        print("\n🗣️ Testing Bhashini TTS Engine")
        print("=" * 50)
        
        # Check for API credentials
        api_key = os.getenv("BHASHINI_API_KEY")
        user_id = os.getenv("BHASHINI_USER_ID")
        
        if not api_key or not user_id:
            print("⚠️ Bhashini API credentials not found")
            print("   Please set environment variables:")
            print("   - BHASHINI_API_KEY")
            print("   - BHASHINI_USER_ID")
            print("   Get credentials from: https://bhashini.gov.in/ulca")
            return False
        
        try:
            bhashini = BhashiniTTSEngine()
            
            # Test API initialization
            if bhashini.initialize_api(api_key, user_id):
                print("✅ Bhashini API credentials validated")
            else:
                print("❌ Bhashini API credentials invalid")
                return False
            
            # Test Malayalam synthesis
            test_texts = [
                ("നമസ്കാരം", "ml"),
                ("ആത്മാവിന്റെ സ്വഭാവം എന്താണ്?", "ml"),
                ("शान्ति", "hi")  # Sanskrit fallback
            ]
            
            for text, lang in test_texts:
                print(f"\nTesting TTS: '{text}' in {lang}")
                
                audio_file = bhashini.synthesize(text, lang, "male")
                
                if audio_file and os.path.exists(audio_file):
                    print(f"✅ Audio generated: {audio_file}")
                    print(f"   File size: {os.path.getsize(audio_file)} bytes")
                    
                    # Clean up test file
                    try:
                        os.unlink(audio_file)
                    except:
                        pass
                else:
                    print("❌ Audio generation failed")
                    return False
            
            self.results['bhashini_test'] = True
            return True
            
        except Exception as e:
            print(f"❌ Bhashini test failed: {e}")
            return False
    
    def test_enhanced_tts_fallbacks(self):
        """Test existing TTS fallbacks"""
        print("\n🔊 Testing Enhanced TTS Fallbacks")
        print("=" * 50)
        
        try:
            enhanced_tts = EnhancedTTSManager()
            
            # Test voice selection
            voice, engine, score = enhanced_tts.get_best_male_voice("ml")
            print(f"✅ Best Malayalam voice: {voice} via {engine} (score: {score})")
            
            voice, engine, score = enhanced_tts.get_best_male_voice("en")
            print(f"✅ Best English voice: {voice} via {engine} (score: {score})")
            
            # Test synthesis (without actually playing audio)
            test_text = "Testing voice synthesis capabilities"
            audio_file = enhanced_tts.synthesize_speech(test_text, "en")
            
            if audio_file:
                print(f"✅ TTS synthesis successful: {audio_file}")
                # Clean up
                try:
                    os.unlink(audio_file)
                except:
                    pass
            else:
                print("⚠️ TTS synthesis failed")
            
            return True
            
        except Exception as e:
            print(f"❌ Enhanced TTS test failed: {e}")
            return False
    
    def test_full_pipeline_integration(self):
        """Test the complete pipeline integration"""
        print("\n🚀 Testing Complete Pipeline Integration")
        print("=" * 50)
        
        try:
            # Import the premium pipeline
            from enhanced_pipeline_integration import integrate_premium_pipeline
            
            # Create a mock assistant (simplified version)
            class MockAssistant:
                def __init__(self):
                    self.whisper_engine = WhisperEngine() if TRANSFORMERS_AVAILABLE else None
                    self.indictrans2_engine = IndicTrans2Engine() if TRANSFORMERS_AVAILABLE else None
                    self.bhashini_engine = BhashiniTTSEngine()
                    self.enhanced_tts = EnhancedTTSManager()
                
                def get_response(self, text):
                    return "Namaste! In the Advaita tradition, we understand that all existence is one consciousness."
            
            # Create mock assistant and integrate premium pipeline
            mock_assistant = MockAssistant()
            premium_pipeline = integrate_premium_pipeline(mock_assistant)
            
            print("✅ Premium pipeline integration successful")
            
            # Test pipeline processing (text-only mode)
            response_text = "आत्मा ही ब्रह्म है। The Self is Brahman itself."
            
            result = premium_pipeline.full_pipeline_process(
                audio_input=None,  # Skip audio input for testing
                target_language="ml",
                response_text=response_text
            )
            
            print(f"\n📊 Pipeline Results:")
            print(f"   Overall Quality: {result['overall_quality']:.1f}%")
            print(f"   Processing Time: {result['processing_time']:.2f}s")
            print(f"   Engines Used: {', '.join(result['engines_used'])}")
            
            if result['voice_output']['audio_file']:
                print(f"   ✅ Audio file generated: {result['voice_output']['audio_file']}")
            else:
                print(f"   ⚠️ Audio generation failed")
            
            self.results['pipeline_test'] = True
            return True
            
        except Exception as e:
            print(f"❌ Pipeline integration test failed: {e}")
            return False
    
    def generate_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "=" * 60)
        print("🎯 PREMIUM PIPELINE TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(self.results.values())
        
        print(f"\nOverall Score: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
        
        print(f"\n📋 Component Test Results:")
        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        print(f"\n💡 Recommendations:")
        
        if self.results['whisper_test']:
            print("   ✅ Whisper Large-v3 is ready for superior speech recognition")
        else:
            print("   ⚠️ Install torch and transformers for Whisper support")
        
        if self.results['indictrans2_test']:
            print("   ✅ IndicTrans2 is ready for high-quality Indian language translation")
        else:
            print("   ⚠️ IndicTrans2 needs torch and transformers packages")
        
        if self.results['bhashini_test']:
            print("   ✅ Bhashini TTS is ready for authentic Indian voices")
        else:
            print("   ⚠️ Get Bhashini API credentials for premium Indian TTS")
        
        if self.results['pipeline_test']:
            print("   ✅ Premium pipeline integration is complete and working")
        else:
            print("   ⚠️ Pipeline integration needs debugging")
        
        print(f"\n🚀 Implementation Readiness:")
        if passed_tests >= 3:
            print("   🟢 READY: You can implement the premium pipeline now!")
            print("   🎯 Focus: Get any missing API credentials and you're set")
        elif passed_tests >= 2:
            print("   🟡 PARTIAL: Core components work, minor setup needed")
            print("   🎯 Focus: Complete package installation and API setup")
        else:
            print("   🔴 SETUP NEEDED: Install required packages and dependencies")
            print("   🎯 Focus: Follow installation guide in PREMIUM_PIPELINE_INTEGRATION_GUIDE.md")
        
        print(f"\n🔗 Next Steps:")
        print("   1. Address any failed components above")
        print("   2. Integrate premium pipeline calls in your main conversation loop")
        print("   3. Test with real voice interactions")
        print("   4. Monitor quality improvements")


def main():
    """Run all tests and generate report"""
    print("🧪 Premium Pipeline Component Testing")
    print("Testing the ChatGPT-suggested pipeline implementation")
    print("=" * 60)
    
    tester = PremiumPipelineTester()
    
    # Run all tests
    tester.test_whisper_engine()
    tester.test_indictrans2_engine()
    tester.test_bhashini_engine()
    tester.test_enhanced_tts_fallbacks()
    tester.test_full_pipeline_integration()
    
    # Generate final report
    tester.generate_report()


if __name__ == "__main__":
    main()
