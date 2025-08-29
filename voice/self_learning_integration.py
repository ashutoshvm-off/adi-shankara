"""
Enhanced Self-Learning Integration for main1.py
This module extends the main1.py with self-learning capabilities.
"""

import json
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime

# Import our self-learning components
try:
    from self_learning_engine import SelfLearningEngine
    from wikipedia_content_processor import WikipediaContentProcessor
    SELF_LEARNING_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Self-learning components not available: {e}")
    SELF_LEARNING_AVAILABLE = False

logger = logging.getLogger(__name__)

class SelfLearningMixin:
    """
    Mixin class to add self-learning capabilities to the NaturalShankaraAssistant
    This can be integrated into the existing main1.py
    """
    
    def __init_self_learning__(self):
        """Initialize self-learning components"""
        if SELF_LEARNING_AVAILABLE:
            try:
                self.learning_engine = SelfLearningEngine()
                self.content_processor = WikipediaContentProcessor()
                self.learning_enabled = True
                self.learning_mode = "auto"  # auto, manual, disabled
                self.feedback_collection = True
                
                # Learning statistics
                self.session_stats = {
                    "questions_answered": 0,
                    "new_learnings": 0,
                    "wikipedia_humanized": 0,
                    "knowledge_base_updates": 0,
                    "session_start": datetime.now().isoformat()
                }
                
                print("🧠 Self-learning system initialized successfully!")
                logger.info("Self-learning components initialized")
                
            except Exception as e:
                logger.error(f"Error initializing self-learning: {e}")
                self.learning_enabled = False
                print("⚠ Self-learning initialization failed, continuing without it")
        else:
            self.learning_enabled = False
            print("💡 Self-learning components not available")
    
    def enhanced_get_wisdom_response(self, query: str) -> str:
        """
        Enhanced version of get_wisdom_response with self-learning
        This replaces the original get_wisdom_response method
        """
        if not query.strip():
            return self.create_natural_unknown_response()
        
        original_query = query
        self.session_stats["questions_answered"] += 1
        
        # Process the query through the original system
        response = self.get_original_wisdom_response(query)
        
        # Apply self-learning if enabled
        if self.learning_enabled and response:
            response = self.apply_self_learning(original_query, response)
        
        return response
    
    def get_original_wisdom_response(self, query: str) -> str:
        """
        Call the original get_wisdom_response method
        This should be the original method from main1.py
        """
        # This would call the original get_wisdom_response
        # For now, we'll use a placeholder that calls the existing logic
        return self.get_wisdom_response_original(query)
    
    def apply_self_learning(self, user_query: str, system_response: str) -> str:
        """Apply self-learning to improve the response and learn from interaction"""
        try:
            # Step 1: Determine the source of the response
            response_source = self.determine_response_source(system_response)
            
            # Step 2: Humanize Wikipedia content if needed
            if response_source == "wikipedia":
                humanized_response = self.content_processor.process_wikipedia_content(
                    system_response, 
                    self.learning_engine.categorize_question(user_query)
                )
                
                if humanized_response != system_response:
                    self.session_stats["wikipedia_humanized"] += 1
                    logger.info("Humanized Wikipedia content for user")
                    system_response = humanized_response
            
            # Step 3: Learn from this interaction
            if self.learning_mode == "auto":
                confidence = self.calculate_response_confidence(user_query, system_response, response_source)
                learned = self.learning_engine.learn_from_interaction(
                    user_query, 
                    system_response, 
                    response_source, 
                    confidence
                )
                
                if learned:
                    self.session_stats["new_learnings"] += 1
                    self.session_stats["knowledge_base_updates"] += 1
            
            # Step 4: Check if we should request user feedback
            if self.feedback_collection and self.should_request_feedback(user_query, system_response):
                system_response = self.add_feedback_request(system_response)
            
            return system_response
            
        except Exception as e:
            logger.error(f"Error in self-learning application: {e}")
            return system_response
    
    def determine_response_source(self, response: str) -> str:
        """Determine the likely source of a response"""
        if not response:
            return "unknown"
        
        # Check for Wikipedia indicators
        wikipedia_indicators = [
            "according to", "wikipedia", "sources indicate", "it is reported",
            "scholars believe", "historical records", "documented"
        ]
        
        if any(indicator in response.lower() for indicator in wikipedia_indicators):
            return "wikipedia"
        
        # Check for knowledge base indicators
        knowledge_indicators = [
            "I am Adi Shankara", "I was born", "I taught", "I established",
            "my philosophy", "my teaching", "my understanding"
        ]
        
        if any(indicator in response for indicator in knowledge_indicators):
            return "knowledge_base"
        
        # Check for third-person content (likely Wikipedia)
        if any(term in response for term in ["Adi Shankara", "Shankara", "he ", "his "]):
            return "wikipedia"
        
        return "generated"
    
    def calculate_response_confidence(self, query: str, response: str, source: str) -> float:
        """Calculate confidence level for the response quality"""
        confidence = 0.5  # Base confidence
        
        try:
            # Source-based confidence adjustment
            source_confidence = {
                "knowledge_base": 0.9,
                "wikipedia": 0.7,
                "generated": 0.6,
                "unknown": 0.4
            }
            
            confidence = source_confidence.get(source, 0.5)
            
            # Response length adjustment
            if 50 <= len(response) <= 500:
                confidence += 0.1
            elif len(response) < 20:
                confidence -= 0.2
            
            # First-person indicators (good for Adi Shankara responses)
            first_person_count = response.count(" I ") + response.count(" my ") + response.count(" me ")
            if first_person_count > 0:
                confidence += 0.1
            
            # Third-person indicators (needs improvement)
            third_person_terms = ["Adi Shankara", "Shankara", "he ", "his "]
            if any(term in response for term in third_person_terms):
                confidence -= 0.1
            
            # Spiritual/philosophical content indicators
            spiritual_terms = ["consciousness", "self", "truth", "realization", "wisdom", "advaita"]
            spiritual_count = sum(1 for term in spiritual_terms if term.lower() in response.lower())
            confidence += min(spiritual_count * 0.05, 0.2)
            
            # Ensure confidence stays within bounds
            confidence = max(0.0, min(1.0, confidence))
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def should_request_feedback(self, query: str, response: str) -> bool:
        """Determine if we should request user feedback"""
        # Request feedback for every 10th interaction
        return self.session_stats["questions_answered"] % 10 == 0
    
    def add_feedback_request(self, response: str) -> str:
        """Add a gentle feedback request to the response"""
        feedback_requests = [
            "\n\nDid this answer help clarify your understanding? Your feedback helps me improve.",
            "\n\nI hope this response resonated with you. Please let me know if you'd like me to explain anything differently.",
            "\n\nWas this explanation clear and helpful? I'm always learning to serve seekers better.",
        ]
        
        import random
        return response + random.choice(feedback_requests)
    
    def enhanced_search_wikipedia_content(self, query: str) -> Optional[str]:
        """
        Enhanced Wikipedia search that immediately humanizes content
        This replaces the original search_wikipedia_content method
        """
        # Call original Wikipedia search
        original_result = self.search_wikipedia_content_original(query)
        
        if original_result and self.learning_enabled:
            try:
                # Humanize the Wikipedia content
                humanized_result = self.content_processor.process_wikipedia_content(
                    original_result,
                    self.learning_engine.categorize_question(query)
                )
                
                # Log the improvement
                if humanized_result != original_result:
                    logger.info("Humanized Wikipedia search result")
                    self.session_stats["wikipedia_humanized"] += 1
                
                return humanized_result
                
            except Exception as e:
                logger.error(f"Error humanizing Wikipedia content: {e}")
                return original_result
        
        return original_result
    
    def process_user_feedback(self, feedback: str, last_query: str, last_response: str):
        """Process user feedback to improve the system"""
        if not self.learning_enabled:
            return
        
        try:
            feedback_lower = feedback.lower().strip()
            
            # Positive feedback indicators
            positive_indicators = [
                "yes", "good", "helpful", "clear", "perfect", "excellent", "thank", "great",
                "wonderful", "amazing", "brilliant", "correct", "right", "accurate"
            ]
            
            # Negative feedback indicators
            negative_indicators = [
                "no", "wrong", "incorrect", "bad", "unclear", "confusing", "improve",
                "better", "not helpful", "didn't help", "unclear"
            ]
            
            if any(indicator in feedback_lower for indicator in positive_indicators):
                # Positive feedback - increase confidence in this type of response
                self.learning_engine.learn_from_interaction(
                    last_query, 
                    last_response, 
                    "user_confirmed", 
                    0.9
                )
                logger.info("Received positive feedback, reinforcing learning")
                
            elif any(indicator in feedback_lower for indicator in negative_indicators):
                # Negative feedback - lower confidence or queue for review
                logger.info("Received negative feedback, queuing for review")
                # Could implement a feedback-based improvement system here
                
        except Exception as e:
            logger.error(f"Error processing user feedback: {e}")
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get current learning statistics"""
        stats = {
            "session_stats": self.session_stats.copy(),
            "learning_enabled": self.learning_enabled,
            "learning_mode": getattr(self, 'learning_mode', 'unknown')
        }
        
        if self.learning_enabled:
            engine_stats = self.learning_engine.get_learning_statistics()
            stats["engine_stats"] = engine_stats
        
        return stats
    
    def print_learning_summary(self):
        """Print a summary of learning activities for this session"""
        if not self.learning_enabled:
            print("🧠 Self-learning was not available this session")
            return
        
        stats = self.get_learning_statistics()
        session = stats["session_stats"]
        
        print("\n" + "="*50)
        print("🧠 SELF-LEARNING SESSION SUMMARY")
        print("="*50)
        print(f"📊 Questions Answered: {session['questions_answered']}")
        print(f"🎓 New Learnings: {session['new_learnings']}")
        print(f"📚 Wikipedia Content Humanized: {session['wikipedia_humanized']}")
        print(f"💾 Knowledge Base Updates: {session['knowledge_base_updates']}")
        
        if "engine_stats" in stats:
            engine = stats["engine_stats"]
            print(f"📈 Total Knowledge Entries: {engine.get('knowledge_base_size', 'unknown')}")
            print(f"✅ Successful Learnings (Total): {engine.get('successful_learnings', 'unknown')}")
        
        print("="*50)
    
    def enable_learning_mode(self, mode: str = "auto"):
        """Enable or change learning mode"""
        if not self.learning_enabled:
            print("❌ Self-learning components not available")
            return False
        
        valid_modes = ["auto", "manual", "disabled"]
        if mode not in valid_modes:
            print(f"❌ Invalid mode. Valid modes: {valid_modes}")
            return False
        
        self.learning_mode = mode
        print(f"🧠 Learning mode set to: {mode}")
        
        if mode == "disabled":
            print("⚠ Learning is now disabled for this session")
        elif mode == "manual":
            print("📝 Learning will require manual approval")
        else:
            print("🤖 Learning will happen automatically")
        
        return True
    
    def manually_teach(self, question: str, answer: str, category: str = "manual") -> bool:
        """Manually teach the system a new Q&A pair"""
        if not self.learning_enabled:
            print("❌ Self-learning components not available")
            return False
        
        try:
            # Humanize the answer if it contains third-person references
            if any(term in answer for term in ["Adi Shankara", "Shankara", "he ", "his "]):
                humanized_answer = self.content_processor.process_wikipedia_content(answer, category)
                print(f"📝 Humanized the answer: {answer[:50]}... -> {humanized_answer[:50]}...")
                answer = humanized_answer
            
            # Learn from this manual input
            learned = self.learning_engine.learn_from_interaction(
                question, 
                answer, 
                "manual_teaching", 
                0.95  # High confidence for manual teaching
            )
            
            if learned:
                print(f"✅ Successfully taught: {question[:50]}...")
                self.session_stats["new_learnings"] += 1
                self.session_stats["knowledge_base_updates"] += 1
                return True
            else:
                print(f"⚠ Question may already exist or needs review: {question[:50]}...")
                return False
                
        except Exception as e:
            logger.error(f"Error in manual teaching: {e}")
            print(f"❌ Error teaching the system: {e}")
            return False
    
    def humanize_existing_knowledge_base(self) -> bool:
        """Humanize the existing knowledge base"""
        if not self.learning_enabled:
            print("❌ Self-learning components not available")
            return False
        
        try:
            print("🔄 Humanizing existing knowledge base...")
            success = self.content_processor.batch_process_knowledge_base(
                self.learning_engine.knowledge_file
            )
            
            if success:
                print("✅ Knowledge base humanization completed!")
                # Reload the knowledge base
                self.learning_engine.knowledge_base = self.learning_engine.load_knowledge_base()
                return True
            else:
                print("❌ Knowledge base humanization failed")
                return False
                
        except Exception as e:
            logger.error(f"Error humanizing knowledge base: {e}")
            print(f"❌ Error humanizing knowledge base: {e}")
            return False

def integrate_self_learning_into_assistant(assistant_class):
    """
    Function to integrate self-learning capabilities into the existing assistant class
    This modifies the class to include self-learning features
    """
    
    # Add the mixin methods to the assistant class
    for method_name in dir(SelfLearningMixin):
        if not method_name.startswith('_'):
            method = getattr(SelfLearningMixin, method_name)
            if callable(method):
                setattr(assistant_class, method_name, method)
    
    # Override the original methods
    original_get_wisdom_response = assistant_class.get_wisdom_response
    original_search_wikipedia_content = getattr(assistant_class, 'search_wikipedia_content', None)
    
    def enhanced_get_wisdom_response_wrapper(self, query):
        # Initialize self-learning if not already done
        if not hasattr(self, 'learning_enabled'):
            self.__init_self_learning__()
        
        if hasattr(self, 'learning_enabled') and self.learning_enabled:
            return self.enhanced_get_wisdom_response(query)
        else:
            return original_get_wisdom_response(self, query)
    
    def enhanced_search_wikipedia_content_wrapper(self, query):
        # Store original result for comparison
        if original_search_wikipedia_content:
            self.search_wikipedia_content_original = lambda q: original_search_wikipedia_content(self, q)
            
            if hasattr(self, 'learning_enabled') and self.learning_enabled:
                return self.enhanced_search_wikipedia_content(query)
            else:
                return original_search_wikipedia_content(self, query)
        return None
    
    # Store original methods
    assistant_class.get_wisdom_response_original = original_get_wisdom_response
    if original_search_wikipedia_content:
        assistant_class.search_wikipedia_content_original = original_search_wikipedia_content
    
    # Replace with enhanced methods
    assistant_class.get_wisdom_response = enhanced_get_wisdom_response_wrapper
    if original_search_wikipedia_content:
        assistant_class.search_wikipedia_content = enhanced_search_wikipedia_content_wrapper
    
    print("🧠 Self-learning integration completed!")
    return assistant_class

# Example usage and testing
if __name__ == "__main__":
    # This would be used to test the self-learning components
    if SELF_LEARNING_AVAILABLE:
        print("🧠 Testing self-learning components...")
        
        # Test the learning engine
        engine = SelfLearningEngine()
        processor = WikipediaContentProcessor()
        
        # Test humanization
        test_content = "Adi Shankara was born in Kaladi, Kerala. He established four mathas and wrote many commentaries."
        humanized = processor.process_wikipedia_content(test_content, "biography")
        print(f"Original: {test_content}")
        print(f"Humanized: {humanized}")
        
        # Test learning
        test_question = "Where were you born?"
        test_answer = "I was born in Kaladi, Kerala, a sacred village blessed by divine grace."
        learned = engine.learn_from_interaction(test_question, test_answer, "test", 0.9)
        print(f"Learning test successful: {learned}")
        
        stats = engine.get_learning_statistics()
        print(f"Learning statistics: {stats}")
        
    else:
        print("❌ Self-learning components not available for testing")
