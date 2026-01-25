#!/usr/bin/env python3
"""
XTTS v2 Voice Cloning Tool for Palmir Device

This script provides local voice cloning capabilities using Coqui TTS XTTS v2.
It can record reference audio, clone voices, and generate speech.
"""

import sys
import os
import argparse
import warnings
warnings.filterwarnings('ignore')

# Add Palmir SDK to path
sys.path.insert(0, '/opt/distiller-cm5-sdk')

import torch
import torchaudio
import numpy as np
from TTS.api import TTS


class VoiceCloner:
    """Voice cloning using XTTS v2 with Palmir hardware integration."""

    def __init__(self, device="cpu"):
        """
        Initialize the voice cloner.

        Args:
            device: Device to run on ('cpu' or 'cuda')
        """
        print("🎤 Initializing XTTS v2 Voice Cloner...")
        print(f"📱 Running on: {device}")

        self.device = device
        self.tts = None
        self.audio = None
        self._load_model()

    def _load_model(self):
        """Load the XTTS v2 model."""
        try:
            print("⏳ Loading XTTS v2 model (this may take a minute)...")
            # Initialize TTS with XTTS v2
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2",
                          progress_bar=True).to(self.device)
            print("✅ Model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise

    def _init_audio(self):
        """Initialize Palmir audio hardware (lazy loading)."""
        if self.audio is None:
            try:
                from distiller_cm5_sdk.hardware.audio import Audio
                self.audio = Audio()
                print("✅ Palmir audio hardware initialized")
            except Exception as e:
                print(f"⚠️  Could not initialize Palmir audio: {e}")
                print("   Audio features will be limited")

    def record_reference(self, duration=10, output_path="reference.wav"):
        """
        Record reference audio using Palmir microphone.

        Args:
            duration: Recording duration in seconds
            output_path: Where to save the recording

        Returns:
            Path to recorded file
        """
        self._init_audio()

        if self.audio is None:
            print("❌ Audio hardware not available. Please provide a .wav file instead.")
            return None

        print(f"🎙️  Recording {duration} seconds of reference audio...")
        print("   Speak clearly and naturally!")

        try:
            # Record audio at 22050 Hz (XTTS v2 native sample rate)
            audio_data = self.audio.record_audio(duration=duration, sample_rate=22050)
            self.audio.save_recording(output_path, audio_data, sample_rate=22050)
            print(f"✅ Reference audio saved to: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ Recording failed: {e}")
            return None

    def clone_voice(self, text, reference_audio, output_path="cloned_voice.wav", language="en"):
        """
        Clone a voice and generate speech.

        Args:
            text: Text to synthesize
            reference_audio: Path to reference audio file (WAV format)
            output_path: Where to save generated audio
            language: Language code (en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, hu, ko, hi)

        Returns:
            Path to generated audio file
        """
        if not os.path.exists(reference_audio):
            print(f"❌ Reference audio not found: {reference_audio}")
            return None

        print(f"🎭 Cloning voice from: {reference_audio}")
        print(f"💬 Text: {text}")
        print(f"🌍 Language: {language}")
        print("⏳ Generating speech (this may take 10-30 seconds)...")

        try:
            # Generate speech with voice cloning
            self.tts.tts_to_file(
                text=text,
                speaker_wav=reference_audio,
                language=language,
                file_path=output_path
            )
            print(f"✅ Cloned voice saved to: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ Voice cloning failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def play_audio(self, audio_path):
        """
        Play audio file through Palmir speakers.

        Args:
            audio_path: Path to audio file to play
        """
        self._init_audio()

        if self.audio is None:
            print(f"⚠️  Audio playback not available. File saved to: {audio_path}")
            return

        print(f"🔊 Playing: {audio_path}")
        try:
            self.audio.play_audio_file(audio_path)
            print("✅ Playback complete")
        except Exception as e:
            print(f"❌ Playback failed: {e}")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="XTTS v2 Voice Cloning Tool")
    parser.add_argument("--mode", choices=["record", "clone", "full"], default="full",
                       help="Mode: record reference, clone voice, or full pipeline")
    parser.add_argument("--text", type=str,
                       default="Hello! This is a test of voice cloning technology.",
                       help="Text to synthesize")
    parser.add_argument("--reference", type=str, default="reference.wav",
                       help="Path to reference audio file")
    parser.add_argument("--output", type=str, default="cloned_voice.wav",
                       help="Output file path")
    parser.add_argument("--duration", type=int, default=10,
                       help="Recording duration in seconds (for record mode)")
    parser.add_argument("--language", type=str, default="en",
                       help="Language code (en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, hu, ko, hi)")
    parser.add_argument("--no-play", action="store_true",
                       help="Don't play the generated audio")
    parser.add_argument("--device", type=str, default="cpu",
                       help="Device to run on (cpu or cuda)")

    args = parser.parse_args()

    print("=" * 60)
    print("🎙️  XTTS v2 Voice Cloning Tool - Palmir Edition")
    print("=" * 60)

    cloner = VoiceCloner(device=args.device)

    if args.mode == "record":
        # Record reference audio only
        cloner.record_reference(duration=args.duration, output_path=args.reference)

    elif args.mode == "clone":
        # Clone voice using existing reference
        output = cloner.clone_voice(args.text, args.reference, args.output, args.language)
        if output and not args.no_play:
            cloner.play_audio(output)

    elif args.mode == "full":
        # Full pipeline: record + clone
        print("\n📋 FULL PIPELINE MODE")
        print("   1. Record reference audio")
        print("   2. Clone voice and generate speech")
        print()

        # Step 1: Record reference
        ref_path = cloner.record_reference(duration=args.duration, output_path=args.reference)
        if ref_path is None:
            print("❌ Pipeline failed at recording step")
            return 1

        print()

        # Step 2: Clone voice
        output = cloner.clone_voice(args.text, ref_path, args.output, args.language)
        if output and not args.no_play:
            cloner.play_audio(output)

    print("\n" + "=" * 60)
    print("✅ Done!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
