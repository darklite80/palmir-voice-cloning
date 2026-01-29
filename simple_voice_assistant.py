#!/usr/bin/env python3
"""
Simple Voice Assistant using Distiller Hardware
- Listens for speech using Parakeet ASR
- Responds using your cloned voice via XTTS
- Uses LED feedback for visual status
"""

import sys
sys.path.insert(0, '/opt/distiller-sdk')
sys.path.insert(0, '/home/distiller/projects/voice cloning')

from distiller_sdk.parakeet import Parakeet
from distiller_sdk.hardware.led import LED
from distiller_sdk.hardware.audio import Audio
from distiller_xtts_tts import DistillerXTTS
from pathlib import Path


def find_reference_audio():
    """Find a reference audio file for voice cloning."""
    # Check uploads directory
    uploads_dir = Path("uploads")
    audio_files = list(uploads_dir.glob("*.wav"))

    if audio_files:
        return str(audio_files[0])

    # Check voice profiles
    profiles_dir = Path("voice_profiles")
    if profiles_dir.exists():
        for profile_dir in profiles_dir.iterdir():
            if profile_dir.is_dir() and profile_dir.name.startswith("profile_"):
                audio_files = list(profile_dir.glob("*.wav"))
                if audio_files:
                    return str(audio_files[0])

    return None


def main():
    print("=" * 60)
    print("🎙️  Voice Assistant with Cloned Voice")
    print("=" * 60)

    # Find reference audio
    print("\n1. Looking for reference audio...")
    reference_audio = find_reference_audio()

    if not reference_audio:
        print("❌ No reference audio found!")
        print("   Please upload a voice sample first using the web interface:")
        print("   http://localhost:5001")
        return

    print(f"✓ Using reference: {reference_audio}")

    # Initialize hardware
    print("\n2. Initializing hardware...")
    try:
        asr = Parakeet()
        led = LED(use_sudo=True)
        audio = Audio()
        tts = DistillerXTTS(reference_audio=reference_audio)
        print("✓ All hardware initialized")
    except Exception as e:
        print(f"❌ Hardware initialization failed: {e}")
        return

    print("\n" + "=" * 60)
    print("Voice Assistant Ready!")
    print("=" * 60)
    print("\nPress Ctrl+C to exit")
    print("\nListening modes:")
    print("  • Push-to-talk: Speak and release to transcribe")
    print("  • Auto-detect: Automatic voice activity detection")
    print("\nStarting in auto-detect mode...")
    print("=" * 60)

    try:
        # Set LED to green (ready)
        led.set_rgb_color(0, 0, 255, 0)

        # Listen for speech with automatic voice detection
        for transcribed_text in asr.auto_record_and_transcribe():
            print(f"\n📝 You said: {transcribed_text}")

            # Blue LED (processing)
            led.set_rgb_color(0, 0, 0, 255)

            # Simple echo response (you can add AI/logic here)
            response = f"You said: {transcribed_text}"

            # Generate and play response with cloned voice
            print(f"🔊 Responding...")
            try:
                wav_path = tts.get_wav_file_path(response, output_name="temp_response.wav")
                audio.play(wav_path)
                print("✓ Response played")
            except Exception as e:
                print(f"❌ TTS error: {e}")

            # Green LED (ready)
            led.set_rgb_color(0, 0, 255, 0)
            print("\nListening...")

    except KeyboardInterrupt:
        print("\n\nStopping voice assistant...")

    finally:
        # Cleanup
        led.turn_off_all()
        asr.cleanup()
        audio.close()
        print("✓ Goodbye!")


if __name__ == "__main__":
    main()
