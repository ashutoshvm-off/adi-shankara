#!/usr/bin/env python3
"""
Enhanced Pipeline Integration for Adi Shankara Assistant
Implementing the ChatGPT-suggested pipeline: Whisper Large-v3 → IndicTrans2 → Bhashini-TTS

This module integrates the premium pipeline with existing fallbacks for maximum reliability.
"""

import os
import tempfile
import logging
from typing import Optional, Tuple, Dict, Any

class PremiumPipeline:
    """
    Premium AI Pipeline for Malayalam/Sanskrit Voice Assistant
    
    Pipeline Flow:
    1. Speech Input → Whisper Large-v3 (Auto language detection + transcription)
    2. Translation → IndicTrans2 (English ↔ Malayalam/Sanskrit)
    3. Voice Output → Bhashini-TTS (Authentic Indian voices)
    
    Fallbacks at each stage ensure reliability.
    """
    
    def __init__(self, existing_assistant):
        """Initialize with reference to existing assistant for fallbacks"""
        self.assistant = existing_assistant
        self.logger = logging.getLogger(__name__)
        
        # Premium engines (already implemented in your main1.py)
        self.whisper_engine = existing_assistant.whisper_engine if hasattr(existing_assistant, 'whisper_engine') else None
        self.indictrans2_engine = existing_assistant.indictrans2_engine if hasattr(existing_assistant, 'indictrans2_engine') else None
        self.bhashini_engine = existing_assistant.bhashini_engine if hasattr(existing_assistant, 'bhashini_engine') else None
        
        # Enhanced TTS manager for fallbacks
        self.enhanced_tts = existing_assistant.enhanced_tts if hasattr(existing_assistant, 'enhanced_tts') else None
        
        # Quality metrics for each engine
        self.engine_quality_scores = {
            'whisper_large_v3': 95,  # Best speech recognition
            'indictrans2': 90,       # Best Indian language translation
            'bhashini_tts': 95,      # Best Indian voice quality
            'edge_tts': 85,          # Good fallback voice
            'google_tts': 75,        # Standard fallback
            'pyttsx3': 60            # Basic fallback
        }
        
        # Language mappings for different engines
        self.language_mappings = {
            'whisper': {
                'malayalam': 'ml',
                'sanskrit': 'hi',  # Whisper doesn't have Sanskrit, use Hindi as closest
                'hindi': 'hi',
                'english': 'en'
            },
            'indictrans2': {
                'english_to_malayalam': 'en2ml',
                'english_to_sanskrit': 'en2hi',  # IndicTrans2 uses 'hi' for Sanskrit
                'malayalam_to_english': 'ml2en',
                'sanskrit_to_english': 'hi2en'
            },
            'bhashini': {
                'malayalam': 'ml',
                'sanskrit': 'sa',
                'hindi': 'hi',
                'english': 'en'
            }
        }
    
    def process_speech_input(self, audio_file_path: Optional[str] = None, 
                           language_hint: str = "auto") -> Tuple[str, str, Dict[str, Any]]:
        """
        Step 1: Process speech input with Whisper Large-v3
        
        Returns:
            (transcribed_text, detected_language, metadata)
        """
        metadata = {
            'engine_used': None,
            'confidence': 0.0,
            'processing_time': 0.0,
            'fallback_reason': None
        }
        
        # Priority 1: Whisper Large-v3 (Premium)
        if self.whisper_engine:
            try:
                import time
                start_time = time.time()
                
                text, detected_lang = self.whisper_engine.transcribe(audio_file_path)
                
                if text and text.strip():
                    processing_time = time.time() - start_time
                    metadata.update({
                        'engine_used': 'whisper_large_v3',
                        'confidence': 0.95,  # Whisper is very reliable
                        'processing_time': processing_time,
                        'quality_score': self.engine_quality_scores['whisper_large_v3']
                    })
                    
                    self.logger.info(f"✅ Whisper Large-v3 success: '{text}' ({detected_lang})")
                    return text.strip(), detected_lang, metadata
                    
            except Exception as e:
                metadata['fallback_reason'] = f"Whisper failed: {e}"
                self.logger.warning(f"⚠️ Whisper Large-v3 failed: {e}")
        
        # Fallback: Use existing STT from your assistant
        if hasattr(self.assistant, 'enhanced_stt') and self.assistant.enhanced_stt:
            try:
                text, lang = self.assistant.enhanced_stt.transcribe_audio(audio_file_path, language_hint)
                metadata.update({
                    'engine_used': 'enhanced_stt_fallback',
                    'confidence': 0.75,
                    'fallback_reason': metadata.get('fallback_reason', 'Premium engine unavailable')
                })
                return text, lang, metadata
            except Exception as e:
                self.logger.error(f"❌ STT fallback failed: {e}")
        
        # Last resort: Manual input
        text = input("🎤 Speech recognition unavailable. Please type your message: ").strip()
        detected_lang = self._detect_language_from_text(text)
        
        metadata.update({
            'engine_used': 'manual_input',
            'confidence': 1.0,
            'fallback_reason': 'All automatic speech recognition failed'
        })
        
        return text, detected_lang, metadata
    
    def process_translation(self, text: str, source_lang: str, 
                          target_lang: str) -> Tuple[str, Dict[str, Any]]:
        """
        Step 2: Process translation with IndicTrans2
        
        Returns:
            (translated_text, metadata)
        """
        metadata = {
            'engine_used': None,
            'quality_score': 0,
            'translation_direction': f"{source_lang}→{target_lang}",
            'fallback_reason': None
        }
        
        # Skip translation if source and target are the same
        if source_lang == target_lang:
            metadata.update({
                'engine_used': 'no_translation_needed',
                'quality_score': 100
            })
            return text, metadata
        
        # Priority 1: IndicTrans2 (Premium for Indian languages)
        if self.indictrans2_engine and self._is_indian_language_pair(source_lang, target_lang):
            try:
                if source_lang == 'en':
                    # English to Indian language
                    translated = self.indictrans2_engine.translate(text, target_lang)
                else:
                    # Indian language to English
                    translated = self.indictrans2_engine.reverse_translate(text, source_lang)
                
                if translated and translated.strip():
                    metadata.update({
                        'engine_used': 'indictrans2',
                        'quality_score': self.engine_quality_scores['indictrans2']
                    })
                    
                    self.logger.info(f"✅ IndicTrans2 translation success")
                    return translated.strip(), metadata
                    
            except Exception as e:
                metadata['fallback_reason'] = f"IndicTrans2 failed: {e}"
                self.logger.warning(f"⚠️ IndicTrans2 failed: {e}")
        
        # Fallback: Google Translate (from your existing implementation)
        try:
            from googletrans import Translator
            translator = Translator()
            
            # Map language codes for Google Translate
            google_source = self._map_to_google_lang_code(source_lang)
            google_target = self._map_to_google_lang_code(target_lang)
            
            result = translator.translate(text, src=google_source, dest=google_target)
            
            metadata.update({
                'engine_used': 'google_translate_fallback',
                'quality_score': 70,
                'fallback_reason': metadata.get('fallback_reason', 'Premium engine unavailable')
            })
            
            return result.text, metadata
            
        except Exception as e:
            self.logger.error(f"❌ Translation fallback failed: {e}")
            
        # Last resort: Return original text
        metadata.update({
            'engine_used': 'no_translation',
            'quality_score': 0,
            'fallback_reason': 'All translation engines failed'
        })
        
        return text, metadata
    
    def process_voice_output(self, text: str, language: str = "en", 
                           gender: str = "male") -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Step 3: Process voice output with Bhashini-TTS
        
        Returns:
            (audio_file_path, metadata)
        """
        metadata = {
            'engine_used': None,
            'quality_score': 0,
            'voice_language': language,
            'voice_gender': gender,
            'fallback_reason': None
        }
        
        # Priority 1: Bhashini-TTS (Premium for Indian languages)
        if self.bhashini_engine and self._is_indian_language(language):
            try:
                audio_file = self.bhashini_engine.synthesize(text, language, gender)
                
                if audio_file and os.path.exists(audio_file):
                    metadata.update({
                        'engine_used': 'bhashini_tts',
                        'quality_score': self.engine_quality_scores['bhashini_tts']
                    })
                    
                    self.logger.info(f"✅ Bhashini TTS success for {language}")
                    return audio_file, metadata
                    
            except Exception as e:
                metadata['fallback_reason'] = f"Bhashini TTS failed: {e}"
                self.logger.warning(f"⚠️ Bhashini TTS failed: {e}")
        
        # Fallback: Use existing enhanced TTS manager
        if self.enhanced_tts:
            try:
                audio_file = self.enhanced_tts.synthesize_speech(text, language)
                
                if audio_file:
                    metadata.update({
                        'engine_used': 'enhanced_tts_fallback',
                        'quality_score': 80,
                        'fallback_reason': metadata.get('fallback_reason', 'Premium engine unavailable')
                    })
                    return audio_file, metadata
                    
            except Exception as e:
                self.logger.error(f"❌ TTS fallback failed: {e}")
        
        metadata.update({
            'engine_used': 'tts_failed',
            'quality_score': 0,
            'fallback_reason': 'All TTS engines failed'
        })
        
        return None, metadata
    
    def full_pipeline_process(self, audio_input: Optional[str] = None, 
                            target_language: str = "ml", 
                            response_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete pipeline processing for voice interaction
        
        Args:
            audio_input: Path to audio file or None for microphone
            target_language: Target language for response (ml, hi, en, etc.)
            response_text: Pre-generated response text (if any)
            
        Returns:
            Complete interaction metadata and results
        """
        pipeline_result = {
            'speech_input': {},
            'translation': {},
            'voice_output': {},
            'overall_quality': 0,
            'processing_time': 0,
            'engines_used': []
        }
        
        import time
        total_start_time = time.time()
        
        try:
            # Step 1: Speech Input Processing
            if audio_input is not None or not response_text:
                user_text, detected_lang, stt_metadata = self.process_speech_input(audio_input)
                pipeline_result['speech_input'] = {
                    'text': user_text,
                    'detected_language': detected_lang,
                    'metadata': stt_metadata
                }
                pipeline_result['engines_used'].append(stt_metadata['engine_used'])
            else:
                # Skip speech input if response_text is provided
                user_text, detected_lang = "", "en"
                pipeline_result['speech_input'] = {'text': '', 'detected_language': 'en'}
            
            # Step 2: Generate response (using existing assistant logic)
            if not response_text:
                # Use your existing response generation
                response_text = self._generate_response(user_text, detected_lang)
            
            # Step 3: Translation (if needed)
            response_lang = target_language
            if response_lang != "en":
                translated_response, trans_metadata = self.process_translation(
                    response_text, "en", response_lang
                )
                pipeline_result['translation'] = {
                    'original': response_text,
                    'translated': translated_response,
                    'metadata': trans_metadata
                }
                pipeline_result['engines_used'].append(trans_metadata['engine_used'])
                response_text = translated_response
            
            # Step 4: Voice Output
            audio_file, tts_metadata = self.process_voice_output(response_text, response_lang)
            pipeline_result['voice_output'] = {
                'text': response_text,
                'audio_file': audio_file,
                'metadata': tts_metadata
            }
            pipeline_result['engines_used'].append(tts_metadata['engine_used'])
            
            # Calculate overall quality and timing
            total_time = time.time() - total_start_time
            pipeline_result['processing_time'] = total_time
            
            # Calculate weighted quality score
            quality_scores = []
            if 'metadata' in pipeline_result['speech_input']:
                quality_scores.append(pipeline_result['speech_input']['metadata'].get('quality_score', 0))
            if 'metadata' in pipeline_result['translation']:
                quality_scores.append(pipeline_result['translation']['metadata'].get('quality_score', 0))
            quality_scores.append(pipeline_result['voice_output']['metadata'].get('quality_score', 0))
            
            pipeline_result['overall_quality'] = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            self.logger.info(f"🎯 Pipeline complete: Quality {pipeline_result['overall_quality']:.1f}%, Time {total_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline processing failed: {e}")
            pipeline_result['error'] = str(e)
        
        return pipeline_result
    
    # Helper methods
    def _detect_language_from_text(self, text: str) -> str:
        """Detect language from text content"""
        # Use your existing language detection logic
        if hasattr(self.assistant, 'detect_language'):
            return self.assistant.detect_language(text)
        
        # Simple fallback detection
        malayalam_chars = sum(1 for char in text if '\u0d00' <= char <= '\u0d7f')
        devanagari_chars = sum(1 for char in text if '\u0900' <= char <= '\u097f')
        
        if malayalam_chars > len(text) * 0.3:
            return "ml"
        elif devanagari_chars > len(text) * 0.3:
            return "hi"
        else:
            return "en"
    
    def _is_indian_language(self, lang_code: str) -> bool:
        """Check if language is an Indian language"""
        indian_languages = ['ml', 'hi', 'ta', 'te', 'kn', 'gu', 'mr', 'bn', 'pa', 'or', 'as']
        return lang_code.lower() in indian_languages
    
    def _is_indian_language_pair(self, source: str, target: str) -> bool:
        """Check if this is an English ↔ Indian language translation"""
        return (source == 'en' and self._is_indian_language(target)) or \
               (target == 'en' and self._is_indian_language(source))
    
    def _map_to_google_lang_code(self, lang_code: str) -> str:
        """Map internal language codes to Google Translate codes"""
        mapping = {
            'ml': 'ml',      # Malayalam
            'hi': 'hi',      # Hindi (for Sanskrit too)
            'ta': 'ta',      # Tamil
            'te': 'te',      # Telugu
            'kn': 'kn',      # Kannada
            'en': 'en'       # English
        }
        return mapping.get(lang_code, 'en')
    
    def _generate_response(self, user_text: str, detected_lang: str) -> str:
        """Generate response using existing assistant logic"""
        if hasattr(self.assistant, 'get_response'):
            return self.assistant.get_response(user_text)
        else:
            # Fallback response
            return "I understand your question. Let me share some wisdom from the Advaita Vedanta tradition."


