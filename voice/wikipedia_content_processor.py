"""
Wikipedia Content Processor for Adi Shankara Assistant
Processes Wikipedia content to make it sound like Adi Shankara himself is speaking.
"""

import re
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import json

logger = logging.getLogger(__name__)

class WikipediaContentProcessor:
    """Processes Wikipedia content to humanize it as Adi Shankara's first-person responses"""
    
    def __init__(self):
        """Initialize the Wikipedia content processor"""
        
        # Comprehensive conversion patterns for different contexts
        self.conversion_patterns = {
            # Basic identity conversions
            'identity': [
                (r'\bAdi Shankara\b', 'I'),
                (r'\bShankara\b', 'I'),
                (r'\bShankaracharya\b', 'I'),
                (r'\bthe Acharya\b', 'I'),
                (r'\bAcharya Shankara\b', 'I'),
            ],
            
            # Biographical verbs (past tense)
            'biography': [
                (r'\bAdi Shankara was born\b', 'I was born'),
                (r'\bShankara was born\b', 'I was born'),
                (r'\bAdi Shankara lived\b', 'I lived'),
                (r'\bShankara lived\b', 'I lived'),
                (r'\bAdi Shankara grew up\b', 'I grew up'),
                (r'\bShankara grew up\b', 'I grew up'),
                (r'\bAdi Shankara studied\b', 'I studied'),
                (r'\bShankara studied\b', 'I studied'),
                (r'\bAdi Shankara became\b', 'I became'),
                (r'\bShankara became\b', 'I became'),
                (r'\bAdi Shankara died\b', 'I left this physical form'),
                (r'\bShankara died\b', 'I left this physical form'),
                (r'\bAdi Shankara passed away\b', 'I transcended this physical existence'),
                (r'\bShankara passed away\b', 'I transcended this physical existence'),
            ],
            
            # Teaching and philosophical activities
            'teaching': [
                (r'\bAdi Shankara taught\b', 'I taught'),
                (r'\bShankara taught\b', 'I taught'),
                (r'\bAdi Shankara explained\b', 'I explained'),
                (r'\bShankara explained\b', 'I explained'),
                (r'\bAdi Shankara argued\b', 'I argued'),
                (r'\bShankara argued\b', 'I argued'),
                (r'\bAdi Shankara believed\b', 'I believe'),
                (r'\bShankara believed\b', 'I believe'),
                (r'\bAdi Shankara maintained\b', 'I maintain'),
                (r'\bShankara maintained\b', 'I maintain'),
                (r'\bAdi Shankara proposed\b', 'I propose'),
                (r'\bShankara proposed\b', 'I propose'),
                (r'\bAdi Shankara developed\b', 'I developed'),
                (r'\bShankara developed\b', 'I developed'),
                (r'\bAdi Shankara formulated\b', 'I formulated'),
                (r'\bShankara formulated\b', 'I formulated'),
            ],
            
            # Creative and establishment activities
            'works': [
                (r'\bAdi Shankara wrote\b', 'I wrote'),
                (r'\bShankara wrote\b', 'I wrote'),
                (r'\bAdi Shankara composed\b', 'I composed'),
                (r'\bShankara composed\b', 'I composed'),
                (r'\bAdi Shankara created\b', 'I created'),
                (r'\bShankara created\b', 'I created'),
                (r'\bAdi Shankara established\b', 'I established'),
                (r'\bShankara established\b', 'I established'),
                (r'\bAdi Shankara founded\b', 'I founded'),
                (r'\bShankara founded\b', 'I founded'),
                (r'\bAdi Shankara instituted\b', 'I instituted'),
                (r'\bShankara instituted\b', 'I instituted'),
                (r'\bAdi Shankara set up\b', 'I set up'),
                (r'\bShankara set up\b', 'I set up'),
            ],
            
            # Travel and movement
            'travels': [
                (r'\bAdi Shankara traveled\b', 'I traveled'),
                (r'\bShankara traveled\b', 'I traveled'),
                (r'\bAdi Shankara journeyed\b', 'I journeyed'),
                (r'\bShankara journeyed\b', 'I journeyed'),
                (r'\bAdi Shankara visited\b', 'I visited'),
                (r'\bShankara visited\b', 'I visited'),
                (r'\bAdi Shankara went to\b', 'I went to'),
                (r'\bShankara went to\b', 'I went to'),
                (r'\bAdi Shankara walked\b', 'I walked'),
                (r'\bShankara walked\b', 'I walked'),
            ],
            
            # Possessive forms
            'possessive': [
                (r'\bAdi Shankara\'s\b', 'my'),
                (r'\bShankara\'s\b', 'my'),
                (r'\bShankaracharya\'s\b', 'my'),
                (r'\bthe Acharya\'s\b', 'my'),
                (r'\bhis\b', 'my'),
                (r'\bHis\b', 'My'),
            ],
            
            # Pronouns
            'pronouns': [
                (r'\bhe\b', 'I'),
                (r'\bHe\b', 'I'),
                (r'\bhim\b', 'me'),
                (r'\bHim\b', 'Me'),
                (r'\bhimself\b', 'myself'),
                (r'\bHimself\b', 'Myself'),
            ],
        }
        
        # Context-specific introductory phrases
        self.contextual_intros = {
            'birth': [
                "Let me tell you about my birth and early life.",
                "Regarding my entrance into this physical world,",
                "About my earthly manifestation,",
            ],
            'philosophy': [
                "Regarding my philosophical understanding,",
                "In terms of the truth I have realized and shared,",
                "About the profound wisdom I have contemplated,",
                "Concerning the eternal principles I teach,",
            ],
            'travels': [
                "About my journeys across this sacred land of Bharata,",
                "Regarding my travels to spread the eternal wisdom,",
                "In my wanderings to awaken souls to truth,",
            ],
            'works': [
                "Concerning the texts and commentaries I have written,",
                "About my literary contributions to preserve the wisdom,",
                "Regarding the works I composed to clarify the scriptures,",
            ],
            'debates': [
                "In my philosophical discussions and debates,",
                "During my encounters with various schools of thought,",
                "In my dialogues with fellow seekers and scholars,",
            ],
            'establishments': [
                "About the institutions I established to preserve the teaching,",
                "Regarding the mathas I founded across the four directions,",
                "Concerning the monastic orders I created,",
            ],
        }
        
        # Spiritual context replacements
        self.spiritual_replacements = {
            'the philosopher': 'I, as a seeker of ultimate truth,',
            'the teacher': 'I, as one who shares the eternal wisdom,',
            'the sage': 'I, in my understanding of the Self,',
            'the mystic': 'I, through direct realization,',
            'the saint': 'I, devoted to the highest truth,',
            'the master': 'I, as a humble servant of truth,',
            'the guru': 'I, as one who removes the darkness of ignorance,',
        }
    
    def detect_content_context(self, content: str) -> str:
        """Detect the primary context of the Wikipedia content"""
        content_lower = content.lower()
        
        # Define context patterns
        context_patterns = {
            'birth': ['born', 'birth', 'childhood', 'early life', 'parents', 'family'],
            'philosophy': ['advaita', 'vedanta', 'brahman', 'maya', 'philosophy', 'teaching', 'doctrine'],
            'travels': ['traveled', 'journey', 'pilgrimage', 'visited', 'went to', 'wandered'],
            'works': ['wrote', 'composed', 'commentary', 'text', 'work', 'treatise', 'hymn'],
            'debates': ['debate', 'discussion', 'argued', 'refuted', 'opponent', 'scholar'],
            'establishments': ['established', 'founded', 'matha', 'monastery', 'institution'],
        }
        
        # Find the context with most matches
        context_scores = {}
        for context, patterns in context_patterns.items():
            score = sum(1 for pattern in patterns if pattern in content_lower)
            context_scores[context] = score
        
        # Return the context with highest score, or 'general' if tie/no clear winner
        if context_scores:
            max_score = max(context_scores.values())
            if max_score > 0:
                # Find the key with max score
                for context, score in context_scores.items():
                    if score == max_score:
                        return context
        
        return 'general'
    
    def apply_conversion_patterns(self, content: str, context: str = 'general') -> str:
        """Apply conversion patterns based on context"""
        converted_content = content
        
        # Apply all conversion patterns
        for pattern_type, patterns in self.conversion_patterns.items():
            for pattern, replacement in patterns:
                converted_content = re.sub(pattern, replacement, converted_content, flags=re.IGNORECASE)
        
        # Apply spiritual context replacements
        for term, replacement in self.spiritual_replacements.items():
            converted_content = re.sub(re.escape(term), replacement, converted_content, flags=re.IGNORECASE)
        
        return converted_content
    
    def add_contextual_introduction(self, content: str, context: str) -> str:
        """Add appropriate introduction based on context"""
        if context in self.contextual_intros:
            intro_options = self.contextual_intros[context]
            # For now, use the first option (could be randomized later)
            intro = intro_options[0]
            return f"{intro} {content}"
        
        return content
    
    def clean_and_polish(self, content: str) -> str:
        """Clean up the converted content and polish it"""
        
        # Fix common grammatical issues from conversion
        content = re.sub(r'\bI I\b', 'I', content)
        content = re.sub(r'\bmy my\b', 'my', content)
        content = re.sub(r'\bme me\b', 'me', content)
        content = re.sub(r'\bmyself myself\b', 'myself', content)
        
        # Fix spacing issues
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        # Ensure proper capitalization after periods
        sentences = content.split('. ')
        polished_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Capitalize first letter
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                polished_sentences.append(sentence)
        
        polished_content = '. '.join(polished_sentences)
        
        # Ensure it ends with proper punctuation
        if polished_content and not polished_content.endswith(('.', '!', '?')):
            polished_content += '.'
        
        return polished_content
    
    def add_spiritual_authenticity(self, content: str, context: str) -> str:
        """Add spiritual authenticity to make it sound more like Adi Shankara"""
        
        # Add spiritual depth based on context
        spiritual_additions = {
            'philosophy': [
                " This understanding arose through direct realization, not mere intellectual study.",
                " Such is the nature of truth that reveals itself to the prepared mind.",
                " This wisdom flows from the source of all knowledge within.",
            ],
            'travels': [
                " Each step was guided by the divine purpose to awaken souls.",
                " These journeys were not mere physical movements but spiritual missions.",
                " In every place I visited, the same eternal truth was shared.",
            ],
            'works': [
                " These writings emerged from direct experience of the ultimate reality.",
                " Each word was carefully chosen to guide seekers to their true nature.",
                " The purpose was always to remove ignorance and reveal the Self.",
            ],
            'debates': [
                " In every discussion, my aim was not victory but the revelation of truth.",
                " These dialogues served to clarify understanding for all sincere seekers.",
                " Through reasoning and scriptural authority, the path was made clear.",
            ],
        }
        
        if context in spiritual_additions:
            # Add one of the spiritual depth comments (could be randomized)
            addition = spiritual_additions[context][0]
            content += addition
        
        return content
    
    def process_wikipedia_content(self, content: str, topic: str = "") -> str:
        """
        Main method to process Wikipedia content about Adi Shankara
        
        Args:
            content: Raw Wikipedia content
            topic: Topic or context hint for better processing
            
        Returns:
            Humanized first-person content as if Adi Shankara is speaking
        """
        if not content or not content.strip():
            return content
        
        try:
            # Detect the context from content
            detected_context = self.detect_content_context(content)
            
            # If topic is provided, use it to override detection if relevant
            if topic:
                topic_lower = topic.lower()
                if any(keyword in topic_lower for keyword in ['birth', 'born', 'early']):
                    detected_context = 'birth'
                elif any(keyword in topic_lower for keyword in ['philosophy', 'advaita', 'teaching']):
                    detected_context = 'philosophy'
                elif any(keyword in topic_lower for keyword in ['travel', 'journey', 'pilgrimage']):
                    detected_context = 'travels'
                elif any(keyword in topic_lower for keyword in ['work', 'wrote', 'composition']):
                    detected_context = 'works'
                elif any(keyword in topic_lower for keyword in ['debate', 'discussion']):
                    detected_context = 'debates'
                elif any(keyword in topic_lower for keyword in ['matha', 'established', 'founded']):
                    detected_context = 'establishments'
            
            # Step 1: Apply conversion patterns
            converted_content = self.apply_conversion_patterns(content, detected_context)
            
            # Step 2: Add contextual introduction
            introduced_content = self.add_contextual_introduction(converted_content, detected_context)
            
            # Step 3: Add spiritual authenticity
            authentic_content = self.add_spiritual_authenticity(introduced_content, detected_context)
            
            # Step 4: Clean and polish
            polished_content = self.clean_and_polish(authentic_content)
            
            logger.info(f"Processed Wikipedia content with context: {detected_context}")
            return polished_content
            
        except Exception as e:
            logger.error(f"Error processing Wikipedia content: {e}")
            # Return original content if processing fails
            return content
    
    def batch_process_knowledge_base(self, knowledge_base_path: str) -> bool:
        """
        Batch process existing knowledge base to humanize third-person content
        
        Args:
            knowledge_base_path: Path to the knowledge base JSON file
            
        Returns:
            bool: True if processing was successful
        """
        try:
            # Load existing knowledge base
            with open(knowledge_base_path, 'r', encoding='utf-8') as f:
                knowledge_base = json.load(f)
            
            updated_count = 0
            
            for entry in knowledge_base.get('knowledge_base', []):
                original_answer = entry.get('answer', '')
                
                # Check if it contains third-person references to Shankara
                if any(term in original_answer for term in ['Adi Shankara', 'Shankara', 'he ', 'his ', 'him ']):
                    # Process the answer
                    category = entry.get('category', 'general')
                    processed_answer = self.process_wikipedia_content(original_answer, category)
                    
                    # Update only if significantly different
                    if processed_answer != original_answer:
                        entry['answer'] = processed_answer
                        entry['humanized'] = True
                        entry['humanization_date'] = str(datetime.now().isoformat())
                        updated_count += 1
                        logger.info(f"Humanized entry: {entry.get('id', 'unknown')}")
            
            # Save updated knowledge base
            if updated_count > 0:
                # Create backup
                backup_path = f"{knowledge_base_path}.backup.{int(time.time())}"
                import shutil
                shutil.copy2(knowledge_base_path, backup_path)
                
                # Save updated version
                with open(knowledge_base_path, 'w', encoding='utf-8') as f:
                    json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Batch processing completed. Updated {updated_count} entries.")
                return True
            else:
                logger.info("No entries needed humanization.")
                return True
                
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            return False
    
    def validate_humanization(self, original: str, humanized: str) -> Dict[str, Any]:
        """
        Validate that humanization was successful and appropriate
        
        Returns:
            dict: Validation results with score and issues
        """
        validation_results = {
            'score': 0.0,
            'issues': [],
            'improvements': [],
            'is_valid': False
        }
        
        try:
            # Check if third-person references were removed
            third_person_terms = ['Adi Shankara', 'Shankara ', 'he ', 'his ', 'him ', 'himself']
            remaining_third_person = [term for term in third_person_terms if term in humanized]
            
            if not remaining_third_person:
                validation_results['score'] += 0.4
                validation_results['improvements'].append("Successfully removed third-person references")
            else:
                validation_results['issues'].append(f"Still contains third-person terms: {remaining_third_person}")
            
            # Check if first-person terms were added
            first_person_terms = [' I ', ' my ', ' me ', ' myself']
            first_person_count = sum(1 for term in first_person_terms if term in humanized)
            
            if first_person_count > 0:
                validation_results['score'] += 0.3
                validation_results['improvements'].append(f"Added {first_person_count} first-person references")
            else:
                validation_results['issues'].append("No first-person references added")
            
            # Check length difference (shouldn't be too different)
            length_ratio = len(humanized) / len(original) if len(original) > 0 else 1
            if 0.8 <= length_ratio <= 1.5:
                validation_results['score'] += 0.2
                validation_results['improvements'].append("Appropriate length maintained")
            else:
                validation_results['issues'].append(f"Unusual length change ratio: {length_ratio:.2f}")
            
            # Check for grammatical coherence (basic)
            if humanized.strip() and humanized[0].isupper():
                validation_results['score'] += 0.1
                validation_results['improvements'].append("Proper capitalization")
            
            # Overall validation
            validation_results['is_valid'] = validation_results['score'] >= 0.6
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error in validation: {e}")
            validation_results['issues'].append(f"Validation error: {e}")
            return validation_results
