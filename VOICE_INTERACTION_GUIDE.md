# Voice Interaction with Distiller Hardware

Complete guide for using voice input/output with your Distiller device.

## Quick Start

```bash
cd "/home/distiller/projects/voice cloning"
source venv/bin/activate
python simple_voice_assistant.py
```

## Hardware Components

### 1. Microphone (Input)
- Built-in microphone via Distiller Audio SDK
- Automatic gain control
- Voice Activity Detection (VAD)

### 2. Speaker (Output)
- Built-in speaker
- Volume control
- Cloned voice TTS output

### 3. LED (Visual Feedback)
- Green: Ready/listening
- Blue: Processing/speaking
- Red: Error

## Interaction Modes

### Mode 1: Push-to-Talk (PTT)

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/opt/distiller-sdk')
from distiller_sdk.parakeet import Parakeet

asr = Parakeet()

print("Hold button and speak, release when done...")
for text in asr.record_and_transcribe_ptt():
    print(f"You said: {text}")
    # Process text here
    break

asr.cleanup()
```

### Mode 2: Auto Voice Detection

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/opt/distiller-sdk')
from distiller_sdk.parakeet import Parakeet

asr = Parakeet()

print("Listening... speak naturally")
for text in asr.auto_record_and_transcribe():
    print(f"Heard: {text}")
    # Process text here
    if "stop" in text.lower():
        break

asr.cleanup()
```

### Mode 3: Continuous Recording

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/opt/distiller-sdk')
from distiller_sdk.hardware.audio import Audio

audio = Audio()

# Start recording
audio.record("my_recording.wav", duration=10)  # 10 seconds

# Or manual control
audio.record("my_recording.wav")  # Start
# ... do something ...
audio.stop_recording()  # Stop

audio.close()
```

## Voice Response with Cloned Voice

### Simple Response

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/distiller/projects/voice cloning')
from distiller_xtts_tts import DistillerXTTS

# Initialize with your voice
tts = DistillerXTTS(reference_audio="uploads/my_voice.wav")

# Speak directly through speakers
tts.speak_stream("Hello! This is my cloned voice.", volume=80)

# Or save to file
wav_file = tts.get_wav_file_path("Save this message")
print(f"Saved to: {wav_file}")
```

### With Distiller Audio System

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/opt/distiller-sdk')
sys.path.insert(0, '/home/distiller/projects/voice cloning')

from distiller_sdk.hardware.audio import Audio
from distiller_xtts_tts import DistillerXTTS

audio = Audio()
tts = DistillerXTTS(reference_audio="uploads/my_voice.wav")

# Generate speech
wav_path = tts.get_wav_file_path("Hello from Distiller!")

# Play through Distiller audio system
audio.play(wav_path)
audio.close()
```

## Complete Voice Assistant Examples

### Example 1: Echo Assistant

```python
#!/usr/bin/env python3
"""Echo back what you say in your cloned voice."""

import sys
sys.path.insert(0, '/opt/distiller-sdk')
sys.path.insert(0, '/home/distiller/projects/voice cloning')

from distiller_sdk.parakeet import Parakeet
from distiller_sdk.hardware.audio import Audio
from distiller_xtts_tts import DistillerXTTS

asr = Parakeet()
audio = Audio()
tts = DistillerXTTS(reference_audio="uploads/my_voice.wav")

print("Say something... (say 'stop' to exit)")

try:
    for text in asr.auto_record_and_transcribe():
        print(f"You: {text}")

        if "stop" in text.lower():
            tts.speak_stream("Goodbye!", volume=70)
            break

        # Echo back
        response = f"You said: {text}"
        wav = tts.get_wav_file_path(response, output_name="echo.wav")
        audio.play(wav)

finally:
    asr.cleanup()
    audio.close()
```

### Example 2: Command Recognition

```python
#!/usr/bin/env python3
"""Voice command recognition with responses."""

import sys
sys.path.insert(0, '/opt/distiller-sdk')
sys.path.insert(0, '/home/distiller/projects/voice cloning')

from distiller_sdk.parakeet import Parakeet
from distiller_sdk.hardware.led import LED
from distiller_xtts_tts import DistillerXTTS

asr = Parakeet()
led = LED(use_sudo=True)
tts = DistillerXTTS(reference_audio="uploads/my_voice.wav")

commands = {
    "hello": "Hello! How can I help you?",
    "time": "I don't have a clock, but it's now!",
    "lights on": "Turning lights on",
    "lights off": "Turning lights off",
    "goodbye": "Goodbye! Have a great day!"
}

led.set_rgb_color(0, 0, 255, 0)  # Green = ready

try:
    print("Listening for commands...")
    for text in asr.auto_record_and_transcribe():
        print(f"Heard: {text}")
        text_lower = text.lower()

        # Check commands
        response = None
        for cmd, resp in commands.items():
            if cmd in text_lower:
                response = resp

                # Special actions
                if "lights on" in text_lower:
                    led.set_rgb_color(0, 255, 255, 255)  # White
                elif "lights off" in text_lower:
                    led.turn_off(0)
                    led.set_rgb_color(0, 0, 255, 0)  # Back to green
                elif "goodbye" in text_lower:
                    tts.speak_stream(response, volume=70)
                    break

                break

        if not response:
            response = "I didn't understand that command"

        # Respond
        led.set_rgb_color(0, 0, 0, 255)  # Blue = speaking
        tts.speak_stream(response, volume=70)
        led.set_rgb_color(0, 0, 255, 0)  # Green = ready

finally:
    led.turn_off_all()
    asr.cleanup()
```

### Example 3: Question & Answer

```python
#!/usr/bin/env python3
"""Simple Q&A system with voice."""

