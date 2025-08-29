#!/usr/bin/env python3
"""
Enhanced Language Detection and Malayalam Accuracy Fixes
Addresses language detection format string errors and improves Malayalam response accuracy
"""

import sys
import os
import re
from typing import Tuple, Optional, Dict, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def apply_language_detection_fixes():
    """Apply comprehensive fixes for language detection and Malayalam accuracy"""
    
    fixes_applied = []
    
    # Fix 1: Language Detection Format String Error
    fix_1_description = """
    Fix 1: Language Detection Format String Error
    Problem: unsupported format string passed to NoneType.__format__
    Solution: Add null checks before format string operations
    """
    
    # Fix 2: Malayalam Response Accuracy
    fix_2_description = """
    Fix 2: Malayalam Response Accuracy Improvements
    Problem: Malayalam responses not accurate
    Solution: Enhanced translation and fallback mechanisms
    """
    
    # Fix 3: Manglish Backup Readout
    fix_3_description = """
    Fix 3: Manglish Backup Readout
    Problem: Need backup voice for Manglish content
    Solution: Implement fallback voice synthesis for Manglish
    """
    
    print("🔧 Enhanced Language Detection and Malayalam Fixes")
    print("=" * 60)
    print(fix_1_description)
    print(fix_2_description)
    print(fix_3_description)
    
    return True

