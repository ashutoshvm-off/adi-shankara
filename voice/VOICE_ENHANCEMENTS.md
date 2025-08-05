# Adi Shankara Voice Enhancement Summary

## Voice Improvements Made

### 1. **Edge TTS Voice Selection (Premium Quality)**
- **REMOVED** female voices: AriaNeural, SoniaNeural, ClaraNeural
- **ADDED** masculine, sage-like voices:
  - `en-IN-PrabhatNeural` (Preferred - Indian English male voice)
  - `en-US-DavisNeural` (Deep, mature male voice)
  - `en-US-JasonNeural` (Warm, authoritative male voice)
  - `en-US-TonyNeural` (Rich, confident male voice)
  - `en-GB-RyanNeural` (Distinguished British male voice)
  - `en-AU-WilliamNeural` (Mature Australian male voice)
  - `en-US-GuyNeural` (Deep, resonant male voice)
  - `en-GB-ThomasNeural` (Authoritative British male voice)

### 2. **Pyttsx3 Voice Selection Enhancement**
- **Prioritized** male voices (+15 score bonus)
- **Enhanced** scoring for deep, mature names (+12 points)
- **Penalized** female/high-pitched voices (-10 points)
- **Avoided** robotic voices (-15 points)
- **Added** voice characteristics configuration:
  - Slower speech rate (150 vs default 200)
  - High volume (0.9) for clear authority
  - Measured, contemplative delivery

### 3. **Coqui TTS Model Enhancement**
- **Multiple model fallbacks** for better voice options
- **Improved error handling** for model loading
- **Focus on** high-quality English models suitable for philosophical content

### 4. **Speech Enhancement for Sage-like Delivery**
Enhanced the `enhance_text_for_speech` function with:

#### Contemplative Pauses:
- Longer pauses between sentences (`... `)
- Brief pauses at commas (`.. `)
- Emphasis pauses before key concepts

#### Key Concept Emphasis:
- Pauses before: Advaita, Brahman, consciousness, Self, truth, reality, liberation
- Special emphasis for profound statements

#### Sanskrit Pronunciation Guide:
- moksha → mok-sha
- dharma → dhar-ma
- karma → kar-ma
- maya → ma-ya
- atman → at-man
- brahman → brah-man
- vedanta → ve-dan-ta
- upanishad → oo-pa-ni-shad
- samadhi → sa-ma-dhee
- samsara → sam-sa-ra
- nirvana → nir-va-na
- mantra → man-tra

## Expected Voice Characteristics

### 🎭 **Masculine Presence**
- Deep, mature male voice
- Authoritative but gentle tone
- Wisdom-conveying gravitas

### 🧘 **Sage-like Delivery**
- Slower, contemplative speech rate
- Thoughtful pauses between concepts
- Clear, measured pronunciation

### 🕉️ **Cultural Authenticity**
- Preference for Indian English accent (en-IN-PrabhatNeural)
- Proper Sanskrit term pronunciation
- Respectful, traditional speaking style

### 💭 **Philosophical Depth**
- Emphasis on key spiritual concepts
- Natural pauses for reflection
- Clear articulation of complex ideas

## Testing

Run the test script to verify voice improvements:
```bash
python test_sage_voice.py
```

This will test all voice enhancements and verify the masculine, sage-like characteristics are working correctly.

## Technical Implementation

The voice system now uses a hierarchical approach (Coqui TTS disabled by user request):
1. **Edge TTS** (Highest quality) - Masculine voice selection with Indian English preference
2. **Pyttsx3** (Medium quality) - Enhanced male voice preference with sage-like characteristics
3. **Google TTS** (Fallback) - Basic functionality

**Note: Coqui TTS has been disabled by user request to reduce system load and dependencies.**

All implementations prioritize masculine voices and include the enhanced speech processing for sage-like delivery.
