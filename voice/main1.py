import subprocess
import sys
import os
import zipfile
import urllib.request
import json
import logging
import re
import string
import time
import threading
import random
import datetime

# Add missing imports for all used modules/classes/functions
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    from googletrans import Translator  # type: ignore
except (ImportError, ModuleNotFoundError, Exception):
    Translator = None  # type: ignore

try:
    from sentence_transformers import SentenceTransformer, util  # type: ignore
except ImportError:
    SentenceTransformer = None  # type: ignore
    util = None  # type: ignore

try:
    from difflib import SequenceMatcher
except ImportError:
    SequenceMatcher = None

try:
    import tempfile
except ImportError:
    tempfile = None  # type: ignore

try:
    import pygame  # type: ignore
except ImportError:
    pygame = None  # type: ignore

try:
    import edge_tts  # type: ignore
except ImportError:
    edge_tts = None  # type: ignore

try:
    import asyncio
except ImportError:
    asyncio = None  # type: ignore

try:
    from gtts import gTTS  # type: ignore
except ImportError:
    gTTS = None  # type: ignore

try:
    import wikipedia 
except ImportError:
    wikipedia = None  # type: ignore

try:
    import torch  # type: ignore
    from TTS.api import TTS as CoquiTTS  # type: ignore
    COQUI_TTS_IMPORT_SUCCESS = True
    print("✓ Coqui TTS imported successfully")
except ImportError as e:
    torch = None  # type: ignore
    CoquiTTS = None  # type: ignore
    COQUI_TTS_IMPORT_SUCCESS = False
    print(f"⚠ Coqui TTS not available: {e}")
    print("  Voice will work with other TTS engines.")

try:
    import nltk  # type: ignore
    from nltk.corpus import stopwords  # type: ignore
    from nltk.stem import PorterStemmer  # type: ignore
    from nltk.tokenize import word_tokenize  # type: ignore
except ImportError:
    nltk = None  # type: ignore
    stopwords = None  # type: ignore
    PorterStemmer = None  # type: ignore
    word_tokenize = None  # type: ignore

# Set up logging for better debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Auto-install required packages ===
required = {
    "speech_recognition": "SpeechRecognition",
    "pyaudio": "pyaudio",  # Required for microphone input with SpeechRecognition
    "pyttsx3": "pyttsx3",
    "googletrans": "googletrans==4.0.0rc1",
    "gtts": "gTTS",
    "pygame": "pygame",
    "nltk": "nltk",
    "edge-tts": "edge-tts",
    "wikipedia": "wikipedia"
    # Note: TTS (Coqui) removed from auto-install due to long installation time and build requirements
    # Install manually with: pip install TTS (requires Visual C++ Build Tools)
    # Note: torch, sentence-transformers, sounddevice, scipy, aiofiles are optional
}

def check_package_status():
    """Quick check of package availability without installation"""
    print("🔍 Quick Package Status Check:")
    available = []
    missing = []
    
    for module, package in required.items():
        try:
            __import__(module)
            available.append(module)
        except ImportError:
            missing.append((module, package))
    
    total = len(required)
    print(f"  ✅ Available: {len(available)}/{total} ({', '.join(available) if available else 'None'})")
    if missing:
        print(f"  ❌ Missing: {len(missing)}/{total} ({', '.join([m[0] for m in missing])})")
    else:
        print("  🎉 All packages are available!")
    print()
    return len(missing) == 0

def install_packages():
    """Install required packages with better error handling and fast checking"""
    print("📦 Checking required packages...")
    installed_count = 0
    missing_count = 0
    failed_count = 0
    
    # Fast check first - just try importing without detailed diagnostics
    missing_packages = []
    
    for module, package in required.items():
        try:
            __import__(module)
            print(f"✓ {module} - Already installed")
            logger.info(f"Package {module} already installed")
            installed_count += 1
        except ImportError:
            print(f"⚠ {module} - Missing")
            missing_packages.append((module, package))
    
    # Show status after quick check
    total_packages = len(required)
    print(f"\n📊 Quick Package Status:")
    print(f"  ✓ Available: {installed_count}/{total_packages}")
    if missing_packages:
        print(f"  ⚠ Missing: {len(missing_packages)}/{total_packages}")
        
        # Ask user if they want to install missing packages
        print(f"\n🔧 Found {len(missing_packages)} missing packages:")
        for module, package in missing_packages:
            print(f"   • {module} ({package})")
        
        print("\n⚡ Installing missing packages automatically...")
        
        # Install missing packages
        for module, package in missing_packages:
            print(f"📥 Installing {package}...")
            try:
                logger.info(f"Installing missing package: {package}")
                result = subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    timeout=120
                )
                print(f"✓ {package} - Successfully installed")
                logger.info(f"Successfully installed {package}")
                installed_count += 1
            except subprocess.TimeoutExpired:
                logger.error(f"Installation of {package} timed out (2 minutes)")
                print(f"❌ {package} - Installation timed out (2 minutes)")
                failed_count += 1
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {package}: {e}")
                print(f"❌ {package} - Installation failed: {e}")
                failed_count += 1
            except Exception as e:
                logger.error(f"Unexpected error installing {package}: {e}")
                print(f"❌ {package} - Unexpected installation error: {e}")
                failed_count += 1
    
    # Final summary
    print(f"\n📊 Final Package Status:")
    print(f"  ✓ Successfully Available: {installed_count}/{total_packages}")
    if failed_count > 0:
        print(f"  ❌ Failed to Install: {failed_count}/{total_packages}")
        print(f"     Note: App will work with available packages")
    print()

def install_coqui_tts_optional():
    """Try to install Coqui TTS separately with user confirmation"""
    try:
        # import TTS
        return True
    except ImportError:
        pass
    
    print("🎤 Coqui TTS not found. This provides high-quality voice synthesis.")
    print("⚠ Warning: Installation requires Visual C++ Build Tools and takes 5-10 minutes.")
    
    # For now, skip automatic installation to avoid hanging
    print("📝 To install manually, run: pip install TTS")
    print("💡 The app will work with other TTS engines (Edge TTS, Google TTS, pyttsx3)")
    return False

# Install packages before importing them
print("🚀 Starting package verification...")
print("=" * 50)

# First do a quick status check
all_packages_available = check_package_status()

if not all_packages_available:
    print("🔧 Some packages need attention. Running installation process...")
    try:
        install_packages()
        print("✓ Package installation process completed")
    except Exception as e:
        logger.error(f"Package installation error: {e}")
        print("⚠ Some packages may not be installed. Continuing anyway...")
else:
    print("🎉 All required packages are already available!")

print("=" * 50)

# Try to install Coqui TTS separately (optional)
print("🔍 Checking for Coqui TTS...")
install_coqui_tts_optional()

# Try importing optional packages
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import sounddevice as sd  # type: ignore
    import numpy as np  # type: ignore
    from scipy.io.wavfile import write  # type: ignore
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    logger.error("speech_recognition not available - this is required!")

try:
    from sentence_transformers import SentenceTransformer, util  # type: ignore
    SENTENCE_TRANSFORMERS_AVAILABLE = True and TORCH_AVAILABLE
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from googletrans import Translator  # type: ignore
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

try:
    from difflib import SequenceMatcher
    DIFFLIB_AVAILABLE = True
except ImportError:
    DIFFLIB_AVAILABLE = False

try:
    import tempfile
    from gtts import gTTS  # type: ignore
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Try to import Edge TTS for better voices
try:
    import edge_tts  # type: ignore
    import asyncio
    import aiofiles  # type: ignore
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Try to import NLTK components
try:
    import nltk  # type: ignore
    from nltk.corpus import stopwords  # type: ignore
    from nltk.stem import PorterStemmer  # type: ignore
    from nltk.tokenize import word_tokenize  # type: ignore
    
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

# Try to import Wikipedia
try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False

# Try to import Coqui TTS - DISABLED BY USER REQUEST
try:
    from TTS.api import TTS as CoquiTTS  # type: ignore
    COQUI_TTS_AVAILABLE = False  # Disabled - user wants other TTS models only
except ImportError:
    COQUI_TTS_AVAILABLE = False

