import subprocess
import sys
import os
import zipfile
import urllib.request
import json
import logging

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
    "pygame": "pygame"
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

class ShankaraVoiceAssistant:
    def __init__(self, qa_file="shankaracharya_qa.txt"):
        self.qa_file = qa_file
        self.wake_word = "hey shankara"
        self.log_file = "transcript_log.txt"
        self.is_listening = False
        
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
                        import winsound
                        # Convert MP3 to WAV for Windows playback
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

    def keyword_search(self, query):
        """Keyword-based search with improved matching"""
        if not self.qa_pairs:
            return None
            
        query_lower = query.lower()
        best_ratio, best_answer = 0, ""
        
        for q, a in self.qa_pairs:
            q_lower = q.lower()
            
            # Check for exact word matches first
            query_words = set(query_lower.split())
            q_words = set(q_lower.split())
            
            if len(query_words.union(q_words)) == 0:
                continue
                
            word_overlap = len(query_words.intersection(q_words)) / len(query_words.union(q_words))
            
            # Sequence matching
            sequence_ratio = SequenceMatcher(None, query_lower, q_lower).ratio()
            
            # Combined score
            combined_ratio = (word_overlap * 0.6) + (sequence_ratio * 0.4)
            
            if combined_ratio > best_ratio:
                best_ratio, best_answer = combined_ratio, a
                
        return best_answer if best_ratio > 0.25 else None

    def semantic_search(self, query):
        """Semantic search with better error handling"""
        if not self.embedding_model or not self.embeddings or not self.qa_pairs:
            return None
            
        try:
            query_embedding = self.embedding_model.encode(query, convert_to_tensor=True)
            scores = util.pytorch_cos_sim(query_embedding, self.embeddings)[0]
            best_score, best_idx = scores.max().item(), int(scores.argmax().item())
            
            logger.info(f"Best semantic match score: {best_score:.3f}")
            return self.qa_pairs[best_idx][1] if best_score > 0.35 else None
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return None

    def hybrid_search(self, query):
        """Hybrid search combining keyword and semantic approaches"""
        if not query.strip():
            return "I didn't catch that. Could you please repeat your question?"
            
        # Try keyword search first
        keyword_result = self.keyword_search(query)
        if keyword_result:
            logger.info("Found answer using keyword search")
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
            "That question is beyond my current knowledge. Try asking about Maya, Brahman, Atman, or other concepts from Advaita Vedanta."
        ]
        
        import random
        return random.choice(fallback_responses)

    def run(self):
        """Main run loop with better error handling"""
        logger.info("Starting Shankara Voice Assistant")
        
        # Check if essential components are available
        if not self.recognizer:
            print("❌ Speech recognition not available")
            return
        if not self.qa_pairs:
            print("❌ No Q&A data available")
            return
        if not self.tts_engine:
            print("⚠️  Warning: TTS engine not available, will use gTTS fallback")
            
        # Test TTS before starting
        print("🔊 Testing speech output...")
        self.speak("Hello, I am your Shankara assistant. Say 'Hey Shankara' to ask me questions about Advaita Vedanta and Shankaracharya's teachings.", lang='en')
        
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

if __name__ == "__main__":
    try:
        # Create and run assistant
        assistant = ShankaraVoiceAssistant()
        assistant.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure your microphone is working and not muted")
        print("2. Check your internet connection for Google Speech Recognition")
        print("3. Try running: pip install SpeechRecognition pyaudio")
        print("4. On Windows, you might need: pip install pipwin && pipwin install pyaudio")