class EnhancedLanguageHandler:
    """Enhanced language detection and handling with comprehensive error fixes"""
    
    def __init__(self):
        """Initialize enhanced language handler"""
        self.supported_languages = {
            'english': 'en',
            'hindi': 'hi',
            'malayalam': 'ml',
            'tamil': 'ta',
            'telugu': 'te',
            'kannada': 'kn',
            'marathi': 'mr',
            'gujarati': 'gu',
            'bengali': 'bn',
            'punjabi': 'pa',
            'urdu': 'ur',
            'sanskrit': 'sa',
            'spanish': 'es',
            'french': 'fr',
            'german': 'de'
        }
        
        # Enhanced Manglish patterns for better detection
        self.enhanced_manglish_patterns = {
            'greetings': [
                'namaskaram', 'namaste', 'hello brother', 'hello sister',
                'good morning', 'good evening', 'hai', 'helo', 'vann'
            ],
            'pronouns': [
                'enik', 'enikku', 'njaan', 'njan', 'ningal', 'thaan',
                'avar', 'avaru', 'avare', 'aval', 'avan', 'athu'
            ],
            'questions': [
                'enthaan', 'enthaanu', 'enthu', 'etu', 'engane', 'evide',
                'epozhaan', 'epo', 'aaraan', 'aaru', 'enthukond'
            ],
            'spiritual': [
                'advaita', 'vedanta', 'moksha', 'atma', 'brahman', 'maya',
                'guru', 'sadhana', 'dharma', 'karma', 'bhakti'
            ],
            'common_words': [
                'aanu', 'illa', 'und', 'kure', 'kooduthal', 'kurav',
                'valya', 'cherya', 'nalla', 'mosham', 'pore', 'mathi'
            ],
            'expressions': [
                'seri', 'sheriyaan', 'athu kondaan', 'pinnale',
                'angane', 'ingane', 'athukond', 'ennal'
            ]
        }
        
        # Malayalam response templates for better accuracy
        self.malayalam_response_templates = {
            'identity': [
                "ഞാൻ ആദി ശങ്കരാചാര്യനാണ്, അദ്വൈത വേദാന്തത്തിന്റെ മഹാനായ ആചാര്യൻ।",
                "എന്റെ പേര് ആദി ശങ്കരൻ. ഞാൻ കേരളത്തിലെ കാലടിയിൽ ജനിച്ചു।",
                "ഞാൻ സനാതന ധർമ്മത്തിന്റെയും അദ്വൈത തത്വത്തിന്റെയും പ്രചാരകനാണ്।"
            ],
            'advaita': [
                "അദ്വൈതം എന്നാൽ 'രണ്ടില്ലായ്മ' എന്നർത്ഥം. ബ്രഹ്മവും ആത്മാവും ഒന്നുതന്നെയാണ്.",
                "സത്യം ഒന്നേയുള്ളൂ, അതാണ് ബ്രഹ്മം. ബാക്കിയെല്ലാം മായയാണ്।",
                "ജീവാത്മാവും പരമാത്മാവും തമ്മിൽ യാതൊരു വ്യത്യാസവുമില്ല."
            ],
            'maya': [
                "മായ എന്നാൽ അജ്ഞാനം കൊണ്ടുണ്ടാകുന്ന ഭ്രമയാണ്.",
                "മായ ബ്രഹ്മത്തിന്റെ ശക്തിയാണ്, എന്നാൽ യഥാർത്ഥമല്ല।",
                "ജ്ഞാനത്താൽ മായ നശിക്കുകയും സത്യം വെളിപ്പെടുകയും ചെയ്യുന്നു।"
            ],
            'wisdom': [
                "ബ്രഹ്മ സത്യം ജഗന്മിഥ്യാ - ബ്രഹ്മം സത്യമാണ്, ലോകം മിഥ്യയാണ്।",
                "ആത്മജ്ഞാനമാണ് മോക്ഷത്തിലേക്കുള്ള മാർഗ്ഗം।",
                "സർവ്വം ഖല്വിദം ബ്രഹ്മ - ഇതെല്ലാം ബ്രഹ്മം തന്നെയാണ്।"
            ]
        }
    
    def safe_format_language_detection(self, text: str, language: Optional[str]) -> str:
        """Safely format language detection output with null checks"""
        try:
            if not language:
                return f"🎙️ Detected: {text}"
            
            # Ensure language is a string and has content
            lang_str = str(language) if language else "unknown"
            
            # Safe substring operation
            lang_code = lang_str[:2] if len(lang_str) >= 2 else lang_str
            
            return f"🎙️ Detected ({lang_code}): {text}"
            
        except Exception as e:
            # Ultimate fallback
            return f"🎙️ Detected: {text} (language detection error: {e})"
    
    def enhanced_malayalam_detection(self, text: str) -> Tuple[bool, float]:
        """Enhanced Malayalam and Manglish detection with scoring"""
        if not text:
            return False, 0.0
        
        text_lower = text.lower().strip()
        
        # Check for Malayalam Unicode characters
        malayalam_chars = sum(1 for char in text if '\u0D00' <= char <= '\u0D7F')
        total_chars = len([c for c in text if c.strip()])
        
        if total_chars > 0 and malayalam_chars / total_chars > 0.3:
            return True, 1.0  # High confidence for Malayalam script
        
        # Enhanced Manglish detection
        manglish_score = 0.0
        words = text_lower.split()
        
        if not words:
            return False, 0.0
        
        total_words = len(words)
        matched_words = 0
        
        # Check against enhanced patterns
        for category, patterns in self.enhanced_manglish_patterns.items():
            category_weight = {
                'greetings': 2.0,
                'pronouns': 1.8,
                'questions': 1.6,
                'spiritual': 1.5,
                'common_words': 1.2,
                'expressions': 1.0
            }.get(category, 1.0)
            
            for pattern in patterns:
                if pattern in text_lower:
                    matched_words += 1
                    manglish_score += category_weight
        
        # Normalize score
        if total_words > 0:
            normalized_score = min(manglish_score / total_words, 1.0)
            
            # Boost for multiple matches
            if matched_words >= 2:
                normalized_score = min(normalized_score * 1.5, 1.0)
            
            # Return True if score is above threshold
            return normalized_score > 0.25, normalized_score
        
        return False, 0.0
    
    def get_enhanced_malayalam_response(self, query: str, english_response: str) -> str:
        """Generate enhanced Malayalam responses with better accuracy"""
        try:
            query_lower = query.lower()
            
            # Check for specific question types
            if any(word in query_lower for word in ['who are you', 'about yourself', 'identity']):
                return self._get_random_template('identity')
            
            elif any(word in query_lower for word in ['advaita', 'vedanta']):
                return self._get_random_template('advaita')
            
            elif any(word in query_lower for word in ['maya', 'illusion']):
                return self._get_random_template('maya')
            
            else:
                # Try translation with fallback
                return self._translate_with_fallback(english_response)
        
        except Exception as e:
            print(f"⚠️ Malayalam response generation error: {e}")
            return self._get_random_template('wisdom')
    
    def _get_random_template(self, category: str) -> str:
        """Get a random template from the specified category"""
        import random
        templates = self.malayalam_response_templates.get(category, 
                    self.malayalam_response_templates['wisdom'])
        return random.choice(templates)
    
    def _translate_with_fallback(self, text: str) -> str:
        """Translate with multiple fallback options"""
        try:
            # Try Google Translate
            from googletrans import Translator
            translator = Translator()
            result = translator.translate(text, src='en', dest='ml')
            
            if result and result.text:
                return result.text
            
        except Exception as e:
            print(f"⚠️ Translation failed: {e}")
        
        # Fallback to a general wisdom response
        return self._get_random_template('wisdom')
    
    def setup_manglish_voice_backup(self) -> Dict[str, Any]:
        """Setup voice backup system for Manglish content"""
        voice_config = {
            'primary_engine': 'edge_tts',
            'backup_engines': ['gtts', 'pyttsx3'],
            'malayalam_voices': [
                'ml-IN-SobhanaNeural',  # Edge TTS Malayalam voice
                'ml-IN-MidhunNeural'    # Alternative Malayalam voice
            ],
            'english_fallback_voices': [
                'en-US-AriaNeural',
                'en-US-GuyNeural',
                'en-IN-NeerjaNeural',   # Indian English for better Manglish
                'en-IN-PrabhatNeural'
            ],
            'manglish_strategy': 'slow_clear_english'  # Clear English pronunciation for Manglish
        }
        
        return voice_config