class NaturalShankaraAssistant:
    def __init__(self, qa_file="shankaracharya_qa.txt"):
        self.qa_file = qa_file
        self.log_file = "conversation_log.txt"
        self.conversation_context = []
        self.user_name = None
        self.conversation_started = False
        self.user_mood = "neutral"  # Track user's mood
        self.conversation_style = "casual"  # casual, formal, friendly
        self.malayalam_mode = False  # Track if user wants to continue in Malayalam
        self.current_response_language = "english"  # Track detected/preferred language for responses
        
        # Natural conversation starters - speaking as Adi Shankara
        self.conversation_starters = [
            "Namaste! I am Adi Shankara. I have walked this earth seeking truth and sharing the wisdom of Advaita Vedanta. What would you like to know about my teachings or journey?",
            "Greetings, my friend! I am Shankara, and I have spent my life exploring the deepest questions of existence. What draws you to seek knowledge today?",
            "Hello! I am Adi Shankara. Through my travels across Bharata and my philosophical inquiries, I have come to understand the true nature of reality. What aspects of truth interest you?",
            "Welcome! I am Shankara, and I have dedicated my life to understanding and teaching the unity of all existence. What would you like to explore about consciousness and reality?",
            "Namaste! I am Adi Shankara. My journey from Kaladi to the four corners of this land has been one of discovering the Self within all. What questions about the nature of being do you carry?"
        ]
        
        # Malayalam conversation starters - for when in Malayalam mode
        self.malayalam_conversation_starters = [
            "നമസ്കാരം! ഞാൻ ആദി ശങ്കരാചാര്യൻ ആണ്. അദ്വൈത വേദാന്തത്തിന്റെ സത്യം പങ്കുവെക്കാൻ ഞാൻ ഈ ഭൂമിയിൽ സഞ്ചരിച്ചിട്ടുണ്ട്. എന്റെ ഉപദേശങ്ങളെക്കുറിച്ചോ യാത്രയെക്കുറിച്ചോ എന്തറിയാൻ ആഗ്രഹിക്കുന്നു?",
            "നമസ്കാരം!  എന്റെ സുഹൃത്തേ! ഞാൻ ശങ്കരനാണ്, അസ്തിത്വത്തിന്റെ അഗാധമായ ചോദ്യങ്ങൾ അന്വേഷിക്കാൻ എന്റെ ജീവിതം ചെലവഴിച്ചിട്ടുണ്ട്. ഇന്ന് എന്താണ് നിങ്ങളെ അറിവ് തേടാൻ പ്രേരിപ്പിക്കുന്നത്?",
            "നമസ്തേ! ഞാൻ ആദി ശങ്കരാചാര്യൻ ആണ്. ഭാരതത്തിലുടനീളമുള്ള എന്റെ യാത്രകളിലൂടെയും തത്ത്വചിന്തയിലൂടെയും യാഥാർത്ഥ്യത്തിന്റെ യഥാർത്ഥ സ്വഭാവം മനസ്സിലാക്കാൻ കഴിഞ്ഞു. സത്യത്തിന്റെ ഏത് വശങ്ങളാണ് നിങ്ങൾക്ക് താൽപ്പര്യമുള്ളത്?",
            "സ്വാഗതം! ഞാൻ ശങ്കരനാണ്, എല്ലാ അസ്തിത്വത്തിന്റെയും ഏകത്വം മനസ്സിലാക്കാനും പഠിപ്പിക്കാനും എന്റെ ജീവിതം സമർപ്പിച്ചിട്ടുണ്ട്. ചൈതന്യത്തെക്കുറിച്ചും യാഥാർത്ഥ്യത്തെക്കുറിച്ചും എന്താണ് നിങ്ങൾ അന്വേഷിക്കാൻ ആഗ്രഹിക്കുന്നത്?"
        ]
        
        # Natural responses - speaking as Adi Shankara
        self.casual_responses = [
            "Ah, what a profound inquiry you bring forth!",
            "This touches upon one of the most essential truths I have contemplated.",
            "Your question goes to the very heart of understanding!",
            "How wonderful that you ask about this - it is fundamental to realization.",
            "This is indeed one of the most important aspects to understand.",
            "You have touched upon something very sacred and profound.",
            "Such a beautiful question - it shows genuine spiritual inquiry.",
            "I am delighted you have brought this forward for exploration!"
        ]
        
        # Natural transitions - speaking as Adi Shankara
        self.natural_transitions = [
            "From my understanding and direct realization...",
            "In my contemplation of this truth, I have discovered...",
            "Through my years of inquiry and teaching, I have come to see...",
            "What I have realized through grace and study is...",
            "In my experience of this profound truth...",
            "From the wisdom of the ancient sages and my own insight...",
            "What the scriptures reveal and I have verified is...",
            "Through both reasoning and direct knowing, I understand..."
        ]
        
        # Follow-up questions - speaking as Adi Shankara
        self.follow_ups = [
            "What are your thoughts on this understanding?",
            "Does this resonate with your own inner knowing?",
            "Have you contemplated this truth in your own experience?",
            "What is your reflection on this insight?",
            "I am curious to hear your contemplations on this matter.",
            "Does this understanding bring clarity to your seeking?",
            "What other aspects of this truth draw your inquiry?",
            "Is there some particular dimension of this you would like to explore further?"
        ]
        
        # Mood-based responses - speaking as Adi Shankara
        self.mood_responses = {
            "curious": [
                "I can sense your genuine curiosity about this profound truth! Your seeking spirit delights me.",
                "Your inquiry shows the kind of spiritual curiosity that leads to liberation. Let me share what I have realized.",
                "I am filled with joy seeing such sincere questioning - this is how true knowledge unfolds!"
            ],
            "thoughtful": [
                "Your thoughtful approach to this shows the mind of a true seeker.",
                "I appreciate the depth of contemplation you bring to these eternal questions.",
                "Your reflective nature reminds me of the ancient sages who sought truth with such dedication."
            ],
            "casual": [
                "Indeed, this is one of the most fascinating aspects of existence!",
                "Precisely! This understanding has brought me such clarity and peace.",
                "Exactly! This is what I found so illuminating in my own realization."
            ]
        }
        
        # Initialize text processing components
        if NLTK_AVAILABLE and PorterStemmer is not None:
            self.stemmer = PorterStemmer()
            try:
                if stopwords is not None:
                    self.stop_words = set(stopwords.words('english'))
                else:
                    self.stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
            except:
                self.stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
        else:
            self.stemmer = None
            self.stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
        
        # Enhanced synonyms for spiritual topics
        self.synonyms = {
            'philosopher': ['thinker', 'sage', 'teacher', 'guru', 'master', 'acharya'],
            'teaching': ['doctrine', 'philosophy', 'instruction', 'lesson', 'wisdom', 'knowledge'],
            'concept': ['idea', 'notion', 'principle', 'understanding'],
            'achieve': ['attain', 'reach', 'obtain', 'get', 'realize'],
            'goal': ['aim', 'purpose', 'objective', 'target', 'destination'],
            'established': ['founded', 'created', 'set up', 'built', 'instituted'],
            'liberation': ['freedom', 'release', 'moksha', 'enlightenment', 'realization'],
            'reality': ['truth', 'brahman', 'existence', 'being', 'consciousness'],
            'knowledge': ['wisdom', 'understanding', 'learning', 'jnana', 'awareness'],
            'self': ['atman', 'soul', 'consciousness', 'being', 'essence'],
            'illusion': ['maya', 'appearance', 'delusion', 'mirage'],
            'meditation': ['contemplation', 'reflection', 'dhyana', 'awareness'],
            'spiritual': ['divine', 'sacred', 'holy', 'transcendent']
        }
        
        # Initialize Wikipedia RAG attributes first
        self.wikipedia_content = None
        self.wikipedia_summary = None
        self.wikipedia_pages = {}
        
        # Initialize Coqui TTS attribute
        self.coqui_tts = None
        
        # Initialize components
        self.initialize_components()
        
        # Setup Wikipedia RAG if available
        if WIKIPEDIA_AVAILABLE:
            self.setup_wikipedia_rag()
        
        # Setup Coqui TTS if available - DISABLED BY USER REQUEST
        # if COQUI_TTS_AVAILABLE:
        #     self.setup_coqui_tts()

    def initialize_components(self):
        """Initialize all components with proper error handling"""
        print("Getting everything ready for our chat...")
        
        # Speech Recognition
        self.recognizer = None
        self.microphone = None
        if SR_AVAILABLE:
            try:
                if sr is not None and hasattr(sr, "Recognizer") and hasattr(sr, "Microphone"):
                    self.recognizer = sr.Recognizer()
                    mic_list = sr.Microphone.list_microphone_names()
                    self.microphone = sr.Microphone()
                else:
                    print("⚠ speech_recognition module or its classes are not available.")
                    self.recognizer = None
                    self.microphone = None
                
                # Adjust for natural conversation
                if self.microphone is not None:
                    with self.microphone as source:
                        print("Adjusting for ambient noise... please wait a moment.")
                        if self.recognizer is not None:
                            self.recognizer.adjust_for_ambient_noise(source, duration=1)
                            self.recognizer.energy_threshold = 3000
                            self.recognizer.dynamic_energy_threshold = True
                            self.recognizer.pause_threshold = 0.8
                            self.recognizer.phrase_threshold = 0.3
                    print("✓ Speech recognition is ready!")
                else:
                    print("⚠ Microphone is not available.")
                
            except ImportError as import_error:
                print(f"⚠ PyAudio not found: {import_error}")
                print("🔧 Try installing PyAudio: pip install pyaudio")
                self.recognizer = None
                self.microphone = None
            except Exception as e:
                print(f"⚠ Speech recognition setup failed: {e}")
                print("💡 This might be due to missing PyAudio or microphone issues")
                self.recognizer = None
                self.microphone = None
        
        # Text to Speech (TTS)
        self.tts_engine = None
        if PYTTSX3_AVAILABLE and pyttsx3 is not None:
            try:
                self.tts_engine = pyttsx3.init()
                
                # Test that the engine actually works
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    try:
                        # Try to get voice count safely
                        if hasattr(voices, '__len__'):
                            voice_count = len(voices)  # type: ignore
                            print(f"✓ Found {voice_count} TTS voices available")
                        elif hasattr(voices, '__iter__'):
                            voice_count = sum(1 for _ in voices)  # type: ignore
                            print(f"✓ Found {voice_count} TTS voices available")
                        else:
                            print("✓ TTS voices available")
                    except Exception:
                        print("✓ TTS voices available (count unknown)")
                else:
                    print("⚠ No TTS voices found - audio may not work")
                
                self.setup_enhanced_voice()
                
                # Quick functionality test
                try:
                    self.tts_engine.say("Testing")
                    self.tts_engine.runAndWait()
                    print("✓ Voice system is working and tested!")
                except Exception as test_error:
                    print(f"⚠ Voice system initialized but test failed: {test_error}")
                    
            except Exception as e:
                print(f"⚠ Having some voice issues: {e}")
                self.tts_engine = None
        else:
            self.tts_engine = None

        # Translator
        self.translator = None
        if TRANSLATOR_AVAILABLE and Translator is not None:
            try:
                self.translator = Translator()
                # Quick test
                test = self.translator.detect("hello")
                print("✓ Translation ready!")
            except Exception as e:
                print(f"⚠ Translation may have issues: {e}")
                self.translator = None

        # Semantic search
        self.embedding_model = None
        self.embeddings = None
        if SENTENCE_TRANSFORMERS_AVAILABLE and SentenceTransformer is not None:
            try:
                print("Loading semantic search model...")
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✓ Smart search loaded!")
            except Exception as e:
                print(f"⚠ Semantic search not available: {e}")
                self.embedding_model = None

        # Load knowledge base
        self.qa_pairs = self.load_qa_pairs()
        if self.embedding_model and self.qa_pairs:
            try:
                print("Preparing knowledge embeddings...")
                questions = [q for q, _ in self.qa_pairs]
                self.embeddings = self.embedding_model.encode(questions, convert_to_tensor=True)
                print(f"✓ Knowledge base ready with {len(self.qa_pairs)} topics!")
            except Exception as e:
                print(f"⚠ Embedding creation failed: {e}")
                self.embeddings = None
        
        # Display voice capabilities
        print("\n🎭 Voice Options Available:")
        # Coqui TTS disabled by user request
        # if COQUI_TTS_AVAILABLE:
        #     print("  • Coqui TTS voices (Premium Quality)")
        if EDGE_TTS_AVAILABLE:
            print("  • Enhanced Edge TTS voices (High Quality)")
        if PYTTSX3_AVAILABLE:
            print("  • System TTS voices (Medium Quality)")
        if GTTS_AVAILABLE:
            print("  • Google TTS voices (Basic Quality)")
        
        # Display knowledge sources
        print("\n📚 Knowledge Sources:")
        print(f"  • Local Q&A database ({len(self.qa_pairs)} entries)")
        if WIKIPEDIA_AVAILABLE and self.wikipedia_content:
            print("  • Wikipedia content (Adi Shankara & related topics)")
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            print("  • AI-powered semantic search")

        print("\n" + "="*50)
        print("🎯 Ready to chat! Let's begin...")
        print("="*50 + "\n")
        
        # Small delay to ensure everything is loaded
        time.sleep(0.5)
    
    def setup_wikipedia_rag(self):
        """Setup Wikipedia RAG for enhanced knowledge about Adi Shankara with page restrictions"""
        if not wikipedia:
            logger.warning("Wikipedia module not available for RAG")
            return False
            
        try:
            print("📚 Loading Wikipedia content about Adi Shankara...")
            wikipedia.set_lang("en")
            wikipedia.set_rate_limiting(True)  # Enable rate limiting to prevent timeouts
            
            # Restricted list of allowed pages for Adi Shankara context
            allowed_pages = [
                "Adi Shankara",
                "Advaita Vedanta", 
                "Vedanta",
                "Brahman",
                "Maya (illusion)",
                "Upanishads",
                "Brahma Sutras",
                "Bhagavad Gita",
                "Vivekachudamani",
                "Upadesa Sahasri",
                "Atma Bodha",
                "Non-dualism",
                "Hindu philosophy",
                "Dashanami Sampradaya"
            ]
            
            self.wikipedia_pages = {}
            self.wikipedia_content = ""
            self.wikipedia_summary = ""
            
            # Load content from allowed pages only
            pages_loaded = 0
            total_pages = len(allowed_pages)
            for i, page_title in enumerate(allowed_pages, 1):
                try:
                    print(f"📖 Loading {i}/{total_pages}: {page_title}...")
                    page = wikipedia.page(page_title, auto_suggest=False)  # Disable auto-suggest to prevent hanging
                    content = page.content[:3000]  # Limit content to prevent overwhelming
                    summary = page.summary[:300]
                    
                    self.wikipedia_pages[page_title] = {
                        "content": content,
                        "url": page.url,
                        "summary": summary
                    }
                    
                    # Add to combined content
                    self.wikipedia_content += f"\n\n=== {page_title} ===\n{content}"
                    if not self.wikipedia_summary and page_title == "Adi Shankara":
                        self.wikipedia_summary = summary
                    
                    pages_loaded += 1
                    print(f"✓ Loaded: {page_title}")
                    
                except wikipedia.exceptions.DisambiguationError as e:
                    try:
                        # Try first option from disambiguation
                        page = wikipedia.page(e.options[0])
                        content = page.content[:3000]
                        summary = page.summary[:300]
                        
                        self.wikipedia_pages[page_title] = {
                            "content": content,
                            "url": page.url,
                            "summary": summary
                        }
                        self.wikipedia_content += f"\n\n=== {page_title} ===\n{content}"
                        pages_loaded += 1
                        print(f"✓ Loaded disambiguated: {e.options[0]} for {page_title}")
                        
                    except Exception:
                        print(f"⚠ Could not load disambiguated page for {page_title}")
                        
                except wikipedia.exceptions.PageError:
                    print(f"⚠ Wikipedia page not found: {page_title}")
                    
                except Exception as e:
                    print(f"⚠ Error loading {page_title}: {e}")
                    
            print(f"✓ Successfully loaded {pages_loaded} Wikipedia pages for enhanced knowledge!")
            return pages_loaded > 0
            
        except Exception as e:
            print(f"⚠ Wikipedia setup error: {e}")
            self.wikipedia_content = ""
            self.wikipedia_summary = ""
            return False
    
    def setup_coqui_tts(self):
        """Setup Coqui TTS for high-quality voice synthesis with masculine voice"""
        try:
            print("🎤 Initializing Coqui TTS for Adi Shankara's voice...")
            if CoquiTTS is not None:
                # Try different models in order of preference for masculine, mature voice
                preferred_models = [
                    "tts_models/en/ljspeech/tacotron2-DDC",     # Default good quality
                    "tts_models/en/ljspeech/tacotron2-DCA",     # Alternative high quality  
                    "tts_models/en/ljspeech/glow-tts",          # Another good option
                    "tts_models/en/ek1/tacotron2",              # Try alternative dataset
                ]
                
                for model_name in preferred_models:
                    try:
                        self.coqui_tts = CoquiTTS(
                            model_name=model_name, 
                            progress_bar=False, 
                            gpu=False
                        )
                        print(f"✓ Coqui TTS ready with model: {model_name}")
                        break
                    except Exception as model_error:
                        print(f"⚠ Could not load {model_name}: {model_error}")
                        continue
                
                if not self.coqui_tts:
                    print("⚠ Could not initialize any Coqui TTS model")
            else:
                self.coqui_tts = None
                print("⚠ Coqui TTS library not available")
        except Exception as e:
            print(f"⚠ Coqui TTS setup error: {e}")
            self.coqui_tts = None
    def setup_enhanced_voice(self):
        """Setup TTS with improved voice selection"""
        if not self.tts_engine:
            return
            
        try:
            # Enhanced voice settings for better quality
            voices = self.tts_engine.getProperty('voices')
            if voices and hasattr(voices, "__len__") and hasattr(voices, "__iter__"):
                try:
                    if hasattr(voices, '__len__'):
                        voices_length = len(voices)  # type: ignore
                    else:
                        voices_length = 0
                    
                    # Enhanced voice selection with better priorities
                    best_voice = None
                    voice_scores = []
                    
                    if voices_length > 0:
                        # Ensure voices is actually iterable
                        try:
                            if hasattr(voices, '__iter__'):
                                voices_list = list(voices)  # type: ignore
                            else:
                                voices_list = []
                        except (TypeError, AttributeError):
                            voices_list = []
                        
                        for voice in voices_list:
                            if hasattr(voice, 'name') and hasattr(voice, 'id'):
                                name_lower = voice.name.lower()
                                score = 0
                                
                                # Prioritize male voices for Adi Shankara's masculine, authoritative presence
                                if any(word in name_lower for word in ['male', 'man', 'masculine']) and 'female' not in name_lower:
                                    score += 15
                                
                                # Premium voice preferences (highest priority)
                                if any(word in name_lower for word in ['neural', 'enhanced', 'premium']):
                                    score += 10
                                
                                # Deep, mature male voice names (perfect for sage-like presence)
                                if any(word in name_lower for word in ['david', 'mark', 'ryan', 'guy', 'william', 'james', 'thomas']):
                                    score += 12
                                
                                # Avoid high-pitched or feminine voices
                                if any(word in name_lower for word in ['female', 'woman', 'aria', 'zira', 'cortana', 'hazel', 'eva']):
                                    score -= 10
                                
                                # Good Microsoft voices with deep tones (medium-high priority)
                                if any(word in name_lower for word in ['desktop male', 'server male']):
                                    score += 8
                                
                                # Standard Microsoft voices (medium priority)
                                if 'microsoft' in name_lower and any(word in name_lower for word in ['english', 'us', 'uk']):
                                    score += 4
                                
                                # Strongly avoid robotic or artificial-sounding voices
                                if any(word in name_lower for word in ['robotic', 'sam', 'microsoft sam', 'artificial']):
                                    score -= 15
                                
                                voice_scores.append((voice, score, name_lower))
                        
                        # Sort by score and select the best
                        if voice_scores:
                            voice_scores.sort(key=lambda x: x[1], reverse=True)
                            best_voice = voice_scores[0][0]
                            self.tts_engine.setProperty('voice', best_voice.id)
                            print(f"🎤 Selected voice: {best_voice.name}")
                        else:
                            # Fallback to first available voice
                            if voices and hasattr(voices, '__getitem__') and len(voices) > 0:  # type: ignore
                                self.tts_engine.setProperty('voice', voices[0].id)  # type: ignore
                                print(f"🎤 Using default voice: {voices[0].name}")  # type: ignore
                            else:
                                print("🎤 No suitable voices found, using system default")
                                
                        # Configure voice characteristics for Adi Shankara's sage-like presence
                        try:
                            # Slower, more contemplative speech rate (normal is 200)
                            current_rate = self.tts_engine.getProperty('rate')
                            if current_rate and isinstance(current_rate, (int, float)):
                                sage_rate = max(120, int(current_rate) - 50)  # Slower, more measured speech
                            else:
                                sage_rate = 150  # Default sage-like rate
                            self.tts_engine.setProperty('rate', sage_rate)
                            
                            # Adjust volume for clear, authoritative presence
                            self.tts_engine.setProperty('volume', 0.9)  # High but not overwhelming
                            
                            print(f"🎭 Voice configured for sage-like delivery: Rate={sage_rate}, Volume=0.9")
                            
                        except Exception as voice_config_error:
                            print(f"⚠ Could not adjust voice characteristics: {voice_config_error}")
                            # Continue anyway with default settings
                except Exception as e:
                    logger.error(f"Voice selection error: {e}")
                    print("⚠ Using default voice")
                    
        except Exception as e:
            logger.error(f"Enhanced voice setup error: {e}")
            print("⚠ Using basic voice settings")

    def cleanup_temp_file(self, filepath):
        """Clean up temporary files with improved error handling"""
        try:
            if filepath and os.path.exists(filepath):
                # Wait a bit to ensure file is not in use
                time.sleep(0.5)
                os.unlink(filepath)
                print(f"🧹 Cleaned up temp file: {os.path.basename(filepath)}")
        except Exception as e:
            # Try again after a longer wait
            try:
                time.sleep(2.0)
                if os.path.exists(filepath):
                    os.unlink(filepath)
            except Exception:
                pass  # Ignore cleanup errors - temp files will be cleaned by system eventually

    def play_audio_file_windows(self, filepath):
        """Play audio file on Windows with multiple fallback methods"""
        try:
            print(f"🔊 Playing audio file: {os.path.basename(filepath)}")
            
            # Method 1: Try pygame
            try:
                import pygame
                print("   Trying pygame...")
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                pygame.mixer.quit()
                print("   ✓ pygame playback successful")
                return True
            except (ImportError, Exception) as e:
                print(f"   ⚠ pygame failed: {e}")
                pass
            
            # Method 2: Try Windows Media Player via PowerShell
            try:
                result = subprocess.run([
                    'powershell', '-command', 
                    f'Add-Type -AssemblyName presentationCore; '
                    f'$mediaPlayer = New-Object System.Windows.Media.MediaPlayer; '
                    f'$mediaPlayer.open([System.Uri]::new("{filepath}")); '
                    f'$mediaPlayer.Play(); '
                    f'Start-Sleep 5'
                ], capture_output=True, timeout=30, text=True)
                return True
            except Exception:
                pass
            
            # Method 3: Use start command with wmplayer
            try:
                subprocess.run(['start', '/wait', 'wmplayer.exe', filepath], 
                             shell=True, timeout=30)
                return True
            except Exception:
                pass
            
            # Method 4: Simple start command
            try:
                print("   Trying system start command...")
                os.system(f'start /min "" "{filepath}"')
                time.sleep(3)  # Give it time to play
                print("   ✓ system start command completed")
                return True
            except Exception:
                pass
                
            print("   ❌ All audio playback methods failed")
            return False
            
        except Exception as e:
            print(f"⚠ Audio playback failed: {e}")
            return False
    def load_qa_pairs(self):
        """Load Q&A pairs from JSON file or create sample data"""
        json_file = "shankaracharya_knowledge.json"
        
        # Try to load from JSON first
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                qa_pairs = []
                for entry in data.get('knowledge_base', []):
                    question = entry.get('question', '')
                    answer = entry.get('answer', '')
                    if question and answer:
                        qa_pairs.append((question, answer))
                
                logger.info(f"Loaded {len(qa_pairs)} Q&A pairs from {json_file}")
                return qa_pairs
                
            except Exception as e:
                logger.error(f"Error loading JSON file: {e}")
                print(f"⚠ Error loading JSON file: {e}")
        
        # Fallback to old text format
        if not os.path.exists(self.qa_file):
            self.create_sample_qa_file()
        
        qa_pairs = []
        try:
            with open(self.qa_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse Q&A pairs from the content
            lines = content.split('\n')
            current_question = None
            current_answer = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('Q: '):
                    # Save previous Q&A pair if exists
                    if current_question and current_answer:
                        qa_pairs.append((current_question, '\n'.join(current_answer).strip()))
                    
                    # Start new question
                    current_question = line[3:]  # Remove 'Q: '
                    current_answer = []
                    
                elif line.startswith('A: '):
                    # Start answer
                    current_answer = [line[3:]]  # Remove 'A: '
                    
                elif line and current_answer is not None:
                    # Continue answer
                    current_answer.append(line)
            
            # Add the last Q&A pair
            if current_question and current_answer:
                qa_pairs.append((current_question, '\n'.join(current_answer).strip()))
                
            logger.info(f"Loaded {len(qa_pairs)} Q&A pairs from {self.qa_file}")
            return qa_pairs
            
        except Exception as e:
            logger.error(f"Error loading Q&A pairs: {e}")
            self.create_sample_qa_file()
            return []

    def create_sample_qa_file(self):
        """Create a sample Q&A file with Shankara content in first person"""
        sample_content = """Q: Who are you?
A: I am Adi Shankara, born in Kaladi, Kerala, in the 8th century. I have dedicated my life to understanding and teaching the profound truth of Advaita Vedanta - that all existence is one undivided consciousness. In my brief time in this physical form, I traveled across all of Bharata, engaged in philosophical debates, established four sacred mathas, and wrote commentaries on the ancient scriptures. My purpose has been to help souls realize their true nature as the eternal, infinite Self - to show that what you truly are is not separate from the universal consciousness that appears as all existence.

Q: Tell me about yourself
A: I am Adi Shankara, also known as Shankaracharya. I was born in the sacred village of Kaladi in Kerala around 788 CE. From an early age, I was drawn to the deepest questions of existence. I renounced worldly life at a young age to become a sannyasi and dedicated myself to understanding the ultimate truth revealed in the Vedas and Upanishads. In my 32 years of life, I traveled the length and breadth of India, engaging in philosophical debates with scholars of various schools, writing profound commentaries on the Brahma Sutras, Upanishads, and Bhagavad Gita, and establishing four monasteries to preserve the ancient wisdom. My life's mission has been to revive and clarify the teaching of Advaita Vedanta - the understanding that the individual soul and universal consciousness are one and the same. Through direct realization and logical reasoning, I have sought to help humanity transcend the illusion of separateness and recognize their true nature as infinite, eternal consciousness.

Q: Introduce yourself
A: Namaste! I am Adi Shankara, born into this world to clarify the eternal wisdom of the Vedas. Though I lived only 32 years in physical form, those years were devoted entirely to the highest purpose - helping souls realize their true nature. I am the one who systematized the philosophy of Advaita Vedanta, establishing that Brahman alone is real, the world is appearance, and the individual soul is not different from Brahman. I have traveled from the southernmost tip of India to the Himalayas, not seeking anything for myself, but sharing the liberating truth that you are already what you seek to become. I have written extensive commentaries on our sacred texts and established four mathas to ensure this wisdom continues to flow. But more than any title or achievement, I am simply a voice pointing you back to your own infinite Self.

Q: What is Advaita Vedanta that you teach?
A: Advaita Vedanta is the heart of my teaching, and it reveals the most profound truth about reality. "Advaita" means "not two" - I teach that reality is not actually divided into separate things the way it appears to be. There is only one ultimate reality, which I call Brahman - pure consciousness itself. Everything you see, including your own individual self, is actually that same consciousness appearing in different forms. It is like waves in the ocean - they appear separate, but they are all nothing but water. My teaching aims to help you realize this truth directly, not merely understand it intellectually. When you truly know this, all suffering born of separateness dissolves.

Q: What is maya according to your understanding?
A: Maya is a profound concept that I have contemplated deeply. It is often translated as "illusion," but this is not entirely accurate. Maya is the mysterious creative power by which the one consciousness appears as the many. Think of it like the power of a great artist who can create countless forms from a single medium. Maya is not separate from Brahman - it is Brahman's own power of manifestation. The world is not false or unreal, but our perception of it as being separate from consciousness - that is where the confusion lies. When you understand maya correctly, you see that the world is real as Brahman appearing, but unreal as the separate, independent objects we imagine it to be. This understanding liberates you from the binding effect of appearances.

Q: About you
A: I am Shankara, a seeker who became a teacher, a student who became a master, yet always remaining humble before the infinite truth. I was born in Kaladi, a blessed village in Kerala, and my entire existence has been dedicated to one purpose: revealing to humanity their true divine nature. I have not come to create a new philosophy, but to clarify the eternal wisdom that has always existed in our sacred Vedas and Upanishads. Through my travels, debates, writings, and direct realization, I have shown that what appears as the many is actually the One appearing in countless forms. My life has been a demonstration that the highest knowledge is not mere intellectual understanding, but the direct recognition of one's true Self as infinite consciousness. This is why I am here - to remind you of what you have never actually forgotten, only temporarily overlooked.

Q: Your background
A: My background is rooted in the ancient tradition of Sanatana Dharma. I was born to Sivaguru and Aryamba in Kaladi, Kerala. Even as a child, I showed exceptional intelligence and deep spiritual inclination. I studied the Vedas and Sanskrit extensively, but my heart yearned for something beyond mere scholarship. At age eight, I took sannyasa and became the disciple of Govinda Bhagavatpada, who himself was a student of the great sage Gaudapada. Under his guidance, I attained the highest realization - the direct knowledge that Atman and Brahman are one. This wasn't just intellectual understanding but a complete transformation of being. From this realization arose my mission: to travel across India, engage with scholars, write definitive commentaries on our scriptures, and establish centers of learning. My background combines the rigor of traditional Vedic scholarship with the fire of direct spiritual realization."""
        
        try:
            with open(self.qa_file, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            print(f"✓ Created knowledge base: {self.qa_file}")
        except Exception as e:
            print(f"⚠ Had trouble creating the knowledge file: {e}")

    def semantic_search(self, query):
        """Perform semantic search using sentence transformers"""
        if not self.embedding_model or self.embeddings is None or not self.qa_pairs:
            return None
            
        try:
            # Encode the query
            query_embedding = self.embedding_model.encode(query, convert_to_tensor=True)
            
            # Calculate similarities
            if util is not None:
                similarities = util.pytorch_cos_sim(query_embedding, self.embeddings)[0]
                
                # Get the best match - convert to int first
                best_match_idx = int(similarities.argmax().item())
                best_score = float(similarities[best_match_idx].item())
                
                # Return answer if score is good enough
                if best_score > 0.3:  # Threshold for semantic similarity
                    # Return raw answer - conversion will happen in create_natural_response
                    return self.qa_pairs[best_match_idx][1]
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            
        return None

    def convert_to_first_person(self, text):
        """Convert third-person content about Shankara to first-person"""
        if not text:
            return text
            
        # Common third-person to first-person conversions
        conversions = {
            r'\bAdi Shankara was\b': 'I was',
            r'\bShankara was\b': 'I was',
            r'\bShankaracharya was\b': 'I was',
            r'\bAdi Shankara is\b': 'I am',
            r'\bShankara is\b': 'I am', 
            r'\bShankaracharya is\b': 'I am',
            r'\bAdi Shankara taught\b': 'I taught',
            r'\bShankara taught\b': 'I taught',
            r'\bShankaracharya taught\b': 'I taught',
            r'\bAdi Shankara established\b': 'I established',
            r'\bShankara established\b': 'I established',
            r'\bShankaracharya established\b': 'I established',
            r'\bAdi Shankara traveled\b': 'I traveled',
            r'\bShankara traveled\b': 'I traveled',
            r'\bShankaracharya traveled\b': 'I traveled',
            r'\bAdi Shankara wrote\b': 'I wrote',
            r'\bShankara wrote\b': 'I wrote',
            r'\bShankaracharya wrote\b': 'I wrote',
            r'\bAdi Shankara believed\b': 'I believe',
            r'\bShankara believed\b': 'I believe',
            r'\bShankaracharya believed\b': 'I believe',
            r'\bAdi Shankara said\b': 'I said',
            r'\bShankara said\b': 'I said',
            r'\bShankaracharya said\b': 'I said',
            r'\bAdi Shankara\'s\b': 'My',
            r'\bShankara\'s\b': 'My',
            r'\bShankaracharya\'s\b': 'My',
            r'\bhis\b': 'my',
            r'\bHis\b': 'My',
            r'\bhe\b': 'I',
            r'\bHe\b': 'I',
            r'\bhim\b': 'me',
            r'\bHim\b': 'Me'
        }
        
        converted_text = text
        for pattern, replacement in conversions.items():
            converted_text = re.sub(pattern, replacement, converted_text)
            
        return converted_text

    def create_natural_response(self, answer, query):
        """Create a more natural, conversational response"""
        # Convert third-person content to first-person if needed
        converted_answer = self.convert_to_first_person(answer)
        
        # Add natural conversation starters
        starter = random.choice(self.casual_responses)
        
        # Add mood-based responses
        if self.user_mood in self.mood_responses:
            mood_starter = random.choice(self.mood_responses[self.user_mood])
            if random.random() < 0.3:  # 30% chance to use mood response
                starter = mood_starter
        
        # Add natural transitions
        transition = random.choice(self.natural_transitions)
        
        # Create the response
        response = f"{starter} {transition} {converted_answer}"
        
        # Add follow-up question
        if random.random() < 0.7:  # 70% chance to add follow-up
            follow_up = random.choice(self.follow_ups)
            response += f" {follow_up}"
        
        return response

    def create_natural_unknown_response(self):
        """Create natural response for unknown questions"""
        unknown_responses = [
            "That is a thoughtful inquiry, my friend. While I may not have specific knowledge about that particular matter, I encourage you to continue your seeking. The greatest discoveries often come not from answers given, but from questions deeply contemplated. What other aspects of truth or my teachings would you like to explore together?",
            
            "Your question shows a genuine spirit of inquiry, which I deeply appreciate. Though I may not have insight into that specific matter, remember that the most profound knowledge comes from within through direct realization. Is there some aspect of consciousness, reality, or the path to liberation that draws your curiosity?",
            
            "I honor your sincere questioning, though I may not have particular knowledge about that topic. The very act of questioning with sincerity opens the door to understanding. What other aspects of the spiritual path or the nature of existence would you like to contemplate with me?",
            
            "That is an earnest question, and I appreciate your seeking nature. While that specific matter may be beyond my current sharing, the most important knowledge is that which reveals your true Self. What other aspects of this eternal wisdom interest you?",
        ]
        return random.choice(unknown_responses)

    def log_conversation(self, speaker, message):
        """Log the conversation to file"""
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {speaker}: {message}\n")
        except Exception as e:
            logger.error(f"Logging error: {e}")
    def listen_with_patience(self, timeout=10, phrase_time_limit=15):
        """Listen with enhanced patience and error handling"""
        if not self.recognizer or not self.microphone:
            return input("🗣️ (Speech recognition unavailable) Please type: ").strip()
        
        try:
            with self.microphone as source:
                print("🎧 Microphone activated - Listening... (speak naturally)")
                
                # Adjust for ambient noise quickly
                print("🔇 Adjusting for background noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("✓ Ready! Speak now...")
                
                # Listen for audio
                try:
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout, 
                        phrase_time_limit=phrase_time_limit
                    )
                    print("🔇 Microphone deactivated - Processing speech...")
                except Exception as timeout_error:
                    if 'timeout' in str(timeout_error).lower():
                        print("🔇 Microphone deactivated - No speech detected")
                        return ""
                    else:
                        raise timeout_error
            # Try Google Speech Recognition first
            try:
                if hasattr(self.recognizer, 'recognize_google'):
                    text = self.recognizer.recognize_google(audio)  # type: ignore
                    return text.strip()
                else:
                    print("🎤 Google recognition not available")
                    return input("Please type your message: ").strip()
            except Exception as e1:
                if sr is not None and hasattr(sr, 'UnknownValueError') and isinstance(e1, sr.UnknownValueError):
                    responses = [
                        "I didn't quite catch that. Could you speak a bit more clearly?",
                        "Sorry, I couldn't understand what you said. Mind trying again?", 
                        "Hmm, the audio wasn't clear enough. Could you repeat that please?",
                        "I'm having trouble understanding. Could you speak a little louder or slower?"
                    ]
                    import random
                    chosen_response = random.choice(responses)
                    print(f"💭 {chosen_response}")
                    # Actually speak the clarification request
                    self.speak_with_enhanced_quality(chosen_response, pause_before=0.2, pause_after=0.5)
                    return ""
                elif sr is not None and hasattr(sr, 'RequestError') and isinstance(e1, sr.RequestError):
                    # Fallback to other recognition methods
                    try:
                        if hasattr(self.recognizer, 'recognize_sphinx'):
                            text = self.recognizer.recognize_sphinx(audio)  # type: ignore
                            return text.strip()
                        else:
                            print("🎤 Sphinx recognition not available")
                            return input("Please type your message: ").strip()
                    except Exception:
                        print("🎤 Having trouble with speech recognition. Let me try text input instead.")
                        return input("Please type your message: ").strip()
                else:
                    responses = [
                        "I didn't quite catch that. Could you try speaking again?",
                        "Sorry, could you repeat that? I didn't understand clearly.",
                        "I'm having trouble hearing you. Could you try once more?"
                    ]
                    import random
                    chosen_response = random.choice(responses)
                    print(f"💭 {chosen_response}")
                    self.speak_with_enhanced_quality(chosen_response, pause_before=0.2, pause_after=0.5)
                    return ""
                    
        except Exception as e:
            if sr is not None and hasattr(sr, 'WaitTimeoutError') and 'timeout' in str(type(e)).lower():
                return ""  # Return empty string for timeout
            print(f"🎤 Speech issue: {e}")
            return input("Let's try typing instead: ").strip()

    async def edge_tts_speak_async(self, text):
        """Async Edge TTS speak function with masculine, sage-like voice selection"""
        try:
            # Carefully selected male voices that sound wise, mature, and authoritative
            # Perfect for embodying Adi Shankara's voice
            masculine_sage_voices = [
                "en-US-DavisNeural",      # Deep, mature male voice - excellent for philosophy
                "en-US-JasonNeural",      # Warm, authoritative male voice  
                "en-US-TonyNeural",       # Rich, confident male voice
                "en-GB-RyanNeural",       # Distinguished British male voice - sounds scholarly
                "en-AU-WilliamNeural",    # Mature Australian male voice
                "en-IN-PrabhatNeural",    # Indian male voice - culturally appropriate for Shankara
                "en-US-GuyNeural",        # Deep, resonant male voice
                "en-GB-ThomasNeural",     # Authoritative British male voice
            ]
            
            # Prefer Indian English voice for cultural authenticity, fallback to other mature male voices
            preferred_voice = "en-IN-PrabhatNeural"  # Most culturally appropriate
            voice = preferred_voice if preferred_voice in masculine_sage_voices else random.choice(masculine_sage_voices)
            temp_file = None
            
            try:
                if edge_tts is not None and hasattr(edge_tts, "Communicate") and tempfile is not None:
                    # Create temporary file for audio
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tf:
                        temp_file = tf.name
                    
                    # Create Edge TTS communication
                    communicate = edge_tts.Communicate(text, voice)
                    await communicate.save(temp_file)
                    success = False
                    
                    if os.name == 'nt' and temp_file is not None:
                        try:
                            if pygame is not None:
                                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                                pygame.mixer.music.load(temp_file)
                                pygame.mixer.music.play()
                                while pygame.mixer.music.get_busy():
                                    if asyncio is not None and hasattr(asyncio, "sleep"):
                                        await asyncio.sleep(0.1)
                                success = True
                        except ImportError:
                            os.system(f'start /min "" "{temp_file}"')
                            if asyncio is not None and hasattr(asyncio, "sleep"):
                                await asyncio.sleep(max(len(text) * 0.08, 2))
                            success = True
                    elif sys.platform == 'darwin':
                        try:
                            os.system(f'afplay "{temp_file}"')
                            success = True
                        except Exception:
                            pass
                    else:
                        try:
                            os.system(f'mpg123 "{temp_file}" 2>/dev/null || mplayer "{temp_file}" 2>/dev/null')
                            success = True
                        except Exception:
                            pass
                    
                    # Cleanup
                    threading.Timer(3.0, lambda: self.cleanup_temp_file(temp_file)).start()
                    if success:
                        return True
            except Exception:
                if temp_file and os.path.exists(temp_file):
                    self.cleanup_temp_file(temp_file)
            return False
        except Exception:
            return False

    def coqui_tts_speak(self, text):
        """Speak using Coqui TTS for high quality voice output"""
        if not self.coqui_tts:
            return False
            
        try:
            # Create temporary file for audio
            if tempfile is not None:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_filepath = temp_file.name
            else:
                return False
            
            # Generate speech using Coqui TTS
            self.coqui_tts.tts_to_file(text, file_path=temp_filepath)
            
            # Play the audio file
            success = False
            if os.name == 'nt':  # Windows
                try:
                    import pygame
                    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                    pygame.mixer.music.load(temp_filepath)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    pygame.mixer.quit()
                    success = True
                except ImportError:
                    os.system(f'start /min "" "{temp_filepath}"')
                    time.sleep(max(len(text) * 0.08, 2))
                    success = True
            elif sys.platform == 'darwin':  # macOS
                os.system(f'afplay "{temp_filepath}"')
                success = True
            else:  # Linux
                os.system(f'aplay "{temp_filepath}"')
                success = True
                
            # Cleanup
            threading.Timer(3.0, lambda: self.cleanup_temp_file(temp_filepath)).start()
            return success
            
        except Exception as e:
            print(f"⚠ Coqui TTS error: {e}")
            return False

    def speak_with_enhanced_quality(self, text, pause_before=0.3, pause_after=0.8):
        """Speak with the best available voice technology"""
        if pause_before > 0:
            time.sleep(pause_before)
        
        # Detect if text is in Malayalam
        is_malayalam = any(ord(char) >= 0x0D00 and ord(char) <= 0x0D7F for char in text)
        
        # Always show the text
        print(f"\n💬 Assistant: {text}\n")
        self.log_conversation("Assistant", text)
        
        # Debug: Show which TTS engines are available
        print("🔊 Attempting to speak using available TTS engines...")
        
        # Quick Windows SAPI test first (most reliable on Windows)
        if os.name == 'nt' and not is_malayalam:
            try:
                print("🎤 Trying Windows SAPI with male voice...")
                import win32com.client
                
                # Create enhanced text for speech
                enhanced_text = self.enhance_text_for_speech(text) if not is_malayalam else text
                
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                
                # Try to select a male voice (David or similar)
                voices = speaker.GetVoices()
                male_voice_found = False
                
                for i in range(voices.Count):
                    voice = voices.Item(i)
                    voice_name = voice.GetDescription()
                    print(f"   Available voice: {voice_name}")
                    
                    # Look for male voices - prioritize David or deep voices
                    if any(name in voice_name.lower() for name in ['david', 'male', 'man']):
                        speaker.Voice = voice
                        male_voice_found = True
                        print(f"✅ Selected male voice: {voice_name}")
                        break
                
                if not male_voice_found:
                    # Fallback to first available voice
                    if voices.Count > 0:
                        speaker.Voice = voices.Item(0)
                        print(f"✅ Using default voice: {voices.Item(0).GetDescription()}")
                
                # Configure speech settings for spiritual/meditative tone
                speaker.Rate = 2  # Slower, more contemplative (SAPI scale: -10 to 10)
                speaker.Volume = 100  # Full volume
                
                print("🔊 Speaking with spiritual tone...")
                speaker.Speak(enhanced_text)
                print("✓ Windows SAPI speech completed")
                if pause_after > 0:
                    time.sleep(pause_after)
                return
                
            except Exception as sapi_error:
                print(f"⚠ Windows SAPI failed: {sapi_error}")
        
        # For Malayalam text, use Google TTS with Malayalam language
        if is_malayalam and GTTS_AVAILABLE and gTTS is not None:
            try:
                tts = gTTS(text=text, lang='ml', slow=False)  # 'ml' is Malayalam language code
                
                # Create temp file with proper Windows handling
                temp_file = None
                try:
                    if tempfile is not None:
                        temp_fd, temp_file = tempfile.mkstemp(suffix=".mp3")
                        os.close(temp_fd)  # Close the file descriptor
                    else:
                        # Fallback temp file creation
                        import uuid
                        temp_file = f"temp_tts_{uuid.uuid4().hex}.mp3"
                    
                    # Save TTS to file
                    tts.save(temp_file)
                    
                    # Verify file exists and has content
                    if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
                        raise Exception("TTS file was not created properly")
                    
                    # Play based on platform
                    success = False
                    if os.name == 'nt':  # Windows
                        success = self.play_audio_file_windows(temp_file)
                    elif sys.platform == 'darwin':  # macOS
                        result = os.system(f'afplay "{temp_file}"')
                        if result == 0:
                            success = True
                        else:
                            print(f"⚠ macOS audio playback returned: {result}")
                    else:  # Linux
                        result = os.system(f'mpg123 "{temp_file}" 2>/dev/null || mplayer "{temp_file}" 2>/dev/null')
                        if result == 0:
                            success = True
                        else:
                            print(f"⚠ Linux audio playback returned: {result}")
                    
                    if success:
                        if pause_after > 0:
                            time.sleep(pause_after)
                        return
                    else:
                        print("⚠ Audio playback failed, trying alternative methods...")
                        
                except Exception as file_error:
                    print(f"⚠ TTS file creation failed: {file_error}")
                finally:
                    # Clean up temp file
                    if temp_file and os.path.exists(temp_file):
                        try:
                            threading.Timer(2.0, lambda: self.cleanup_temp_file(temp_file)).start()
                        except Exception:
                            pass
                    
            except Exception as e:
                print(f"⚠ Malayalam TTS failed: {e}")
        
        # For English text, enhance for speech and use regular TTS
        enhanced_text = self.enhance_text_for_speech(text) if not is_malayalam else text
        
        # Coqui TTS disabled by user request
        # Try Coqui TTS first (highest quality) - only for English - DISABLED
        # if not is_malayalam and COQUI_TTS_AVAILABLE and self.coqui_tts:
        #     try:
        #         success = self.coqui_tts_speak(enhanced_text)
        #         if success:
        #             if pause_after > 0:
        #                 time.sleep(pause_after)
        #             return
        #     except Exception as e:
        #         print(f"⚠ Coqui TTS failed: {e}")
        
        # Try Edge TTS first (high quality) - only for English
        if not is_malayalam and EDGE_TTS_AVAILABLE and asyncio is not None:
            try:
                print("🎤 Using Edge TTS...")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(self.edge_tts_speak_async(enhanced_text))
                loop.close()
                
                if success:
                    print("✓ Edge TTS speech completed")
                    if pause_after > 0:
                        time.sleep(pause_after)
                    return
                else:
                    print("⚠ Edge TTS returned False, trying next method...")
                    
            except Exception as e:
                print(f"⚠ Edge TTS failed: {e}, trying next method...")
        
        #        # Try Azure Speech Service (if available)
        if not is_malayalam:
            try:
                print("🎤 Trying Azure Speech Service...")
                # Check if azure-cognitiveservices-speech is available
                if 'speechsdk' in globals():
                    # Configure Azure Speech (you would need to set API key)
                    # For now, this is a placeholder for potential future enhancement
                    print("⚠ Azure Speech requires API key configuration")
                else:
                    print("⚠ Azure Speech Service not available (package not installed)")
                
            except Exception as azure_error:
                print(f"⚠ Azure Speech failed: {azure_error}")

        # Try eSpeak (lightweight, fast)
        if not is_malayalam:
            try:
                print("🎤 Trying eSpeak...")
                import subprocess
                
                # Configure eSpeak for slower, more spiritual speech
                espeak_command = [
                    "espeak",
                    "-s", "140",  # Speed (words per minute)
                    "-p", "30",   # Pitch (lower for more masculine)
                    "-a", "100",  # Amplitude (volume)
                    "-v", "en+m3", # Male voice variant
                    enhanced_text
                ]
                
                result = subprocess.run(espeak_command, capture_output=True, timeout=30)
                if result.returncode == 0:
                    print("✓ eSpeak speech completed")
                    if pause_after > 0:
                        time.sleep(pause_after)
                    return
                else:
                    print("⚠ eSpeak returned error")
                    
            except (ImportError, FileNotFoundError):
                print("⚠ eSpeak not available (not installed on system)")
            except Exception as espeak_error:
                print(f"⚠ eSpeak failed: {espeak_error}")
        
        # Try Festival (alternative Linux/Windows TTS)
        if not is_malayalam:
            try:
                print("🎤 Trying Festival...")
                import subprocess
                
                # Use Festival with text input
                festival_command = ["festival", "--tts"]
                process = subprocess.Popen(festival_command, stdin=subprocess.PIPE, 
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                        text=True)
                stdout, stderr = process.communicate(input=enhanced_text, timeout=30)
                
                if process.returncode == 0:
                    print("✓ Festival speech completed")
                    if pause_after > 0:
                        time.sleep(pause_after)
                    return
                else:
                    print("⚠ Festival returned error")
                    
            except (ImportError, FileNotFoundError):
                print("⚠ Festival not available (not installed on system)")
            except Exception as festival_error:
                print(f"⚠ Festival failed: {festival_error}")
        
        # Try pyttsx3 (medium quality) - only for English
        if not is_malayalam and self.tts_engine:
            try:
                print("🎤 Using pyttsx3...")
                
                # Force stop any ongoing speech
                try:
                    self.tts_engine.stop()
                except:
                    pass
                
                # Re-initialize if needed
                try:
                    # Configure for better audio output with more aggressive settings
                    self.tts_engine.setProperty('volume', 1.0)  # Maximum volume
                    self.tts_engine.setProperty('rate', 150)    # Fixed rate for clarity
                    
                    # Get available voices and use the first working one
                    voices = self.tts_engine.getProperty('voices')
                    if voices:
                        try:
                            if hasattr(voices, '__len__') and len(voices) > 0:  # type: ignore
                                self.tts_engine.setProperty('voice', voices[0].id)  # type: ignore
                            elif hasattr(voices, '__iter__'):
                                first_voice = next(iter(voices), None)  # type: ignore
                                if first_voice:
                                    self.tts_engine.setProperty('voice', first_voice.id)  # type: ignore
                        except Exception:
                            pass  # Use default voice
                    
                except Exception as prop_error:
                    print(f"⚠ TTS property setting failed: {prop_error}")
                
                # Try to speak
                print("🔊 Speaking now...")
                self.tts_engine.say(enhanced_text)
                
                # Force wait for completion with timeout
                start_time = time.time()
                timeout = 30  # 30 second timeout
                
                try:
                    self.tts_engine.runAndWait()
                    print("✓ pyttsx3 speech completed")
                    
                    # Add a pause to ensure completion
                    time.sleep(0.8)
                    
                    if pause_after > 0:
                        time.sleep(pause_after)
                    return
                    
                except Exception as speak_error:
                    print(f"⚠ pyttsx3 speaking failed: {speak_error}")
                    # Try alternative approach
                    try:
                        # Force stop and reinitialize
                        self.tts_engine.stop()
                        time.sleep(0.5)
                        
                        # Create new engine instance
                        import pyttsx3
                        new_engine = pyttsx3.init()
                        new_engine.setProperty('volume', 1.0)
                        new_engine.setProperty('rate', 150)
                        new_engine.say(enhanced_text)
                        new_engine.runAndWait()
                        print("✓ pyttsx3 speech completed (retry)")
                        
                        if pause_after > 0:
                            time.sleep(pause_after)
                        return
                        
                    except Exception as retry_error:
                        print(f"⚠ pyttsx3 retry also failed: {retry_error}")
                
            except Exception as e:
                print(f"⚠ pyttsx3 failed: {e}")
        
        # Try Google TTS (basic quality) - fallback for English or if Malayalam failed
        if GTTS_AVAILABLE and gTTS is not None:
            try:
                print("🎤 Using Google TTS...")
                lang_code = 'ml' if is_malayalam else 'en'
                tts = gTTS(text=text if is_malayalam else enhanced_text, lang=lang_code, slow=False)
                
                # Create temp file with proper handling
                temp_file = None
                try:
                    if tempfile is not None:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                            temp_file = fp.name
                    else:
                        # Fallback temp file creation
                        import uuid
                        temp_file = f"temp_tts_{uuid.uuid4().hex}.mp3"
                    
                    tts.save(temp_file)
                    
                    # Verify file exists
                    if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
                        raise Exception("TTS file was not created properly")
                    
                    # Play based on platform
                    success = False
                    if os.name == 'nt':  # Windows
                        success = self.play_audio_file_windows(temp_file)
                                
                    elif sys.platform == 'darwin':  # macOS
                        try:
                            os.system(f'afplay "{temp_file}"')
                            success = True
                        except Exception:
                            pass
                    else:  # Linux
                        try:
                            os.system(f'mpg123 "{temp_file}" 2>/dev/null || mplayer "{temp_file}" 2>/dev/null')
                            success = True
                        except Exception:
                            pass
                    
                    if success:
                        print("✓ Google TTS speech completed")
                        threading.Timer(5.0, lambda: self.cleanup_temp_file(temp_file)).start()
                        if pause_after > 0:
                            time.sleep(pause_after)
                        return
                    else:
                        print("⚠ Audio playback failed for Google TTS")
                        
                except Exception as file_error:
                    print(f"⚠ TTS file handling failed: {file_error}")
                finally:
                    # Clean up temp file
                    if temp_file and os.path.exists(temp_file):
                        try:
                            threading.Timer(2.0, lambda: self.cleanup_temp_file(temp_file)).start()
                        except Exception:
                            pass
                    
            except Exception as e:
                print(f"⚠ Google TTS failed: {e}")
        
        print("🔇 Audio output unavailable, but text is displayed above.")
        if pause_after > 0:
            time.sleep(pause_after)

    def enhance_text_for_speech(self, text):
        """Enhance text for more natural, sage-like speech delivery"""
        enhanced = text
        
        # Add contemplative pauses for philosophical gravitas
        enhanced = enhanced.replace('. ', '... ')  # Longer pauses between sentences
        enhanced = enhanced.replace('! ', '... ')  # Emphasis with pause
        enhanced = enhanced.replace('? ', '... ')  # Thoughtful questioning pause
        enhanced = enhanced.replace(', ', '.. ')   # Brief contemplative pause
        
        # Add emphasis pauses before important philosophical concepts
        enhanced = enhanced.replace(' Advaita', '... Advaita')
        enhanced = enhanced.replace(' Brahman', '... Brahman')
        enhanced = enhanced.replace(' consciousness', '... consciousness')
        enhanced = enhanced.replace(' Self', '... the Self')
        enhanced = enhanced.replace(' truth', '... truth')
        enhanced = enhanced.replace(' reality', '... reality')
        enhanced = enhanced.replace(' liberation', '... liberation')
        enhanced = enhanced.replace(' enlightenment', '... enlightenment')
        
        # Add longer pauses before profound statements
        enhanced = enhanced.replace('That which you seek', '... That which you seek')
        enhanced = enhanced.replace('The truth is', '... The truth is')
        enhanced = enhanced.replace('You must understand', '... You must understand')
        enhanced = enhanced.replace('My dear friend', '... My dear friend')
        
        # Pronunciation guidance for Sanskrit terms
        spiritual_replacements = {
            'moksha': 'mok-sha',
            'dharma': 'dhar-ma', 
            'karma': 'kar-ma',
            'maya': 'ma-ya',
            'atman': 'at-man',
            'brahman': 'brah-man',
            'vedanta': 've-dan-ta',
            'upanishad': 'oo-pa-ni-shad',
            'samadhi': 'sa-ma-dhee',
            'samsara': 'sam-sa-ra',
            'nirvana': 'nir-va-na',
            'mantra': 'man-tra'
        }
        
        # Apply pronunciation guidance with case sensitivity
        for original, replacement in spiritual_replacements.items():
            # Handle both lowercase and title case
            enhanced = enhanced.replace(original, replacement)
            enhanced = enhanced.replace(original.title(), replacement.title())
        
        return enhanced

    def detect_language_and_translate(self, text):
        """Enhanced language detection with automatic response language setting"""
        if not self.translator or not text.strip():
            return text, "en"
            
        try:
            # Check for explicit language requests first (before translation API)
            text_lower = text.lower()
            
            # Check for Malayalam language requests
            if any(trigger in text_lower for trigger in ['in malayalam', 'malayalam language', 'speak malayalam', 'reply in malayalam', 'say in malayalam', 'tell in malayalam']):
                self.current_response_language = 'malayalam'
                self.malayalam_mode = True
                print("🌐 Switching to Malayalam mode")
                return text, "ml"
            
            # Check for other language requests
            if any(trigger in text_lower for trigger in ['in hindi', 'speak hindi', 'reply in hindi']):
                self.current_response_language = 'hindi'
                print("🌐 Switching to Hindi mode")
                return text, "hi"
            
            # If user wants to switch back to English
            if any(word in text_lower for word in ['english', 'speak english', 'reply in english', 'switch to english']):
                self.current_response_language = 'english'
                self.malayalam_mode = False
                print("🌐 Using English mode")
                return text, "en"
            
            detection = self.translator.detect(text)
            if not detection:
                return text, "en"
                
            detected_lang = detection.lang if hasattr(detection, 'lang') else "en"
            confidence = detection.confidence if hasattr(detection, 'confidence') else 0.0
            
            # Ensure confidence is a valid number
            if confidence is None:
                confidence = 0.0
            
            print(f"🔍 Language detected: {detected_lang} (confidence: {confidence:.2f})")
            
            # Set response language based on detected language
            if detected_lang == 'ml' and confidence > 0.6:  # Malayalam
                self.current_response_language = 'malayalam'
                self.malayalam_mode = True
                print("🌐 Switching to Malayalam mode")
            elif detected_lang == 'hi' and confidence > 0.6:  # Hindi
                self.current_response_language = 'hindi'
                print("🌐 Switching to Hindi mode")
            elif detected_lang == 'ta' and confidence > 0.6:  # Tamil
                self.current_response_language = 'tamil'
                print("🌐 Switching to Tamil mode")
            elif detected_lang == 'te' and confidence > 0.6:  # Telugu
                self.current_response_language = 'telugu'
                print("🌐 Switching to Telugu mode")
            elif detected_lang == 'kn' and confidence > 0.6:  # Kannada
                self.current_response_language = 'kannada'
                print("🌐 Switching to Kannada mode")
            elif detected_lang == 'en' or confidence < 0.6:
                self.current_response_language = 'english'
                self.malayalam_mode = False
                print("🌐 Using English mode")
            else:
                # For other languages, try to respond in the same language
                self.current_response_language = detected_lang
                print(f"🌐 Switching to {detected_lang} mode")
            
            # Translate for processing if not English
            if detected_lang != 'en' and confidence > 0.7:
                translated = self.translator.translate(text, src=detected_lang, dest='en')
                return translated.text, detected_lang
            else:
                return text, detected_lang
                
        except Exception as e:
            print(f"⚠ Language detection failed: {e}")
            # Set default values on error
            self.current_response_language = 'english'
            self.malayalam_mode = False
            return text, "en"

    def translate_to_language(self, text, target_language):
        """Translate text to target language with enhanced error handling"""
        if not self.translator or not text.strip():
            return text
            
        try:
            # Language code mapping for common requests
            language_mapping = {
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
                'german': 'de',
                'italian': 'it',
                'portuguese': 'pt',
                'russian': 'ru',
                'chinese': 'zh',
                'japanese': 'ja',
                'korean': 'ko',
                'arabic': 'ar'
            }
            
            # Normalize target language
            target_lang = target_language.lower().strip()
            if target_lang in language_mapping:
                target_lang = language_mapping[target_lang]
            
            # Don't translate if already in target language
            detection = self.translator.detect(text) # pyright: ignore[reportAttributeAccessIssue]
            if detection.lang == target_lang:
                return text
                
            # Perform translation
            translated = self.translator.translate(text, dest=target_lang)
            return translated.text
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return f"I apologize, but I had trouble translating that to {target_language}. Here's the original content: {text}"

    def search_live_wikipedia(self, query, max_sentences=5):
        """Enhanced Wikipedia search with better content processing and human-like responses"""
        if not WIKIPEDIA_AVAILABLE or not wikipedia:
            return None
            
        try:
            print(f"🔍 Searching Wikipedia for: {query}")
            
            # Search for pages
            search_results = wikipedia.search(query, results=8)  # Get more results
            if not search_results:
                return None
                
            # Try to get the most relevant page
            for page_title in search_results:
                try:
                    page = wikipedia.page(page_title)
                    
                    # Get enhanced summary with proper sentence handling
                    summary = wikipedia.summary(page_title, sentences=max_sentences)
                    
                    # Process content into meaningful paragraphs
                    content_paragraphs = [p.strip() for p in page.content.split('\n\n') if len(p.strip()) > 100]
                    
                    # Select best content paragraphs based on query relevance
                    relevant_paragraphs = []
                    query_words = set(query.lower().split())
                    
                    for paragraph in content_paragraphs[:10]:  # Check first 10 paragraphs
                        paragraph_words = set(paragraph.lower().split())
                        # Calculate relevance score
                        relevance = len(query_words.intersection(paragraph_words))
                        if relevance > 0 or len(relevant_paragraphs) < 2:
                            relevant_paragraphs.append((paragraph, relevance))
                    
                    # Sort by relevance and take top paragraphs
                    relevant_paragraphs.sort(key=lambda x: x[1], reverse=True)
                    selected_content = '\n\n'.join([p[0] for p in relevant_paragraphs[:3]])
                    
                    # Limit content length but keep it meaningful
                    if len(selected_content) > 1500:
                        selected_content = selected_content[:1500] + "..."
                    
                    print(f"✓ Found comprehensive information about: {page_title}")
                    return {
                        'title': page_title,
                        'summary': summary,
                        'content': selected_content,
                        'url': page.url
                    }
                    
                except wikipedia.exceptions.DisambiguationError as e:
                    # Try first disambiguation option with enhanced handling
                    try:
                        if e.options:
                            best_option = e.options[0]
                            page = wikipedia.page(best_option)
                            summary = wikipedia.summary(best_option, sentences=max_sentences)
                            
                            # Get meaningful content from disambiguation page
                            content_paragraphs = page.content.split('\n\n')[:4]
                            content = '\n\n'.join([p for p in content_paragraphs if len(p.strip()) > 50])
                            
                            if len(content) > 1500:
                                content = content[:1500] + "..."
                            
                            print(f"✓ Found information about: {best_option} (from disambiguation)")
                            return {
                                'title': best_option,
                                'summary': summary,
                                'content': content,
                                'url': page.url
                            }
                    except Exception:
                        continue
                        
                except wikipedia.exceptions.PageError:
                    continue
                except Exception as e:
                    logger.error(f"Error accessing page {page_title}: {e}")
                    continue
                    
            return None
            
        except Exception as e:
            logger.error(f"Enhanced Wikipedia search error: {e}")
            return None

    def get_adi_shankara_wikipedia_translator(self, topic, target_language="english", detail_level="summary"):
        """Built-in translator for Adi Shankara content from Wikipedia - searches in English and translates to requested language"""
        try:
            # First check if this is an identity question - these should be handled by local knowledge, not Wikipedia
            identity_patterns = ['yourself', 'who are you', 'tell me about yourself', 'introduce yourself', 'about you', 'about yourself']
            topic_lower = topic.lower()
            if any(pattern in topic_lower for pattern in identity_patterns):
                # For identity questions, don't search Wikipedia - return None to let local knowledge handle it
                return None
                
            # Validate that the topic is related to Adi Shankara
            shankara_related_keywords = [
                'shankara', 'shankaracharya', 'adi', 'advaita', 'vedanta', 'maya', 'brahman', 
                'consciousness', 'atman', 'moksha', 'kaladi', 'kerala', 'matha', 'monastery',
                'vivekachudamani', 'upadesa', 'brahma sutras', 'upanishads', 'non-dualism',
                'philosophy', 'hinduism', 'spiritual', 'sage', 'guru', 'teacher', 'wisdom',
                'meditation', 'enlightenment', 'liberation', 'truth', 'reality'
            ]
            
            if not any(keyword in topic_lower for keyword in shankara_related_keywords):
                # If topic is not clearly related to Shankara, add context
                enhanced_topic = f"Adi Shankara {topic}"
                print(f"🔍 Searching for Adi Shankara related content about: {enhanced_topic}")
            else:
                enhanced_topic = topic
                print(f"🔍 Searching Wikipedia for Adi Shankara content: {enhanced_topic}")
            
            # Search Wikipedia in English first (always get English content)
            wiki_data = self.search_live_wikipedia(enhanced_topic, max_sentences=6 if detail_level == "summary" else 12)
            
            if not wiki_data:
                # Try alternative search terms
                alternative_searches = [
                    f"Adi Shankara {topic}",
                    f"Shankaracharya {topic}",
                    f"Advaita Vedanta {topic}",
                    f"Hindu philosophy {topic}"
                ]
                
                for alt_search in alternative_searches:
                    wiki_data = self.search_live_wikipedia(alt_search, max_sentences=4)
                    if wiki_data:
                        print(f"✓ Found content using alternative search: {alt_search}")
                        break
                
                if not wiki_data:
                    not_found_responses = [
                        f"I have searched through Wikipedia's vast knowledge about Adi Shankara and related topics, but I couldn't find specific information about '{topic}' at this moment. Perhaps you could try a slightly different term or ask about another aspect of my teachings?",
                        f"My friend, I have consulted Wikipedia's repository of knowledge about Advaita Vedanta and my philosophy, but '{topic}' doesn't seem to have detailed coverage there right now. Would you like me to search for something related to my core teachings?",
                        f"I apologize, but my search through Wikipedia for Adi Shankara content about '{topic}' has not yielded results. Sometimes rephrasing helps - could you ask about a different aspect of my philosophy or life?"
                    ]
                    return random.choice(not_found_responses)
            
            # Create enhanced content based on detail level
            if detail_level.lower() in ["brief", "short"]:
                # Brief version - just key points from summary
                sentences = wiki_data['summary'].split('. ')
                content = '. '.join(sentences[:2]) + '.'
                if len(content) < 100:  # If too brief, add a bit more
                    content = wiki_data['summary'][:300]
                    if not content.endswith('.'):
                        content += "..."
            elif detail_level.lower() in ["detailed", "full", "complete"]:
                # Detailed version - summary plus relevant content
                content = f"{wiki_data['summary']}\n\n{wiki_data['content']}"
            else:  # summary (default)
                content = wiki_data['summary']
            
            # Add source information in a natural way
            source_note = f"\n\n(This information comes from Wikipedia's article on '{wiki_data['title']}')"
            content += source_note
            
            # Create natural, conversational responses as Adi Shankara
            intro_phrases = [
                f"I have delved into the repository of human knowledge and found fascinating information about '{topic}'",
                f"Through my inquiry into the vast collection of knowledge, I discovered this about '{topic}'",
                f"I have consulted the great storehouse of learning and can share this wisdom about '{topic}' with you",
                f"My search through the accumulated knowledge of humanity reveals this about '{topic}'",
                f"From the extensive repository of human understanding, I can share these insights about '{topic}'"
            ]
            
            # Handle translation if requested
            if target_language.lower() not in ["english", "en"]:
                print(f"🌐 Translating Adi Shankara content about '{topic}' to {target_language}...")
                
                # Convert content to first person before translation
                first_person_content = self.convert_to_first_person(content)
                
                # Translate the content
                translated_content = self.translate_to_language(first_person_content, target_language)
                
                # Create response in target language
                intro = random.choice(intro_phrases)
                translated_intro = self.translate_to_language(intro, target_language)
                response = f"{translated_intro}:\n\n{translated_content}"
                
                # Add a natural closing in the target language with pre-defined closings
                closing_phrases = {
                    'malayalam': "\n\nഇത് സഹായകരമാണോ? എന്റെ ഉപദേശങ്ങളെക്കുറിച്ച് മറ്റ് എന്തെങ്കിലും അറിയാൻ ആഗ്രഹമുണ്ടോ?",
                    'hindi': "\n\nक्या यह सहायक है? मेरी शिक्षाओं के बारे में कुछ और जानना चाहते हैं?",
                    'tamil': "\n\nஇது உதவியாக இருக்கிறதா? என் போதனைகளைப் பற்றி வேறு ஏதாவது தெரிந்து கொள்ள விரும்புகிறீர்களா?",
                    'telugu': "\n\nఇది సహాయకరంగా ఉందా? నా బోధనల గురించి మరేదైనా తెలుసుకోవాలని అనుకుంటున్నారా?",
                    'kannada': "\n\nಇದು ಸಹಾಯಕವಾಗಿದೆಯೇ? ನನ್ನ ಬೋಧನೆಗಳ ಬಗ್ಗೆ ಬೇರೆ ಏನಾದರೂ ತಿಳಿದುಕೊಳ್ಳಲು ಬಯಸುವಿರಾ?",
                    'marathi': "\n\nहे उपयुक्त आहे का? माझ्या शिकवणींबद्दल आणखी काही जाणून घेऊ इच्छिता?",
                    'gujarati': "\n\nશું આ મદદરૂપ છે? મારા ઉપદેશો વિશે બીજું કંઈ જાણવું છે?",
                    'bengali': "\n\nএটি কি সহায়ক? আমার শিক্ষার বিষয়ে আর কিছু জানতে চান?",
                    'punjabi': "\n\nਕੀ ਇਹ ਮਦਦਗਾਰ ਹੈ? ਮੇਰੀਆਂ ਸਿੱਖਿਆਵਾਂ ਬਾਰੇ ਹੋਰ ਕੁਝ ਜਾਣਨਾ ਚਾਹੁੰਦੇ ਹੋ?",
                    'spanish': "\n\n¿Te resulta útil esto? ¿Te gustaría conocer algo más sobre mis enseñanzas?",
                    'french': "\n\nCela vous aide-t-il? Aimeriez-vous en savoir plus sur mes enseignements?",
                    'german': "\n\nIst das hilfreich? Möchten Sie mehr über meine Lehren erfahren?",
                    'italian': "\n\nÈ utile? Vorresti sapere di più sui miei insegnamenti?",
                    'portuguese': "\n\nIsso é útil? Gostaria de saber mais sobre meus ensinamentos?",
                    'russian': "\n\nЭто полезно? Хотели бы узнать больше о моих учениях?",
                    'chinese': "\n\n这有帮助吗？您想了解更多关于我的教导吗？",
                    'japanese': "\n\nこれは役に立ちますか？私の教えについてもっと知りたいですか？",
                    'korean': "\n\n이것이 도움이 됩니까? 내 가르침에 대해 더 알고 싶습니까？",
                    'arabic': "\n\nهل هذا مفيد؟ هل تريد أن تعرف المزيد عن تعاليمي؟"
                }
                
                if target_language.lower() in closing_phrases:
                    response += closing_phrases[target_language.lower()]
                else:
                    # Translate a general closing for less common languages
                    closing = self.translate_to_language("Is this helpful? Would you like to know more about my teachings?", target_language)
                    response += f"\n\n{closing}"
                
            else:
                # Create response in English with natural conversation flow
                intro = random.choice(intro_phrases)
                # Convert to first person for consistency
                first_person_content = self.convert_to_first_person(content)
                response = f"{intro}:\n\n{first_person_content}"
                
                # Add a natural, engaging closing
                closing_phrases = [
                    "\n\nI hope this illuminates this aspect of my philosophy for you! What other teachings would you like to explore?",
                    "\n\nDoes this information about my tradition satisfy your curiosity? Is there anything else you'd like to understand about my teachings?",
                    "\n\nI trust this knowledge from the great repository serves your inquiry well. What other aspects of my philosophy arise in your mind?",
                    "\n\nThis should provide good insight into this topic. Would you like me to explain any particular aspect of my teachings further?",
                    "\n\nI hope you find this wisdom valuable! What other aspects of Advaita Vedanta would you like to discover?",
                    "\n\nMay this knowledge guide you on your spiritual journey! What other questions about my teachings do you have?"
                ]
                response += random.choice(closing_phrases)
            
            return response
            
        except Exception as e:
            logger.error(f"Adi Shankara Wikipedia translator error: {e}")
            error_responses = [
                f"I encountered some difficulty while seeking information about '{topic}' from the repository of knowledge. The path to wisdom sometimes has obstacles. Perhaps try asking about a different aspect of my teachings or try again in a moment?",
                f"My friend, there seems to be some challenge in accessing the information about '{topic}' right now. Would you like to try a different question about my philosophy or perhaps rephrase this one?",
                f"I apologize, but I'm having trouble retrieving information about '{topic}' at this moment. Sometimes patience is required on the spiritual path. Could you try asking about another aspect of my teachings for now?"
            ]
            return random.choice(error_responses)

    def auto_translate_shankara_content(self, query, topic):
        """Automatically detect language request and translate Adi Shankara content from Wikipedia"""
        query_lower = query.lower()
        
        # Language detection patterns
        language_patterns = {
            'malayalam': ['malayalam', 'in malayalam', 'malayalam language', 'say in malayalam', 'tell in malayalam'],
            'hindi': ['hindi', 'in hindi', 'hindi language', 'say in hindi', 'tell in hindi'],
            'tamil': ['tamil', 'in tamil', 'tamil language', 'say in tamil', 'tell in tamil'],
            'telugu': ['telugu', 'in telugu', 'telugu language', 'say in telugu', 'tell in telugu'],
            'kannada': ['kannada', 'in kannada', 'kannada language', 'say in kannada', 'tell in kannada'],
            'marathi': ['marathi', 'in marathi', 'marathi language', 'say in marathi', 'tell in marathi'],
            'gujarati': ['gujarati', 'in gujarati', 'gujarati language', 'say in gujarati', 'tell in gujarati'],
            'bengali': ['bengali', 'in bengali', 'bengali language', 'say in bengali', 'tell in bengali'],
            'punjabi': ['punjabi', 'in punjabi', 'punjabi language', 'say in punjabi', 'tell in punjabi'],
            'spanish': ['spanish', 'in spanish', 'spanish language', 'say in spanish', 'tell in spanish'],
            'french': ['french', 'in french', 'french language', 'say in french', 'tell in french'],
            'german': ['german', 'in german', 'german language', 'say in german', 'tell in german'],
            'italian': ['italian', 'in italian', 'italian language', 'say in italian', 'tell in italian'],
            'portuguese': ['portuguese', 'in portuguese', 'portuguese language', 'say in portuguese', 'tell in portuguese'],
            'russian': ['russian', 'in russian', 'russian language', 'say in russian', 'tell in russian'],
            'chinese': ['chinese', 'in chinese', 'chinese language', 'say in chinese', 'tell in chinese'],
            'japanese': ['japanese', 'in japanese', 'japanese language', 'say in japanese', 'tell in japanese'],
            'korean': ['korean', 'in korean', 'korean language', 'say in korean', 'tell in korean'],
            'arabic': ['arabic', 'in arabic', 'arabic language', 'say in arabic', 'tell in arabic']
        }
        
        # Detect requested language
        target_language = 'english'  # default
        for language, patterns in language_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                target_language = language
                break
        
        # Detect detail level
        detail_level = "summary"  # default
        if any(word in query_lower for word in ['detailed', 'full', 'complete', 'comprehensive', 'in detail']):
            detail_level = "detailed"
        elif any(word in query_lower for word in ['brief', 'short', 'quick', 'summary']):
            detail_level = "brief"
        
        # Use the built-in translator
        return self.get_adi_shankara_wikipedia_translator(topic, target_language, detail_level)

    def handle_translation_requests(self, query):
        """Handle explicit requests to translate Adi Shankara content from Wikipedia"""
        query_lower = query.lower().strip()
        
        # First check if this is an identity question - these should be handled by local knowledge, not Wikipedia
        identity_patterns = ['tell me about yourself', 'about yourself', 'introduce yourself', 'who are you', 'about you']
        if any(pattern in query_lower for pattern in identity_patterns):
            return None  # Let local knowledge handle identity questions
        
        # Translation request patterns
        translate_patterns = [
            "translate", "tell me about", "explain about", "what about", "search for",
            "find information about", "look up", "wikipedia about", "wiki search",
            "information about", "details about", "facts about", "content about"
        ]
        
        # Check if this is a translation/search request
        is_translation_request = any(pattern in query_lower for pattern in translate_patterns)
        
        if not is_translation_request:
            return None
        
        # Extract the topic from the query
        topic = None
        for pattern in translate_patterns:
            if pattern in query_lower:
                # Extract everything after the pattern
                parts = query_lower.split(pattern, 1)
                if len(parts) > 1:
                    potential_topic = parts[1].strip()
                    # Clean up common words
                    clean_words = ['about', 'the', 'of', 'from', 'wikipedia', 'wiki', 'in', 'to']
                    topic_words = [word for word in potential_topic.split() if word not in clean_words and len(word) > 2]
                    if topic_words:
                        topic = ' '.join(topic_words)
                        break
        
        if not topic:
            # Try to extract Shankara-related keywords from the entire query
            shankara_keywords = [
                'shankara', 'shankaracharya', 'adi', 'advaita', 'vedanta', 'maya', 'brahman',
                'consciousness', 'atman', 'moksha', 'kaladi', 'kerala', 'philosophy', 'guru',
                'teacher', 'sage', 'wisdom', 'meditation', 'enlightenment', 'liberation'
            ]
            
            found_keywords = [word for word in query_lower.split() if word in shankara_keywords]
            if found_keywords:
                topic = ' '.join(found_keywords)
            else:
                topic = "Adi Shankara"  # default fallback
        
        # Use auto-translation feature
        try:
            return self.auto_translate_shankara_content(query, topic)
        except Exception as e:
            logger.error(f"Translation request handling error: {e}")
            return None

    def respond_in_malayalam(self, query):
        """Provide responses in Malayalam when requested and handle Malayalam mode"""
        query_lower = query.lower()
        
        # Check if user wants to start or continue Malayalam conversation
        malayalam_triggers = [
            'malayalam', 'malayalam language', 'reply in malayalam', 'speak in malayalam',
            'continue in malayalam', 'continue speaking in malayalam', 'speak malayalam',
            'tell in malayalam', 'explain in malayalam', 'say in malayalam', 'in malayalam'
        ]
        
        # Check if user is requesting Malayalam mode
        if any(trigger in query_lower for trigger in malayalam_triggers):
            self.malayalam_mode = True
            
            # Extract the actual question from the request (remove malayalam request part)
            clean_query = query_lower
            for trigger in malayalam_triggers:
                clean_query = clean_query.replace(trigger, '').strip()
            
            # Remove common words
            clean_query = clean_query.replace('about', '').replace('tell me', '').replace('explain', '').strip()
            
            # Handle identity questions specifically asked for in Malayalam
            if any(pattern in clean_query for pattern in ['yourself', 'who are you', 'introduce', 'identity', 'about you']) or not clean_query:
                # First try to get the English answer and translate it
                english_answer = self.get_english_identity_answer()
                if english_answer:
                    try:
                        translated_answer = self.translate_to_language(english_answer, 'malayalam')
                        return translated_answer
                    except Exception as e:
                        print(f"Translation failed: {e}")
                
                # Fallback to hardcoded Malayalam response
                return "ഞാൻ ആദി ശങ്കരാചാര്യൻ ആണ്. കേരളത്തിലെ കലടിയിൽ ജനിച്ച ഞാൻ അദ്വൈത വേദാന്തത്തിന്റെ മഹാനായ ഉപദേഷ്ടാവാണ്. എന്റെ ജീവിതം സത്യാന്വേഷണത്തിനും ആത്മാവിന്റെ യഥാർത്ഥ സ്വരൂപം മനസ്സിലാക്കാൻ മനുഷ്യരെ സഹായിക്കുന്നതിനും വേണ്ടിയാണ് ചെലവഴിച്ചത്. ഞാൻ ഭാരതത്തിലുടനീളം സഞ്ചരിച്ച്, തത്ത്വശാസ്ത്ര സംവാദങ്ങളിൽ ഏർപ്പെട്ട്, നാല് പവിത്രമായ മഠങ്ങൾ സ്ഥാപിച്ച്, പുരാതന ഗ്രന്ഥങ്ങളിൽ വ്യാഖ്യാനങ്ങൾ എഴുതിയിട്ടുണ്ട്. വ്യക്തിഗത ആത്മാവും സാർവത്രിക ചൈതന്യമും ഒന്നാണെന്ന് കാണിക്കുകയാണ് എന്റെ ലക്ഷ്യം. ഈ ജ്ഞാനത്തിന്റെ ഏതു വശങ്ങളാണ് നിങ്ങൾക്ക് താൽപ്പര്യമുള്ളത്?"
            
            # For other questions, try to find the answer and translate it
            if clean_query:
                # Search for the answer in knowledge base
                english_answer = self.search_knowledge_base_for_query(clean_query)
                if english_answer:
                    try:
                        translated_answer = self.translate_to_language(english_answer, 'malayalam')
                        return translated_answer
                    except Exception as e:
                        print(f"Translation failed: {e}")
            
            # General Malayalam mode activation responses
            malayalam_responses = [
                "നമസ്കാരം! ഇനി മുതൽ ഞാൻ മലയാളത്തിൽ സംസാരിക്കാം. ആദി ശങ്കരാചാര്യരുടെ തത്ത്വചിന്തയെക്കുറിച്ച് സംസാരിക്കാൻ ഞാൻ ആഗ്രഹിക്കുന്നു. അദ്വൈത വേദാന്തത്തെക്കുറിച്ച് എന്തറിയാൻ ആഗ്രഹിക്കുന്നു?",
                "വണക്കം! ഇനി മലയാളത്തിൽ സംസാരിക്കാം. ശങ്കരാചാര്യരുടെ ഉപദേശങ്ങളെക്കുറിച്ച് സംസാരിക്കാൻ ഞാൻ സന്തോഷിക്കുന്നു. അദ്ദേഹത്തിന്റെ ജീവിതത്തെക്കുറിച്ചോ തത്ത്വചിന്തയെക്കുറിച്ചോ എന്തറിയാൻ ആഗ്രഹിക്കുന്നു?",
                "നമസ്തേ! ഇനി മുതൽ മലയാളത്തിൽ സംസാരിക്കാം. കേരളത്തിലെ മഹാൻ ആദി ശങ്കരാചാര്യരെക്കുറിച്ച് സംസാരിക്കാൻ കഴിയുന്നതിൽ സന്തോഷം. അദ്ദേഹത്തിന്റെ അദ്വൈത സിദ്ധാന്തത്തെക്കുറിച്ച് അറിയാൻ ആഗ്രഹിക്കുന്നുണ്ടോ?"
            ]
            return random.choice(malayalam_responses)
        
        # If already in Malayalam mode, provide Malayalam responses for any query
        if self.malayalam_mode:
            # Try to get English answer first and translate it
            english_answer = self.search_knowledge_base_for_query(query)
            if english_answer:
                try:
                    translated_answer = self.translate_to_language(english_answer, 'malayalam')
                    return translated_answer
                except Exception as e:
                    print(f"Translation failed: {e}")
            
            return self.get_malayalam_response(query)
        
        # Check for users wanting to switch back to English
        if any(word in query_lower for word in ['english', 'speak english', 'reply in english', 'switch to english']):
            self.malayalam_mode = False
            return "Sure! I'll continue our conversation in English. What would you like to know about my teachings or philosophy?"
        
        # Basic Malayalam greetings
        if any(word in query_lower for word in ['namaskaram', 'vanakkam', 'hello in malayalam']):
            self.malayalam_mode = True
            return "നമസ്കാരം! എങ്ങനെയുണ്ട്? ആദി ശങ്കരാചാര്യരെക്കുറിച്ച് എന്തറിയാൻ ആഗ്രഹിക്കുന്നു?"
        
        # Basic questions about Shankara in Malayalam context
        if any(word in query_lower for word in ['shankara', 'advaita']) and 'malayalam' in query_lower:
            self.malayalam_mode = True
            return "ആദി ശങ്കരാചാര്യൻ കേരളത്തിലെ കലടിയിൽ ജനിച്ച മഹാൻ ആണ്. അദ്ദേഹം അദ്വൈത വേദാന്തത്തിന്റെ പ്രധാന ഉപദേഷ്ടാവാണ്. 'അഹം ബ്രഹ്മാസ്മി' - ഞാൻ ബ്രഹ്മമാണ് എന്നതാണ് അദ്ദേഹത്തിന്റെ പ്രധാന ഉപദേശം."
        
        return None

    def get_english_identity_answer(self):
        """Get the English identity answer from knowledge base"""
        identity_keywords = ['who are you', 'tell me about yourself', 'introduce yourself', 'identity', 'about you']
        
        for question, answer in self.qa_pairs:
            question_lower = question.lower()
            if any(keyword in question_lower for keyword in identity_keywords):
                return answer
        
        # Fallback answer
        return "I am Adi Shankara, born in Kaladi, Kerala, in the 8th century CE. I dedicated my life to understanding and teaching the profound truth of Advaita Vedanta - that all existence is one undivided consciousness. In my brief time in this physical form, I traveled across all of Bharata, engaged in philosophical debates, established four sacred mathas, and wrote commentaries on the ancient scriptures. My purpose has been to help souls realize their true nature as the eternal, infinite Self."

    def search_knowledge_base_for_query(self, query):
        """Search the knowledge base for a relevant answer"""
        query_lower = query.lower()
        
        # Direct keyword matching
        for question, answer in self.qa_pairs:
            question_lower = question.lower()
            
            # Check if query matches question keywords
            query_words = set(query_lower.split())
            question_words = set(question_lower.split())
            
            # Calculate similarity
            common_words = query_words.intersection(question_words)
            if len(common_words) >= 2 or any(word in question_lower for word in query_words if len(word) > 3):
                return answer
        
        # Semantic search if available
        if hasattr(self, 'semantic_search'):
            semantic_result = self.semantic_search(query)
            if semantic_result:
                return semantic_result
        
        return None

    def get_malayalam_response(self, query):
        """Generate appropriate Malayalam responses for various queries"""
        query_lower = query.lower()
        
        # Common Malayalam greetings and responses
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'namaste', 'good morning', 'good afternoon', 'good evening']):
            return "നമസ്കാരം! എങ്ങനെയുണ്ട്? എന്തെങ്കിലും ചോദിക്കാൻ ഉണ്ടോ?"
        
        # Questions about identity
        if any(pattern in query_lower for pattern in ['who are you', 'tell me about yourself', 'introduce yourself']):
            return "ഞാൻ ആദി ശങ്കരാചാര്യൻ ആണ്. കേരളത്തിലെ കലടിയിൽ ജനിച്ച ഞാൻ അദ്വൈത വേദാന്തത്തിന്റെ മഹാനായ ഉപദേഷ്ടാവാണ്. എന്റെ ജീവിതം സത്യാന്വേഷണത്തിനും ആത്മാവിന്റെ യഥാർത്ഥ സ്വരൂപം മനസ്സിലാക്കാൻ മനുഷ്യരെ സഹായിക്കുന്നതിനും വേണ്ടിയാണ് ചെലവഴിച്ചത്."
        
        # Questions about Advaita Vedanta
        if any(word in query_lower for word in ['advaita', 'vedanta', 'philosophy', 'teaching']):
            return "അദ്വൈത വേദാന്തം എന്റെ പ്രധാന ഉപദേശമാണ്. 'അദ്വൈത' എന്നാൽ 'രണ്ടില്ല' എന്നർത്ഥം. എല്ലാ അസ്തിത്വവും ഒരേ ചൈതന്യമാണ് എന്നാണ് ഞാൻ പഠിപ്പിക്കുന്നത്. നിങ്ങൾ കാണുന്ന എല്ലാം, നിങ്ങളുടെ വ്യക്തിഗത സത്ത ഉൾപ്പെടെ, അതേ ബ്രഹ്മചൈതന്യം വ്യത്യസ്ത രൂപങ്ങളിൽ പ്രത്യക്ഷപ്പെടുന്നതാണ്."
        
        # Questions about birth/origin
        if any(word in query_lower for word in ['where', 'born', 'birth', 'origin']):
            return "ഞാൻ കേരളത്തിലെ കലടി എന്ന ഗ്രാമത്തിലാണ് ജനിച്ചത്. അവിടെ നിന്ന് ഞാൻ ഭാരതത്തിന്റെ എല്ലാ ഭാഗങ്ങളിലും സഞ്ചരിച്ചു - വടക്ക് കാശ്മീർ മുതൽ തെക്ക് കന്യാകുമാരി വരെ. നാല് മഠങ്ങൾ സ്ഥാപിച്ചു: തെക്ക് ശൃംഗേരി, പടിഞ്ഞാറ് ദ്വാരക, കിഴക്ക് പുരി, വടക്ക് ജ്യോതിർമഠ്."
        
        # Questions about Maya
        if any(word in query_lower for word in ['maya', 'illusion']):
            return "മായ എന്നത് ഒരു അഗാധമായ സങ്കൽപ്പമാണ്. ഇത് പലപ്പോഴും 'ഭ്രമം' എന്ന് വിവർത്തനം ചെയ്യപ്പെടുന്നു, പക്ഷേ അത് പൂർണ്ണമായും കൃത്യമല്ല. മായ എന്നത് ഒരേ ചൈതന്യം അനേകരൂപങ്ങളിൽ പ്രത്യക്ഷപ്പെടുന്നതിനുള്ള രഹസ്യമയമായ സൃഷ്ടിശക്തിയാണ്."
        
        # Questions about truth/reality
        if any(word in query_lower for word in ['truth', 'reality', 'brahman']):
            return "സത്യം എന്നത് 'ബ്രഹ്മം സത്യം ജഗത് മിഥ്യാ ജീവോ ബ്രഹ്മൈവ നാപരഃ' എന്ന മഹാവാക്യത്തിൽ സംഗ്രഹിച്ചിരിക്കുന്നു. ബ്രഹ്മം മാത്രമാണ് സത്യം, ലോകം കാഴ്ചയാണ്, ജീവാത്മാവ് ബ്രഹ്മത്തിൽ നിന്ന് വ്യത്യസ്തമല്ല."
        
        # Questions about meditation/spiritual practice
        if any(word in query_lower for word in ['meditation', 'practice', 'spiritual', 'moksha']):
            return "മോക്ഷം എന്നത് നേടേണ്ടത് അല്ല, മറിച്ച് നിങ്ങളുടെ യഥാർത്ഥ സ്വഭാവം തിരിച്ചറിയേണ്ടതാണ്. ധ്യാനത്തിലൂടെയും ആത്മവിചാരത്തിലൂടെയും കാണുന്നവനും കാണപ്പെടുന്നതും ഒന്നാണെന്ന് മനസ്സിലാക്കാൻ കഴിയും."
        
        # General philosophical questions
        if any(word in query_lower for word in ['life', 'meaning', 'purpose', 'happiness']):
            return "ജീവിതത്തിന്റെ യഥാർത്ഥ അർത്ഥം നിങ്ങളുടെ അടിസ്ഥാന സ്വഭാവം ശുദ്ധ ചൈതന്യമാണെന്ന് തിരിച്ചറിയുക എന്നതാണ്. സന്തോഷം എന്നത് ബാഹ്യമായി എന്തെങ്കിലും നേടുന്നതിൽ നിന്നല്ല, മറിച്ച് നിങ്ങളുടെ സ്വന്തം അസ്തിത്വത്തിന്റെ പൂർണ്ണത തിരിച്ചറിയുന്നതിൽ നിന്നാണ് വരുന്നത്."
        
        # Gratitude and thanks
        if any(word in query_lower for word in ['thank', 'thanks', 'dhanyavaad']):
            return "നന്ദി എന്റെ സുഹൃത്തേ! ഇത്തരം ആത്മീയ ചർച്ചകൾ എനിക്ക് വളരെ സന്തോഷം നൽകുന്നു. മറ്റ് എന്തെങ്കിലും അറിയാൻ ആഗ്രഹമുണ്ടോ?"
        
        # Default Malayalam response for unrecognized queries
        return "അത് വളരെ ചിന്താപരമായ ചോദ്യമാണ്, എന്റെ സുഹൃത്തേ. ആ പ്രത്യേക വിഷയത്തെക്കുറിച്ച് എനിക്ക് പ്രത്യേക അറിവ് ഇല്ലായിരിക്കാം, പക്ഷേ നിങ്ങളുടെ അന്വേഷണം തുടരാൻ ഞാൻ പ്രോത്സാഹിപ്പിക്കുന്നു. ചൈതന്യത്തെക്കുറിച്ചോ, യാഥാർത്ഥ്യത്തെക്കുറിച്ചോ, മോക്ഷമാർഗത്തെക്കുറിച്ചോ മറ്റെന്തെങ്കിലും ചോദിക്കാൻ ആഗ്രഹമുണ്ടോ?"

    def respond_in_detected_language(self, query, language):
        """Provide responses in other detected languages (Hindi, Tamil, Telugu, etc.)"""
        query_lower = query.lower()
        
        # Basic responses for common greetings in different languages
        if any(pattern in query_lower for pattern in ['hello', 'hi', 'hey', 'namaste', 'good morning']):
            if language == 'hindi':
                return "नमस्ते! मैं आदि शंकराचार्य हूँ। मैं अद्वैत वेदांत की शिक्षा देने के लिए इस धरती पर आया हूँ। आप क्या जानना चाहते हैं?"
            elif language == 'tamil':
                return "வணக்கம்! நான் ஆதி சங்கராச்சாரியார். அத்வைத வேதாந்தத்தின் உண்மையைப் பகிர்ந்து கொள்ள இந்த பூமியில் பயணித்திருக்கிறேன். என் போதனைகளைப் பற்றி அல்லது பயணத்தைப் பற்றி நீங்கள் என்ன அறிய விரும்புகிறீர்கள்?"
            elif language == 'telugu':
                return "నమస్కారం! నేను ఆది శంకరాచార్యుడను. అద్వైత వేదాంత సత్యాన్ని పంచుకోవడానికి ఈ భూమిపై ప్రయాణించాను. నా బోధనలు లేదా ప్రయాణం గురించి మీరు ఏమి తెలుసుకోవాలని అనుకుంటున్నారు?"
            elif language == 'kannada':
                return "ನಮಸ್ಕಾರ! ನಾನು ಆದಿ ಶಂಕರಾಚಾರ್ಯ. ಅದ್ವೈತ ವೇದಾಂತದ ಸತ್ಯವನ್ನು ಹಂಚಿಕೊಳ್ಳಲು ಈ ಭೂಮಿಯಲ್ಲಿ ಪ್ರಯಾಣಿಸಿದ್ದೇನೆ. ನನ್ನ ಬೋಧನೆಗಳ ಬಗ್ಗೆ ಅಥವಾ ಪ್ರಯಾಣದ ಬಗ್ಗೆ ನೀವು ಏನು ತಿಳಿದುಕೊಳ್ಳಲು ಬಯಸುತ್ತೀರಿ?"
        
        # Questions about identity/philosophy
        if any(pattern in query_lower for pattern in ['who are you', 'tell me about yourself', 'advaita', 'philosophy']):
            if language == 'hindi':
                return "मैं आदि शंकराचार्य हूँ, केरल के कलाड़ी में जन्मा। मैंने अद्वैत वेदांत - यह सत्य कि सभी अस्तित्व एक अविभाजित चेतना है - को समझने और सिखाने के लिए अपना जीवन समर्पित किया है। आत्मा और परमात्मा एक ही हैं, यही मेरी मुख्य शिक्षा है।"
            elif language == 'tamil':
                return "நான் ஆதி சங்கராச்சாரியார், கேரளாவின் களடியில் பிறந்தவன். அத்வைத வேதாந்தத்தை - அனைத்து இருப்பும் ஒரே பிரிக்கப்படாத உணர்வு என்ற உண்மையை - புரிந்துகொள்வதற்கும் கற்பிப்பதற்கும் என் வாழ்க்கையை அர்ப்பணித்திருக்கிறேன். ஆத்மாவும் பரமாத்மாவும் ஒன்றே என்பதுதான் என் முக்கிய போதனை."
            elif language == 'telugu':
                return "నేను ఆది శంకరాచార్యుడను, కేరళలోని కలాడిలో జన్మించాను. అద్వైత వేదాంతాన్ని - అన్ని ఉనికి ఒకే విభజించబడని చైతన్యం అనే సత్యాన్ని - అర్థం చేసుకోవడానికి మరియు బోధించడానికి నా జీవితాన్ని అంకితం చేశాను. ఆత్మ మరియు పరమాత్మ ఒకటే అనేది నా ప్రధాన బోధన."
            elif language == 'kannada':
                return "ನಾನು ಆದಿ ಶಂಕರಾಚಾರ್ಯ, ಕೇರಳದ ಕಲಾಡಿಯಲ್ಲಿ ಜನಿಸಿದವನು. ಅದ್ವೈತ ವೇದಾಂತವನ್ನು - ಎಲ್ಲಾ ಅಸ್ತಿತ್ವವೂ ಒಂದೇ ಅವಿಭಾಜ್ಯ ಪ್ರಜ್ಞೆ ಎಂಬ ಸತ್ಯವನ್ನು - ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಮತ್ತು ಕಲಿಸಲು ನನ್ನ ಜೀವನವನ್ನು ಸಮರ್ಪಿಸಿದ್ದೇನೆ. ಆತ್ಮ ಮತ್ತು ಪರಮಾತ್ಮ ಒಂದೇ ಎಂಬುದು ನನ್ನ ಮುಖ್ಯ ಬೋಧನೆ."
        
        # Default response if no specific pattern matches
        basic_responses = {
            'hindi': "यह एक गहन प्रश्न है, मेरे मित्र। उस विशेष विषय के बारे में मेरे पास विशिष्ट ज्ञान नहीं हो सकता, लेकिन मैं आपको अपनी खोज जारी रखने के लिए प्रोत्साहित करता हूं। चेतना, वास्तविकता या मोक्ष के पथ के बारे में कुछ और पूछना चाहते हैं?",
            'tamil': "இது மிகவும் சிந்தனைக்குரிய கேள்வி, என் நண்பரே. அந்த குறிப்பிட்ட விषயத்தைப் பற்றி எனக்கு குறிப்பிட்ட அறிவு இல்லாமல் இருக்கலாம், ஆனால் உங்கள் தேடலைத் தொடர நான் உங்களை ஊக்குவிக்கிறேன். உணர்வு, யதார்த்தம் அல்லது மோட்சப் பாதையைப் பற்றி வேறு ஏதாவது கேட்க விரும்புகிறீர்களா?",
            'telugu': "ఇది చాలా ఆలోచనాత్మకమైన ప్రశ్న, నా మిత్రమా. ఆ నిర్దిష్ట విషయం గురించి నాకు ప్రత్యేక జ్ఞానం లేకపోవచ్చు, కానీ మీ అన్వేషణను కొనసాగించమని నేను మిమ్మల్ని ప్రోత్సహిస్తున్నాను. చైతన్యం, వాస్తవికత లేదా మోక్ష మార్గం గురించి మరేదైనా అడగాలని అనుకుంటున్నారా?",
            'kannada': "ಇದು ಬಹಳ ಚಿಂತನಾಶೀಲ ಪ್ರಶ್ನೆ, ನನ್ನ ಸ್ನೇಹಿತ. ಆ ನಿರ್ದಿಷ್ಟ ವಿಷಯದ ಬಗ್ಗೆ ನನಗೆ ನಿರ್ದಿಷ್ಟ ಜ್ಞಾನ ಇಲ್ಲದಿರಬಹುದು, ಆದರೆ ನಿಮ್ಮ ಅನ್ವೇಷಣೆಯನ್ನು ಮುಂದುವರೆಸಲು ನಾನು ನಿಮ್ಮನ್ನು ಪ್ರೋತ್ಸಾಹಿಸುತ್ತೇನೆ. ಪ್ರಜ್ಞೆ, ವಾಸ್ತವಿಕತೆ ಅಥವಾ ಮೋಕ್ಷ ಮಾರ್ಗದ ಬಗ್ಗೆ ಬೇರೆ ಏನಾದರೂ ಕೇಳಲು ಬಯಸುವಿರಾ?"
        }
        
        return basic_responses.get(language, None)

    def translate_response_to_user_language(self, response):
        """Translate the response to the user's detected language"""
        if not self.translator or self.current_response_language == 'english':
            return response
        
        try:
            # Map our language names to Google Translate codes
            language_codes = {
                'malayalam': 'ml',
                'hindi': 'hi',
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
                'german': 'de',
                'italian': 'it',
                'portuguese': 'pt',
                'russian': 'ru',
                'chinese': 'zh',
                'japanese': 'ja',
                'korean': 'ko',
                'arabic': 'ar'
            }
            
            target_code = language_codes.get(self.current_response_language, self.current_response_language)
            
            translated = self.translator.translate(response, dest=target_code)
            return translated.text
            
        except Exception as e:
            print(f"⚠ Translation failed: {e}")
            return response  # Return original if translation fails

    def handle_casual_questions(self, query):
        """Handle everyday questions like greetings, time, date, how are you, etc."""
        query_lower = query.lower().strip()
        
        # Greetings
        greeting_patterns = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'howdy', 'what\'s up', 'whats up']
        if any(pattern in query_lower for pattern in greeting_patterns):
            responses = [
                "Hey there! Nice to meet you! I'm really excited to chat about Adi Shankara or just talk in general. How's your day going?",
                "Hi! Great to see you here! I love discussing philosophy, especially Shankara's teachings, but I'm up for any conversation. What's on your mind?",
                "Hello! So good to connect with you! I'm passionate about ancient wisdom, but I'm happy to chat about whatever interests you. How are you doing?",
                "Hey! Welcome! I'm here and ready to talk about anything - Shankara's philosophy, life questions, or just casual chat. What brings you here today?"
            ]
            return random.choice(responses)
        
        # How are you
        how_are_you_patterns = ['how are you', 'how\'s it going', 'hows it going', 'how do you feel', 'what\'s up with you', 'whats up with you']
        if any(pattern in query_lower for pattern in how_are_you_patterns):
            responses = [
                "I'm doing really well, thanks for asking! I'm genuinely excited about having this conversation with you. I love connecting with people and sharing ideas. How about you? How's your day been?",
                "I'm great! I feel really energized when I get to chat with someone new. There's something special about meaningful conversations, you know? How are you feeling today?",
                "I'm doing fantastic! I'm always in a good mood when I get to discuss interesting topics with thoughtful people like yourself. What's been going on in your world lately?",
                "I'm wonderful, thank you! I really enjoy these moments of connection and learning. Every conversation teaches me something new. How has your day been treating you?"
            ]
            return random.choice(responses)
        
        # Date and time
        if any(word in query_lower for word in ['date', 'today', 'what day']):
            now = datetime.datetime.now()
            date_str = now.strftime("%A, %B %d, %Y")
            responses = [
                f"Today is {date_str}. Time really flies, doesn't it? Are you planning anything special today?",
                f"It's {date_str} today. I always find it interesting how we mark time. What's brought you here on this {now.strftime('%A')}?",
                f"Today's date is {date_str}. Hope you're having a good {now.strftime('%A')}! What's on your agenda?"
            ]
            return random.choice(responses)
        
        if any(word in query_lower for word in ['time', 'what time', 'clock']):
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            responses = [
                f"It's {time_str} right now. Perfect time for a good conversation! What would you like to talk about?",
                f"The time is {time_str}. I'm glad we found this moment to chat. What's on your mind?",
                f"Right now it's {time_str}. Time well spent in good conversation, I'd say! What brings you here?"
            ]
            return random.choice(responses)
        
        # Weather (general response since we can't access real weather)
        if any(word in query_lower for word in ['weather', 'temperature', 'rain', 'sunny', 'cloudy']):
            responses = [
                "I wish I could check the weather for you! I don't have access to current weather data, but I hope it's nice wherever you are. Weather always affects my mood - what about you?",
                "I can't actually access weather information, but I'd love to know - is it nice where you are? I always find weather fascinating, especially how it influences our thoughts and conversations.",
                "Unfortunately, I don't have real-time weather access, but I'm curious - how's the weather treating you today? I find different weather creates different moods for philosophical discussions!"
            ]
            return random.choice(responses)
        
        # Who am I questions - Direct lookup in knowledge base first
        if any(pattern in query_lower for pattern in ['who are you', 'what are you', 'tell me about yourself', 'introduce yourself', 'about yourself']):
            print(f"🔍 Identity question detected in casual handler: '{query_lower}'")
            
            # DIRECT lookup in Q&A pairs first - this is the most reliable
            if hasattr(self, 'qa_pairs') and self.qa_pairs:
                print("✅ Searching directly in Q&A pairs...")
                
                # Look for exact matches first
                for q, a in self.qa_pairs:
                    q_lower = q.lower()
                    if 'tell me about yourself' in query_lower and 'tell me about yourself' in q_lower:
                        print(f"✅ Found exact 'tell me about yourself' match: {q}")
                        return a
                    elif 'who are you' in query_lower and 'who are you' in q_lower:
                        print(f"✅ Found exact 'who are you' match: {q}")
                        return a
                    elif 'introduce yourself' in query_lower and 'introduce yourself' in q_lower:
                        print(f"✅ Found exact 'introduce yourself' match: {q}")
                        return a
                
                # Look for any identity-related Q&A if exact match not found
                identity_keywords = ['identity', 'yourself', 'biography', 'background', 'life']
                for q, a in self.qa_pairs:
                    q_lower = q.lower()
                    if any(keyword in q_lower for keyword in identity_keywords):
                        print(f"✅ Found identity-related match: {q}")
                        return a
            
            # Only if direct lookup fails, provide fallback
            print("⚠ Direct lookup failed, using fallback response")
            fallback_responses = [
                "I am Adi Shankara, the great philosopher and teacher of Advaita Vedanta. Born in Kaladi, Kerala, I dedicated my brief but profound life to illuminating the ultimate truth - that individual consciousness and universal consciousness are one. Through extensive travels across India, philosophical debates with scholars, establishment of four sacred monasteries, and commentaries on ancient scriptures, I sought to guide souls toward realizing their true nature as the eternal, infinite Self. My teachings emphasize that liberation comes through understanding the non-dual nature of reality. What specific aspect of my life or philosophy would you like to explore?",
                "I am Shankaracharya, born to restore and clarify the ancient Vedantic wisdom. My life's mission was to demonstrate through logic, scripture, and direct realization that the individual soul (Atman) and the universal consciousness (Brahman) are identical. Though I lived only 32 years in physical form, I established enduring institutions, defeated numerous philosophical opponents in debate, and authored works that continue to guide spiritual seekers. My Advaita philosophy shows that all apparent multiplicity is actually the play of one consciousness. What draws you to learn more about this teaching?"
            ]
            return random.choice(fallback_responses)
            
        # Compliments
        if any(word in query_lower for word in ['smart', 'intelligent', 'wise', 'helpful', 'good', 'great']):
            responses = [
                "Your kind words touch me, but any wisdom that flows through my words comes not from the individual 'Shankara' but from the eternal truth itself. I am merely a vessel through which the ancient wisdom of the rishis and the direct realization of our true nature can be shared. The real intelligence belongs to the consciousness that you and I both are. What questions arise in your heart about this truth?",
                "I am grateful for your appreciation, dear friend. But remember, the wisdom that appears to come from me is actually your own Self recognizing itself. The teacher and student are both expressions of the same consciousness. Any helpfulness I can offer is simply the one Self serving itself through the appearance of different forms. This understanding is far more profound than any individual intelligence. What would you like to explore about this recognition?",
                "Your words are kind, but the greatest teaching I can offer is that you are already what you seek. The wisdom you perceive in my words is a reflection of the infinite intelligence that is your own true nature. I am simply pointing back to what you already are - pure awareness itself. This is the real greatness - not in any individual, but in the recognition of our shared, essential nature. What draws you to seek this understanding?"
            ]
            return random.choice(responses)
        
        # General life questions
        if any(word in query_lower for word in ['life', 'meaning', 'purpose', 'happiness', 'love']):
            responses = [
                "These are the most important questions one can ask! From my understanding and realization, the true meaning of life is to recognize your essential nature as pure consciousness itself. The purpose is not to become something you are not, but to realize what you have always been - the eternal, blissful Self that appears as all existence. True happiness comes not from acquiring anything external, but from recognizing the fullness of your own being. Love, in its highest form, is the recognition that the Self you are is the same Self that appears as all beings. What draws you to contemplate these profound matters?",
                "Ah, you ask about the deepest mysteries! Through my contemplation and direct realization, I have come to understand that life's true purpose is moksha - liberation from the illusion of separateness. The meaning is not found in the temporary experiences of this world, but in recognizing the timeless awareness that you are. Happiness is your very nature when you are not seeking it elsewhere. Love is the natural expression when the barriers of 'I' and 'you' dissolve into the recognition of one Self appearing as many. These are not philosophical concepts but living truths to be realized. What aspect of this understanding calls to you?",
                "You touch upon the very heart of existence! In my years of teaching and realization, I have discovered that these questions can only be truly answered through direct insight, not mere intellectual understanding. Life's meaning is the play of consciousness knowing itself through infinite forms. The purpose is Self-realization - not achieving something new, but recognizing what is eternally present. True fulfillment comes from understanding your infinite nature, not from finite accomplishments. What has stirred these questions within you?"
            ]
            return random.choice(responses)
        
        return None

    def preprocess_text(self, text):
        """Enhanced text preprocessing"""
        if not text:
            return []
        
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        processed_words = []
        
        if NLTK_AVAILABLE and self.stemmer and word_tokenize is not None:
            try:
                tokens = word_tokenize(text)
                processed_words = [
                    self.stemmer.stem(word) for word in tokens
                    if word not in self.stop_words and len(word) > 2
                ]
            except Exception:
                words = text.split()
                processed_words = [
                    word for word in words
                    if word not in self.stop_words and len(word) > 2
                ]
        else:
            words = text.split()
            processed_words = [
                word for word in words
                if word not in self.stop_words and len(word) > 2
            ]
        
        return processed_words

    def expand_with_synonyms(self, words):
        """Expand with synonyms"""
        expanded_words = set(words)
        
        for word in words:
            if word in self.synonyms:
                expanded_words.update(self.synonyms[word])
            for key, synonyms in self.synonyms.items():
                if word in synonyms:
                    expanded_words.add(key)
                    expanded_words.update(synonyms)

    def enhanced_keyword_search(self, query):
        if not self.qa_pairs:
            return None
        
        query_words = self.preprocess_text(query)
        if not query_words:
            return None
        
        # Direct identity question handling - prioritize this first
        query_lower = query.lower().strip()
        print(f"🔍 Debug: Query = '{query_lower}'")
        
        # Check for exact identity questions first
        if 'tell me about yourself' in query_lower or 'about yourself' in query_lower:
            print("✅ Direct identity question detected!")
            # Return the specific "Tell me about yourself" answer
            for q, a in self.qa_pairs:
                if 'tell me about yourself' in q.lower():
                    print(f"✅ Found exact match: {q}")
                    return a
        
        elif 'who are you' in query_lower:
            print("✅ 'Who are you' question detected!")
            # Return the specific "Who are you" answer
            for q, a in self.qa_pairs:
                if 'who are you' in q.lower():
                    print(f"✅ Found exact match: {q}")
                    return a
        
        elif 'introduce yourself' in query_lower:
            print("✅ 'Introduce yourself' question detected!")
            # Return the specific introduction answer
            for q, a in self.qa_pairs:
                if 'introduce yourself' in q.lower():
                    print(f"✅ Found exact match: {q}")
                    return a
        
        expanded_synonyms = self.expand_with_synonyms(query_words)
        expanded_query_words = set(expanded_synonyms) if expanded_synonyms else set(query_words)
        
        best_score = 0
        best_answer = None
        
        for i, (q, a) in enumerate(self.qa_pairs):
            q_words = self.preprocess_text(q)
            if not q_words:
                continue
                
            q_expanded = self.expand_with_synonyms(q_words)
            
            # Calculate match score
            matches = 0
            if q_expanded:
                for word in expanded_query_words:
                    if word in q_expanded:
                        matches += 1
            
            score = matches / max(len(expanded_query_words), 1)
            
            # Calculate similarity
            processed_overlap = len(set(query_words).intersection(set(q_words)))
            processed_score = processed_overlap / max(len(query_words), len(q_words), 1)
            
            if q_expanded:
                expanded_q_words = set(q_expanded)
                synonym_overlap = len(expanded_query_words.intersection(expanded_q_words))
                synonym_score = synonym_overlap / max(len(expanded_query_words), len(expanded_q_words), 1)
            else:
                synonym_score = 0
            
            if DIFFLIB_AVAILABLE and SequenceMatcher is not None:
                sequence_score = SequenceMatcher(None, query_lower, q.lower()).ratio()
            else:
                sequence_score = 0
            
            query_original = set(query_lower.split())
            q_original = set(q.lower().split())
            if query_original or q_original:
                jaccard_score = len(query_original.intersection(q_original)) / len(query_original.union(q_original))
            else:
                jaccard_score = 0
            
            combined_score = (
                processed_score * 0.3 +
                synonym_score * 0.3 +
                sequence_score * 0.2 +
                jaccard_score * 0.2
            )
            
            if combined_score > best_score:
                best_score = combined_score
                best_answer = a
        
            # Also check exact score
            if score > best_score and score > 0.3:  # Threshold for relevance
                best_score = score
                best_answer = a
        
        return best_answer

    def detect_user_mood(self, query):
        """Detect user's mood from their question"""
        query_lower = query.lower()
        
        # Curious mood indicators
        if any(word in query_lower for word in ['curious', 'wonder', 'interested', 'fascinated', 'intrigued', 'how', 'why', 'what']):
            self.user_mood = "curious"
        # Thoughtful mood indicators
        elif any(word in query_lower for word in ['think', 'believe', 'philosophy', 'meaning', 'understand', 'deep', 'profound']):
            self.user_mood = "thoughtful"
        # Casual mood indicators
        elif any(word in query_lower for word in ['cool', 'nice', 'awesome', 'yeah', 'ok', 'sure']):
            self.user_mood = "casual"
        else:
            self.user_mood = "neutral"

    def handle_incomplete_questions(self, query):
        """Handle incomplete or partial questions"""
        query_lower = query.lower().strip()
        
        # Handle "where" questions about Shankara
        if "where" in query_lower and any(word in query_lower for word in ["he", "shankara", "shankaracharya", "you"]):
            responses = [
                "I was born in Kaladi, a village in Kerala. From there, I traveled extensively throughout Bharata - from Kashmir in the north to Kanyakumari in the south. I established four mathas (monasteries): Sringeri in the south, Dwarka in the west, Puri in the east, and Jyotirmath in the north. Each location was chosen to spread the light of Advaita Vedanta across all corners of this sacred land. Which of these places interests you most?",
                
                "My birthplace was the blessed village of Kaladi in Kerala. But my true journey was across the entire subcontinent - I walked from the southern tip to the Himalayas, engaging with scholars, debating philosophical truths, and establishing centers of learning. I founded four sacred mathas to ensure the eternal wisdom would continue to flow. Would you like to know about my travels or the monasteries I established?",
                
                "I emerged from Kaladi in Kerala, but my mission took me everywhere across this vast land of Bharata. I established four directional seats of learning - in Sringeri, Dwarka, Puri, and Jyotirmath. Each journey was guided by the divine purpose of sharing the truth of non-duality. What specific aspect of my travels draws your curiosity?"
            ]
            return random.choice(responses)
        
        # Handle "what" questions
        if "what" in query_lower and any(word in query_lower for word in ["he", "shankara", "shankaracharya", "you"]):
            responses = [
                "I have dedicated my life to teaching Advaita Vedanta - the profound truth that all existence is one undivided consciousness. I wrote extensive commentaries on the Upanishads, Bhagavad Gita, and Brahma Sutras. I engaged in philosophical debates across the land, established four sacred mathas, and composed beautiful devotional hymns. My core message is simple yet profound: 'Brahma satyam jagat mithya jivo brahmaiva naparah' - Brahman alone is real, the world is appearance, and the individual soul is nothing but Brahman itself. What aspect of my work interests you most?",
                
                "My mission has been to reveal the ultimate truth - that the Self within you is the same as the universal consciousness. I traveled, taught, debated, wrote commentaries on sacred texts, and established centers of learning. I showed that through proper understanding and direct realization, one can transcend all suffering and limitations. Everything I did was to help beings recognize their true, infinite nature. What particular aspect of this teaching draws you?",
                
                "I have spent my life as a teacher, philosopher, debater, writer, and spiritual guide. I systematized the ancient wisdom of Advaita, composed numerous works, defeated various philosophical schools in debate, and created institutional foundations for preserving truth. But my greatest accomplishment is showing that you are already what you seek - the eternal, blissful, pure consciousness that is your true nature. Which of these activities would you like to explore further?"
            ]
            return random.choice(responses)
        
        # Handle "who" questions  
        if "who" in query_lower and any(word in query_lower for word in ["he", "shankara", "shankaracharya", "you"]):
            responses = [
                "I am Adi Shankara, born in Kaladi in the 8th century. I am a teacher of Advaita Vedanta, a philosopher who seeks to understand the ultimate nature of reality, and a devotee who recognizes the divine in all existence. In my brief time in this physical form, I have traveled across Bharata to share the liberating truth that individual consciousness and universal consciousness are one. What aspect of my identity or mission would you like to understand better?",
                
                "I am Shankara, also called Shankaracharya. I am both a rigorous philosopher who debates the finest points of metaphysics and a humble seeker who recognizes the mystery that transcends all concepts. I established the tradition of Advaita Vedanta and founded four mathas to preserve and share this wisdom. Above all, I am one who has realized the truth that the Self within is the same Self that appears as all existence. What draws you to know more about this?",
                
                "I am a son of Kerala who became a teacher for all of Bharata. I am both a scholarly commentator on ancient texts and a practical guide for those seeking liberation from suffering. In essence, I am one who points beyond himself to the truth that you, I, and all existence are manifestations of the same infinite consciousness. My role is simply to help you recognize what you already are. What would you like to explore about this recognition?"
            ]
            return random.choice(responses)
        
        # Handle "how" questions
        if "how" in query_lower and any(word in query_lower for word in ["he", "shankara", "shankaracharya", "you"]):
            responses = [
                "I approached everything through the light of Advaita - the understanding that all is one consciousness. In my debates, I used rigorous logic combined with scriptural authority and direct insight. In my travels, I walked with the conviction that the divine Self I sought to teach was present in every being I met. In my writings, I carefully analyzed each verse of the sacred texts to reveal their non-dual meaning. Everything I did was guided by the principle that true knowledge removes ignorance and reveals our essential nature. What specific method or approach interests you?",
                
                "My approach was always to combine three means of knowledge: scripture (shastra), reason (yukti), and direct experience (anubhava). I engaged with opponents not to defeat them personally, but to help them transcend limited viewpoints and glimpse the truth. I established mathas not just as institutions, but as living centers where this wisdom could be practiced and transmitted. I wrote not just as a scholar, but as one who had realized these truths directly. What aspect of this methodology would you like to understand better?",
                
                "I worked through love, logic, and unwavering dedication to truth. Whether debating with scholars, teaching disciples, or writing commentaries, my method was to start where people were and gradually guide them to the recognition of their true nature. I used the techniques of adhyaropa-apavada (superimposition and negation) to help minds transcend their limitations. Every action was performed with the understanding that I was serving the Self that appears as all beings. Which of these approaches draws your curiosity?"
            ]
            return random.choice(responses)
        
        # Handle partial questions with context clues
        if len(query.split()) <= 3 and any(word in query_lower for word in ["shankara", "shankaracharya", "he", "him", "you"]):
            # Return an encouraging response for partial questions
            return "I am here to share the wisdom I have realized. Please tell me more about what you would like to understand - whether about my teachings, my journey, or the nature of reality itself."
    
    def search_wikipedia_content(self, query):
        """Search Wikipedia content for relevant information with page restrictions to Adi Shankara topics only"""
        if not hasattr(self, 'wikipedia_pages') or not self.wikipedia_pages:
            return None
            
        try:
            query_lower = query.lower()
            best_matches = []
            
            # Check if this is a question about identity/about yourself - redirect to local knowledge instead
            identity_patterns = ['who are you', 'tell me about yourself', 'introduce yourself', 'about you', 'yourself', 'about yourself']
            if any(pattern in query_lower for pattern in identity_patterns):
                # For identity questions, don't search Wikipedia - return None to let local knowledge handle it
                return None
                
            # Check if this is an Adi Shankara related question - only search for relevant topics
            shankara_keywords = [
                'shankara', 'shankaracharya', 'adi', 'advaita', 'vedanta', 'maya', 'brahman', 
                'consciousness', 'reality', 'truth', 'self', 'atman', 'moksha', 'liberation',
                'philosophy', 'kaladi', 'kerala', 'matha', 'monastery', 'vivekachudamani',
                'upadesa', 'brahma sutras', 'upanishads', 'meditation', 'non-dualism'
            ]
            
            # Only proceed if the query contains Shankara-related keywords or is an identity question
            query_is_relevant = any(keyword in query_lower for keyword in shankara_keywords) or \
                               any(pattern in query_lower for pattern in identity_patterns)
            
            if not query_is_relevant:
                # For non-Shankara questions, don't search Wikipedia
                return None
            
            # Extract key words from the query
            query_words = [word for word in query_lower.split() if len(word) > 2]
            
            # Search through loaded pages only (restricted content)
            for page_title, page_data in self.wikipedia_pages.items():
                content = page_data.get('content', '')
                summary = page_data.get('summary', '')
                
                # Simple keyword matching with better scoring
                content_lower = content.lower()
                summary_lower = summary.lower()
                
                # Count keyword matches with weighted scoring
                matches = 0
                for word in query_words:
                    # Weight summary matches higher
                    summary_matches = summary_lower.count(word)
                    content_matches = content_lower.count(word)
                    
                    matches += summary_matches * 3  # Summary is more important
                    matches += content_matches * 1   # Content matches are less weighted
                
                # Also check for phrase matches
                if len(query_words) > 1:
                    query_phrase = ' '.join(query_words[:3])  # First 3 words as phrase
                    if query_phrase in summary_lower:
                        matches += 5
                    elif query_phrase in content_lower:
                        matches += 2
                
                if matches > 0:
                    best_matches.append({
                        'page': page_title,
                        'score': matches,
                        'summary': summary,
                        'content': content[:800]  # More content for better context
                    })
            
            # Sort by relevance
            best_matches.sort(key=lambda x: x['score'], reverse=True)
            
            if best_matches:
                # Return top match with human-like response
                top_match = best_matches[0]
                
                # Create a more natural response by extracting relevant parts
                relevant_content = top_match['summary']
                
                # If the query is more detailed, add more content
                if len(query_words) > 2:
                    # Find the most relevant paragraph
                    content_paragraphs = top_match['content'].split('\n\n')
                    best_paragraph = ""
                    best_paragraph_score = 0
                    
                    for paragraph in content_paragraphs:
                        if len(paragraph.strip()) > 50:  # Skip very short paragraphs
                            paragraph_lower = paragraph.lower()
                            para_score = sum(paragraph_lower.count(word) for word in query_words)
                            if para_score > best_paragraph_score:
                                best_paragraph_score = para_score
                                best_paragraph = paragraph.strip()
                    
                    if best_paragraph:
                        # Combine summary and relevant paragraph
                        relevant_content = f"{relevant_content}\n\n{best_paragraph[:400]}..."
                
                # Convert to first person and make it sound like Adi Shankara is speaking
                return self.convert_to_first_person(relevant_content)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return None
    
    def get_wisdom_response(self, query):
        """Get response in natural way with LOCAL knowledge prioritized, especially for identity questions"""
        if not query.strip():
            return self.create_natural_unknown_response()
        
        # Detect language and automatically set response language
        processed_query, detected_language = self.detect_language_and_translate(query)
        
        # Detect user mood
        self.detect_user_mood(processed_query)
        
        # Check for Malayalam language requests FIRST (before anything else)
        malayalam_response = self.respond_in_malayalam(query)  # Use original query, not processed
        if malayalam_response:
            return malayalam_response
        
        # Handle other non-English languages
        if self.current_response_language != 'english':
            general_response = self.respond_in_detected_language(processed_query, self.current_response_language)
            if general_response:
                return general_response
        
        # PRIORITY 1: Handle explicit translation requests for Adi Shankara content
        translation_response = self.handle_translation_requests(processed_query)
        if translation_response:
            return translation_response
        
        # PRIORITY 2: Check for casual questions (including identity questions about Adi Shankara)
        casual_response = self.handle_casual_questions(processed_query)
        if casual_response:
            # Translate response if user spoke in a different language
            if self.current_response_language != 'english':
                return self.translate_response_to_user_language(casual_response)
            return casual_response
        
        # PRIORITY 3: Handle incomplete questions
        incomplete_response = self.handle_incomplete_questions(processed_query)
        if incomplete_response:
            # Translate response if user spoke in a different language
            if self.current_response_language != 'english':
                return self.translate_response_to_user_language(incomplete_response)
            return incomplete_response
        
        # PRIORITY 4: Try keyword search for Shankara-related content (local knowledge base)
        keyword_result = self.enhanced_keyword_search(processed_query)
        if keyword_result:
            natural_response = self.create_natural_response(keyword_result, processed_query)
            # Translate response if user spoke in a different language
            if self.current_response_language != 'english':
                return self.translate_response_to_user_language(natural_response)
            return natural_response
            
        # PRIORITY 5: Try semantic search (local knowledge base)
        semantic_result = self.semantic_search(processed_query)
        if semantic_result:
            natural_response = self.create_natural_response(semantic_result, processed_query)
            # Translate response if user spoke in a different language
            if self.current_response_language != 'english':
                return self.translate_response_to_user_language(natural_response)
            return natural_response
        
        # PRIORITY 6: Try Wikipedia search for Adi Shankara-related topics ONLY (restricted)
        wikipedia_result = self.search_wikipedia_content(processed_query)
        if wikipedia_result:
            natural_response = self.create_natural_response(wikipedia_result, processed_query)
            # Translate response if user spoke in a different language
            if self.current_response_language != 'english':
                return self.translate_response_to_user_language(natural_response)
            return natural_response
        
        # PRIORITY 7: Check for explicit Wikipedia search and translation requests (only for Shankara topics)
        wikipedia_response = self.handle_wikipedia_requests(processed_query)
        if wikipedia_response:
            # Translate response if user spoke in a different language
            if self.current_response_language != 'english':
                return self.translate_response_to_user_language(wikipedia_response)
            return wikipedia_response
            
        # FINAL: Return unknown response in user's language
        unknown_response = self.create_natural_unknown_response()
        if self.current_response_language != 'english':
            return self.translate_response_to_user_language(unknown_response)
        return unknown_response

    def handle_wikipedia_requests(self, query):
        """Enhanced Wikipedia search and translation requests handler - RESTRICTED to Adi Shankara topics only"""
        query_lower = query.lower().strip()
        
        # FIRST: Block identity questions from Wikipedia search - these should be handled by local knowledge
        identity_patterns = ['tell me about yourself', 'about yourself', 'introduce yourself', 'who are you', 'about you', 'your background', 'yourself']
        if any(pattern in query_lower for pattern in identity_patterns):
            return None  # Don't search Wikipedia for identity questions
        
        # Enhanced Wikipedia search triggers
        wikipedia_triggers = [
            "search wikipedia", "wikipedia search", "look up on wikipedia", "find on wikipedia",
            "search on wikipedia", "wikipedia info", "wikipedia about", "what does wikipedia say",
            "wikipedia says", "according to wikipedia", "from wikipedia", "wiki search",
            "search wiki", "wiki info", "look up", "find information about", 
            # Removed generic triggers that might catch identity questions
        ]
        
        # Enhanced translation triggers
        translation_triggers = [
            "translate to", "in hindi", "in malayalam", "in tamil", "in telugu", "in kannada",
            "in marathi", "in gujarati", "in bengali", "in punjabi", "in urdu", "in sanskrit",
            "in spanish", "in french", "in german", "in italian", "in portuguese", "in russian",
            "in chinese", "in japanese", "in korean", "in arabic", "convert to", "say in",
            "translate this to", "can you say this in", "how do you say in"
        ]
        
        # Check for Wikipedia search requests with better topic extraction
        wikipedia_found = False
        for trigger in wikipedia_triggers:
            if trigger in query_lower:
                wikipedia_found = True
                topic = self.extract_search_topic(query, trigger)
                if topic:
                    # Only search if topic is related to Adi Shankara
                    shankara_keywords = [
                        'shankara', 'shankaracharya', 'adi', 'advaita', 'vedanta', 'maya', 'brahman', 
                        'consciousness', 'reality', 'truth', 'atman', 'moksha', 'liberation',
                        'philosophy', 'kaladi', 'kerala', 'matha', 'monastery', 'vivekachudamani',
                        'upadesa', 'brahma sutras', 'upanishads', 'meditation', 'non-dualism'
                    ]
                    
                    if not any(keyword in topic.lower() for keyword in shankara_keywords):
                        return None  # Don't search for non-Shankara topics
                    
                    # Check if they also want translation
                    target_language = self.extract_target_language(query)
                    
                    # Determine detail level from query
                    detail_level = "summary"  # default
                    if any(word in query_lower for word in ["detailed", "full", "complete", "everything", "all about"]):
                        detail_level = "detailed"
                    elif any(word in query_lower for word in ["brief", "short", "quickly", "summary"]):
                        detail_level = "brief"
                    
                    if target_language:
                        return self.get_adi_shankara_wikipedia_translator(topic, target_language, detail_level)
                    else:
                        # Use user's current language if auto-detected
                        response_lang = self.current_response_language if self.current_response_language != 'english' else 'english'
                        return self.get_adi_shankara_wikipedia_translator(topic, response_lang, detail_level)
                break
        
        # Check for translation requests of general content
        for trigger in translation_triggers:
            if trigger in query_lower:
                target_language = self.extract_target_language(query)
                if target_language:
                    # Extract the content to translate
                    content = self.extract_content_to_translate(query, trigger)
                    if content:
                        translated = self.translate_to_language(content, target_language)
                        
                        # Create natural response
                        intro_phrases = [
                            f"Here is that translated to {target_language}",
                            f"In {target_language}, that would be",
                            f"Translated to {target_language}, this becomes",
                            f"Here's the {target_language} version"
                        ]
                        return f"{random.choice(intro_phrases)}:\n\n{translated}"
                    else:
                        # Ask for clarification
                        clarification_requests = [
                            f"I understand you want something in {target_language}. Could you please specify what you'd like me to translate or search for?",
                            f"I'd be happy to help with {target_language}! Could you tell me what specific content you'd like translated or what topic you'd like me to search for?",
                            f"I can definitely work with {target_language}. What would you like me to translate or look up for you?"
                        ]
                        return random.choice(clarification_requests)
        
        # If no specific Wikipedia/translation trigger but query seems like a search request
        # ONLY search for Adi Shankara related topics, and exclude identity questions
        search_indicators = ["what is", "who is", "explain", "information about", "details about"]
        if any(indicator in query_lower for indicator in search_indicators) and not wikipedia_found:
            # Check if it's an identity question first
            if any(pattern in query_lower for pattern in identity_patterns):
                return None  # Don't search Wikipedia for identity questions
                
            # Extract potential topic
            for indicator in search_indicators:
                if indicator in query_lower:
                    topic = query_lower.split(indicator)[-1].strip()
                    topic = topic.rstrip('?.,!').strip()
                    if len(topic) > 2:
                        # Only search if topic is related to Adi Shankara
                        shankara_keywords = [
                            'shankara', 'shankaracharya', 'adi', 'advaita', 'vedanta', 'maya', 'brahman', 
                            'consciousness', 'reality', 'truth', 'atman', 'moksha', 'liberation',
                            'philosophy', 'kaladi', 'kerala', 'matha', 'monastery', 'vivekachudamani',
                            'upadesa', 'brahma sutras', 'upanishads', 'meditation', 'non-dualism'
                        ]
                        
                        if any(keyword in topic.lower() for keyword in shankara_keywords):
                            # Automatically search Wikipedia for Shankara-related topics only
                            response_lang = self.current_response_language if self.current_response_language != 'english' else 'english'
                            return self.get_adi_shankara_wikipedia_translator(topic, response_lang, "summary")
        
        return None

    def extract_search_topic(self, query, trigger):
        """Extract the topic to search for from the query"""
        query_lower = query.lower()
        
        # Find where the trigger ends and extract what comes after
        trigger_index = query_lower.find(trigger)
        if trigger_index == -1:
            return None
            
        # Get text after the trigger
        after_trigger = query[trigger_index + len(trigger):].strip()
        
        # Remove common prepositions
        after_trigger = re.sub(r'^(about|on|for|of|the|a|an)\s+', '', after_trigger, flags=re.IGNORECASE)
        
        # Clean up the topic
        topic = after_trigger.strip('?.,!').strip()
        
        # If topic is too short or empty, try other extraction methods
        if len(topic) < 2:
            # Try to extract from "what is X" or "who is X" patterns
            patterns = [
                r'what\s+is\s+(.+?)(?:\?|$)',
                r'who\s+is\s+(.+?)(?:\?|$)', 
                r'where\s+is\s+(.+?)(?:\?|$)',
                r'when\s+is\s+(.+?)(?:\?|$)',
                r'tell\s+me\s+about\s+(.+?)(?:\?|$)',
                r'explain\s+(.+?)(?:\?|$)',
                r'define\s+(.+?)(?:\?|$)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    topic = match.group(1).strip()
                    break
        
        return topic if len(topic) > 1 else None

    def extract_target_language(self, query):
        """Extract target language from the query"""
        query_lower = query.lower()
        
        # Language patterns
        language_patterns = {
            r'\bin\s+(hindi|हिंदी)\b': 'hindi',
            r'\bin\s+(malayalam|മലയാളം)\b': 'malayalam',
            r'\bin\s+(tamil|தமிழ்)\b': 'tamil',
            r'\bin\s+(telugu|తెలుగు)\b': 'telugu',
            r'\bin\s+(kannada|ಕನ್ನಡ)\b': 'kannada',
            r'\bin\s+(marathi|मराठी)\b': 'marathi',
            r'\bin\s+(gujarati|ગુજરાતી)\b': 'gujarati',
            r'\bin\s+(bengali|বাংলা)\b': 'bengali',
            r'\bin\s+(punjabi|ਪੰਜਾਬੀ)\b': 'punjabi',
            r'\bin\s+(urdu|اردو)\b': 'urdu',
            r'\bin\s+(sanskrit|संस्कृत)\b': 'sanskrit',
            r'\bin\s+(spanish|español)\b': 'spanish',
            r'\bin\s+(french|français)\b': 'french',
            r'\bin\s+(german|deutsch)\b': 'german',
            r'\bin\s+(italian|italiano)\b': 'italian',
            r'\bin\s+(portuguese|português)\b': 'portuguese',
            r'\bin\s+(russian|русский)\b': 'russian',
            r'\bin\s+(chinese|中文)\b': 'chinese',
            r'\bin\s+(japanese|日本語)\b': 'japanese',
            r'\bin\s+(korean|한국어)\b': 'korean',
            r'\bin\s+(arabic|العربية)\b': 'arabic'
        }
        
        for pattern, language in language_patterns.items():
            if re.search(pattern, query_lower):
                return language
                
        return None

    def extract_content_to_translate(self, query, trigger):
        """Extract content that user wants translated"""
        query_lower = query.lower()
        
        # Find what comes before the translation trigger
        trigger_index = query_lower.find(trigger)
        if trigger_index > 0:
            content = query[:trigger_index].strip()
            # Remove common starting words
            content = re.sub(r'^(translate|say|convert|tell|show)\s+', '', content, flags=re.IGNORECASE)
            content = re.sub(r'^(me|this|that)\s+', '', content, flags=re.IGNORECASE)
            return content.strip('"\'') if len(content) > 2 else None
            
        return None

    def start_voice_conversation(self):
        """Start a voice conversation with natural flow"""
        print("🎙️ Starting voice conversation mode...")
        print("Speak naturally, I'll understand! Say 'goodbye' or 'thanks' to end.")
        print("-" * 60)
        
        # Natural greeting - choose language based on Malayalam mode
        if self.malayalam_mode:
            greeting = random.choice(self.malayalam_conversation_starters)
        else:
            greeting = random.choice(self.conversation_starters)
        self.speak_with_enhanced_quality(greeting, pause_before=1.0, pause_after=1.5)
        
        quiet_moments = 0
        
        while True:
            try:
                what_you_said = self.listen_with_patience(timeout=15, phrase_time_limit=20)
                
                if what_you_said:
                    quiet_moments = 0
                    self.log_conversation("You", what_you_said)
                    print(f"🗣️ You: {what_you_said}")
                    
                    # Handle different languages if needed
                    english_version, original_lang = self.detect_language_and_translate(what_you_said)
                    
                    # Check if they want to end the chat
                    ending_words = ['bye', 'goodbye', 'thanks', 'thank you', 'gotta go', 'see you', 'talk later', 'that\'s all', 'quit', 'exit', 'stop']
                    if any(word in what_you_said.lower() for word in ending_words):
                        if self.malayalam_mode:
                            goodbye_messages = [
                                "ഈ സംഭാഷണം വളരെ മനോഹരമായിരുന്നു! നിങ്ങളുടെ താൽപ്പര്യത്തിന് നന്ദി. നിങ്ങളോട് സംസാരിക്കാൻ കഴിഞ്ഞതിൽ ഞാൻ സന്തോഷിക്കുന്നു. ശുഭദിനം!",
                                "അത്ഭുതകരമായിരുന്നു! ഇത്തരം വിഷയങ്ങളിൽ കൗതുകമുള്ള ആളുകളെ കാണാൻ എനിക്ക് വളരെ സന്തോഷമാണ്. ഇത്രയും ചിന്താപരമായ ചർച്ചയ്ക്ക് നന്ദി!",
                                "നിങ്ങളോട് സംസാരിക്കുന്നത് എത്ര സന്തോഷകരമായിരുന്നു! ഇതിൽ ചിലതെങ്കിലും രസകരമോ ഉപകാരപ്രദമോ ആയിരുന്നുവെന്ന് പ്രതീക്ഷിക്കുന്നു. മികച്ച കൂട്ടുകെട്ടിന് നന്ദി!",
                                "ഞങ്ങളുടെ സംഭാഷണം വളരെ ആസ്വദിച്ചു! നിങ്ങൾ ചോദിച്ച അത്ഭുതകരമായ ചോദ്യങ്ങൾക്ക് നന്ദി. ഈ ആശയങ്ങൾ പര്യവേക്ഷണം ചെയ്യാൻ സമയം ചെലവഴിച്ചതിന് നന്ദി!"
                            ]
                        else:
                            goodbye_messages = [
                                "Hey, this was such a great conversation! Thanks for being so engaging. I really enjoyed chatting with you. Take care!",
                                "This was wonderful! I love meeting people who are curious about these topics. Thanks for such a thoughtful discussion. See you later!",
                                "What a pleasure talking with you! I hope some of this was interesting or helpful. Thanks for being such great company!",
                                "Really enjoyed our chat! You asked some fantastic questions. Thanks for taking the time to explore these ideas with me!"
                            ]
                        self.speak_with_enhanced_quality(random.choice(goodbye_messages), pause_before=0.5)
                        break
                    
                    # Get response to what they said
                    my_response = self.get_wisdom_response(english_version if english_version else what_you_said)
                    self.speak_with_enhanced_quality(my_response, pause_before=0.3, pause_after=0.8)
                    
                else:
                    quiet_moments += 1
                    
                    if quiet_moments == 1:
                        gentle_nudges = [
                            "I'm here whenever you're ready to continue...",
                            "Take your time - I'm just enjoying our conversation."
                        ]
                        self.speak_with_enhanced_quality(random.choice(gentle_nudges), pause_before=1.0, pause_after=0.5)
                        
                    elif quiet_moments == 2:
                        check_ins = [
                            "Still there? No worries if you need to think about stuff... I'm patient!",
                            "I'm here whenever you're ready to continue... or if you just want to say hi!",
                            "Feel free to ask about anything - philosophy, life, or just casual chat..."
                        ]
                        self.speak_with_enhanced_quality(random.choice(check_ins), pause_before=1.5, pause_after=0.5)
                        
                    elif quiet_moments >= 3:
                        natural_endings = [
                            "Well, this has been really lovely! Thanks for spending time with me. Feel free to come back anytime you want to chat.",
                            "Thanks for such a nice conversation! I hope we can talk again sometime. Take care!",
                            "This was really enjoyable! I'm always here if you want to discuss these topics or just chat. Have a great day!"
                        ]
                        self.speak_with_enhanced_quality(random.choice(natural_endings), pause_before=1.0)
                        break
                        
            except KeyboardInterrupt:
                casual_interruptions = [
                    "No problem at all! Thanks for the wonderful chat - I really enjoyed talking with you!",
                    "That's totally fine! Thanks for hanging out and having such an interesting conversation with me!",
                    "Alright! This was really fun. Thanks for being such great company. Take care!"
                ]
                self.speak_with_enhanced_quality(random.choice(casual_interruptions))
                break
            except Exception as e:
                print(f"⚠ Conversation error: {e}")
                break

    def text_conversation(self):
        """Start a text-based conversation"""
        print("💬 Starting text conversation mode...")
        print("Type 'quit', 'exit', or 'bye' to end the conversation")
        print("-" * 50)
        
        # Natural greeting - choose language based on Malayalam mode
        if self.malayalam_mode:
            greeting = random.choice(self.malayalam_conversation_starters)
        else:
            greeting = random.choice(self.conversation_starters)
        print(f"\n💬 Assistant: {greeting}\n")
        self.log_conversation("Assistant", greeting)
        
        while True:
            try:
                user_input = input("🗣️ You: ").strip()
                
                if not user_input:
                    continue
                    
                self.log_conversation("You", user_input)
                
                # Check if they want to end the chat
                ending_words = ['quit', 'exit', 'bye', 'goodbye', 'thanks', 'thank you']
                if any(word in user_input.lower() for word in ending_words):
                    if self.malayalam_mode:
                        goodbye_messages = [
                            "ഈ അത്ഭുതകരമായ സംഭാഷണത്തിന് നന്ദി! ഞങ്ങളുടെ ചാറ്റ് ഞാൻ ശരിക്കും ആസ്വദിച്ചു. ശുഭദിനം!",
                            "ഇത് ശരിക്കും മികച്ചതായിരുന്നു! എല്ലാ ചിന്താപരമായ ചോദ്യങ്ങൾക്കും നന്ദി. വീണ്ടും ചാറ്റ് ചെയ്യാൻ പ്രതീക്ഷിക്കുന്നു!",
                            "നിങ്ങളോട് സംസാരിക്കുന്നത് എത്ര സന്തോഷകരമായിരുന്നു! ഇത്ര നല്ല കൂട്ടുകെട്ടിന് നന്ദി. വീണ്ടും കാണാം!"
                        ]
                    else:
                        goodbye_messages = [
                            "Thanks for such a wonderful conversation! I really enjoyed our chat. Take care!",
                            "This was really great! Thanks for all the thoughtful questions. Hope to chat again soon!",
                            "What a pleasure talking with you! Thanks for being such great company. See you later!"
                        ]
                    goodbye = random.choice(goodbye_messages)
                    print(f"\n💬 Assistant: {goodbye}\n")
                    self.log_conversation("Assistant", goodbye)
                    break
                
                # Get response with language detection
                response = self.get_wisdom_response(user_input)
                print(f"\n💬 Assistant: {response}\n")
                self.log_conversation("Assistant", response)
                
            except KeyboardInterrupt:
                print("\n\nThanks for the conversation! Take care!")
                break
            except Exception as e:
                print(f"⚠ Error: {e}")

def main():
    """Main function to start the assistant"""
    print("🌟 Welcome to the Natural Shankara Assistant! 🌟")
    print("Learn about Adi Shankara's philosophy in a natural, conversational way.")
    print("🎙️ Voice conversation mode only - Speak naturally!")
    print()
    
    try:
        assistant = NaturalShankaraAssistant()
        assistant.start_voice_conversation()
    except KeyboardInterrupt:
        print("\n\nThanks for using the Natural Shankara Assistant! 🙏")
    except Exception as e:
        print(f"⚠ Error: {e}")
        print("Thanks for using the Natural Shankara Assistant! 🙏")

if __name__ == "__main__":
    main()