def integrate_premium_pipeline(existing_assistant):
    """
    Integration function to add premium pipeline to existing assistant
    
    Usage:
        premium_pipeline = integrate_premium_pipeline(your_assistant)
        result = premium_pipeline.full_pipeline_process(target_language="ml")
    """
    return PremiumPipeline(existing_assistant)


# Example usage and testing
if __name__ == "__main__":
    print("🚀 Premium Pipeline Integration for Adi Shankara Assistant")
    print("=" * 60)
    print()
    print("This module implements the ChatGPT-suggested pipeline:")
    print("  1. 🎤 Whisper Large-v3 → Speech Recognition & Language Detection")
    print("  2. 🔄 IndicTrans2 → High-quality Indian Language Translation") 
    print("  3. 🗣️ Bhashini-TTS → Authentic Indian Voice Synthesis")
    print()
    print("Integration Benefits:")
    print("  ✅ Best-in-class quality for Malayalam & Sanskrit")
    print("  ✅ Seamless fallbacks to your existing engines")
    print("  ✅ Preserves all current functionality")
    print("  ✅ Adds premium quality when available")
    print()
    print("To integrate with your main1.py:")
    print("  1. Import this module")
    print("  2. Call integrate_premium_pipeline(your_assistant)")
    print("  3. Use premium_pipeline.full_pipeline_process()")
    print()