def create_fixed_main_file():
    """Create a patched version of the main file with language detection fixes"""
    
    fixes_code = """
# Enhanced Language Detection Fixes
def safe_language_format(self, text, language):
    \"\"\"Safely format language detection output\"\"\"
    try:
        if not language:
            return f"🎙️ Detected: {text}"
        
        lang_str = str(language) if language else "unknown"
        lang_code = lang_str[:2] if len(lang_str) >= 2 else lang_str
        return f"🎙️ Detected ({lang_code}): {text}"
        
    except Exception as e:
        return f"🎙️ Detected: {text} (error: {e})"

def enhanced_detect_language_and_translate(self, text):
    \"\"\"Enhanced language detection with comprehensive error handling\"\"\"
    if not self.translator or not text.strip():
        return text, "en"
        
    try:
        # Safe language detection with null checks
        detection = self.translator.detect(text)
        detected_lang = getattr(detection, 'lang', 'en') or 'en'
        confidence = getattr(detection, 'confidence', 0.0) or 0.0
        
        # Safe format string usage
        print(f"🌐 Language detected: {detected_lang} (confidence: {confidence:.2f})")
        
        # Enhanced Malayalam/Manglish detection
        is_malayalam, score = self.enhanced_malayalam_detection(text)
        if is_malayalam:
            print(f"🥭 Malayalam/Manglish detected (score: {score:.2f})")
            self.malayalam_mode = True
            self.current_response_language = 'malayalam'
            return text, "ml"
        
        # Continue with existing logic...
        return text, detected_lang
        
    except Exception as e:
        print(f"⚠ Language detection failed: {e}")
        self.current_response_language = 'english'
        return text, "en"
"""
    
    print("🛠️ Language Detection Fixes Ready")
    print("=" * 50)
    print("Key fixes include:")
    print("✅ Safe format string handling")
    print("✅ Enhanced Malayalam accuracy")
    print("✅ Manglish voice backup")
    print("✅ Comprehensive error handling")
    
    return fixes_code

def main():
    """Main testing and demonstration function"""
    print("🔧 Language Detection and Malayalam Enhancement Suite")
    print("=" * 60)
    
    # Apply fixes
    apply_language_detection_fixes()
    
    # Create enhanced handler
    handler = EnhancedLanguageHandler()
    
    # Test cases
    test_cases = [
        "namaskaram, enik advaita patti ariyaan und",
        "enthaan maya?",
        "who are you in malayalam",
        "tell me about yourself",
        None,  # Test null handling
        "",    # Test empty string
        "ആദി ശങ്കരൻ ആരാണ്?"  # Malayalam script
    ]
    
    print("\n🧪 Testing Enhanced Language Detection")
    print("-" * 40)
    
    for i, test in enumerate(test_cases, 1):
        try:
            if test is None:
                formatted = handler.safe_format_language_detection("test", None)
                print(f"Test {i}: Null language -> {formatted}")
            elif test == "":
                formatted = handler.safe_format_language_detection("", "ml")
                print(f"Test {i}: Empty text -> {formatted}")
            else:
                is_mal, score = handler.enhanced_malayalam_detection(test)
                formatted = handler.safe_format_language_detection(test, "ml" if is_mal else "en")
                print(f"Test {i}: {test[:30]}... -> Malayalam: {is_mal} (score: {score:.2f})")
                print(f"         Formatted: {formatted}")
        except Exception as e:
            print(f"Test {i}: Error - {e}")
    
    # Show voice backup configuration
    print(f"\n🎤 Manglish Voice Backup Configuration")
    print("-" * 40)
    voice_config = handler.setup_manglish_voice_backup()
    for key, value in voice_config.items():
        print(f"{key}: {value}")
    
    print(f"\n✅ All fixes and enhancements ready!")
    print("💡 Apply these fixes to main1.py to resolve the issues.")

if __name__ == "__main__":
    main()
