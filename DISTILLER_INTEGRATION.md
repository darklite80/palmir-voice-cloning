# Using Cloned Voice with Distiller Platform

This guide explains how to use your cloned voice as the TTS output for your Distiller device.

## Overview

The `distiller_xtts_tts.py` module provides a Distiller-compatible TTS interface using XTTS voice cloning. It's designed to work similarly to the built-in Piper TTS, making it easy to replace or supplement Piper with your cloned voice.

## Quick Start

### 1. Prepare Your Reference Voice

First, you need a reference audio file (your voice sample):

```bash
# Option A: Use an uploaded file from the web interface
ls uploads/

# Option B: Record a new sample
# (10-30 seconds of clean speech is ideal)
```

### 2. Test the Integration

```bash
cd /home/distiller/projects/voice\ cloning
source venv/bin/activate

# Run the test script
python test_distiller_tts.py
```

This will:
- Load your reference voice from `uploads/`
- Generate a test WAV file
- Play audio through the speakers
- Verify multi-language support

### 3. Basic Usage

```python
from distiller_xtts_tts import DistillerXTTS

# Initialize with your reference voice
tts = DistillerXTTS(reference_audio="uploads/reference_123456.wav")

# Option 1: Stream directly to speakers
tts.speak_stream("Hello from Distiller!", volume=80)

# Option 2: Generate WAV file
wav_path = tts.get_wav_file_path("This is a test", output_name="test.wav")
```

## Integration Options

### Option 1: Standalone Script

Use the XTTS TTS in your own scripts:

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/distiller/projects/voice cloning')

from distiller_xtts_tts import DistillerXTTS

tts = DistillerXTTS(reference_audio="path/to/voice.wav")
tts.speak_stream("Your message here")
```

### Option 2: Replace Piper in Existing Code

The interface is designed to be compatible with Piper:

```python
# Before (using Piper):
# from distiller_sdk.piper import Piper
# tts = Piper()

# After (using XTTS):
from distiller_xtts_tts import DistillerXTTS
tts = DistillerXTTS(reference_audio="uploads/my_voice.wav")

# Same interface works!
tts.speak_stream("Hello!", volume=70)
wav = tts.get_wav_file_path("Test")
```

### Option 3: Use with Distiller Hardware

Combine with Distiller SDK hardware modules:

```python
import sys
sys.path.insert(0, '/opt/distiller-sdk')
sys.path.insert(0, '/home/distiller/projects/voice cloning')

from distiller_sdk.hardware.audio import Audio
from distiller_sdk.hardware.led import LED
from distiller_xtts_tts import DistillerXTTS

# Initialize hardware
audio = Audio()
led = LED(use_sudo=True)
tts = DistillerXTTS(reference_audio="uploads/reference.wav")

# Visual feedback
led.set_rgb_color(0, 0, 0, 255)  # Blue = speaking

# Generate and play speech
wav_path = tts.get_wav_file_path("Distiller is working!")
audio.play(wav_path)

# Cleanup
led.turn_off(0)
audio.close()
```

### Option 4: Command-Line Usage

Use from the command line:

```bash
# Activate environment
cd /home/distiller/projects/voice\ cloning
source venv/bin/activate

# Play audio
python distiller_xtts_tts.py \
    --reference uploads/reference.wav \
    --text "Hello from the command line" \
    --play \
    --volume 80

# Save to file
python distiller_xtts_tts.py \
    --reference uploads/reference.wav \
    --text "Save this to a file" \
    --output my_message.wav
```

## Advanced Usage

### Multi-Language Support

```python
tts = DistillerXTTS(reference_audio="uploads/reference.wav")

# Get supported languages
languages = tts.list_languages()
# Returns: ['en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', ...]

# Speak in different languages
tts.speak_stream("Hello", language="en")
tts.speak_stream("Hola", language="es")
tts.speak_stream("Bonjour", language="fr")
```

### Custom Sound Card

```python
# Use specific sound card
tts.speak_stream(
    "Testing custom sound card",
    sound_card_name="snd_pamir_ai_soundcard",
    volume=70
)
```

### Batch Processing

```python
tts = DistillerXTTS(reference_audio="uploads/reference.wav")

