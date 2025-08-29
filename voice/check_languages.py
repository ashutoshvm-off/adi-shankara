#!/usr/bin/env python3
"""Check available languages in Google Translate"""

import googletrans
from googletrans import Translator

print("Checking Google Translate language support...")
print("=" * 50)

# Check specific codes
test_codes = ['hi', 'sa', 'ur', 'bn', 'gu', 'kn', 'ml', 'mr', 'pa', 'ta', 'te']
langs = googletrans.LANGUAGES

print("Indian language codes:")
for code in test_codes:
    name = langs.get(code, "NOT FOUND")
    print(f"{code}: {name}")

print("\nTesting Sanskrit translation...")
translator = Translator()

# Test Sanskrit detection
try:
    result = translator.detect("कः त्वम्?")
    print(f"Detected language: {result.lang} (confidence: {result.confidence})")
except Exception as e:
    print(f"Detection failed: {e}")

# Test Sanskrit translation
try:
    result = translator.translate("Hello", dest="sa")
    print(f"Translation to 'sa' worked: {result.text}")
except Exception as e:
    print(f"Translation to 'sa' failed: {e}")

# Test Hindi as alternative
try:
    result = translator.translate("Hello", dest="hi")
    print(f"Translation to Hindi worked: {result.text}")
except Exception as e:
    print(f"Translation to Hindi failed: {e}")
