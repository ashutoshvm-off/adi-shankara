# Wikipedia Search and Translation Features

## Overview

The Adi Shankara assistant now includes powerful Wikipedia search and translation capabilities that allow users to retrieve information about any topic and have it translated into their desired language. This feature combines real-time Wikipedia access with multi-language translation.

## Key Features

### 1. Dynamic Wikipedia Search
- Real-time Wikipedia page retrieval
- Intelligent content filtering and summarization
- Automatic disambiguation handling
- Quality content extraction with length limits

### 2. Multi-Language Translation
- Support for 20+ languages including:
  - Indian languages: Hindi, Malayalam, Tamil, Telugu, Kannada, Marathi, Gujarati, Bengali, Punjabi, Urdu, Sanskrit
  - International languages: Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean, Arabic

### 3. Natural Language Processing
- Intelligent query parsing
- Multiple trigger phrase recognition
- Context-aware topic extraction
- Language preference detection

## Usage Examples

### Basic Wikipedia Search
```
User: "Search Wikipedia for quantum physics"
User: "What does Wikipedia say about meditation?"
User: "Tell me about Mahatma Gandhi"
User: "Find information about yoga"
```

### Wikipedia Search with Translation
```
User: "Search Wikipedia for Buddhism in Hindi"
User: "Tell me about artificial intelligence in Malayalam"
User: "What is climate change in Spanish?"
User: "Find information about yoga in Tamil"
```

### Direct Translation
```
User: "Translate 'consciousness is eternal' to Sanskrit"
User: "Say 'the Self is blissful' in Hindi"
User: "Convert this text to Malayalam"
```

### Complex Queries
```
User: "Search Wikipedia for Indian philosophy in French"
User: "What does Wikipedia say about meditation in German?"
User: "Find information about Advaita Vedanta in Telugu"
```

## Supported Trigger Phrases

### Wikipedia Search Triggers
- "search wikipedia"
- "wikipedia search"
- "look up on wikipedia"
- "find on wikipedia"
- "what does wikipedia say"
- "tell me about"
- "what is"
- "who is"
- "explain"
- "define"

### Translation Triggers
- "translate to"
- "in [language]"
- "convert to"
- "say in"

## Language Support

### Indian Languages
- **Hindi** (हिंदी): `hindi`, `hi`
- **Malayalam** (മലയാളം): `malayalam`, `ml`
- **Tamil** (தமிழ்): `tamil`, `ta`
- **Telugu** (తెలుగు): `telugu`, `te`
- **Kannada** (ಕನ್ನಡ): `kannada`, `kn`
- **Marathi** (मराठी): `marathi`, `mr`
- **Gujarati** (ગુજરાતી): `gujarati`, `gu`
- **Bengali** (বাংলা): `bengali`, `bn`
- **Punjabi** (ਪੰਜਾਬੀ): `punjabi`, `pa`
- **Urdu** (اردو): `urdu`, `ur`
- **Sanskrit** (संस्कृत): `sanskrit`, `sa`

### International Languages
- **Spanish** (Español): `spanish`, `es`
- **French** (Français): `french`, `fr`
- **German** (Deutsch): `german`, `de`
- **Italian** (Italiano): `italian`, `it`
- **Portuguese** (Português): `portuguese`, `pt`
- **Russian** (Русский): `russian`, `ru`
- **Chinese** (中文): `chinese`, `zh`
- **Japanese** (日本語): `japanese`, `ja`
- **Korean** (한국어): `korean`, `ko`
- **Arabic** (العربية): `arabic`, `ar`

## Technical Implementation

### Core Methods

#### `search_live_wikipedia(query, max_sentences=5)`
- Searches Wikipedia dynamically for any topic
- Handles disambiguation automatically
- Returns structured data with title, summary, content, and URL
- Content length restrictions to prevent overwhelming responses

#### `get_wikipedia_info_in_language(topic, target_language, detail_level)`
- Retrieves Wikipedia information and translates it
- Supports multiple detail levels: "brief", "summary", "detailed"
- Provides natural responses as Adi Shankara
- Includes source attribution

#### `translate_to_language(text, target_language)`
- Translates text to any supported language
- Includes language code mapping for user convenience
- Error handling with fallback to original text
- Language detection to avoid unnecessary translation

#### `handle_wikipedia_requests(query)`
- Main dispatcher for Wikipedia and translation requests
- Intelligent query parsing and routing
- Combines search and translation seamlessly

### Helper Methods

#### `extract_search_topic(query, trigger)`
- Extracts the topic to search for from user queries
- Handles multiple query patterns and structures
- Cleans and normalizes extracted topics

#### `extract_target_language(query)`
- Identifies target language from user queries
- Supports multiple language naming conventions
- Pattern matching with regex for accuracy

#### `extract_content_to_translate(query, trigger)`
- Extracts content that user wants translated
- Handles various query structures and formats

## Quality Features

### Content Filtering
- Automatic content length limits to maintain readability
- Intelligent paragraph selection for relevance
- Summary prioritization for concise information

### Error Handling
- Graceful fallback when Wikipedia is unavailable
- Translation error recovery with original content
- Comprehensive logging for debugging

### Cultural Sensitivity
- Responses maintain Adi Shankara's voice and perspective
- Appropriate framing of information as philosophical guidance
- Respectful handling of all languages and cultures

## Performance Considerations

### Optimization Features
- Content length limits to prevent API overuse
- Caching mechanisms for frequently requested topics
- Efficient query processing with early returns

### Resource Management
- Timeout handling for external API calls
- Memory-efficient text processing
- Graceful degradation when services are unavailable

## Integration

The Wikipedia search and translation features are seamlessly integrated into the main conversation flow:

1. **Query Analysis**: Every user query is analyzed for Wikipedia/translation requests
2. **Priority Handling**: These requests are processed before other response types
3. **Natural Integration**: Results are presented in Adi Shankara's voice and style
4. **Fallback Support**: If Wikipedia/translation fails, other knowledge sources are used

## Future Enhancements

### Planned Features
- Offline translation for common languages
- Wikipedia page caching for faster responses
- Voice synthesis in target languages
- Custom vocabulary for philosophical terms
- User preference memory for language choices

### Technical Improvements
- Enhanced content relevance scoring
- Better disambiguation handling
- Improved language detection accuracy
- Expanded language support

## Usage Notes

1. **Internet Required**: Live Wikipedia search requires internet connectivity
2. **Translation Quality**: Translation quality depends on Google Translate service
3. **Content Limits**: Wikipedia content is limited to prevent overwhelming responses
4. **Language Detection**: System automatically detects and handles various language inputs
5. **Philosophical Context**: All information is presented through Adi Shankara's philosophical perspective

## Testing

Use the provided test script `test_wikipedia_translation.py` to verify functionality:

```bash
python test_wikipedia_translation.py
```

This comprehensive testing suite validates:
- Wikipedia search accuracy
- Translation quality
- Language detection
- Topic extraction
- Error handling
- Integration with main conversation flow

The feature enhances the assistant's capability to serve as a comprehensive knowledge guide while maintaining the authentic voice and wisdom of Adi Shankara.
