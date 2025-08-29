"""
Self-Learning Engine for Adi Shankara Assistant
Implements continuous learning from user interactions and Wikipedia content.
"""

import json
import re
import time
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SelfLearningEngine:
    """Engine that enables the assistant to learn and improve from interactions"""
    
    def __init__(self, knowledge_file="shankaracharya_knowledge.json", 
                 conversation_log="conversation_log.txt",
                 learning_log="learning_log.txt"):
        self.knowledge_file = knowledge_file
        self.conversation_log = conversation_log
        self.learning_log = learning_log
        self.knowledge_base = self.load_knowledge_base()
        self.learning_threshold = 0.7  # Confidence threshold for auto-learning
        self.manual_review_queue = []
        
        # Initialize learning statistics
        self.learning_stats = {
            "total_interactions": 0,
            "successful_learnings": 0,
            "manual_reviews": 0,
            "knowledge_base_size": len(self.knowledge_base.get("knowledge_base", [])),
            "last_update": datetime.now().isoformat()
        }
        
    def load_knowledge_base(self) -> Dict:
        """Load the current knowledge base"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"knowledge_base": [], "metadata": {"created": datetime.now().isoformat()}}
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            return {"knowledge_base": [], "metadata": {"created": datetime.now().isoformat()}}
    
    def save_knowledge_base(self):
        """Save the updated knowledge base"""
        try:
            # Update metadata
            if "metadata" not in self.knowledge_base:
                self.knowledge_base["metadata"] = {}
            
            self.knowledge_base["metadata"]["last_updated"] = datetime.now().isoformat()
            self.knowledge_base["metadata"]["total_entries"] = len(self.knowledge_base.get("knowledge_base", []))
            
            # Create backup before saving
            backup_file = f"{self.knowledge_file}.backup.{int(time.time())}"
            if os.path.exists(self.knowledge_file):
                import shutil
                shutil.copy2(self.knowledge_file, backup_file)
            
            # Save updated knowledge base
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Knowledge base saved with {len(self.knowledge_base.get('knowledge_base', []))} entries")
            
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
    
    def humanize_wikipedia_content(self, content: str, topic: str = "") -> str:
        """
        Convert Wikipedia content about Adi Shankara to first-person responses
        as if Adi Shankara himself is speaking
        """
        if not content:
            return content
        
        # Enhanced third-person to first-person conversions
        conversions = [
            # Basic name conversions
            (r'\bAdi Shankara\b', 'I'),
            (r'\bShankara\b', 'I'),
            (r'\bShankaracharya\b', 'I'),
            (r'\bAcharya\b', 'I'),
            
            # Verb conversions (past tense)
            (r'\bAdi Shankara was born\b', 'I was born'),
            (r'\bShankara was born\b', 'I was born'),
            (r'\bAdi Shankara lived\b', 'I lived'),
            (r'\bShankara lived\b', 'I lived'),
            (r'\bAdi Shankara taught\b', 'I taught'),
            (r'\bShankara taught\b', 'I taught'),
            (r'\bAdi Shankara established\b', 'I established'),
            (r'\bShankara established\b', 'I established'),
            (r'\bAdi Shankara traveled\b', 'I traveled'),
            (r'\bShankara traveled\b', 'I traveled'),
            (r'\bAdi Shankara wrote\b', 'I wrote'),
            (r'\bShankara wrote\b', 'I wrote'),
            (r'\bAdi Shankara composed\b', 'I composed'),
            (r'\bShankara composed\b', 'I composed'),
            (r'\bAdi Shankara founded\b', 'I founded'),
            (r'\bShankara founded\b', 'I founded'),
            (r'\bAdi Shankara created\b', 'I created'),
            (r'\bShankara created\b', 'I created'),
            (r'\bAdi Shankara developed\b', 'I developed'),
            (r'\bShankara developed\b', 'I developed'),
            
            # Verb conversions (present tense)
            (r'\bAdi Shankara is\b', 'I am'),
            (r'\bShankara is\b', 'I am'),
            (r'\bAdi Shankara teaches\b', 'I teach'),
            (r'\bShankara teaches\b', 'I teach'),
            (r'\bAdi Shankara believes\b', 'I believe'),
            (r'\bShankara believes\b', 'I believe'),
            (r'\bAdi Shankara argues\b', 'I argue'),
            (r'\bShankara argues\b', 'I argue'),
            (r'\bAdi Shankara explains\b', 'I explain'),
            (r'\bShankara explains\b', 'I explain'),
            
            # Possessive conversions
            (r'\bAdi Shankara\'s\b', 'my'),
            (r'\bShankara\'s\b', 'my'),
            (r'\bShankaracharya\'s\b', 'my'),
            (r'\bAcharya\'s\b', 'my'),
            (r'\bhis\b', 'my'),
            (r'\bHis\b', 'My'),
            
            # Pronoun conversions
            (r'\bhe\b', 'I'),
            (r'\bHe\b', 'I'),
            (r'\bhim\b', 'me'),
            (r'\bHim\b', 'Me'),
            (r'\bhimself\b', 'myself'),
            (r'\bHimself\b', 'Myself'),
            
            # Specific philosophical terms
            (r'\bAccording to Adi Shankara\b', 'As I teach'),
            (r'\bAccording to Shankara\b', 'As I teach'),
            (r'\bShankara\'s philosophy\b', 'my philosophy'),
            (r'\bAdi Shankara\'s philosophy\b', 'my philosophy'),
            (r'\bShankara\'s teachings\b', 'my teachings'),
            (r'\bAdi Shankara\'s teachings\b', 'my teachings'),
            (r'\bShankara\'s doctrine\b', 'my doctrine'),
            (r'\bAdi Shankara\'s doctrine\b', 'my doctrine'),
        ]
        
        # Apply conversions
        humanized_content = content
        for pattern, replacement in conversions:
            humanized_content = re.sub(pattern, replacement, humanized_content, flags=re.IGNORECASE)
        
        # Add natural introductory phrases for different types of content
        if topic.lower() in ['birth', 'birthplace', 'early life']:
            humanized_content = f"Let me tell you about my early life. {humanized_content}"
        elif topic.lower() in ['philosophy', 'advaita', 'vedanta']:
            humanized_content = f"Regarding my philosophical teachings, {humanized_content}"
        elif topic.lower() in ['travels', 'journey', 'pilgrimage']:
            humanized_content = f"About my journeys across Bharata, {humanized_content}"
        elif topic.lower() in ['works', 'writings', 'commentaries']:
            humanized_content = f"Concerning my written works, {humanized_content}"
        elif topic.lower() in ['debates', 'discussions']:
            humanized_content = f"In my philosophical debates and discussions, {humanized_content}"
        
        # Clean up any remaining awkward constructions
        humanized_content = re.sub(r'\bI I\b', 'I', humanized_content)
        humanized_content = re.sub(r'\bmy my\b', 'my', humanized_content)
        humanized_content = re.sub(r'\s+', ' ', humanized_content)  # Remove extra spaces
        
        return humanized_content.strip()
    
    def extract_keywords_from_question(self, question: str) -> List[str]:
        """Extract meaningful keywords from a user question"""
        # Remove common stop words and extract meaningful terms
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 
            'to', 'for', 'of', 'as', 'by', 'what', 'who', 'where', 'when', 'why', 'how',
            'can', 'could', 'would', 'should', 'will', 'do', 'does', 'did', 'are', 'was',
            'were', 'been', 'being', 'have', 'has', 'had', 'you', 'your', 'tell', 'me',
            'about', 'explain', 'describe'
        }
        
        # Extract words and filter
        words = re.findall(r'\b\w+\b', question.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add some compound terms if they exist
        question_lower = question.lower()
        compound_terms = [
            'adi shankara', 'advaita vedanta', 'brahma sutras', 'upanishads',
            'bhagavad gita', 'four mathas', 'shankaracharya', 'non-dual',
            'self realization', 'consciousness', 'maya', 'brahman'
        ]
        
        for term in compound_terms:
            if term in question_lower:
                keywords.append(term.replace(' ', '_'))
        
        return list(set(keywords))  # Remove duplicates
    
    def categorize_question(self, question: str) -> str:
        """Categorize the question to organize knowledge base"""
        question_lower = question.lower()
        
        # Define category patterns
        categories = {
            'identity': ['who are you', 'tell me about yourself', 'introduce', 'yourself', 'who is', 'about you'],
            'philosophy': ['advaita', 'vedanta', 'philosophy', 'teaching', 'doctrine', 'principle', 'concept'],
            'biography': ['born', 'birth', 'life', 'lived', 'early', 'childhood', 'family', 'background'],
            'travels': ['travel', 'journey', 'pilgrimage', 'visit', 'went to', 'where did'],
            'works': ['wrote', 'written', 'work', 'commentary', 'text', 'book', 'composition'],
            'debates': ['debate', 'discussion', 'argument', 'opponent', 'philosopher'],
            'establishments': ['matha', 'monastery', 'established', 'founded', 'institution'],
            'spiritual': ['liberation', 'moksha', 'enlightenment', 'realization', 'consciousness', 'self'],
            'concepts': ['maya', 'brahman', 'atman', 'reality', 'illusion', 'truth', 'knowledge']
        }
        
        # Find best matching category
        for category, patterns in categories.items():
            if any(pattern in question_lower for pattern in patterns):
                return category
        
        return 'general'
    
    def generate_knowledge_entry_id(self, question: str, category: str) -> str:
        """Generate a unique ID for a knowledge entry"""
        # Create hash from question and category
        content = f"{category}_{question.lower()}"
        hash_object = hashlib.md5(content.encode())
        hash_hex = hash_object.hexdigest()[:8]
        
        # Count existing entries in category
        existing_count = sum(1 for entry in self.knowledge_base.get("knowledge_base", []) 
                           if entry.get("category") == category)
        
        return f"{category}_{existing_count + 1}_{hash_hex}"
    
    def learn_from_interaction(self, user_question: str, system_response: str, 
                             source: str = "conversation", confidence: float = 0.8) -> bool:
        """
        Learn from a user interaction by potentially adding it to the knowledge base
        
        Args:
            user_question: The question asked by the user
            system_response: The response given by the system
            source: Source of the information (conversation, wikipedia, etc.)
            confidence: Confidence level in the quality of this interaction
        
        Returns:
            bool: True if learning was successful, False otherwise
        """
        try:
            # Clean and validate inputs
            if not user_question or not system_response:
                return False
                
            if len(user_question.strip()) < 5 or len(system_response.strip()) < 20:
                return False
            
            # Check if this question already exists
            if self.question_exists(user_question):
                logger.info(f"Question already exists in knowledge base: {user_question[:50]}...")
                return False
            
            # Humanize the response if it's from Wikipedia or third-person source
            if source == "wikipedia" or "Adi Shankara" in system_response:
                humanized_response = self.humanize_wikipedia_content(system_response, 
                                                                   self.categorize_question(user_question))
            else:
                humanized_response = system_response
            
            # Extract keywords and categorize
            keywords = self.extract_keywords_from_question(user_question)
            category = self.categorize_question(user_question)
            
            # Create new knowledge entry
            new_entry = {
                "id": self.generate_knowledge_entry_id(user_question, category),
                "question": user_question.strip(),
                "answer": humanized_response.strip(),
                "keywords": keywords,
                "category": category,
                "source": source,
                "confidence": confidence,
                "created_date": datetime.now().isoformat(),
                "usage_count": 0,
                "last_used": None
            }
            
            # Decide whether to auto-learn or queue for manual review
            if confidence >= self.learning_threshold:
                # Auto-learn high-confidence entries
                self.knowledge_base["knowledge_base"].append(new_entry)
                self.learning_stats["successful_learnings"] += 1
                self.log_learning_event(f"AUTO-LEARNED: {user_question[:50]}...", new_entry)
                self.save_knowledge_base()
                return True
            else:
                # Queue low-confidence entries for manual review
                self.manual_review_queue.append(new_entry)
                self.learning_stats["manual_reviews"] += 1
                self.log_learning_event(f"QUEUED FOR REVIEW: {user_question[:50]}...", new_entry)
                return False
                
        except Exception as e:
            logger.error(f"Error in learn_from_interaction: {e}")
            return False
    
    def question_exists(self, question: str) -> bool:
        """Check if a similar question already exists in the knowledge base"""
        question_lower = question.lower().strip()
        
        for entry in self.knowledge_base.get("knowledge_base", []):
            existing_question = entry.get("question", "").lower().strip()
            
            # Check for exact match
            if question_lower == existing_question:
                return True
            
            # Check for high similarity (simple word overlap)
            question_words = set(question_lower.split())
            existing_words = set(existing_question.split())
            
            if len(question_words) > 0 and len(existing_words) > 0:
                overlap = len(question_words.intersection(existing_words))
                similarity = overlap / max(len(question_words), len(existing_words))
                
                if similarity > 0.8:  # 80% similarity threshold
                    return True
        
        return False
    
    def log_learning_event(self, event: str, entry: dict):
        """Log learning events for monitoring and debugging"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "event": event,
                "entry_id": entry.get("id", "unknown"),
                "category": entry.get("category", "unknown"),
                "confidence": entry.get("confidence", 0.0),
                "source": entry.get("source", "unknown")
            }
            
            with open(self.learning_log, 'a', encoding='utf-8') as f:
                f.write(f"{json.dumps(log_entry)}\n")
                
        except Exception as e:
            logger.error(f"Error logging learning event: {e}")
    
    def update_usage_statistics(self, entry_id: str):
        """Update usage statistics when a knowledge entry is used"""
        try:
            for entry in self.knowledge_base.get("knowledge_base", []):
                if entry.get("id") == entry_id:
                    entry["usage_count"] = entry.get("usage_count", 0) + 1
                    entry["last_used"] = datetime.now().isoformat()
                    break
            
            # Save periodically (every 10 uses)
            total_uses = sum(entry.get("usage_count", 0) for entry in self.knowledge_base.get("knowledge_base", []))
            if total_uses % 10 == 0:
                self.save_knowledge_base()
                
        except Exception as e:
            logger.error(f"Error updating usage statistics: {e}")
    
    def get_learning_statistics(self) -> Dict:
        """Get current learning statistics"""
        current_size = len(self.knowledge_base.get("knowledge_base", []))
        
        self.learning_stats.update({
            "knowledge_base_size": current_size,
            "manual_review_queue_size": len(self.manual_review_queue),
            "last_check": datetime.now().isoformat()
        })
        
        return self.learning_stats.copy()
    
    def process_manual_review_queue(self, auto_approve_threshold: float = 0.9) -> int:
        """Process the manual review queue, auto-approving high-confidence entries"""
        approved_count = 0
        
        try:
            remaining_queue = []
            
            for entry in self.manual_review_queue:
                if entry.get("confidence", 0.0) >= auto_approve_threshold:
                    # Auto-approve very high confidence entries
                    self.knowledge_base["knowledge_base"].append(entry)
                    self.learning_stats["successful_learnings"] += 1
                    self.log_learning_event(f"AUTO-APPROVED FROM QUEUE: {entry.get('question', '')[:50]}...", entry)
                    approved_count += 1
                else:
                    remaining_queue.append(entry)
            
            self.manual_review_queue = remaining_queue
            
            if approved_count > 0:
                self.save_knowledge_base()
            
            return approved_count
            
        except Exception as e:
            logger.error(f"Error processing manual review queue: {e}")
            return 0
    
    def get_manual_review_queue(self) -> List[Dict]:
        """Get the current manual review queue"""
        return self.manual_review_queue.copy()
    
    def approve_manual_entry(self, entry_id: str) -> bool:
        """Manually approve an entry from the review queue"""
        try:
            for i, entry in enumerate(self.manual_review_queue):
                if entry.get("id") == entry_id:
                    # Move to knowledge base
                    self.knowledge_base["knowledge_base"].append(entry)
                    self.manual_review_queue.pop(i)
                    self.learning_stats["successful_learnings"] += 1
                    self.log_learning_event(f"MANUALLY APPROVED: {entry.get('question', '')[:50]}...", entry)
                    self.save_knowledge_base()
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error approving manual entry: {e}")
            return False
    
    def reject_manual_entry(self, entry_id: str) -> bool:
        """Manually reject an entry from the review queue"""
        try:
            for i, entry in enumerate(self.manual_review_queue):
                if entry.get("id") == entry_id:
                    self.manual_review_queue.pop(i)
                    self.log_learning_event(f"MANUALLY REJECTED: {entry.get('question', '')[:50]}...", entry)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error rejecting manual entry: {e}")
            return False
