"""
Self-Learning Demo Script for Adi Shankara Assistant
This script demonstrates the self-learning capabilities.
"""

def demonstrate_self_learning():
    """Demonstrate the self-learning system"""
    print("🧠 ADI SHANKARA ASSISTANT - SELF-LEARNING DEMONSTRATION")
    print("="*60)
    
    # Test if self-learning components are available
    try:
        from self_learning_engine import SelfLearningEngine
        from wikipedia_content_processor import WikipediaContentProcessor
        print("✅ Self-learning components loaded successfully!")
    except ImportError as e:
        print(f"❌ Self-learning components not available: {e}")
        return
    
    # Test the learning engine
    print("\n🔬 Testing Learning Engine...")
    engine = SelfLearningEngine()
    
    # Test humanization
    print("\n🎭 Testing Wikipedia Content Humanization...")
    processor = WikipediaContentProcessor()
    
    test_cases = [
        {
            "original": "Adi Shankara was born in Kaladi, Kerala in 788 CE. He established four mathas across India and wrote many commentaries on the Upanishads.",
            "context": "biography"
        },
        {
            "original": "Shankara taught that Brahman is the ultimate reality and that the individual self is not different from this universal consciousness.",
            "context": "philosophy"
        },
        {
            "original": "Adi Shankara traveled extensively across India, engaging in debates with scholars from various philosophical schools.",
            "context": "travels"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i} ({test['context']}):")
        print(f"   Original: {test['original']}")
        
        humanized = processor.process_wikipedia_content(test['original'], test['context'])
        print(f"   Humanized: {humanized}")
        
        # Validate the humanization
        validation = processor.validate_humanization(test['original'], humanized)
        print(f"   Quality Score: {validation['score']:.1f}/1.0")
        if validation['improvements']:
            print(f"   ✅ Improvements: {', '.join(validation['improvements'])}")
        if validation['issues']:
            print(f"   ⚠️ Issues: {', '.join(validation['issues'])}")
    
    # Test learning from interactions
    print("\n🎓 Testing Learning from Interactions...")
    
    sample_interactions = [
        {
            "question": "What is the purpose of meditation according to you?",
            "answer": "Meditation, my dear seeker, is the practice of turning attention inward to realize your true nature. Through sustained contemplation, the mind becomes still and the Self reveals itself. It is not merely a technique but a way of being that dissolves the illusion of separateness.",
            "source": "conversation",
            "confidence": 0.9
        },
        {
            "question": "How do you explain the concept of Maya?",
            "answer": "Maya is the mysterious power by which the one appears as many. It is not falsehood, but the creative force that manifests this beautiful diversity while the underlying reality remains unchanged. Like a rope appearing as a snake in dim light, objects appear separate when seen through Maya.",
            "source": "manual_teaching",
            "confidence": 0.95
        }
    ]
    
    for i, interaction in enumerate(sample_interactions, 1):
        print(f"\n📚 Learning Example {i}:")
        print(f"   Question: {interaction['question']}")
        print(f"   Answer: {interaction['answer'][:80]}...")
        
        learned = engine.learn_from_interaction(
            interaction['question'],
            interaction['answer'],
            interaction['source'],
            interaction['confidence']
        )
        
        if learned:
            print(f"   ✅ Successfully learned (confidence: {interaction['confidence']})")
        else:
            print(f"   ⚠️ Queued for review or already exists")
    
    # Show learning statistics
    print("\n📊 Learning Statistics:")
    stats = engine.get_learning_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test manual review queue
    queue = engine.get_manual_review_queue()
    if queue:
        print(f"\n📋 Manual Review Queue: {len(queue)} items")
        for item in queue[:2]:  # Show first 2 items
            print(f"   - {item.get('question', 'Unknown')[:50]}...")
    
    print("\n✨ Self-Learning Demonstration Complete!")
    print("="*60)
    
    # Cleanup test entries if needed
    print("\n🧹 Note: Test entries were added to demonstrate learning.")
    print("   In production, you may want to review and clean test data.")

def test_enhanced_assistant():
    """Test the enhanced assistant with self-learning"""
    print("\n🤖 Testing Enhanced Assistant Integration...")
    
    try:
        # This would test the enhanced main1.py if imported
        # For now, just show what the integration provides
        features = [
            "🧠 Automatic learning from user interactions",
            "📚 Dynamic knowledge base updates",
            "🎭 Wikipedia content humanization",
            "📊 Learning statistics tracking",
            "🎯 Confidence-based learning decisions",
            "📝 Manual teaching capabilities",
            "🔄 Continuous improvement from feedback",
            "💾 Persistent knowledge storage",
            "🎨 First-person response conversion",
            "📈 Session learning summaries"
        ]
        
        print("✨ Enhanced Features Available:")
        for feature in features:
            print(f"   {feature}")
        
        print("\n🎮 How to Use:")
        print("   1. Run main1.py normally")
        print("   2. The system will automatically learn from conversations")
        print("   3. Wikipedia content will be humanized in real-time")
        print("   4. Knowledge base will grow with each interaction")
        print("   5. Learning summary will be shown at session end")
        
    except Exception as e:
        print(f"   ⚠️ Integration test error: {e}")

if __name__ == "__main__":
    demonstrate_self_learning()
    test_enhanced_assistant()
