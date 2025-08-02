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
    import wikipedia  # type: ignore
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
    "pyttsx3": "pyttsx3",
    "googletrans": "googletrans==4.0.0rc1",
    "gtts": "gTTS",
    "pygame": "pygame",
    "nltk": "nltk",
    "edge-tts": "edge-tts",
    "wikipedia": "wikipedia"
    # Note: TTS (Coqui) removed due to installation issues requiring Visual C++ Build Tools
    # Note: torch, sentence-transformers, sounddevice, scipy, pyaudio, aiofiles are optional
}

def install_packages():
    """Install required packages with better error handling"""
    for module, package in required.items():
        try:
            __import__(module)
            logger.info(f"Package {module} already installed")
        except ImportError:
            try:
                logger.info(f"Installing missing package: {package}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                logger.info(f"Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {package}: {e}")

# Install packages before importing them
try:
    install_packages()
except Exception as e:
    logger.error(f"Package installation error: {e}")
    print("Some packages may not be installed. Continuing anyway...")

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

# Try to import Coqui TTS
try:
    from TTS.api import TTS as CoquiTTS  # type: ignore
    COQUI_TTS_AVAILABLE = True and COQUI_TTS_IMPORT_SUCCESS
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
        
        # Natural conversation starters - more human-like
        self.conversation_starters = [
            "Hey there! I'm really into discussing the fascinating aspects of Adi Shankara's life and philosophy. What would you like to know about?",
            "Hi! I love chatting about Shankara's teachings and the interesting stories about his life. What catches your curiosity?",
            "Hello! I've been studying Adi Shankara for a while now, and there's so much fascinating stuff about him. What interests you most?",
            "Hey! Nice to meet you. I'm passionate about Shankara's philosophy and the amazing things he accomplished. What would you like to explore?",
            "Hi there! I find Adi Shankara's story absolutely captivating - his teachings, his travels, everything! What draws you to learn about him?"
        ]
        
        # Natural responses - more conversational
        self.casual_responses = [
            "Oh, that's such an interesting question!",
            "You know, that's one of my favorite topics to discuss.",
            "Great question! I was just thinking about that recently.",
            "That's fascinating that you asked about that!",
            "I love talking about this aspect!",
            "You've touched on something really profound there.",
            "That's a really thoughtful question.",
            "Oh, I'm so glad you brought that up!"
        ]
        
        # Natural transitions
        self.natural_transitions = [
            "You know what's really interesting about this?",
            "Here's what I find amazing about this topic...",
            "What really strikes me about this is...",
            "I think you'll find this fascinating...",
            "The way I understand it is...",
            "From what I've learned...",
            "Here's something that might interest you...",
            "What I find remarkable is..."
        ]
        
        # Follow-up questions - more natural
        self.follow_ups = [
            "What do you think about that?",
            "Does that resonate with you?",
            "Have you ever thought about it that way?",
            "What's your take on this?",
            "I'm curious about your thoughts on this.",
            "Does that make sense to you?",
            "What other aspects interest you?",
            "Is there anything specific you'd like to know more about?"
        ]
        
        # Mood-based responses
        self.mood_responses = {
            "curious": [
                "I can sense you're really curious about this! That's awesome.",
                "Your curiosity is contagious! Let me share what I know.",
                "I love how inquisitive you are about these topics!"
            ],
            "thoughtful": [
                "You're asking really thoughtful questions.",
                "I appreciate how deeply you're thinking about this.",
                "Your reflective approach to this is wonderful."
            ],
            "casual": [
                "Yeah, totally!",
                "Right? It's pretty cool stuff.",
                "Exactly! That's what I find so interesting too."
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
        
        # Setup Coqui TTS if available
        if COQUI_TTS_AVAILABLE:
            self.setup_coqui_tts()

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
                
            except Exception as e:
                print(f"⚠ Having some mic issues: {e}")
                self.recognizer = None
                self.microphone = None
        
        # Text to Speech (TTS)
        self.tts_engine = None
        if PYTTSX3_AVAILABLE and pyttsx3 is not None:
            try:
                self.tts_engine = pyttsx3.init()
                self.setup_enhanced_voice()
                print("✓ Voice system is working!")
            except Exception as e:
                print(f"⚠ Having some voice issues: {e}")
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
        if COQUI_TTS_AVAILABLE:
            print("  • Coqui TTS voices (Premium Quality)")
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
    
    def setup_wikipedia_rag(self):
        """Setup Wikipedia RAG for enhanced knowledge about Adi Shankara with page restrictions"""
        if not wikipedia:
            logger.warning("Wikipedia module not available for RAG")
            return False
            
        try:
            print("📚 Loading Wikipedia content about Adi Shankara...")
            wikipedia.set_lang("en")
            
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
            for page_title in allowed_pages:
                try:
                    page = wikipedia.page(page_title)
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
        """Setup Coqui TTS for high-quality voice synthesis"""
        try:
            print("🎤 Initializing Coqui TTS...")
            # Use a good English model for philosophical content
            if CoquiTTS is not None:
                self.coqui_tts = CoquiTTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", 
                                        progress_bar=False, gpu=False)
                print("✓ Coqui TTS ready!")
            else:
                self.coqui_tts = None
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
                                
                                # Premium voice preferences (highest priority)
                                if any(word in name_lower for word in ['neural', 'enhanced', 'premium']):
                                    score += 10
                                
                                # High-quality voice names (high priority)
                                if any(word in name_lower for word in ['david', 'mark', 'ryan', 'guy', 'william']):
                                    score += 8
                                
                                # Good Microsoft voices (medium-high priority)
                                if any(word in name_lower for word in ['zira', 'hazel', 'eva', 'james']):
                                    score += 6
                                
                                # Standard Microsoft voices (medium priority)
                                if 'microsoft' in name_lower and any(word in name_lower for word in ['english', 'us', 'uk']):
                                    score += 4
                                
                                # Prefer male voices for deeper sound (slight preference)
                                if any(word in name_lower for word in ['male', 'man']) and 'female' not in name_lower:
                                    score += 2
                                
                                if any(word in name_lower for word in ['robotic', 'sam', 'microsoft sam']):
                                    score -= 5
                                
                                voice_scores.append((voice, score, name_lower))
                        
                        # Sort by score and select the best
                        if voice_scores:
                            voice_scores.sort(key=lambda x: x[1], reverse=True)
                            best_voice = voice_scores[0][0]
                            print(f"🎤 Selected voice: {best_voice.name}")
                        else:
                            # Fallback to first available voice
                            if voices and hasattr(voices, '__getitem__') and len(voices) > 0:  # type: ignore
                                self.tts_engine.setProperty('voice', voices[0].id)  # type: ignore
                                print(f"🎤 Using default voice: {voices[0].name}")  # type: ignore
                            else:
                                print("🎤 No suitable voices found, using system default")
                except Exception as e:
                    logger.error(f"Voice selection error: {e}")
                    print("⚠ Using default voice")
                    
        except Exception as e:
            logger.error(f"Enhanced voice setup error: {e}")
            print("⚠ Using basic voice settings")

    def cleanup_temp_file(self, filepath):
        """Clean up temporary files"""
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
        except Exception as e:
            pass  # Ignore cleanup errors
    def load_qa_pairs(self):
        """Load Q&A pairs from file or create sample data"""
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
        """Create a sample Q&A file with Shankara content"""
        sample_content = """Q: Who was Adi Shankara?
A: Adi Shankara was this absolutely brilliant philosopher and spiritual teacher who lived in ancient India around 788-820 CE. What amazes me about him is how much he accomplished in just 32 years! He basically revolutionized Indian philosophy by systematizing and clarifying the teachings of Advaita Vedanta - the idea that everything is ultimately one consciousness. He wasn't just a theorist though; he was this incredible debater who traveled all across India, engaging with scholars from different schools of thought and often winning them over. Plus, he established four major monasteries that are still active today!

Q: What is Advaita Vedanta?
A: Advaita Vedanta is Shankara's core teaching, and it's really profound when you think about it. "Advaita" literally means "not two" - so it's saying that reality isn't actually divided into separate things the way it appears to be. According to this philosophy, there's only one ultimate reality called Brahman, which is pure consciousness, and everything we see - including ourselves - is actually that same consciousness appearing in different forms. It's like waves in the ocean - they look separate, but they're all just water. The goal is to realize this truth directly, not just understand it intellectually.

Q: What is maya according to Shankara?
A: Maya is this really subtle concept that Shankara taught about. It's often translated as "illusion," but that's not quite right - it's more like... the power that makes the one appear as many. Think of it like a movie projector - there's one light, but it creates all these different images on the screen. Maya is like that projector power. It's not that the world is fake or unreal, but that our perception of it as being separate from us is what's the illusion. The world exists, but not in the way we think it does. It's actually all one consciousness appearing as this amazing diversity of forms and experiences."""
        
        try:
            with open(self.qa_file, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            print(f"✓ Created knowledge base: {self.qa_file}")
        except Exception as e:
            print(f"⚠ Had trouble creating the knowledge file: {e}")

    def semantic_search(self, query):
        """Perform semantic search using sentence transformers"""
        if not self.embedding_model or not self.embeddings or not self.qa_pairs:
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
                    return self.qa_pairs[best_match_idx][1]
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            
        return None

    def create_natural_response(self, answer, query):
        """Create a more natural, conversational response"""
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
        response = f"{starter} {transition} {answer}"
        
        # Add follow-up question
        if random.random() < 0.7:  # 70% chance to add follow-up
            follow_up = random.choice(self.follow_ups)
            response += f" {follow_up}"
        
        return response

    def create_natural_unknown_response(self):
        """Create natural response for unknown questions"""
        unknown_responses = [
            "That's a really interesting question, but I don't have specific information about that aspect of Shankara's teachings. Is there something else about his philosophy or life that you'd like to explore?",
            
            "You know, that's a thoughtful question, but it's not something I have detailed knowledge about. What other aspects of Shankara's work or teachings are you curious about?",
            
            "I wish I had a good answer for that! It's outside my current knowledge about Shankara. What else would you like to discuss about his philosophy or life story?",
            
            "That's a great question, but I'm not sure about that particular detail. There's so much about Shankara that is fascinating though - what other aspects interest you?",
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
                print("🎧 Listening... (speak naturally)")
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
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
                    print("🤔 Didn't quite catch that. Could you try again?")
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
                    print("🤔 Didn't quite catch that. Could you try again?")
                    return ""
                    
        except Exception as e:
            if sr is not None and hasattr(sr, 'WaitTimeoutError') and 'timeout' in str(type(e)).lower():
                return ""  # Return empty string for timeout
            print(f"🎤 Speech issue: {e}")
            return input("Let's try typing instead: ").strip()

    async def edge_tts_speak_async(self, text):
        """Async Edge TTS speak function"""
        try:
            premium_voices = [
                "en-US-AriaNeural",
                "en-US-DavisNeural", 
                "en-US-JasonNeural",
                "en-US-TonyNeural",
                "en-GB-RyanNeural",
                "en-GB-SoniaNeural",
                "en-AU-WilliamNeural",
                "en-CA-ClaraNeural",
            ]
            
            voice = random.choice(premium_voices)
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
        
        # Enhance text for speech
        enhanced_text = self.enhance_text_for_speech(text)
        
        # Always show the text
        print(f"\n💬 Assistant: {text}\n")
        self.log_conversation("Assistant", text)
        
        # Try Coqui TTS first (highest quality)
        if COQUI_TTS_AVAILABLE and self.coqui_tts:
            try:
                success = self.coqui_tts_speak(enhanced_text)
                if success:
                    if pause_after > 0:
                        time.sleep(pause_after)
                    return
            except Exception as e:
                print(f"⚠ Coqui TTS failed: {e}")
        
        # Try Edge TTS second (high quality)
        if EDGE_TTS_AVAILABLE and asyncio is not None:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(self.edge_tts_speak_async(enhanced_text))
                loop.close()
                
                if success:
                    if pause_after > 0:
                        time.sleep(pause_after)
                    return
                    
            except Exception as e:
                print(f"⚠ Edge TTS failed: {e}")
        
        # Try pyttsx3 (medium quality)
        if self.tts_engine:
            try:
                self.tts_engine.stop()  # Stop any ongoing speech
                self.tts_engine.say(enhanced_text)
                self.tts_engine.runAndWait()
                if pause_after > 0:
                    time.sleep(pause_after)
                return
                
            except Exception as e:
                print(f"⚠ pyttsx3 failed: {e}")
        
        # Try Google TTS (basic quality)
        if GTTS_AVAILABLE and gTTS is not None and tempfile is not None:
            try:
                tts = gTTS(text=enhanced_text, lang='en', slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    temp_file = fp.name
                    tts.save(temp_file)
                    
                    # Play based on platform
                    if os.name == 'nt':  # Windows
                        try:
                            import pygame
                            pygame.mixer.init()
                            pygame.mixer.music.load(temp_file)
                            pygame.mixer.music.play()
                            while pygame.mixer.music.get_busy():
                                time.sleep(0.1)
                        except ImportError:
                            os.system(f'start /min "" "{temp_file}"')
                            time.sleep(max(len(text) * 0.08, 2))
                            
                    elif sys.platform == 'darwin':  # macOS
                        os.system(f'afplay "{temp_file}"')
                    else:  # Linux
                        os.system(f'mpg123 "{temp_file}" 2>/dev/null || mplayer "{temp_file}" 2>/dev/null')
                    
                    threading.Timer(5.0, lambda: self.cleanup_temp_file(temp_file)).start()
                    if pause_after > 0:
                        time.sleep(pause_after)
                    return
                    
            except Exception as e:
                print(f"⚠ Google TTS failed: {e}")
        
        print("🔇 Audio output unavailable, but text is displayed above.")
        if pause_after > 0:
            time.sleep(pause_after)

    def enhance_text_for_speech(self, text):
        """Enhance text for more natural speech"""
        enhanced = text
        enhanced = enhanced.replace('. ', '... ')
        enhanced = enhanced.replace('! ', '... ')
        enhanced = enhanced.replace('? ', '... ')
        enhanced = enhanced.replace(', ', ', ')
        spiritual_replacements = {
            'moksha': 'mok-sha',
            'dharma': 'dhar-ma',
            'karma': 'kar-ma',
            'maya': 'ma-ya',
            'atman': 'at-man'
        }
        for original, replacement in spiritual_replacements.items():
            enhanced = enhanced.replace(original, replacement)
        return enhanced

    def detect_language_and_translate(self, text):
        """Detect and translate if needed"""
        if not self.translator or not text.strip():
            return text, "en"
            
        try:
            detection = self.translator.detect(text)
            detected_lang = detection.lang
            confidence = detection.confidence
            
            if detected_lang != 'en' and confidence > 0.7:
                translated = self.translator.translate(text, src=detected_lang, dest='en')
                return translated.text, detected_lang
            else:
                return text, detected_lang
                
        except Exception as e:
            return text, "en"

    def respond_in_malayalam(self, query):
        """Provide responses in Malayalam when requested"""
        query_lower = query.lower()
        
        # Check if user is specifically asking for Malayalam
        if any(word in query_lower for word in ['malayalam', 'malayalam language', 'reply in malayalam']):
            malayalam_responses = [
                "നമസ്കാരം! ആദി ശങ്കരാചാര്യരുടെ തത്ത്വചിന്തയെക്കുറിച്ച് സംസാരിക്കാൻ ഞാൻ ആഗ്രഹിക്കുന്നു. അദ്വൈത വേദാന്തത്തെക്കുറിച്ച് എന്തറിയാൻ ആഗ്രഹിക്കുന്നു?",
                "വണക്കം! ശങ്കരാചാര്യരുടെ ഉപദേശങ്ങളെക്കുറിച്ച് സംസാരിക്കാൻ ഞാൻ സന്തോഷിക്കുന്നു. അദ്ദേഹത്തിന്റെ ജീവിതത്തെക്കുറിച്ചോ തത്ത്വചിന്തയെക്കുറിച്ചോ എന്തറിയാൻ ആഗ്രഹിക്കുന്നു?",
                "നമസ്തേ! കേരളത്തിലെ മഹാൻ ആദി ശങ്കരാചാര്യരെക്കുറിച്ച് സംസാരിക്കാൻ കഴിയുന്നതിൽ സന്തോഷം. അദ്ദേഹത്തിന്റെ അദ്വൈത സിദ്ധാന്തത്തെക്കുറിച്ച് അറിയാൻ ആഗ്രഹിക്കുന്നുണ്ടോ?"
            ]
            return random.choice(malayalam_responses)
        
        # Basic Malayalam greetings
        if any(word in query_lower for word in ['namaskaram', 'vanakkam', 'hello in malayalam']):
            return "നമസ്കാരം! എങ്ങനെയുണ്ട്? ആദി ശങ്കരാചാര്യരെക്കുറിച്ച് എന്തറിയാൻ ആഗ്രഹിക്കുന്നു?"
        
        # Basic questions about Shankara in Malayalam context
        if any(word in query_lower for word in ['shankara', 'advaita']) and 'malayalam' in query_lower:
            return "ആദി ശങ്കരാചാര്യൻ കേരളത്തിലെ കലടിയിൽ ജനിച്ച മഹാൻ ആണ്. അദ്ദേഹം അദ്വൈത വേദാന്തത്തിന്റെ പ്രധാന ഉപദേഷ്ടാവാണ്. 'അഹം ബ്രഹ്മാസ്മി' - ഞാൻ ബ്രഹ്മമാണ് എന്നതാണ് അദ്ദേഹത്തിന്റെ പ്രധാന ഉപദേശം."
        
        return None

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
        
        # Who am I questions
        if any(pattern in query_lower for pattern in ['who are you', 'what are you', 'tell me about yourself']):
            responses = [
                "I'm a person who finds real fulfillment in discussing life's big questions and sharing knowledge, particularly about Shankara's philosophy. I genuinely enjoy connecting with people and hearing different perspectives. I'd say I'm naturally curious and love learning. What drives your curiosity?",
                "I'm someone who's deeply interested in ancient wisdom traditions, especially Adi Shankara's work, but I also love just having genuine conversations about life. I find myself happiest when I'm sharing ideas and learning from others. What kinds of things are you passionate about?"
            ]
            return random.choice(responses)
        # Compliments
        if any(word in query_lower for word in ['smart', 'intelligent', 'wise', 'helpful', 'good', 'great']):
            responses = [
                "That's really kind of you to say! I appreciate it. I just love learning and sharing ideas - it's what energizes me. You ask great questions too!",
                "Thank you! That means a lot. I think the best conversations happen when both people are genuinely curious, and you definitely bring that energy. What else would you like to explore?",
                "Aw, thanks! I really enjoy our chat too. I think you're asking all the right questions. There's something special about connecting with someone who's genuinely interested in these topics."
            ]
            return random.choice(responses)
        
        # General life questions
        if any(word in query_lower for word in ['life', 'meaning', 'purpose', 'happiness', 'love']):
            responses = [
                "Those are such profound questions! You know, I think about these things a lot, especially through the lens of what Shankara taught about the nature of existence and consciousness. What's your take on finding meaning in life?",
                "Wow, you're getting into the deep stuff! I love it. These are exactly the kinds of questions that drew me to studying Shankara's philosophy in the first place. He had some fascinating insights about the purpose of existence. What's been on your mind about this?",
                "These are the questions that really matter, aren't they? I find Shankara's approach to understanding the self and reality offers some beautiful perspectives on living meaningfully. What's prompted you to think about these things?"
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
        
        return list(expanded_words)

    def enhanced_keyword_search(self, query):
        if not self.qa_pairs:
            return None
        
        query_words = self.preprocess_text(query)
        if not query_words:
            return None
        
        expanded_query_words = set(self.expand_with_synonyms(query_words))
        
        best_score = 0
        best_answer = None
        
        for i, (q, a) in enumerate(self.qa_pairs):
            q_words = self.preprocess_text(q)
            expanded_q_words = set(self.expand_with_synonyms(q_words))
            
            if not q_words:
                continue
            
            # Calculate similarity
            processed_overlap = len(set(query_words).intersection(set(q_words)))
            processed_score = processed_overlap / max(len(query_words), len(q_words), 1)
            
            synonym_overlap = len(expanded_query_words.intersection(expanded_q_words))
            synonym_score = synonym_overlap / max(len(expanded_query_words), len(expanded_q_words), 1)
            
            if DIFFLIB_AVAILABLE and SequenceMatcher is not None:
                sequence_score = SequenceMatcher(None, query.lower(), q.lower()).ratio()
            else:
                sequence_score = 0
            
            query_original = set(query.lower().split())
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
        
        return best_answer if best_score > 0.15 else None

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
        if "where" in query_lower and any(word in query_lower for word in ["he", "shankara", "shankaracharya"]):
            responses = [
                "Are you asking where Shankara was born, where he traveled, or where he established his monasteries? He was born in Kaladi, Kerala, but he traveled extensively throughout India and established four major mathas in different regions. What specifically would you like to know about his locations?",
                
                "I'd love to help with that! Are you curious about where Shankara was from originally? He was born in Kaladi in Kerala. Or maybe you're asking about where he went during his travels? He covered pretty much all of India! What aspect of his geography interests you most?",
                
                "That sounds like you're asking about Shankara's locations! He was born in Kerala, traveled all across India, and established monasteries in four corners of the subcontinent. Which particular place or aspect of his travels are you most curious about?"
            ]
            return random.choice(responses)
        
        # Handle "what" questions
        if "what" in query_lower and any(word in query_lower for word in ["he", "shankara", "shankaracharya"]):
            responses = [
                "I'd be happy to tell you about Shankara! Are you asking about what he taught, what he accomplished, what he wrote, or something else? He did so many amazing things - philosophy, debates, establishing monasteries, writing beautiful commentaries. What aspect interests you most?",
                
                "There's so much to say about what Shankara did! He was a philosopher, teacher, traveler, writer, and spiritual master. What particular aspect of his life or work would you like to explore?",
                
                "Shankara accomplished incredible things in his short life! What specifically would you like to know - his teachings, his travels, his writings, his debates? I'm excited to share whatever interests you most!"
            ]
            return random.choice(responses)
        
        # Handle "who" questions  
        if "who" in query_lower and any(word in query_lower for word in ["he", "shankara", "shankaracharya"]):
            responses = [
                "Ah, you're asking who Shankara was! He was this incredible 8th-century philosopher and spiritual teacher who basically revolutionized Indian philosophy. Would you like to know about his background, his accomplishments, or what made him so special?",
                
                "Great question! Shankara was an amazing philosopher, teacher, and spiritual master from ancient India. He lived around 788-820 CE and did some truly remarkable things. What aspect of who he was interests you most?",
                
                "Shankara was such a fascinating person! He was a brilliant philosopher, an incredible debater, a spiritual teacher, and a prolific writer - all packed into just 32 years of life. What would you like to know about him?"
            ]
            return random.choice(responses)
        
        # Handle "how" questions
        if "how" in query_lower and any(word in query_lower for word in ["he", "shankara", "shankaracharya"]):
            responses = [
                "I'd love to tell you about how Shankara did things! Are you curious about how he developed his philosophy, how he traveled and taught, how he debated with other scholars, or something else? What specifically interests you?",
                
                "There are so many fascinating 'how' questions about Shankara! How he managed to accomplish so much so young, how he traveled across India, how he convinced people through his debates. What particular 'how' are you most curious about?",
                
                "That's a great question about Shankara's methods! He had such interesting approaches to teaching, debating, and spreading his philosophy. What aspect of 'how' he did things would you like to explore?"
            ]
            return random.choice(responses)
        
        # Handle partial questions with context clues
        if len(query.split()) <= 3 and any(word in query_lower for word in ["shankara", "shankaracharya", "he", "him"]):
            # Return an encouraging response for partial questions
            return "I'd love to help you learn about Shankara! Could you tell me a bit more about what specifically you'd like to know?"
    
    def search_wikipedia_content(self, query):
        """Search Wikipedia content for relevant information with page restrictions"""
        if not hasattr(self, 'wikipedia_pages') or not self.wikipedia_pages:
            return None
            
        try:
            query_lower = query.lower()
            best_matches = []
            
            # Search through loaded pages only (restricted content)
            for page_title, page_data in self.wikipedia_pages.items():
                content = page_data.get('content', '')
                summary = page_data.get('summary', '')
                
                # Simple keyword matching
                content_lower = content.lower()
                summary_lower = summary.lower()
                
                # Count keyword matches
                matches = 0
                for word in query_lower.split():
                    if len(word) > 2:  # Skip very short words
                        matches += content_lower.count(word)
                        matches += summary_lower.count(word) * 2  # Weight summary higher
                
                if matches > 0:
                    best_matches.append({
                        'page': page_title,
                        'score': matches,
                        'summary': summary,
                        'content': content[:600]  # First 600 chars
                    })
            
            # Sort by relevance
            best_matches.sort(key=lambda x: x['score'], reverse=True)
            
            if best_matches:
                # Return top match with context
                top_match = best_matches[0]
                response = f"From {top_match['page']}: {top_match['summary']}"
                1
                # Add relevant content snippet if needed
                if len(query_lower.split()) > 2:  # More detailed query
                    response += f"\n\nMore detail: {top_match['content'][:400]}..."
                
                return response
            else:
                return None
                
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return None
    
    def get_wisdom_response(self, query):
        """Get response in natural way"""
        if not query.strip():
            return self.create_natural_unknown_response()
        
        # Detect user mood
        self.detect_user_mood(query)
        
        # Check for Malayalam language requests first
        malayalam_response = self.respond_in_malayalam(query)
        if malayalam_response:
            return malayalam_response
        
        # First check for casual questions
        casual_response = self.handle_casual_questions(query)
        if casual_response:
            return casual_response
        
        # Handle incomplete questions
        incomplete_response = self.handle_incomplete_questions(query)
        if incomplete_response:
            return incomplete_response
        
        # Try keyword search for Shankara-related content
        keyword_result = self.enhanced_keyword_search(query)
        if keyword_result:
            return self.create_natural_response(keyword_result, query)
            
        # Try semantic search
        semantic_result = self.semantic_search(query)
        if semantic_result:
            return self.create_natural_response(semantic_result, query)
        
        # Try Wikipedia search for broader knowledge
        wikipedia_result = self.search_wikipedia_content(query)
        if wikipedia_result:
            return self.create_natural_response(wikipedia_result, query)
            
        # Return casual unknown response
        return self.create_natural_unknown_response()

    def start_voice_conversation(self):
        """Start a voice conversation with natural flow"""
        print("🎙️ Starting voice conversation mode...")
        print("Speak naturally, I'll understand! Say 'goodbye' or 'thanks' to end.")
        print("-" * 60)
        
        # Natural greeting
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
        
        # Natural greeting  
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
                    goodbye_messages = [
                        "Thanks for such a wonderful conversation! I really enjoyed our chat. Take care!",
                        "This was really great! Thanks for all the thoughtful questions. Hope to chat again soon!",
                        "What a pleasure talking with you! Thanks for being such great company. See you later!"
                    ]
                    goodbye = random.choice(goodbye_messages)
                    print(f"\n💬 Assistant: {goodbye}\n")
                    self.log_conversation("Assistant", goodbye)
                    break
                
                # Get response
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
    print()
    
    assistant = NaturalShankaraAssistant()
    
    while True:
        print("\nChoose your interaction mode:")
        print("1. 🎙️  Voice conversation (recommended)")
        print("2. 💬 Text conversation")
        print("3. 🚪 Exit")
        
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                assistant.start_voice_conversation()
            elif choice == '2':
                assistant.text_conversation()
            elif choice == '3':
                print("Thanks for using the Natural Shankara Assistant! 🙏")
                break
            else:
                print("Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\nThanks for using the Natural Shankara Assistant! 🙏")
            break
        except Exception as e:
            print(f"⚠ Error: {e}")

if __name__ == "__main__":
    main()