import sys
sys.path.insert(0, '/opt/distiller-sdk')
sys.path.insert(0, '/home/distiller/projects/voice cloning')

from distiller_sdk.parakeet import Parakeet
from distiller_xtts_tts import DistillerXTTS

asr = Parakeet()
tts = DistillerXTTS(reference_audio="uploads/my_voice.wav")

# Knowledge base
qa_pairs = {
    "what is your name": "I am a voice assistant running on a Distiller device",
    "what can you do": "I can listen to your voice and respond with a cloned voice",
    "how are you": "I'm doing great! Thanks for asking",
    "what time": "I don't have access to a clock right now",
}

print("Ask me a question...")

try:
    for question in asr.auto_record_and_transcribe():
        print(f"Q: {question}")

        # Find answer
        answer = "I don't know the answer to that"
        question_lower = question.lower()

        for key, value in qa_pairs.items():
            if key in question_lower:
                answer = value
                break

        print(f"A: {answer}")
        tts.speak_stream(answer, volume=70)

        if "goodbye" in question_lower or "bye" in question_lower:
            break

finally:
    asr.cleanup()
```

## Audio Settings

### Adjust Microphone Gain

```python
from distiller_sdk.hardware.audio import Audio

audio = Audio()

# Set gain (0-100)
Audio.set_mic_gain_static(80)  # 80% gain

# Check current gain
gain = audio.get_mic_gain()
print(f"Microphone gain: {gain}")

audio.close()
```

### Adjust Speaker Volume

```python
from distiller_sdk.hardware.audio import Audio

audio = Audio()

# Set volume (0-100)
Audio.set_speaker_volume_static(70)  # 70% volume

# Check current volume
volume = audio.get_speaker_volume()
print(f"Speaker volume: {volume}")

audio.close()
```

### Test Audio Devices

```bash
# List audio devices
aplay -l
arecord -l

# Test speaker
speaker-test -t wav -c 2

# Test microphone recording
arecord -d 5 test.wav
aplay test.wav
```

## LED Visual Feedback

```python
from distiller_sdk.hardware.led import LED

led = LED(use_sudo=True)

# Status colors
led.set_rgb_color(0, 0, 255, 0)      # Green = ready
led.set_rgb_color(0, 0, 0, 255)      # Blue = processing
led.set_rgb_color(0, 255, 0, 0)      # Red = error
led.set_rgb_color(0, 255, 255, 0)    # Yellow = waiting

# Animations
led.blink_led(0, 255, 0, 0, timing=500)     # Blink red
led.fade_led(0, 0, 255, 0, timing=1000)     # Fade green
led.rainbow_led(0, timing=800)              # Rainbow cycle

# Turn off
led.turn_off_all()
```

## Troubleshooting

### Microphone Not Working

```bash
# Check device
arecord -l

# Check permissions
groups | grep audio

# Add user to audio group (if needed)
sudo usermod -a -G audio $USER
# Then logout and login
```

### Speaker Not Working

```bash
# Check device
aplay -l

# Test speaker
speaker-test -t wav -c 2

# Adjust volume
alsamixer
```

### Voice Recognition Issues

```python
# Adjust microphone gain
from distiller_sdk.hardware.audio import Audio
Audio.set_mic_gain_static(85)  # Increase gain

# Check recording quality
from distiller_sdk.hardware.audio import Audio
audio = Audio()
audio.record("test.wav", duration=5)
audio.close()
# Listen to test.wav to check quality
```

### TTS Not Loading

```bash
# Check if server is running
systemctl status voice-cloning.service

# Check logs
sudo journalctl -u voice-cloning.service -f

# Test API
curl http://localhost:5001/api/status
```

## Performance Tips

1. **Keep TTS model loaded**: Don't create new `DistillerXTTS` instances frequently
2. **Pre-generate common phrases**: Save frequently used responses as WAV files
3. **Adjust VAD sensitivity**: Configure Parakeet for your environment
4. **Use shorter sentences**: Faster generation and better quality

## Integration with Voice Profiles

```python
#!/usr/bin/env python3
"""Use voice profiles in voice assistant."""

import sys
import requests
sys.path.insert(0, '/opt/distiller-sdk')
sys.path.insert(0, '/home/distiller/projects/voice cloning')

from distiller_sdk.parakeet import Parakeet
from distiller_sdk.hardware.audio import Audio
from voice_profiles import VoiceProfileManager

asr = Parakeet()
audio = Audio()
profile_mgr = VoiceProfileManager()

# Get a voice profile
profiles = profile_mgr.list_profiles()
if not profiles:
    print("No voice profiles found!")
    exit(1)

# Use first profile
profile = profiles[0]
profile_id = profile['profile_id']
print(f"Using profile: {profile['name']}")

# Listen and respond
for text in asr.auto_record_and_transcribe():
    print(f"You: {text}")

    # Generate with profile via API
    response = requests.post('http://localhost:5001/api/clone_with_profile',
        json={
            'profile_id': profile_id,
            'text': f"You said: {text}",
            'language': 'en'
        })

    if response.json()['success']:
        # Play the generated audio
        output_file = response.json()['output_file']
        audio.play(f"outputs/{output_file}")

    if 'stop' in text.lower():
        break

asr.cleanup()
audio.close()
```

## Resources

- **Distiller SDK Docs**: `/opt/distiller-sdk/README.md`
- **Voice Cloning API**: `VOICE_PROFILES_API.md`
- **Distiller Integration**: `DISTILLER_INTEGRATION.md`
- **Web Interface**: `http://localhost:5001`

## Example Projects

All examples are in: `/home/distiller/projects/voice cloning/`

- `simple_voice_assistant.py` - Basic voice assistant
- `distiller_xtts_tts.py` - Cloned voice TTS module
- `test_profiles.py` - Profile management examples
