#!/usr/bin/env python3
"""
XTTS TTS module for Distiller SDK
Provides voice cloning TTS compatible with Distiller's Piper interface
"""

import os
import sys
import warnings
import subprocess
from pathlib import Path
from typing import Optional

warnings.filterwarnings('ignore')

# Configure environment for TTS
os.environ['COQUI_TOS_AGREED'] = '1'
os.environ['TORCHAUDIO_USE_BACKEND_DISPATCHER'] = '0'


class DistillerXTTS:
    """XTTS TTS for Distiller - Compatible with Piper interface."""

    def __init__(self, reference_audio: str, model_name: str = 'tts_models/multilingual/multi-dataset/xtts_v2'):
        """
        Initialize XTTS TTS with a reference voice.

        Args:
            reference_audio: Path to reference audio file for voice cloning
            model_name: XTTS model name (default: xtts_v2)
        """
        self.reference_audio = Path(reference_audio)
        self.model_name = model_name
        self.tts_model = None
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)

        if not self.reference_audio.exists():
            raise FileNotFoundError(f"Reference audio not found: {reference_audio}")

        # Initialize model
        self._load_model()

    def _load_model(self):
        """Load the XTTS model with proper PyTorch configuration."""
        print(f"Loading XTTS model: {self.model_name}...")

        # Configure PyTorch to load TTS models
        import torch
        original_load = torch.load

        def patched_load(*args, **kwargs):
            kwargs.setdefault('weights_only', False)
            return original_load(*args, **kwargs)

        torch.load = patched_load

        try:
            from TTS.api import TTS
            self.tts_model = TTS(self.model_name, progress_bar=False)
            print("✅ XTTS model loaded successfully!")
        finally:
            torch.load = original_load

    def speak_stream(self, text: str, language: str = "en", volume: int = 100,
                    sound_card_name: Optional[str] = None):
        """
        Synthesize speech and stream directly to speakers.
        Compatible with Distiller Piper interface.

        Args:
            text: Text to synthesize
            language: Language code (default: 'en')
            volume: Volume level 0-100 (default: 100)
            sound_card_name: Optional sound card name for playback
        """
        # Generate speech to temporary file
        output_file = self.output_dir / "temp_output.wav"

        print(f"Generating speech: '{text}' in {language}")
        self.tts_model.tts_to_file(
            text=text,
            speaker_wav=str(self.reference_audio),
            language=language,
            file_path=str(output_file)
        )

        # Play audio using aplay
        cmd = ["aplay", "-q"]

        if sound_card_name:
            cmd.extend(["-D", sound_card_name])

        # Set volume (using amixer if volume != 100)
        if volume != 100:
            vol_percent = max(0, min(100, volume))
            try:
                subprocess.run(["amixer", "-q", "sset", "Master", f"{vol_percent}%"],
                             check=False, capture_output=True)
            except Exception:
                pass  # Ignore volume control errors

        cmd.append(str(output_file))

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Playback error: {e}")
            raise

    def get_wav_file_path(self, text: str, language: str = "en",
                         output_name: Optional[str] = None) -> str:
        """
        Generate speech and save to WAV file.
        Compatible with Distiller Piper interface.

        Args:
            text: Text to synthesize
            language: Language code (default: 'en')
            output_name: Optional output filename (default: 'output.wav')

        Returns:
            Path to generated WAV file
        """
        if output_name is None:
            output_name = "output.wav"

        output_file = self.output_dir / output_name

        print(f"Generating WAV: '{text}' -> {output_file}")
        self.tts_model.tts_to_file(
            text=text,
            speaker_wav=str(self.reference_audio),
            language=language,
            file_path=str(output_file)
        )

        return str(output_file)

    def list_languages(self):
        """
        List available languages for XTTS.

        Returns:
            List of supported language codes
        """
        return ['en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru',
                'nl', 'cs', 'ar', 'zh-cn', 'ja', 'hu', 'ko', 'hi']


# Example usage and testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="XTTS TTS for Distiller")
    parser.add_argument("--reference", required=True, help="Reference audio file")
    parser.add_argument("--text", required=True, help="Text to synthesize")
    parser.add_argument("--language", default="en", help="Language code")
    parser.add_argument("--volume", type=int, default=100, help="Volume 0-100")
    parser.add_argument("--play", action="store_true", help="Play audio")
    parser.add_argument("--output", help="Output WAV file name")

    args = parser.parse_args()

    # Initialize TTS
    tts = DistillerXTTS(reference_audio=args.reference)

    if args.play:
        # Stream to speakers
        tts.speak_stream(args.text, language=args.language, volume=args.volume)
    else:
        # Save to file
        output_path = tts.get_wav_file_path(
            args.text,
            language=args.language,
            output_name=args.output
        )
        print(f"Saved to: {output_path}")