messages = [
    "First message",
    "Second message",
    "Third message"
]

for i, msg in enumerate(messages):
    wav_path = tts.get_wav_file_path(msg, output_name=f"message_{i}.wav")
    print(f"Generated: {wav_path}")
```

## Example: Voice Assistant

Here's a complete example of a voice assistant using cloned voice:

```python
#!/usr/bin/env python3
"""Voice assistant with cloned voice on Distiller."""

import sys
sys.path.insert(0, '/opt/distiller-sdk')
sys.path.insert(0, '/home/distiller/projects/voice cloning')

from distiller_sdk.parakeet import Parakeet
from distiller_sdk.hardware.led import LED
from distiller_xtts_tts import DistillerXTTS

# Initialize components
asr = Parakeet()  # Speech recognition
tts = DistillerXTTS(reference_audio="uploads/my_voice.wav")
led = LED(use_sudo=True)

try:
    print("Voice assistant ready! Speak now...")
    led.set_rgb_color(0, 0, 255, 0)  # Green = ready

    # Listen for speech
    for text in asr.record_and_transcribe_ptt():
        print(f"You said: {text}")

        # Process command (simple echo for demo)
        response = f"You said: {text}"

        # Respond with cloned voice
        led.set_rgb_color(0, 0, 0, 255)  # Blue = speaking
        tts.speak_stream(response, volume=80)
        led.set_rgb_color(0, 0, 255, 0)  # Green = ready

        break  # Remove this for continuous operation

finally:
    led.turn_off_all()
    asr.cleanup()
```

## Troubleshooting

### Model Loading Issues

If the model fails to load, ensure dependencies are correct:

```bash
cd /home/distiller/projects/voice\ cloning
source venv/bin/activate

# Check versions
pip list | grep -E "torch|torchaudio|transformers|TTS"

# Should see:
# torch==2.4.1
# torchaudio==2.4.1
# transformers==4.39.3
# TTS==0.22.0
```

### Audio Playback Issues

```bash
# Check audio devices
aplay -l

# Test audio
speaker-test -t wav -c 2

# Check permissions
groups | grep audio
```

### Import Errors

```python
# Make sure paths are set correctly
import sys
sys.path.insert(0, '/home/distiller/projects/voice cloning')

# Activate the venv before running Python
# source venv/bin/activate
```

## Performance Notes

- **First generation**: Takes 10-20 seconds (model loading + synthesis)
- **Subsequent generations**: 3-5 seconds (synthesis only)
- **Memory usage**: ~2GB RAM for XTTS model
- **CPU usage**: High during generation, optimized for ARM64

## Tips for Best Results

1. **Reference Audio Quality**:
   - Use clean, noise-free recordings
   - 10-30 seconds of speech is ideal
   - WAV format at 22050Hz works best

2. **Performance**:
   - Keep the model loaded (don't recreate DistillerXTTS each time)
   - Pre-generate common phrases if possible
   - Use shorter text for faster generation

3. **Voice Quality**:
   - Match the language of reference audio when possible
   - Shorter sentences produce better quality
   - Avoid very long paragraphs

## Files Overview

- `distiller_xtts_tts.py` - Main XTTS TTS module (Piper-compatible interface)
- `test_distiller_tts.py` - Test script and examples
- `DISTILLER_INTEGRATION.md` - This file
- `uploads/` - Reference audio files
- `outputs/` - Generated speech files

## Next Steps

1. Test the integration: `python test_distiller_tts.py`
2. Try the examples above
3. Create your own voice assistant or application
4. See integration examples: `python test_distiller_tts.py --example`

## Support

For issues specific to:
- **XTTS/TTS**: Check the main project README.md
- **Distiller SDK**: See /opt/distiller-sdk/README.md
- **Integration**: Review this file and test_distiller_tts.py
