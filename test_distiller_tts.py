#!/usr/bin/env python3
"""
Test script for Distiller XTTS integration
Demonstrates how to use the cloned voice with Distiller-compatible interface
"""

import sys
from pathlib import Path
from distiller_xtts_tts import DistillerXTTS


def test_basic_speech():
    """Test basic speech synthesis."""
    print("=" * 60)
    print("Testing Distiller XTTS Integration")
    print("=" * 60)

    # Find a reference audio file
    reference_files = list(Path("uploads").glob("*.wav"))
    if not reference_files:
        print("❌ No reference audio found in uploads/")
        print("   Please upload a reference audio file first")
        return False

    reference_audio = str(reference_files[0])
    print(f"\n📁 Using reference: {reference_audio}")

    try:
        # Initialize TTS with cloned voice
        print("\n🔄 Initializing XTTS...")
        tts = DistillerXTTS(reference_audio=reference_audio)

        # Test 1: Generate WAV file
        print("\n✅ Test 1: Generating WAV file...")
        text = "Hello, this is a test of the voice cloning system on Distiller."
        wav_path = tts.get_wav_file_path(text, output_name="test_output.wav")
        print(f"   ✓ WAV saved to: {wav_path}")

        # Test 2: Stream to speakers
        print("\n✅ Test 2: Streaming to speakers...")
        test_text = "Voice cloning is working on the Distiller platform."
        tts.speak_stream(test_text, volume=70)
        print("   ✓ Audio played successfully")

        # Test 3: Multi-language support
        print("\n✅ Test 3: Multi-language support...")
        languages = tts.list_languages()
        print(f"   ✓ Supported languages: {', '.join(languages[:5])}...")

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_integration_example():
    """Show example code for integrating with Distiller SDK."""
    example = """
# Example: Integration with Distiller SDK
# ========================================

from distiller_xtts_tts import DistillerXTTS

# Option 1: Direct usage (similar to Piper)
tts = DistillerXTTS(reference_audio="uploads/my_voice.wav")

# Speak text
tts.speak_stream("Hello from Distiller!", volume=80)

# Save to file
wav_file = tts.get_wav_file_path("Test message", output_name="message.wav")

# Option 2: Replace Piper in existing code
# Instead of:
#   from distiller_sdk.piper import Piper
#   tts = Piper()

# Use:
#   from distiller_xtts_tts import DistillerXTTS
#   tts = DistillerXTTS(reference_audio="path/to/voice.wav")

# The interface is compatible!
tts.speak_stream("This works like Piper!")

# Option 3: Use with Distiller hardware
from distiller_sdk.hardware.audio import Audio

audio = Audio()
tts = DistillerXTTS(reference_audio="uploads/reference.wav")

# Generate speech
wav_path = tts.get_wav_file_path("Distiller is amazing!")

# Play using Distiller audio system
audio.play(wav_path)
audio.close()
"""
    print(example)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--example":
        show_integration_example()
    else:
        success = test_basic_speech()
        sys.exit(0 if success else 1)
