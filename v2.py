import subprocess
import sys
import os
import zipfile
import urllib.request
import json
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Install speech recognition packages ===
required = {
    "speech_recognition": "SpeechRecognition",
    "pyaudio": "pyaudio",
    "pyttsx3": "pyttsx3",
    "vosk": "vosk",
    "pocketsphinx": "pocketsphinx"
}

def install_packages():
    """Install required packages"""
    for module, package in required.items():
        try:
            __import__(module)
            logger.info(f"Package {module} already installed")
        except ImportError:
            try:
                logger.info(f"Installing missing package: {package}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.info(f"Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {package}: {e}")
                # For pyaudio, try alternative installation
                if package == "pyaudio":
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", "pipwin"])
                        subprocess.check_call([sys.executable, "-m", "pipwin", "install", "pyaudio"])
                    except:
                        print("Please install PyAudio manually if you encounter issues")

# Install packages
install_packages()

# Import modules
import speech_recognition as sr
import pyttsx3
from difflib import SequenceMatcher
import threading

class ImprovedSpeechAssistant:
    def __init__(self, qa_file="shankaracharya_qa.txt"):
        self.qa_file = qa_file
        self.wake_words = ["hey shankara", "shankara", "sankara", "hey sankara"]
        self.log_file = "transcript_log.txt"
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Configure recognition settings for better accuracy
        self.configure_recognition()
        
        # Initialize TTS
        self.initialize_tts()
        
        # Load Q&A data
        self.qa_pairs = self.load_qa_pairs()
        
        # Test microphone
        self.test_microphone()

    def configure_recognition(self):
        """Configure speech recognition for better accuracy"""
        try:
            # Adjust for ambient noise
            print("🎤 Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            # Configure recognition parameters for better accuracy
            self.recognizer.energy_threshold = 300  # Adjust based on your environment
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8  # How long to wait for pause
            self.recognizer.phrase_threshold = 0.3  # Minimum length of phrase
            self.recognizer.non_speaking_duration = 0.8  # How long of non-speaking audio before a phrase is complete
            
            print("✅ Microphone calibrated successfully")
            
        except Exception as e:
            print(f"❌ Error configuring microphone: {e}")

    def initialize_tts(self):
        """Initialize text-to-speech"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
            print("✅ Text-to-speech initialized")
        except Exception as e:
            print(f"❌ TTS initialization failed: {e}")
            self.tts_engine = None

    def speak(self, text):
        """Speak the given text"""
        print(f"\n🤖 Assistant: {text}\n")
        self.log_transcript("Assistant", text)
        
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")

    def log_transcript(self, speaker, message):
        """Log conversation to file"""
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {speaker}: {message}\n")
        except Exception as e:
            logger.error(f"Logging error: {e}")

    def test_microphone(self):
        """Test microphone functionality"""
        print("\n🧪 MICROPHONE TEST")
        print("=" * 40)
        print("Say something for 3 seconds to test your microphone...")
        
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                
            print("🔄 Processing audio...")
            
            # Try multiple recognition engines for comparison
            results = self.test_multiple_engines(audio)
            
            if any(results.values()):
                print("✅ Microphone test successful!")
                for engine, result in results.items():
                    if result:
                        print(f"   {engine}: '{result}'")
            else:
                print("❌ No speech detected. Please check:")
                print("   1. Microphone is connected and working")
                print("   2. Microphone volume is adequate")
                print("   3. You're speaking clearly and loudly enough")
                
        except sr.WaitTimeoutError:
            print("❌ No audio detected - microphone timeout")
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")

    def test_multiple_engines(self, audio):
        """Test multiple speech recognition engines"""
        results = {}
        
        # Test Google Speech Recognition (online)
        try:
            result = self.recognizer.recognize_google(audio)
            results["Google"] = result
        except:
            results["Google"] = None
            
        # Test Sphinx (offline)
        try:
            result = self.recognizer.recognize_sphinx(audio)
            results["Sphinx"] = result
        except:
            results["Sphinx"] = None
            
        return results

    def listen_for_speech(self, timeout=5, phrase_time_limit=None):
        """Listen for speech with multiple recognition attempts"""
        try:
            print("🎤 Listening...")
            
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            print("🔄 Processing speech...")
            
            # Try multiple recognition methods
            recognized_text = None
            
            # Method 1: Google Speech Recognition (most accurate, requires internet)
            try:
                text = self.recognizer.recognize_google(audio)
                if text.strip():
                    print(f"🎯 Google recognized: '{text}'")
                    recognized_text = text
            except sr.UnknownValueError:
                print("🔍 Google couldn't understand the audio")
            except sr.RequestError as e:
                print(f"🌐 Google Speech Recognition error: {e}")
            except Exception as e:
                print(f"❌ Google recognition error: {e}")
            # Method 2: Sphinx (offline backup)
            if not recognized_text:
                if hasattr(self.recognizer, "recognize_sphinx"):
                    try:
                        text = self.recognizer.recognize_sphinx(audio)
                        if text.strip():
                            print(f"🎯 Sphinx recognized: '{text}'")
                            recognized_text = text
                    except sr.UnknownValueError:
                        print("🔍 Sphinx couldn't understand the audio")
                    except Exception as e:
                        print(f"❌ Sphinx recognition error: {e}")
                else:
                    print("⚠️ Sphinx recognition is not available (pocketsphinx not installed)")
                    print(f"❌ Sphinx recognition error: {e}")
            
            # Method 3: Show what we got
            if recognized_text:
                return recognized_text.lower().strip()
            else:
                print("❌ No speech could be recognized")
                return ""
                
        except sr.WaitTimeoutError:
            print("⏰ Listening timeout - no speech detected")
            return ""
        except Exception as e:
            print(f"❌ Speech recognition error: {e}")
            return ""

    def check_wake_word(self, text):
        """Check if wake word is present"""
        if not text:
            return False
            
        print(f"🔍 Checking for wake word in: '{text}'")
        
        text_lower = text.lower()
        
        # Check exact wake words
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                print(f"✅ Found wake word: '{wake_word}'")
                return True
        
        # Check individual key words
        words = text_lower.split()
        key_words = ['shankara', 'sankara', 'shankra', 'shankara']
        
        for word in words:
            for key_word in key_words:
                # Use fuzzy matching for similar sounding words
                similarity = SequenceMatcher(None, word, key_word).ratio()
                if similarity > 0.7:  # 70% similarity
                    print(f"✅ Found similar wake word: '{word}' (matches '{key_word}' at {similarity:.2f})")
                    return True
        
        print(f"❌ No wake word found")
        return False

    def load_qa_pairs(self):
        """Load Q&A pairs from file"""
        qa_pairs = []
        
        if not os.path.exists(self.qa_file):
            self.create_sample_qa_file()
        
        try:
            with open(self.qa_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
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
                    
            print(f"✅ Loaded {len(qa_pairs)} Q&A pairs")
            
        except Exception as e:
            print(f"❌ Error loading Q&A pairs: {e}")
            
        return qa_pairs

    def create_sample_qa_file(self):
        """Create sample Q&A file"""
        sample_content = """Q: Who is Shankaracharya?
A: Shankaracharya was a great Indian philosopher and theologian who consolidated the doctrine of Advaita Vedanta. He lived in the 8th century CE.

Q: What is Advaita Vedanta?
A: Advaita Vedanta teaches the unity of the soul and Brahman. Advaita means non-duality, emphasizing no difference between individual self and ultimate reality.

Q: When did Shankara live?
A: Adi Shankara lived in the 8th century CE, approximately between 788 and 820 CE.

Q: What are Shankara's main works?
A: His main works include commentaries on the Upanishads, Bhagavad Gita, and Brahma Sutras, known as the Prasthanatrayi.

Q: What is Brahman?
A: Brahman is the ultimate reality, pure consciousness, existence, and bliss. It is beyond all attributes and is both material and efficient cause of the universe.

Q: What is Maya?
A: Maya is the cosmic illusion that makes the one Brahman appear as diverse forms of the universe. It is neither real nor unreal.

Q: Hello
A: Hello! I am your Shankara assistant. I can answer questions about Shankaracharya and Advaita Vedanta. What would you like to know?

Q: How are you?
A: I am doing well, thank you! I am here to help you learn about Shankaracharya's teachings. What would you like to know about Advaita Vedanta?"""

        try:
            with open(self.qa_file, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            print(f"✅ Created Q&A file: {self.qa_file}")
        except Exception as e:
            print(f"❌ Failed to create Q&A file: {e}")

    def find_best_answer(self, query):
        """Find best matching answer"""
        if not self.qa_pairs or not query.strip():
            return "I didn't understand your question. Could you please ask about Shankaracharya or Advaita Vedanta?"
            
        query_lower = query.lower().strip()
        best_score = 0
        best_answer = ""
        matched_question = ""
        
        print(f"🔍 Searching for: '{query}'")
        
        for q, a in self.qa_pairs:
            q_lower = q.lower()
            
            # Multiple matching strategies
            scores = []
            
            # 1. Exact substring match
            if query_lower in q_lower or q_lower in query_lower:
                scores.append(0.9)
            
            # 2. Word overlap
            query_words = set(query_lower.split())
            q_words = set(q_lower.split())
            
            if query_words and q_words:
                intersection = query_words.intersection(q_words)
                union = query_words.union(q_words)
                word_score = len(intersection) / len(union) if union else 0
                scores.append(word_score * 0.8)
            
            # 3. Sequence similarity
            seq_score = SequenceMatcher(None, query_lower, q_lower).ratio()
            scores.append(seq_score * 0.6)
            
            # 4. Key word matching
            key_words = ['who', 'what', 'when', 'where', 'how', 'why']
            query_key_words = [w for w in query_words if w in key_words]
            q_key_words = [w for w in q_words if w in key_words]
            
            if query_key_words and q_key_words:
                key_match = len(set(query_key_words).intersection(set(q_key_words))) > 0
                if key_match:
                    scores.append(0.3)
            
            # Take the best score
            current_score = max(scores) if scores else 0
            
            if current_score > best_score:
                best_score = current_score
                best_answer = a
                matched_question = q
        
        print(f"🎯 Best match (score: {best_score:.3f}): '{matched_question}'")
        
        if best_score > 0.15:  # Lower threshold for better matching
            return best_answer
        else:
            return "I'm sorry, I couldn't find a relevant answer. Please ask me about Shankaracharya, Advaita Vedanta, Brahman, Maya, or his philosophical teachings."

    def run(self):
        """Main application loop"""
        print("\n🕉️  IMPROVED SHANKARA VOICE ASSISTANT")
        print("=" * 50)
        print("Features:")
        print("• Multiple speech recognition engines")
        print("• Improved wake word detection")
        print("• Better audio processing")
        print("• Real-time feedback on what's heard")
        print("=" * 50)
        
        self.speak("Hello! I am your improved Shankara assistant. Say Hey Shankara to start.")
        
        while True:
            try:
                print(f"\n--- Listening for Wake Word ---")
                print("Say: 'Hey Shankara' or just 'Shankara'")
                
                # Listen for wake word
                wake_text = self.listen_for_speech(timeout=10, phrase_time_limit=4)
                
                if not wake_text:
                    print("No speech detected. Please try again.")
                    continue
                
                print(f"👂 I heard: '{wake_text}'")
                
                # Check for wake word
                if self.check_wake_word(wake_text):
                    self.speak("Yes, I'm listening. What would you like to know about Shankaracharya?")
                    
                    print(f"\n--- Listening for Your Question ---")
                    
                    # Listen for question
                    question = self.listen_for_speech(timeout=15, phrase_time_limit=8)
                    
                    if not question:
                        self.speak("I didn't hear your question. Please try again.")
                        continue
                    
                    print(f"👤 Your question: '{question}'")
                    self.log_transcript("User", question)
                    
                    # Check for exit
                    if any(word in question.lower() for word in ['exit', 'quit', 'goodbye', 'stop', 'bye']):
                        self.speak("Goodbye! May you find peace and wisdom in your spiritual journey.")
                        break
                    
                    # Find and speak answer
                    answer = self.find_best_answer(question)
                    self.speak(answer)
                    
                else:
                    print(f"'{wake_text}' is not a wake word. Please say 'Hey Shankara' or 'Shankara'")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                logger.error(f"Main loop error: {e}")

if __name__ == "__main__":
    try:
        assistant = ImprovedSpeechAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")