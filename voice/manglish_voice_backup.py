#!/usr/bin/env python3
"""
Manglish Voice Backup System
Enhanced voice synthesis with fallback mechanisms for Manglish content
"""

import sys
import os
import tempfile
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

class ManglishVoiceBackup:
    """Enhanced voice backup system specifically for Manglish content"""
    
    def __init__(self):
        """Initialize the Manglish voice backup system"""
        self.voice_engines = []
        self.current_engine = None
        self.malayalam_voices = [
            'ml-IN-SobhanaNeural',  # Female Malayalam voice
            'ml-IN-MidhunNeural'    # Male Malayalam voice  
        ]
        self.english_indian_voices = [
            'en-IN-NeerjaNeural',   # Female Indian English
            'en-IN-PrabhatNeural'   # Male Indian English
        ]
        self.fallback_voices = [
            'en-US-AriaNeural',
            'en-US-GuyNeural'
        ]
        
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize available voice engines in order of preference"""
        
        # Engine 1: Edge TTS (Best quality for Indian languages)
        try:
            import edge_tts
            import asyncio
            self.voice_engines.append({
                'name': 'edge_tts',
                'module': edge_tts,
                'asyncio': asyncio,
                'available': True,
                'priority': 1
            })
            print("✅ Edge TTS initialized for Manglish backup")
        except ImportError:
            print("⚠️ Edge TTS not available")
        
        # Engine 2: Google TTS
        try:
            from gtts import gTTS
            self.voice_engines.append({
                'name': 'gtts', 
                'module': gTTS,
                'available': True,
                'priority': 2
            })
            print("✅ Google TTS initialized for Manglish backup")
        except ImportError:
            print("⚠️ Google TTS not available")
        
        # Engine 3: System TTS (Fallback)
        try:
            import pyttsx3
            self.voice_engines.append({
                'name': 'pyttsx3',
                'module': pyttsx3,
                'available': True,
                'priority': 3
            })
            print("✅ System TTS initialized for Manglish backup")
        except ImportError:
            print("⚠️ System TTS not available")
        
        # Sort engines by priority
        self.voice_engines.sort(key=lambda x: x['priority'])
        
        if self.voice_engines:
            self.current_engine = self.voice_engines[0]
            print(f"🎤 Primary voice engine: {self.current_engine['name']}")
        else:
            print("❌ No voice engines available!")
    
    def synthesize_manglish_voice(self, text, language_hint='malayalam'):
        """Synthesize voice for Manglish content with smart fallbacks"""
        
        if not text or not text.strip():
            return None
        
        # Try each engine in order of priority
        for engine in self.voice_engines:
            try:
                audio_file = self._synthesize_with_engine(text, engine, language_hint)
                if audio_file:
                    print(f"✅ Manglish voice synthesized with {engine['name']}")
                    return audio_file
            except Exception as e:
                logger.warning(f"Voice synthesis failed with {engine['name']}: {e}")
                continue
        
        print("❌ All voice engines failed for Manglish content")
        return None
    
    def _synthesize_with_engine(self, text, engine, language_hint):
        """Synthesize voice with a specific engine"""
        
        if engine['name'] == 'edge_tts':
            return self._edge_tts_synthesize(text, language_hint, engine)
        
        elif engine['name'] == 'gtts':
            return self._gtts_synthesize(text, language_hint, engine)
        
        elif engine['name'] == 'pyttsx3':
            return self._pyttsx3_synthesize(text, language_hint, engine)
        
        return None
    
    def _edge_tts_synthesize(self, text, language_hint, engine):
        """Synthesize using Edge TTS with Malayalam/Indian English voices"""
        try:
            import asyncio
            edge_tts = engine['module']
            
            # Choose voice based on language hint and content
            voice = self._select_best_voice_for_content(text, language_hint)
            
            async def generate_speech():
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_file.close()
                
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(temp_file.name)
                
                return temp_file.name
            
            # Run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_file = loop.run_until_complete(generate_speech())
            loop.close()
            
            return audio_file
            
        except Exception as e:
            logger.error(f"Edge TTS synthesis failed: {e}")
            return None
    
    def _gtts_synthesize(self, text, language_hint, engine):
        """Synthesize using Google TTS"""
        try:
            gTTS = engine['module']
            
            # Choose language for gTTS
            if language_hint == 'malayalam' and self._is_malayalam_heavy(text):
                lang = 'ml'
            else:
                lang = 'en'
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Google TTS synthesis failed: {e}")
            return None
    
    def _pyttsx3_synthesize(self, text, language_hint, engine):
        """Synthesize using system TTS (pyttsx3)"""
        try:
            pyttsx3 = engine['module']
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_file.close()
            
            tts_engine = pyttsx3.init()
            
            # Configure for Indian English if available
            voices = tts_engine.getProperty('voices')
            for voice in voices:
                if any(keyword in voice.name.lower() for keyword in ['indian', 'india', 'hindi']):
                    tts_engine.setProperty('voice', voice.id)
                    break
            
            # Slower speech rate for better clarity
            tts_engine.setProperty('rate', 150)
            
            tts_engine.save_to_file(text, temp_file.name)
            tts_engine.runAndWait()
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"System TTS synthesis failed: {e}")
            return None
    
    def _select_best_voice_for_content(self, text, language_hint):
        """Select the best voice based on content analysis"""
        
        # Analyze content for Malayalam vs English ratio
        if self._is_malayalam_heavy(text):
            # Use Malayalam voice for Malayalam-heavy content
            return self.malayalam_voices[0]  # Female Malayalam voice
        
        elif self._is_manglish_content(text):
            # Use Indian English for Manglish content
            return self.english_indian_voices[0]  # Female Indian English
        
        else:
            # Use standard English for pure English content
            return self.fallback_voices[0]  # Standard English
    
    def _is_malayalam_heavy(self, text):
        """Check if text is Malayalam-heavy"""
        malayalam_chars = sum(1 for char in text if '\u0D00' <= char <= '\u0D7F')
        total_chars = len([c for c in text if c.strip()])
        
        return total_chars > 0 and malayalam_chars / total_chars > 0.3
    
    def _is_manglish_content(self, text):
        """Check if content is Manglish (Malayalam-English mix)"""
        text_lower = text.lower()
        
        manglish_indicators = [
            'enik', 'njaan', 'ningal', 'enthaan', 'evide', 'epozhaan',
            'aanu', 'illa', 'und', 'seri', 'angane', 'athu kondaan'
        ]
        
        return any(indicator in text_lower for indicator in manglish_indicators)
    
    def cleanup_temp_file(self, file_path):
        """Clean up temporary audio files"""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
                print(f"🗑️ Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")

def integrate_manglish_backup_to_main():
    """Integration instructions for the main assistant"""
    
    integration_code = '''
# Add to main1.py NaturalShankaraAssistant class:

def __init__(self, qa_file="shankaracharya_qa.txt"):
    # ... existing initialization ...
    
    # Initialize Manglish voice backup
    try:
        from manglish_voice_backup import ManglishVoiceBackup
        self.manglish_voice = ManglishVoiceBackup()
        print("🥭 Manglish voice backup system initialized")
    except ImportError:
        self.manglish_voice = None
        print("⚠️ Manglish voice backup not available")

def speak_with_manglish_backup(self, text, language='malayalam'):
    """Enhanced speak function with Manglish backup"""
    
    # Try primary voice synthesis first
    success = self.speak_text(text, language)
    
    # If primary fails and we have Manglish content, use backup
    if not success and self.manglish_voice:
        print("🔄 Primary voice failed, using Manglish backup...")
        
        try:
            audio_file = self.manglish_voice.synthesize_manglish_voice(text, language)
            if audio_file:
                # Play the audio file
                success = self.play_audio_file(audio_file)
                # Cleanup
                self.manglish_voice.cleanup_temp_file(audio_file)
                return success
        except Exception as e:
            print(f"⚠️ Manglish backup also failed: {e}")
    
    return success

def play_audio_file(self, file_path):
    """Play audio file using available audio libraries"""
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        # Wait for playback to complete
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        
        return True
        
    except Exception as e:
        print(f"⚠️ Audio playback failed: {e}")
        return False
'''
    
    return integration_code

def main():
    """Test the Manglish voice backup system"""
    print("🥭 Manglish Voice Backup System")
    print("=" * 50)
    
    # Initialize the backup system
    voice_backup = ManglishVoiceBackup()
    
    # Test cases
    test_cases = [
        {
            'text': 'namaskaram, enik advaita patti ariyaan und',
            'language': 'malayalam',
            'description': 'Pure Manglish content'
        },
        {
            'text': 'ആദി ശങ്കരാചാര്യൻ അദ്വൈത വേദാന്തത്തിന്റെ പ്രവർത്തകനാണ്',
            'language': 'malayalam', 
            'description': 'Pure Malayalam script'
        },
        {
            'text': 'Advaita Vedanta is the philosophy of non-dualism taught by Adi Shankara',
            'language': 'english',
            'description': 'Pure English content'
        }
    ]
    
    print(f"\n🧪 Testing voice synthesis for different content types:")
    print("-" * 50)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Text: {test['text'][:50]}...")
        
        try:
            audio_file = voice_backup.synthesize_manglish_voice(
                test['text'], 
                test['language']
            )
            
            if audio_file:
                print(f"✅ Audio generated: {audio_file}")
                # In a real scenario, you would play the audio here
                voice_backup.cleanup_temp_file(audio_file)
            else:
                print("❌ Audio generation failed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Show integration instructions
    print(f"\n📋 Integration Instructions:")
    print("-" * 30)
    print("Copy this file to your voice directory and add the integration code to main1.py")
    
    integration = integrate_manglish_backup_to_main()
    print(f"\n💻 Integration Code Preview:")
    print(integration[:300] + "...")

if __name__ == "__main__":
    main()
