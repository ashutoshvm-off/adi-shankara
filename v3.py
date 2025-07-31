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
    import sounddevice as sd
    import numpy as np
    from scipy.io.wavfile import write
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
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True and TORCH_AVAILABLE
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from googletrans import Translator
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
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Try to import NLTK components
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    from nltk.tokenize import word_tokenize
    
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

class NaturalShankaraAssistant:
    def __init__(self, qa_file="shankaracharya_qa.txt"):
        self.qa_file = qa_file
        self.log_file = "conversation_log.txt"
        self.conversation_context = []
        self.user_name = None
        self.conversation_started = False
        
        # More natural, human-like conversation starters
        self.conversation_starters = [
            "Hey there! You know, I was just thinking about some deep philosophical stuff. What's on your mind today?",
            "Hi! I love talking about life, consciousness, and all those big questions. What brings you here?",
            "Hello! So nice to meet someone who's curious about deeper things. What would you like to explore?",
            "Hey! I find these ancient teachings about consciousness absolutely fascinating. What draws your interest?",
            "Hi there! You know what I love? Good conversations about the nature of reality. What's got you thinking lately?"
        ]
        
        # Natural responses - much more casual
        self.casual_responses = [
            "Oh, that's interesting!",
            "Yeah, I totally get that.",
            "You know what? That's a really good question.",
            "Hmm, that makes me think...",
            "Oh wow, that's deep!",
            "I love that you're asking about this.",
            "That's something I think about a lot too.",
            "You're really getting to the heart of it here."
        ]
        
        # Natural transitions
        self.natural_transitions = [
            "So here's what I think about that...",
            "You know, the way I see it...",
            "From what I understand...",
            "The way it was explained to me...",
            "I've always found it helpful to think of it like this...",
            "What really clicks for me is...",
            "The cool thing about this is...",
            "What I find amazing is..."
        ]
        
        # Casual follow-ups
        self.follow_ups = [
            "Does that make sense to you?",
            "What do you think about that?",
            "Have you ever thought about it that way?",
            "How does that land with you?",
            "What's your take on this?",
            "Does that resonate at all?",
            "Am I making any sense here?",
            "What comes up for you when I say that?"
        ]
        
        # Encouraging responses
        self.encouragements = [
            "I love that you're thinking about this stuff.",
            "These are exactly the right questions to be asking.",
            "You're really digging into the important stuff here.",
            "It's so cool that you're exploring this.",
            "This kind of curiosity is awesome."
        ]
        
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
        
        # Initialize components
        self.initialize_components()

    def initialize_components(self):
        """Initialize all components with proper error handling"""
        print("Getting everything ready for our chat...")
        
        if not SR_AVAILABLE:
            print("Looks like we'll need to stick to typing for now - that's totally fine!")
            return
        
        try:
            # Speech Recognition
            self.recognizer = sr.Recognizer()
            mic_list = sr.Microphone.list_microphone_names()
            self.microphone = sr.Microphone()
            
            # Adjust for natural conversation
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.recognizer.energy_threshold = 3000
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8
                self.recognizer.phrase_threshold = 0.3
                
            print("Cool, I can hear you!")
            
        except Exception as e:
            print(f"Hmm, having some mic issues: {e}")
            self.recognizer = None
            self.microphone = None

        # TTS Engine setup
        self.tts_engine = None
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.setup_natural_voice()
                print("Voice is working great!")
            except Exception as e:
                print(f"Voice stuff needs some tweaking: {e}")
                self.tts_engine = None

        # Translator
        self.translator = None
        if TRANSLATOR_AVAILABLE:
            try:
                self.translator = Translator()
                test = self.translator.detect("hello")
                print("Language stuff is good to go!")
            except Exception as e:
                self.translator = None

        # Semantic search
        self.embedding_model = None
        self.embeddings = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                print("Loading up the smart stuff...")
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                self.embedding_model = None

        # Load knowledge base
        self.qa_pairs = self.load_qa_pairs()
        if self.embedding_model and self.qa_pairs:
            try:
                questions = [q for q, _ in self.qa_pairs]
                self.embeddings = self.embedding_model.encode(questions, convert_to_tensor=True)
                print(f"Awesome! I've got {len(self.qa_pairs)} things I can chat about!")
            except Exception as e:
                self.embeddings = None
                
        print("Alright, we're all set! Let's chat!\n")

    def setup_natural_voice(self):
        """Setup TTS for natural, conversational speech"""
        if not self.tts_engine:
            return
            
        try:
            # More natural speaking pace
            self.tts_engine.setProperty('rate', 160)  # A bit faster, more conversational
            self.tts_engine.setProperty('volume', 0.9)
            
            voices = self.tts_engine.getProperty('voices')
            if voices and len(voices) > 0:
                # Try to find a nice voice
                for voice in voices:
                    if hasattr(voice, 'name'):
                        name_lower = voice.name.lower()
                        if any(word in name_lower for word in ['zira', 'female', 'david']):
                            self.tts_engine.setProperty('voice', voice.id)
                            break
                else:
                    self.tts_engine.setProperty('voice', voices[0].id)
                    
        except Exception as e:
            logger.error(f"Voice setup error: {e}")

    def speak_naturally(self, text, pause_before=0.3, pause_after=0.5):
        """Speak with natural timing"""
        time.sleep(pause_before)
        
        print(f"\n{text}\n")
        self.log_conversation("Me", text)
        
        if not text.strip():
            return
        
        # Try pyttsx3 first
        if self.tts_engine:
            try:
                self.tts_engine.stop()
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                time.sleep(pause_after)
                return
                
            except Exception as e:
                pass
        
        # Fallback to gTTS
        if GTTS_AVAILABLE:
            try:
                tts = gTTS(text=text, lang='en', slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    temp_file = fp.name
                    tts.save(temp_file)
                    
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
                        os.system(f'mpg123 "{temp_file}" 2>/dev/null')
                    
                    threading.Timer(3.0, lambda: self.cleanup_temp_file(temp_file)).start()
                    time.sleep(pause_after)
                    
            except Exception as e:
                pass

    def listen_naturally(self, timeout=10, phrase_time_limit=15):
        """Listen for natural speech"""
        if not self.recognizer or not self.microphone:
            return ""
            
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            try:
                text = self.recognizer.recognize_google(audio, language='en-US')
                return text.strip()
                
            except sr.UnknownValueError:
                return ""
            except sr.RequestError as e:
                return ""
                
        except sr.WaitTimeoutError:
            return ""
        except Exception as e:
            return ""

    def cleanup_temp_file(self, filepath):
        """Clean up temporary audio files"""
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
        except:
            pass

    def log_conversation(self, speaker, message):
        """Log the conversation"""
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {speaker}: {message}\n")
        except Exception as e:
            logger.error(f"Logging error: {e}")

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

    def preprocess_text(self, text):
        """Enhanced text preprocessing"""
        if not text:
            return []
        
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        if NLTK_AVAILABLE and self.stemmer:
            try:
                tokens = word_tokenize(text)
                processed_words = [
                    self.stemmer.stem(word) for word in tokens 
                    if word not in self.stop_words and len(word) > 2
                ]
            except:
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
        """Enhanced search"""
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
            
            if DIFFLIB_AVAILABLE:
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

    def semantic_search(self, query):
        """Semantic search"""
        if not self.embedding_model or not self.embeddings or not self.qa_pairs:
            return None
            
        try:
            query_embedding = self.embedding_model.encode(query, convert_to_tensor=True)
            scores = util.pytorch_cos_sim(query_embedding, self.embeddings)[0]
            best_score, best_idx = scores.max().item(), int(scores.argmax().item())
            
            return self.qa_pairs[best_idx][1] if best_score > 0.3 else None
            
        except Exception as e:
            return None

    def create_natural_response(self, answer, query):
        """Create a natural, human-like response"""
        if not answer:
            return self.create_natural_unknown_response()
        
        # Sometimes just give a casual response
        if random.random() < 0.3:
            casual = random.choice(self.casual_responses)
            return f"{casual} {answer} {random.choice(self.follow_ups)}"
        
        # Sometimes add a natural transition
        if random.random() < 0.5:
            transition = random.choice(self.natural_transitions)
            return f"{transition} {answer}"
        
        # Sometimes add encouragement
        if random.random() < 0.2:
            encouragement = random.choice(self.encouragements)
            return f"{encouragement} {answer} {random.choice(self.follow_ups)}"
        
        # Otherwise just give the answer naturally
        return f"{answer} {random.choice(self.follow_ups) if random.random() < 0.4 else ''}"

    def create_natural_unknown_response(self):
        """Create casual response when answer isn't known"""
        responses = [
            "Hmm, that's a really interesting question! I'm not sure I have a great answer for that specific thing, but I love that you're thinking about it. What got you curious about this?",
            
            "You know, that's something I haven't really thought about in depth. But it sounds fascinating! What draws you to that particular question?",
            
            "Oh wow, that's deep! I don't think I can give you a solid answer on that one, but I'm curious - what made you think about this?",
            
            "That's a really thoughtful question! I wish I had a better answer for you on that specific thing. What aspect of it interests you most?",
            
            "You're asking some really good questions here! I don't have all the answers, but I love exploring this stuff. What's your take on it?"
        ]
        
        return random.choice(responses)

    def load_qa_pairs(self):
        """Load the knowledge base"""
        qa_pairs = []
        
        if not os.path.exists(self.qa_file):
            self.create_enhanced_qa_file()
        
        try:
            with open(self.qa_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            if not content:
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
                    
        except Exception as e:
            print(f"Had some trouble loading the knowledge base: {e}")
            
        return qa_pairs

    def create_enhanced_qa_file(self):
        """Create knowledge base with natural, conversational answers"""
        sample_content = """Q: Who is Shankaracharya?
A: Oh, Shankara is this absolutely incredible guy from ancient India - like 8th century. He was basically a spiritual genius who figured out some of the deepest truths about consciousness and reality. What's amazing is he lived only about 32 years but completely revolutionized spiritual thinking. He taught this philosophy called Advaita Vedanta, which is all about how everything is actually one consciousness appearing as many different things. Pretty mind-blowing stuff!

Q: What is Advaita Vedanta?
A: So Advaita literally means "not two" - and it's this beautiful understanding that there's really no fundamental separation between you, me, and everything else. Like, we think we're all separate individuals, but according to Advaita, that's kind of like waves thinking they're separate from the ocean. The waves are real, but they're all just water appearing in different forms. It's the same with consciousness - we're all different expressions of the same underlying awareness. When you really get this, it changes everything about how you see life.

Q: When did Shankara live?
A: He lived in the 8th century CE - around 788 to 820 CE, though some scholars put the dates a bit differently. What blows my mind is that he accomplished SO much in just 32 years! He traveled all over India, had these incredible philosophical debates, wrote tons of commentaries, established monasteries, and basically shaped how people think about spirituality for over a thousand years. Talk about making your life count!

Q: What are Shankara's main works?
A: His big thing was writing commentaries on what they call the Prasthanatrayi - basically the three main texts of Vedanta: the Upanishads, Bhagavad Gita, and Brahma Sutras. These aren't just academic commentaries though - they're like practical wisdom for actually realizing these truths. He also wrote some beautiful independent works like Vivekachudamani and these gorgeous devotional songs like Bhaja Govindam. The cool thing is how he combined the highest philosophy with real devotion and love.

Q: What are the four mathas established by Shankara?
A: Shankara set up these four centers of learning called mathas - one in each direction of India. There's Sringeri in the south, Dwarka in the west, Puri in the east, and Jyotirmath in the north. What's amazing is these places are still going strong after more than 1200 years! They're like living libraries where this wisdom gets passed down from teacher to student. Each one has a head called a Shankaracharya who keeps the tradition alive.

Q: What is Maya according to Shankara?
A: Maya is probably one of the trickiest concepts to wrap your head around. People often translate it as "illusion," but that's not quite right. It's more like the creative power that makes the one appear as many. Think of it like this - water can appear as ice, steam, or liquid water, but it's all still H2O. Maya is that power of appearance. The world isn't fake or unreal, but seeing it as separate from consciousness - that's the illusion. It's like how a movie screen shows all these different scenes, but it's still just one screen.

Q: What is the goal of human life according to Advaita?
A: The ultimate goal is what they call Moksha - which is basically waking up to who you really are. It's not about becoming something different or going somewhere else, but recognizing that what you've been looking for - infinite peace, love, fulfillment - is actually your own true nature. It's like you've been a millionaire your whole life but thought you were poor. The money was always there; you just didn't know it. When this recognition happens, there's this incredible sense of completeness because you realize you were never actually incomplete.

Q: How do you achieve liberation in Advaita?
A: It's all about knowledge - but not book knowledge. It's direct recognition of what you are. There are three main steps: first you hear the truth from someone who knows (Shravana), then you really think about it deeply (Manana), then you rest in that understanding until it becomes your living reality (Nididhyasana). Self-inquiry is huge - constantly asking "Who am I?" and looking beyond all the temporary stuff to find the awareness that's always there. Having a good teacher helps a lot because the mind can be really sneaky about this stuff.

Q: What is the relationship between Atman and Brahman?
A: This is the most beautiful thing - Atman (your true self) and Brahman (ultimate reality) are exactly the same thing! It's not like they're similar or connected - they're literally identical. What you really are - not your body or thoughts or personality, but the pure awareness in which all experience happens - that's the same consciousness that's the source of everything. It's like the space inside a jar is the same as infinite space. When you really get this, the whole sense of being a separate, limited person just dissolves.

Q: What is self-inquiry and how do I practice it?
A: Self-inquiry is basically investigating who you really are by asking "Who am I?" But it's not an intellectual exercise. You're looking directly at the sense of "I" - that feeling of being yourself - and tracing it back to its source. When thoughts come up, ask "Who knows these thoughts?" When emotions arise, ask "Who's aware of these feelings?" Keep pointing attention back to the one who's aware. As you do this, you'll start to see that the "I" you're looking for isn't an object you can find, but the very awareness that's doing the looking.

Q: How do I deal with suffering on the spiritual path?
A: Suffering happens when we identify with things that come and go - thoughts, emotions, circumstances. But here's the thing: what you really are - that aware presence - is never actually touched by any of this stuff. It's like how a movie screen isn't hurt by the explosions in the movie. When suffering comes up, instead of trying to fix it right away, just notice: "Who's aware of this pain?" The one who's aware of suffering is always at peace. This gradually loosens suffering's grip and reveals the peace that was always there.

Q: What is the role of meditation in Advaita?
A: In Advaita, meditation isn't about achieving some special state or stopping thoughts. It's more about recognizing the awareness that's already here. True meditation is just being - resting as the consciousness you already are. When you sit quietly, don't try to become peaceful; just notice the peace that's already in the gaps between thoughts. This natural awareness doesn't need to be created or maintained - it's always present. Eventually you realize that meditation isn't something you do, but something you are.

Q: How do I know if I'm making spiritual progress?
A: Real progress isn't about having special experiences or mystical states. It shows up as more natural peace, less reactivity to life's ups and downs, and a growing sense of completeness that doesn't depend on circumstances. You might notice that questions that used to stress you out don't seem as urgent anymore. The ultimate progress is realizing there was never actually anyone who needed to make progress - there's just this eternal awareness that you are, which was never lost in the first place."""
        
        try:
            with open(self.qa_file, 'w', encoding='utf-8') as f:
                f.write(sample_content)
        except Exception as e:
            print(f"Had trouble creating the knowledge file: {e}")

    def get_wisdom_response(self, query):
        """Get response in natural way"""
        if not query.strip():
            return self.create_natural_unknown_response()
        
        # Try keyword search first
        keyword_result = self.enhanced_keyword_search(query)
        if keyword_result:
            return self.create_natural_response(keyword_result, query)
            
        # Try semantic search
        semantic_result = self.semantic_search(query)
        if semantic_result:
            return self.create_natural_response(semantic_result, query)
            
        # Return casual unknown response
        return self.create_natural_unknown_response()

    def start_conversation(self):
        """Start a natural conversation"""
        print("=" * 50)
        print("    CHATTING ABOUT CONSCIOUSNESS & LIFE")
        print("=" * 50)
        
        # Check if we can do voice
        if not self.recognizer:
            print("Looks like we'll be typing today - that's totally cool!")
            return self.text_conversation()
        
        if not self.qa_pairs:
            print("Hmm, having trouble loading my knowledge. Let me try to fix that...")
            return
            
        # Natural, casual greeting
        greeting = random.choice(self.conversation_starters)
        self.speak_naturally(greeting, pause_before=0.5, pause_after=1.0)
        
        self.conversation_started = True
        quiet_moments = 0
        
        while True:
            try:
                # Listen naturally
                what_you_said = self.listen_naturally(timeout=12, phrase_time_limit=12)
                
                if what_you_said.strip():
                    quiet_moments = 0
                    
                    # Log and show what they said
                    self.log_conversation("You", what_you_said)
                    print(f"You: {what_you_said}")
                    
                    # Handle different languages if needed
                    english_version, original_lang = self.detect_language_and_translate(what_you_said)
                    
                    # Check if they want to end the chat
                    ending_words = ['bye', 'goodbye', 'thanks', 'thank you', 'gotta go', 'see you', 'talk later', 'that\'s all']
                    if any(word in what_you_said.lower() for word in ending_words):
                        goodbye_messages = [
                            "Hey, this was really fun! Thanks for such a great conversation. Take care!",
                            "Awesome chatting with you! Hope some of this was helpful. Catch you later!",
                            "This was such a cool conversation! Thanks for being so thoughtful. See you around!",
                            "Really enjoyed talking with you about all this deep stuff! Take it easy!"
                        ]
                        self.speak_naturally(random.choice(goodbye_messages), pause_before=0.5)
                        break
                    
                    # Get response to what they said
                    my_response = self.get_wisdom_response(english_version)
                    
                    # Translate back if they were speaking another language
                    if original_lang != 'en' and self.translator:
                        try:
                            translated = self.translator.translate(my_response, src='en', dest=original_lang)
                            self.speak_naturally(translated.text, pause_before=0.5, pause_after=1.0)
                        except:
                            self.speak_naturally(my_response, pause_before=0.5, pause_after=1.0)
                    else:
                        self.speak_naturally(my_response, pause_before=0.5, pause_after=1.0)
                
                else:
                    # Handle quiet moments naturally
                    quiet_moments += 1
                    
                    if quiet_moments == 1:
                        gentle_nudges = [
                            "I'm here if you want to keep chatting...",
                            "What's on your mind?",
                            "Anything else you're curious about?",
                            "Take your time - I'm listening."
                        ]
                        self.speak_naturally(random.choice(gentle_nudges), pause_before=1.0, pause_after=0.5)
                        
                    elif quiet_moments == 2:
                        check_ins = [
                            "Still there? No worries if you need to think about stuff...",
                            "I'm here whenever you're ready to continue...",
                            "Feel free to ask about anything that comes to mind..."
                        ]
                        self.speak_naturally(random.choice(check_ins), pause_before=1.5, pause_after=0.5)
                        
                    elif quiet_moments >= 3:
                        natural_endings = [
                            "Well, this has been really nice! Feel free to come back anytime you want to chat about this stuff.",
                            "Thanks for hanging out and talking about these deep topics! Hope it was helpful.",
                            "This was fun! Come back anytime you want to explore more of these ideas."
                        ]
                        self.speak_naturally(random.choice(natural_endings), pause_before=1.0)
                        break
                        
            except KeyboardInterrupt:
                casual_interruptions = [
                    "No problem! Thanks for the chat - it was really great talking with you!",
                    "Cool, thanks for hanging out! Hope some of this was interesting.",
                    "Alright! This was fun. Take care and keep exploring these ideas!"
                ]
                self.speak_naturally(random.choice(casual_interruptions))
                break
            except Exception as e:
                self.speak_naturally("Hmm, having some technical hiccups, but this was a great conversation! Thanks for chatting.")
                break

    def text_conversation(self):
        """Natural text-based conversation"""
        print("\nAlright, let's chat through text! I love these conversations.")
        print("-" * 40)
        
        greeting = random.choice(self.conversation_starters)
        print(f"\n{greeting}\n")
        
        while True:
            try:
                your_message = input("You: ").strip()
                
                if not your_message:
                    continue
                    
                # Check for goodbye
                ending_words = ['bye', 'goodbye', 'thanks', 'thank you', 'gotta go', 'see you', 'talk later', 'that\'s all', 'quit', 'exit']
                if any(word in your_message.lower() for word in ending_words):
                    farewell = "This was such a great conversation! Thanks for being so thoughtful and curious. Hope you got something useful out of it!"
                    print(f"\n{farewell}\n")
                    break
                
                # Get and show response
                my_response = self.get_wisdom_response(your_message)
                print(f"\n{my_response}\n")
                
            except KeyboardInterrupt:
                print("\n\nNo worries! Thanks for the awesome conversation. Keep exploring these big questions!\n")
                break
            except Exception as e:
                print("\nHad some technical issues, but thanks for such a thoughtful chat!\n")
                break

    def run(self):
        """Start the conversation"""
        self.start_conversation()

if __name__ == "__main__":
    try:
        assistant = NaturalShankaraAssistant()
        
        if len(sys.argv) > 1 and sys.argv[1] == "--text":
            assistant.text_conversation()
        else:
            assistant.run()
        
    except KeyboardInterrupt:
        print("\nThanks for chatting!")
    except Exception as e:
        print(f"Something went wrong: {e}")
        print("\nFor text-only chat, try: python script.py --text")