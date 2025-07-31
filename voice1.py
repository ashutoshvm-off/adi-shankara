import subprocess
import sys
import os
import zipfile
import urllib.request
import json
import logging
import re
import string

# Set up logging for better debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Auto-install required packages ===
required = {
    "speech_recognition": "SpeechRecognition",
    "pyttsx3": "pyttsx3",
    "torch": "torch",
    "sentence_transformers": "sentence-transformers",
    "googletrans": "googletrans==4.0.0rc1",
    "sounddevice": "sounddevice",
    "scipy": "scipy",
    "gtts": "gTTS",
    "pyaudio": "pyaudio",
    "pygame": "pygame",
    "nltk": "nltk"
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
                if package == "pyaudio":
                    logger.info("If PyAudio installation fails, try: pip install pipwin && pipwin install pyaudio")
                raise

# Install packages before importing them
install_packages()

# === Main Assistant Code ===
import time
import torch
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import pyttsx3
import speech_recognition as sr
from sentence_transformers import SentenceTransformer, util
from googletrans import Translator
from difflib import SequenceMatcher
import tempfile
from gtts import gTTS
import threading

# Try to import NLTK components for enhanced text processing
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    from nltk.tokenize import word_tokenize
    
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    
    NLTK_AVAILABLE = True
    logger.info("NLTK components loaded successfully")
except ImportError:
    NLTK_AVAILABLE = False
    logger.warning("NLTK not available, using basic text processing")

class ShankaraVoiceAssistant:
    def __init__(self, qa_file="shankaracharya_qa.txt"):
        self.qa_file = qa_file
        self.wake_word = "hey shankara"
        self.log_file = "transcript_log.txt"
        self.is_listening = False
        
        # Initialize text processing components
        if NLTK_AVAILABLE:
            self.stemmer = PorterStemmer()
            try:
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
        else:
            self.stemmer = None
            self.stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
        
        # Synonym dictionary for better matching
        self.synonyms = {
            'philosopher': ['thinker', 'sage', 'teacher', 'guru'],
            'teaching': ['doctrine', 'philosophy', 'instruction', 'lesson'],
            'concept': ['idea', 'notion', 'principle'],
            'achieve': ['attain', 'reach', 'obtain', 'get'],
            'goal': ['aim', 'purpose', 'objective', 'target'],
            'established': ['founded', 'created', 'set up', 'built'],
            'liberation': ['freedom', 'release', 'moksha'],
            'reality': ['truth', 'brahman', 'existence'],
            'knowledge': ['wisdom', 'understanding', 'learning', 'jnana']
        }
        
        # Initialize components with error handling
        self.initialize_components()

    def initialize_components(self):
        """Initialize all components with proper error handling"""
        try:
            # Google Speech Recognition
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            logger.info("Adjusting for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Google Speech Recognition initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Speech Recognition: {e}")
            self.recognizer = None
            self.microphone = None

        try:
            # TTS Engine
            self.tts_engine = pyttsx3.init()
            self.setup_tts()
            logger.info("TTS engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.tts_engine = None

        try:
            # Translator
            self.translator = Translator()
            logger.info("Translator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize translator: {e}")
            self.translator = None

        try:
            # Sentence Transformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model initialized")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            self.embedding_model = None

        # Load Q&A pairs
        self.qa_pairs = self.load_qa_pairs()
        if self.embedding_model and self.qa_pairs:
            try:
                self.embeddings = self.embedding_model.encode([q for q, _ in self.qa_pairs], convert_to_tensor=True)
                logger.info(f"Loaded {len(self.qa_pairs)} Q&A pairs with embeddings")
            except Exception as e:
                logger.error(f"Failed to create embeddings: {e}")
                self.embeddings = None
        else:
            self.embeddings = None

    def setup_tts(self):
        """Setup TTS with error handling"""
        if self.tts_engine:
            try:
                # Configure TTS properties
                self.tts_engine.setProperty('rate', 150)  # Slower rate for better clarity
                self.tts_engine.setProperty('volume', 1.0)  # Maximum volume
                
                # Test available voices and log them
                voices = self.tts_engine.getProperty('voices')
                if voices is not None and hasattr(voices, '__iter__'):
                    voices = list(voices)
                else:
                    voices = []
                if voices and len(voices) > 0:
                    logger.info(f"Available voices: {len(voices)}")
                    for i, voice in enumerate(voices[:3]):  # Log first 3 voices
                        logger.info(f"Voice {i}: {voice.id} - {getattr(voice, 'name', 'Unknown')}")
                    
                    # Try to find a better voice (female voice if available)
                    voice_set = False
                    for voice in voices:
                        if hasattr(voice, 'name') and ('zira' in voice.name.lower() or 'female' in voice.name.lower()):
                            self.tts_engine.setProperty('voice', voice.id)
                            logger.info(f"Using female voice: {voice.name}")
                            voice_set = True
                            break
                    
                    if not voice_set:
                        self.tts_engine.setProperty('voice', voices[0].id)
                        logger.info(f"Using default voice: {getattr(voices[0], 'name', voices[0].id)}")
                else:
                    logger.warning("No voices found for TTS")
                    
                # Test TTS by speaking a short phrase
                logger.info("Testing TTS...")
                self.tts_engine.say("TTS initialized successfully")
                self.tts_engine.runAndWait()
                
            except Exception as e:
                logger.error(f"TTS setup error: {e}")
                self.tts_engine = None

    def preprocess_text(self, text):
        """Enhanced text preprocessing with NLTK support"""
        if not text:
            return []
        
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        if NLTK_AVAILABLE and self.stemmer:
            try:
                # Tokenize
                tokens = word_tokenize(text)
                # Remove stop words and stem
                processed_words = [
                    self.stemmer.stem(word) for word in tokens 
                    if word not in self.stop_words and len(word) > 2
                ]
            except:
                # Fallback to basic processing
                words = text.split()
                processed_words = [
                    word for word in words 
                    if word not in self.stop_words and len(word) > 2
                ]
        else:
            # Basic processing without NLTK
            words = text.split()
            processed_words = [
                word for word in words 
                if word not in self.stop_words and len(word) > 2
            ]
        
        return processed_words

    def expand_with_synonyms(self, words):
        """Expand word list with synonyms"""
        expanded_words = set(words)
        
        for word in words:
            if word in self.synonyms:
                expanded_words.update(self.synonyms[word])
            # Also check if any synonym maps to this word
            for key, synonyms in self.synonyms.items():
                if word in synonyms:
                    expanded_words.add(key)
                    expanded_words.update(synonyms)
        
        return list(expanded_words)

    def enhanced_keyword_search(self, query):
        """Enhanced keyword search with better preprocessing and synonym support"""
        if not self.qa_pairs:
            logger.warning("No Q&A pairs available for keyword search")
            return None
        
        # Preprocess query
        query_words = self.preprocess_text(query)
        if not query_words:
            return None
        
        # Expand with synonyms
        expanded_query_words = set(self.expand_with_synonyms(query_words))
        
        best_score = 0
        best_answer = None
        best_match_info = ""
        
        logger.info(f"Searching with processed words: {query_words}")
        logger.info(f"Expanded with synonyms: {expanded_query_words}")
        
        for i, (q, a) in enumerate(self.qa_pairs):
            # Preprocess question
            q_words = self.preprocess_text(q)
            expanded_q_words = set(self.expand_with_synonyms(q_words))
            
            if not q_words:
                continue
            
            # Calculate different similarity metrics
            
            # 1. Exact word overlap (processed words)
            processed_overlap = len(set(query_words).intersection(set(q_words)))
            processed_score = processed_overlap / max(len(query_words), len(q_words), 1)
            
            # 2. Synonym-expanded overlap
            synonym_overlap = len(expanded_query_words.intersection(expanded_q_words))
            synonym_score = synonym_overlap / max(len(expanded_query_words), len(expanded_q_words), 1)
            
            # 3. Original sequence matching (for phrase similarity)
            sequence_score = SequenceMatcher(None, query.lower(), q.lower()).ratio()
            
            # 4. Jaccard similarity on original words
            query_original = set(query.lower().split())
            q_original = set(q.lower().split())
            if query_original or q_original:
                jaccard_score = len(query_original.intersection(q_original)) / len(query_original.union(q_original))
            else:
                jaccard_score = 0
            
            # Combined score with weights
            combined_score = (
                processed_score * 0.3 +
                synonym_score * 0.3 +
                sequence_score * 0.2 +
                jaccard_score * 0.2
            )
            
            if combined_score > best_score:
                best_score = combined_score
                best_answer = a
                best_match_info = f"Q{i}: '{q}' (score: {combined_score:.3f})"
        
        # Use a more reasonable threshold
        threshold = 0.15
        logger.info(f"Best keyword match: {best_match_info}")
        
        if best_score > threshold:
            logger.info(f"Keyword search successful with score: {best_score:.3f}")
            return best_answer
        else:
            logger.info(f"Keyword search failed, best score {best_score:.3f} below threshold {threshold}")
            return None

    def speak(self, text, lang='en'):
        """Improved speak function with better error handling and guaranteed speech output"""
        print(f"\nAssistant: {text}\n")
        self.log_transcript("Assistant", text)
        
        speech_success = False
        
        try:
            if lang != 'en' and self.translator:
                # Use gTTS for non-English languages
                logger.info(f"Using gTTS for language: {lang}")
                tts = gTTS(text=text, lang=lang, slow=False)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    temp_file = fp.name
                    tts.save(temp_file)
                    
                    # Play the audio file
                    if os.name == 'nt':  # Windows
                        try:
                            import pygame
                            pygame.mixer.init()
                            pygame.mixer.music.load(temp_file)
                            pygame.mixer.music.play()
                            while pygame.mixer.music.get_busy():
                                time.sleep(0.1)
                            speech_success = True
                        except ImportError:
                            # Fallback to system command
                            os.system(f'start /min "" "{temp_file}"')
                            time.sleep(len(text) * 0.1 + 2)  # Wait based on text length
                            speech_success = True
                    elif sys.platform == 'darwin':  # macOS
                        os.system(f'afplay "{temp_file}"')
                        speech_success = True
                    else:  # Linux
                        os.system(f'mpg123 "{temp_file}" 2>/dev/null || ffplay -nodisp -autoexit "{temp_file}" 2>/dev/null')
                        speech_success = True
                    
                    # Clean up the temporary file
                    threading.Timer(3.0, lambda: self.cleanup_temp_file(temp_file)).start()
                    
            else:
                # Use pyttsx3 for English (more reliable)
                if self.tts_engine:
                    logger.info("Using pyttsx3 for English speech")
                    try:
                        # Clear any previous speech
                        self.tts_engine.stop()
                        
                        # Set text and speak
                        self.tts_engine.say(text)
                        self.tts_engine.runAndWait()
                        speech_success = True
                        logger.info("Speech completed successfully")
                        
                    except Exception as tts_error:
                        logger.error(f"pyttsx3 error: {tts_error}")
                        # Fallback to gTTS even for English
                        try:
                            logger.info("Falling back to gTTS for English")
                            tts = gTTS(text=text, lang='en', slow=False)
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                                temp_file = fp.name
                                tts.save(temp_file)
                                
                                if os.name == 'nt':  # Windows
                                    os.system(f'start /min "" "{temp_file}"')
                                    time.sleep(len(text) * 0.1 + 2)
                                elif sys.platform == 'darwin':  # macOS
                                    os.system(f'afplay "{temp_file}"')
                                else:  # Linux
                                    os.system(f'mpg123 "{temp_file}" 2>/dev/null')
                                
                                speech_success = True
                                threading.Timer(3.0, lambda: self.cleanup_temp_file(temp_file)).start()
                                
                        except Exception as gtts_error:
                            logger.error(f"gTTS fallback error: {gtts_error}")
                else:
                    logger.warning("No TTS engine available")
                    
        except Exception as e:
            logger.error(f"Speech error: {e}")
            
        if not speech_success:
            logger.warning("Speech synthesis failed - text only output")
            print("🔇 (Speech synthesis failed - check audio settings)")
            
    def cleanup_temp_file(self, filepath):
        """Clean up temporary audio files"""
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
        except Exception as e:
            logger.error(f"Failed to cleanup temp file: {e}")

    def log_transcript(self, speaker, message):
        """Log transcript with error handling"""
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {speaker}: {message}\n")
        except Exception as e:
            logger.error(f"Logging error: {e}")

    def listen_for_wake_word(self):
        """Listen for wake word using Google Speech Recognition"""
        if not self.recognizer or not self.microphone:
            return False
            
        try:
            print("🎤 Listening for wake word...")
            
            with self.microphone as source:
                # Listen for audio with a timeout
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
            
            try:
                # Use Google Speech Recognition
                text = self.recognizer.recognize_google(audio).lower()
                print(f"🔍 Detected: '{text}'")
                
                # Check for wake word variations
                wake_detected = (
                    self.wake_word in text or 
                    'hey shankara' in text or
                    'hey sankara' in text or
                    'shankara' in text or
                    'sankara' in text
                )
                
                if wake_detected:
                    logger.info(f"Wake word detected in: {text}")
                    return True
                    
            except sr.UnknownValueError:
                # Google Speech Recognition could not understand audio
                pass
            except sr.RequestError as e:
                logger.error(f"Could not request results from Google Speech Recognition service; {e}")
                
        except sr.WaitTimeoutError:
            # No audio detected within timeout
            pass
        except Exception as e:
            logger.error(f"Wake word detection error: {e}")
            
        return False

    def listen_for_query(self, timeout=10):
        """Listen for user query using Google Speech Recognition"""
        if not self.recognizer or not self.microphone:
            return "", "en"
            
        try:
            print("🎤 Listening for your question...")
            
            with self.microphone as source:
                # Listen for the query with longer timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
            
            try:
                # Try Google Speech Recognition first
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Google STT: {text}")
                return text.strip(), "en"
                
            except sr.UnknownValueError:
                print("Could not understand audio")
                return "", "en"
            except sr.RequestError as e:
                logger.error(f"Google Speech Recognition error: {e}")
                
                # Fallback: try offline recognition if available
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    logger.info(f"Sphinx STT (fallback): {text}")
                    return text.strip(), "en"
                except:
                    logger.error("All speech recognition methods failed")
                    return "", "en"
                
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout")
            return "", "en"
        except Exception as e:
            logger.error(f"Query listening error: {e}")
            return "", "en"

    def detect_language_and_translate(self, text):
        """Detect language and translate to English if needed"""
        if not self.translator or not text.strip():
            return text, "en"
            
        try:
            # Detect language
            detection = self.translator.detect(text)
            detected_lang = detection.lang
            confidence = detection.confidence
            
            logger.info(f"Detected language: {detected_lang} (confidence: {confidence})")
            
            # If not English and confidence is high, translate
            if detected_lang != 'en' and confidence > 0.7:
                translated = self.translator.translate(text, src=detected_lang, dest='en')
                logger.info(f"Translated '{text}' to '{translated.text}'")
                return translated.text, detected_lang
            else:
                return text, detected_lang
                
        except Exception as e:
            logger.error(f"Language detection/translation error: {e}")
            return text, "en"

    def load_qa_pairs(self):
        """Load Q&A pairs with better error handling"""
        qa_pairs = []
        
        if not os.path.exists(self.qa_file):
            logger.warning(f"Q&A file {self.qa_file} not found, creating sample file")
            self.create_sample_qa_file()
        
        try:
            with open(self.qa_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            if not content:
                logger.warning("Q&A file is empty")
                return []
                
            blocks = content.split('\n\n')
            
            for block in blocks:
                lines = block.strip().split('\n')
                q, a = '', ''
                
                for line in lines:
                    if line.startswith("Q:"):
                        q = line[2:].strip()
                    elif line.startswith("A:"):
                        a = line[2:].strip()
                
                if q and a:
                    qa_pairs.append((q, a))
                    
            logger.info(f"Loaded {len(qa_pairs)} Q&A pairs")
            
        except Exception as e:
            logger.error(f"Failed to load Q&A pairs: {e}")
            
        return qa_pairs

    def create_sample_qa_file(self):
        """Create a sample Q&A file"""
        sample_content = """Q: Who is Shankaracharya?
A: Shankaracharya was a great Indian philosopher and theologian who consolidated the doctrine of Advaita Vedanta. He lived in the 8th century CE and is considered one of the most important spiritual teachers in Hindu philosophy.

Q: What is Advaita Vedanta?
A: Advaita Vedanta is a school of Hindu philosophy that teaches the unity of the soul and Brahman, meaning there is no duality between the individual self and ultimate reality. According to this philosophy, the apparent world is Maya or illusion.

Q: When did Shankara live?
A: Adi Shankara lived in the 8th century CE, approximately 788-820 CE, though some scholars place his dates slightly differently.

Q: What are Shankara's main works?
A: His main works include commentaries on the Upanishads, Bhagavad Gita, and Brahma Sutras, collectively known as the Prasthanatrayi. He also wrote many independent treatises and devotional hymns.

Q: What are the four mathas established by Shankara?
A: Shankara established four mathas or monasteries: Sringeri in Karnataka, Dwarka in Gujarat, Puri in Odisha, and Jyotirmath in Uttarakhand. These serve as centers of Advaitic learning.

Q: What is Maya according to Shankara?
A: According to Shankara, Maya is the cosmic illusion that makes the one Brahman appear as the many phenomenal world. It is neither real nor unreal but is transcended through knowledge of the Self.

Q: What is the goal of human life according to Advaita?
A: According to Advaita Vedanta, the goal of human life is Moksha or liberation, which is the realization that the individual self (Atman) and the ultimate reality (Brahman) are one and the same.

Q: How do you achieve liberation in Advaita?
A: Liberation in Advaita is achieved through Jnana or knowledge - specifically, the direct realization of one's true nature as Brahman. This comes through study, reflection, and meditation under a qualified teacher.
"""
        try:
            with open(self.qa_file, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            logger.info(f"Created sample Q&A file: {self.qa_file}")
        except Exception as e:
            logger.error(f"Failed to create sample Q&A file: {e}")

    def semantic_search(self, query):
        """Semantic search with better error handling and improved threshold"""
        if not self.embedding_model or not self.embeddings or not self.qa_pairs:
            logger.warning("Semantic search components not available")
            return None
            
        try:
            query_embedding = self.embedding_model.encode(query, convert_to_tensor=True)
            scores = util.pytorch_cos_sim(query_embedding, self.embeddings)[0]
            best_score, best_idx = scores.max().item(), int(scores.argmax().item())
            
            logger.info(f"Best semantic match score: {best_score:.3f} for Q{best_idx}: '{self.qa_pairs[best_idx][0]}'")
            
            # Use a slightly lower threshold for semantic search
            return self.qa_pairs[best_idx][1] if best_score > 0.3 else None
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return None

    def hybrid_search(self, query):
        """Enhanced hybrid search with detailed logging"""
        if not query.strip():
            return "I didn't catch that. Could you please repeat your question?"
        
        logger.info(f"Starting hybrid search for query: '{query}'")
        
        # Try enhanced keyword search first
        keyword_result = self.enhanced_keyword_search(query)
        if keyword_result:
            logger.info("Found answer using enhanced keyword search")
            return keyword_result
            
        # Try semantic search
        semantic_result = self.semantic_search(query)
        if semantic_result:
            logger.info("Found answer using semantic search")
            return semantic_result
            
        # Fallback responses with more helpful suggestions
        fallback_responses = [
            "I'm sorry, I couldn't find a relevant answer in my knowledge base. Could you try asking about Shankaracharya's philosophy, his works, or Advaita Vedanta?",
            "I don't have information about that specific topic. You could ask me about Shankara's life, his teachings, or the four mathas he established.",
            "That question is beyond my current knowledge. Try asking about Maya, Brahman, Atman, or other concepts from Advaita Vedanta.",
            "I couldn't match your question to my knowledge base. Perhaps try rephrasing your question about Shankaracharya or Advaita philosophy?"
        ]
        
        import random
        logger.info("No matches found, using fallback response")
        return random.choice(fallback_responses)

    def run(self):
        """Main run loop with better error handling"""
        logger.info("Starting Enhanced Shankara Voice Assistant")
        
        # Check if essential components are available
        if not self.recognizer:
            print("❌ Speech recognition not available")
            return
        if not self.qa_pairs:
            print("❌ No Q&A data available")
            return
        if not self.tts_engine:
            print("⚠️  Warning: TTS engine not available, will use gTTS fallback")
            
        # Print initialization status
        print(f"🔧 Text processing: {'NLTK Enhanced' if NLTK_AVAILABLE else 'Basic'}")
        print(f"🧠 Semantic search: {'Available' if self.embedding_model else 'Unavailable'}")
        print(f"📚 Knowledge base: {len(self.qa_pairs)} Q&A pairs loaded")
            
        # Test TTS before starting
        print("🔊 Testing speech output...")
        self.speak("Hello, I am your enhanced Shankara assistant. Say 'Hey Shankara' to ask me questions about Advaita Vedanta and Shankaracharya's teachings.", lang='en')
        
        consecutive_failures = 0
        max_failures = 5
        
        while consecutive_failures < max_failures:
            try:
                # Listen for wake word
                if self.listen_for_wake_word():
                    self.speak("Yes, I'm listening. What would you like to know?", lang='en')
                    
                    # Listen for the actual query
                    query, _ = self.listen_for_query()
                    
                    if not query.strip():
                        self.speak("I didn't hear your question clearly. Please try again.")
                        continue
                    
                    # Detect language and translate if needed
                    english_query, original_lang = self.detect_language_and_translate(query)
                    
                    self.log_transcript("User", f"{query} (lang: {original_lang})")
                    print(f"👤 User ({original_lang}): {query}")
                    if original_lang != 'en':
                        print(f"🔄 Translated: {english_query}")
                    
                    # Check for exit commands
                    exit_commands = ['exit', 'quit', 'goodbye', 'stop', 'bye', 'thank you', 'thanks']
                    if any(cmd in english_query.lower() for cmd in exit_commands):
                        self.speak("Thank you for learning about Shankaracharya's teachings. Goodbye!", lang='en')
                        break
                    
                    # Get the answer using hybrid search
                    answer = self.hybrid_search(english_query)
                    
                    # Translate answer back to original language if needed
                    if original_lang != 'en' and self.translator:
                        try:
                            translated_answer = self.translator.translate(answer, src='en', dest=original_lang)
                            self.speak(translated_answer.text, lang=original_lang)
                        except Exception as e:
                            logger.error(f"Answer translation error: {e}")
                            self.speak(answer, lang='en')
                    else:
                        self.speak(answer, lang='en')
                    
                    # Reset failure counter on successful interaction
                    consecutive_failures = 0
                        
            except KeyboardInterrupt:
                print("\n👋 Interrupted by user")
                self.speak("Goodbye!", lang='en')
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                consecutive_failures += 1
                if consecutive_failures < max_failures:
                    self.speak("Sorry, I encountered an error. Please try saying 'Hey Shankara' again.")
                
        if consecutive_failures >= max_failures:
            print("❌ Too many consecutive failures. Shutting down.")
            logger.error("Assistant stopped due to repeated failures")

    def test_keyword_search(self):
        """Test function to validate keyword search functionality"""
        print("\n🧪 Testing Enhanced Keyword Search:")
        print("=" * 50)
        
        test_queries = [
            "Who is Shankaracharya?",
            "Tell me about the philosopher Shankara",
            "What is the teaching of Advaita?",
            "How to achieve liberation?",
            "What are the four monasteries?",
            "Explain Maya concept",
            "When did the sage live?",
            "What is the goal of life?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            result = self.enhanced_keyword_search(query)
            if result:
                print(f"✅ Found: {result[:100]}...")
            else:
                print("❌ No match found")
                # Try semantic search as fallback
                semantic_result = self.semantic_search(query)
                if semantic_result:
                    print(f"🔍 Semantic fallback: {semantic_result[:100]}...")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    try:
        # Create assistant
        assistant = ShankaraVoiceAssistant()
        
        # Option to test keyword search functionality
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            assistant.test_keyword_search()
        else:
            # Run normal assistant
            assistant.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure your microphone is working and not muted")
        print("2. Check your internet connection for Google Speech Recognition")
        print("3. Try running: pip install SpeechRecognition pyaudio nltk")
        print("4. On Windows, you might need: pip install pipwin && pipwin install pyaudio")
        print("5. Run with --test flag to test keyword search: python script.py --test")
        import subprocess
import sys
import os
import zipfile
import urllib.request
import json
import logging
import re
import string

# Set up logging for better debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Auto-install required packages ===
required = {
    "speech_recognition": "SpeechRecognition",
    "pyttsx3": "pyttsx3",
    "torch": "torch",
    "sentence_transformers": "sentence-transformers",
    "googletrans": "googletrans==4.0.0rc1",
    "sounddevice": "sounddevice",
    "scipy": "scipy",
    "gtts": "gTTS",
    "pyaudio": "pyaudio",
    "pygame": "pygame",
    "nltk": "nltk"
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
                if package == "pyaudio":
                    logger.info("If PyAudio installation fails, try: pip install pipwin && pipwin install pyaudio")
                # Don't raise - continue with other packages

# Install packages before importing them
try:
    install_packages()
except Exception as e:
    logger.error(f"Package installation error: {e}")
    print("Some packages may not be installed. Continuing anyway...")

# === Main Assistant Code ===
import time
import threading

# Try importing optional packages
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available")

try:
    import sounddevice as sd
    import numpy as np
    from scipy.io.wavfile import write
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    logger.warning("SoundDevice not available")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not available")

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    logger.error("speech_recognition not available - this is required!")

try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True and TORCH_AVAILABLE
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence_transformers not available")

try:
    from googletrans import Translator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    logger.warning("googletrans not available")

try:
    from difflib import SequenceMatcher
    DIFFLIB_AVAILABLE = True
except ImportError:
    DIFFLIB_AVAILABLE = False

try:
    import tempfile
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS not available")

# Try to import NLTK components for enhanced text processing
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    from nltk.tokenize import word_tokenize
    
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    
    NLTK_AVAILABLE = True
    logger.info("NLTK components loaded successfully")
except ImportError:
    NLTK_AVAILABLE = False
    logger.warning("NLTK not available, using basic text processing")

class ShankaraVoiceAssistant:
    def __init__(self, qa_file="shankaracharya_qa.txt"):
        self.qa_file = qa_file
        self.wake_word = "hey shankara"
        self.log_file = "transcript_log.txt"
        self.is_listening = False
        
        # Initialize text processing components
        if NLTK_AVAILABLE:
            self.stemmer = PorterStemmer()
            try:
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
        else:
            self.stemmer = None
            self.stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
        
        # Synonym dictionary for better matching
        self.synonyms = {
            'philosopher': ['thinker', 'sage', 'teacher', 'guru'],
            'teaching': ['doctrine', 'philosophy', 'instruction', 'lesson'],
            'concept': ['idea', 'notion', 'principle'],
            'achieve': ['attain', 'reach', 'obtain', 'get'],
            'goal': ['aim', 'purpose', 'objective', 'target'],
            'established': ['founded', 'created', 'set up', 'built'],
            'liberation': ['freedom', 'release', 'moksha'],
            'reality': ['truth', 'brahman', 'existence'],
            'knowledge': ['wisdom', 'understanding', 'learning', 'jnana']
        }
        
        # Initialize components with error handling
        self.initialize_components()

    def initialize_components(self):
        """Initialize all components with proper error handling"""
        print("🔧 Initializing components...")
        
        # Check critical dependencies first
        if not SR_AVAILABLE:
            print("❌ CRITICAL: speech_recognition module not available!")
            print("Please install it with: pip install SpeechRecognition")
            return
        
        try:
            # Google Speech Recognition - CRITICAL
            self.recognizer = sr.Recognizer()
            
            # Try to get microphone list first
            mic_list = sr.Microphone.list_microphone_names()
            print(f"📱 Available microphones: {len(mic_list)}")
            for i, name in enumerate(mic_list[:3]):  # Show first 3
                print(f"  {i}: {name}")
            
            self.microphone = sr.Microphone()
            
            # Test microphone access
            print("🎤 Testing microphone access...")
            with self.microphone as source:
                print("🔊 Adjusting for ambient noise (this may take a moment)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.recognizer.energy_threshold = 4000  # Adjust sensitivity
                self.recognizer.dynamic_energy_threshold = True
                
            print("✅ Speech Recognition initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Speech Recognition: {e}")
            print("🔧 Troubleshooting tips:")
            print("  - Check if your microphone is connected and not muted")
            print("  - Try: pip install pyaudio")
            print("  - On Windows: pip install pipwin && pipwin install pyaudio")
            self.recognizer = None
            self.microphone = None

        # TTS Engine - Try multiple options
        self.tts_engine = None
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.setup_tts()
                print("✅ pyttsx3 TTS engine initialized")
            except Exception as e:
                print(f"⚠️  pyttsx3 failed: {e}")
                self.tts_engine = None
        
        if not self.tts_engine:
            print("ℹ️  Will use gTTS for text-to-speech")

        # Translator
        self.translator = None
        if TRANSLATOR_AVAILABLE:
            try:
                self.translator = Translator()
                # Test translator
                test = self.translator.detect("hello")
                print("✅ Translator initialized successfully")
            except Exception as e:
                print(f"⚠️  Translator failed: {e}")
                self.translator = None
        else:
            print("⚠️  Translator not available")

        # Sentence Transformer
        self.embedding_model = None
        self.embeddings = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                print("🧠 Loading semantic search model...")
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Semantic search model loaded")
            except Exception as e:
                print(f"⚠️  Semantic search failed: {e}")
                self.embedding_model = None
        else:
            print("⚠️  Semantic search not available (missing torch/sentence-transformers)")

        # Load Q&A pairs
        self.qa_pairs = self.load_qa_pairs()
        if self.embedding_model and self.qa_pairs:
            try:
                questions = [q for q, _ in self.qa_pairs]
                print("🔄 Creating semantic embeddings...")
                self.embeddings = self.embedding_model.encode(questions, convert_to_tensor=True)
                print(f"✅ Created embeddings for {len(self.qa_pairs)} Q&A pairs")
            except Exception as e:
                print(f"⚠️  Failed to create embeddings: {e}")
                self.embeddings = None
        else:
            self.embeddings = None
            
        print("🚀 Initialization complete!")

    def setup_tts(self):
        """Setup TTS with error handling"""
        if not self.tts_engine:
            return
            
        try:
            # Configure TTS properties
            self.tts_engine.setProperty('rate', 150)  # Slower rate for better clarity
            self.tts_engine.setProperty('volume', 1.0)  # Maximum volume
            
            # Test available voices and log them
            voices = self.tts_engine.getProperty('voices')
            if voices and len(voices) > 0:
                print(f"🎵 Found {len(voices)} TTS voices")
                for i, voice in enumerate(voices[:2]):  # Show first 2 voices
                    name = getattr(voice, 'name', 'Unknown')
                    print(f"  Voice {i}: {name}")
                
                # Try to find a better voice
                for voice in voices:
                    if hasattr(voice, 'name') and ('zira' in voice.name.lower() or 'female' in voice.name.lower()):
                        self.tts_engine.setProperty('voice', voice.id)
                        print(f"✅ Using voice: {voice.name}")
                        break
                else:
                    self.tts_engine.setProperty('voice', voices[0].id)
                    print(f"✅ Using default voice")
            else:
                print("⚠️  No TTS voices found")
                
            # Test TTS
            print("🔊 Testing TTS...")
            self.tts_engine.say("TTS test successful")
            self.tts_engine.runAndWait()
            
        except Exception as e:
            print(f"❌ TTS setup error: {e}")
            self.tts_engine = None

    def preprocess_text(self, text):
        """Enhanced text preprocessing with NLTK support"""
        if not text:
            return []
        
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        if NLTK_AVAILABLE and self.stemmer:
            try:
                # Tokenize
                tokens = word_tokenize(text)
                # Remove stop words and stem
                processed_words = [
                    self.stemmer.stem(word) for word in tokens 
                    if word not in self.stop_words and len(word) > 2
                ]
            except:
                # Fallback to basic processing
                words = text.split()
                processed_words = [
                    word for word in words 
                    if word not in self.stop_words and len(word) > 2
                ]
        else:
            # Basic processing without NLTK
            words = text.split()
            processed_words = [
                word for word in words 
                if word not in self.stop_words and len(word) > 2
            ]
        
        return processed_words

    def expand_with_synonyms(self, words):
        """Expand word list with synonyms"""
        expanded_words = set(words)
        
        for word in words:
            if word in self.synonyms:
                expanded_words.update(self.synonyms[word])
            # Also check if any synonym maps to this word
            for key, synonyms in self.synonyms.items():
                if word in synonyms:
                    expanded_words.add(key)
                    expanded_words.update(synonyms)
        
        return list(expanded_words)

    def enhanced_keyword_search(self, query):
        """Enhanced keyword search with better preprocessing and synonym support"""
        if not self.qa_pairs:
            logger.warning("No Q&A pairs available for keyword search")
            return None
        
        # Preprocess query
        query_words = self.preprocess_text(query)
        if not query_words:
            return None
        
        # Expand with synonyms
        expanded_query_words = set(self.expand_with_synonyms(query_words))
        
        best_score = 0
        best_answer = None
        best_match_info = ""
        
        print(f"🔍 Searching with processed words: {query_words}")
        print(f"🔍 Expanded with synonyms: {list(expanded_query_words)[:5]}...")  # Show first 5
        
        for i, (q, a) in enumerate(self.qa_pairs):
            # Preprocess question
            q_words = self.preprocess_text(q)
            expanded_q_words = set(self.expand_with_synonyms(q_words))
            
            if not q_words:
                continue
            
            # Calculate different similarity metrics
            
            # 1. Exact word overlap (processed words)
            processed_overlap = len(set(query_words).intersection(set(q_words)))
            processed_score = processed_overlap / max(len(query_words), len(q_words), 1)
            
            # 2. Synonym-expanded overlap
            synonym_overlap = len(expanded_query_words.intersection(expanded_q_words))
            synonym_score = synonym_overlap / max(len(expanded_query_words), len(expanded_q_words), 1)
            
            # 3. Original sequence matching (for phrase similarity)
            if DIFFLIB_AVAILABLE:
                sequence_score = SequenceMatcher(None, query.lower(), q.lower()).ratio()
            else:
                sequence_score = 0
            
            # 4. Jaccard similarity on original words
            query_original = set(query.lower().split())
            q_original = set(q.lower().split())
            if query_original or q_original:
                jaccard_score = len(query_original.intersection(q_original)) / len(query_original.union(q_original))
            else:
                jaccard_score = 0
            
            # Combined score with weights
            combined_score = (
                processed_score * 0.3 +
                synonym_score * 0.3 +
                sequence_score * 0.2 +
                jaccard_score * 0.2
            )
            
            if combined_score > best_score:
                best_score = combined_score
                best_answer = a
                best_match_info = f"Q{i}: '{q}' (score: {combined_score:.3f})"
        
        # Use a more reasonable threshold
        threshold = 0.15
        print(f"🎯 Best keyword match: {best_match_info}")
        
        if best_score > threshold:
            print(f"✅ Keyword search successful with score: {best_score:.3f}")
            return best_answer
        else:
            print(f"❌ Keyword search failed, best score {best_score:.3f} below threshold {threshold}")
            return None

    def speak(self, text, lang='en'):
        """Improved speak function with guaranteed output"""
        print(f"\n🤖 Assistant: {text}\n")
        self.log_transcript("Assistant", text)
        
        if not text.strip():
            return
        
        # Try pyttsx3 first for English
        if lang == 'en' and self.tts_engine:
            try:
                print("🔊 Speaking with pyttsx3...")
                self.tts_engine.stop()  # Clear any previous speech
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                print("✅ Speech completed")
                return
            except Exception as e:
                print(f"⚠️  pyttsx3 failed: {e}")
        
        # Try gTTS as fallback
        if GTTS_AVAILABLE:
            try:
                print(f"🔊 Speaking with gTTS (lang: {lang})...")
                tts = gTTS(text=text, lang=lang, slow=False)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    temp_file = fp.name
                    tts.save(temp_file)
                    
                    # Play the audio file based on OS
                    if os.name == 'nt':  # Windows
                        try:
                            import pygame
                            pygame.mixer.init()
                            pygame.mixer.music.load(temp_file)
                            pygame.mixer.music.play()
                            while pygame.mixer.music.get_busy():
                                time.sleep(0.1)
                            print("✅ Speech completed with pygame")
                        except ImportError:
                            os.system(f'start /min "" "{temp_file}"')
                            time.sleep(max(len(text) * 0.1, 2))  # Wait based on text length
                            print("✅ Speech completed with system command")
                    elif sys.platform == 'darwin':  # macOS
                        os.system(f'afplay "{temp_file}"')
                        print("✅ Speech completed with afplay")
                    else:  # Linux
                        os.system(f'mpg123 "{temp_file}" 2>/dev/null || ffplay -nodisp -autoexit "{temp_file}" 2>/dev/null')
                        print("✅ Speech completed with mpg123/ffplay")
                    
                    # Clean up the temporary file after a delay
                    threading.Timer(3.0, lambda: self.cleanup_temp_file(temp_file)).start()
                    return
                    
            except Exception as e:
                print(f"⚠️  gTTS failed: {e}")
        
        print("🔇 Speech synthesis not available - text output only")

    def cleanup_temp_file(self, filepath):
        """Clean up temporary audio files"""
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
        except Exception as e:
            logger.error(f"Failed to cleanup temp file: {e}")

    def log_transcript(self, speaker, message):
        """Log transcript with error handling"""
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {speaker}: {message}\n")
        except Exception as e:
            logger.error(f"Logging error: {e}")

    def listen_for_wake_word(self):
        """Listen for wake word using Google Speech Recognition"""
        if not self.recognizer or not self.microphone:
            print("❌ Speech recognition not available")
            return False
            
        try:
            print("👂 Listening for wake word 'Hey Shankara'...")
            
            with self.microphone as source:
                # Listen for audio with a timeout
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=4)
            
            try:
                # Use Google Speech Recognition
                text = self.recognizer.recognize_google(audio, language='en-US').lower()
                print(f"🎤 Heard: '{text}'")
                
                # Check for wake word variations - more flexible
                wake_detected = (
                    'shankara' in text or 
                    'sankara' in text or
                    'hey shankara' in text or
                    'hey sankara' in text or
                    ('hey' in text and ('shank' in text or 'sank' in text))
                )
                
                if wake_detected:
                    print(f"✅ Wake word detected!")
                    return True
                else:
                    print(f"❌ Wake word not detected")
                    
            except sr.UnknownValueError:
                print("🔇 Could not understand audio")
            except sr.RequestError as e:
                print(f"❌ Google Speech Recognition error: {e}")
                print("💡 Check your internet connection")
                
        except sr.WaitTimeoutError:
            # No audio detected - this is normal, don't print anything
            pass
        except Exception as e:
            print(f"❌ Wake word detection error: {e}")
            
        return False

    def listen_for_query(self, timeout=10):
        """Listen for user query using Google Speech Recognition"""
        if not self.recognizer or not self.microphone:
            print("❌ Speech recognition not available")
            return "", "en"
            
        try:
            print("🎤 Listening for your question... (speak now)")
            
            with self.microphone as source:
                # Listen for the query with longer timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            try:
                # Try Google Speech Recognition first
                text = self.recognizer.recognize_google(audio, language='en-US')
                print(f"✅ Understood: '{text}'")
                return text.strip(), "en"
                
            except sr.UnknownValueError:
                print("❌ Could not understand the audio clearly")
                return "", "en"
            except sr.RequestError as e:
                print(f"❌ Google Speech Recognition error: {e}")
                print("💡 Check your internet connection")
                return "", "en"
                
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout")
            return "", "en"
        except Exception as e:
            print(f"❌ Query listening error: {e}")
            return "", "en"

    def detect_language_and_translate(self, text):
        """Detect language and translate to English if needed"""
        if not self.translator or not text.strip():
            return text, "en"
            
        try:
            # Detect language
            detection = self.translator.detect(text)
            detected_lang = detection.lang
            confidence = detection.confidence
            
            print(f"🌐 Language: {detected_lang} (confidence: {confidence:.2f})")
            
            # If not English and confidence is high, translate
            if detected_lang != 'en' and confidence > 0.7:
                translated = self.translator.translate(text, src=detected_lang, dest='en')
                print(f"🔄 Translated: '{text}' → '{translated.text}'")
                return translated.text, detected_lang
            else:
                return text, detected_lang
                
        except Exception as e:
            print(f"⚠️  Translation error: {e}")
            return text, "en"

    def load_qa_pairs(self):
        """Load Q&A pairs with better error handling"""
        qa_pairs = []
        
        if not os.path.exists(self.qa_file):
            print(f"📄 Q&A file {self.qa_file} not found, creating sample file...")
            self.create_sample_qa_file()
        
        try:
            with open(self.qa_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            if not content:
                print("⚠️  Q&A file is empty")
                return []
                
            blocks = content.split('\n\n')
            
            for block in blocks:
                lines = block.strip().split('\n')
                q, a = '', ''
                
                for line in lines:
                    if line.startswith("Q:"):
                        q = line[2:].strip()
                    elif line.startswith("A:"):
                        a = line[2:].strip()
                
                if q and a:
                    qa_pairs.append((q, a))
                    
            print(f"📚 Loaded {len(qa_pairs)} Q&A pairs from {self.qa_file}")
            
        except Exception as e:
            print(f"❌ Failed to load Q&A pairs: {e}")
            
        return qa_pairs

    def create_sample_qa_file(self):
        """Create a sample Q&A file"""
        sample_content = """Q: Who is Shankaracharya?
A: Shankaracharya was a great Indian philosopher and theologian who consolidated the doctrine of Advaita Vedanta. He lived in the 8th century CE and is considered one of the most important spiritual teachers in Hindu philosophy.

Q: What is Advaita Vedanta?
A: Advaita Vedanta is a school of Hindu philosophy that teaches the unity of the soul and Brahman, meaning there is no duality between the individual self and ultimate reality. According to this philosophy, the apparent world is Maya or illusion.

Q: When did Shankara live?
A: Adi Shankara lived in the 8th century CE, approximately 788-820 CE, though some scholars place his dates slightly differently.

Q: What are Shankara's main works?
A: His main works include commentaries on the Upanishads, Bhagavad Gita, and Brahma Sutras, collectively known as the Prasthanatrayi. He also wrote many independent treatises and devotional hymns.

Q: What are the four mathas established by Shankara?
A: Shankara established four mathas or monasteries: Sringeri in Karnataka, Dwarka in Gujarat, Puri in Odisha, and Jyotirmath in Uttarakhand. These serve as centers of Advaitic learning.

Q: What is Maya according to Shankara?
A: According to Shankara, Maya is the cosmic illusion that makes the one Brahman appear as the many phenomenal world. It is neither real nor unreal but is transcended through knowledge of the Self.

Q: What is the goal of human life according to Advaita?
A: According to Advaita Vedanta, the goal of human life is Moksha or liberation, which is the realization that the individual self (Atman) and the ultimate reality (Brahman) are one and the same.

Q: How do you achieve liberation in Advaita?
A: Liberation in Advaita is achieved through Jnana or knowledge - specifically, the direct realization of one's true nature as Brahman. This comes through study, reflection, and meditation under a qualified teacher.
"""
        try:
            with open(self.qa_file, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            print(f"✅ Created sample Q&A file: {self.qa_file}")
        except Exception as e:
            print(f"❌ Failed to create sample Q&A file: {e}")

    def semantic_search(self, query):
        """Semantic search with better error handling and improved threshold"""
        if not self.embedding_model or not self.embeddings or not self.qa_pairs:
            print("⚠️  Semantic search not available")
            return None
            
        try:
            print("🧠 Running semantic search...")
            query_embedding = self.embedding_model.encode(query, convert_to_tensor=True)
            scores = util.pytorch_cos_sim(query_embedding, self.embeddings)[0]
            best_score, best_idx = scores.max().item(), int(scores.argmax().item())
            
            print(f"🎯 Best semantic match: Q{best_idx} (score: {best_score:.3f})")
            print(f"   Question: '{self.qa_pairs[best_idx][0]}'")
            
            # Use a slightly lower threshold for semantic search
            if best_score > 0.3:
                print("✅ Semantic search successful")
                return self.qa_pairs[best_idx][1]
            else:
                print("❌ Semantic search score too low")
                return None
            
        except Exception as e:
            print(f"❌ Semantic search error: {e}")
            return None

    def hybrid_search(self, query):
        """Enhanced hybrid search with detailed logging"""
        if not query.strip():
            return "I didn't catch that. Could you please repeat your question?"
        
        print(f"\n🔍 Searching for answer to: '{query}'")
        print("=" * 60)
        
        # Try enhanced keyword search first
        keyword_result = self.enhanced_keyword_search(query)
        if keyword_result:
            print("✅ Found answer using keyword search")
            return keyword_result
            
        # Try semantic search
        semantic_result = self.semantic_search(query)
        if semantic_result:
            print("✅ Found answer using semantic search")
            return semantic_result
            
        # Fallback responses with more helpful suggestions
        fallback_responses = [
            "I'm sorry, I couldn't find a relevant answer in my knowledge base. Could you try asking about Shankaracharya's philosophy, his works, or Advaita Vedanta?",
            "I don't have information about that specific topic. You could ask me about Shankara's life, his teachings, or the four mathas he established.",
            "That question is beyond my current knowledge. Try asking about Maya, Brahman, Atman, or other concepts from Advaita Vedanta.",
            "I couldn't match your question to my knowledge base. Perhaps try rephrasing your question about Shankaracharya or Advaita philosophy?"
        ]
        
        import random
        print("❌ No matches found, using fallback response")
        return random.choice(fallback_responses)

    def test_components(self):
        """Test all components to diagnose issues"""
        print("\n🧪 COMPONENT DIAGNOSTIC TEST")
        print("=" * 50)
        
        # Test microphone
        if self.recognizer and self.microphone:
            print("✅ Speech Recognition: Available")
            try:
                with self.microphone as source:
                    print("🎤 Testing microphone... (say something)")
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio)
                    print(f"✅ Microphone test successful: '{text}'")
            except Exception as e:
                print(f"❌ Microphone test failed: {e}")
        else:
            print("❌ Speech Recognition: Not available")
        
        # Test TTS
        if self.tts_engine:
            print("✅ pyttsx3 TTS: Available")
            try:
                self.tts_engine.say("TTS test")
                self.tts_engine.runAndWait()
                print("✅ pyttsx3 test successful")
            except Exception as e:
                print(f"❌ pyttsx3 test failed: {e}")
        else:
            print("❌ pyttsx3 TTS: Not available")
        
        if GTTS_AVAILABLE:
            print("✅ gTTS: Available")
        else:
            print("❌ gTTS: Not available")
        
        # Test semantic search
        if self.embedding_model:
            print("✅ Semantic Search: Available")
        else:
            print("❌ Semantic Search: Not available")
        
        # Test Q&A data
        print(f"📚 Q&A Pairs: {len(self.qa_pairs)} loaded")
        
        print("=" * 50)

    def run_interactive_mode(self):
        """Run in interactive text mode for testing"""
        print("\n💬 INTERACTIVE TEXT MODE")
        print("Type your questions (or 'quit' to exit):")
        print("-" * 40)
        
        while True:
            try:
                query = input("\n👤 You: ").strip()
                
                if not query:
                    continue
                    
                if query.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                answer = self.hybrid_search(query)
                print(f"\n🤖 Assistant: {answer}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def run(self):
        """Main run loop with better error handling and diagnostics"""
        print("\n🚀 ENHANCED SHANKARA VOICE ASSISTANT")
        print("=" * 50)
        
        # Run component diagnostics first
        self.test_components()
        
        # Check if critical components are available
        if not self.recognizer:
            print("\n❌ CRITICAL ERROR: Speech recognition not available!")
            print("🔧 Please install required packages:")
            print("   pip install SpeechRecognition pyaudio")
            print("\n💬 Would you like to try text mode instead? (y/n)")
            choice = input().strip().lower()
            if choice in ['y', 'yes']:
                self.run_interactive_mode()
            return
        
        if not self.qa_pairs:
            print("❌ No Q&A data available")
            return
            
        # Print status summary
        print(f"\n📊 STATUS SUMMARY:")
        print(f"🎤 Speech Recognition: {'✅' if self.recognizer else '❌'}")
        print(f"🔊 Text-to-Speech: {'✅' if (self.tts_engine or GTTS_AVAILABLE) else '❌'}")
        print(f"🧠 Semantic Search: {'✅' if self.embedding_model else '❌'}")
        print(f"🌐 Translation: {'✅' if self.translator else '❌'}")
        print(f"📚 Knowledge Base: {len(self.qa_pairs)} Q&A pairs")
        
        # Test speech output before starting
        print("\n🔊 Testing speech output...")
        self.speak("Hello! I am your Shankara assistant. I'm ready to answer questions about Advaita Vedanta and Shankaracharya's teachings.")
        
        print("\n" + "=" * 50)
        print("🎤 VOICE MODE ACTIVE")
        print("💡 Say 'Hey Shankara' to ask questions")
        print("💡 Press Ctrl+C to exit")
        print("=" * 50)
        
        consecutive_failures = 0
        max_failures = 10
        successful_interactions = 0
        
        while consecutive_failures < max_failures:
            try:
                # Listen for wake word
                if self.listen_for_wake_word():
                    self.speak("Yes, I'm listening. What would you like to know?")
                    
                    # Listen for the actual query
                    query, _ = self.listen_for_query()
                    
                    if not query.strip():
                        self.speak("I didn't hear your question clearly. Please try saying 'Hey Shankara' again.")
                        continue
                    
                    # Log the interaction
                    self.log_transcript("User", query)
                    print(f"\n👤 User: {query}")
                    
                    # Check for exit commands
                    exit_commands = ['exit', 'quit', 'goodbye', 'stop', 'bye', 'thank you', 'thanks']
                    if any(cmd in query.lower() for cmd in exit_commands):
                        self.speak("Thank you for learning about Shankaracharya's teachings. May you find wisdom and peace. Goodbye!")
                        break
                    
                    # Detect language and translate if needed
                    english_query, original_lang = self.detect_language_and_translate(query)
                    
                    if original_lang != 'en':
                        print(f"🔄 Translated to English: {english_query}")
                    
                    # Get the answer using hybrid search
                    answer = self.hybrid_search(english_query)
                    
                    # Translate answer back to original language if needed
                    if original_lang != 'en' and self.translator:
                        try:
                            translated_answer = self.translator.translate(answer, src='en', dest=original_lang)
                            self.speak(translated_answer.text, lang=original_lang)
                        except Exception as e:
                            print(f"⚠️  Answer translation failed: {e}")
                            self.speak(answer, lang='en')
                    else:
                        self.speak(answer, lang='en')
                    
                    # Reset failure counter and increment success counter
                    consecutive_failures = 0
                    successful_interactions += 1
                    
                    if successful_interactions == 1:
                        print("🎉 First successful interaction! The assistant is working properly.")
                        
            except KeyboardInterrupt:
                print("\n👋 Interrupted by user")
                self.speak("Goodbye! Om Shanti Shanti Shanti.")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                consecutive_failures += 1
                if consecutive_failures < max_failures:
                    print(f"⚠️  Error count: {consecutive_failures}/{max_failures}")
                    self.speak("Sorry, I encountered an error. Please try saying 'Hey Shankara' again.")
                
        if consecutive_failures >= max_failures:
            print("❌ Too many consecutive failures. Shutting down.")
            print("🔧 Please check your microphone and internet connection.")

    def test_keyword_search(self):
        """Test function to validate keyword search functionality"""
        print("\n🧪 TESTING ENHANCED KEYWORD SEARCH")
        print("=" * 60)
        
        test_queries = [
            "Who is Shankaracharya?",
            "Tell me about the philosopher Shankara",
            "What is the teaching of Advaita?",
            "How to achieve liberation?",
            "What are the four monasteries?",
            "Explain Maya concept",
            "When did the sage live?",
            "What is the goal of life?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: '{query}'")
            print("-" * 40)
            
            # Test keyword search
            keyword_result = self.enhanced_keyword_search(query)
            if keyword_result:
                print(f"✅ Keyword: {keyword_result[:80]}...")
            else:
                print("❌ Keyword: No match")
            
            # Test semantic search if available
            if self.embedding_model:
                semantic_result = self.semantic_search(query)
                if semantic_result:
                    print(f"✅ Semantic: {semantic_result[:80]}...")
                else:
                    print("❌ Semantic: No match")
            
            # Test hybrid
            hybrid_result = self.hybrid_search(query)
            print(f"🔄 Final: {hybrid_result[:80]}...")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        # Create assistant
        assistant = ShankaraVoiceAssistant()
        
        # Handle command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--test":
                assistant.test_keyword_search()
            elif sys.argv[1] == "--text":
                assistant.run_interactive_mode()
            elif sys.argv[1] == "--diagnostic":
                assistant.test_components()
            else:
                print("Available options:")
                print("  --test      : Test keyword search functionality")
                print("  --text      : Run in text-only interactive mode")
                print("  --diagnostic: Run component diagnostic tests")
                print("  (no args)   : Run normal voice assistant")
        else:
            # Run normal assistant
            assistant.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        print("\n🔧 TROUBLESHOOTING GUIDE:")
        print("=" * 40)
        print("1. 🎤 Microphone issues:")
        print("   - Check if microphone is connected and not muted")
        print("   - Test microphone in other applications")
        print("   - Try: pip install pyaudio")
        print("   - Windows: pip install pipwin && pipwin install pyaudio")
        
        print("\n2. 📦 Package issues:")
        print("   - Try: pip install --upgrade SpeechRecognition pyttsx3 gTTS")
        print("   - For semantic search: pip install torch sentence-transformers")
        
        print("\n3. 🌐 Internet connection:")
        print("   - Google Speech Recognition requires internet")
        print("   - Check your network connection")
        
        print("\n4. 🔊 Audio output issues:")
        print("   - Check system volume and audio drivers")
        print("   - Try different TTS engines")
        
        print("\n5. 🧪 Test modes:")
        print("   - Run: python script.py --diagnostic")
        print("   - Run: python script.py --text (for text-only mode)")
        print("   - Run: python script.py --test (test search functions)")
        
        print("\n💡 If issues persist, try text mode: python script.py --text")