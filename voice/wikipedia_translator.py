#!/usr/bin/env python3
"""
Enhanced Wikipedia to Any Language Translator
A comprehensive system for retrieving Wikipedia content and translating it to any language
"""

import sys
import os
import random
import wikipedia
from googletrans import Translator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WikipediaTranslator:
    """Enhanced Wikipedia content retrieval and translation system"""
    
    def __init__(self):
        """Initialize the Wikipedia translator"""
        try:
            self.translator = Translator()
            # Test translator
            test = self.translator.detect("hello")
            print("✅ Translator initialized successfully")
        except Exception as e:
            print(f"⚠️ Translator initialization failed: {e}")
            self.translator = None
        
        # Language code mappings for better support
        self.language_codes = {
            'hindi': 'hi', 'malayalam': 'ml', 'tamil': 'ta', 'telugu': 'te',
            'kannada': 'kn', 'marathi': 'mr', 'gujarati': 'gu', 'bengali': 'bn',
            'punjabi': 'pa', 'urdu': 'ur', 'sanskrit': 'sa', 'nepali': 'ne',
            'spanish': 'es', 'french': 'fr', 'german': 'de', 'italian': 'it',
            'portuguese': 'pt', 'russian': 'ru', 'chinese': 'zh', 'japanese': 'ja',
            'korean': 'ko', 'arabic': 'ar', 'persian': 'fa', 'turkish': 'tr',
            'vietnamese': 'vi', 'thai': 'th', 'indonesian': 'id', 'malay': 'ms',
            'english': 'en'
        }
        
        # Natural language identifiers
        self.language_indicators = {
            'hindi': ['hindi', 'हिंदी', 'हिन्दी'],
            'malayalam': ['malayalam', 'മലയാളം'],
            'tamil': ['tamil', 'தமிழ்'],
            'telugu': ['telugu', 'తెలుగు'],
            'kannada': ['kannada', 'ಕನ್ನಡ'],
            'marathi': ['marathi', 'मराठी'],
            'gujarati': ['gujarati', 'ગુજરાતી'],
            'bengali': ['bengali', 'বাংলা'],
            'spanish': ['spanish', 'español'],
            'french': ['french', 'français'],
            'german': ['german', 'deutsch'],
            'italian': ['italian', 'italiano'],
            'portuguese': ['portuguese', 'português'],
            'russian': ['russian', 'русский'],
            'chinese': ['chinese', '中文'],
            'japanese': ['japanese', '日本語'],
            'korean': ['korean', '한국어'],
            'arabic': ['arabic', 'العربية']
        }

    def detect_target_language(self, query):
        """Detect what language the user wants the content translated to"""
        query_lower = query.lower()
        
        # Check for explicit language requests
        for lang, indicators in self.language_indicators.items():
            for indicator in indicators:
                if f"in {indicator}" in query_lower or f"to {indicator}" in query_lower:
                    return lang
        
        # Check for common translation patterns
        import re
        patterns = [
            r'translate.*to\s+(\w+)',
            r'convert.*to\s+(\w+)',
            r'say.*in\s+(\w+)',
            r'explain.*in\s+(\w+)',
            r'tell.*in\s+(\w+)',
            r'search.*in\s+(\w+)',
            r'(.+)\s+in\s+(\w+)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                lang_name = match.group(-1)  # Get the last group (language name)
                if lang_name in self.language_codes:
                    return lang_name
                # Check if it's a variant
                for lang, indicators in self.language_indicators.items():
                    if lang_name in indicators:
                        return lang
        
        return None

    def search_wikipedia_enhanced(self, topic, max_sentences=5):
        """Enhanced Wikipedia search with better content processing"""
        try:
            print(f"🔍 Searching Wikipedia for: {topic}")
            
            # Search for pages
            search_results = wikipedia.search(topic, results=8)
            if not search_results:
                return None
            
            # Try to get the most relevant page
            for page_title in search_results:
                try:
                    page = wikipedia.page(page_title)
                    
                    # Get enhanced summary
                    summary = wikipedia.summary(page_title, sentences=max_sentences)
                    
                    # Get meaningful content paragraphs
                    content_paragraphs = [p.strip() for p in page.content.split('\n\n') 
                                        if len(p.strip()) > 100]
                    
                    # Select best content based on topic relevance
                    topic_words = set(topic.lower().split())
                    relevant_paragraphs = []
                    
                    for paragraph in content_paragraphs[:10]:
                        para_words = set(paragraph.lower().split())
                        relevance = len(topic_words.intersection(para_words))
                        if relevance > 0 or len(relevant_paragraphs) < 3:
                            relevant_paragraphs.append((paragraph, relevance))
                    
                    # Sort by relevance and combine
                    relevant_paragraphs.sort(key=lambda x: x[1], reverse=True)
                    selected_content = '\n\n'.join([p[0] for p in relevant_paragraphs[:3]])
                    
                    if len(selected_content) > 2000:
                        selected_content = selected_content[:2000] + "..."
                    
                    print(f"✅ Found information about: {page_title}")
                    return {
                        'title': page_title,
                        'summary': summary,
                        'content': selected_content,
                        'url': page.url
                    }
                    
                except wikipedia.exceptions.DisambiguationError as e:
                    if e.options:
                        try:
                            page = wikipedia.page(e.options[0])
                            summary = wikipedia.summary(e.options[0], sentences=max_sentences)
                            content = page.content[:2000] + "..." if len(page.content) > 2000 else page.content
                            
                            print(f"✅ Found information about: {e.options[0]} (from disambiguation)")
                            return {
                                'title': e.options[0],
                                'summary': summary,
                                'content': content,
                                'url': page.url
                            }
                        except Exception:
                            continue
                            
                except wikipedia.exceptions.PageError:
                    continue
                except Exception as e:
                    logger.warning(f"Error processing page {page_title}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return None

    def translate_content(self, content, target_language):
        """Translate content to target language with enhanced error handling and Malayalam accuracy"""
        if not self.translator:
            return f"Translation service unavailable. Original content: {content}"
        
        if not content or not content.strip():
            return "No content to translate."
        
        try:
            # Safe target language handling
            target_language = target_language or 'english'
            target_code = self.language_codes.get(target_language.lower(), target_language.lower())
            
            # Ensure target_code is not None and is a valid string
            if not target_code or not isinstance(target_code, str):
                target_code = 'en'  # fallback to English
            
            # Special handling for Malayalam to improve accuracy
            if target_language.lower() in ['malayalam', 'ml']:
                # Pre-processing for better Malayalam translation
                content = self._preprocess_for_malayalam(content)
            
            # Handle long content by splitting into chunks
            if len(content) > 4000:
                chunks = []
                sentences = content.split('. ')
                current_chunk = ""
                
                for sentence in sentences:
                    if len(current_chunk + sentence) < 4000:
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + ". "
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Translate each chunk
                translated_chunks = []
                for i, chunk in enumerate(chunks):
                    try:
                        translated = self.translator.translate(chunk, dest=target_code)
                        translated_chunks.append(translated.text)
                        print(f"✅ Translated chunk {i+1}/{len(chunks)}")
                    except Exception as e:
                        logger.warning(f"Failed to translate chunk {i+1}: {e}")
                        translated_chunks.append(chunk)  # Keep original if translation fails
                
                return ' '.join(translated_chunks)
            
            else:
                # Translate shorter content directly
                translated = self.translator.translate(content, dest=target_code)
                return translated.text
                
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return f"Translation failed. Original content: {content}"

    def get_wikipedia_in_language(self, topic, target_language, detail_level="summary"):
        """Main function to get Wikipedia content in any language"""
        
        # Search Wikipedia
        wiki_data = self.search_wikipedia_enhanced(
            topic, 
            max_sentences=3 if detail_level == "summary" else 6
        )
        
        if not wiki_data:
            return {
                'success': False,
                'message': f"No information found about '{topic}' on Wikipedia.",
                'topic': topic,
                'language': target_language
            }
        
        # Prepare content based on detail level
        if detail_level.lower() in ["brief", "short"]:
            content = wiki_data['summary'][:400] + "..." if len(wiki_data['summary']) > 400 else wiki_data['summary']
        elif detail_level.lower() in ["detailed", "full", "complete"]:
            content = f"{wiki_data['summary']}\n\n{wiki_data['content']}"
        else:  # summary (default)
            content = wiki_data['summary']
        
        # Add source information
        source_info = f"\n\n[Source: {wiki_data['title']} - Wikipedia]"
        content += source_info
        
        # Translate if not English
        if target_language.lower() not in ['english', 'en']:
            print(f"🌐 Translating to {target_language}...")
            translated_content = self.translate_content(content, target_language)
        else:
            translated_content = content
        
        return {
            'success': True,
            'topic': topic,
            'language': target_language,
            'title': wiki_data['title'],
            'content': translated_content,
            'original_content': content,
            'url': wiki_data['url']
        }

    def process_query(self, query):
        """Process a natural language query for Wikipedia content and translation"""
        
        # Extract topic and target language
        target_language = self.detect_target_language(query)
        if not target_language:
            target_language = "english"
        
        # Extract topic
        topic = self.extract_topic_from_query(query)
        if not topic:
            return {
                'success': False,
                'message': "Could not determine what topic to search for.",
                'query': query
            }
        
        # Determine detail level
        detail_level = "summary"
        query_lower = query.lower()
        if any(word in query_lower for word in ["detailed", "full", "complete", "everything", "all about"]):
            detail_level = "detailed"
        elif any(word in query_lower for word in ["brief", "short", "quickly", "summary"]):
            detail_level = "brief"
        
        # Get the content
        result = self.get_wikipedia_in_language(topic, target_language, detail_level)
        result['query'] = query
        result['detail_level'] = detail_level
        
        return result

    def extract_topic_from_query(self, query):
        """Extract the main topic from a query"""
        query_lower = query.lower()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "tell me about", "what is", "who is", "explain", "search for",
            "find information about", "look up", "search wikipedia for",
            "get information about", "i want to know about", "can you tell me about"
        ]
        
        topic = query
        for prefix in prefixes_to_remove:
            if query_lower.startswith(prefix):
                topic = query[len(prefix):].strip()
                break
        
        # Remove language specifications
        import re
        topic = re.sub(r'\s+in\s+\w+$', '', topic, flags=re.IGNORECASE)
        topic = re.sub(r'\s+to\s+\w+$', '', topic, flags=re.IGNORECASE)
        
        # Clean up
        topic = topic.strip('?.,!').strip()
        
        return topic if len(topic) > 1 else None

    def _preprocess_for_malayalam(self, content):
        """Preprocess content for better Malayalam translation accuracy"""
        try:
            # Split into smaller, more manageable sentences for better translation
            sentences = content.split('. ')
            
            # Process each sentence to improve translation quality
            processed_sentences = []
            for sentence in sentences:
                if len(sentence.strip()) > 0:
                    # Remove excessive technical jargon that might confuse translation
                    processed_sentence = self._simplify_for_translation(sentence)
                    processed_sentences.append(processed_sentence)
            
            return '. '.join(processed_sentences)
            
        except Exception as e:
            logger.warning(f"Malayalam preprocessing failed: {e}")
            return content  # Return original if preprocessing fails
    
    def _simplify_for_translation(self, text):
        """Simplify text for better translation accuracy"""
        try:
            # Replace complex terms with simpler alternatives
            replacements = {
                'philosophical': 'spiritual',
                'metaphysical': 'spiritual',
                'epistemological': 'knowledge-related',
                'ontological': 'existence-related',
                'phenomenological': 'experience-related'
            }
            
            simplified = text
            for complex_term, simple_term in replacements.items():
                simplified = simplified.replace(complex_term, simple_term)
            
            return simplified
            
        except Exception:
            return text  # Return original if simplification fails

def main():
    """Demo function"""
    translator = WikipediaTranslator()
    
    # Test queries
    test_queries = [
        "Tell me about artificial intelligence in Hindi",
        "What is quantum computing in Malayalam",
        "Explain neural networks in Tamil",
        "Search for Albert Einstein in Spanish",
        "Get information about meditation in French",
        "Machine learning in German",
    ]
    
    print("🌐 Wikipedia Multi-Language Translator Demo")
    print("=" * 50)
    
    for i, query in enumerate(test_queries):
        print(f"\n📝 Test {i+1}: {query}")
        result = translator.process_query(query)
        
        if result['success']:
            print(f"✅ Found: {result['title']}")
            print(f"🌐 Language: {result['language']}")
            print(f"📄 Content: {result['content'][:200]}...")
        else:
            print(f"❌ {result['message']}")
        
        print("-" * 30)

if __name__ == "__main__":
    main()
