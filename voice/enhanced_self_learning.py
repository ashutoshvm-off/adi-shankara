"""
Enhanced Self-Learning Engine with Multilingual Support
Implements continuous learning from interactions in multiple languages.
"""

import json
import re
import time
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class EnhancedSelfLearningEngine:
    """Enhanced engine that enables multilingual learning and response improvement"""
    
    def __init__(self, 
                 knowledge_file="shankaracharya_knowledge.json",
                 translation_cache_file="translation_cache.json",
                 learning_log="learning_log.txt"):
        
        self.knowledge_file = knowledge_file
        self.translation_cache_file = translation_cache_file
        self.learning_log = learning_log
        
        # Load knowledge bases
        self.knowledge_base = self.load_knowledge_base()
        self.translation_cache = self.load_translation_cache()
        
        # Confidence thresholds
        self.learning_threshold = 0.7  # Base threshold for auto-learning
        self.translation_threshold = 0.85  # Higher threshold for translation caching
        
        # Review queues
        self.manual_review_queue = []
        self.translation_review_queue = []
        
        # Language-specific learning stats
        self.learning_stats = {
            "total_interactions": defaultdict(int),
            "successful_learnings": defaultdict(int),
            "translation_cache_hits": defaultdict(int),
            "knowledge_base_size": len(self.knowledge_base.get("knowledge_base", [])),
            "translation_cache_size": len(self.translation_cache),
            "last_update": datetime.now().isoformat()
        }
        
        # Initialize language tracking
        self.supported_languages = {
            'en': 'english',
            'ml': 'malayalam',
            'sa': 'sanskrit',
            'hi': 'hindi',
            'ta': 'tamil',
            'te': 'telugu'
        }
        
        # Performance metrics
        self.performance_metrics = defaultdict(lambda: {
            'response_time': [],
            'confidence_scores': [],
            'user_feedback': []
        })
    
    def load_translation_cache(self) -> Dict:
        """Load the translation cache"""
        try:
            if os.path.exists(self.translation_cache_file):
                with open(self.translation_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading translation cache: {e}")
            return {}
    
    def save_translation_cache(self):
        """Save the translation cache"""
        try:
            with open(self.translation_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.translation_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving translation cache: {e}")
    
    def learn_from_multilingual_interaction(self,
                                          user_question: str,
                                          system_response: str,
                                          source_lang: str,
                                          target_lang: str,
                                          translation: Optional[str] = None,
                                          confidence: float = 0.8,
                                          source: str = "conversation") -> bool:
        """
        Learn from a multilingual interaction
        
        Args:
            user_question: Original user question
            system_response: System's response
            source_lang: Source language code
            target_lang: Target language code
            translation: Translated response (if any)
            confidence: Confidence level
            source: Source of the interaction
            
        Returns:
            bool: True if learning was successful
        """
        try:
            # Track language-specific interaction
            self.learning_stats["total_interactions"][source_lang] += 1
            self.learning_stats["total_interactions"][target_lang] += 1
            
            # Basic validation
            if not user_question or not system_response:
                return False
            
            # Learn the base interaction
            success = self.learn_from_interaction(
                user_question,
                system_response,
                source=source,
                confidence=confidence,
                language=source_lang
            )
            
            # If there's a translation, cache it if confidence is high enough
            if translation and confidence >= self.translation_threshold:
                cache_key = self._generate_translation_cache_key(
                    system_response, source_lang, target_lang
                )
                self.translation_cache[cache_key] = {
                    "translation": translation,
                    "confidence": confidence,
                    "last_used": datetime.now().isoformat(),
                    "use_count": 1
                }
                self.save_translation_cache()
                
                # Update stats
                self.learning_stats["successful_learnings"][target_lang] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Error in multilingual learning: {e}")
            return False
    
    def get_cached_translation(self,
                             text: str,
                             source_lang: str,
                             target_lang: str) -> Optional[str]:
        """
        Retrieve a cached translation if available
        
        Returns:
            Cached translation or None if not found
        """
        cache_key = self._generate_translation_cache_key(text, source_lang, target_lang)
        
        if cache_key in self.translation_cache:
            entry = self.translation_cache[cache_key]
            entry["use_count"] += 1
            entry["last_used"] = datetime.now().isoformat()
            self.learning_stats["translation_cache_hits"][target_lang] += 1
            return entry["translation"]
        
        return None
    
    def update_language_performance(self,
                                  language: str,
                                  response_time: float,
                                  confidence: float,
                                  user_feedback: Optional[float] = None):
        """Track performance metrics for each language"""
        metrics = self.performance_metrics[language]
        metrics['response_time'].append(response_time)
        metrics['confidence_scores'].append(confidence)
        if user_feedback is not None:
            metrics['user_feedback'].append(user_feedback)
    
    def get_language_performance_summary(self, language: str) -> Dict:
        """Get performance metrics summary for a language"""
        metrics = self.performance_metrics[language]
        
        if not metrics['response_time']:
            return {}
            
        return {
            'avg_response_time': sum(metrics['response_time']) / len(metrics['response_time']),
            'avg_confidence': sum(metrics['confidence_scores']) / len(metrics['confidence_scores']),
            'avg_user_feedback': sum(metrics['user_feedback']) / len(metrics['user_feedback']) if metrics['user_feedback'] else None,
            'total_interactions': self.learning_stats['total_interactions'][language],
            'cache_hits': self.learning_stats['translation_cache_hits'][language]
        }
    
    def _generate_translation_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate a unique key for translation caching"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{source_lang}_{target_lang}_{text_hash}"
    
    def cleanup_old_cache_entries(self, max_age_days: int = 30):
        """Remove old cache entries to prevent unbounded growth"""
        now = datetime.now()
        to_remove = []
        
        for key, entry in self.translation_cache.items():
            last_used = datetime.fromisoformat(entry["last_used"])
            age_days = (now - last_used).days
            
            if age_days > max_age_days:
                to_remove.append(key)
        
        for key in to_remove:
            del self.translation_cache[key]
        
        if to_remove:
            self.save_translation_cache()
            logger.info(f"Cleaned up {len(to_remove)} old cache entries")
    
    def get_learning_statistics(self) -> Dict:
        """Get comprehensive learning statistics"""
        stats = self.learning_stats.copy()
        
        # Add language-specific performance metrics
        stats['language_performance'] = {
            lang: self.get_language_performance_summary(lang)
            for lang in self.supported_languages
        }
        
        # Add cache efficiency metrics
        total_cache_hits = sum(stats['translation_cache_hits'].values())
        total_interactions = sum(stats['total_interactions'].values())
        stats['cache_hit_rate'] = total_cache_hits / total_interactions if total_interactions > 0 else 0
        
        return stats

# Example usage
if __name__ == "__main__":
    engine = EnhancedSelfLearningEngine()
    
    # Example: Learning from a multilingual interaction
    engine.learn_from_multilingual_interaction(
        user_question="What is Advaita Vedanta?",
        system_response="Advaita Vedanta is a school of Hindu philosophy...",
        source_lang="en",
        target_lang="ml",
        translation="അദ്വൈത വേദാന്തം ഹിന്ദു തത്വചിന്തയുടെ ഒരു ശാഖയാണ്...",
        confidence=0.95
    )
    
    # Check cache
    cached = engine.get_cached_translation(
        "Advaita Vedanta is a school of Hindu philosophy...",
        "en",
        "ml"
    )
    
    if cached:
        print("✓ Translation found in cache!")
    
    # Get statistics
    stats = engine.get_learning_statistics()
    print("\n📊 Learning Statistics:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
